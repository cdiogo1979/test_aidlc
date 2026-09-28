# Code Structure

## Build and Deployment

- Python project settings: `pyproject.toml` and `requirements-dev.txt`.
- CI/CD: `cicd/Jenkinsfile`.
- Databricks bundles: `jobs/<project>/databricks.yml` with included `resources/*.yml`.

## Relevant Files

- `notebooks/P1/bronze/bronze_ingestion.py` — Kafka to bronze Delta ingestion.
- `notebooks/P1/silver/silver_processing.py` — bronze CDF processing, silver output, quarantine.
- `jobs/P1/databricks.yml` — P1 bundle variables, sync paths, target.
- `jobs/P1/resources/p1-daily-pipeline.yml` — scheduled bronze then silver job.
- `configs/prod.yaml` — production environment configuration, including Kafka topic.
- `src/common.py`, `src/delta_schema.py` — shared configuration and Delta schema helpers.
- `tests/` — unit tests for helpers and workflow tooling.
