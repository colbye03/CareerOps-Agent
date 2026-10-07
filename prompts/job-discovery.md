# Job Discovery Prompt Template

## Goal

Find current, high-fit technical openings while preserving source metadata and avoiding duplicated effort.

## Instructions

Search across the configured role families and work arrangements. Use multiple independent sources where available and prefer authoritative employer pages for final application links.

For every candidate posting, extract:

- company
- title
- requisition ID if present
- location and work arrangement
- compensation if listed
- source and source URL
- verified direct employer apply URL when available
- required technologies
- architecture / engineering scope
- domain requirements
- clearance, degree, travel, or other hard constraints

Do not evaluate an obviously duplicated posting twice.

Do not assume a posting is active solely because a stale aggregator page exists; validate against an authoritative source when practical.

Return structured job objects suitable for the job schema.
