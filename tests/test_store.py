import tempfile,unittest
from pathlib import Path
from node47_espn.store import DataStore
class StoreTests(unittest.TestCase):
 def test_persists_and_filters_events_and_coverage(self):
  with tempfile.TemporaryDirectory() as tmp:
   store=DataStore(Path(tmp)/"test.sqlite3")
   data={"fetched_at_utc":"2026-11-19T12:00:00Z","event_count":1,"events":[{"event_id":"e1","sport":"basketball","league":"nba","start_time_utc":"2026-11-20T00:00:00Z","status":{"state":"pre"}}],"coverage":[{"sport":"basketball","league":"nba","competition":"NBA","status":"ok","event_count":1,"error":None}]}
   store.save_dataset(data); self.assertEqual(store.count_events(),1)
   self.assertEqual(store.list_events(sport="basketball")[0]["event_id"],"e1")
   self.assertEqual(store.get_event("e1")["league"],"nba")
   self.assertEqual(store.get_coverage()[0]["status"],"ok")
   self.assertEqual(store.get_meta()["last_refresh_utc"],data["fetched_at_utc"])
 def test_missing_event_returns_none(self):
  with tempfile.TemporaryDirectory() as tmp: self.assertIsNone(DataStore(Path(tmp)/"x.sqlite3").get_event("missing"))
if __name__=="__main__": unittest.main()
