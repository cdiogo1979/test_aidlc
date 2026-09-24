# U2 Silver Processing and Quarantine — Code Summary

## Artifacts

- **Notebook**: `notebooks/P1/silver/silver_processing.py`
- **Shared configuration library**: `src/common.py` (`load_environment_config`, `required_text`, and `quote_qualified_identifier`).
- **Entry point**: `run_silver_processing()`; the Databricks task supplies the `environment` widget, which defaults to `prod` for interactive use.
- **Configuration**: Loads `configs/{environment}.yaml` through `src.common`. `P1_PROJECT_ROOT` may identify the deployed project root when needed.
- **Source**: Bronze Delta table `<database>.p1_test_kfk_brz`, currently `test_prod.p1_test_kfk_brz`, with Delta Change Data Feed enabled by U1.
- **Outputs**: Silver `<database>.p1_test` and quarantine `<database>.p1_test_kfk_quarantine`.

## Notebook layout

The notebook follows the project’s six ordered Databricks cells: Information, Imports, Widgets, Parameters, Additional Functions, and Main Execution. All generated functions include Google-style docstrings.

## Input and output contracts

The notebook reads CDF records from bronze and expects insert changes because U1’s bronze contract is append-only. Each source record retains its Kafka identity `(topic, partition, offset)` and source timestamp.

Silver contains at most one current row per valid `event_key`. It stores the nonblank string key, all other JSON object properties in an `attributes VARIANT` object, and the source topic, partition, offset, and timestamp. Nested JSON values are preserved. Quarantine stores the original binary payload, Kafka metadata, ingestion timestamp, and a safe parse or validation diagnostic for invalid JSON, non-object roots, and invalid keys.

## Incremental processing and recovery

- The notebook uses Delta Change Data Feed through Structured Streaming with `AvailableNow`. It enables the Delta `delta.enableVariant` table property for silver and validates that an existing silver schema has an `attributes VARIANT` column. Empty JSON objects produce an empty `VARIANT` attributes object.
- The first stream start processes the current bronze snapshot as inserts. Later runs resume from the stable checkpoint `{data_path}/checkpoints/P1/silver_processing`.
- U1 enables CDF on new and existing bronze tables. The bronze CDF and table history must be retained for U2’s recovery window. If required history is unavailable, the task fails; recovery requires a deliberate full refresh/rebuild and checkpoint reset.
- Unexpected CDF update or delete records fail the task because U1 is defined as insert-only.
- Silver keeps the newest event by source timestamp, then partition and offset. Replay is safe through ordered silver upserts and quarantine source-identity deduplication.
- Silver and quarantine are independent Delta writes, not a cross-table transaction. If one write succeeds and the other fails, the callback fails and the stream does not commit the batch; replay safely repeats completed idempotent writes.
- Logs report batch counts and table/source identifiers only; raw payloads and secrets are not logged.

## Runtime and deployment requirements

Use Databricks Runtime 15.4 LTS or later and enable Delta `VARIANT` support for the silver table. Enabling the feature can upgrade the Delta writer protocol, so older external Delta clients must be checked for compatibility. The `environment` configuration must provide a valid database and stable S3 `data_path`; the shared job identity needs bronze CDF read access, silver/quarantine write access, and checkpoint access.

## Scope

This artifact does not create U3’s Bundle job definition, add tests, or execute a notebook. Build and Test remains a later AI-DLC stage.
