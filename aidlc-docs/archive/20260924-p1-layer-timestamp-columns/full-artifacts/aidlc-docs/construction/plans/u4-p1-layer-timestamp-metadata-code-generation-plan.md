# U4 Code Generation Plan — P1 Layer Timestamp Metadata

## Plan Status

Approved for Part 2 generation. This document is the single source of truth for the implementation sequence.

## Unit Context

- **Unit**: U4 — P1 Layer Timestamp Metadata.
- **Project type and root**: Brownfield Databricks workload at `/Users/carlosdiogo/code_repo/test_aidlc`.
- **Requirements**: FR-01 through FR-09 in `aidlc-docs/inception/requirements/requirements.md`.
- **User stories**: None in this intent; User Stories was skipped in the approved execution plan. The work supports existing P1 downstream data contracts.
- **Dependencies**: Extend U1 bronze and U2 silver modules in that order. U3 job and orchestration are unchanged.
- **Interfaces**: Continue using the bronze Delta/CDF contract and current table identities. Add only `bronze_ingestion_timestamp TIMESTAMP` and `silver_processing_timestamp TIMESTAMP`.
- **Entities**: Bronze source record keyed by `(topic, partition, offset)`; silver current-state event keyed by `event_key`.
- **Generation constraints**: Preserve the six-cell Databricks notebook structure; every generated function has a Google-style docstring; preserve existing code in place; no secrets/config/job changes.

## Exact Target Paths

### Application code

- Modify `notebooks/P1/bronze/bronze_ingestion.py`.
- Modify `notebooks/P1/silver/silver_processing.py`.
- Create `src/delta_schema.py` with one reusable nullable timestamp-column migration/validation helper, used by both notebooks.

### Tests

- Create `tests/test_delta_schema.py` for the shared schema helper using a small fake Spark/table schema interface; do not require a live Databricks workspace.
- Tests are authored during Code Generation and executed only in the approved Build and Test stage.

### Documentation

- Create `aidlc-docs/construction/u4-p1-layer-timestamp-metadata/code/code-summary.md` after code generation; Markdown only.
- No Bundle/job or configuration artifact is changed.

## Numbered Generation Steps

1. **Add shared additive schema helper** — Create `src/delta_schema.py` with a Google-style documented function that checks for a field, adds a nullable `TIMESTAMP` column when absent, validates the resulting type, and raises a clear error on inspection/migration/type failure. It must accept the existing quoted table identifier and known constant column names; add no external dependency.
2. **Update bronze notebook** — Add the nullable field to `BRONZE_COLUMNS_SQL`; set Spark session timezone to UTC before processing; invoke the shared schema helper after table creation and before streaming writes; project a Spark current-timestamp expression as `bronze_ingestion_timestamp`; preserve deduplication and insert-only merge semantics; leave CDF property and checkpoint unchanged.
3. **Update silver notebook** — Add the nullable field to silver table creation; invoke the shared schema helper before CDF processing; set Spark session timezone to UTC before timestamp expressions; populate `silver_processing_timestamp` in accepted silver candidates; preserve explicit source projection, latest-event ordering, conditional merge predicate, and quarantine schema/behavior.
4. **Add focused local tests** — Create `tests/test_delta_schema.py` covering absent-column migration, existing TIMESTAMP no-op, incompatible-type failure, and migration/inspection failure using fakes. Do not claim this proves Databricks Delta/CDF runtime behavior.
5. **Review cross-layer contract and notebook conventions** — Confirm both notebooks retain the order Information, Imports, Widgets, Parameters, Additional Functions, Main Execution; all new functions have Google-style docstrings; existing source timestamps, checkpoints, CDF, latest-event ordering, quarantine, and job files remain unchanged.
6. **Write code summary and update workflow state** — Document modified/created files, behavior, tests authored (not yet run), and Databricks verification limits in `code-summary.md`; mark plan steps complete and prepare Build and Test.

## Story and Requirement Traceability

No new user story is assigned. All functional requirements map to U4:

| Requirement | Generation step(s) |
|---|---|
| FR-01 preserve `source_timestamp` | 2, 3, 5 |
| FR-02 bronze first-insert timestamp | 1, 2, 4 |
| FR-03 silver accepted insert/update timestamp | 1, 3, 4 |
| FR-04 UTC instants | 2, 3, 4 |
| FR-05 independent layer timestamps | 2, 3, 5 |
| FR-06 duplicate/no-op replay stability | 2, 3, 4, 5 |
| FR-07 additive existing-table migration | 1, 2, 3, 4 |
| FR-08 historical values remain NULL | 1, 4, 5 |
| FR-09 preserve existing pipeline behavior | 2, 3, 5 |

## Approval Gate

Part 2 generation must not begin until the user explicitly approves this complete plan. After approval, execute Steps 1–6 in order and update each checkbox as completed.

## Execution Checklist

- [x] Step 1 — Add shared additive schema helper.
- [x] Step 2 — Update bronze notebook.
- [x] Step 3 — Update silver notebook.
- [x] Step 4 — Add focused local tests.
- [x] Step 5 — Review cross-layer contract and notebook conventions.
- [x] Step 6 — Write code summary and update workflow state.
