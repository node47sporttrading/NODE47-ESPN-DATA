"""Small, quota-aware PropLine API client for NODE.47."""
from __future__ import annotations

import os
from typing import Any
from urllib.parse import quote

import requests


class PropLineError(RuntimeError):
    """Sanitized provider error; never includes request headers or credentials."""


class PropLineClient:
    BASE_URL = "https://api.prop-line.com/v1"

    def __init__(self, api_key: str | None = None, timeout: int = 20, session=None):
        self.api_key = (api_key if api_key is not None else os.getenv("PROPLINE_API_KEY", "")).strip()
        if not self.api_key:
            raise PropLineError("PROPLINE_API_KEY is not configured")
        self.timeout = max(3, int(timeout))
        self.session = session or requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "X-API-Key": self.api_key,
            "User-Agent": "NODE47-SPORT-ANALYT/0.0.12",
        })

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self.BASE_URL}/{path.lstrip('/')}"
        try:
            response = self.session.get(url, params=params or {}, timeout=self.timeout)
        except requests.RequestException as exc:
            raise PropLineError(f"PropLine network error: {type(exc).__name__}") from None

        if response.status_code == 401:
            raise PropLineError("PropLine rejected the API key (401). Check PROPLINE_API_KEY.")
        if response.status_code == 403:
            raise PropLineError("PropLine denied this endpoint for the current subscription (403).")
        if response.status_code == 429:
            remaining = response.headers.get("X-Daily-Remaining", "unknown")
            retry_after = response.headers.get("Retry-After", "not provided")
            raise PropLineError(
                f"PropLine rate/quota limit reached (429); daily remaining={remaining}, "
                f"Retry-After={retry_after}. Do not retry aggressively."
            )
        if response.status_code >= 500:
            raise PropLineError(f"PropLine server error ({response.status_code}).")
        if not response.ok:
            raise PropLineError(f"PropLine request failed ({response.status_code}).")
        try:
            return response.json()
        except ValueError:
            raise PropLineError("PropLine returned invalid JSON.") from None

    def sports(self) -> Any:
        return self._get("/sports")

    def events(self, sport_key: str, **params: Any) -> Any:
        return self._get(f"/sports/{quote(sport_key, safe='_')}/events", params)

    def odds(self, sport_key: str, markets: str = "h2h,spreads,totals",
             bookmakers: str | None = None, max_age: int | None = None) -> Any:
        params: dict[str, Any] = {"markets": markets}
        if bookmakers:
            params["bookmakers"] = bookmakers
        if max_age is not None:
            params["max_age"] = max(1, int(max_age))
        return self._get(f"/sports/{quote(sport_key, safe='_')}/odds", params)

    def event_odds(self, sport_key: str, event_id: str, markets: str) -> Any:
        path = f"/sports/{quote(sport_key, safe='_')}/events/{quote(str(event_id), safe='')}/odds"
        return self._get(path, {"markets": markets})

    def event_markets(self, sport_key: str, event_id: str) -> Any:
        path = f"/sports/{quote(sport_key, safe='_')}/events/{quote(str(event_id), safe='')}/markets"
        return self._get(path)

    def freshness(self) -> Any:
        return self._get("/freshness")
