# U3 P1 Integration — Code Generation Plan

This is the single source of truth for U3 Code Generation after explicit user approval. It uses Databricks Declarative Automation Bundles, as selected by the user in the deployment-rendering clarification. The bundle YAML is the single authoritative job definition; no duplicate Jobs API JSON is planned.

## Unit context

- **Unit**: U3 — P1 Integration.
- **Project type**: Greenfield P1 Databricks workload; U3 integrates existing U1/U2 notebooks.
- **Approved infrastructure**: Existing P1 Databricks workspace/environment and job compute policy; shared job identity; daily schedule; one active run maximum with native queueing; no job notifications.
- **Functional contract**: Run bronze first and silver only after bronze succeeds. Pass the same `environment` parameter to both notebooks. Fail the job if either required task fails.
- **Inputs**: `notebooks/P1/bronze/bronze_ingestion.py`, `notebooks/P1/silver/silver_processing.py`, `src/common.py`, and `configs/{environment}.yaml` (`configs/prod.yaml` currently exists).
- **Bundle root**: `jobs/P1/databricks.yml`, with the job resource in `jobs/P1/resources/p1-daily-pipeline.yml`.
- **Stories and requirements**: FR-01 (P1 job artifact location), FR-03 (daily incremental pipeline), FR-08 (same environment reaches both tasks); supports US-P1-01 and US-P1-02 through the approved U1/U2 contracts.
- **Dependencies**: U1 and U2 notebooks and infrastructure are complete; U3 Functional Design, NFR Requirements, NFR Design, and Infrastructure Design are approved.
- **Explicitly out of scope**: New notebooks, changes to U1/U2 processing, new workspace/storage/network resources, alert recipients, notebook-level retry logic, Databricks deployment, and running the workload. Verification remains in Build and Test.

## Clarification resolution and artifact-format decision

Question 1 in `aidlc-docs/construction/plans/u3-p1-integration-code-generation-clarification-questions.md` was answered C: adopt Databricks Declarative Automation Bundles and allow bundle YAML instead of the previously specified job creation JSON. Use bundle variables and targets for deployment-owned values. This changes job packaging only; the approved Databricks platform, job contract, and runtime task design remain unchanged.

Bundle sync includes only `notebooks/P1/`, `src/`, and `configs/` in addition to the bundle root. Keep their relative layout so the existing notebooks can discover `src/common.py` and `configs/{environment}.yaml`. Use repository-relative notebook paths in the job resource; the Bundle CLI resolves them against the selected sync paths to workspace paths. Do not add a separate renderer or hard-code a workspace notebook root.

Define target variables without invented deployment values for the daily cron expression/timezone, job compute policy and required cluster settings, supported runtime (Databricks Runtime 15.4 LTS or later), shared run-as service principal, and the approved task retry policy. Supply values through the selected bundle target at deployment; keep credentials in Databricks Secrets. Databricks CLI workspace authentication remains an external deployment prerequisite.

## Generation steps

1. **Align repository conventions and current design references** — Update `AGENTS.md` to allow bundle YAML as the authoritative job definition, update the U3 infrastructure/technology decision artifacts and active design references from JSON to Bundles, and preserve this clarification answer and prior audit history unchanged.
2. **Set up the bundle root and resource include** — Create `jobs/P1/databricks.yml` and include `resources/p1-daily-pipeline.yml`. Declare the P1 bundle, required deployment variables, and a `prod` target without fabricated workspace-specific values.
3. **Configure selective sync and deployment outputs** — Sync `notebooks/P1/`, `src/`, `configs/`, and the bundle files while excluding unrelated repository folders. Resolve notebook workspace paths through supported bundle local-path resolution against those sync paths. Add `.databricks/` to `.gitignore` if it is not already ignored so local deployment state is not committed.
4. **Define the P1 job resource** — Create one daily scheduled job. Use bundle variables for deployment-owned schedule/timezone, compute/policy, runtime, run-as identity, and retry settings. Set `max_concurrent_runs` to one, enable queueing, and configure no email/notification recipients.
5. **Define ordered task interfaces** — Add the bronze task referencing the existing U1 notebook. Add the silver task referencing the existing U2 notebook and depending on bronze success. Pass one `environment` job parameter (default `prod`) to both notebook tasks. Keep secrets and Kafka/data configuration out of the job resource.
6. **Document the job artifact** — Create `aidlc-docs/construction/u3-p1-integration/code/code-summary.md` with the bundle structure, task interface/order, environment parameter, concurrency/queue behavior, target variables, sync layout, runtime requirement, and deployment command boundaries.
7. **Review generated artifacts** — Validate YAML structure and bundle includes, workspace file paths, target variables, task dependency, same environment parameter, one-active-run/queue settings, no notification settings, runtime minimum, secret safety, and FR-01/FR-03/FR-08 traceability. Do not run `bundle deploy` or trigger Databricks jobs; deployment and runtime verification are outside this code-generation plan.

## Deployment command guidance

The bundle is deployed from `jobs/P1/` using the selected target. Required variable values are supplied through Databricks bundle target/environment variable inputs, not committed as production values. `databricks bundle validate` and target deployment are documented, but only validation of generated source files is included before code review; deployment execution is not authorized by this plan.

## Plan status

- [x] Inspect U3 designs, U1/U2 contracts, notebook interfaces, repository structure, and code-generation rules.
- [x] Resolve the deployment-rendering clarification: adopt Declarative Automation Bundles and allow bundle YAML as the authoritative job definition.
- [x] Update project conventions and current design references to record the bundle decision without changing historic audit/question content.
- [x] User approves this complete Code Generation plan.
- [x] Generate the Bundle job definition and code summary exactly as approved.
- [x] Validate generated YAML syntax, includes, notebook paths, job contract, deployment variable references, and secret/notification constraints; CLI validation remains unavailable because the Databricks CLI and actual deployment values are not present.
