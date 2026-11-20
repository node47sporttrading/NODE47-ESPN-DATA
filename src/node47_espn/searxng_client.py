"""Public SearXNG JSON API client for NODE.47."""
from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlsplit

import requests


class SearXNGError(RuntimeError):
    """Sanitized SearXNG error; never includes credentials or request headers."""


class SearXNGClient:
    def __init__(self, base_url: str | None = None, timeout: int = 20, session=None):
        raw_url = (base_url if base_url is not None else os.getenv("SEARXNG_URL", "")).strip()
        if not raw_url:
            raise SearXNGError("SEARXNG_URL is not configured")
        if "://" not in raw_url:
            raw_url = f"http://{raw_url}"
        parsed = urlsplit(raw_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise SearXNGError("SEARXNG_URL must be an HTTP(S) URL or an internal host:port")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise SearXNGError("SEARXNG_URL must not contain credentials, query parameters or fragments")
        self.base_url = raw_url.rstrip("/")
        self.timeout = min(60, max(3, int(timeout)))
        self.session = session or requests.Session()
        self.session.headers.update({"Accept": "application/json", "User-Agent": "NODE47-SPORT-ANALYT/0.0.15"})

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            response = self.session.get(
                f"{self.base_url}{path}",
                params=params or {},
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise SearXNGError(f"SearXNG network error: {type(exc).__name__}") from None

        if response.status_code == 403:
            raise SearXNGError("SearXNG refused the JSON API (403); verify search.formats includes json.")
        if response.status_code == 429:
            raise SearXNGError("SearXNG rate limit reached (429); reduce search frequency.")
        if response.status_code >= 500:
            raise SearXNGError(f"SearXNG server error ({response.status_code}).")
        if not response.ok:
            raise SearXNGError(f"SearXNG request failed ({response.status_code}).")
        try:
            payload = response.json()
        except ValueError:
            raise SearXNGError("SearXNG returned invalid JSON.") from None
        if not isinstance(payload, dict):
            raise SearXNGError("SearXNG returned an unexpected JSON structure.")
        return payload

    def health(self) -> dict[str, Any]:
        payload = self._get(
            "/search",
            {"q": "NODE47 health check", "format": "json", "safesearch": 1, "pageno": 1},
        )
        results = payload.get("results")
        if not isinstance(results, list):
            raise SearXNGError("SearXNG JSON API is unavailable: 'results' is missing.")
        return {
            "service": "searxng",
            "status": "ok",
            "json_api": True,
            "result_count": len(results),
            "unresponsive_engines": payload.get("unresponsive_engines", []),
        }

    def search(
        self,
        query: str,
        categories: str = "general,news",
        language: str = "fr",
        time_range: str | None = None,
        safesearch: int = 1,
        max_results: int = 10,
    ) -> dict[str, Any]:
        query = (query or "").strip()
        if not query:
            raise ValueError("query is required")
        if len(query) > 500:
            raise ValueError("query must contain at most 500 characters")
        if not 1 <= int(max_results) <= 20:
            raise ValueError("max_results must be between 1 and 20")
        if int(safesearch) not in (0, 1, 2):
            raise ValueError("safesearch must be 0, 1 or 2")
        if time_range not in (None, "", "day", "week", "month", "year"):
            raise ValueError("time_range must be day, week, month, year or omitted")

        params: dict[str, Any] = {
            "q": query,
            "format": "json",
            "categories": (categories or "general,news")[:100],
            "language": (language or "fr")[:16],
            "safesearch": int(safesearch),
            "pageno": 1,
        }
        if time_range:
            params["time_range"] = time_range

        payload = self._get("/search", params)
        raw_results = payload.get("results")
        if not isinstance(raw_results, list):
            raise SearXNGError("SearXNG JSON API response has no results list.")

        results = []
        for item in raw_results[: int(max_results)]:
            if not isinstance(item, dict):
                continue
            results.append({
                "title": item.get("title"),
                "url": item.get("url"),
                "content": item.get("content") or item.get("snippet"),
                "engine": item.get("engine"),
                "category": item.get("category") or item.get("categories"),
                "published_date": item.get("publishedDate"),
                "score": item.get("score"),
            })

        return {
            "status": "ok",
            "query": query,
            "count": len(results),
            "unresponsive_engines": payload.get("unresponsive_engines", []),
            "results": results,
        }
