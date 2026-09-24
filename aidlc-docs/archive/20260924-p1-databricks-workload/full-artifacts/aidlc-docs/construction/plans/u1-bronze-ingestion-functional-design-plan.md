# U1 Bronze Ingestion — Functional Design Plan

## Unit context

- **Unit**: U1 — Bronze Ingestion.
- **Responsibilities**: Read incremental records from Kafka topic `my-topic`; preserve each source payload and Kafka metadata in bronze table `test_prod.p1_test_kfk_brz`.
- **Dependencies**: `configs/{environment}.yaml`, Kafka, and the configured Databricks secret reference.
- **Downstream contract**: U2 reads the persisted bronze Delta table; U3 schedules U1 before U2.
- **Assigned stories**: Supports US-P1-01 and US-P1-02 by providing persisted source events.
- **Code location**: `notebooks/P1/bronze/` (Functional Design remains technology-agnostic; exact code is a later stage).

## Functional design checklist

- [x] Define the source record and bronze entity fields.
- [x] Specify first-run offset selection and subsequent incremental behavior.
- [x] Specify source-record identity and duplicate/replay behavior.
- [x] Define malformed/null-message handling at the bronze boundary.
- [x] Define behavior for Kafka and bronze-write failures.
- [x] Generate `aidlc-docs/construction/u1-bronze-ingestion/functional-design/business-logic-model.md`.
- [x] Generate `aidlc-docs/construction/u1-bronze-ingestion/functional-design/business-rules.md`.
- [x] Generate `aidlc-docs/construction/u1-bronze-ingestion/functional-design/domain-entities.md`.
- [x] Validate the design against FR-02, FR-03, and FR-04 and the U1 unit contract.

## Question 1 — First-run Kafka position
When the workload starts with no existing checkpoint, which Kafka records should the first run read?

A) Start at the earliest available offset (Recommended if the bronze table must capture the topic's available history)

B) Start at the latest offset (capture only records arriving after initial deployment)

X) Other (please describe after `[Answer]:`)

[Answer]: A

## Question 2 — Bronze source record fields
What should bronze retain from each Kafka record to meet the 1:1 source requirement?

A) Raw value, Kafka key, headers, topic, partition, offset, and source timestamp (Recommended for traceability and replay analysis)

B) Raw value plus topic, partition, offset, and source timestamp; omit Kafka key and headers

X) Other (please describe after `[Answer]:`)

[Answer]: A

## Question 3 — Retry and replay duplicates
If a job retry re-reads a Kafka offset, how should bronze handle the same source record identity (`topic`, `partition`, `offset`)?

A) Avoid duplicate bronze rows using the source identity, in addition to checkpointed incremental progress (Recommended)

B) Allow duplicate bronze rows on retry and rely on downstream silver merge behavior

X) Other (please describe after `[Answer]:`)

[Answer]:A

## Question 4 — Null/tombstone Kafka values
Can the topic produce Kafka records with a null value (tombstones)? If yes, how should U1 preserve them for downstream handling?

A) No — the topic will not produce tombstone records

B) Yes — preserve them as source records in bronze; describe any additional handling expectation

X) Other (please describe after `[Answer]:`)

[Answer]:A

## Question 5 — Bronze validation boundary
Where should JSON validity be checked and malformed payloads be quarantined?

A) Bronze stores every source value unchanged; U2 validates JSON and quarantines malformed messages (Recommended; matches the approved bronze/silver responsibilities)

B) U1 validates JSON and separates malformed messages before writing bronze

X) Other (please describe after `[Answer]:`)

[Answer]: A

## Question 6 — Kafka or bronze-write failures
What should U1 do when Kafka is unavailable or a bronze write fails?

A) Fail the task without advancing successful progress; configured job retry or a later run resumes from the last committed checkpoint (Recommended)

B) Skip the failed batch and continue with later offsets

X) Other (please describe after `[Answer]:`)

[Answer]: A

## Deferred design detail

The exact Kafka JSON payload schema is not needed for U1 because bronze preserves the raw value. U2 will define schema parsing and `event_key` behavior in its Functional Design. The Kafka secret-scope value and job retry count remain environment/deployment details for later stages.
