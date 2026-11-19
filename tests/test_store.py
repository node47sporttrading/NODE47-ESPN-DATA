import tempfile
import unittest
from pathlib import Path
from node47_espn.store import DataStore


class StoreTests(unittest.TestCase):
    def test_persists_and_filters_events_and_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = DataStore(Path(tmp) / "test.sqlite3")
            data = {"fetched_at_utc": "2026-11-19T12:00:00Z", "event_count": 1,
                "events": [{"event_id": "e1", "sport": "basketball", "league": "nba",
                    "start_time_utc": "2026-11-20T00:00:00Z", "status": {"state": "pre"}}],
                "coverage": [{"sport": "basketball", "league": "nba", "competition": "NBA",
                    "status": "ok", "event_count": 1, "error": None}]}
            store.save_dataset(data)
            self.assertEqual(store.count_events(), 1)
            self.assertEqual(store.list_events(sport="basketball")[0]["event_id"], "e1")
            self.assertEqual(store.get_event("e1")["league"], "nba")
            self.assertEqual(store.get_coverage()[0]["status"], "ok")
            self.assertEqual(store.get_meta()["last_refresh_utc"], data["fetched_at_utc"])

    def test_successful_full_snapshot_prunes_stale_events_for_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = DataStore(Path(tmp) / "test.sqlite3")
            base = {"sport": "tennis", "league": "atp", "competition": "ATP"}
            store.save_dataset({"fetched_at_utc": "2026-11-19T10:00:00Z", "event_count": 2,
                "events": [{"event_id": "old", **base}, {"event_id": "keep", **base}],
                "coverage": [{"sport": "tennis", "league": "atp", "competition": "ATP",
                    "status": "ok", "event_count": 2}]})
            result = store.save_dataset({"fetched_at_utc": "2026-11-19T10:15:00Z", "event_count": 1,
                "events": [{"event_id": "keep", **base}],
                "coverage": [{"sport": "tennis", "league": "atp", "competition": "ATP",
                    "status": "ok", "event_count": 1}]})
            self.assertEqual(store.count_events(), 1)
            self.assertIsNone(store.get_event("old"))
            self.assertIsNotNone(store.get_event("keep"))
            self.assertEqual(result["deleted_stale_count"], 1)

    def test_unavailable_route_preserves_previous_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = DataStore(Path(tmp) / "test.sqlite3")
            event = {"event_id": "old", "sport": "soccer", "league": "eng.1"}
            store.save_dataset({"fetched_at_utc": "2026-11-19T10:00:00Z", "events": [event],
                "coverage": [{"sport": "soccer", "league": "eng.1", "competition": "EPL", "status": "ok"}]})
            store.save_dataset({"fetched_at_utc": "2026-11-19T10:15:00Z", "events": [],
                "coverage": [{"sport": "soccer", "league": "eng.1", "competition": "EPL", "status": "unavailable"}]})
            self.assertIsNotNone(store.get_event("old"))

    def test_date_scoped_snapshot_never_prunes_other_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = DataStore(Path(tmp) / "test.sqlite3")
            event = {"event_id": "future", "sport": "tennis", "league": "atp"}
            store.save_dataset({"fetched_at_utc": "2026-11-19T10:00:00Z", "events": [event],
                "coverage": [{"sport": "tennis", "league": "atp", "competition": "ATP", "status": "ok"}]})
            store.save_dataset({"fetched_at_utc": "2026-11-19T10:15:00Z", "requested_date": "20261119",
                "events": [], "coverage": [{"sport": "tennis", "league": "atp", "competition": "ATP", "status": "empty"}]})
            self.assertIsNotNone(store.get_event("future"))

    def test_missing_event_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(DataStore(Path(tmp) / "x.sqlite3").get_event("missing"))


if __name__ == "__main__":
    unittest.main()
