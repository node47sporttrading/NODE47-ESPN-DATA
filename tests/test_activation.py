import unittest

from tools.activate_verified_competitions import build_activation

class ActivationTests(unittest.TestCase):
    def test_new_routes_require_verification_and_existing_routes_survive_outage(self):
        registry = {"entries": [
            {"sport": "soccer", "competition_id": "old.league", "name": "Old", "status": "unavailable"},
            {"sport": "soccer", "competition_id": "new.league", "name": "New", "status": "verified"},
            {"sport": "basketball", "competition_id": "candidate.league", "name": "Candidate", "status": "candidate"},
        ]}
        config = {"max_workers": 4, "competitions": [
            {"sport": "soccer", "league": "old.league", "enabled": True},
        ]}
        active, enriched = build_activation(registry, config)
        keys = {(item["sport"], item["league"]) for item in active["competitions"]}
        self.assertEqual(keys, {("soccer", "old.league"), ("soccer", "new.league")})
        statuses = {(item["sport"], item["competition_id"]): item["status"] for item in enriched["entries"]}
        self.assertEqual(statuses[("soccer", "old.league")], "unavailable")
        self.assertFalse(enriched["entries"][2]["collection_enabled"])

if __name__ == "__main__":
    unittest.main()
