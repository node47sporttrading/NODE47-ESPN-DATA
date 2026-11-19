import os
import tempfile
import unittest

_TMP = tempfile.TemporaryDirectory()
os.environ["NODE47_DATA_PATH"] = os.path.join(_TMP.name, "module-test.sqlite3")
os.environ["NODE47_DISABLE_SCHEDULER"] = "1"

from node47_espn.api import _propline_market_keys, _propline_module, _validate_propline_period


class PropLineModuleAdapterTests(unittest.TestCase):
    def test_football_catalogue_matches_documented_soccer_markets(self):
        module, key, markets, config = _propline_module("football", "soccer_england_premier_league")
        self.assertEqual(module, "football")
        self.assertIn("both_teams_to_score", config["markets"])
        self.assertIn("total_corners", config["markets"])
        self.assertEqual(_validate_propline_period(config, "h1"), "h1")

    def test_basketball_uses_dynamic_event_market_discovery(self):
        module, key, markets, config = _propline_module("basketball", "basketball_nba")
        self.assertEqual(module, "basketball")
        self.assertTrue(config["dynamic_event_markets"])
        self.assertEqual(_validate_propline_period(config, "q1"), "q1")

    def test_tennis_uses_unified_provider_key_and_dynamic_event_markets(self):
        module, key, markets, config = _propline_module("tennis", "tennis")
        self.assertEqual(key, "tennis")
        self.assertEqual(markets, "h2h,spreads,totals")
        self.assertTrue(config["dynamic_event_markets"])
        self.assertEqual(_validate_propline_period(config, "s1"), "s1")

    def test_rejects_wrong_sport_key_market_and_period(self):
        with self.assertRaises(ValueError):
            _propline_module("football", "basketball_nba")
        with self.assertRaises(ValueError):
            _propline_module("basketball", "basketball_nba", "player_points")
        module, key, markets, config = _propline_module("basketball", "basketball_nba", "player_points", allow_dynamic=True)
        self.assertEqual(markets, "player_points")
        with self.assertRaises(ValueError):
            _validate_propline_period({"periods": ("q1",)}, "s1")

    def test_market_discovery_parses_documented_event_market_array(self):
        self.assertEqual(_propline_market_keys([{"key": "h2h"}, {"key": "player_aces"}]), {"h2h", "player_aces"})


if __name__ == "__main__":
    unittest.main()
