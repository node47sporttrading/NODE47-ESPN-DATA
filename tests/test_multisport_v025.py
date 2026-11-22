import os
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient

os.environ["NODE47_DISABLE_SCHEDULER"] = "1"
from node47_espn import api
from node47_espn.tennis_model import predict_tennis
from node47_espn.multisport_decision import edge_ev, stake_u

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

    def test_tennis_api(self):
        payload={"player_a":{"name":"A","overall_elo":1800,"matches_played":30},
                 "player_b":{"name":"B","overall_elo":1600,"matches_played":25},
                 "surface":"clay","best_of":3}
        r=self.client.post("/v1/predictions/tennis",json=payload)
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json()["rating_basis"],"overall_elo")


    def test_basketball_backtest_endpoint(self):
        rows = []
        for index in range(4):
            rows.append({
                "prediction_time": f"2026-01-0{index+1}T12:00:00Z",
                "home": {"name":"Home","points_for_per_game":110.0,"points_against_per_game":105.0,"pace":98.0},
                "away": {"name":"Away","points_for_per_game":108.0,"points_against_per_game":107.0,"pace":97.0},
                "actual_home_score": 112.0,
                "actual_away_score": 104.0,
            })
        response = self.client.post("/v1/backtests/basketball",
                                    json={"rows":rows,"test_fraction":0.25})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "evaluation_only_not_model_validation")
        self.assertEqual(response.json()["out_of_sample_rows"], 1)
        self.assertEqual(response.json()["validation_status"], "not_validated")

    def test_all_sports_default_no_bet_zero_u(self):
        for sport in ("football","basketball","tennis"):
            result=stake_u(sport,0.7,2.0,100)
            self.assertEqual(result["decision"],"NO BET")
            self.assertEqual(result["stake_u"],0.0)

    def test_sport_validation_is_independent(self):
        with patch.dict(os.environ, {
            "NODE47_TENNIS_MODEL_VALIDATED":"1",
            "NODE47_TENNIS_VALIDATION_ID":"tennis-audit-001",
        }, clear=False):
            self.assertTrue(edge_ev("tennis",0.7,2.0)["bet_eligible"])
            self.assertFalse(edge_ev("football",0.7,2.0)["bet_eligible"])
            self.assertFalse(edge_ev("basketball",0.7,2.0)["bet_eligible"])

    def test_stake_caps_cannot_be_raised_by_request(self):
        with self.assertRaises(ValueError):
            stake_u("tennis",0.7,2.0,100,max_stake_u=5)
        with self.assertRaises(ValueError):
            stake_u("tennis",0.7,2.0,100,kelly_fraction=0.5)

if __name__ == "__main__":
    unittest.main()
