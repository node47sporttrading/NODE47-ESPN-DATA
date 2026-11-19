#!/usr/bin/env python3
"""Activate every registry competition whose endpoint status is verified."""
from __future__ import annotations
import argparse
import json
from pathlib import Path


def build_activation(registry: dict, config: dict, expected_total: int = 237):
    entries = registry.get("entries", [])
    verified = [entry for entry in entries if entry.get("status") == "verified"]
    keys = [(entry.get("sport"), entry.get("competition_id")) for entry in verified]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate verified competition keys in registry")
    if expected_total and len(verified) != expected_total:
        raise ValueError(f"Expected {expected_total} verified routes, found {len(verified)}")
    counts = {}
    for entry in verified:
        counts[entry["sport"]] = counts.get(entry["sport"], 0) + 1
    activated_config = dict(config)
    activated_config["collection_mode"] = "all_verified_registry_entries"
    activated_config["max_workers"] = max(1, min(int(config.get("max_workers", 4)), 12))
    activated_config["competitions"] = [
        {"sport": entry["sport"], "league": entry["competition_id"],
         "name": entry.get("name") or entry["competition_id"], "enabled": True,
         "registry_status": "verified"}
        for entry in verified
    ]
    activated_registry = dict(registry)
    activated_registry["collection_activation"] = {
        "enabled_at_version": "0.0.7",
        "mode": "all_verified_registry_entries",
        "enabled_count": len(verified),
        "by_sport": counts,
        "semantics": "collected and collection_enabled indicate inclusion in the configured collector; observed request outcomes are recorded separately in the coverage manifest."
    }
    activated_registry["entries"] = [
        {**entry, "collected": entry.get("status") == "verified", "collection_enabled": entry.get("status") == "verified"}
        for entry in entries
    ]
    return activated_config, activated_registry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", default="config/registry.json")
    parser.add_argument("--config", default="config/competitions.json")
    parser.add_argument("--expected-total", type=int, default=237)
    args = parser.parse_args()
    registry_path, config_path = Path(args.registry), Path(args.config)
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    config = json.loads(config_path.read_text(encoding="utf-8"))
    activated_config, activated_registry = build_activation(registry, config, args.expected_total)
    config_path.write_text(json.dumps(activated_config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    registry_path.write_text(json.dumps(activated_registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Configured {len(activated_config['competitions'])} active ESPN routes: " +
          ", ".join(f"{sport}={count}" for sport, count in sorted(activated_registry["collection_activation"]["by_sport"].items())))


if __name__ == "__main__":
    main()
