# U1 Bronze Ingestion — Business Logic Model

## Purpose

Capture Kafka source records from `my-topic` into the bronze dataset so downstream processing can inspect each original value together with its source identity and metadata. U1 does not interpret the message payload.

## Inputs and outputs

| Kind | Description |
|---|---|
| Input | Kafka records from topic `my-topic`, including value, key, headers, topic, partition, offset, and source timestamp. |
| Configuration | The selected environment's Kafka host and secret reference, plus the configured bronze destination. Secret values are obtained through the approved secret store. |
| Output | Bronze records in `test_prod.p1_test_kfk_brz`, preserving the source value and the selected Kafka fields. |
| Progress | A durable checkpoint records successfully committed source progress for subsequent runs. |

## Main flow

1. Load the selected environment configuration and resolve Kafka connectivity using its host and secret reference.
2. Establish the read position. On the first run with no checkpoint, begin at the earliest offset available from Kafka. On subsequent runs, continue incrementally from the durable checkpoint.
3. Read records from `my-topic` and retain the original value, key, headers, topic, partition, offset, and source timestamp.
4. Identify each source record by `(topic, partition, offset)`. Do not create a second bronze record for a source identity already persisted when retry or replay presents it again.
5. Persist source records to the bronze destination and advance durable progress only as successful processing is committed.
6. Ensure Delta Change Data Feed is enabled on the bronze table, including existing tables before adding further records.
7. Make successfully persisted records available to U2 through the table snapshot and subsequent CDF insert changes. U2 performs JSON validation and routes malformed payloads to quarantine.

## Alternate and failure flows

- **No available records**: Complete the run without adding bronze records; retain the existing checkpoint.
- **Null value / tombstone**: Not an expected input under the confirmed topic contract. U1 has no tombstone transformation or business handling rule.
- **Malformed JSON**: Preserve the value unchanged in bronze. U1 does not parse or discard it; U2 owns validation and quarantine.
- **Kafka read or bronze persistence failure**: Fail the task. Do not intentionally skip the failing input or mark its progress successful. A configured retry or later run resumes from the last committed checkpoint; replayed source identities remain protected by the deduplication rule.

## Unit boundary

U1 owns acquisition, source fidelity, bronze persistence, and incremental progress. U2 owns parsing, valid-event shaping, and malformed-message quarantine. U3 owns the daily job orchestration and runs U2 after successful U1 completion.

## Traceability

- **FR-02**: Read the configured Kafka topic using environment-specific connectivity and secret references.
- **FR-03**: Process incrementally with durable progress across successful runs.
- **FR-04**: Preserve source values and traceability metadata in bronze.
- **U1 contract**: Produce the bronze dataset consumed by U2, without taking on U2 validation responsibilities.
