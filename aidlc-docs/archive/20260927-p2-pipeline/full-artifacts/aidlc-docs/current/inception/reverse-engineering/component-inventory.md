# Component Inventory

## Application Components

- P1 bronze ingestion notebook — Kafka acquisition and bronze persistence.
- P1 silver processing notebook — JSON validation, current-state merge, and quarantine.
- P1 daily Databricks job — schedule and task orchestration.

## Shared Components

- Shared Python configuration and Delta schema helpers under `src/`.
- Environment configuration under `configs/`.

## Test and Delivery Components

- Python tests under `tests/`.
- Jenkins delivery pipeline under `cicd/`.
- Databricks bundle definitions under `jobs/P1/`.
