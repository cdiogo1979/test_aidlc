# U1 Bronze Ingestion — Code Generation Plan

This plan is the single source of truth for generating U1 application artifacts after user approval.

## Unit context

- **Unit**: U1 — Bronze Ingestion.
- **Project type**: Greenfield Databricks workload in the existing artifact repository.
- **Code location**: `notebooks/P1/bronze/`; environment configuration in `configs/`; code summary markdown in `aidlc-docs/construction/u1-bronze-ingestion/code/`.
- **Stories supported**: US-P1-01 (provide source events for latest-state queries) and US-P1-02 (preserve source events so U2 can isolate malformed messages). U1 supplies bronze inputs; it does not implement silver behavior.
- **Requirements**: FR-02 (Kafka source and secret reference), FR-03 (daily incremental processing), FR-04 (bronze source and metadata persistence), and FR-08 (environment configuration).
- **Dependencies**: Kafka topic `my-topic`; `configs/{environment}.yaml`; Databricks Secrets; U2 consumes the bronze Delta contract; U3 later supplies job orchestration and passes `environment`.
- **Input interface**: Databricks notebook widget/task parameter `environment`, used to load `configs/{environment}.yaml`.
- **Output contract**: Delta bronze table `test_prod.p1_test_kfk_brz`, carrying raw Kafka value, key, headers, topic, partition, offset, and source timestamp; source identity is `(topic, partition, offset)`.
- **Failure and progress contract**: Start at earliest available offsets when no checkpoint exists; subsequently resume from a stable checkpoint; fail on Kafka/read/write errors; use job-level retry; deduplicate repeated source identities.
- **Excluded from U1**: JSON parsing, quarantine, silver table, daily P1 Bundle job, and job task dependency configuration (owned by U2/U3).

## Pre-generation clarification — Kafka authentication

The approved design identifies Kafka secret key `my-secret`, but does not define the Kafka security protocol/mechanism, username source, or whether the secret value is a password or a complete JAAS configuration. These details change the Kafka source options and must be decided before generating a working notebook.

### Question 1 — Kafka authentication contract

Which authentication contract does the existing Kafka broker require?

A) SASL_SSL with PLAIN; username is a non-secret environment setting and `my-secret` contains the password.

B) SASL_SSL with SCRAM; username is a non-secret environment setting and `my-secret` contains the password. Specify SCRAM-SHA-256 or SCRAM-SHA-512 after `[Answer]:`.

X) Other — specify the security protocol, SASL mechanism (if any), username source, and whether `my-secret` contains a password or JAAS configuration after `[Answer]:`.

[Answer]: A

**Resolved contract**: Use `SASL_SSL` with `PLAIN`; read the non-secret username from environment configuration; retrieve the password from Databricks secret key `my-secret`. The actual username and secret scope are deployment-provided values and are not available in the repository. The notebook must fail with a clear configuration error if either is unset.

## Generation steps

1. **Create P1 notebook directories** — Create `notebooks/P1/bronze/`, `notebooks/P1/silver/`, and `notebooks/P1/gold/` if absent, following `AGENTS.md`. U1 code is placed only in the bronze folder.
2. **Complete environment configuration contract** — Update `configs/prod.yaml` with the approved Kafka topic (`my-topic`), `security_protocol: SASL_SSL`, `sasl_mechanism: PLAIN`, secret key (`my-secret`), secret-scope setting (`kafka.secret_scope`), and non-secret username setting (`kafka.username`). Keep actual username and secret scope deployment-provided if unavailable, represent them as unset configuration values, and validate they are populated before connecting. Keep the credential value exclusively in Databricks Secrets.
3. **Generate bronze ingestion notebook** — Create `notebooks/P1/bronze/bronze_ingestion.py`. It will:
   - Read the `environment` widget and load/validate `configs/{environment}.yaml`.
   - Resolve the configured Kafka secret through Databricks Secrets and construct source options for the user-confirmed authentication contract without logging secret material.
   - Read topic records incrementally using the configured broker and `Trigger.AvailableNow`; use earliest offsets for a first run with no checkpoint. Use the stable checkpoint path `{data_path}/checkpoints/P1/bronze_ingestion`. The deployment runtime must support AvailableNow for Kafka (Databricks Runtime 10.4 LTS or newer).
   - Preserve raw value, Kafka key, headers, topic, partition, offset, and Kafka source timestamp; do not parse/validate the payload.
   - Write to the configured bronze Delta destination, avoiding duplicate logical rows for `(topic, partition, offset)` on replay.
   - Fail visibly on configuration, Kafka, checkpoint, or Delta write errors so the job-level retry can resume committed progress.
   - Return/emit a concise run summary without exposing credential material.
4. **Document U1 code artifact** — Create `aidlc-docs/construction/u1-bronze-ingestion/code/code-summary.md` with the notebook entry point, configuration contract, output schema, checkpoint behavior, and deployment-provided values.
5. **Review implementation against approved design** — Confirm exact paths, source fields, secret safety, retry/checkpoint contract, unit boundaries, and FR-02/FR-03/FR-04/FR-08 traceability. Do not implement U2 or U3 artifacts in this unit.

## Plan status

- [x] Resolve Question 1 — Kafka authentication contract.
- [x] User approves this complete generation plan before code is created.
- [x] Step 1 — Create P1 notebook directories.
- [x] Step 2 — Complete environment configuration contract.
- [x] Step 3 — Generate bronze ingestion notebook.
- [x] Step 4 — Document U1 code artifact.
- [x] Step 5 — Review implementation against approved design.

## Implementation note

This plan does not create or run tests. Verification activities belong to the later Build and Test workflow stage. The deployment-provided workspace, runtime/compute, secret scope value, and catalog resolution remain configuration values and must not be replaced with invented credentials or environment identifiers.

## User-requested revision

- [x] Move project root discovery for config lookup, YAML loading, required config value validation, and qualified identifier validation into `src/common.py`.
- [x] Keep only notebook import-path bootstrap in `notebooks/P1/bronze/bronze_ingestion.py`; use the shared helpers for environment config access.
- [x] Update this summary and review the refactor. No tests or notebook execution are included.
