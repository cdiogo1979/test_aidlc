# U3 P1 Integration — Code Summary

## Bundle layout

The P1 job is defined by one Databricks Declarative Automation Bundle:

| Path | Purpose |
|---|---|
| `.gitignore` | Repository-wide exclusion for local Databricks Bundle state and deployment variable overrides. |
| `jobs/P1/.gitignore` | Bundle-root exclusion for local state during Bundle sync. |
| `jobs/P1/databricks.yml` | Bundle metadata, selective sync paths, required deployment variables, and the `prod` target. |
| `jobs/P1/resources/p1-daily-pipeline.yml` | Scheduled job, shared job cluster, runtime job identity, parameters, retries, and ordered notebook tasks. |
| `notebooks/P1/bronze/bronze_ingestion.py` | Existing U1 bronze ingestion notebook. |
| `notebooks/P1/silver/silver_processing.py` | Existing U2 silver processing and quarantine notebook. |
| `src/common.py` | Existing shared configuration helpers synced with the notebooks. |
| `configs/prod.yaml` | Existing production environment configuration synced with the notebooks. |

The bundle syncs only the P1 notebook folder, `src/`, `configs/`, and the bundle root. It preserves their paths so notebooks can locate the shared library and the selected `configs/{environment}.yaml`. Notebook task paths refer to the repository's local notebook files; the Bundle CLI resolves those paths for the target workspace.

## Job contract

- Run the bronze notebook first; run silver only after bronze succeeds.
- Pass the job-level `environment` parameter, defaulting to `prod`, to both notebook tasks. Databricks pushes key-value job parameters to notebook tasks automatically.
- Use one shared policy-backed job cluster for both tasks.
- Enforce at most one active job run and queue later triggers.
- Apply the approved existing P1 retry policy to both notebook tasks.
- Configure no email or webhook notifications.
- Keep credentials and secret values out of the bundle. U1 continues retrieving Kafka credentials through Databricks Secrets.

## Required deployment inputs

The bundle deliberately has no fabricated production values. Supply these values to the `prod` target through the Databricks CLI variable mechanism or an ignored `.databricks/bundle/prod/variable-overrides.json` file:

| Variable | Deployment-owned value |
|---|---|
| `daily_schedule_cron_expression` | Approved daily Quartz schedule. |
| `daily_schedule_timezone` | Approved timezone. |
| `job_cluster_policy_id` | ID of the approved P1 job compute policy. |
| `job_spark_version` | Supported Databricks Runtime, 15.4 LTS or later, with Delta VARIANT support. |
| `job_run_as_service_principal` | Application ID of the shared P1 run-as identity. |
| `job_max_retries` | Retry count from the existing approved policy. |
| `job_min_retry_interval_millis` | Retry delay in milliseconds from the existing approved policy. |

The policy supplies its required cluster defaults through `apply_policy_default_values`. Workspace authentication and required grants must be configured in the deployment environment; no authentication material is stored in this repository.

## Requirements traceability

| Requirement | Implementation |
|---|---|
| FR-01 — P1 job artifact location | The single authoritative job definition is the Bundle rooted at `jobs/P1/databricks.yml`, with its resource in `jobs/P1/resources/`. |
| FR-03 — daily incremental pipeline | The daily scheduled job runs the existing checkpointed U1 notebook followed by U2; its cron expression and timezone are supplied at deployment. |
| FR-08 — shared environment selection | The job defines one `environment` parameter defaulting to `prod`; Databricks pushes this key-value parameter to both notebook tasks. |
| US-P1-01 and US-P1-02 | The job composes the approved bronze ingestion and silver/quarantine contracts in dependency order. |

## Validation and release boundary

From `jobs/P1/`, validate using `databricks bundle validate -t prod` after supplying all required variables and configuring Databricks CLI authentication. Deploy with `databricks bundle deploy -t prod` only through the approved deployment process. Neither command deploys in this code-generation review; no Databricks workspace was contacted and no notebook was run.

Ruby's YAML parser and static checks confirmed both YAML files parse, the included resource exists, both notebook paths resolve to existing files, the silver task depends on bronze, the job parameter defaults to `prod`, and maximum concurrency/queueing are set to one/enabled. Static review confirmed that secrets and notification recipients are absent and all required deployment variables are declared and referenced. The Databricks CLI is not installed in this workspace, so `databricks bundle validate` and workspace authentication checks were not run. The deployment-supplied runtime must be checked against the documented 15.4 LTS minimum before deployment.
