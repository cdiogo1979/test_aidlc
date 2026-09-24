# Build and Test — Non-Production Verification Questions

P1 local source checks passed, but the Databricks integration scenarios cannot run against the current `prod`-only bundle. To continue runtime verification, answer the following without including passwords, tokens, or secret values.

## Question 1 — Non-production Databricks target

Is an isolated non-production Databricks workspace available for P1 integration testing?

A) Yes. Provide the non-secret workspace/target details, confirm the approved Databricks CLI is installed and authenticated locally, and provide the approved values/references needed for a non-production bundle target.

B) Not yet. Keep P1 runtime verification blocked until the environment is available.

[Answer]: B

## Question 2 — Test deployment and execution authorization

If the non-production target is available, may the test process deploy the P1 bundle to that target and run it with disposable test messages/tables/checkpoints?

A) Yes. Confirm the Kafka topic, database/storage path, checkpoints, and Databricks secret references are isolated test resources, and authorize bundle deployment and job execution in that non-production target.

B) No. Do not deploy or run the job; keep verification limited to local checks and instructions.

[Answer]: B

Do not provide authentication credentials or secret values in this file. Keep secret material in the approved local credential mechanism and Databricks Secrets.

## Current disposition

On 2026-09-24, the user chose to consider Build and Test complete with P1 runtime integration and performance tests deferred. This is a workflow deferral and does not constitute successful end-to-end verification. The answers above remain blank because no non-production environment details or test deployment authorization were supplied.
