import os
import unittest
from unittest.mock import patch, MagicMock

from node47_espn import searxng_actions


class GitHubActionsSearXNGTests(unittest.TestCase):
    def test_callback_authentication_requires_configured_secret(self):
        with patch.dict(os.environ, {"SEARXNG_CALLBACK_SECRET": "test-secret"}):
            self.assertTrue(searxng_actions.authenticate_callback("test-secret"))
            self.assertFalse(searxng_actions.authenticate_callback("wrong"))

    def test_callback_completes_known_request_only(self):
        event = __import__("threading").Event()
        request_id = "test-request"
        with searxng_actions._PENDING_LOCK:
            searxng_actions._PENDING[request_id] = {"event": event, "payload": None}
        try:
            self.assertTrue(searxng_actions.complete_search(request_id, {"status": "ok", "results": []}))
            self.assertTrue(event.is_set())
            self.assertFalse(searxng_actions.complete_search("unknown", {"status": "ok"}))
        finally:
            with searxng_actions._PENDING_LOCK:
                searxng_actions._PENDING.pop(request_id, None)

    def test_dispatch_requires_actions_write(self):
        response = MagicMock(status_code=403)
        session = MagicMock()
        session.post.return_value = response
        with patch.dict(os.environ, {
            "GITHUB_ACTIONS_TOKEN": "token",
            "NODE47_RENDER_CALLBACK_URL": "https://example.onrender.com/v1/searxng/callback",
        }):
            client = searxng_actions.GitHubActionsSearXNGClient(session=session)
            with self.assertRaisesRegex(searxng_actions.GitHubSearXNGError, "Actions: write"):
                client._dispatch({"request_id": "x"})

    def test_search_dispatches_page_fetch_preference(self):
        with patch.dict(os.environ, {
            "GITHUB_ACTIONS_TOKEN": "token",
            "NODE47_RENDER_CALLBACK_URL": "https://example.onrender.com/v1/searxng/callback",
        }):
            client = searxng_actions.GitHubActionsSearXNGClient()
            captured = {}
            def dispatch(inputs):
                captured.update(inputs)
                searxng_actions.complete_search(inputs["request_id"], {
                    "status": "ok",
                    "results": [{"url": "https://example.org", "fetch_status": "ok", "page_content": "verified text"}],
                })
            client._dispatch = dispatch
            result = client.search("tactical matchup", max_results=1, fetch_pages=True)
            self.assertEqual(captured["fetch_pages"], "true")
            self.assertEqual(result["results"][0]["page_content"], "verified text")

    def test_search_can_disable_page_fetch(self):
        with patch.dict(os.environ, {
            "GITHUB_ACTIONS_TOKEN": "token",
            "NODE47_RENDER_CALLBACK_URL": "https://example.onrender.com/v1/searxng/callback",
        }):
            client = searxng_actions.GitHubActionsSearXNGClient()
            captured = {}
            def dispatch(inputs):
                captured.update(inputs)
                searxng_actions.complete_search(inputs["request_id"], {"status": "ok", "results": []})
            client._dispatch = dispatch
            client.search("health check", max_results=1, fetch_pages=False)
            self.assertEqual(captured["fetch_pages"], "false")
