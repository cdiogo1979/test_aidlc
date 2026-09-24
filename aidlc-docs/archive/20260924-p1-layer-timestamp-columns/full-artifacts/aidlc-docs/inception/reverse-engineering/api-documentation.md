# API Documentation

## External Interfaces

### Kafka source
- **Protocol**: Kafka Structured Streaming source with SASL_SSL/PLAIN authentication.
- **Topic**: Configured by `kafka.topic` (`my-topic` in `configs/prod.yaml`).
- **Input**: Binary key/value and headers, topic, partition, offset, and Kafka timestamp.
- **Authentication**: Username and Databricks secret scope are deployment configuration; password is retrieved from Databricks Secrets using `kafka.secret_key`.

### Databricks job parameters
- **Parameter**: `environment`.
- **Default**: `prod` for the configured production target and interactive notebook defaults.
- **Purpose**: Select `configs/{environment}.yaml` for both notebook tasks.

## Internal APIs

### `src.common`
- `find_project_root(start_path: str | Path | None = None) -> Path` — locate the project root.
- `load_environment_config(environment: str, project_root: Path | None = None) -> dict[str, Any]` — load environment YAML.
- `required_text(mapping: dict[str, Any], key: str, setting: str) -> str` — validate a required nonblank setting.
- `quote_qualified_identifier(identifier: str) -> str` — quote a qualified SQL identifier.

### Bronze notebook
- `_ensure_bronze_table(table_name: str) -> None` — create the bronze table if missing and enable CDF.
- `_write_batch(batch_df: DataFrame, _batch_id: int, table_name: str) -> None` — insert unseen Kafka identities.
- `run_bronze_ingestion(environment: str, config: dict[str, Any]) -> None` — execute checkpointed Kafka ingestion.

### Silver notebook
- `_ensure_output_tables() -> None` — create silver and quarantine outputs and validate VARIANT support.
- `_classify_bronze_records(records: DataFrame) -> DataFrame` — parse and validate records.
- `_write_silver(valid_records: DataFrame) -> int` — merge latest valid per-key rows.
- `_write_quarantine(invalid_records: DataFrame) -> int` — persist invalid records and diagnostics.
- `run_silver_processing() -> None` — process available bronze CDF changes.

## Data Models

### Bronze table `test_prod.p1_test_kfk_brz`

Fields: `value BINARY`, `key BINARY`, `headers ARRAY<STRUCT<key STRING,value BINARY>>`, `topic STRING`, `partition INT`, `offset BIGINT`, and `source_timestamp TIMESTAMP`. No processing/ingestion timestamp column is currently defined.

### Silver table `test_prod.p1_test`

Fields: `event_key STRING`, `attributes VARIANT`, Kafka `topic`, `partition`, and `offset`, plus `source_timestamp TIMESTAMP`. No processing/ingestion timestamp column is currently defined.

### Quarantine table `test_prod.p1_test_kfk_quarantine`

Fields include raw payload, Kafka identity and `source_timestamp`, `ingestion_timestamp TIMESTAMP`, and parse/validation `error STRING`.
