import unittest

from node47_espn.football_model import calculate_edge_ev, no_vig_probabilities, predict_football
from node47_espn.multisport_decision import robot_stake


class FootballModelTests(unittest.TestCase):
    def setUp(self):
        self.home = {"goals_for_per_match": 1.8, "goals_against_per_match": 0.8,
                     "sample_matches": 12}
        self.away = {"goals_for_per_match": 1.2, "goals_against_per_match": 1.5,
                     "sample_matches": 10}

    def test_poisson_probabilities_sum_to_one(self):
        result = predict_football(self.home, self.away)
        self.assertAlmostEqual(sum(result["probabilities"][k] for k in
                                   ("home_win", "draw", "away_win")), 1.0, places=5)
        self.assertEqual(result["model_status"], "baseline_uncalibrated")
        self.assertNotIn("betting_eligible", result)

    def test_insufficient_sample_is_flagged(self):
        home = dict(self.home, sample_matches=2)
        result = predict_football(home, self.away)
        self.assertEqual(result["sample_adequacy"], "insufficient")

    def test_no_vig_normalizes_market(self):
        probs = no_vig_probabilities({"home": 2.0, "draw": 3.5, "away": 4.0})
        self.assertAlmostEqual(sum(probs.values()), 1.0)

    def test_ev_uses_supplied_probability_and_price(self):
        result = calculate_edge_ev(0.6, 2.0)
        self.assertEqual(result["decision"], "VALUE_CANDIDATE")
        self.assertAlmostEqual(result["ev_per_unit"], 0.2)
        self.assertNotIn("model_validated", result)

    def test_robot_native_stake_calculator_uses_profile(self):
        result = robot_stake("football", 0.60, 80, 2.0, profile="STANDARD")
        self.assertAlmostEqual(result["p_cons"], 0.59)
        self.assertEqual(result["stake_u"], 3.0)


if __name__ == "__main__":
    unittest.main()
