# U2 Silver Processing and Quarantine — Functional Design

## Purpose and boundary

Consume persisted bronze records, publish the latest valid event per `event_key` to silver, and retain malformed or invalid records in quarantine. U2 owns CDF consumption, JSON validation, current-state selection, and quarantine. U1 owns Kafka acquisition and bronze persistence.

## Inputs and outputs

- **Input**: Bronze table `<database>.p1_test_kfk_brz` through Delta CDF, including the initial snapshot on first stream start.
- **Configuration**: Selected environment and `silver_lookback_days` parameter.
- **Silver output**: `<database>.p1_test`, at most one latest row per valid `event_key`, with non-key properties stored in `attributes` as Delta `VARIANT`.
- **Quarantine output**: `<database>.p1_test_kfk_quarantine`, preserving raw payload, source identity/metadata, ingestion timestamp, and diagnostic.
- **Progress**: `{data_path}/checkpoints/P1/silver_processing`.

## Business logic

1. With zero lookback, resume the durable CDF checkpoint. With positive lookback, reset the silver checkpoint and replay from the bronze CDF commit-time cutoff. Validate as a non-negative integer before checkpoint operations.
2. Parse each non-null payload as JSON. Accept only a JSON object with a present, nonblank string `event_key`; preserve the key as supplied.
3. Place all other top-level properties in the extensible `attributes` value, preserving JSON types and nested objects/arrays. Missing fields remain absent.
4. Rank accepted events by Kafka `source_timestamp`, then partition, then offset. Keep the greatest candidate per key in a batch and merge only when it outranks the stored row.
5. Route invalid JSON, non-object roots, or invalid keys to quarantine. Deduplicate quarantine by `(topic, partition, offset)` and preserve the original payload and diagnostic context.
6. Record `silver_processing_timestamp` as a UTC processing instant only on an accepted insert or winning update. Losing candidates and no-op replay do not refresh it.

## Business rules

- U2 reads bronze Delta only; it does not read Kafka directly.
- Silver business identity is `event_key`; source identity is `(topic, partition, offset)`.
- Do not coerce or trim a valid event key. Do not impose a fixed schema on other JSON properties.
- Malformed records do not block valid records in the same run.
- Unexpected bronze updates/deletes or expired CDF history fail the task rather than silently skipping data. Recovery from missing history requires intentional full refresh/rebuild and checkpoint reset.
- Read and persistence failures fail U2; the job must not report a partial result as successful.
- If the processing timestamp column is absent, add nullable `TIMESTAMP` before writes without backfill. Incompatible type or failed migration/validation fails before processing writes.
- Quarantine retains its existing `ingestion_timestamp` semantics; this design does not replace it with the silver processing timestamp.

## Domain entities

### Bronze source record

Carries original payload and Kafka metadata; identity is `(topic, partition, offset)`.

### Valid event and silver current event

A valid event has a nonblank string `event_key`, extensible `attributes`, Kafka source identity, and source timestamp. Silver contains one current row per key: the highest-ranked event under timestamp/partition/offset ordering. Its `silver_processing_timestamp` marks acceptance into current state, not source event time.

### Quarantined source record

Represents a malformed or invalid bronze record and retains raw payload, source identity, source timestamp, ingestion timestamp, and error diagnostic. Identity is `(topic, partition, offset)`; repeated invalid source records map to one logical quarantine row.

## Historical sources

- `aidlc-docs/archive/20260924-p1-databricks-workload/full-artifacts/aidlc-docs/construction/u2-silver-processing-and-quarantine/functional-design/`
- `aidlc-docs/archive/20260924-p1-layer-timestamp-columns/full-artifacts/aidlc-docs/construction/u4-p1-layer-timestamp-metadata/functional-design/` (timestamp semantics)
