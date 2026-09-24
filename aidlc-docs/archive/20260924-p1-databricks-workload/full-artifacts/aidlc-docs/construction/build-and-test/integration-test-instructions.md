# Integration Test Instructions

## Status and prerequisites

P1 end-to-end integration testing is **blocked pending a non-production Databricks environment**. The current Bundle defines only a `prod` target, and no Databricks CLI, workspace authentication, isolated Kafka topic, test secret scope, or non-production configuration was available during this stage. Do not use production tables, checkpoints, Kafka offsets, or the `prod` Bundle target for test runs.

Before running these scenarios, the deployment owner must provide:

- An isolated non-production Databricks workspace and an approved Bundle target for it.
- A Databricks CLI installation and authentication profile for that workspace.
- A supported Databricks Runtime (15.4 LTS or later) with Delta VARIANT support.
- An isolated Kafka topic, its test broker settings, and a Databricks secret scope/key for the test identity.
- A non-production database/storage path, distinct bronze and silver CDF checkpoints, and the required table and secret grants.
- Approved retry, compute-policy, runtime, and schedule values for the non-production target.

The current repository has only `configs/prod.yaml`; create an environment-specific test configuration only after the deployment owner supplies its values. No test configuration or workspace resource is created by these instructions.

## Scenario 1: Bronze-to-silver processing and malformed-message isolation

1. Confirm the selected non-production configuration points to isolated tables, S3 paths, Kafka resources, and checkpoints.
2. Publish two valid records for one test key in known chronological order, for example `{"event_key":"test-1","status":"older"}` followed by `{"event_key":"test-1","status":"newer"}`.
3. Publish a malformed JSON record to the same test topic.
4. Run the P1 job with `environment` set to the non-production environment name.
5. Confirm the bronze table contains traceable Kafka source records, including the malformed record's original payload.
6. Confirm the silver table has exactly one current row for `test-1`, that it is the latest valid event, and that its `attributes` object contains `status: newer`.
7. Confirm the malformed record is present in quarantine with source metadata and an error, and is absent from silver.
8. Confirm the silver task started only after bronze succeeded and the overall job completed successfully.

## Scenario 2: Incremental progress and retry/idempotency

1. Record the isolated Kafka offsets and both checkpoint locations before the run.
2. Run the job; confirm bronze and silver checkpoints advance and expected records are present.
3. Run the job again without publishing new data. Confirm no duplicate bronze source identities or duplicate silver current rows appear, and that no old Kafka range is reprocessed beyond normal checkpoint recovery behavior.
4. If a retry test is required, use a deployment-approved fault in the non-production workspace only. Confirm the job retry policy is applied and the bronze Kafka and silver CDF checkpoints permit safe recovery.
5. Never delete or reset checkpoints as routine cleanup. Any intentional reset requires a separate approved recovery plan.

## Result capture and cleanup

Record the Bundle target, environment name, job run ID, task results, table counts/queries, quarantine evidence, and checkpoint locations. Use only disposable or approved test data. Clean up temporary messages and test tables only when the non-production data owner approves; preserve checkpoints until the test results are captured.

These scenarios have not been run. They are not considered passed until an isolated environment is available and the evidence is recorded.
