import unittest
from unittest.mock import Mock
from node47_espn.client import ESPNClient


class ClientTests(unittest.TestCase):
    def test_scoreboard_builds_expected_url(self):
        session = Mock()
        response = Mock()
        response.json.return_value = {"events": []}
        session.get.return_value = response
        client = ESPNClient("https://site.api.espn.com/apis/site/v2/sports", session=session)
        result = client.scoreboard("basketball", "nba")
        session.get.assert_called_once()
        self.assertEqual(result, {"events": []})
        self.assertIn("/basketball/nba/scoreboard", session.get.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
