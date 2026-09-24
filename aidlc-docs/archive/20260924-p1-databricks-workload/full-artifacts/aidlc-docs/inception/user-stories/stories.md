# P1 User Stories — P1 Event Data

## Scope

These stories translate the approved P1 requirements into outcomes for the downstream data engineer who consumes the silver table. They use a domain-based grouping under the neutral label **P1 event data**. Operator stories and gold-layer outputs are out of scope.

## Domain: P1 event data

### US-P1-01 — Query the latest event state

**As a** downstream data engineer,  
**I want** to query the latest valid event for each `event_key` from `test_prod.p1_test`,  
**so that** I can build downstream data products from current event data.

**Acceptance criteria**

- After a successful daily run, the silver table `test_prod.p1_test` is available for querying.
- Each newly consumed source event is retained in bronze table `test_prod.p1_test_kfk_brz` with its source payload preserved and Kafka metadata available.
- The silver table contains no more than one current row per `event_key`.
- When multiple valid events exist for a key, the row with the latest Kafka record timestamp is retained; partition and offset resolve timestamp ties, as specified by the approved requirements assumption.
- The valid event's non-key JSON properties are available in the silver `attributes` object, including nested properties.
- Reprocessing previously consumed Kafka offsets does not create duplicate current rows for a key.

**Requirement traceability**: FR-03, FR-04, FR-05, FR-06; acceptance criteria in `requirements.md`.

**INVEST check**: Independent vertical outcome for a data consumer; negotiable within the approved Kafka-to-silver design; valuable for downstream data products; estimable as one current-state query capability; small enough for one consumer outcome; testable through table availability and key-level data checks.

### US-P1-02 — Query valid events when malformed messages occur

**As a** downstream data engineer,  
**I want** malformed Kafka messages isolated from valid events,  
**so that** I can query usable event data without malformed messages entering the silver table.

**Acceptance criteria**

- Valid JSON messages that meet the expected event schema continue through the pipeline into silver.
- Malformed messages are excluded from silver and written to the configured quarantine destination with their raw payload and parse error details.
- The presence of a malformed message does not prevent other valid messages in the same processing run from being available in silver.
- Quarantined records retain the Kafka metadata needed to identify their source records.

**Requirement traceability**: FR-04, FR-05, FR-07; data quality requirements and quarantine assumption in `requirements.md`.

**INVEST check**: Independently verifiable with valid and malformed message inputs; negotiable in quarantine implementation details; valuable for downstream data quality; estimable as one data-quality outcome; small and focused on consumer-visible validity; testable through silver and quarantine contents.

## Story coverage

| Requirement area | Story coverage |
|---|---|
| Daily incremental processing and bronze retention | US-P1-01 |
| JSON parsing and latest event by `event_key` | US-P1-01 |
| Malformed-message quarantine | US-P1-02 |
| Gold-layer output | Excluded by approved scope |
| Job operations and monitoring | No operator story, per user decision |
