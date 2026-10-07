from __future__ import annotations

from dataclasses import dataclass

from .dedupe import deduplicate_jobs
from .scoring import FitInputs, FitResult, score_fit


@dataclass(frozen=True)
class CandidatePolicy:
    minimum_base_compensation: float | None = None
    blacklisted_companies: frozenset[str] = frozenset()
    holds_required_clearance: bool = False


@dataclass(frozen=True)
class ApplicationRecord:
    company: str
    requisition_id: str | None
    status: str


@dataclass
class SearchFunnel:
    raw_postings: int = 0
    unique_postings: int = 0
    plausible_matches: int = 0
    fully_evaluated: int = 0
    apply: int = 0
    maybe: int = 0
    skip: int = 0


EXCLUDED_STATUSES = {"applied", "rejected", "closed", "withdrawn"}


def hard_exclusion_reason(
    job: dict,
    policy: CandidatePolicy,
    ledger: list[ApplicationRecord],
) -> str | None:
    company = str(job.get("company", "")).strip().lower()
    req_id = job.get("requisition_id")

    if company in {c.lower() for c in policy.blacklisted_companies}:
        return "blacklisted_company"

    if job.get("active_clearance_required") and not policy.holds_required_clearance:
        return "required_clearance_not_held"

    comp_max = job.get("compensation_max")
    if (
        policy.minimum_base_compensation is not None
        and comp_max is not None
        and comp_max < policy.minimum_base_compensation
    ):
        return "compensation_below_floor"

    for record in ledger:
        same_company = record.company.strip().lower() == company
        same_req = bool(req_id) and record.requisition_id == req_id
        if same_company and same_req and record.status.lower() in EXCLUDED_STATUSES:
            return f"exact_req_{record.status.lower()}"

    return None


def evaluate_job(
    job: dict,
    fit_inputs: FitInputs,
    policy: CandidatePolicy,
    ledger: list[ApplicationRecord],
) -> tuple[str | None, FitResult | None]:
    exclusion = hard_exclusion_reason(job, policy, ledger)
    if exclusion:
        return exclusion, None
    return None, score_fit(fit_inputs)


def build_funnel(
    raw_jobs: list[dict],
    plausible_jobs: list[dict],
    evaluated_results: list[FitResult],
) -> SearchFunnel:
    unique = deduplicate_jobs(raw_jobs)
    funnel = SearchFunnel(
        raw_postings=len(raw_jobs),
        unique_postings=len(unique),
        plausible_matches=len(plausible_jobs),
        fully_evaluated=len(evaluated_results),
    )

    for result in evaluated_results:
        if result.decision == "APPLY":
            funnel.apply += 1
        elif result.decision == "MAYBE":
            funnel.maybe += 1
        else:
            funnel.skip += 1

    return funnel
