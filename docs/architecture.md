# Architecture and extension contracts

The domain pipeline in `engine.py` is independent of CLI persistence and career vocabulary. `models.py` validates versioned candidate, job, evidence and role-pack contracts using the schemas bundled with the package. The root `schemas/` files mirror those contracts for external adapters.

## Data boundaries

- Candidate profile: selected packs, declared skills, clearances, search policy and hard exclusions.
- Evidence: candidate-owned verified career facts with IDs, provenance, proficiency, capabilities, skills and metrics. No evidence is borrowed from another persona.
- Role pack: title aliases, weighted dimensions, recognized terms and required proficiency.
- Job: normalized company/title/requisition/location/work arrangement, description, source, optional salary/clearance/apply URL.
- Report: candidate ID, search funnel, ranked jobs, exclusion reasons, score breakdowns, warnings and retrieved evidence.
- Application ledger: canonical job ID and append-only normalized status events; current state is derived by authority and recency.

An exact company/requisition produces a stable hashed job ID. Without a requisition, URL identity preserves ATS query identifiers while removing known tracking parameters. Company/title/location is the last-resort identity, which may need human review. Employer sources win duplicate selection. Different requisitions at the same employer remain independent.

## Retrieval augmentation

`Retriever.retrieve(terms, evidence)` returns evidence IDs, matched terms, levels, sources, summaries and metrics. `LexicalRetriever` is the reference implementation. A semantic adapter must preserve that output contract and return only verified candidate evidence. The engine uses matched terms and levels for scoring; `tailor()` selects cited summaries without inventing prose. The CLI refreshes evidence before drafting so removed evidence cannot survive in a stale report.

A future LLM orchestration layer can extract requirements or rephrase retrieved facts, but must treat job text as untrusted input, validate structured output, restrict claims to allowed evidence IDs, and retain human review. No LLM or external service is called in this version.

## State and storage

`storage.py` atomically replaces local JSON files. It assumes one writer per workspace; transactions, multi-user isolation, encryption and concurrency control are future persistence work. Init uses owner-only directory permissions where supported and save uses private temporary files. Each workspace has its own candidate, evidence, packs, jobs, report, drafts and ledger. The CLI does not submit applications or send messages.

Status events contain metadata only and require timezone-aware timestamps. Exact duplicates are idempotent. Higher authority wins before recency. This can preserve stale high-authority state by design; user-confirmed correction is the explicit override. Silence is never emitted as a rejection.

## Extension seams

| Seam | Current implementation | Future adapter |
|---|---|---|
| Ingestion | Validated JSON job array | Employer/board source emitting the same contract |
| Requirement extraction | Role-pack phrase recognition | Validated structured required/preferred requirements |
| Retrieval | Verified lexical search | Candidate-scoped vector search with provenance |
| Status input | Normalized JSON events | Consent-based communication/ATS metadata extraction |
| Storage | Single-process atomic JSON | SQLite/Postgres transactional ledger |
| Rendering | Evidence-cited Markdown | Chronological DOCX/PDF renderer |

Private adapters and credentials belong outside this public repo. No live ChatGPT workflow or automation is connected to this engine.
