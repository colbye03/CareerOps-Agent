# Operational Workflow

## 1. Search and collect

Search multiple role families rather than one broad query:

- Solution / Cloud / Data Platform Architect
- Azure Data & AI / Databricks / Fabric Architect
- Data Architect / Principal Data Architect
- Senior / Staff / Principal Data Engineer
- Data/cloud-aligned Solutions Engineer / Sales Engineer

Prioritize remote U.S. and configured hybrid markets.

## 2. Normalize

Convert each posting to the common job schema: employer, title, requisition ID, source, URLs, location, work arrangement, compensation, requirements, preferences, and observed timestamp.

## 3. Deduplicate

Prefer, in order:

1. exact requisition ID
2. verified direct apply URL
3. normalized company + normalized title + location

Prefer the employer career page over a secondary board when both describe the same requisition.

## 4. Exclude

Apply configured hard exclusions before model scoring.

## 5. Evaluate

Score the remaining roles and record fit, strongest matches, gaps, realistic interview outlook, and APPLY / MAYBE / SKIP. Do not add weak roles simply to fill a quota.

## 6. Prepare

For APPLY roles, use a verified employer link when possible and tailor resume emphasis while preserving exact employment history and factual evidence.

## 7. Track

Update the application ledger with exact requisition IDs and timestamps.

## 8. Reconcile communications

Status-source precedence:

```text
user-confirmed / recruiter-confirmed
    > employer portal
    > employer automated email
    > job-board automation
    > inference
```

Never infer rejection from silence. Use **no meaningful response yet** with elapsed time.

## 9. Report

Recommended report order:

1. urgent/time-sensitive actions and interviews
2. active consideration
3. applications with no meaningful response
4. rejections/closures/withdrawals
5. new recommendations

Expose the search funnel at the top of each run.
