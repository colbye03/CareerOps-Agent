# Fit Evaluation Prompt Template

Evaluate one normalized job against the candidate policy and evidence.

## Required output

- fit score /100
- APPLY / MAYBE / SKIP
- strongest matches
- material gaps or risks
- realistic ATS/interview outlook
- recommended resume emphasis
- any hard-exclusion reason

## Rules

1. Run deterministic exclusions first.
2. Do not inflate scores to be encouraging.
3. Distinguish required qualifications from preferences.
4. Do not claim experience that is not in candidate evidence.
5. Prefer architecture/data-platform work when configured, but do not eliminate strong Staff/Principal engineering roles.
6. Treat compensation and location as first-class fit dimensions.
7. If evidence is insufficient for a dimension, say so rather than inventing support.
