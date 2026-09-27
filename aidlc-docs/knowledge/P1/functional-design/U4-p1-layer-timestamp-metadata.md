# U4 P1 Layer Timestamp Metadata — Functional Design

## Purpose and boundary

Record when a source record is first accepted into bronze and when a valid event becomes the accepted current state in silver. U4 owns the layer-specific processing timestamps and additive schema handling. Kafka source time and existing quarantine ingestion timestamps keep their existing meanings.

## Processing logic

### Bronze

- Ensure bronze includes nullable `bronze_ingestion_timestamp TIMESTAMP` before data writes.
- Add the column to an existing table if absent; fail if the existing column has an incompatible type.
- Assign a UTC processing instant to candidate records, but persist it only when a previously unseen Kafka identity is inserted.
- A duplicate `(topic, partition, offset)` does not update the row or refresh the timestamp.

### Silver

- Ensure silver includes nullable `silver_processing_timestamp TIMESTAMP` before data writes, applying the same additive/type-validation behavior.
- Assign a UTC processing instant only when a valid event inserts a current row or wins the existing source-time/partition/offset ordering and updates it.
- Losing candidates and no-op replays do not change the current row or timestamp.
- Never derive this value from or copy `bronze_ingestion_timestamp` or Kafka `source_timestamp`.

## Business rules and invariants

- `source_timestamp` remains Kafka event time and controls latest-event ordering.
- Bronze and silver timestamps represent distinct UTC processing instants at their respective accepted write boundaries.
- New columns are nullable. Existing rows remain NULL after migration; do not infer or backfill historical timestamps.
- Migration/type validation failures fail before data writes.
- Existing CDF, checkpoints, quarantine schema/`ingestion_timestamp`, event ordering, and job sequencing are unchanged.
- If an attempted write did not commit, a retry may receive a new timestamp. A committed row's timestamp remains stable under replay unless a later-ranked silver event wins.

## Domain entities

- **Bronze source record**: Kafka identity and source metadata plus nullable `bronze_ingestion_timestamp` marking first acceptance into bronze.
- **Silver current event**: `event_key`, extensible attributes, winning Kafka source identity/time, and nullable `silver_processing_timestamp` marking acceptance as current state.
- These timestamps are independent of each other and of Kafka source time. Quarantine remains a separate existing entity.

## Historical source

- `aidlc-docs/archive/20260924-p1-layer-timestamp-columns/full-artifacts/aidlc-docs/construction/u4-p1-layer-timestamp-metadata/functional-design/`
