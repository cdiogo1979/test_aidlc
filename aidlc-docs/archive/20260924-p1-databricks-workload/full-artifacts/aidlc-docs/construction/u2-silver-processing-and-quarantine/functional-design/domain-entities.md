# U2 Silver Processing and Quarantine — Domain Entities

## Bronze Source Record

The input to U2 is one record persisted by U1. Its source identity and metadata are inherited unchanged from the bronze contract.

| Attribute | Meaning |
|---|---|
| `topic` | Kafka topic for the source record. |
| `partition` | Kafka partition number. |
| `offset` | Kafka offset within the partition. |
| `value` | Original payload bytes. |
| `source_timestamp` | Timestamp supplied by Kafka. |

**Identity**: `(topic, partition, offset)`.

## Valid Event

Represents a parsed JSON object eligible for current-state processing.

| Attribute | Meaning |
|---|---|
| `event_key` | Required nonblank string identifying the current-state entity. Kept as supplied. |
| `attributes` | Extensible collection of all other JSON object properties, preserving parsed JSON values, including nested values. No fixed event-specific schema is assumed. |
| `topic`, `partition`, `offset` | Source identity used for traceability and retry deduplication. |
| `source_timestamp` | Kafka timestamp used for latest-event ordering. |

**Business identity**: `event_key`. **Source identity**: `(topic, partition, offset)`.

## Silver Current Event

Represents the highest-ranked valid event processed for an `event_key`.

- Contains one `event_key`, its `attributes`, and the Kafka source identity and timestamp of the winning event.
- At most one current row exists for a given `event_key`.
- A new event replaces the current row only when its source timestamp is later, or its partition/offset tie-breaker ranks later for an equal timestamp.

## Quarantined Source Record

Represents a bronze record that cannot be represented as a valid event.

| Attribute | Meaning |
|---|---|
| `raw_payload` | Original source bytes retained for diagnosis. |
| `topic`, `partition`, `offset` | Kafka source identity. |
| `source_timestamp` | Original Kafka timestamp. |
| `ingestion_timestamp` | Time U2 classified the record. |
| `error` | Parse error or validation diagnostic, including invalid JSON root or `event_key`. |

**Identity**: `(topic, partition, offset)`. Reprocessing the same invalid source record updates or recognizes the same logical quarantine entry rather than adding a duplicate.

## Relationships and lifecycle

- Each bronze source record is classified as either a valid event or a quarantined record.
- A valid event may update the one current silver row for its `event_key`; older-ranked events do not replace newer state.
- Each source record identity contributes at most one logical quarantine record.
- Source metadata connects both silver and quarantine outcomes to the bronze record.

## Scope note

The event-specific JSON schema is intentionally open because no representative payload is available. Silver stores `event_key` and the remaining top-level properties in an extensible Delta `VARIANT` object, preserving arbitrary nested JSON values. Delta merge mechanics are implementation details.
