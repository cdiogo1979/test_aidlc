# P1 Requirements

## Intent analysis

- **User request**: Build the first Databricks subproject to ingest events from Kafka into bronze and consolidate them by key in silver.
- **Request type**: New workload / new project.
- **Scope estimate**: One Databricks job with bronze ingestion, silver transformation, environment configuration, and malformed-message handling.
- **Complexity estimate**: Moderate. The workload is focused, but incremental Kafka processing, checkpointing, and latest-event semantics need careful handling.
- **Project type**: Greenfield workload in an existing Databricks artifact repository.

## Functional requirements

| ID | Requirement |
|---|---|
| FR-01 | Create subproject `P1` under `notebooks/P1/` and `jobs/P1/`; the notebook project contains `bronze/`, `silver/`, and `gold/` directories. Gold output is out of scope for this workload. |
| FR-02 | Read Kafka topic `my-topic` using the configured Kafka hosts (`kafka.hosts`) and Databricks secret key `my-secret`. Secret values must not be stored in repository files. |
| FR-03 | Run the ingestion job once daily and process Kafka data incrementally, retaining progress across successful runs. |
| FR-04 | Write each source event to bronze table `test_prod.p1_test_kfk_brz`, preserving the source payload and adding the Kafka metadata needed for traceability and incremental processing. |
| FR-05 | Parse the JSON message payload and expose its non-key fields in the silver table `test_prod.p1_test`. |
| FR-06 | Maintain one current row per `event_key` in silver, applying the latest event for each key. |
| FR-07 | Quarantine malformed messages so valid events can continue through processing. |
| FR-08 | Use the environment values in `configs/prod.yaml`: database `test_prod` and data path `s3://test_prod`. |

## Non-functional requirements

- **Security**: Kafka credentials are retrieved from a Databricks secret reference. No secret values are committed to source or configuration files. The optional Security Baseline extension was declined; this does not remove the requirement to protect credentials.
- **Reliability**: Incremental processing must retain its checkpoint/progress so a daily run can continue from previously processed Kafka data. Retry details are captured below as an assumption.
- **Data quality**: Invalid JSON or otherwise malformed messages are isolated in quarantine and do not silently become valid silver records.
- **Performance and scale**: No daily event volume or processing-window target was provided. No numeric throughput or latency SLA is set by these requirements.
- **Maintainability**: Keep environment-specific values in `configs/` and workload notebooks/jobs under the matching `P1` subproject directories.

## Data flow

1. The daily job reads new records from Kafka topic `my-topic`.
2. Bronze retains the source payload with Kafka metadata and the current ingestion context.
3. Malformed records are written to a quarantine destination with error details.
4. Valid JSON records are parsed and their non-key fields are preserved in silver; silver is upserted by `event_key` so each key reflects its latest event.

## Confirmed decisions

- Subproject name: `P1`.
- Kafka topic: `my-topic`.
- Kafka host setting: `kafka.hosts`.
- Configured production Kafka host: `test.com:9995` in `configs/prod.yaml`.
- Databricks secret key name: `my-secret`.
- Schedule: once daily.
- Ingestion mode: incremental.
- Message format: JSON.
- Event consolidation key: `event_key`.
- Latest event wins for a key.
- Bronze table: `test_prod.p1_test_kfk_brz`.
- Silver table: `test_prod.p1_test`.
- Malformed messages are quarantined.
- Gold output is not part of this workload.
- Environment values: `database: test_prod`, `data_path: s3://test_prod`.
- Security Baseline, Property-Based Testing, and Resiliency Baseline extensions: disabled by user choice.

## Assumptions for review

These assumptions fill details the user marked `TBD` or did not specify. They are provisional until the requirements are approved.

1. Use `configs/prod.yaml` key `kafka.hosts` (`test.com:9995`) for the production Kafka bootstrap host. `my-secret` is the Databricks secret key name, with its secret scope supplied by deployment configuration.
2. Use a Databricks job with a daily scheduled run and a persistent Structured Streaming checkpoint under `s3://test_prod` to track Kafka offsets. A retry resumes from the last committed offsets.
3. Use the Kafka record timestamp to determine which event is latest for a given `event_key`; use Kafka partition and offset as deterministic tie-breakers. The JSON schema must contain `event_key`.
4. Store malformed records in a Delta quarantine table named `test_prod.p1_test_kfk_quarantine`, including the raw payload, Kafka topic/partition/offset/timestamp, ingestion timestamp, and parse error.
5. No fixed daily volume or processing-window SLA is required yet. Record workload metrics so targets can be added when expected volumes are known.
6. The bronze and silver tables are Delta tables. Bronze preserves each source payload unchanged, alongside metadata columns.

## Acceptance criteria

- A daily job definition exists under `jobs/P1/` and refers to the P1 notebooks and configuration.
- The job reads only Kafka records not already committed in its persistent checkpoint during normal subsequent runs.
- Every consumed Kafka record is traceable in bronze or quarantine using its Kafka metadata.
- Valid JSON events with `event_key` have their other fields exposed in silver and are upserted so that silver contains the latest event per key according to the approved ordering rule.
- Malformed records are captured in quarantine with enough source and error information to diagnose them.
- The configured database and storage location come from the environment configuration, and secret material is not hard-coded.
- No gold table or gold transformation is produced in this scope.

## Open items deferred

- Databricks secret scope is an environment/deployment value not present in the repository yet.
- The complete JSON payload schema and exact field names were not provided. Code Generation selected an extensible Delta `VARIANT` attributes object for the non-key JSON fields; sample messages or a schema can inform future typed silver columns.
- Daily event volume and processing-window target are unknown; no numeric SLA is asserted.
