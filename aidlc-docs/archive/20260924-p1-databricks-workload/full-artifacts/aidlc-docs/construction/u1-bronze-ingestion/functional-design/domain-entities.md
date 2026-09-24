# U1 Bronze Ingestion — Domain Entities

## Kafka Source Record

Represents one record read from the configured Kafka topic.

| Attribute | Meaning |
|---|---|
| `topic` | Kafka topic containing the record; expected value is `my-topic`. |
| `partition` | Source partition number. |
| `offset` | Record position within the partition. |
| `key` | Original Kafka record key, when present. |
| `value` | Original source value, retained unchanged. JSON interpretation belongs to U2. |
| `headers` | Original Kafka headers. |
| `source_timestamp` | Timestamp supplied by Kafka for the source record. |

**Identity**: `(topic, partition, offset)`. This identity is used to recognize the same source record during retry or replay.

## Bronze Record

Represents a Kafka Source Record persisted for downstream consumption. It carries the source record attributes unchanged and uses the Kafka source identity to prevent duplicate bronze rows when an already-persisted offset is replayed.

The Bronze Record does not introduce a second business identity, parsed JSON fields, or an ingestion-time field in this functional design. Any storage-specific representation is defined in later design and implementation stages while preserving this logical contract.

## Relationships and lifecycle

- One Kafka Source Record may be observed more than once due to retry or replay.
- Observations with the same source identity map to one logical Bronze Record.
- Distinct topic/partition/offset identities remain distinct even when their values are identical.
- The Bronze Record is the input record for U2. U2 may classify its value as valid or malformed but U1 preserves it without such classification.

## Scope note

The configured bronze destination is `test_prod.p1_test_kfk_brz`. The exact physical column types and serialization for Kafka keys and headers are implementation details for later stages; they must retain the information represented by this logical entity.
