"""Small, defensive HTTP client for ESPN's undocumented JSON endpoints."""
from __future__ import annotations

import time
from typing import Any

import requests


class ESPNClient:
    def __init__(self, base_url: str, timeout: int = 20, retries: int = 2, session=None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = max(0, retries)
        self.session = session or requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "NODE47-ESPN-DATA/0.0.5 (+https://github.com/node47sporttrading/NODE47-ESPN-DATA)",
        })

    def scoreboard(self, sport: str, league: str, date: str | None = None) -> dict[str, Any]:
        url = f"{self.base_url}/{sport}/{league}/scoreboard"
        params = {"dates": date} if date else None
        last_error = None
        for attempt in range(self.retries + 1):
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, dict):
                    raise ValueError("ESPN response is not a JSON object")
                return payload
            except (requests.RequestException, ValueError) as exc:
                last_error = exc
                if attempt < self.retries:
                    time.sleep(min(2 ** attempt, 4))
        raise RuntimeError(f"ESPN scoreboard request failed: {last_error}") from last_error
