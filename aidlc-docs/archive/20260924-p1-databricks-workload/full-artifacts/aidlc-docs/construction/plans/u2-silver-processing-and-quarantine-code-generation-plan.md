# U2 Silver Processing and Quarantine — Code Generation Plan

This is the single source of truth for U2 code generation after clarification and explicit approval of this plan.

## Unit context

- **Unit**: U2 — Silver Processing and Quarantine.
- **Project type**: Greenfield Databricks workload in the existing P1 artifact repository.
- **Code location**: `notebooks/P1/silver/silver_processing.py`; code summary at `aidlc-docs/construction/u2-silver-processing-and-quarantine/code/code-summary.md`.
- **Stories implemented**: US-P1-01 (current valid event per `event_key`) and US-P1-02 (quarantine malformed messages while valid records continue).
- **Requirements**: FR-05 (JSON parsing and expansion), FR-06 (latest current row per key), FR-07 (quarantine), and FR-08 (environment configuration).
- **Dependencies**: U1 bronze Delta table `test_prod.p1_test_kfk_brz` with Delta Change Data Feed enabled; `configs/{environment}.yaml`; shared configuration helpers in `src/common.py`; U3 later supplies the P1 job and environment parameter.
- **Input interface**: Databricks widget/task parameter `environment`, defaulting to `prod`, used to load the environment configuration.
- **Output contract**: Silver table `test_prod.p1_test` with `event_key`, extensible attributes, and winning Kafka metadata; quarantine table `test_prod.p1_test_kfk_quarantine` with raw payload, source metadata, ingestion timestamp, and parse/validation error.
- **Attributes encoding**: Store `attributes` as a Delta `VARIANT` object, preserving arbitrary nested JSON values. Deployment must use Databricks Runtime 15.4 LTS or later and enable Delta variant table support. The Delta writer protocol upgrade may affect older external Delta clients.
- **Processing contract**: Consume bronze with Delta Change Data Feed through Structured Streaming and a stable checkpoint at `{data_path}/checkpoints/P1/silver_processing`, using `AvailableNow` per daily run. The first run processes the current bronze snapshot and then future changes. U1 must enable CDF on the bronze table; its append-only contract means U2 expects inserts. Invalid JSON roots and invalid keys go to quarantine; all other JSON property types are accepted. Latest event ordering uses Kafka source timestamp, then partition and offset. Silver and quarantine are idempotent by `(topic, partition, offset)`; any read/write failure fails the task.
- **Notebook structure**: Exactly six ordered cells per `AGENTS.md`: Information, Imports, Widgets, Parameters, Additional Functions, Main Execution. Use Databricks `# COMMAND ----------` cell separators.
- **Function documentation**: Every generated function has a Google-style docstring, including applicable Args, Returns, and Raises sections.
- **Excluded from U2**: Kafka access and Kafka checkpoint (U1), P1 Bundle job definition and task dependency (U3), and test artifacts/execution (Build and Test; no tests are requested in this code-generation task). U1's bronze table must enable CDF for U2 consumption.

## Resolved pre-generation clarification

Question 1 selected A: store `attributes` as a Delta `VARIANT` object. The selected format preserves arbitrary JSON values and supports nested querying. Deployment must use Databricks Runtime 15.4 LTS or later and enable Delta variant table support; enabling the feature upgrades the writer protocol and may affect older external Delta clients. See the official [Delta VARIANT support documentation](https://docs.databricks.com/aws/en/tables/features/variant) and [VARIANT type documentation](https://docs.databricks.com/aws/en/sql/language-manual/data-types/variant-type).

Clarification 2 selected `X`: consume Delta Change Data Feed from bronze. U1 will enable CDF when creating the bronze table and enable it on an existing table before ingesting further records. U2 uses a stable Structured Streaming checkpoint under the configured S3 root and `AvailableNow`. The new stream's initial snapshot processes the current bronze table as inserts; subsequent runs consume changes after the checkpoint. Source CDF retention must cover the stream's recovery window; if required versions expire, the task must fail rather than silently skip data and require a full refresh/recovery procedure.

## Generation steps

1. **Confirm notebook target and structure** — Create `notebooks/P1/silver/` if absent and create `silver_processing.py` with six separate, ordered notebook cells: Information, Imports, Widgets, Parameters, Additional Functions, and Main Execution.
2. **Enable bronze Change Data Feed** — Update U1's bronze table creation to enable `delta.enableChangeDataFeed`; enable CDF on an existing bronze table before subsequent ingestion. Update the U1 code summary and source contract documentation.
3. **Set up imports and shared configuration** — Use `src/common.py` for project-root/config loading, required text settings, and qualified identifier validation. Keep any import-path bootstrap small and documented. Do not duplicate general configuration retrieval helpers.
4. **Define widgets and runtime parameters** — Create/read the `environment` widget; load its YAML config, validate the database and table identifiers, and prepare input/output Delta table names plus the stable CDF checkpoint path without hardcoding environment-specific values.
5. **Implement table contracts and source parsing** — Ensure or validate silver and quarantine tables with an `attributes VARIANT` column for silver. Read the bronze CDF with Structured Streaming and `AvailableNow`; preserve default initial snapshot behavior. Decode inserted bronze `value` bytes as JSON; require an object and a nonblank string `event_key`; preserve all other top-level properties and nested values in a VARIANT object. Require the supported runtime/table feature and fail clearly if unavailable.
6. **Implement CDF batch classification and writes** — Process only supported `insert` change records; fail on unexpected change types. Separate valid and invalid records so malformed records do not block valid records. Deduplicate by `(topic, partition, offset)`. Upsert quarantine with raw payload, topic, partition, offset, source timestamp, ingestion timestamp, and diagnostic. Upsert silver by `event_key`, replacing only with a later-ranked source timestamp/partition/offset. A CDF batch checkpoint advances only after both writes complete. Fail the task on read or either output write error; do not claim cross-table atomicity.
7. **Implement safe operational output** — Report concise completion status and non-sensitive counts/source identifiers. Never log raw payloads, secret values, or complete sensitive diagnostics.
8. **Document U2 code artifact** — Create `aidlc-docs/construction/u2-silver-processing-and-quarantine/code/code-summary.md` describing notebook cells, input/output contracts, CDF/checkpoint behavior, configuration, ordering/idempotency, failure/retention behavior, and runtime/table-feature requirements.
9. **Review implementation against approved design** — Confirm exact paths, six-cell order, Google-style docstrings, interfaces, CDF insert handling, checkpoint stability, source identity behavior, current-row ordering, malformed-record isolation, log safety, and FR-05/FR-06/FR-07/FR-08 traceability. Do not generate the P1 Bundle job definition or tests.

## Plan status

- [x] Resolve the pre-generation clarification about arbitrary JSON attributes encoding and runtime/table compatibility — selected Delta `VARIANT`.
- [x] User approved the generation plan, selected Delta `VARIANT` for attributes, and resolved incremental processing with bronze Delta CDF.
- [x] Update the plan and supporting U1/U2 design artifacts for bronze CDF and the U2 stream checkpoint.
- [x] Step 1 — Create the U2 silver notebook with the required cell structure.
- [x] Step 2 — Enable CDF on the U1 bronze table and update U1 documentation.
- [x] Step 3 — Reuse the shared configuration helpers.
- [x] Step 4 — Define widgets and parameters.
- [x] Step 5 — Implement table contracts and JSON parsing/validation.
- [x] Step 6 — Implement CDF batch classification and idempotent writes.
- [x] Step 7 — Implement safe operational output.
- [x] Step 8 — Create the U2 code summary.
- [x] Step 9 — Review implementation against approved design.

## Implementation note

No tests will be added or run as part of this plan. Verification belongs to the later Build and Test stage. Runtime version, catalog/schema resolution, physical table locations, and compute policy remain deployment-provided values. Keep the CDF streaming checkpoint stable across daily runs and do not disable failure-on-data-loss behavior; if retained CDF history is unavailable, fail visibly and require a deliberate full refresh.
