"""Role-neutral pipeline. All career-specific vocabulary lives in role packs."""
from hashlib import sha256
import json

from .dedupe import deduplicate_jobs, job_identity
from .evidence import LexicalRetriever, contains
from .models import validate


BLOCKING = {"applied", "interviewing", "offer", "accepted", "rejected", "closed", "withdrawn"}


def normalize(job):
    validate("job", job)
    result = dict(job)
    for field in ("title", "company", "location", "requisition_id"):
        if field in result:
            result[field] = result[field].strip()
    result["id"] = sha256(json.dumps(job_identity(result)).encode()).hexdigest()[:16]
    return result


def exclusion(job, profile, ledger):
    policy = profile["search_policy"]
    hard = profile["hard_exclusions"]
    if job["company"].casefold() in {c.casefold() for c in hard["companies"]}:
        return "excluded_company"
    if job["work_mode"] not in policy["work_modes"]:
        return "work_mode"
    if policy["locations"] and job["location"].casefold() not in {x.casefold() for x in policy["locations"]}:
        return "location"
    if job.get("clearance") and job["clearance"] not in profile["clearances"]:
        return "clearance_not_held"
    floor = policy["minimum_salary"]
    salary = job.get("salary")
    if floor and salary and salary["currency"] == policy["currency"] and salary["max"] < floor:
        return "compensation_below_floor"
    if hard["require_known_salary"] and (not salary or salary["currency"] != policy["currency"]):
        return "compensation_unknown_or_currency_mismatch"
    text = job["title"] + " " + job["description"]
    if any(contains(text, t) for t in hard["terms"]):
        return "excluded_term"
    if any(r["job_id"] == job["id"] and r["status"] in BLOCKING for r in ledger):
        return "existing_application"
    return None


def select_pack(job, profile, packs):
    candidates = [(sum(contains(job["title"], a) for a in packs[p]["title_aliases"]), p)
                  for p in profile["role_packs"]]
    # Candidate's configured order breaks ties, never an engine-specific role preference.
    return max(candidates, key=lambda pair: pair[0])[1] if max(x[0] for x in candidates) else None


def evaluate(job, profile, evidence, pack, retriever):
    dimensions = []
    text = job["description"]
    for dimension in pack["dimensions"]:
        terms = [t for t in dimension["terms"] if contains(text, t)]
        if not terms:
            continue
        # Retrieval selects IDs and relevance; canonical evidence owns factual content.
        allowed = {item["id"]: item for item in evidence if item["verified"]}
        hits = []
        for retrieved in retriever.retrieve(terms, evidence):
            item = allowed.get(retrieved.get("evidence_id"))
            matched = [t for t in terms if t in retrieved.get("matched_terms", [])]
            if item and matched:
                hits.append({"evidence_id": item["id"], "matched_terms": matched,
                             "level": item["level"], "source": item["source"],
                             "summary": item["summary"], "metrics": item["metrics"]})
        values = []
        for term in terms:
            levels = [h["level"] for h in hits if term in h["matched_terms"]]
            demonstrated = min(1, max(levels, default=0) / dimension["required_level"])
            self_reported = .25 if any(contains(s, term) for s in profile["skills"]) else 0
            values.append(max(demonstrated, self_reported))
        dimensions.append({"id": dimension["id"], "weight": dimension["weight"],
                           "score": round(100 * sum(values) / len(values), 2),
                           "requirements": terms, "evidence": hits,
                           "gaps": [t for t, v in zip(terms, values) if v < 1]})
    total_weight = sum(d["weight"] for d in dimensions)
    score = round(sum(d["score"] * d["weight"] for d in dimensions) / total_weight, 2) if total_weight else 0
    policy = profile["search_policy"]
    decision = "APPLY" if score >= policy["apply_threshold"] else "MAYBE" if score >= policy["maybe_threshold"] else "SKIP"
    warnings = []
    if not job.get("salary") or job["salary"]["currency"] != policy["currency"]:
        warnings.append("Compensation cannot be compared to the configured floor.")
    if not total_weight or total_weight < policy["minimum_requirement_coverage"]:
        warnings.append("Insufficient role requirements recognized; manual review required.")
        decision = "MAYBE"
    return {"job": job, "role_pack": pack["id"], "score": score, "decision": decision,
            "dimensions": dimensions, "recognized_weight": round(total_weight, 4), "warnings": warnings,
            "exclusion": None}


def run(jobs, profile, evidence, packs, ledger=(), retriever=None):
    validate("candidate", profile)
    validate("evidence", evidence)
    for name in profile["role_packs"]:
        validate("role-pack", packs[name])
        if packs[name]["id"] != name:
            raise ValueError("role pack filename and ID must match")
    unique = deduplicate_jobs([normalize(j) for j in jobs])
    results = []
    plausible = evaluated = 0
    for job in unique:
        pack_id = select_pack(job, profile, packs)
        reason = exclusion(job, profile, ledger)
        plausible += bool(pack_id)
        if reason or not pack_id:
            results.append({"job": job, "role_pack": pack_id, "score": None, "decision": "SKIP",
                            "exclusion": reason or "outside_target_roles", "dimensions": [], "warnings": []})
        else:
            results.append(evaluate(job, profile, evidence, packs[pack_id], retriever or LexicalRetriever()))
            evaluated += 1
    results.sort(key=lambda r: (-(r["score"] if r["score"] is not None else -1), r["job"]["id"]))
    funnel = {"raw_postings": len(jobs), "unique_postings": len(unique), "plausible_matches": plausible,
              "fully_evaluated": evaluated, "excluded": len(unique) - evaluated,
              **{d.lower(): sum(r["decision"] == d for r in results) for d in ("APPLY", "MAYBE", "SKIP")}}
    return {"candidate_id": profile["id"], "funnel": funnel, "results": results}


def tailor(result):
    """Only quote retrieved facts; never generate unsupported career claims."""
    lines = [f"# Evidence draft: {result['job']['title']}", "", "Review before submission. Gaps are not candidate claims.", ""]
    seen = set()
    for dimension in result["dimensions"]:
        for hit in dimension["evidence"]:
            if hit["evidence_id"] not in seen:
                lines.append(f"- {hit['summary']} [evidence: {hit['evidence_id']}; source: {hit['source']}]")
                for metric in hit["metrics"]:
                    lines.append(f"  - {metric['name']}: {metric['value']} {metric['unit']} ({metric['context']})")
                seen.add(hit["evidence_id"])
    lines += ["", "## Gaps", *[f"- {d['id']}: {', '.join(d['gaps'])}" for d in result["dimensions"] if d["gaps"]]]
    return "\n".join(lines) + "\n"
