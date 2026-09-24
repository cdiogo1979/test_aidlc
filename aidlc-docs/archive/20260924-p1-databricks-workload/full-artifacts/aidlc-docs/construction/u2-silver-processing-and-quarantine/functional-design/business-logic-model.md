# U2 Silver Processing and Quarantine — Business Logic Model

## Purpose

Read persisted bronze records, expose valid events in the silver current-state table, and retain malformed records with diagnostic source context in quarantine.

## Inputs and outputs

| Kind | Description |
|---|---|
| Input | Bronze inserts from the Delta Change Data Feed of `test_prod.p1_test_kfk_brz`, including raw binary payload and Kafka source metadata. On first start, the stream processes the current table snapshot, then subsequent changes. |
| Silver output | At most one current row per valid, nonblank string `event_key` in `test_prod.p1_test`. Each row contains the key, all other parsed JSON properties in an extensible Delta `VARIANT` object, and Kafka source metadata. |
| Quarantine output | One logical quarantine record per invalid bronze source identity in `test_prod.p1_test_kfk_quarantine`, retaining raw payload, topic, partition, offset, source timestamp, ingestion timestamp, and parse/validation error. |

## Main flow

1. Read bronze change records available after successful U1 completion using Structured Streaming with Delta Change Data Feed and `AvailableNow`. Use a stable checkpoint under `{data_path}/checkpoints/P1/silver_processing`; the first stream start includes the current bronze snapshot, while later runs resume from the checkpoint.
2. Decode each non-null source payload as JSON and parse it without requiring known property types or additional required fields.
3. Require a JSON object with a non-null, nonblank string `event_key`. Preserve the key as supplied; do not coerce other types or trim it for storage.
4. For accepted events, place every other top-level property in an extensible Delta `VARIANT` object. Preserve parsed JSON values, including nested objects and arrays. Missing properties remain absent; no schema-based null filling is required.
5. Compare accepted events by Kafka source timestamp, then partition and offset to resolve timestamp ties. Keep only the latest candidate per `event_key` in the batch and upsert it into silver only when it ranks later than the stored row. Replaying the same source identity does not add a duplicate current row.
6. For malformed JSON, a non-object JSON root, or an invalid `event_key`, write the original payload and source metadata with a parse or validation diagnostic to quarantine. Upsert/deduplicate quarantine records by `(topic, partition, offset)`.
7. Process valid and invalid records independently so a malformed record does not prevent valid records in the same run from reaching silver.

## Alternate and failure flows

- **Empty bronze input**: Complete without changing silver or quarantine.
- **Missing, null, blank, or non-string `event_key`**: Quarantine the source record; do not create a silver row.
- **Syntactically valid JSON with fields of any JSON type**: Accept the event if it has a valid `event_key`; preserve other values in the `VARIANT` attributes object without schema validation.
- **Repeated source identity**: Silver remains one current row per key; quarantine remains one logical record per invalid source identity.
- **Unexpected bronze update/delete event**: Fail the task; U1's approved bronze contract is insert-only and U2 does not define delete/update semantics.
- **CDF history expired**: Fail rather than silently skipping missing source versions. Recovery requires an intentional downstream full refresh/rebuild and checkpoint reset.
- **Read or persistence failure**: Fail U2 so the job reports unsuccessful processing. Do not treat a partial run as complete; retry/replay is safe through source-identity idempotency and ordered silver upserts.

## Unit boundary

U1 owns Kafka acquisition, source fidelity, and bronze persistence. U2 owns JSON parsing, event shaping, latest-current-state selection, and quarantine. U3 schedules U2 after U1 succeeds.

## Traceability

- **FR-05**: Parse JSON payloads and expose their properties in silver.
- **FR-06**: Maintain the latest current event by `event_key` using the approved Kafka timestamp, partition, and offset ordering.
- **FR-07**: Isolate malformed messages in quarantine while allowing valid events through.
- **US-P1-01 / US-P1-02**: Provide current queryable valid events and preserve malformed source records with diagnostics.
