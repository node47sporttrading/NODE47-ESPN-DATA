import os
import json
import tempfile
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient

os.environ["NODE47_DISABLE_SCHEDULER"] = "1"
from node47_espn import api
from node47_espn.tennis_model import predict_tennis
from node47_espn.multisport_decision import edge_ev, stake_u, validation_state

class MultisportV025Tests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(api.app)

    def tearDown(self):
        self.client.close()

    def test_tennis_elo_is_symmetric_and_uncalibrated(self):
        a = {"name":"A","overall_elo":1800,"matches_played":30}
        b = {"name":"B","overall_elo":1600,"matches_played":25}
        result = predict_tennis(a,b,surface="hard")
        self.assertGreater(result["probabilities"]["player_a_win"], 0.5)
        self.assertAlmostEqual(sum(result["probabilities"].values()),1.0)
        self.assertEqual(result["status"],"baseline_uncalibrated")
        self.assertFalse(result["betting_eligible"])

    def test_tennis_elo_extreme_ratings_remain_finite(self):
        a = {"name":"A","overall_elo":1000000,"matches_played":20}
        b = {"name":"B","overall_elo":0,"matches_played":20}
        result = predict_tennis(a,b)
        self.assertEqual(result["probabilities"]["player_a_win"], 1.0)
        self.assertEqual(result["probabilities"]["player_b_win"], 0.0)

    def test_tennis_api(self):
        payload={"player_a":{"name":"A","overall_elo":1800,"matches_played":30},
                 "player_b":{"name":"B","overall_elo":1600,"matches_played":25},
                 "surface":"clay","best_of":3}
        r=self.client.post("/v1/predictions/tennis",json=payload)
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json()["rating_basis"],"overall_elo")



    def test_all_sports_default_no_bet_zero_u(self):
        for sport in ("football","basketball","tennis"):
            result=stake_u(sport,0.7,2.0,100)
            self.assertEqual(result["decision"],"NO BET")
            self.assertEqual(result["stake_u"],0.0)

    def test_shared_staking_rest_gate_blocks_all_sports_by_default(self):
        for sport in ("football", "basketball", "tennis"):
            response = self.client.post("/v1/decision/staking/u", json={
                "sport": sport, "model_probability": 0.7, "decimal_odds": 2.0,
                "bankroll_units": 100,
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["decision"], "NO BET")
            self.assertEqual(response.json()["stake_u"], 0.0)

    def test_validation_registry_requires_complete_independent_evidence(self):
        valid_record = {
            "status": "validated",
            "validation_id": "audit-001",
            "reviewer": {"name": "Independent Reviewer", "independence": "independent"},
            "report_url": "https://example.org/audit.pdf",
            "report_sha256": "a" * 64,
            "validated_at_utc": "2026-11-22T12:00:00Z",
            "protocol": "out_of_sample",
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "validation.json")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump({"sports": {"football": valid_record}}, handle)
            with patch.dict(os.environ, {"NODE47_MODEL_VALIDATION_PATH": path}, clear=False):
                self.assertEqual(validation_state("football"), (True, "audit-001"))
                incomplete = dict(valid_record)
                incomplete.pop("report_sha256")
                with open(path, "w", encoding="utf-8") as handle:
                    json.dump({"sports": {"football": incomplete}}, handle)
                self.assertFalse(validation_state("football")[0])

    def test_legacy_owner_flags_do_not_activate_any_sport(self):
        with patch.dict(os.environ, {
            "NODE47_TENNIS_MODEL_VALIDATED": "1",
            "NODE47_TENNIS_VALIDATION_ID": "legacy-id",
        }, clear=False):
            for sport in ("football", "basketball", "tennis"):
                self.assertFalse(edge_ev(sport, 0.7, 2.0)["bet_eligible"])

    def test_stake_caps_cannot_be_raised_by_request(self):
        with self.assertRaises(ValueError):
            stake_u("tennis",0.7,2.0,100,max_stake_u=5)
        with self.assertRaises(ValueError):
            stake_u("tennis",0.7,2.0,100,kelly_fraction=0.5)

if __name__ == "__main__":
    unittest.main()
