# U2 Silver Processing and Quarantine — Functional Design Plan

## Unit context

- **Unit**: U2 — Silver Processing and Quarantine.
- **Responsibilities**: Read bronze Delta records, parse valid JSON events into the silver current-state table, and isolate invalid records in quarantine.
- **Inputs**: Bronze table `test_prod.p1_test_kfk_brz`; environment configuration in `configs/{environment}.yaml`.
- **Outputs**: Silver table `test_prod.p1_test` and quarantine table `test_prod.p1_test_kfk_quarantine`.
- **Assigned stories**: US-P1-01 and US-P1-02; requirements FR-05, FR-06, and FR-07.
- **Code location**: `notebooks/P1/silver/`.
- **Approved ordering rule**: Kafka record timestamp determines the latest event per `event_key`; partition and offset break timestamp ties. This rule is already approved and is not reopened here.

## Functional design checklist

- [x] Define the JSON event schema and silver columns as `event_key` plus an extensible attributes map; no sample payload was available.
- [x] Define required fields, permissive property handling, and `event_key` validation behavior.
- [x] Define handling for unknown/additional fields and nested JSON values.
- [x] Specify source-record identity, retry behavior, and deduplication across silver and quarantine.
- [x] Specify parse/validation error details and quarantine record fields.
- [x] Ensure malformed records do not prevent valid records in the same run from reaching silver.
- [x] Define silver and quarantine entity contracts and write behavior.
- [x] Generate the U2 functional design artifacts and validate against FR-05, FR-06, FR-07, US-P1-01, US-P1-02, and the U2 unit contract.

## Question 1 — Expected JSON event schema

What JSON fields and types should the silver table expose? Include a representative message or list each field's name, type, and whether it is required. The approved requirements already establish that `event_key` is required.

A) Provide a representative JSON message; use it to propose the remaining field definitions for review.

B) Provide a field-by-field schema (name, type, required/optional) after `[Answer]:`.

X) Other (please describe after `[Answer]:`)

[Answer]: A

## Question 2 — Missing or invalid event key

How should U2 handle a JSON object whose `event_key` is missing, null, blank, or not a string?

A) Exclude it from silver and quarantine it with a validation error (Recommended; maintains the one-current-row-per-key contract).

B) Convert scalar values to strings and quarantine only missing, null, or blank keys.

X) Other (please describe after `[Answer]:`)

[Answer]: A

## Question 3 — Unknown or additional JSON fields

When a valid event includes fields not in the agreed schema, how should U2 handle them?

A) Preserve them in silver using an extensible representation, while keeping agreed fields queryable.

B) Ignore unknown fields and write the agreed schema only.

C) Treat unknown fields as a schema violation and quarantine the event.

X) Other (please describe after `[Answer]:`)

[Answer]: A

## Question 4 — Type and required-field validation

Beyond `event_key`, how should schema mismatches be treated?

A) Require agreed required fields and types; quarantine events that fail validation, while allowing omitted optional fields (Recommended for predictable silver data).

B) Parse JSON syntax only; retain absent or mismatched fields as null where possible.

X) Other (please describe after `[Answer]:`)

[Answer]: B

## Question 5 — Retry and quarantine duplicates

If a run reprocesses a bronze source record identified by `(topic, partition, offset)`, what should happen to its U2 outputs?

A) Make both silver upserts and quarantine writes idempotent by source identity, so retries do not add duplicate current or quarantine records (Recommended).

B) Keep silver current-state upserts idempotent, but allow repeated quarantine entries to preserve each processing attempt.

X) Other (please describe after `[Answer]:`)

[Answer]: A

## Already approved behavior

- Retain one latest valid silver row per `event_key`, ordered by Kafka timestamp, then partition and offset for ties.
- Keep malformed events out of silver and capture raw payload, Kafka topic/partition/offset/timestamp, ingestion timestamp, and parse error in quarantine.
- Continue processing valid events when malformed events occur in the same run.

## Answers applied

Answers: Q1 A (sample-driven schema, then clarified to extensible map without a sample); Q2 A; Q3 A; Q4 B; Q5 A. The clarification selected B: use `event_key` and an extensible map for all other JSON properties, preserving parsed value types and validating JSON syntax only.
