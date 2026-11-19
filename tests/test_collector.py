import unittest
from unittest.mock import Mock

from node47_espn.collector import collect


def _config():
    return {"competitions": [
        {"sport": "basketball", "league": "nba", "name": "NBA", "enabled": True},
        {"sport": "basketball", "league": "wnba", "name": "WNBA", "enabled": True},
        {"sport": "tennis", "league": "atp", "name": "ATP", "enabled": True},
        {"sport": "tennis", "league": "wta", "name": "WTA", "enabled": False},
    ]}


class CollectorTests(unittest.TestCase):
    def test_routes_with_events_are_marked_ok(self):
        client = Mock()
        client.scoreboard.return_value = {"events": [{
            "id": "1", "name": "A at B", "date": "2026-11-19T18:00:00Z",
            "competitions": [{"competitors": [
                {"homeAway": "home", "team": {"id": "1", "displayName": "A"}},
                {"homeAway": "away", "team": {"id": "2", "displayName": "B"}},
            ]}],
        }]}
        dataset = collect(_config(), client)
        nba = next(r for r in dataset["coverage"] if r["league"] == "nba")
        self.assertEqual(nba["status"], "ok")
        self.assertEqual(nba["event_count"], 1)
        self.assertEqual(dataset["event_count"], 3)

    def test_empty_scoreboard_is_not_unavailable(self):
        client = Mock()
        client.scoreboard.return_value = {"events": []}
        dataset = collect(_config(), client)
        wnba = next(r for r in dataset["coverage"] if r["league"] == "wnba")
        self.assertEqual(wnba["status"], "empty")
        self.assertIsNone(wnba["error"])

    def test_failed_route_is_isolated_and_marked_unavailable(self):
        client = Mock()
        ok_payload = {"events": [{
            "id": "1", "name": "A at B", "date": "2026-11-19T18:00:00Z",
            "competitions": [{"competitors": [
                {"homeAway": "home", "team": {"id": "1", "displayName": "A"}},
                {"homeAway": "away", "team": {"id": "2", "displayName": "B"}},
            ]}],
        }]}
        client.scoreboard.side_effect = [ok_payload, ok_payload, RuntimeError("boom")]
        dataset = collect(_config(), client)
        by_league = {r["league"]: r for r in dataset["coverage"]}
        self.assertEqual(by_league["nba"]["status"], "ok")
        self.assertEqual(by_league["wnba"]["status"], "ok")
        self.assertEqual(by_league["atp"]["status"], "unavailable")
        self.assertIn("boom", by_league["atp"]["error"])
        self.assertEqual(dataset["event_count"], 2)

    def test_disabled_routes_are_not_requested(self):
        client = Mock()
        client.scoreboard.return_value = {"events": []}
        dataset = collect(_config(), client)
        self.assertNotIn("wta", [r["league"] for r in dataset["coverage"]])
        self.assertEqual(client.scoreboard.call_count, 3)


if __name__ == "__main__":
    unittest.main()
