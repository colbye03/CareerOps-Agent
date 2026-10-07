# Scoring Methodology

CareerOps uses a weighted 0-100 fit score after hard exclusions.

## Default weights

| Dimension | Weight |
|---|---:|
| Platform / technical alignment | 25% |
| Architecture alignment | 20% |
| Seniority / scope | 15% |
| Relevant domain experience | 10% |
| Compensation | 10% |
| Location / work arrangement | 10% |
| Interview probability | 5% |
| Career-direction alignment | 5% |

Each dimension is scored from 0 to 100.

```text
fit_score = Σ(dimension_score × dimension_weight)
```

## Decision thresholds

- **APPLY**: 85+
- **MAYBE**: 70-84.99
- **SKIP**: below 70

Thresholds are configurable.

## Hard exclusions

Hard exclusions run before scoring. A 98/100 role should still be excluded when, for example:

- the exact requisition was already submitted
- the exact requisition was already rejected or withdrawn
- the employer is explicitly blacklisted
- an active clearance is mandatory and the candidate does not hold it
- compensation is below a configured non-negotiable floor

A company is not globally excluded merely because one requisition was rejected.

## Interview probability

Interview probability is intentionally low-weight because it is uncertain. It can incorporate direct platform experience, scale evidence, domain overlap, seniority match, location alignment, and hard requirements.

It should never be presented as a guaranteed probability of interview.

## Explainability

Every recommendation should expose:

- final fit score
- strongest matches
- material gaps/risks
- hard-exclusion result
- APPLY / MAYBE / SKIP
- source and verified application link when available
