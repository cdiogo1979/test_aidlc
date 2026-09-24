# U4 NFR Design Patterns — P1 Layer Timestamp Metadata

## UTC Timestamp Pattern

- Configure each notebook's Spark session timezone to UTC before timestamp expressions or writes are evaluated.
- Generate processing timestamps with Spark's current-timestamp expression in the existing DataFrame pipeline. Do not collect records to Python or create a separate timestamp lookup per row.
- Persist the timestamp in the same Delta insert/update as its accepted data row.
- Keep `source_timestamp` separate and do not use either processing timestamp to select the silver winner.
- Databricks runtime verification must confirm session timezone behavior and serialized/display interpretation.

## Additive Schema Compatibility Pattern

1. Create a missing table with its new nullable timestamp field in the initial schema.
2. For an existing table, inspect schema metadata before processing data. If the field is absent, add only that nullable `TIMESTAMP` field.
3. Re-read/validate the schema after migration. If inspection, migration, or type validation fails, stop before processing the batch and propagate a clear task failure.
4. Never backfill old rows; the additive Delta column leaves pre-existing values NULL.
5. Preserve all other schema fields and table properties, including bronze CDF configuration.

Concrete Delta DDL and CDF behavior must be checked on the target Databricks Runtime before production use. The local implementation can validate code paths and generated statements but cannot certify live Delta behavior.

## Replay-Safe Merge Pattern

- **Bronze**: Continue merging by `(topic, partition, offset)` with insert-only behavior. Candidate rows carry a UTC timestamp; only an unseen identity is inserted. A match never updates the timestamp.
- **Silver**: Continue selecting the latest candidate per `event_key` by `source_timestamp`, partition, and offset. Candidate rows carry their own processing timestamp. The existing conditional update and insert paths persist it only when the candidate is accepted.
- **Retry**: Keep the existing streaming checkpoints and Delta transaction behavior. Replayed already-committed input must encounter an existing bronze identity or a silver row that does not satisfy the later-event predicate, preserving the accepted value.

## Resilience and Failure Handling

- Preserve current exception propagation from schema setup and Delta writes; do not swallow migration errors.
- Do not add retries, recovery tables, or alternate write paths. The current checkpoint and idempotent merges remain the recovery mechanism.
- A failure before a Delta merge commits may be retried with a later candidate processing instant; no accepted row exists yet. Once a row commits, retries must not refresh it.

## Performance and Scale

- Keep timestamp values as native Spark expressions in existing transformations.
- Do not add row-wise Python UDFs, extra per-row actions, or full-table scans.
- Schema metadata inspection and post-migration validation are performed at table initialization, not for every row.
- No numeric throughput, latency, or growth SLO is introduced.

## Security and Availability

- No new component, network path, permission, secret, or data classification is introduced.
- Existing platform access controls and scheduled-job availability remain unchanged. Security Baseline and Resiliency Baseline remain disabled per project configuration.

## NFR Traceability

| NFR | Applied pattern |
|---|---|
| NFR-01 | UTC Spark session and native Spark timestamp expression; distinct fields. |
| NFR-02 | Existing insert-only and conditional update Delta merge semantics. |
| NFR-03 | Additive migration plus schema validation; preserve existing properties. |
| NFR-04 | Nullable add-column migration without backfill. |
| NFR-05 | Fail-fast initialization and propagated task failure. |
| NFR-06 | Existing projections/merges; no per-row action or additional full-table scan. |
| NFR-07 | No change to job, CDF mode, checkpoint, winner ordering, or quarantine. |
| NFR-08 | Localized notebook changes, documented helpers, and focused tests in later stages. |
