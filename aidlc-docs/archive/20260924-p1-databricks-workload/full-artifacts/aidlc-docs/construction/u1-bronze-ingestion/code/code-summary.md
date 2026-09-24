# U1 Bronze Ingestion — Code Summary

## Artifact

- **Notebook**: `notebooks/P1/bronze/bronze_ingestion.py`
- **Shared configuration library**: `src/common.py` (`find_project_root`, `load_environment_config`, `required_text`, and `quote_qualified_identifier`).
- **Entry point**: `run_bronze_ingestion(environment, config)`; the notebook supplies its validated environment name and loaded configuration. The Databricks task supplies the `environment` widget (defaults to `prod` for interactive use).
- **Configuration**: The notebook imports `src.common`; the shared helper loads and validates `configs/{environment}.yaml` from the project root. `P1_PROJECT_ROOT` may identify the deployed project root when needed.
- **Source**: Kafka topic and hosts from configuration, authenticated with SASL_SSL/PLAIN; username is a non-secret config value and password is retrieved with `dbutils.secrets.get` using the configured scope and key.
- **Destination**: Delta table `<database>.p1_test_kfk_brz`; current configured database is `test_prod`.

## Bronze schema

| Column | Logical content | Type |
|---|---|---|
| `value` | Original Kafka payload, unchanged | Binary |
| `key` | Original Kafka key | Binary |
| `headers` | Original Kafka headers | Array of key/binary-value structs |
| `topic` | Kafka topic | String |
| `partition` | Kafka partition | Integer |
| `offset` | Kafka offset | Long |
| `source_timestamp` | Kafka source timestamp | Timestamp |

Source identity is `(topic, partition, offset)`. The notebook uses an insert-only Delta merge in `foreachBatch` to avoid inserting the same identity more than once when a micro-batch is retried. The bronze table enables Delta Change Data Feed for incremental U2 consumption, both when created and when an existing table is encountered. CDF/table history must remain available for U2's recovery window. Payload parsing and quarantine remain U2 responsibilities.

## Incremental run behavior

- First run without an existing checkpoint starts at the earliest Kafka offsets.
- Later runs resume from the checkpoint at `{data_path}/checkpoints/P1/bronze_ingestion`.
- `Trigger.AvailableNow` consumes available unprocessed records in bounded micro-batches and then exits, matching the scheduled daily task.
- Kafka or Delta failures fail the task; the P1 job's deployment-configured retry can resume from committed checkpoint progress.
- The bronze Delta table has Change Data Feed enabled. U2's first CDF stream processes the current table snapshot, then consumes later changes using its own checkpoint.

## Deployment values required

`configs/prod.yaml` contains `username: null` and `secret_scope: null` because these deployment values were not supplied. Set both before running. Store the corresponding password only in Databricks Secrets under key `my-secret`. The selected Databricks Runtime must support Kafka `AvailableNow` (10.4 LTS or later). `data_path` must remain a stable S3 path accessible to the job identity.

## Design references

- Kafka authentication uses Databricks' documented shaded Kafka `PlainLoginModule` class and `SASL_SSL`/`PLAIN` options: [Databricks Kafka authentication](https://docs.databricks.com/aws/en/connect/streaming/kafka/authentication).
- Incremental batch execution uses `AvailableNow`, which Databricks documents for scheduled Kafka ingestion: [Databricks Structured Streaming triggers](https://docs.databricks.com/aws/en/structured-streaming/triggers).
- Kafka fields and `includeHeaders` follow the [Apache Spark Kafka integration guide](https://spark.apache.org/docs/latest/streaming/structured-streaming-kafka-integration.html).
- Insert-only Delta merge in `foreachBatch` follows [Delta Lake streaming writes](https://docs.delta.io/delta-update/), which requires idempotent merge logic when a stream restarts.
- The notebook import path follows [Databricks Python module guidance](https://docs.databricks.com/aws/en/files/workspace-modules); Git folders add the repository root to Python's path in supported runtimes, while the notebook bootstraps the root for this nested `src` import.
