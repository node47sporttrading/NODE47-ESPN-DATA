import unittest

from node47_espn.prediction import ModelConfig, TeamForm, predict_matchup
from node47_espn.evaluation import chronological_split, evaluate_predictions


class PredictionTests(unittest.TestCase):
    def setUp(self):
        self.spurs = TeamForm("Spurs", 117.1, 105.9, 97.7)
        self.clippers = TeamForm("Clippers", 111.9, 117.7, 99.0)

    def test_projection_is_reproducible_and_probabilities_sum_to_one(self):
        result = predict_matchup(self.spurs, self.clippers, market_total=225.5,
                                 market_home_handicap=-15.5)
        self.assertEqual(result["status"], "baseline_uncalibrated")
        self.assertAlmostEqual(result["home_win_probability"] + result["away_win_probability"], 1.0)
        self.assertAlmostEqual(result["over_probability"] + result["under_probability"], 1.0)
        self.assertAlmostEqual(result["home_cover_probability"] + result["away_cover_probability"], 1.0)
        self.assertGreater(result["projected_home_points"], result["projected_away_points"])

    def test_invalid_team_inputs_are_rejected(self):
        bad = TeamForm("Bad", 0, 100, 98)
        with self.assertRaises(ValueError):
            predict_matchup(bad, self.clippers)

    def test_config_can_be_explicitly_overridden(self):
        result = predict_matchup(self.spurs, self.clippers,
                                 config=ModelConfig(home_court_points=0, margin_standard_deviation=10))
        self.assertEqual(result["assumptions"]["home_court_points"], 0)
        self.assertEqual(result["assumptions"]["margin_standard_deviation"], 10)


class EvaluationTests(unittest.TestCase):
    def test_chronological_split_keeps_later_rows_in_test(self):
        rows = [{"prediction_time": f"2026-11-{day:02d}", "value": day} for day in range(1, 11)]
        train, test = chronological_split(rows, test_fraction=0.2)
        self.assertEqual(len(train), 8)
        self.assertEqual(len(test), 2)
        self.assertLess(train[-1]["prediction_time"], test[0]["prediction_time"])

    def test_metrics_and_score_errors(self):
        rows = [
            {"home_win_probability": 0.8, "home_win": 1,
             "predicted_home_score": 110, "predicted_away_score": 100,
             "actual_home_score": 108, "actual_away_score": 102},
            {"home_win_probability": 0.3, "home_win": 0,
             "predicted_home_score": 99, "predicted_away_score": 101,
             "actual_home_score": 100, "actual_away_score": 104},
        ]
        result = evaluate_predictions(rows)
        self.assertEqual(result["sample_size"], 2)
        self.assertEqual(result["accuracy"], 1.0)
        self.assertAlmostEqual(result["brier_score"], 0.065)
        self.assertIn("score_mae", result)
        self.assertIn("score_rmse", result)

    def test_invalid_probability_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_predictions([{"home_win_probability": 1.2, "home_win": 1}])


if __name__ == "__main__":
    unittest.main()
