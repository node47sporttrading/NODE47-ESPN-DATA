import os
import tempfile
import unittest

_TMP = tempfile.TemporaryDirectory()
os.environ["NODE47_DATA_PATH"] = os.path.join(_TMP.name, "module-test.sqlite3")
os.environ["NODE47_DISABLE_SCHEDULER"] = "1"

from node47_espn.api import _propline_module


class PropLineModuleAdapterTests(unittest.TestCase):
    def test_football_requires_soccer_provider_key(self):
        module, key, markets, config = _propline_module("football", "soccer_england_premier_league")
        self.assertEqual(module, "football")
        self.assertIn("both_teams_to_score", markets)
        self.assertIn("h1", config["periods"])

    def test_basketball_has_game_and_player_markets(self):
        module, key, markets, config = _propline_module("basketball", "basketball_nba")
        self.assertEqual(module, "basketball")
        self.assertIn("player_points", markets)
        self.assertIn("q1", config["periods"])

    def test_tennis_uses_single_provider_key_and_tennis_markets(self):
        module, key, markets, config = _propline_module("tennis", "tennis")
        self.assertEqual(key, "tennis")
        self.assertIn("total_sets", markets)
        self.assertIn("player_aces", markets)
        self.assertIn("s1", config["periods"])

    def test_rejects_wrong_sport_key_and_unsupported_market(self):
        with self.assertRaises(ValueError):
            _propline_module("football", "basketball_nba")
        with self.assertRaises(ValueError):
            _propline_module("tennis", "tennis", "player_points")


if __name__ == "__main__":
    unittest.main()
