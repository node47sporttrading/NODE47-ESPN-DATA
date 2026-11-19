import unittest
from unittest.mock import Mock

from tools.discover_core_leagues import build_candidates, discover_sport, league_slug_from_ref

class CoreLeagueDiscoveryTests(unittest.TestCase):
    def test_extracts_only_expected_sport_league_refs(self):
        self.assertEqual(league_slug_from_ref("https://sports.core.api.espn.com/v2/sports/soccer/leagues/eng.1?lang=en", "soccer"), "eng.1")
        self.assertIsNone(league_slug_from_ref("https://sports.core.api.espn.com/v2/sports/basketball/leagues/nba", "soccer"))
        self.assertIsNone(league_slug_from_ref("https://example.com/leagues/eng.1", "soccer"))

    def test_reads_paginated_collection(self):
        session = Mock()
        first = Mock()
        first.json.return_value = {"pageIndex": 1, "pageCount": 2, "items": [{"$ref": "https://sports.core.api.espn.com/v2/sports/soccer/leagues/eng.1"}]}
        second = Mock()
        second.json.return_value = {"pageIndex": 2, "pageCount": 2, "items": [{"$ref": "https://sports.core.api.espn.com/v2/sports/soccer/leagues/fra.1"}]}
        session.get.side_effect = [first, second]
        self.assertEqual(discover_sport(session, "soccer", limit=1), ["eng.1", "fra.1"])
        self.assertEqual(session.get.call_count, 2)

    def test_merges_core_discovery_and_retains_site_only_routes(self):
        result = build_candidates(
            {"soccer": ["eng.1"], "basketball": ["nba"], "tennis": ["atp"]},
            {"sports": {"soccer": {"competition_ids": ["old.route"]}}},
            {"competitions": [{"sport": "soccer", "league": "site.only", "enabled": True}]},
        )
        self.assertEqual(result["sports"]["soccer"]["competition_ids"], ["eng.1", "old.route", "site.only"])
        self.assertEqual(result["total_candidates"], 5)
        self.assertEqual(result["discovery"]["core_counts"]["soccer"], 1)

if __name__ == "__main__":
    unittest.main()
