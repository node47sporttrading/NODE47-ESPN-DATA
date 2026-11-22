import os
import unittest
from fastapi.testclient import TestClient
os.environ["NODE47_DISABLE_SCHEDULER"] = "1"
from node47_espn import api
from node47_espn.tennis_model import predict_tennis
from node47_espn.multisport_decision import robot_stake, edge_ev

class MultisportRobotRiskTests(unittest.TestCase):
    def setUp(self): self.client = TestClient(api.app)
    def tearDown(self): self.client.close()

    def test_tennis_elo_is_symmetric_and_uncalibrated(self):
        a={"name":"A","overall_elo":1800,"matches_played":30}
        b={"name":"B","overall_elo":1600,"matches_played":25}
        result=predict_tennis(a,b,surface="hard")
        self.assertGreater(result["probabilities"]["player_a_win"],0.5)
        self.assertAlmostEqual(sum(result["probabilities"].values()),1.0)
        self.assertEqual(result["status"],"baseline_uncalibrated")
        self.assertNotIn("validation_status", result)
        self.assertNotIn("betting_eligible", result)

    def test_robot_stake_mirrors_native_mise_de(self):
        result=robot_stake("football",0.60,80,2.0,profile="STANDARD")
        self.assertEqual(result["p_cons"],0.59)
        self.assertEqual(result["stake_u"],3.0)

    def test_push_probability_is_included(self):
        result=robot_stake("football",0.50,100,2.0,p_push=0.10,profile="STANDARD")
        self.assertEqual(result["stake_u"],2.5)

    def test_native_profile_caps(self):
        prudent=robot_stake("basketball",0.80,100,2.0,profile="PRUDENT")
        standard=robot_stake("basketball",0.80,100,2.0,profile="STANDARD")
        self.assertEqual(prudent["stake_u"],2.0)
        self.assertEqual(standard["stake_u"],3.0)

    def test_corners_cards_is_a_supported_separate_module(self):
        result=robot_stake("corners_cartons",0.70,80,2.0,profile="CUSTOM",stake_max=4)
        self.assertEqual(result["module"],"corners_cartons")
        self.assertGreater(result["stake_u"],0)

    def test_custom_profile_requires_explicit_cap(self):
        with self.assertRaises(ValueError):
            robot_stake("tennis",0.70,80,2.0,profile="CUSTOM")

    def test_positive_ev_is_reported_without_a_model_gate(self):
        result=edge_ev("football",0.70,2.0)
        self.assertTrue(result["bet_eligible"])
        self.assertEqual(result["decision"],"VALUE_CANDIDATE")
        self.assertNotIn("model_validated",result)

    def test_rest_robot_staking_endpoint(self):
        response=self.client.post("/v1/decision/staking/robot",json={
            "module":"football","p_final":0.60,"confidence":80,
            "decimal_odds":2.0,"profile":"STANDARD"})
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()["stake_u"],3.0)

if __name__ == "__main__": unittest.main()
