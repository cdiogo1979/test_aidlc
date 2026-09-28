# P2 Deployment Instructions

Deployment is conditional. Local tests passed, but Databricks bundle and runtime verification were waived and remain unverified. Do not enable the schedule or run the pipeline until the blockers and required validation below are resolved.

## 1. Resolve deployment inputs and prerequisites
- **Target:** Databricks workspace and production bundle target `prod`; the concrete workspace URL/account and deployment owner are required inputs.
- Confirm an approved deployment identity with permission to validate/deploy the bundle, create/update jobs and job clusters, access notebooks, and use the required catalogs, schemas, Kafka, and storage.
- Supply the bundle variables defined in `jobs/P2/databricks.yml`: daily schedule Quartz expression and timezone, approved job cluster policy ID, supported Databricks Runtime version (15.4 LTS or later), service principal application ID, max retries, and retry interval. Use the project's approved shared policy values; do not infer them.
- Configure `configs/prod.yaml`'s deployment placeholders using approved non-secret values. Store Kafka credentials in the approved Databricks secret scope/key; never commit secret values.
- Confirm Kafka topic `my-test-p2`, broker access, P2 database/schema and storage path, table permissions, and P2 checkpoint permissions. Confirm they do not overlap P1 state.
- Confirm the CI/package index can install the exact pinned development dependencies from `requirements-dev.txt`, or resolve the pin/index discrepancy through the project dependency process.

## 2. Validate the P2 bundle (automated CLI step)
- **Action and target:** Validate `jobs/P2/` against the production target without deploying.
- **Prerequisites:** Resolve bundle variables, configure Databricks CLI authentication for the approved workspace, and complete step 1.
- **Execution:** From `jobs/P2/`, run `databricks bundle validate -t prod`.
- **Validation:** Require successful validation and review the resolved P2 notebook paths, job identity, policy/runtime, schedule, retry values, and target workspace. Correct issues and rerun validation before deployment.
- **Failure handling:** Stop on any validation error. No deployment or schedule enablement is allowed until validation passes. Preserve existing job configuration; do not improvise rollback values.

## 3. Deploy the P2 bundle (automated CLI step)
- **Action and target:** Create/update bundle `p2_databricks_workload` and job `P2 Daily Pipeline` in the approved production workspace.
- **Prerequisites:** Step 2 passes; deployment is authorized by the workspace owner; all variable and service prerequisites are confirmed. The job resource currently sets the schedule to `UNPAUSED`, so obtain explicit release authorization before deploying this schedule state.
- **Execution:** From `jobs/P2/`, run `databricks bundle deploy -t prod` only after the above approval.
- **Validation:** Confirm the deployed job points to `notebooks/P2/bronze/bronze_ingestion.py` then `notebooks/P2/silver/silver_processing.py`, uses the P2 job cluster and approved run-as identity, and has the approved schedule and parameters. Confirm P1 job/config remain unchanged.
- **Failure handling:** Stop if deployment partially fails or changes shared/P1 resources. Notify the deployment owner and use the workspace's approved recovery procedure. This intent does not define a safe rollback or deletion procedure.

## 4. Run controlled P2 verification (manual workspace action)
- **Action and target:** Execute the deployed P2 job once in the approved workspace using its default `prod` environment and approved lookback settings.
- **Prerequisites:** Step 3 is approved and complete; topic, secret access, data permissions, and P2 checkpoint/table locations are confirmed. Coordinate the run window with data owners.
- **Execution:** Trigger `P2 Daily Pipeline` manually from the Databricks Jobs UI. Do not change the P1 job.
- **Validation:** Confirm bronze reads only `my-test-p2`; bronze, silver, quarantine, and checkpoints are P2-specific; silver depends on successful bronze completion; review row counts, quarantine results, and job logs. Verify no P1 table or checkpoint was modified.
- **Failure handling:** Stop subsequent/scheduled runs on unexpected topic, table, checkpoint, or identity behavior. Preserve logs and checkpoint/data evidence; have the data owner determine repair/replay. No destructive cleanup or rollback is specified by this intent.

## 5. Enable normal schedule
- **Action and target:** Keep/enable the approved daily schedule for `P2 Daily Pipeline`.
- **Prerequisites:** Controlled run in step 4 passes; data and operations owners approve regular schedule activation.
- **Execution:** If the job was paused for verification, enable its approved daily schedule in Databricks Jobs UI.
- **Validation:** Confirm the next run is scheduled at the approved time and the P1 schedule remains unchanged.
- **Failure handling:** Pause P2 if scheduling or isolation is incorrect and contact the job owner. Follow the operational recovery procedure established by that owner.

## Verification limitation
The user accepted verification limitations for the unavailable local Databricks bundle/runtime checks and the unexecuted Jenkins pipeline/new Code Analysis checks (including the Flake8 version unavailable from the configured local package index). These waivers do not validate production configuration, prove runtime behavior, authorize deployment, or replace the validation and approvals above.
