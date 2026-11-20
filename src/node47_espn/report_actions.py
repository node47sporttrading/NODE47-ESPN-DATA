"""Archive complete NODE.47 analysis reports through GitHub Actions."""
from __future__ import annotations

import hmac
import os
import re
import threading
import time
import uuid
from datetime import date
from typing import Any
from urllib.parse import urlsplit

import requests


class GitHubReportError(RuntimeError):
    """Sanitized GitHub report archival error."""


_PENDING_REPORTS: dict[str, dict[str, Any]] = {}
_PENDING_REPORTS_LOCK = threading.Lock()


def complete_report(request_id: str, payload: dict[str, Any]) -> bool:
    with _PENDING_REPORTS_LOCK:
        item = _PENDING_REPORTS.get(request_id)
        if item is None:
            return False
        item["payload"] = payload
        item["event"].set()
        return True


class GitHubActionsReportClient:
    REPOSITORY = "node47sporttrading/NODE47-ESPN-DATA"
    WORKFLOW = "node47-report-save.yml"

    def __init__(self, timeout: int = 240, session=None):
        self.token = os.getenv("GITHUB_ACTIONS_TOKEN", "").strip()
        self.callback_url = os.getenv("NODE47_REPORT_CALLBACK_URL", "").strip()
        self.timeout = min(300, max(30, int(timeout)))
        self.session = session or requests.Session()
        if not self.token:
            raise GitHubReportError("GITHUB_ACTIONS_TOKEN is not configured on Render.")
        if not self.callback_url:
            raise GitHubReportError("NODE47_REPORT_CALLBACK_URL is not configured on Render.")
        parsed = urlsplit(self.callback_url)
        if parsed.scheme != "https" or not parsed.netloc or parsed.query or parsed.fragment:
            raise GitHubReportError("NODE47_REPORT_CALLBACK_URL must be an HTTPS callback URL.")

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
                timeout=20,
            )
        except requests.RequestException as exc:
            raise GitHubReportError(
                f"Unable to dispatch GitHub report workflow ({type(exc).__name__})."
            ) from None
        if response.status_code != 204:
            if response.status_code in (401, 403):
                detail = "GitHub token must have Actions: write permission."
            elif response.status_code == 404:
                detail = "Report workflow is not available on the repository default branch."
            else:
                detail = f"GitHub report workflow dispatch failed ({response.status_code})."
            raise GitHubReportError(detail)

    def save(
        self, sport: str, event_slug: str, event_date: str, report_markdown: str
    ) -> dict[str, Any]:
        sport = (sport or "").strip().lower()
        event_slug = (event_slug or "").strip().lower()
        event_date = (event_date or "").strip()
        report_markdown = (report_markdown or "").strip()
        if sport not in {"football", "basketball", "tennis"}:
            raise ValueError("sport must be football, basketball or tennis")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", event_slug) or len(event_slug) > 100:
            raise ValueError("event_slug must contain only lowercase letters, digits and hyphens")
        try:
            date.fromisoformat(event_date)
        except ValueError:
            raise ValueError("event_date must use YYYY-MM-DD") from None
        if not report_markdown or len(report_markdown.encode("utf-8")) > 60_000:
            raise ValueError("report_markdown is required and must not exceed 60 KB")
        if not re.search(r"\b(BET PRUDENT|BET|NO BET)\b", report_markdown, re.I):
            raise ValueError("report_markdown must contain a final BET, BET PRUDENT or NO BET verdict")

        request_id = str(uuid.uuid4())
        event = threading.Event()
        with _PENDING_REPORTS_LOCK:
            _PENDING_REPORTS[request_id] = {
                "event": event, "payload": None, "created": time.monotonic()
            }
        inputs = {
            "request_id": request_id,
            "sport": sport,
            "event_slug": event_slug,
            "event_date": event_date,
            "report_markdown": report_markdown,
            "callback_url": self.callback_url,
        }
        try:
            self._dispatch(inputs)
            if not event.wait(self.timeout):
                raise GitHubReportError(
                    f"GitHub report save timed out after {self.timeout} seconds; no successful confirmation was received."
                )
            with _PENDING_REPORTS_LOCK:
                payload = _PENDING_REPORTS[request_id]["payload"]
            if not isinstance(payload, dict) or payload.get("status") != "ok":
                detail = payload.get("error") if isinstance(payload, dict) else None
                raise GitHubReportError(str(detail or "GitHub did not confirm report archival."))
            required = ("path", "url", "commit_sha")
            if any(not isinstance(payload.get(key), str) or not payload[key] for key in required):
                raise GitHubReportError("GitHub callback omitted the saved path, URL or commit SHA.")
            return {
                "status": "saved",
                "request_id": request_id,
                "repository": self.REPOSITORY,
                "path": payload["path"],
                "url": payload["url"],
                "commit_sha": payload["commit_sha"],
                "verified_by": "github_actions_commit_callback",
            }
        finally:
            with _PENDING_REPORTS_LOCK:
                _PENDING_REPORTS.pop(request_id, None)
