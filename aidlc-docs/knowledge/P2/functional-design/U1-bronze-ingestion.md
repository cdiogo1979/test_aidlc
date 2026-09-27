# U1 P2 Bronze Ingestion — Functional Design

## Purpose and boundary

Read Kafka records from the explicit P2 project topic and preserve source payload and metadata unchanged in P2 bronze Delta. U1 owns Kafka acquisition, source fidelity, deduplication, and P2 Kafka checkpoint progress. JSON interpretation and quarantine belong to U2.

## Inputs and outputs

- **Input**: Kafka record value, key, headers, topic, partition, offset, and source timestamp from topic `my-test-p2`.
- **Configuration**: Shared `configs/prod.yaml`; Kafka settings and secret references; `bronze_lookback_days` parameter.
- **Output**: `<database>.p2_test_kfk_brz`, with Delta CDF enabled.
- **Progress**: `{data_path}/checkpoints/P2/bronze_ingestion`.

## Business logic and rules

1. Resolve `kafka.topics_by_project.P2`; fail closed if the mapping or topic is absent/blank. Never fall back to the shared default topic.
2. Resolve Kafka credentials through Databricks Secrets; do not store secret values in source or job parameters.
3. With zero lookback, continue from the durable P2 checkpoint (starting at earliest available offset on first start). With positive lookback, reset only the P2 bronze checkpoint and replay from the configured Kafka timestamp cutoff.
4. Preserve source payload and Kafka metadata. Deduplicate by `(topic, partition, offset)` and retain CDF for silver.
5. Keep P1's `kafka.topic`, tables, and checkpoints unchanged and isolated from P2.

## Failure and recovery

Kafka, configuration, checkpoint, or persistence failures fail the task. Retries rely on the P2 checkpoint and source-identity deduplication. A positive lookback intentionally resets P2 bronze checkpoint state and may replay records; it does not alter P1 state.
