# Intent Summary: P1 Databricks Workload

## Intent
P1 Databricks Workload (`20260924-p1-databricks-workload`)

## Objective
Build the P1 Kafka-to-Delta bronze and silver workload with quarantine handling and a scheduled Databricks job.

## Date
2026-09-24

## Scope
P1 bronze ingestion, silver processing and quarantine, shared configuration helpers, the daily Databricks Bundle job, and AI-DLC lifecycle/compaction workflow updates. Gold processing and production deployment are excluded.

## Units / workstreams
P1 bronze Kafka ingestion, P1 silver processing and quarantine, P1 daily Databricks job integration, AI-DLC intent compaction and verification-waiver workflow

## Major requirements
- Consume Kafka topic my-topic incrementally and preserve source records and Kafka metadata in bronze Delta.
- Use bronze Change Data Feed to process new records incrementally in silver.
- Keep the latest valid event per event_key in silver and quarantine malformed or invalid messages.
- Orchestrate the bronze and silver notebooks in a daily Databricks job with shared environment configuration.

## Architecture and design decisions
- Use Structured Streaming AvailableNow and persistent bronze and silver checkpoints for scheduled incremental processing.
- Use an insert-only bronze merge keyed by topic, partition, and offset; enable Delta Change Data Feed for silver.
- Use source timestamp, then partition and offset to order events; preserve non-key JSON fields as VARIANT attributes in silver.
- Run both ordered notebook tasks on a shared policy-backed job cluster and pass one environment parameter to both.

## Implementation decisions
- Keep shared environment configuration helpers in src/common.py and environment values in configs/.
- Keep P1 notebooks under notebooks/P1/{bronze,silver,gold}/ and the authoritative job Bundle under jobs/P1/.
- Keep deployment-owned production values unset and Kafka credentials in Databricks Secrets.

## Deviations
- P1 runtime integration and performance verification were waived by explicit user acceptance because no Databricks environment is available; the behavior remains unverified.
- The Databricks CLI was unavailable and required Bundle validation/authentication checks were not run.
- The Operations workflow remains a placeholder; monitoring, incident response, rollback, maintenance, and on-call procedures are not defined.

## Verification
The user accepted the verification limitation because no Databricks environment is available. P1 Spark/Kafka/Delta runtime integration, performance, authenticated Bundle validation, and production permission checks were not run. Python syntax checks and static Bundle checks passed; the 16 passing automated tests cover AI-DLC lifecycle tooling only, not P1 data processing. No deployment or production data operation occurred.

## Canonical documents updated
- aidlc-docs/knowledge/p1-databricks-workload.md
- aidlc-docs/knowledge/aidlc-intent-lifecycle.md

## Superseded decisions
- None recorded

## Archived artifacts
- aidlc-docs/archive/20260924-p1-databricks-workload/full-artifacts/aidlc-docs/compaction/20260924-p1-databricks-workload/manifest.json
- aidlc-docs/archive/20260924-p1-databricks-workload/full-artifacts/aidlc-docs/inception
- aidlc-docs/archive/20260924-p1-databricks-workload/full-artifacts/aidlc-docs/construction
- aidlc-docs/archive/20260924-p1-databricks-workload/full-artifacts/aidlc-docs/operations/operations-handoff.md
- aidlc-docs/archive/20260924-p1-databricks-workload/full-artifacts/AGENTS.md
- aidlc-docs/archive/20260924-p1-databricks-workload/full-artifacts/.agents/skills/aidlc-workflows
- aidlc-docs/archive/20260924-p1-databricks-workload/full-artifacts/.gitignore
- aidlc-docs/archive/20260924-p1-databricks-workload/full-artifacts/configs/prod.yaml
- aidlc-docs/archive/20260924-p1-databricks-workload/full-artifacts/jobs/P1
- aidlc-docs/archive/20260924-p1-databricks-workload/full-artifacts/notebooks/P1
- aidlc-docs/archive/20260924-p1-databricks-workload/full-artifacts/scripts/aidlc_intent.py
- aidlc-docs/archive/20260924-p1-databricks-workload/full-artifacts/src
- aidlc-docs/archive/20260924-p1-databricks-workload/full-artifacts/tests/test_aidlc_intent.py

## Archive
- Full artifacts and audit snapshot: `aidlc-docs/archive/20260924-p1-databricks-workload/full-artifacts/`
