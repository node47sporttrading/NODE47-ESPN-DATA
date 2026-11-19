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
async def propline_events(sport_key: str) -> dict[str, Any]:
    """List upcoming PropLine events for a provider sport key (e.g. basketball_nba)."""
    try:
        data = await asyncio.to_thread(_propline().events, sport_key)
        return {"status": "ok", "sport_key": sport_key, "events": data}
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



# Sport-specific PropLine adapters. Provider keys are not ESPN league IDs.
PROPLINE_MODULES = {
    "football": {
        "prefixes": ("soccer_",),
        "sport_key": None,
        "markets": (
            "h2h", "spreads", "totals", "both_teams_to_score",
            "double_chance", "draw_no_bet", "correct_score",
            "total_corners", "corners_spread", "team_corners",
            "total_cards", "team_cards", "anytime_goal_scorer",
            "first_goal_scorer", "2plus_goals", "player_assists",
            "player_2plus_assists", "player_cards", "goal_or_assist",
        ),
        "periods": ("h1", "h2"),
    },
    "basketball": {
        "prefixes": ("basketball_",),
        "sport_key": None,
        # Basketball player props vary by event and book; discover them per event.
        "markets": ("h2h", "spreads", "totals"),
        "periods": ("q1", "q2", "q3", "q4", "h1", "h2"),
        "dynamic_event_markets": True,
    },
    "tennis": {
        "prefixes": (),
        "sport_key": "tennis",
        # PropLine's public market catalogue does not enumerate tennis prop keys.
        # Event-market discovery is the source of truth for optional tennis markets.
        "markets": ("h2h", "spreads", "totals"),
        "periods": ("s1", "s2", "s3", "s4", "s5"),
        "dynamic_event_markets": True,
    },
}


def _propline_module(module: str, sport_key: str, markets: str | None = None, allow_dynamic: bool = False):
    name = (module or "").strip().lower()
    if name not in PROPLINE_MODULES:
        raise ValueError("module must be football, basketball or tennis")
    config = PROPLINE_MODULES[name]
    key = (sport_key or "").strip()
    if config["sport_key"] and key != config["sport_key"]:
        raise ValueError(f"{name} requires PropLine sport_key={config['sport_key']!r}")
    if config["prefixes"] and not key.startswith(config["prefixes"]):
        raise ValueError(f"{name} requires a provider sport_key beginning with {config['prefixes']}")
    if not key:
        raise ValueError("sport_key is required; select it from propline_sports()")
    selected = tuple(x.strip() for x in markets.split(",") if x.strip()) if markets else ("h2h", "spreads", "totals")
    if not selected:
        raise ValueError("at least one market must be requested")
    invalid = sorted(set(selected) - set(config["markets"]))
    if invalid and not (allow_dynamic and config.get("dynamic_event_markets")):
        raise ValueError(f"markets not enabled for {name}: {invalid}")
    return name, key, ",".join(selected), config


def _propline_market_keys(payload: Any) -> set[str]:
    rows = payload.get("markets", []) if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        return set()
    return {
        str(row.get("key")).strip()
        for row in rows
        if isinstance(row, dict) and row.get("key")
    }


def _validate_propline_period(config: dict[str, Any], period: str | None) -> str | None:
    if period is None or period == "":
        return None
    value = period.strip().lower()
    if value != "all" and value not in config["periods"]:
        raise ValueError(f"period {value!r} is not supported for this module")
    return value


@mcp.tool()
async def propline_module_events(module: str, sport_key: str) -> dict[str, Any]:
    """List PropLine fixtures through the football, basketball or tennis adapter."""
    try:
        name, key, _, _ = _propline_module(module, sport_key)
        data = await asyncio.to_thread(_propline().events, key)
        return {"status": "ok", "module": name, "sport_key": key, "events": data}
    except (PropLineError, ValueError) as exc:
        return {"status": "error", "module": module, "sport_key": sport_key, "error": str(exc)}


@mcp.tool()
async def propline_module_odds(
    module: str,
    sport_key: str,
    markets: str | None = None,
    bookmakers: str | None = None,
    max_age_seconds: int | None = 180,
    period: str | None = None,
) -> dict[str, Any]:
    """Fetch validated bulk odds; tennis optional props require per-event market discovery."""
    try:
        name, key, selected, config = _propline_module(module, sport_key, markets)
        selected_period = _validate_propline_period(config, period)
        data = await asyncio.to_thread(
            _propline().odds, key, selected, bookmakers, max_age_seconds, selected_period
        )
        return {
            "status": "ok", "module": name, "sport_key": key,
            "markets": selected, "period": selected_period, "odds": data,
        }
    except (PropLineError, ValueError) as exc:
        return {"status": "error", "module": module, "sport_key": sport_key, "error": str(exc)}


@mcp.tool()
async def propline_module_event_markets(
    module: str, sport_key: str, event_id: str
) -> dict[str, Any]:
    """Discover the markets actually available for one exact PropLine event."""
    try:
        name, key, _, config = _propline_module(module, sport_key)
        data = await asyncio.to_thread(_propline().event_markets, key, event_id)
        return {
            "status": "ok", "module": name, "sport_key": key,
            "event_id": event_id, "module_market_catalog": list(config["markets"]),
            "available_markets": data,
        }
    except (PropLineError, ValueError) as exc:
        return {"status": "error", "module": module, "sport_key": sport_key,
                "event_id": event_id, "error": str(exc)}


@mcp.tool()
async def propline_module_event_odds(
    module: str,
    sport_key: str,
    event_id: str,
    markets: str | None = None,
    period: str | None = None,
) -> dict[str, Any]:
    """Discover and validate event markets before fetching event odds."""
    try:
        name, key, selected, config = _propline_module(module, sport_key, markets, allow_dynamic=True)
        selected_period = _validate_propline_period(config, period)
        client = _propline()
        available_payload = await asyncio.to_thread(client.event_markets, key, event_id)
        available = _propline_market_keys(available_payload)
        requested = set(selected.split(","))
        invalid = sorted(requested - available)
        if invalid:
            return {
                "status": "market_unavailable", "module": name, "sport_key": key,
                "event_id": event_id, "requested_markets": sorted(requested),
                "unavailable_markets": invalid, "available_markets": sorted(available),
                "odds": None,
            }
        data = await asyncio.to_thread(
            client.event_odds, key, event_id, selected, selected_period
        )
        return {
            "status": "ok", "module": name, "sport_key": key,
            "event_id": event_id, "markets": selected, "period": selected_period,
            "available_markets": sorted(available), "odds": data,
        }
    except (PropLineError, ValueError) as exc:
        return {"status": "error", "module": module, "sport_key": sport_key,
                "event_id": event_id, "error": str(exc)}


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
    version="0.0.13",
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
        "version": "0.0.13",
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
