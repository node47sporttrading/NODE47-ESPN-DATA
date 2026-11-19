#!/usr/bin/env python3
"""V0.0.5 verification - probe every candidate scoreboard endpoint with the real client.

For each (sport, competition_id): three windows (D-N, today, D+N) are requested
through node47_espn.client.ESPNClient, the same client the collector uses.

Verdicts:
  verified    = at least one window returned HTTP 200 + a JSON object whose
                "events" field is a list (schema validated).
  unavailable = every window failed (HTTP error, invalid JSON, bad schema).
An empty scoreboard (events: []) is a LEGITIMATE answer and still counts as
verified: empty is not unavailable (constraint 2 of the project charter).

The run is checkpointed to a JSONL file and resumable: already-probed
competitions are skipped on re-run.

Usage:
    PYTHONPATH=src python3 tools/probe_registry.py \
        [--candidates data/registry/candidates.json] \
        [--out data/registry/evidence.json] \
        [--checkpoint data/registry/probe_checkpoint.jsonl] \
        [--window-days 7] [--workers 4]
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from node47_espn.client import ESPNClient  # noqa: E402

DEFAULT_BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"

_lock = threading.Lock()
_tls = threading.local()


def get_client(timeout: int, retries: int) -> ESPNClient:
    if not hasattr(_tls, "client"):
        _tls.client = ESPNClient(DEFAULT_BASE_URL, timeout=timeout, retries=retries)
    return _tls.client


def window_dates(window_days: int) -> list[str]:
    today = datetime.now(timezone.utc).date()
    offsets = [-window_days, 0, window_days]
    return [(today + timedelta(days=o)).strftime("%Y%m%d") for o in offsets]


def probe_league(sport: str, league: str, dates: list[str], timeout: int, retries: int) -> dict:
    windows = []
    for date in dates:
        record = {"date": date, "ok": False, "event_count": 0, "espn_name": None, "error": None}
        try:
            payload = get_client(timeout, retries).scoreboard(sport, league, date=date)
            events = payload.get("events")
            if not isinstance(events, list):
                record["error"] = "schema: events field missing or not a list"
            else:
                record["ok"] = True
                record["event_count"] = len(events)
                leagues = payload.get("leagues") or []
                if isinstance(leagues, list) and leagues and isinstance(leagues[0], dict):
                    record["espn_name"] = leagues[0].get("name")
        except Exception as exc:  # single window failure stays isolated
            record["error"] = str(exc)[:300]
        windows.append(record)
        time.sleep(random.uniform(0.05, 0.15))
    ok_windows = [w for w in windows if w["ok"]]
    names = [w["espn_name"] for w in ok_windows if w["espn_name"]]
    return {
        "sport": sport,
        "competition_id": league,
        "verdict": "verified" if ok_windows else "unavailable",
        "last_verified": datetime.now(timezone.utc).date().isoformat(),
        "windows": windows,
        "http_ok_windows": len(ok_windows),
        "events_seen_max": max((w["event_count"] for w in ok_windows), default=0),
        "sample_event_date": next((w["date"] for w in ok_windows if w["event_count"] > 0), None),
        "espn_name": names[0] if names else None,
        "last_error": next((w["error"] for w in windows if w["error"]), None),
    }


def load_checkpoint(path: Path) -> dict:
    done = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
                done[(item["sport"], item["competition_id"])] = item["result"]
            except (KeyError, ValueError):
                continue
    return done


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe candidate ESPN scoreboard endpoints.")
    parser.add_argument("--candidates", default="data/registry/candidates.json")
    parser.add_argument("--out", default="data/registry/evidence.json")
    parser.add_argument("--checkpoint", default="data/registry/probe_checkpoint.jsonl")
    parser.add_argument("--window-days", type=int, default=7)
    parser.add_argument("--dates", default=None,
                        help="Comma-separated ESPN dates YYYYMMDD overriding the window-days heuristic")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--sport", default=None, help="Probe only this sport (soccer/basketball/tennis)")
    args = parser.parse_args()

    candidates_doc = json.loads(Path(args.candidates).read_text(encoding="utf-8"))
    tasks = []
    for sport, block in candidates_doc["sports"].items():
        if args.sport and sport != args.sport:
            continue
        tasks += [(sport, league) for league in block["competition_ids"]]
    tasks.sort()

    checkpoint_path = Path(args.checkpoint)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    done = load_checkpoint(checkpoint_path)
    pending = [(s, l) for (s, l) in tasks if (s, l) not in done]
    print(f"Candidates: {len(tasks)} | already probed: {len(done)} | pending: {len(pending)}")

    dates = args.dates.split(",") if args.dates else window_dates(args.window_days)
    checkpoint_file = checkpoint_path.open("a", encoding="utf-8")
    results = dict(done)
    processed = 0

    def record_result(result: dict) -> None:
        key = (result["sport"], result["competition_id"])
        results[key] = result
        with _lock:
            checkpoint_file.write(json.dumps({"sport": key[0], "competition_id": key[1], "result": result},
                                             ensure_ascii=False) + "\n")
            checkpoint_file.flush()

    started = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(probe_league, s, l, dates, args.timeout, args.retries) for s, l in pending]
        for future in as_completed(futures):
            result = future.result()
            record_result(result)
            processed += 1
            if processed % 25 == 0 or processed == len(pending):
                rate = processed / max(time.time() - started, 0.001)
                print(f"  probed {processed}/{len(pending)} ({rate:.1f}/s)")

    ordered = [results[(s, l)] for (s, l) in tasks if (s, l) in results]
    verdicts = {"verified": 0, "unavailable": 0}
    by_sport = {}
    for item in ordered:
        verdicts[item["verdict"]] += 1
        by_sport.setdefault(item["sport"], {"verified": 0, "unavailable": 0})
        by_sport[item["sport"]][item["verdict"]] += 1

    evidence = {
        "schema_version": "1.0",
        "dataset": "node47_espn_registry_evidence",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "probe_base_url": DEFAULT_BASE_URL,
        "windows": dates,
        "window_days": args.window_days,
        "verdict_rule": (
            "verified = at least one window HTTP 200 + JSON object with a list 'events' field; "
            "unavailable = every window failed. Empty scoreboards remain verified (constraint 2)."
        ),
        "probed_count": len(ordered),
        "verdicts": verdicts,
        "by_sport": by_sport,
        "results": ordered,
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Evidence written to {out_path}: {verdicts['verified']} verified, {verdicts['unavailable']} unavailable")


if __name__ == "__main__":
    main()
