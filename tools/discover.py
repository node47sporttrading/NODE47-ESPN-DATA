#!/usr/bin/env python3
"""V0.0.5 discovery - enumerate every league ESPN currently exposes per sport.

Source of truth: sports.core.api.espn.com/v2/sports/{sport}/leagues (paged).
This is ESPN's own live enumeration, so no candidate code is ever invented:
every competition_id written to data/registry/candidates.json comes from ESPN.

Usage:
    python3 tools/discover.py [--out data/registry/candidates.json]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

CORE_BASE = "https://sports.core.api.espn.com/v2/sports"
DEFAULT_SPORTS = ["soccer", "basketball", "tennis"]
IN_SCOPE_SPORTS = {"soccer", "basketball", "tennis"}


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(
        url, headers={"Accept": "application/json", "User-Agent": "NODE47-ESPN-DATA/0.0.5"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object from {url}")
    return payload


def slug_from_ref(ref: str) -> str | None:
    marker = "/leagues/"
    if marker not in ref:
        return None
    return ref.split(marker)[1].split("?")[0]


def enumerate_leagues(sport: str) -> list[str]:
    slugs: list[str] = []
    page = 1
    while True:
        payload = fetch_json(f"{CORE_BASE}/{sport}/leagues?page={page}")
        items = payload.get("items", [])
        slugs += [s for s in (slug_from_ref(i.get("$ref", "")) for i in items) if s]
        total = int(payload.get("count", 0) or 0)
        # The API decides the page size itself (pageSize param is ignored).
        page_size = int(payload.get("pageSize", 25) or 25)
        if not items or page * page_size >= total:
            break
        page += 1
        time.sleep(0.2)
    return sorted(set(slugs))


def main() -> None:
    parser = argparse.ArgumentParser(description="Enumerate ESPN leagues for in-scope sports.")
    parser.add_argument("--out", default="data/registry/candidates.json")
    parser.add_argument("--sports", nargs="*", default=DEFAULT_SPORTS)
    args = parser.parse_args()

    unknown = [s for s in args.sports if s not in IN_SCOPE_SPORTS]
    if unknown:
        sys.exit(f"Sports outside the NODE.47 scope (football/basket/tennis): {unknown}")

    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    sports_block = {}
    for sport in args.sports:
        slugs = enumerate_leagues(sport)
        sports_block[sport] = {
            "count": len(slugs),
            "competition_ids": slugs,
        }
        print(f"{sport}: {len(slugs)} leagues enumerated from ESPN core API")

    document = {
        "schema_version": "1.0",
        "dataset": "node47_espn_registry_candidates",
        "generated_at_utc": generated_at,
        "method": "Live enumeration of sports.core.api.espn.com/v2/sports/{sport}/leagues",
        "disclaimer": (
            "Every competition_id below comes from ESPN's own enumeration. "
            "Codes are 'candidate' until a scoreboard probe proves they work "
            "(tools/probe_registry.py). Nothing is invented."
        ),
        "sports": sports_block,
        "total_candidates": sum(block["count"] for block in sports_block.values()),
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Candidates written to {out_path} (total: {document['total_candidates']})")


if __name__ == "__main__":
    main()
