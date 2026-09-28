# P2 Pipeline — Business Logic Model

## Purpose and boundaries

P2 is an independent instance of the approved P1 daily data pipeline. Its only input-topic difference is Kafka topic `my-test-p2`. Processing behavior, schemas, sequencing, retries, lookback semantics, timestamps, and quarantine rules follow P1. P1 remains unchanged.

## Processing flow

1. The P2 job starts bronze ingestion with environment and bronze lookback parameters.
2. Bronze reads only the configured P2 topic, preserves the source payload and Kafka metadata, and writes the P2 bronze Delta table with CDF enabled.
3. If bronze succeeds, the job starts silver processing with environment and silver lookback parameters.
4. Silver reads P2 bronze CDF, retains the latest valid event by `event_key`, and writes P2 silver state and invalid records to P2 quarantine.
5. Any required task failure fails the overall job; silver does not run after bronze failure.

## Persisted state ownership

- Bronze table: `<database>.p2_test_kfk_brz`.
- Silver table: `<database>.p2_test`.
- Quarantine table: `<database>.p2_test_kfk_quarantine`.
- Checkpoints: `{data_path}/checkpoints/P2/bronze_ingestion` and `{data_path}/checkpoints/P2/silver_processing`.
- P2 uses the shared `configs/prod.yaml`. The existing `kafka.topic` remains the P1 default; P2 selects `kafka.topics_by_project.P2` (`my-test-p2`). Both projects use the same `prod` profile and shared Kafka hosts/authentication settings.

## Candidate testable property

The copied bronze `_jaas_quote` helper is pure. A generated property test can verify its escaping invariant for strings containing quotes and backslashes. The Spark DataFrame pipelines use external Spark/Delta state and are outside the user's partial pure-function PBT selection. No serialization/deserialization round-trip is added by P2.
