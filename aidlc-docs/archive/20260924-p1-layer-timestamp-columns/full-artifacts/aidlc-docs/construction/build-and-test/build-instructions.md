# Build Instructions — U4 P1 Layer Timestamp Metadata

## Prerequisites

- **Local build tool**: Python 3.9 or newer; no repository package/build manifest is defined.
- **Local dependencies**: Python standard library for the current local unit suite.
- **Databricks execution**: The existing P1 workload requires Databricks Runtime 15.4 LTS or later for its `VARIANT` functionality, plus the existing Kafka, Delta, catalog, storage, and secret configuration.
- **Environment variables**: None required for the local unit suite. Databricks deployment continues to use the existing project configuration and secret references.

## Build and Syntax Checks

Run from the project root:

```bash
python3 -c 'import ast; from pathlib import Path; files = [Path("src/delta_schema.py"), Path("tests/test_delta_schema.py"), Path("notebooks/P1/bronze/bronze_ingestion.py"), Path("notebooks/P1/silver/silver_processing.py")]; [ast.parse(path.read_text(), filename=str(path)) for path in files]; print(f"Syntax OK: {len(files)} Python files")'
```

Expected result: `Syntax OK: 4 Python files`.

There is no packaging/build manifest and no compiled application artifact. Databricks notebook execution is not part of this local build step.

## Troubleshooting

- If `python3` is missing, install a supported Python 3 interpreter and rerun the commands from the project root.
- If notebook imports fail in Databricks, verify that the deployed project root contains both `src/common.py` and `src/delta_schema.py` and that the existing `P1_PROJECT_ROOT` setting is correct when needed.
- Local syntax checks do not prove Delta DDL, CDF schema compatibility, or live timestamp behavior.
