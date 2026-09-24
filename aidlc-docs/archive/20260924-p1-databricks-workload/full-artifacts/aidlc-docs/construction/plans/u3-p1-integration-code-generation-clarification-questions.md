# U3 P1 Integration — Code Generation Clarification

The approved Infrastructure Design keeps schedule, retry, compute, workspace identity, and workspace notebook paths deployment-owned. The repository currently has no Databricks bundle configuration or job JSON renderer. The job artifact needs a defined handoff to become valid and deployable without inventing workspace-specific values.

## Question 1 — Job JSON deployment rendering

Which deployment contract should Code Generation target for the job JSON and its deployment-owned values (schedule/timezone, retry policy, workspace notebook root, compute/policy, and run-as identity)?

A) An existing external deployment process renders a source-controlled JSON template. Specify the renderer's expected variable/placeholder syntax and how it maps repository notebooks into workspace paths after `[Answer]:`. (Recommended if such a process exists; keeps deployment tooling outside this repository.)

B) Add a small project-local renderer that reads a job template plus environment-specific non-secret values and emits valid Databricks Jobs API JSON. Specify where its workspace notebook root, schedule/timezone, compute/policy, run-as identity, and retry inputs should come from after `[Answer]:`.

C) Adopt Databricks Declarative Automation Bundles and bundle variables/targets for deployment-time values. Confirm that the repository convention may add bundle YAML alongside or instead of the required job creation JSON.

X) Other (describe the deployment/rendering contract and workspace notebook path mapping after `[Answer]:`).

[Answer]: C

## Decision note

Databricks' official documentation describes bundle variables as deployment-time substitutions and provides scheduled-job bundle examples. The repository currently specifies job creation JSON under `jobs/P1/` and contains no bundle setup. Select an option or describe the existing deployment mechanism so the generated artifact matches the team's actual deployment path. See [bundle variables](https://docs.databricks.com/aws/en/dev-tools/bundles/variables) and [bundle scheduled-job examples](https://docs.databricks.com/aws/en/dev-tools/bundles/examples).
