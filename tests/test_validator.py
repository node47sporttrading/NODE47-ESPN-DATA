import unittest
from node47_espn.validator import validate_event


class ValidatorTests(unittest.TestCase):
    def test_tennis_competitors_are_not_flagged_as_missing(self):
        event = {"event_id": "t1", "start_time_utc": "2026-11-19T10:00:00Z",
                 "participants": {"home": None, "away": None, "competitors": [{"name": "Player"}]}}
        self.assertNotIn("participants_unavailable", validate_event(event))

    def test_missing_fields_are_flagged(self):
        event = {"event_id": None, "start_time_utc": None, "participants": {}}
        flags = validate_event(event)
        self.assertIn("missing_event_id", flags)
        self.assertIn("missing_or_invalid_start_time", flags)
        self.assertIn("participants_unavailable", flags)
        self.assertEqual(len(event["quality_flags"]), 3)


if __name__ == "__main__":
    unittest.main()
