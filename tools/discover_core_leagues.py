#!/usr/bin/env python3
"""Discover ESPN Core leagues for soccer, basketball and tennis.

The Core API collection is the discovery source; Site API scoreboard probes
remain the activation gate. Existing scoreboard-only routes are retained.
"""
from __future__ import annotations
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import requests

SPORTS = ("soccer", "basketball", "tennis")
CORE_BASE = "https://sports.core.api.espn.com/v2/sports"
DEFAULT_TIMEOUT = 20
DEFAULT_LIMIT = 1000

def league_slug_from_ref(ref: str, sport: str) -> str | None:
    """Extract a league slug only from a well-formed ESPN Core league ref."""
    try:
        parts = [part for part in urlparse(ref).path.split("/") if part]
        index = parts.index("sports")
        if parts[index + 1] != sport or parts[index + 2] != "leagues":
            return None
        slug = parts[index + 3]
    except (TypeError, ValueError, IndexError):
        return None
    if not re.fullmatch(r"[A-Za-z0-9._-]+", slug):
        return None
    return slug

def discover_sport(session, sport: str, timeout: int = DEFAULT_TIMEOUT, limit: int = DEFAULT_LIMIT, max_pages: int = 100) -> list[str]:
    """Read every page of one Core API league collection."""
    url = f"{CORE_BASE}/{sport}/leagues"
    found: set[str] = set()
    for page in range(1, max_pages + 1):
        response = session.get(url, params={"limit": limit, "page": page}, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
            raise ValueError(f"Unexpected ESPN Core league collection schema for {sport}")
        items = payload["items"]
        for item in items:
            if not isinstance(item, dict):
                continue
            ref = item.get("$ref") or item.get("ref")
            slug = league_slug_from_ref(ref, sport) if isinstance(ref, str) else None
            if slug:
                found.add(slug)
        page_count = payload.get("pageCount")
        page_index = payload.get("pageIndex")
        if isinstance(page_count, int) and isinstance(page_index, int):
            if page_index >= page_count:
                break
        elif len(items) < limit or not items:
            break
    else:
        raise RuntimeError(f"ESPN Core pagination exceeded {max_pages} pages for {sport}")
    if not found:
        raise ValueError(f"ESPN Core returned no usable league references for {sport}")
    return sorted(found)

def build_candidates(discovered: dict[str, list[str]], existing: dict, competitions: dict) -> dict:
    """Union Core-discovered leagues with existing scoreboard route candidates."""
    sports: dict[str, set[str]] = {sport: set(ids) for sport, ids in discovered.items()}
    for sport, block in existing.get("sports", {}).items():
        if sport in SPORTS:
            sports.setdefault(sport, set()).update(block.get("competition_ids", []))
    for item in competitions.get("competitions", []):
        sport, league = item.get("sport"), item.get("league")
        if sport in SPORTS and isinstance(league, str) and league:
            sports.setdefault(sport, set()).add(league)
    ordered = {sport: {"competition_ids": sorted(sports.get(sport, set()))} for sport in SPORTS}
    total = sum(len(block["competition_ids"]) for block in ordered.values())
    return {
        "schema_version": "1.1",
        "dataset": "node47_espn_competition_candidates",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "method": "ESPN Core API league collection plus retained scoreboard-only routes",
        "disclaimer": "Core-discovered league references are candidates, not proof of a working Site API scoreboard. Only live scoreboard probes can mark a route verified.",
        "discovery": {
            "source": "https://sports.core.api.espn.com/v2/sports/{sport}/leagues",
            "sports": list(SPORTS),
            "core_counts": {sport: len(discovered.get(sport, [])) for sport in SPORTS},
            "retained_existing_routes": True,
        },
        "sports": ordered,
        "total_candidates": total,
    }

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", default="data/registry/candidates.json")
    parser.add_argument("--competitions", default="config/competitions.json")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--max-pages", type=int, default=100)
    args = parser.parse_args()
    candidates_path = Path(args.candidates)
    config_path = Path(args.competitions)
    existing = json.loads(candidates_path.read_text(encoding="utf-8"))
    competitions = json.loads(config_path.read_text(encoding="utf-8"))
    session = requests.Session()
    session.headers.update({"Accept": "application/json", "User-Agent": "NODE47-ESPN-DATA/0.0.14"})
    discovered = {sport: discover_sport(session, sport, args.timeout, args.limit, args.max_pages) for sport in SPORTS}
    result = build_candidates(discovered, existing, competitions)
    candidates_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts = {sport: len(block["competition_ids"]) for sport, block in result["sports"].items()}
    print("Core counts:", result["discovery"]["core_counts"], "candidate union:", counts, "total:", result["total_candidates"])

if __name__ == "__main__":
    main()
