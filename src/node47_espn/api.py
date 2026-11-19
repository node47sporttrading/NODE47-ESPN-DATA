"""HTTP + MCP API for persisted NODE.47 multisport ESPN data."""
from __future__ import annotations

import asyncio
import hmac
import json
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from .client import ESPNClient
from .collector import collect
from .propline_client import PropLineClient, PropLineError
from .store import DataStore

if os.getenv("DATABASE_URL"):
    from .postgres_store import PostgresDataStore

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = Path(os.getenv("NODE47_CONFIG_PATH", ROOT / "config" / "competitions.json"))
REGISTRY_PATH = Path(os.getenv("NODE47_REGISTRY_PATH", ROOT / "config" / "registry.json"))
DATA_PATH = os.getenv("NODE47_DATA_PATH", str(ROOT / "data" / "node47.sqlite3"))
REFRESH_SECONDS = max(60, int(os.getenv("NODE47_REFRESH_SECONDS", "900")))
MCP_PUBLIC_HOST = os.getenv("NODE47_MCP_PUBLIC_HOST", "node47-espn-data.onrender.com")
MCP_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "NODE47_MCP_ALLOWED_ORIGINS",
        "https://chatgpt.com,https://chat.openai.com",
    ).split(",")
    if origin.strip()
]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


config = _read_json(CONFIG_PATH)
registry = _read_json(REGISTRY_PATH)
store = PostgresDataStore(os.environ["DATABASE_URL"]) if os.getenv("DATABASE_URL") else DataStore(DATA_PATH)
refresh_lock = asyncio.Lock()


def _client() -> ESPNClient:
    return ESPNClient(
        config["base_url"],
        timeout=int(os.getenv("NODE47_HTTP_TIMEOUT", config.get("request_timeout_seconds", 20))),
        retries=int(os.getenv("NODE47_HTTP_RETRIES", config.get("retries", 2))),
    )


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def refresh_data():
    async with refresh_lock:
        dataset = await asyncio.to_thread(collect, config, _client())
        store.save_dataset(dataset)
        return dataset


async def _refresh_loop():
    while True:
        try:
            await refresh_data()
        except Exception:
            # Health/coverage endpoints expose the last successful snapshot.
            pass
        await asyncio.sleep(REFRESH_SECONDS)


# Read-only MCP surface. Refresh remains available only through the API-key
# protected REST endpoint and is deliberately not exposed as an MCP tool.
mcp = FastMCP(
    name="NODE47 ESPN DATA",
    instructions=(
        "Read-only tools for NODE.47 event identity, competition registry, "
        "scoreboard snapshots and coverage. PropLine tools provide bookmaker odds, markets, "
        "event ID crosswalks and bookmaker freshness. These are raw market data, not predictions."
    ),
    # FastMCP 1.x reads the endpoint path and transport security from its constructor.
    # The internal root path combines with FastAPI's /mcp mount to expose /mcp/.
    streamable_http_path="/",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[MCP_PUBLIC_HOST, f"{MCP_PUBLIC_HOST}:*"],
        allowed_origins=MCP_ALLOWED_ORIGINS,
    ),
)

@mcp.tool()
async def espn_health() -> dict[str, Any]:
    """Return API status, last successful ESPN refresh time, data age and event count."""
    return await health()


@mcp.tool()
async def espn_competitions(sport: str | None = None, status: str | None = None) -> dict[str, Any]:
    """List configured ESPN competitions, optionally filtered by sport and registry status."""
    return await competitions(sport=sport, status=status)


@mcp.tool()
async def espn_coverage() -> dict[str, Any]:
    """Return the latest collection status for every configured competition route."""
    return await coverage()


@mcp.tool()
async def espn_events(
    sport: str | None = None,
    league: str | None = None,
    status: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, Any]:
    """Search normalized ESPN events by sport, league, status and UTC date range."""
    if limit < 1 or limit > 1000:
        raise ValueError("limit must be between 1 and 1000")
    if offset < 0:
        raise ValueError("offset must be zero or greater")
    return await events(
        sport=sport,
        league=league,
        status=status,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )


@mcp.tool()
async def espn_event_detail(event_id: str) -> dict[str, Any]:
    """Return the normalized ESPN record for one exact event ID."""
    return await event_detail(event_id=event_id)




def _propline() -> PropLineClient:
    return PropLineClient(
        timeout=int(os.getenv("PROPLINE_HTTP_TIMEOUT", "20")),
    )


@mcp.tool()
async def propline_health() -> dict[str, Any]:
    """Check PropLine authentication, available sports and bookmaker data freshness."""
    if not os.getenv("PROPLINE_API_KEY", "").strip():
        return {"configured": False, "status": "not_configured",
                "required_environment_variable": "PROPLINE_API_KEY"}
    try:
        client = _propline()
        sports, freshness = await asyncio.gather(
            asyncio.to_thread(client.sports),
            asyncio.to_thread(client.freshness),
        )
        return {"configured": True, "status": "ok", "sports": sports, "freshness": freshness}
    except PropLineError as exc:
        return {"configured": True, "status": "error", "error": str(exc)}


@mcp.tool()
async def propline_sports() -> dict[str, Any]:
    """List sports supported by the connected PropLine account."""
    try:
        return {"status": "ok", "sports": await asyncio.to_thread(_propline().sports)}
    except PropLineError as exc:
        return {"status": "error", "error": str(exc)}


@mcp.tool()
async def propline_events(sport_key: str, commence_time_from: str | None = None,
                          commence_time_to: str | None = None) -> dict[str, Any]:
    """List PropLine events for a provider sport key, optionally bounded by UTC kickoff times."""
    params = {}
    if commence_time_from:
        params["commence_time_from"] = commence_time_from
    if commence_time_to:
        params["commence_time_to"] = commence_time_to
    try:
        data = await asyncio.to_thread(_propline().events, sport_key, **params)
        return {"status": "ok", "sport_key": sport_key, "events": data}
    except PropLineError as exc:
        return {"status": "error", "sport_key": sport_key, "error": str(exc)}


@mcp.tool()
async def propline_event_ids(sport_key: str) -> dict[str, Any]:
    """Return PropLine's event ID crosswalk, including ESPN event IDs where available."""
    try:
        data = await asyncio.to_thread(_propline().event_ids, sport_key)
        return {"status": "ok", "sport_key": sport_key, "crosswalk": data}
    except PropLineError as exc:
        return {"status": "error", "sport_key": sport_key, "error": str(exc)}


@mcp.tool()
async def propline_odds(sport_key: str, markets: str = "h2h,spreads,totals",
                        bookmakers: str | None = None, max_age_seconds: int | None = 180) -> dict[str, Any]:
    """Fetch bulk bookmaker odds; default markets are h2h, spreads and totals."""
    try:
        data = await asyncio.to_thread(
            _propline().odds, sport_key, markets, bookmakers, max_age_seconds
        )
        return {"status": "ok", "sport_key": sport_key, "markets": markets, "odds": data}
    except PropLineError as exc:
        return {"status": "error", "sport_key": sport_key, "error": str(exc)}


@mcp.tool()
async def propline_event_odds(sport_key: str, event_id: str, markets: str) -> dict[str, Any]:
    """Fetch requested game or player-prop markets for one exact PropLine event ID."""
    try:
        data = await asyncio.to_thread(_propline().event_odds, sport_key, event_id, markets)
        return {"status": "ok", "sport_key": sport_key, "event_id": event_id,
                "markets": markets, "odds": data}
    except PropLineError as exc:
        return {"status": "error", "sport_key": sport_key, "event_id": event_id,
                "error": str(exc)}


@mcp.tool()
async def propline_markets(sport_key: str, event_id: str) -> dict[str, Any]:
    """Discover which market keys are actually available for a PropLine event."""
    try:
        data = await asyncio.to_thread(_propline().markets, sport_key, event_id)
        return {"status": "ok", "sport_key": sport_key, "event_id": event_id, "markets": data}
    except PropLineError as exc:
        return {"status": "error", "sport_key": sport_key, "event_id": event_id,
                "error": str(exc)}


# Build the Streamable HTTP ASGI app with the configured FastMCP 1.x settings.
mcp_http_app = mcp.streamable_http_app()


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with mcp.session_manager.run():
        task = None if os.getenv("NODE47_DISABLE_SCHEDULER") == "1" else asyncio.create_task(_refresh_loop())
        try:
            yield
        finally:
            if task is not None:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass


app = FastAPI(
    title="NODE.47 Multisport Data API",
    version="0.0.11",
    description="ESPN scoreboard ingestion, normalized events, competition registry, collection coverage and read-only MCP tools.",
    lifespan=lifespan,
)


async def require_api_key(x_api_key: str | None = Header(default=None)):
    expected = os.getenv("NODE47_API_KEY", "")
    if not expected:
        raise HTTPException(503, detail="Refresh endpoint is disabled: NODE47_API_KEY is not configured")
    if not x_api_key or not hmac.compare_digest(x_api_key, expected):
        raise HTTPException(401, detail="Invalid or missing API key")


@app.get("/health", tags=["system"])
@app.get("/v1/health", tags=["system"])
async def health():
    meta = store.get_meta()
    last = meta.get("last_refresh_utc")
    age = None
    if last:
        try:
            age = max(0, int((_now() - datetime.fromisoformat(last.replace("Z", "+00:00"))).total_seconds()))
        except ValueError:
            pass
    return {
        "service": "NODE.47 SPORT ANALYT DATA API",
        "version": "0.0.11",
        "status": "ok" if last and age is not None and age <= REFRESH_SECONDS * 2 else "degraded",
        "last_refresh_utc": last,
        "data_age_seconds": age,
        "event_count": store.count_events(),
        "deleted_stale_count": int(meta.get("last_pruned_count", "0")),
        "refresh_interval_seconds": REFRESH_SECONDS,
        "source": "ESPN public scoreboard endpoints",
    }


@app.get("/v1/competitions", tags=["catalog"])
async def competitions(sport: str | None = None, status: str | None = None):
    active = {
        (x["sport"], x["league"])
        for x in config.get("competitions", [])
        if x.get("enabled")
    }
    entries = []
    for entry in registry.get("entries", []):
        if sport and entry.get("sport") != sport:
            continue
        if status and entry.get("status") != status:
            continue
        item = dict(entry)
        item["collection_enabled"] = (item.get("sport"), item.get("competition_id")) in active
        entries.append(item)
    return {"count": len(entries), "registry_version": registry.get("version"), "competitions": entries}


@app.get("/v1/coverage", tags=["catalog"])
async def coverage():
    rows = store.get_coverage()
    counts = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    return {
        "registry_competition_count": len(registry.get("entries", [])),
        "collection_route_count": len([x for x in config.get("competitions", []) if x.get("enabled")]),
        "last_collection_route_count": len(rows),
        "status_counts": counts,
        "routes": rows,
        "last_refresh_utc": store.get_meta().get("last_refresh_utc"),
    }


@app.get("/v1/events", tags=["events"])
async def events(
    sport: str | None = None,
    league: str | None = None,
    status: str | None = None,
    date_from: str | None = Query(default=None, description="Inclusive ISO-8601 UTC timestamp"),
    date_to: str | None = Query(default=None, description="Inclusive ISO-8601 UTC timestamp"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    rows = store.list_events(
        sport=sport,
        league=league,
        status=status,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )
    return {
        "count": len(rows),
        "limit": limit,
        "offset": offset,
        "last_refresh_utc": store.get_meta().get("last_refresh_utc"),
        "events": rows,
    }


@app.get("/v1/events/{event_id}", tags=["events"])
async def event_detail(event_id: str):
    event = store.get_event(event_id)
    if event is None:
        raise HTTPException(404, detail="Event not found in the collected dataset")
    return event


@app.post("/v1/refresh", tags=["operations"], dependencies=[Depends(require_api_key)])
async def manual_refresh():
    dataset = await refresh_data()
    return {
        "status": "completed",
        "fetched_at_utc": dataset["fetched_at_utc"],
        "event_count": dataset["event_count"],
        "coverage": dataset["coverage"],
    }


# Public MCP endpoint: https://node47-espn-data.onrender.com/mcp/
app.mount("/mcp", mcp_http_app)
