from __future__ import annotations

import re
from collections.abc import Iterable
from urllib.parse import urlsplit, urlunsplit


SOURCE_PRIORITY = {
    "employer": 4,
    "linkedin": 3,
    "indeed": 3,
    "other": 1,
}


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def normalize_url(url: str | None) -> str:
    if not url:
        return ""
    parts = urlsplit(url)
    return urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), "", "")
    )


def job_identity(job: dict) -> tuple[str, ...]:
    """Build an identity key, preferring exact requisition IDs."""
    company = normalize_text(job.get("company"))
    req_id = normalize_text(job.get("requisition_id"))

    if company and req_id:
        return ("req", company, req_id)

    apply_url = normalize_url(job.get("apply_url"))
    if apply_url:
        return ("url", apply_url)

    return (
        "fallback",
        company,
        normalize_text(job.get("title")),
        normalize_text(job.get("location")),
    )


def _priority(job: dict) -> tuple[int, int]:
    source = normalize_text(job.get("source"))
    direct_apply = 1 if normalize_url(job.get("apply_url")) else 0
    return SOURCE_PRIORITY.get(source, SOURCE_PRIORITY["other"]), direct_apply


def deduplicate_jobs(jobs: Iterable[dict]) -> list[dict]:
    """Keep one best representative for each semantic job identity."""
    winners: dict[tuple[str, ...], dict] = {}

    for job in jobs:
        key = job_identity(job)
        current = winners.get(key)
        if current is None or _priority(job) > _priority(current):
            winners[key] = job

    return list(winners.values())
