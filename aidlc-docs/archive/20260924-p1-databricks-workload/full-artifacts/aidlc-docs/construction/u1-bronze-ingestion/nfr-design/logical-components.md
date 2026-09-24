# U1 Bronze Ingestion — Logical Components

## Components

| Component | Responsibility | Logical interaction |
|---|---|---|
| P1 Databricks Job task | Runs the U1 notebook on the daily schedule and applies deployment-configured retry behavior. | Starts U1; reports task outcome and logs. U3 orders U2 after successful U1 completion. |
| U1 Bronze notebook | Loads the selected environment configuration, reads Kafka incrementally, preserves source values and metadata, and writes bronze records. | Reads from Kafka; uses the checkpoint for progress; writes the bronze Delta table. |
| Environment configuration | Supplies environment-specific Kafka host, table/storage settings, and secret reference. | Loaded by the notebook for the selected environment; contains no secret value. |
| Databricks secret store | Holds Kafka credential material under the configured secret scope/key. | The job/notebook resolves credentials through the approved secret reference; resolved secret material is not logged. |
| Kafka topic `my-topic` | Source of records and Kafka metadata. | U1 reads incrementally using configured Kafka connectivity. |
| Durable streaming checkpoint | Tracks committed incremental source progress. | Read/updated by the streaming process; retry or later execution resumes from committed progress. Its concrete URI and lifecycle are deployment decisions. |
| Bronze Delta table `test_prod.p1_test_kfk_brz` | Durable downstream handoff containing source value and required Kafka metadata. | Receives U1 writes; U2 consumes successfully persisted records. Source identity protects against duplicate logical records on replay. |
| Databricks task status and logs | Initial operational visibility. | Expose success/failure and task diagnostic context; failed source reads or writes fail visibly. |

## Interaction flow

1. The P1 job starts the U1 task using deployment-selected environment and compute settings.
2. U1 loads environment configuration and resolves Kafka credentials through Databricks Secrets.
3. U1 reads the checkpoint to continue incrementally, or starts from the earliest available offset when no checkpoint exists.
4. U1 reads records from Kafka and writes the raw values and source metadata to the bronze Delta table using `(topic, partition, offset)` as source identity.
5. Successful writes advance committed progress. A read or write failure fails the task; the job retry mechanism may restart it from the checkpoint.
6. Databricks records task status and logs. Following successful U1 completion, U3 allows the job's U2 task to consume bronze.

## Components intentionally not introduced

This unit does not add a separate queue, cache, circuit breaker, monitoring service, or notebook-level retry subsystem. Kafka is already the source transport; checkpointing and job retry provide the approved recovery pattern; task status/logs satisfy the current observability requirement.

## Deployment boundaries

This logical design does not select a Databricks Runtime, compute size, retry count/backoff, checkpoint URI, table permissions, or checkpoint retention duration. Infrastructure and deployment design provide those values while preserving the approved requirements.
