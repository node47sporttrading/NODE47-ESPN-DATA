"""Quality checks: report missing data without fabricating replacements."""
from __future__ import annotations


def validate_event(event: dict) -> list[str]:
    flags: list[str] = []
    if not event.get("event_id"):
        flags.append("missing_event_id")
    if not event.get("start_time_utc"):
        flags.append("missing_or_invalid_start_time")
    participants = event.get("participants") or {}
    if not participants.get("home") and not participants.get("away") and not participants.get("competitors"):
        flags.append("participants_unavailable")
    event["quality_flags"] = sorted(set((event.get("quality_flags") or []) + flags))
    return flags
