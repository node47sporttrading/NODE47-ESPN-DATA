import os
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

_TMP = tempfile.TemporaryDirectory()
os.environ["NODE47_DATA_PATH"] = os.path.join(_TMP.name, "api-test.sqlite3")
os.environ["NODE47_DISABLE_SCHEDULER"] = "1"

from fastapi.testclient import TestClient
from node47_espn import api, searxng_actions


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(api.app)

    def tearDown(self):
        self.client.close()

    def test_health_endpoint(self):
        response = self.client.get("/v1/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["version"], "0.0.26")

    def test_competitions_separates_registry_from_active_collection(self):
        response = self.client.get("/v1/competitions?sport=basketball")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(data["count"], 1)
        self.assertTrue(all("collection_enabled" in item for item in data["competitions"]))

    def test_competition_catalog_supports_dynamic_filters(self):
        response = self.client.get("/v1/competitions?sport=soccer&status=verified&collection_enabled=true")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(data["count"], 0)
        self.assertEqual(data["by_sport"], {"soccer": data["count"]})
        self.assertTrue(all(item["collection_enabled"] for item in data["competitions"]))

    def test_mcp_endpoint_is_mounted(self):
        self.assertTrue(any(getattr(route, "path", None) == "/mcp" for route in api.app.routes))

    def test_searxng_callback_rejects_invalid_secret(self):
        with patch.dict(os.environ, {"SEARXNG_CALLBACK_SECRET": "correct-secret"}):
            response = self.client.post(
                "/v1/searxng/callback",
                headers={"X-NODE47-Callback-Secret": "wrong-secret"},
                json={"request_id": "request-1", "status": "ok", "results": []},
            )
        self.assertEqual(response.status_code, 401)

    def test_searxng_callback_accepts_only_pending_request(self):
        import threading
        event = threading.Event()
        request_id = "request-api-test"
        with searxng_actions._PENDING_LOCK:
            searxng_actions._PENDING[request_id] = {
                "event": event, "payload": None, "created": 0,
            }
        try:
            with patch.dict(os.environ, {"SEARXNG_CALLBACK_SECRET": "correct-secret"}):
                response = self.client.post(
                    "/v1/searxng/callback",
                    headers={"X-NODE47-Callback-Secret": "correct-secret"},
                    json={"request_id": request_id, "status": "ok", "results": []},
                )
            self.assertEqual(response.status_code, 200)
            self.assertTrue(event.is_set())
            self.assertEqual(
                searxng_actions._PENDING[request_id]["payload"]["status"], "ok"
            )
        finally:
            with searxng_actions._PENDING_LOCK:
                searxng_actions._PENDING.pop(request_id, None)

    def test_refresh_requires_configured_api_key(self):
        data = {
            "fetched_at_utc": "2026-11-19T12:00:00Z",
            "event_count": 0,
            "coverage": [],
        }
        with patch.dict(os.environ, {"NODE47_API_KEY": "test-secret"}), patch.object(
            api, "refresh_data", new=AsyncMock(return_value=data)
        ):
            self.assertEqual(self.client.post("/v1/refresh").status_code, 401)
            response = self.client.post(
                "/v1/refresh", headers={"X-API-Key": "test-secret"}
            )
            self.assertEqual(response.status_code, 200)

    
    def test_basketball_prediction_endpoint_returns_uncalibrated_baseline(self):
        payload = {
            "home": {"name": "Spurs", "points_for_per_game": 117.1,
                     "points_against_per_game": 105.9, "pace": 97.7},
            "away": {"name": "Clippers", "points_for_per_game": 111.9,
                     "points_against_per_game": 117.7, "pace": 99.0},
            "market_total": 225.5,
            "market_home_handicap": -15.5
        }
        response = self.client.post("/v1/predictions/basketball", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "baseline_uncalibrated")
        self.assertAlmostEqual(
            response.json()["home_win_probability"] + response.json()["away_win_probability"], 1.0
        )


if __name__ == "__main__":
    unittest.main()
