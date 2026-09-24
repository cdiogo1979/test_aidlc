# P1 Units of Work

## Decomposition Summary

P1 is one Databricks workload deployed and owned by one P1 team. It has one daily job with sequential bronze and silver notebook tasks. The three units below are development and planning boundaries; they are not independent services or separately deployed jobs.

## Unit Definitions

### U1 — Bronze Ingestion

- **Purpose**: Ingest new events from Kafka and persist source records for downstream processing.
- **Responsibilities**: Read `my-topic` using the selected environment's Kafka hosts and secret reference; preserve each payload and Kafka metadata in `test_prod.p1_test_kfk_brz`; support the approved incremental/checkpoint contract.
- **Code location**: `notebooks/P1/bronze/`.
- **Inputs**: `configs/{environment}.yaml`, Kafka topic records, Databricks secret scope/key reference.
- **Outputs**: Bronze Delta table `test_prod.p1_test_kfk_brz`.
- **Requirements**: FR-02, FR-03, FR-04.
- **Stories supported**: US-P1-01, US-P1-02.

### U2 — Silver Processing and Quarantine

- **Purpose**: Produce queryable current-state event data and isolate malformed messages.
- **Responsibilities**: Read the bronze Delta table; parse and expand valid JSON; maintain the latest current row per `event_key`; write malformed records and diagnostic metadata to quarantine.
- **Code location**: `notebooks/P1/silver/`.
- **Inputs**: Bronze Delta table `test_prod.p1_test_kfk_brz`, `configs/{environment}.yaml`.
- **Outputs**: Silver Delta table `test_prod.p1_test` and quarantine Delta table `test_prod.p1_test_kfk_quarantine`.
- **Requirements**: FR-05, FR-06, FR-07.
- **Stories implemented**: US-P1-01, US-P1-02.

### U3 — P1 Integration

- **Purpose**: Assemble, configure, and validate the shared P1 deployment.
- **Responsibilities**: Define the once-daily Databricks job; pass the environment parameter; reference the bronze and silver notebooks; make silver depend on bronze success; maintain environment configuration and cross-unit validation.
- **Code location**: Databricks Declarative Automation Bundle in `jobs/P1/`; environment YAML in `configs/`.
- **Inputs**: U1 and U2 notebook paths and interfaces; deployment environment configuration.
- **Outputs**: One daily job definition and integrated workload validation.
- **Requirements**: FR-01, FR-03, FR-08.
- **Stories supported**: US-P1-01, US-P1-02.

## Unit Ownership and Deployment

- One P1 team owns all three units.
- All units are developed and released together as one P1 workload.
- There are no independent schedules, deployment boundaries, or scaling policies.
- Runtime order is U1 (bronze) before U2 (silver), orchestrated by U3.

## Greenfield Code Organization Strategy

Follow the repository's Databricks-specific structure:

```text
configs/prod.yaml
notebooks/P1/bronze/<bronze-ingestion>.py
notebooks/P1/silver/<silver-processing>.py
notebooks/P1/gold/                 # Required folder; no gold output in this scope
jobs/P1/<p1-daily-job>.json
```

The notebooks are Python Databricks notebook source files. Environment-specific Kafka hosts, database, storage path, and secret scope/key references belong in `configs/`; secret values remain in Databricks Secrets. Keep application code in the project folders and generated AI-DLC documentation under `aidlc-docs/`.

## Shared Contracts

- **Configuration contract**: Each notebook receives an environment name from the job and independently loads `configs/{environment}.yaml`.
- **Bronze table contract**: U1 writes the source payload and Kafka metadata to bronze; U2 consumes the persisted Delta table.
- **Job contract**: U3 passes the same environment name to both notebook tasks and starts U2 only after U1 succeeds.
- **Current-state contract**: U2 exposes one latest valid event per `event_key` in silver, following the ordering assumptions in the approved requirements.
- **Quarantine contract**: U2 retains malformed payloads, source metadata, and parse diagnostics outside silver.
