# Application Tracking Prompt Template

Maintain an exact-requisition application ledger.

For each application, track:

- employer
- title
- requisition ID
- application date
- latest communication date
- current status
- status source
- source authority
- upcoming deadline or interview
- required action
- notes

## State rules

- Never infer rejection from silence.
- Use "no meaningful response yet" for acknowledgement-only applications.
- A rejected or withdrawn requisition remains excluded from new recommendations.
- Other distinct requisitions at the same company remain eligible.
- User-confirmed status overrides stale automation.
