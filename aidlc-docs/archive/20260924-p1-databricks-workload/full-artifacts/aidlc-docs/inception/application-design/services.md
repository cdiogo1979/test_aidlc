# P1 Services and Orchestration

## P1 Daily Databricks Job

- **Purpose**: Run the P1 ingestion and transformation once per day.
- **Configuration**: Databricks Declarative Automation Bundle under `jobs/P1/`; passes only the environment name (`prod`) as a notebook parameter.
- **Tasks**:
  1. Run the bronze ingestion notebook.
  2. Run the silver transformation notebook after the bronze task succeeds.
- **Failure behavior**: A failed bronze task prevents the silver task from starting. Databricks job retry policy and notification settings are finalized during Infrastructure Design.

## Notebook Configuration Pattern

Each notebook independently loads `configs/{environment}.yaml` using the environment parameter passed by the job. This follows the selected design preference and keeps the YAML as the source of environment-specific non-secret settings.

The production YAML will hold the Kafka secret scope name and the secret key name `my-secret`; the credential value remains in Databricks Secrets and is read only at runtime.

## Data Orchestration

The bronze notebook consumes Kafka and writes the bronze Delta table. The silver notebook reads the persisted bronze table, expands valid JSON, merges the current row for each `event_key`, and sends malformed records to the quarantine destination. The Delta bronze table is the component boundary; notebooks do not pass event records directly through in-memory calls.
