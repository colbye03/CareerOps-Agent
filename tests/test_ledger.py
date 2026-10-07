from datetime import datetime, timezone

from careerops.ledger import SourceAuthority, StatusEvent, reconcile_status, silence_status


def test_higher_authority_beats_newer_automation():
    recruiter = StatusEvent(
        status="interviewing",
        observed_at=datetime(2026, 10, 1, tzinfo=timezone.utc),
        source="recruiter",
        authority=SourceAuthority.RECRUITER,
    )
    newer_job_board = StatusEvent(
        status="application_viewed",
        observed_at=datetime(2026, 10, 2, tzinfo=timezone.utc),
        source="job_board",
        authority=SourceAuthority.JOB_BOARD,
    )

    assert reconcile_status([recruiter, newer_job_board]) == recruiter


def test_silence_is_not_rejection():
    status = silence_status(14)

    assert status["status"] == "no_meaningful_response_yet"
    assert status["rejected"] is False
