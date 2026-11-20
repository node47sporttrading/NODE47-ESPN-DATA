import unittest
from unittest.mock import Mock

from node47_espn.searxng_client import SearXNGClient, SearXNGError


class SearXNGClientTests(unittest.TestCase):
    def make_client(self, payload, status_code=200):
        response = Mock()
        response.status_code = status_code
        response.ok = status_code < 400
        response.json.return_value = payload
        session = Mock()
        session.headers = {}
        session.get.return_value = response
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

    def test_403_explains_json_format_configuration(self):
        client, _ = self.make_client({}, status_code=403)
        with self.assertRaisesRegex(SearXNGError, "search.formats"):
            client.search("NODE47")

    def test_url_rejects_embedded_credentials(self):
        with self.assertRaises(SearXNGError):
            SearXNGClient("http://user:pass@searxng:8080")


if __name__ == "__main__":
    unittest.main()
