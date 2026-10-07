# Candidate-specific fit scoring

Role packs define all role vocabulary, dimension weights, and expected evidence levels. The engine has no TPM, AI, infrastructure or data-platform branches. Candidate profiles select eligible packs and thresholds.

1. Route a posting using title aliases among candidate-selected packs; ties preserve the candidate's pack order. A title outside those packs is SKIP.
2. Run deterministic exclusions before evidence scoring: work mode, configured locations, blocked companies/terms, clearance, comparable salary floor, and existing exact-job applications.
3. For each pack dimension, recognize requirement terms in the job description using case-insensitive phrase boundaries. This baseline treats every recognized term as a requirement; it does not yet parse preferred versus mandatory wording or negation.
4. Retrieve verified evidence per dimension. For each term, evidence credit is `min(1, highest demonstrated level / required level)`. Levels 1–5 represent exposure through expert leadership. Declared skills receive at most 0.25 credit; they cannot produce resume claims.
5. Average term credit within each recognized dimension, then compute the weighted average across recognized dimensions. Absent dimensions do not silently count as demonstrated experience.
6. Record recognized pack weight. If below the candidate's minimum coverage, return MAYBE and a manual-review warning, including when nothing is recognized.
7. Apply candidate-configured APPLY and MAYBE thresholds. Exclusions always return SKIP with no score.

The output cites matched evidence and sources, recognized terms, dimension scores, partial/missing proficiency gaps, pack ID and warnings. Missing/foreign-currency salaries receive a warning or exclusion when known salary is mandatory. Currency conversion and compensation prediction are not implemented.

A 100 score means complete evidence coverage of **recognized requirements**, not universal qualification. Sparse or misparsed descriptions require review. The current model does not infer employment duration, seniority, certification eligibility, or interview likelihood. Role pack versions and deterministic inputs are the unit of reproducibility.

The funnel counts plausible title matches before exclusions, evaluated jobs after exclusions, and final decisions across every unique posting. `excluded + fully_evaluated = unique`, and `apply + maybe + skip = unique`. Duplicate postings never count twice. Excluded jobs are included in SKIP totals and have separate reasons.

The legacy v0.1 explicit-input scorer is retained for compatibility only; its architecture-biased weights are not used by the reusable engine.
