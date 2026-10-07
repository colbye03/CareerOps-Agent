"""Local-only, atomic JSON persistence. No network or application submission."""
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from datetime import datetime, timezone

from .ledger import SourceAuthority, StatusEvent, reconcile_status

STATUSES = {"applied", "interviewing", "offer", "accepted", "rejected", "withdrawn", "closed"}


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")
        temporary = stream.name
    os.replace(temporary, path)


def record_event(ledger, job_id, status, source, observed_at=None):
    if status not in STATUSES:
        raise ValueError("unsupported application status")
    source = source.lower()
    SourceAuthority[source.upper()]
    stamp = datetime.fromisoformat(observed_at) if observed_at else datetime.now(timezone.utc)
    if stamp.tzinfo is None:
        raise ValueError("observed_at must include a timezone")
    record = next((r for r in ledger if r["job_id"] == job_id), None)
    if record is None:
        record = {"job_id": job_id, "events": []}
        ledger.append(record)
    event = {"status": status, "source": source, "observed_at": stamp.isoformat()}
    if event not in record["events"]:
        record["events"].append(event)
    events = [StatusEvent(e["status"], datetime.fromisoformat(e["observed_at"]), e["source"],
                          SourceAuthority[e["source"].upper()]) for e in record["events"]]
    winner = reconcile_status(events)
    record["status"] = winner.status
    record["source"] = winner.source
    record["observed_at"] = winner.observed_at.isoformat()
    return record
