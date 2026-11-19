"""Registry contract tests: census, activation and observed collection stay distinct."""
import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO / "config" / "registry.json"
COMPETITIONS_PATH = REPO / "config" / "competitions.json"
ALLOWED_STATUS = {"verified", "candidate", "unavailable"}
ALLOWED_SPORT = {"soccer", "basketball", "tennis"}

def _registry():
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

def _competitions():
    return json.loads(COMPETITIONS_PATH.read_text(encoding="utf-8"))

class RegistryContractTests(unittest.TestCase):
    def test_registry_exists_and_parses(self):
        registry = _registry()
        self.assertEqual(registry["schema_version"], "1.0")
        self.assertIn("entries", registry)

    def test_all_entries_have_required_fields(self):
        required = {"sport", "competition_id", "name", "category", "gender",
                    "zone", "status", "collected", "last_verified", "evidence",
                    "collection_enabled"}
        for entry in _registry()["entries"]:
            missing = required - set(entry)
            self.assertEqual(missing, set(), f"entry {entry.get('competition_id')} misses {missing}")

    def test_statuses_and_sports_are_in_allowed_enums(self):
        for entry in _registry()["entries"]:
            self.assertIn(entry["status"], ALLOWED_STATUS, entry["competition_id"])
            self.assertIn(entry["sport"], ALLOWED_SPORT, entry["competition_id"])

    def test_competition_ids_are_unique_per_sport(self):
        keys = [(e["sport"], e["competition_id"]) for e in _registry()["entries"]]
        self.assertEqual(len(keys), len(set(keys)))

    def test_non_candidate_entries_carry_verification_evidence(self):
        for entry in _registry()["entries"]:
            if entry["status"] == "candidate":
                self.assertIsNone(entry["last_verified"], entry["competition_id"])
            else:
                self.assertIsNotNone(entry["last_verified"], entry["competition_id"])
                self.assertGreaterEqual(entry["evidence"]["http_ok_windows"], 0)
                self.assertTrue(entry["evidence"]["windows"], entry["competition_id"])

    def test_every_verified_entry_has_a_probe_date(self):
        for entry in _registry()["entries"]:
            if entry["status"] == "verified":
                self.assertIsNotNone(entry["last_verified"], entry["competition_id"])

    def test_enabled_competition_routes_are_verified_and_enabled_in_registry(self):
        registry = {(e["sport"], e["competition_id"]): e for e in _registry()["entries"]}
        for competition in _competitions()["competitions"]:
            if not competition.get("enabled", False):
                continue
            key = (competition["sport"], competition["league"])
            self.assertIn(key, registry, f"{key} absent from registry")
            self.assertIn(registry[key]["status"], {"verified", "unavailable"}, f"{key} has invalid active status")
            self.assertTrue(registry[key]["collection_enabled"], f"{key} not configured for collection")
            # Legacy `collected` means included in configured collection; live outcome is in coverage.
            self.assertTrue(registry[key]["collected"], f"{key} not marked as configured for collection")

    def test_enabled_competition_routes_match_registry_activation(self):
        registry = _registry()
        enabled = [c for c in _competitions()["competitions"] if c.get("enabled")]
        configured = {(c["sport"], c["league"]) for c in enabled}
        active_registry = {(e["sport"], e["competition_id"]) for e in registry["entries"] if e["collection_enabled"]}
        self.assertGreater(len(configured), 0)
        self.assertEqual(configured, active_registry)

    def test_catalog_contains_all_requested_sports(self):
        sports = {entry["sport"] for entry in _registry()["entries"]}
        self.assertEqual(sports, ALLOWED_SPORT)

    def test_activation_is_dynamic_and_retains_existing_unavailable_routes(self):
        from tools.activate_verified_competitions import build_activation
        registry = {"entries": [
            {"sport": "soccer", "competition_id": "new.1", "status": "verified"},
            {"sport": "basketball", "competition_id": "nba", "status": "unavailable"},
            {"sport": "tennis", "competition_id": "new.circuit", "status": "candidate"},
        ]}
        config = {"max_workers": 4, "competitions": [{"sport": "basketball", "league": "nba", "enabled": True}]}
        activated, updated_registry = build_activation(registry, config)
        keys = {(x["sport"], x["league"]) for x in activated["competitions"]}
        self.assertEqual(keys, {("soccer", "new.1"), ("basketball", "nba")})
        self.assertEqual(updated_registry["collection_activation"]["enabled_count"], 2)
        self.assertFalse(next(x for x in updated_registry["entries"] if x["competition_id"] == "new.circuit")["collection_enabled"])

    def test_registry_counts_match_entries(self):
        registry = _registry()
        counted = {}
        for entry in registry["entries"]:
            bucket = counted.setdefault(entry["sport"], {"verified": 0, "candidate": 0, "unavailable": 0})
            bucket[entry["status"]] += 1
        for sport, block in registry["counts"].items():
            for status in ("verified", "candidate", "unavailable"):
                self.assertEqual(block[status], counted[sport][status],
                                 f"{sport}/{status} counts mismatch")

if __name__ == "__main__":
    unittest.main()
