import unittest

from node47_espn.football_model import (
    backtest_football, calculate_edge_ev, calculate_stake_u,
    no_vig_probabilities, predict_football,
)


class FootballModelTests(unittest.TestCase):
    def setUp(self):
        self.home = {"goals_for_per_match": 1.8, "goals_against_per_match": 0.8,
                     "sample_matches": 12}
        self.away = {"goals_for_per_match": 1.2, "goals_against_per_match": 1.5,
                     "sample_matches": 10}

    def test_poisson_probabilities_sum_to_one_and_are_gated(self):
        result = predict_football(self.home, self.away)
        self.assertAlmostEqual(sum(result["probabilities"][k] for k in
                                   ("home_win", "draw", "away_win")), 1.0, places=5)
        self.assertEqual(result["model_status"], "baseline_uncalibrated")
        self.assertFalse(result["betting_eligible"])

    def test_insufficient_sample_is_flagged(self):
        home = dict(self.home, sample_matches=2)
        result = predict_football(home, self.away)
        self.assertEqual(result["sample_adequacy"], "insufficient")

    def test_no_vig_normalizes_market(self):
        probs = no_vig_probabilities({"home": 2.0, "draw": 3.5, "away": 4.0})
        self.assertAlmostEqual(sum(probs.values()), 1.0)

    def test_ev_is_blocked_without_validation(self):
        result = calculate_edge_ev(0.6, 2.0, model_validated=False)
        self.assertEqual(result["decision"], "NO BET")
        self.assertEqual(result["block_reason"], "model_not_validated")

    def test_u_stake_zero_without_validation_and_capped_when_valid(self):
        blocked = calculate_stake_u(model_probability=0.6, decimal_odds=2.0,
                                    bankroll_units=100, model_validated=False)
        self.assertEqual(blocked["stake_u"], 0.0)
        allowed = calculate_stake_u(model_probability=0.7, decimal_odds=2.0,
                                    bankroll_units=100, model_validated=True,
                                    kelly_fraction=0.25, max_stake_u=1.0)
        self.assertEqual(allowed["stake_u"], 1.0)

    def test_chronological_backtest_is_explicitly_not_validation(self):
        rows = []
        for day in range(10):
            rows.append({
                "prediction_time": f"2026-01-{day + 1:02d}T12:00:00Z",
                "home": self.home, "away": self.away,
                "actual_home_goals": 2, "actual_away_goals": 1,
                "decimal_odds_home": 1.8, "decimal_odds_draw": 3.5,
                "decimal_odds_away": 4.5,
            })
        result = backtest_football(rows)
        self.assertEqual(result["status"], "evaluation_only_not_model_validation")
        self.assertEqual(result["out_of_sample_rows"], 2)
        self.assertEqual(result["validation_status"], "not_validated")


if __name__ == "__main__":
    unittest.main()
