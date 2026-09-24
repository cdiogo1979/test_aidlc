# U4 Business Logic Model — P1 Layer Timestamp Metadata

## Purpose

Record the time at which a source record is accepted into bronze and the time at which a valid event becomes the accepted current state in silver. Keep those processing times separate from Kafka event time.

## Processing Flow

### Bronze ingestion

1. Ensure the bronze table exists with the existing source fields and nullable `bronze_ingestion_timestamp TIMESTAMP`.
2. If the table already exists, inspect its schema. Add the timestamp column if absent; fail clearly if a same-named column has an incompatible type.
3. Preserve the existing Kafka source projection, mapping Kafka `timestamp` to `source_timestamp`. Set `bronze_ingestion_timestamp` to the current UTC processing instant for candidate rows.
4. Deduplicate the micro-batch by `(topic, partition, offset)` as today.
5. Merge using that Kafka identity. Insert unseen records with their candidate timestamp; do not update a matching target row.

### Silver processing

1. Ensure the silver table exists with its existing columns and nullable `silver_processing_timestamp TIMESTAMP`.
2. If the silver table already exists, add the column when absent and validate its type before processing. Do not backfill existing rows.
3. Continue consuming bronze insert CDF records, parsing and validating the payload, and routing invalid records to the existing quarantine path.
4. For valid candidates, preserve the existing per-key winner order: `source_timestamp`, then Kafka partition, then offset. Exclude bronze ingestion time from the silver timestamp value.
5. Set `silver_processing_timestamp` to the current UTC processing instant on the winning silver candidate.
6. Merge by `event_key`. Insert when no target row exists; update only when the existing later-event predicate accepts the source candidate. A no-op or losing candidate does not modify the target timestamp.

## State and Retry Semantics

- Each layer records its own processing instant at its accepted Delta write boundary.
- Bronze duplicate Kafka identities remain insert-only and retain the first committed bronze timestamp.
- Silver retries of an already committed winner do not satisfy the strict later-event predicate and therefore retain the committed silver timestamp.
- When an attempted write did not commit, a later retry may receive a new processing instant because no accepted row existed yet.
- New fields are nullable; rows already present at migration remain `NULL`.

## Unchanged Paths

- `source_timestamp` continues to represent Kafka source time and remains unchanged.
- Bronze CDF, streaming checkpoints, available-now triggers, silver ordering, and the job's bronze-before-silver sequence remain unchanged.
- Quarantine keeps its existing `ingestion_timestamp` behavior and schema.

## Failure Behavior

If a table cannot be inspected, additively migrated, or validated as having the expected timestamp type, fail the notebook task before writing batch data. Preserve the existing exception propagation so the stream does not silently advance past a failed batch.

## Requirement Traceability

This flow implements FR-01 through FR-09. Databricks-specific DDL and CDF compatibility remain subject to NFR design and runtime verification.
