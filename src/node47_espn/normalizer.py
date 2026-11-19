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


def _participant(item: dict[str, Any]) -> dict[str, Any]:
    entity = item.get("team") or item.get("athlete") or {}
    return {
        "id": entity.get("id") or item.get("id"),
        "name": entity.get("displayName") or entity.get("fullName") or entity.get("name")
                or item.get("displayName") or item.get("name"),
        "abbreviation": entity.get("abbreviation"),
        "score": item.get("score"),
        "winner": item.get("winner"),
        "home_away": item.get("homeAway"),
    }


def normalize_event(raw: dict[str, Any], sport: str, league: str, competition_name: str) -> dict[str, Any]:
    competitions = raw.get("competitions") or []
    competition = competitions[0] if competitions and isinstance(competitions[0], dict) else {}
    raw_competitors = competition.get("competitors") or []
    participants = [_participant(item) for item in raw_competitors if isinstance(item, dict)]

    home = next((p for p in participants if p["home_away"] == "home"), None)
    away = next((p for p in participants if p["home_away"] == "away"), None)
    status = (raw.get("status") or {}).get("type") or {}
    links = raw.get("links") or []
    event_url = next((link.get("href") for link in links if isinstance(link, dict) and link.get("href")), None)

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
        "participants": {"home": home, "away": away, "competitors": participants},
        "venue": (competition.get("venue") or {}).get("fullName"),
        "source": {"provider": "ESPN", "event_url": event_url},
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
