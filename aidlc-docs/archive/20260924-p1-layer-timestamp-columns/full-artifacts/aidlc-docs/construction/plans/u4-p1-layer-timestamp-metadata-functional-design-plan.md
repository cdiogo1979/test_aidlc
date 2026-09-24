# U4 Functional Design Plan — P1 Layer Timestamp Metadata

## Scope

Define the domain data, write behavior, additive migration rules, and edge cases for `bronze_ingestion_timestamp` and `silver_processing_timestamp`. Keep this design focused on U4 and preserve the approved pipeline behavior.

## Category Assessment

- **Business logic modeling**: The two layer-specific write boundaries and latest-event merge behavior are specified in the approved requirements. Model them explicitly below.
- **Domain model**: The existing Kafka source record and silver current-state record are documented in the reverse-engineering and requirements artifacts; only their timestamp metadata is extended.
- **Business rules**: UTC instants, first-insert/winning-update assignment, replay stability, nullable migration, and no backfill are explicit in FR-01 through FR-09.
- **Data flow**: Existing Kafka → bronze Delta/CDF → silver/quarantine flow is documented; no flow boundary changes.
- **Integration points**: No external integration or job change; bronze remains the persisted handoff and U3 task ordering remains unchanged.
- **Error handling**: Requirements state unsafe migration or schema mismatch must fail clearly; preserve existing task failure propagation.
- **Business scenarios**: First insert, duplicate replay, winning silver update, losing older event, existing-table migration, new-table creation, and malformed quarantine are covered by approved scenarios.
- **Frontend**: Not applicable; this unit has no user interface.

No clarification questions are needed. Requirements and observed merge behavior provide enough detail for these decisions. The design treats timestamps as UTC processing instants created for an attempted write and persisted only when the Delta merge accepts the insert/update; exact time can vary across a retry that had not previously committed, while already committed rows remain unchanged. No unanswered `[Answer]:` tags are present.

## Design Generation Checklist

- [x] Analyze U4 boundaries, requirements, existing bronze/silver write paths, and baseline P1 design.
- [x] Evaluate the functional design clarification categories; no unresolved ambiguity identified.
- [x] Define entities and timestamp field semantics.
- [x] Define bronze and silver write, migration, replay, and error rules.
- [x] Describe functional processing flow and relevant edge cases.
- [x] Validate FR-01 through FR-09 coverage and preserve explicit scope exclusions.
- [x] Generate `business-logic-model.md`.
- [x] Generate `business-rules.md`.
- [x] Generate `domain-entities.md`.

## Outputs

Functional design artifacts are under `aidlc-docs/construction/u4-p1-layer-timestamp-metadata/functional-design/`. They are submitted for review before proceeding to NFR Requirements.
