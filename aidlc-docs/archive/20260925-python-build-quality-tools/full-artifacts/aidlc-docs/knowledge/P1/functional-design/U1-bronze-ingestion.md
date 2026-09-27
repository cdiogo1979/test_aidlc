# U1 Bronze Ingestion — Functional Design

## Purpose and boundary

Read records from the configured Kafka topic and persist source payload and metadata unchanged to bronze Delta. U1 owns Kafka acquisition, source fidelity, deduplication, and Kafka checkpoint progress. JSON interpretation and quarantine belong to U2.

## Inputs and outputs

- **Input**: Kafka record value, key, headers, topic, partition, offset, and source timestamp from the environment-configured topic.
- **Configuration**: Selected environment's Kafka hosts, secret reference, database, data path, and `bronze_lookback_days` parameter.
- **Output**: `<database>.p1_test_kfk_brz`, including nullable `bronze_ingestion_timestamp`.
- **Progress**: `{data_path}/checkpoints/P1/bronze_ingestion`.

## Business logic

1. Resolve the selected environment configuration and Kafka credentials from Databricks Secrets.
2. With zero lookback, use durable checkpoint behavior: first start begins at the earliest available offset and subsequent runs continue incrementally.
3. With positive lookback, reset the bronze checkpoint and replay from the Kafka record timestamp cutoff. Validate the value as a non-negative integer before checkpoint operations.
4. Preserve the original source value and selected Kafka metadata; do not parse, normalize, filter, or reject payloads based on JSON validity.
5. Identify records by `(topic, partition, offset)` and ensure repeated identities do not create duplicate bronze rows.
6. Enable and retain Delta CDF so U2 can consume the initial table snapshot and subsequent inserts. Do not silently skip unavailable CDF history.
7. Assign `bronze_ingestion_timestamp` as a UTC processing instant only when a source identity is first inserted. Duplicate replay does not refresh it. Existing rows remain NULL after additive schema migration.

## Business rules

- Read only the configured topic and never embed secret values in repository artifacts.
- Preserve payload and source metadata unchanged. Null-value tombstone handling is outside the confirmed topic contract.
- Kafka, read, or write failures fail the task; do not advance successful processing past an uncommitted write.
- Checkpoint progress and source-identity deduplication complement one another; this does not claim a platform-wide exactly-once guarantee.
- Malformed JSON is still a valid bronze source record; U2 owns validation and quarantine.
- If the timestamp column is absent, add it as nullable `TIMESTAMP` before writes; do not backfill old rows. An incompatible type or failed migration/validation fails before data writes.

## Domain entities

### Kafka source record / bronze record

Attributes: topic, partition, offset, key, value, headers, source timestamp, and bronze ingestion timestamp. Identity is `(topic, partition, offset)`. Repeated observations of the same identity represent one logical bronze row; distinct offsets remain distinct even when payloads match.

## Failure and recovery

No available records is a successful no-op. Kafka access, table migration, or persistence failures fail the task. Retries resume from durable progress and remain safe under source-identity deduplication. A positive lookback intentionally resets checkpoint state and may replay records.

## Historical sources

- `aidlc-docs/archive/20260924-p1-databricks-workload/full-artifacts/aidlc-docs/construction/u1-bronze-ingestion/functional-design/`
- `aidlc-docs/archive/20260924-p1-layer-timestamp-columns/full-artifacts/aidlc-docs/construction/u4-p1-layer-timestamp-metadata/functional-design/` (timestamp semantics)
