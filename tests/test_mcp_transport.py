import unittest
from fastapi.testclient import TestClient

from node47_espn.api import app


class MCPTransportContractTests(unittest.TestCase):
    def test_mcp_streamable_http_initialize_and_tools_list(self):
        headers = {
            "content-type": "application/json",
            "accept": "application/json, text/event-stream",
            "host": "node47-espn-data.onrender.com",
        }
        initialize = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "node47-transport-test", "version": "0.0.24"},
            },
        }
        with TestClient(app) as client:
            response = client.post("/mcp/", json=initialize, headers=headers)
            self.assertEqual(response.status_code, 200, response.text)
            session_id = response.headers.get("mcp-session-id")
            self.assertTrue(session_id, "Streamable HTTP initialize must return a session id")
            headers["mcp-session-id"] = session_id
            initialized = client.post(
                "/mcp/",
                json={"jsonrpc": "2.0", "method": "notifications/initialized"},
                headers=headers,
            )
            self.assertIn(initialized.status_code, (200, 202), initialized.text)
            listed = client.post(
                "/mcp/",
                json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
                headers=headers,
            )
            self.assertEqual(listed.status_code, 200, listed.text)
            body = listed.text
            for tool in ("node47_runtime_info", "football_poisson_predict",
                         "node47_robot_stake_u", "searxng_health", "espn_health"):
                self.assertIn(tool, body)
            self.assertNotIn("football_stake_u", body)
            self.assertNotIn("node47_multisport_stake_u", body)


if __name__ == "__main__":
    unittest.main()