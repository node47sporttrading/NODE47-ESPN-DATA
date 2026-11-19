import unittest
from node47_espn.normalizer import normalize_scoreboard


class NormalizerTests(unittest.TestCase):
    def test_normalizes_event_and_score(self):
        payload = {"events": [{
            "id": "123", "name": "A at B", "date": "2026-11-19T18:00:00Z",
            "status": {"type": {"state": "pre", "name": "STATUS_SCHEDULED"}},
            "competitions": [{"venue": {"fullName": "Arena"}, "competitors": [
                {"homeAway": "home", "team": {"id": "1", "displayName": "Home"}, "score": "0"},
                {"homeAway": "away", "team": {"id": "2", "displayName": "Away"}, "score": "0"}
            ]}]
        }]}
        events = normalize_scoreboard(payload, "basketball", "nba", "NBA")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_id"], "123")
        self.assertEqual(events[0]["participants"]["home"]["name"], "Home")
        self.assertEqual(events[0]["start_time_utc"], "2026-11-19T18:00:00Z")

    def test_empty_scoreboard(self):
        self.assertEqual(normalize_scoreboard({"events": []}, "tennis", "atp", "ATP"), [])


if __name__ == "__main__":
    unittest.main()
