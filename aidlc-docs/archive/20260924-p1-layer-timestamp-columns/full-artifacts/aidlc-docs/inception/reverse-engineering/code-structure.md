# Code Structure

## Build System

- **Type**: Repository of Databricks Python notebooks and a Declarative Automation Bundle.
- **Configuration**: `jobs/P1/databricks.yml` includes the job resource YAML. `configs/prod.yaml` supplies the current environment settings.
- **Dependency packaging**: No package/build manifest was found. `src/common.py` is imported from the workspace project root.

## Key Modules

- `notebooks/P1/bronze/bronze_ingestion.py` — Kafka source options, bronze table creation/CDF, idempotent writes, and streaming entry point.
- `notebooks/P1/silver/silver_processing.py` — silver/quarantine table creation, JSON classification, silver merge, quarantine writes, and CDF streaming entry point.
- `src/common.py` — project-root discovery, YAML environment loading, required config validation, and safe SQL identifier quoting.
- `jobs/P1/databricks.yml` — Bundle configuration and production target.
- `jobs/P1/resources/p1-daily-pipeline.yml` — schedule, cluster, job identity, retry variables, and ordered notebook tasks.
- `configs/prod.yaml` — database, S3 path, Kafka connection settings, and secret-key reference; username and secret scope remain unset.
- `tests/test_aidlc_intent.py` — lifecycle/compaction utility tests; these do not test P1 data processing.

## Design Patterns

### Checkpointed incremental streaming
- **Location**: Both notebooks.
- **Purpose**: Resume reads across scheduled runs without reprocessing all source events.
- **Implementation**: `AvailableNow` triggers with stable S3 checkpoint locations.

### Idempotent Delta writes
- **Location**: Bronze and silver notebook write paths.
- **Purpose**: Make retries and replay safe.
- **Implementation**: Bronze insert-only merge by `(topic, partition, offset)`; silver latest-event merge by `event_key`; quarantine deduplication by Kafka identity.

## Critical Dependencies

- Apache Spark Structured Streaming Kafka source.
- Delta Lake tables and Change Data Feed.
- Databricks runtime features, including `VARIANT` support (15.4 LTS or later per project documentation).
- Databricks `dbutils` for widgets and secret access.
- PyYAML through the shared config library.
