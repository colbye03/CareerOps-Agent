# Fit Evaluation Prompt Template

Evaluate one normalized job against the candidate profile, search policy, selected role pack and verified evidence.

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
5. Use only the candidate-selected role pack dimensions and weights; do not assume any career direction.
6. Enforce compensation and location policy before fit scoring. Label uncertain input for review.
7. If evidence is insufficient for a dimension, say so rather than inventing support.
