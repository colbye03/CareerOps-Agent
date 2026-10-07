from careerops.dedupe import deduplicate_jobs


def test_same_req_dedupes_and_prefers_employer_source():
    jobs = [
        {
            "company": "Example Co",
            "title": "Principal Data Architect",
            "requisition_id": "R123",
            "source": "linkedin",
            "apply_url": "https://linkedin.example/job/1",
        },
        {
            "company": "Example Co",
            "title": "Principal Data Architect",
            "requisition_id": "R123",
            "source": "employer",
            "apply_url": "https://example.com/careers/R123",
        },
    ]

    result = deduplicate_jobs(jobs)

    assert len(result) == 1
    assert result[0]["source"] == "employer"
