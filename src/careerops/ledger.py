from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum


class SourceAuthority(IntEnum):
    INFERRED = 0
    JOB_BOARD = 1
    EMPLOYER_EMAIL = 2
    EMPLOYER_PORTAL = 3
    RECRUITER = 4
    USER_CONFIRMED = 5


@dataclass(frozen=True)
class StatusEvent:
    status: str
    observed_at: datetime
    source: str
    authority: SourceAuthority


def reconcile_status(events: list[StatusEvent]) -> StatusEvent | None:
    """Choose highest-authority status; break ties by recency."""
    if not events:
        return None

    return max(events, key=lambda event: (int(event.authority), event.observed_at))


def silence_status(days_since_meaningful_response: int) -> dict[str, object]:
    """Represent silence without converting it into a rejection."""
    if days_since_meaningful_response < 0:
        raise ValueError("days_since_meaningful_response cannot be negative")

    return {
        "status": "no_meaningful_response_yet",
        "elapsed_days": days_since_meaningful_response,
        "rejected": False,
    }
