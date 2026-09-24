# U4 Domain Entities — P1 Layer Timestamp Metadata

## Bronze Source Record

Represents one Kafka source record persisted for downstream processing.

| Attribute | Type | Meaning |
|---|---|---|
| `value` | BINARY | Original Kafka payload. |
| `key` | BINARY, nullable | Original Kafka key. |
| `headers` | ARRAY of key/value records, nullable | Original Kafka headers. |
| `topic` | STRING | Kafka topic. |
| `partition` | INT | Kafka partition. |
| `offset` | BIGINT | Record offset within the partition. |
| `source_timestamp` | TIMESTAMP, nullable | Kafka source/event time. |
| `bronze_ingestion_timestamp` | TIMESTAMP, nullable | UTC instant when this Kafka identity was first accepted into bronze. |

**Identity**: `(topic, partition, offset)`.

**Lifecycle**: Candidate records receive a processing instant. The insert-only merge persists it only for a previously unseen identity. Existing records retain their value during replay. Existing rows remain NULL after additive migration.

## Silver Current-State Event

Represents the latest accepted valid event for one business `event_key`.

| Attribute | Type | Meaning |
|---|---|---|
| `event_key` | STRING | Nonblank key extracted from the valid JSON object; silver merge identity. |
| `attributes` | VARIANT | Non-key properties from the event payload. |
| `topic` | STRING | Kafka source topic. |
| `partition` | INT | Kafka source partition, used in winner ordering. |
| `offset` | BIGINT | Kafka source offset, used in winner ordering. |
| `source_timestamp` | TIMESTAMP, nullable | Kafka source/event time, used in winner ordering. |
| `silver_processing_timestamp` | TIMESTAMP, nullable | UTC instant when this event was accepted as the current silver row. |

**Identity**: `event_key`.

**Lifecycle**: A valid first event inserts a row with a silver processing instant. A candidate that wins existing ordering updates the row and its timestamp. A losing or no-op replay leaves the row unchanged. Existing rows remain NULL after additive migration until a later winning update occurs.

## Timestamp Relationship

`bronze_ingestion_timestamp` describes acceptance into the bronze layer. `silver_processing_timestamp` describes acceptance into the silver current-state layer. They are independent values and neither is derived from `source_timestamp` or copied from one another. Quarantine remains a separate existing entity with its current `ingestion_timestamp`.
