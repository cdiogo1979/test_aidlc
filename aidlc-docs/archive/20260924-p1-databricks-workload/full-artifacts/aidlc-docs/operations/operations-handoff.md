# P1 Operations Handoff

## Stage status

Operations was entered at the user's request. The project's AI-DLC Operations instructions remain a placeholder and define no executable deployment, monitoring, incident-response, or maintenance procedure. This document records the current handoff only; it is not deployment approval.

## P1 release state

- The P1 Declarative Automation Bundle is in `jobs/P1/` with a `prod` target.
- Required production values for schedule/timezone, compute policy/runtime, run-as identity, and retries are intentionally unset.
- Bundle YAML and notebook paths passed static checks. `databricks bundle validate` has not run because the Databricks CLI, authentication, and required values are unavailable.
- Local Python syntax checks passed for both P1 notebooks and `src/common.py`; the current 16-test suite covers the AI-DLC compaction utility, not P1 data processing.
- The user explicitly accepted the absence of a Databricks environment as a P1 verification limitation. Lifecycle status is `VERIFICATION_WAIVED`, not `VERIFICATION_COMPLETE`: Kafka-to-Delta runtime behavior and performance remain unverified. The waiver records accepted risk and does not establish production readiness or authorize deployment.
- No job has been deployed and no notebook or production data has been run or changed.

## Outstanding operational inputs

Before a production release can be planned or executed, the deployment owner must supply values through the approved, non-secret deployment mechanism and confirm the workspace's existing access controls. The configured run-as identity must have the required Kafka secret, Kafka topic, storage/checkpoint, and Delta table permissions. Secret values must remain in Databricks Secrets.

The project has no defined monitoring, alerting, incident response, rollback, maintenance, or on-call procedures beyond using Databricks job/task status and logs. Those operational procedures need owner decisions before production support is established. No monitoring targets or performance thresholds are invented here.

## Verification and lifecycle boundary

The Build and Test stage is marked complete by user-approved deferral, and the user has accepted the P1 runtime verification limitation because no Databricks environment is available. P1 runtime verification remains outstanding. The lifecycle is `VERIFICATION_WAIVED`. Compaction requires a manifest that explicitly records this waiver and separate user approval to close the intent.
