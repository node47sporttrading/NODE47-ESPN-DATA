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
        "linescores": item.get("linescores") or [],
    }


def normalize_event(
    raw: dict[str, Any], sport: str, league: str, competition_name: str,
    *, draw: str | None = None, tournament_event_id: str | None = None,
    tournament_name: str | None = None,
) -> dict[str, Any]:
    competitions = raw.get("competitions") or []
    competition = competitions[0] if competitions and isinstance(competitions[0], dict) else {}
    raw_competitors = competition.get("competitors") or []
    participants = [_participant(item) for item in raw_competitors if isinstance(item, dict)]

    home = next((p for p in participants if p["home_away"] == "home"), None)
    away = next((p for p in participants if p["home_away"] == "away"), None)
    # Tennis payloads may not label competitors home/away; preserve their source order.
    if sport == "tennis" and home is None and away is None and len(participants) >= 2:
        home, away = participants[0], participants[1]
    status = (raw.get("status") or {}).get("type") or {}
    links = raw.get("links") or []
    event_url = next((link.get("href") for link in links if isinstance(link, dict) and link.get("href")), None)

    result = {
        "event_id": str(raw.get("id")) if raw.get("id") is not None else None,
        "sport": sport,
        "league": league,
        "competition": competition_name,
        "name": raw.get("name"),
        "short_name": raw.get("shortName"),
        "start_time_utc": _utc(raw.get("date") or competition.get("date")),
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
    if sport == "tennis":
        round_info = raw.get("round") or competition.get("round") or {}
        result.update({
            "draw": draw,
            "round": round_info.get("displayName") or round_info.get("name"),
            "tournament_event_id": tournament_event_id,
            "tournament": tournament_name or competition_name,
        })
        if len(participants) < 2 or not all(p.get("name") for p in participants[:2]):
            result["quality_flags"].append("tennis_match_missing_two_named_players")
    return result


def _normalize_tennis_scoreboard(events: list[dict[str, Any]], league: str, competition_name: str) -> list[dict[str, Any]]:
    """ESPN tennis scoreboards wrap matches inside event.groupings[].competitions[]."""
    normalized = []
    for tournament in events:
        tournament_id = str(tournament.get("id")) if tournament.get("id") is not None else None
        tournament_name = tournament.get("name") or competition_name
        groupings = tournament.get("groupings") or []
        for grouping_block in groupings:
            if not isinstance(grouping_block, dict):
                continue
            grouping = grouping_block.get("grouping") or {}
            draw = grouping.get("displayName") or grouping.get("name")
            matches = grouping_block.get("competitions") or []
            for match in matches:
                if not isinstance(match, dict):
                    continue
                competitors = match.get("competitors") or []
                if len(competitors) < 2:
                    continue
                match_id = match.get("id") or match.get("uid")
                if match_id is None:
                    continue
                raw_match = {
                    "id": str(match_id),
                    "name": match.get("name") or match.get("shortName"),
                    "shortName": match.get("shortName"),
                    "date": match.get("date") or tournament.get("date"),
                    "status": match.get("status") or tournament.get("status"),
                    "round": match.get("round"),
                    "links": match.get("links") or tournament.get("links") or [],
                    "competitions": [match],
                }
                normalized.append(normalize_event(
                    raw_match, "tennis", league, tournament_name,
                    draw=draw, tournament_event_id=tournament_id,
                    tournament_name=tournament_name,
                ))
    return normalized


def normalize_scoreboard(payload: dict[str, Any], sport: str, league: str, competition_name: str) -> list[dict[str, Any]]:
    events = payload.get("events") or []
    if not isinstance(events, list):
        raise ValueError("ESPN events field must be a list")
    valid_events = [event for event in events if isinstance(event, dict)]
    if sport == "tennis":
        return _normalize_tennis_scoreboard(valid_events, league, competition_name)
    return [normalize_event(event, sport, league, competition_name) for event in valid_events]
