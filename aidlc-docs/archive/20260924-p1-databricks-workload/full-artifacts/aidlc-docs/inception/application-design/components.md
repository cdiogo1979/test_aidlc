# P1 Application Components

## P1 Daily Job

- **Purpose**: Schedule and orchestrate the daily incremental P1 workload.
- **Responsibilities**: Pass the selected environment to notebook tasks; run bronze first; run silver only after bronze succeeds; expose task outcomes through Databricks Jobs.
- **Interface**: Databricks Declarative Automation Bundle under `jobs/P1/`, with an `environment` task parameter such as `prod`.

## Bronze Ingestion Notebook

- **Purpose**: Read new records from the configured Kafka topic and retain them in bronze.
- **Responsibilities**: Load environment configuration; obtain the Kafka credential from the configured Databricks secret scope/key; read incremental Kafka records; write source payload and Kafka metadata to the bronze Delta table.
- **Interface**: Receives the environment name from the job and writes `test_prod.p1_test_kfk_brz`.

## Silver Transformation Notebook

- **Purpose**: Produce queryable current-state data from bronze events.
- **Responsibilities**: Load environment configuration; read bronze records; parse and expand valid JSON; merge the latest valid record per `event_key` into silver; write malformed records to quarantine.
- **Interface**: Receives the environment name from the job; reads `test_prod.p1_test_kfk_brz`; writes `test_prod.p1_test` and the quarantine destination.

## Environment Configuration

- **Purpose**: Supply deployment-specific, non-secret connection and storage settings.
- **Responsibilities**: Define Kafka hosts/topic, database, data path, and Kafka secret scope/key references. Keep actual credentials in Databricks Secrets.
- **Interface**: Each notebook independently loads `configs/{environment}.yaml`. The production file is `configs/prod.yaml`.

## Databricks Secret Store

- **Purpose**: Provide Kafka credential material to the bronze task at runtime.
- **Responsibilities**: Resolve the configured secret scope and key (`my-secret`) without exposing the secret value through configuration or job parameters.
- **Interface**: Databricks Secrets lookup from the bronze notebook.

## Delta Tables

- **Purpose**: Persist the workload's raw, curated, and rejected data.
- **Responsibilities**: Bronze retains source records and Kafka metadata; silver exposes expanded current-state data; quarantine retains malformed records and diagnostic metadata.
- **Interface**: Bronze, silver, and quarantine Delta tables under the configured database and storage environment.
