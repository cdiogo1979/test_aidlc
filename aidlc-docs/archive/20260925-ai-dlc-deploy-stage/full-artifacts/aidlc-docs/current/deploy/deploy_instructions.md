# Deploy Instructions: P1 Streaming Lookback

## Handoff Status

These instructions describe the required deployment and optional replay sequence. No deployment, job run, checkpoint operation, or environment change has been performed.

## Required Inputs and Blockers

Resolve these before proceeding:

- Explicit approval to deploy the P1 Bundle to its configured `prod` target.
- Job owner decision on the schedule: the resource declares `pause_status: UNPAUSED`, so deployment creates or updates an active schedule.
- Approved workspace, deployment identity, Databricks CLI, and permissions to validate/deploy the Bundle and inspect the job.
- Values for all required Bundle variables in the target workspace: schedule expression/timezone, cluster policy, Runtime version, run-as service principal, retry count, and retry interval. Do not put credentials in repository files.
- A decision on whether a non-production integration environment is available. None is currently identified; positive lookback use in production requires separate explicit operational approval.
- An approved validation/run window and an owner for reviewing task logs. No rollback procedure for deleted checkpoint state is defined.

## Ordered Steps

### 1. Confirm deployment and schedule approval — Manual

- **Target:** Databricks workspace selected for the `prod` Bundle target; P1 Daily Pipeline job.
- **Prerequisites:** Resolve the inputs/blockers above, including the production schedule decision and required Bundle variables.
- **Action:** Confirm the change window and the authorized deployment operator. If an active schedule is not approved, stop and update the deployment approach through the normal review process before proceeding.
- **Validation:** Record the approved workspace/target, operator, schedule decision, and change window in the release record.
- **Failure handling:** Stop if target, permissions, required variables, or schedule authorization are unknown. Do not infer or substitute environment values.

### 2. Validate the Bundle — Manual

- **Target:** `jobs/P1/`, target `prod`.
- **Prerequisites:** Databricks CLI installed and authenticated to the approved workspace; required target variables available.
- **Execution:** From `jobs/P1/`, run:

  ```bash
  databricks bundle validate -t prod
  ```

- **Validation:** Require a successful validation of the job resource, notebook paths, target variables, and `environment`, `bronze_lookback_days`, and `silver_lookback_days` parameters before deployment.
- **Failure handling:** Stop on any validation error. Resolve it in source/configuration, review the change, then rerun validation. Do not deploy an invalid Bundle.

### 3. Deploy the P1 Bundle — Manual

- **Target:** Approved workspace, `prod` target; P1 Daily Pipeline job.
- **Prerequisites:** Step 2 passes and production deployment plus schedule behavior is approved.
- **Execution:** From `jobs/P1/`, run:

  ```bash
  databricks bundle deploy -t prod
  ```

- **Validation:** Inspect the resulting job definition. Confirm both lookback parameters default to `0`, the existing `environment` parameter remains, bronze precedes silver, notebook paths resolve, and the approved schedule state is in effect.
- **Failure handling:** Stop subsequent manual runs if deployment fails or job settings differ from the approved definition. Use the workspace's standard job-change recovery process; no code or checkpoint rollback has been validated by this change.

### 4. Validate default continuation — Manual, only when separately authorized

- **Target:** P1 Daily Pipeline in the approved workspace.
- **Prerequisites:** Step 3 succeeded; the job owner approved a run; defaults `bronze_lookback_days=0` and `silver_lookback_days=0` are confirmed.
- **Execution:** Use the approved schedule or manually run the job with both parameters at `0`.
- **Validation:** Confirm both tasks complete in bronze-before-silver order and emit their structured summaries. A successful run confirms only the observed environment/run, not all historical replay behavior.
- **Failure handling:** Stop further manual runs on task failure and follow the existing incident/job support process. Do not change either value to a positive number as an ad hoc retry.

### 5. Perform a lookback replay — Manual, separate operational approval required

- **Target:** P1 Daily Pipeline; bronze and/or silver task checkpoint under the configured `data_path`.
- **Prerequisites:** A replay window, source retention, checkpoint target, workspace, operator, and run window are explicitly approved. Prefer a dedicated non-production environment with isolated source/output tables and checkpoints. Production replay is blocked until separately authorized. Confirm the corresponding source-history retention is sufficient.
- **Execution:** Start with both values at `0` for ordinary continuation. For a replay, set the desired positive day count on the selected parameter (`bronze_lookback_days` or `silver_lookback_days`). For a coordinated replay, set the same positive value for both; the job runs bronze before silver. On a later normal run, set replayed layer parameters back to `0`.
- **Validation:** Review each task's requested cutoff, first observed Kafka record/CDF commit timestamp, `observed_window_shortened`, and task outcome. Verify table results and duplicate/idempotence behavior using environment-approved checks.
- **Failure handling:** A positive value intentionally removes that layer's checkpoint before stream start. On failure, stop and inspect task logs and table effects. A positive retry resets and repeats the replay; after a successful replay, use `0` to resume its advanced checkpoint. This change provides no way to restore the prior checkpoint, and no safe rollback for checkpoint state is defined.

## Verification Boundary

Build and Test was approved with an accepted verification limitation. Automated tests, Bundle validation, notebook execution, Kafka/Delta operations, and checkpoint operations remain unperformed. Complete Bundle validation and the required environment checks before considering deployment; the waiver does not establish successful runtime behavior or production readiness.
