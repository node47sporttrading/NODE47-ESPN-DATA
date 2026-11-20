"""On-demand SearXNG execution through ephemeral GitHub Actions runners."""
from __future__ import annotations

import hmac
import os
import threading
import time
import uuid
from typing import Any
from urllib.parse import urlsplit

import requests


class GitHubSearXNGError(RuntimeError):
    """Sanitized GitHub Actions / SearXNG execution error."""


_PENDING: dict[str, dict[str, Any]] = {}
_PENDING_LOCK = threading.Lock()


def complete_search(request_id: str, payload: dict[str, Any]) -> bool:
    """Complete a waiting search from the authenticated GitHub Actions callback."""
    with _PENDING_LOCK:
        item = _PENDING.get(request_id)
        if item is None:
            return False
        item["payload"] = payload
        item["event"].set()
        return True


def authenticate_callback(provided: str | None) -> bool:
    expected = os.getenv("SEARXNG_CALLBACK_SECRET", "")
    return bool(expected and provided and hmac.compare_digest(expected, provided))


class GitHubActionsSearXNGClient:
    """Dispatch an ephemeral SearXNG container in GitHub Actions and await callback."""

    REPOSITORY = "node47sporttrading/NODE47-ESPN-DATA"
    WORKFLOW = "searxng-search.yml"

    def __init__(self, timeout: int = 210, session=None):
        self.token = os.getenv("GITHUB_ACTIONS_TOKEN", "").strip()
        self.callback_url = os.getenv("NODE47_RENDER_CALLBACK_URL", "").strip()
        self.timeout = min(300, max(30, int(timeout)))
        self.session = session or requests.Session()
        if not self.token:
            raise GitHubSearXNGError("GITHUB_ACTIONS_TOKEN is not configured on Render.")
        if not self.callback_url:
            raise GitHubSearXNGError("NODE47_RENDER_CALLBACK_URL is not configured on Render.")
        parsed = urlsplit(self.callback_url)
        if parsed.scheme != "https" or not parsed.netloc or parsed.query or parsed.fragment:
            raise GitHubSearXNGError("NODE47_RENDER_CALLBACK_URL must be an HTTPS callback URL.")

    def _dispatch(self, inputs: dict[str, str]) -> None:
        url = (
            f"https://api.github.com/repos/{self.REPOSITORY}/actions/"
            f"workflows/{self.WORKFLOW}/dispatches"
        )
        try:
            response = self.session.post(
                url,
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {self.token}",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                json={"ref": "main", "inputs": inputs},
                timeout=15,
            )
        except requests.RequestException as exc:
            raise GitHubSearXNGError(
                f"Unable to dispatch GitHub Actions workflow ({type(exc).__name__})."
            ) from None
        if response.status_code != 204:
            if response.status_code in (401, 403):
                detail = "GitHub token must have Actions: write permission."
            elif response.status_code == 404:
                detail = "Workflow is not available on the repository default branch yet."
            else:
                detail = f"GitHub workflow dispatch failed ({response.status_code})."
            raise GitHubSearXNGError(detail)

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
        if not query or len(query) > 500:
            raise ValueError("query is required and must contain at most 500 characters")
        if time_range not in (None, "", "day", "week", "month", "year"):
            raise ValueError("time_range must be day, week, month, year or omitted")
        if int(safesearch) not in (0, 1, 2):
            raise ValueError("safesearch must be 0, 1 or 2")
        if not 1 <= int(max_results) <= 20:
            raise ValueError("max_results must be between 1 and 20")

        request_id = str(uuid.uuid4())
        event = threading.Event()
        with _PENDING_LOCK:
            _PENDING[request_id] = {"event": event, "payload": None, "created": time.monotonic()}

        inputs = {
            "request_id": request_id,
            "query": query,
            "categories": (categories or "general,news")[:100],
            "language": (language or "fr")[:16],
            "time_range": time_range or "none",
            "safesearch": str(int(safesearch)),
            "max_results": str(int(max_results)),
            "callback_url": self.callback_url,
        }
        try:
            self._dispatch(inputs)
            if not event.wait(self.timeout):
                raise GitHubSearXNGError(
                    f"GitHub Actions search timed out after {self.timeout} seconds; no results were accepted."
                )
            with _PENDING_LOCK:
                payload = _PENDING[request_id]["payload"]
            if not isinstance(payload, dict):
                raise GitHubSearXNGError("GitHub Actions callback returned an invalid payload.")
            if payload.get("status") != "ok":
                raise GitHubSearXNGError(str(payload.get("error") or "GitHub Actions SearXNG search failed."))
            results = payload.get("results")
            if not isinstance(results, list):
                raise GitHubSearXNGError("GitHub Actions callback did not contain a results list.")
            return {
                "status": "ok",
                "execution": "github_actions",
                "request_id": request_id,
                "query": query,
                "count": len(results),
                "unresponsive_engines": payload.get("unresponsive_engines", []),
                "results": results[: int(max_results)],
            }
        finally:
            with _PENDING_LOCK:
                _PENDING.pop(request_id, None)

    def health(self) -> dict[str, Any]:
        result = self.search(
            "NODE47 SearXNG availability check",
            categories="general",
            language="en",
            max_results=1,
        )
        return {
            "service": "searxng",
            "status": "ok",
            "execution": "github_actions",
            "result_count": result["count"],
        }
