# Build Instructions

## Prerequisites
- Python 3.9 or later.
- Development dependencies listed in `requirements-dev.txt`.
- Black, Ruff, and Hypothesis; the configured package index used in this run did not contain the repository-pinned Black/Hypothesis versions. See the summary for actual versions used.
- Databricks CLI and a configured Databricks workspace are needed for bundle validation/deployment; neither was available in this run.

## Build and quality checks

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m black notebooks/P2/bronze/bronze_ingestion.py notebooks/P2/silver/silver_processing.py tests/test_p2_pipeline_properties.py
python3 -m black --check notebooks/P2/bronze/bronze_ingestion.py notebooks/P2/silver/silver_processing.py tests/test_p2_pipeline_properties.py
python3 -m ruff check notebooks/P2/bronze/bronze_ingestion.py notebooks/P2/silver/silver_processing.py tests/test_p2_pipeline_properties.py
python3 -m unittest discover -s tests
```

Validate the production config and P2 bundle YAML with a YAML parser. If the Databricks CLI is installed and authenticated, run `databricks bundle validate -t prod` from `jobs/P2/`.

## Scope
No application binary is produced. The deliverables are Python notebooks, YAML configuration, and a Databricks bundle. This stage does not deploy or execute the job.
