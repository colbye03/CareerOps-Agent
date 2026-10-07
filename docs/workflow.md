# CLI workflow

1. `careerops init --persona ...` creates a synthetic local workspace without overwriting existing data. Use `--workspace PATH` before the command to isolate candidates.
2. Edit the candidate and evidence JSON. Select role pack IDs, adjust policies and thresholds, add verified evidence with provenance, and customize pack weights/expected levels.
3. `careerops run [--jobs FILE]` validates, normalizes, deduplicates, excludes, retrieves evidence, scores, ranks and atomically writes `report.json`. It leaves the application ledger unchanged.
4. `careerops jobs` shows the funnel and ranked job IDs. `careerops explain JOB_ID` shows the last run's evidence, gaps and score breakdown.
5. `careerops resume JOB_ID` re-evaluates against current evidence and writes a cited Markdown draft. It refuses excluded jobs. Review the facts and assemble your final resume yourself.
6. After an actual submission, `careerops ledger --job-id JOB_ID --status applied` records a user-confirmed event. No submission is performed by the CLI.
7. Import normalized communication/ATS events with `careerops ledger --events FILE`, or record a specific status/source/time. Event import validates before persisting the entire updated ledger. Message bodies are not required or accepted as fields.
8. Run again to reconcile recommendations with application state. Exact submitted/rejected/withdrawn/closed/interviewing/offer/accepted jobs are excluded; other requisitions remain eligible.

The CLI prints JSON for piping, returns zero on success and two for invalid configuration/input. Unknown IDs and missing files produce errors instead of empty success output. Reports are last-run snapshots; rerun after changing configuration or ledger state.

Allowed event sources: `inferred`, `job_board`, `employer_email`, `employer_portal`, `recruiter`, `user_confirmed`. Explicit timezone-aware ISO timestamps are required for imported observations; direct records default to current UTC.
