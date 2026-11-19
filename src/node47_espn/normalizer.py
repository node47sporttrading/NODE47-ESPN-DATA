"""Normalize variable ESPN scoreboard payloads into the NODE.47 event contract."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _utc(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return None
        return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    except (TypeError, ValueError):
        return None


def normalize_event(raw: dict[str, Any], sport: str, league: str, competition_name: str) -> dict[str, Any]:
    competitors = []
    competitions = raw.get("competitions") or []
    if competitions and isinstance(competitions[0], dict):
        competitors = competitions[0].get("competitors") or []

    teams: dict[str, Any] = {"home": None, "away": None}
    for item in competitors:
        side = item.get("homeAway")
        if side not in teams:
            continue
        team = item.get("team") or {}
        score = item.get("score")
        teams[side] = {
            "id": team.get("id"),
            "name": team.get("displayName") or team.get("name"),
            "abbreviation": team.get("abbreviation"),
            "score": score,
        }

    status = (raw.get("status") or {}).get("type") or {}
    return {
        "event_id": str(raw.get("id")) if raw.get("id") is not None else None,
        "sport": sport,
        "league": league,
        "competition": competition_name,
        "name": raw.get("name"),
        "short_name": raw.get("shortName"),
        "start_time_utc": _utc(raw.get("date")),
        "status": {
            "state": status.get("state"),
            "name": status.get("name"),
            "description": status.get("description"),
            "completed": status.get("completed"),
        },
        "participants": teams,
        "venue": (competitions[0].get("venue") or {}).get("fullName") if competitions else None,
        "source": {
            "provider": "ESPN",
            "event_url": raw.get("links", [{}])[0].get("href") if raw.get("links") else None,
        },
        "quality_flags": [],
    }


def normalize_scoreboard(payload: dict[str, Any], sport: str, league: str, competition_name: str) -> list[dict[str, Any]]:
    events = payload.get("events") or []
    if not isinstance(events, list):
        raise ValueError("ESPN events field must be a list")
    return [
        normalize_event(event, sport, league, competition_name)
        for event in events if isinstance(event, dict)
    ]
