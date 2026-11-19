import os,tempfile,unittest
from unittest.mock import AsyncMock,patch
_TMP=tempfile.TemporaryDirectory()
os.environ["NODE47_DATA_PATH"]=os.path.join(_TMP.name,"api-test.sqlite3")
os.environ["NODE47_DISABLE_SCHEDULER"]="1"
from fastapi.testclient import TestClient
from node47_espn import api
class ApiTests(unittest.TestCase):
 def setUp(self): self.client=TestClient(api.app)
 def tearDown(self): self.client.close()
 def test_health_endpoint(self):
  r=self.client.get("/v1/health"); self.assertEqual(r.status_code,200); self.assertEqual(r.json()["version"],"0.0.8")
 def test_competitions_separates_registry_from_active_collection(self):
  r=self.client.get("/v1/competitions?sport=basketball"); self.assertEqual(r.status_code,200)
  data=r.json(); self.assertGreaterEqual(data["count"],1)
  self.assertTrue(all("collection_enabled" in x for x in data["competitions"]))
 def test_refresh_requires_configured_api_key(self):
  data={"fetched_at_utc":"2026-11-19T12:00:00Z","event_count":0,"coverage":[]}
  with patch.dict(os.environ,{"NODE47_API_KEY":"test-secret"}),patch.object(api,"refresh_data",new=AsyncMock(return_value=data)):
   self.assertEqual(self.client.post("/v1/refresh").status_code,401)
   r=self.client.post("/v1/refresh",headers={"X-API-Key":"test-secret"}); self.assertEqual(r.status_code,200)
if __name__=="__main__": unittest.main()
