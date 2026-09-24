# Unit-to-Story and Requirement Map — Timestamp Columns Intent

## Current Intent User Stories

User Stories were skipped in the approved execution plan because this is an internal schema and processing-time change without a user workflow change. There are no new user stories to assign in this intent.

## Current Intent Requirement Coverage

| Requirement | Assigned unit | Coverage |
|---|---|---|
| FR-01 — Preserve Kafka `source_timestamp` | U4 — P1 Layer Timestamp Metadata | Preserve the source event-time field while adding separate layer processing-time fields. |
| FR-02 — Bronze ingestion timestamp | U4 — P1 Layer Timestamp Metadata | Add `bronze_ingestion_timestamp` and set it on first insert. |
| FR-03 — Silver processing timestamp | U4 — P1 Layer Timestamp Metadata | Add `silver_processing_timestamp` on valid insert or winning update. |
| FR-04 — UTC instants | U4 — P1 Layer Timestamp Metadata | Generate and interpret both timestamps consistently as UTC instants. |
| FR-05 — Keep layer timestamps distinct | U4 — P1 Layer Timestamp Metadata | Do not copy bronze ingestion time into silver processing time. |
| FR-06 — Replay/no-op stability | U4 — P1 Layer Timestamp Metadata | Preserve timestamps when replay produces no insert or winning update. |
| FR-07 — Additive existing-table migration | U4 — P1 Layer Timestamp Metadata | Add nullable columns before writes when existing tables lack them. |
| FR-08 — Historical values remain NULL | U4 — P1 Layer Timestamp Metadata | Do not backfill historical rows. |
| FR-09 — Preserve existing pipeline behavior | U4 — P1 Layer Timestamp Metadata | Retain checkpoints, CDF, latest-event ordering, quarantine, and job behavior. |

## Baseline P1 Stories

The prior intent's stories remain mapped to the original workload units in the archived design at `aidlc-docs/archive/20260924-p1-databricks-workload/full-artifacts/aidlc-docs/inception/application-design/unit-of-work-story-map.md`:

| Existing story | Primary unit | Supporting units |
|---|---|---|
| US-P1-01 — Query the latest event state | U2 — Silver Processing and Quarantine | U1 supplies events; U3 schedules and integrates the tasks. |
| US-P1-02 — Query valid events when malformed messages occur | U2 — Silver Processing and Quarantine | U1 supplies source records; U3 runs the ordered pipeline. |

These baseline stories are not new requirements for the timestamp intent. U4's changes support existing silver data contracts but do not alter their user outcomes.

## Coverage Check

- Every current functional requirement FR-01 through FR-09 maps to U4.
- No current-intent user story is unassigned because no new stories were generated.
- Baseline P1 stories remain traceable to the archived U1–U3 mapping.
