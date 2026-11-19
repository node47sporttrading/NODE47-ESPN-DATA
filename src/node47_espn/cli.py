"""CLI entry point used by GitHub Actions and local runs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

from .client import ESPNClient
from .collector import collect


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/competitions.json")
    parser.add_argument("--output", default="site")
    parser.add_argument("--date", default=None, help="Optional ESPN date filter YYYYMMDD")
    args = parser.parse_args()

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    client = ESPNClient(
        config["base_url"],
        timeout=int(config.get("request_timeout_seconds", 20)),
        retries=int(config.get("retries", 2)),
    )
    dataset = collect(config, client, date=args.date)
    output = Path(args.output)
    (output / "data").mkdir(parents=True, exist_ok=True)
    (output / "manifests").mkdir(parents=True, exist_ok=True)

    latest = output / "data" / "latest.json"
    latest.write_text(json.dumps(dataset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "dataset": dataset["dataset"],
        "fetched_at_utc": dataset["fetched_at_utc"],
        "event_count": dataset["event_count"],
        "competition_count": len(dataset["coverage"]),
        "coverage": dataset["coverage"],
    }
    (output / "manifests" / "latest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    index = {
        "service": "NODE.47 ESPN DATA",
        "version": "0.3.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "latest_dataset": "data/latest.json",
        "manifest": "manifests/latest.json",
    }
    (output / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    (output / "index.html").write_text(
        "<!doctype html><html lang='en'><meta charset='utf-8'><title>NODE.47 ESPN DATA</title>"
        "<h1>NODE.47 ESPN DATA</h1><p>Multisport snapshot. See <a href='data/latest.json'>latest.json</a> "
        "and <a href='manifests/latest.json'>coverage manifest</a>.</p></html>\n",
        encoding="utf-8",
    )
    print(f"Collected {dataset['event_count']} events across {len(dataset['coverage'])} competition routes.")


if __name__ == "__main__":
    main()
