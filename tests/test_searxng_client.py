import unittest
from unittest.mock import Mock, patch

import requests

from node47_espn.searxng_client import SearXNGClient, SearXNGError


class SearXNGClientTests(unittest.TestCase):
    def make_response(self, payload, status_code=200, headers=None):
        response = Mock()
        response.status_code = status_code
        response.ok = status_code < 400
        response.headers = headers or {}
        response.json.return_value = payload
        return response

    def make_client(self, payload, status_code=200):
        session = Mock()
        session.headers = {}
        session.get.return_value = self.make_response(payload, status_code)
        return SearXNGClient("node47-searxng:8080", session=session), session

    def test_search_normalizes_results_and_uses_json_format(self):
        client, session = self.make_client({
            "results": [{
                "title": "Tactical analysis",
                "url": "https://example.com/article",
                "content": "A verified match report.",
                "engine": "example",
                "publishedDate": "2026-11-20",
                "score": 2.1,
            }],
            "unresponsive_engines": [],
        })
        result = client.search("team pressing", max_results=5)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["results"][0]["title"], "Tactical analysis")
        self.assertEqual(session.get.call_args.kwargs["params"]["format"], "json")
        self.assertTrue(client.base_url.startswith("http://"))
        self.assertEqual(session.headers["User-Agent"], "NODE47-SPORT-ANALYT/0.0.17")

    def test_health_checks_json_endpoint(self):
        client, _ = self.make_client({"results": [], "unresponsive_engines": []})
        result = client.health()
        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["json_api"])

    def test_empty_query_is_rejected_before_network_call(self):
        client, session = self.make_client({"results": []})
        with self.assertRaises(ValueError):
            client.search("   ")
        session.get.assert_not_called()

    def test_403_explains_json_format_configuration_without_retry(self):
        client, session = self.make_client({}, status_code=403)
        with self.assertRaisesRegex(SearXNGError, "search.formats"):
            client.search("NODE47")
        session.get.assert_called_once()

    def test_502_retries_and_recovers(self):
        client, session = self.make_client({"results": [{"title": "recovered"}]})
        session.get.side_effect = [
            self.make_response({}, 502),
            self.make_response({"results": [{"title": "recovered"}]}, 200),
        ]
        with patch("node47_espn.searxng_client.time.sleep") as sleep:
            result = client.search("recent injury", time_range="day")
        self.assertEqual(result["count"], 1)
        self.assertEqual(session.get.call_count, 2)
        sleep.assert_called_once_with(1.0)
        self.assertEqual(session.get.call_args.kwargs["params"]["time_range"], "day")

    def test_502_exhaustion_is_bounded(self):
        client, session = self.make_client({}, status_code=502)
        with patch("node47_espn.searxng_client.time.sleep") as sleep:
            with self.assertRaisesRegex(SearXNGError, "502.*5 attempts"):
                client.search("NODE47")
        self.assertEqual(session.get.call_count, 5)
        self.assertEqual(sleep.call_count, 4)

    def test_retry_after_is_honored_and_bounded(self):
        client, session = self.make_client({"results": []})
        session.get.side_effect = [
            self.make_response({}, 503, {"Retry-After": "2"}),
            self.make_response({"results": []}, 200),
        ]
        with patch("node47_espn.searxng_client.time.sleep") as sleep:
            client.health()
        sleep.assert_called_once_with(2.0)

    def test_network_error_retries_with_bounded_attempts(self):
        client, session = self.make_client({"results": []})
        session.get.side_effect = [
            requests.Timeout(),
            self.make_response({"results": []}, 200),
        ]
        with patch("node47_espn.searxng_client.time.sleep") as sleep:
            result = client.health()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(session.get.call_count, 2)
        sleep.assert_called_once_with(0.5)

    def test_url_rejects_embedded_credentials(self):
        with self.assertRaises(SearXNGError):
            SearXNGClient("http://user:pass@searxng:8080")


if __name__ == "__main__":
    unittest.main()
