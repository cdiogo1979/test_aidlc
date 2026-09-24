# Component Inventory

## Application Components

- **Bronze ingestion notebook** — reads Kafka and writes the source-event Delta table.
- **Silver processing notebook** — reads bronze CDF and writes current silver rows and invalid-record quarantine.

## Infrastructure Components

- **P1 Declarative Automation Bundle** — defines the daily job, shared job cluster, schedule, identity, retries, and task dependency.
- **Environment configuration** — YAML settings under `configs/`.
- **Databricks/S3/Kafka runtime** — external workspace and services, not available for verification in this environment.

## Shared Components

- **`src/common.py`** — environment config and identifier utilities shared by the notebooks.

## Test Components

- **`tests/test_aidlc_intent.py`** — automated tests for the AI-DLC compaction and waiver lifecycle utility; not P1 processing tests.

## Total Count

- **Total repository P1 components**: 5 (2 application notebooks, 1 job bundle, 1 shared library, 1 environment config file)
- **Test files relevant to P1 runtime**: 0
- **External runtime services**: Kafka, Databricks, S3
