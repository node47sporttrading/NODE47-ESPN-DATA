import os
import unittest
import uuid

from node47_espn.postgres_store import PostgresDataStore


@unittest.skipUnless(os.getenv("NODE47_TEST_DATABASE_URL"), "Set NODE47_TEST_DATABASE_URL to run PostgreSQL integration tests")
class PostgresStoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = PostgresDataStore(os.environ["NODE47_TEST_DATABASE_URL"])

    def test_round_trip_and_coverage(self):
        suffix = uuid.uuid4().hex
        event_id = "test-" + suffix
        league = "test-" + suffix
        fetched = "2026-11-19T00:00:00Z"
        event = {
            "event_id": event_id,
            "sport": "test",
            "league": league,
            "start_time_utc": fetched,
            "status": {"state": "pre"},
        }
        dataset = {
            "fetched_at_utc": fetched,
            "requested_date": "test-partial",
            "events": [event],
            "coverage": [{
                "sport": "test",
                "league": league,
                "competition": "PostgreSQL integration test",
                "status": "ok",
                "event_count": 1,
                "error": None,
            }],
        }
        try:
            self.store.save_dataset(dataset)
            self.assertEqual(self.store.get_event(event_id)["event_id"], event_id)
            self.assertEqual(self.store.list_events(sport="test", league=league)[0]["event_id"], event_id)
            self.assertTrue(any(row["league"] == league for row in self.store.get_coverage()))
            self.assertGreaterEqual(self.store.count_events(), 1)
        finally:
            with self.store._connect() as db:
                db.execute("DELETE FROM events WHERE event_id=%s", (event_id,))
                db.execute("DELETE FROM coverage WHERE sport=%s AND league=%s", ("test", league))


if __name__ == "__main__":
    unittest.main()
