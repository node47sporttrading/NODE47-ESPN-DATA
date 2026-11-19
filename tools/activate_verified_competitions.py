#!/usr/bin/env python3
"""Activate verified routes and retain previously active routes during transient probe failures."""
from __future__ import annotations
import argparse
import json
from pathlib import Path


def build_activation(registry: dict, config: dict, expected_total: int = 0):
    entries = registry.get("entries", [])
    previously_active = {(item.get("sport"), item.get("league")) for item in config.get("competitions", []) if item.get("enabled")}
    eligible = [entry for entry in entries if entry.get("status") == "verified" or (entry.get("sport"), entry.get("competition_id")) in previously_active]
    keys = [(entry.get("sport"), entry.get("competition_id")) for entry in eligible]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate eligible competition keys in registry")
    if expected_total and len(eligible) != expected_total:
        raise ValueError(f"Expected {expected_total} routes, found {len(eligible)}")
    counts = {}
    for entry in eligible:
        counts[entry["sport"]] = counts.get(entry["sport"], 0) + 1
    activated_config = dict(config)
    activated_config["collection_mode"] = "verified_plus_previously_active"
    activated_config["max_workers"] = max(1, min(int(config.get("max_workers", 4)), 12))
    activated_config["competitions"] = [
        {"sport": entry["sport"], "league": entry["competition_id"], "name": entry.get("name") or entry["competition_id"], "enabled": True, "registry_status": entry.get("status")}
        for entry in eligible
    ]
    activated_registry = dict(registry)
    activated_registry["collection_activation"] = {
        "enabled_at_version": "0.0.14",
        "mode": "verified_plus_previously_active",
        "enabled_count": len(eligible),
        "by_sport": counts,
        "semantics": "New routes require a successful scoreboard schema probe. Previously active routes remain configured during temporary probe failures; actual collection status is reported separately in coverage.",
    }
    eligible_keys = set(keys)
    activated_registry["entries"] = [
        {**entry, "collected": (entry.get("sport"), entry.get("competition_id")) in eligible_keys, "collection_enabled": (entry.get("sport"), entry.get("competition_id")) in eligible_keys}
        for entry in entries
    ]
    return activated_config, activated_registry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", default="config/registry.json")
    parser.add_argument("--config", default="config/competitions.json")
    parser.add_argument("--expected-total", type=int, default=0, help="Optional exact route-count guard; 0 disables a fixed-count assumption")
    args = parser.parse_args()
    registry_path, config_path = Path(args.registry), Path(args.config)
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    config = json.loads(config_path.read_text(encoding="utf-8"))
    activated_config, activated_registry = build_activation(registry, config, args.expected_total)
    config_path.write_text(json.dumps(activated_config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    registry_path.write_text(json.dumps(activated_registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Enabled {len(activated_config['competitions'])} verified ESPN routes: " +
          ", ".join(f"{sport}={count}" for sport, count in sorted(activated_registry["collection_activation"]["by_sport"].items())))


if __name__ == "__main__":
    main()
