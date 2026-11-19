import unittest
from node47_espn.normalizer import normalize_scoreboard


class NormalizerTests(unittest.TestCase):
    def test_normalizes_event_and_score(self):
        payload = {"events": [{"id": "123", "name": "A at B", "date": "2026-11-19T18:00:00Z",
            "status": {"type": {"state": "pre", "name": "STATUS_SCHEDULED"}},
            "competitions": [{"venue": {"fullName": "Arena"}, "competitors": [
                {"homeAway": "home", "team": {"id": "1", "displayName": "Home"}, "score": "0"},
                {"homeAway": "away", "team": {"id": "2", "displayName": "Away"}, "score": "0"}]}]}]}
        events = normalize_scoreboard(payload, "basketball", "nba", "NBA")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_id"], "123")
        self.assertEqual(events[0]["participants"]["home"]["name"], "Home")
        self.assertEqual(events[0]["start_time_utc"], "2026-11-19T18:00:00Z")

    def test_tennis_direct_match_event_is_supported(self):
        payload = {"events": [{"id": "tennis-1", "date": "2026-11-19T10:00:00Z",
            "competitions": [{"competitors": [
                {"homeAway": "home", "athlete": {"id": "a1", "displayName": "Player A"}, "score": "6"},
                {"homeAway": "away", "athlete": {"id": "b1", "displayName": "Player B"}, "score": "4"}]}]}]}
        event = normalize_scoreboard(payload, "tennis", "atp", "ATP")[0]
        self.assertEqual(event["participants"]["home"]["name"], "Player A")
        self.assertEqual(event["participants"]["away"]["name"], "Player B")

    def test_tennis_tournament_groupings_expand_to_individual_matches(self):
        payload = {"events": [{"id": "421-2026", "name": "Example Open", "date": "2026-11-19T00:00:00Z",
            "groupings": [{"grouping": {"id": "1", "displayName": "Men's Singles"},
                "competitions": [{"id": "183332", "date": "2026-11-19T14:40:00Z",
                    "status": {"type": {"state": "pre", "name": "STATUS_SCHEDULED"}},
                    "round": {"displayName": "Quarterfinal"}, "venue": {"fullName": "Center Court"},
                    "competitors": [
                        {"id": "1", "homeAway": "home", "type": "athlete", "athlete": {"id": "a1", "displayName": "Player A"}, "linescores": []},
                        {"id": "2", "homeAway": "away", "type": "athlete", "athlete": {"id": "b1", "displayName": "Player B"}, "linescores": []}]}]}]}]}
        events = normalize_scoreboard(payload, "tennis", "atp", "ATP")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_id"], "183332")
        self.assertEqual(events[0]["tournament_event_id"], "421-2026")
        self.assertEqual(events[0]["draw"], "Men's Singles")
        self.assertEqual(events[0]["round"], "Quarterfinal")
        self.assertEqual(events[0]["participants"]["home"]["name"], "Player A")
        self.assertEqual(events[0]["participants"]["away"]["name"], "Player B")

    def test_empty_scoreboard(self):
        self.assertEqual(normalize_scoreboard({"events": []}, "tennis", "atp", "ATP"), [])


if __name__ == "__main__":
    unittest.main()
