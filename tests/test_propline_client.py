import unittest
from unittest.mock import Mock

from node47_espn.propline_client import PropLineClient, PropLineError


class FakeResponse:
    def __init__(self, status=200, payload=None, headers=None):
        self.status_code = status
        self.ok = 200 <= status < 300
        self._payload = payload if payload is not None else {"ok": True}
        self.headers = headers or {}

    def json(self):
        return self._payload


class PropLineClientTests(unittest.TestCase):
    def test_auth_header_and_bulk_odds_params(self):
        session = Mock()
        session.headers = {}
        session.get.return_value = FakeResponse(payload={"events": []})
        client = PropLineClient(api_key="test-key", session=session)

        result = client.odds("basketball_nba", "h2h,spreads,totals", "draftkings", 90)

        self.assertEqual(result, {"events": []})
        self.assertEqual(session.headers["X-API-Key"], "test-key")
        args, kwargs = session.get.call_args
        self.assertTrue(args[0].endswith("/sports/basketball_nba/odds"))
        self.assertEqual(kwargs["params"], {
            "markets": "h2h,spreads,totals",
            "bookmakers": "draftkings",
            "max_age": 90,
        })

    def test_event_market_discovery_uses_exact_provider_event(self):
        session = Mock()
        session.headers = {}
        session.get.return_value = FakeResponse(payload=[{"key": "h2h", "outcomes_count": 2}])
        client = PropLineClient(api_key="test-key", session=session)

        result = client.event_markets("tennis", "event-123")

        self.assertEqual(result, [{"key": "h2h", "outcomes_count": 2}])
        args, kwargs = session.get.call_args
        self.assertTrue(args[0].endswith("/sports/tennis/events/event-123/markets"))
        self.assertEqual(kwargs["params"], {})

    def test_period_filter_is_forwarded_for_event_odds(self):
        session = Mock()
        session.headers = {}
        session.get.return_value = FakeResponse(payload={"id": "event-1"})
        client = PropLineClient(api_key="test-key", session=session)

        client.event_odds("tennis", "event-1", "h2h", period="s1")

        self.assertEqual(session.get.call_args.kwargs["params"], {
            "markets": "h2h", "period": "s1"
        })

    def test_missing_key_fails_closed(self):
        with self.assertRaisesRegex(PropLineError, "PROPLINE_API_KEY"):
            PropLineClient(api_key="")

    def test_unauthorized_error_is_sanitized(self):
        session = Mock()
        session.headers = {}
        session.get.return_value = FakeResponse(status=401)
        client = PropLineClient(api_key="never-log-this", session=session)
        with self.assertRaisesRegex(PropLineError, "rejected the API key"):
            client.sports()


if __name__ == "__main__":
    unittest.main()
