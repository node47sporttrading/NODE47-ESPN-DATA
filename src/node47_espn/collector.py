"""Competition-level collection with isolated failures and explicit coverage."""
from __future__ import annotations

from datetime import datetime, timezone

from .normalizer import normalize_scoreboard
from .validator import validate_event


def collect(config: dict, client, date: str | None = None) -> dict:
    fetched_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    all_events = []
    coverage = []

    for competition in config.get("competitions", []):
        if not competition.get("enabled", False):
            continue
        sport = competition["sport"]
        league = competition["league"]
        name = competition.get("name", league)
        record = {
            "sport": sport, "league": league, "competition": name,
            "status": "unknown", "event_count": 0, "error": None,
        }
        try:
            payload = client.scoreboard(sport, league, date=date)
            events = normalize_scoreboard(payload, sport, league, name)
            for event in events:
                validate_event(event)
            all_events.extend(events)
            record["event_count"] = len(events)
            record["status"] = "empty" if not events else "ok"
        except Exception as exc:  # isolate a single unavailable route; keep other sports flowing
            record["status"] = "unavailable"
            record["error"] = str(exc)[:300]
        coverage.append(record)

    return {
        "schema_version": "1.0",
        "dataset": "node47_espn_scoreboard",
        "provider": "ESPN",
        "fetched_at_utc": fetched_at,
        "requested_date": date,
        "event_count": len(all_events),
        "events": all_events,
        "coverage": coverage,
    }
