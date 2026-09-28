# Integration Test Instructions

## Scope and prerequisites
P2 runtime integration requires a Databricks workspace with the intended `prod` configuration, Kafka topic `my-test-p2`, referenced secrets, and the project's storage/catalog permissions. These services and credentials were not available in local Build & Test.

## Scenarios
1. Validate the P2 Databricks bundle with `databricks bundle validate -t prod` from `jobs/P2/`.
2. In an approved non-production workspace, run the P2 job against the P2 Kafka topic and confirm bronze writes use the P2 table/checkpoint.
3. Confirm silver CDF processing writes the P2 silver and quarantine tables and uses its P2 checkpoint.
4. Verify P1 continues reading its existing `kafka.topic` and P1 tables/checkpoints remain isolated.

Do not run or deploy these scenarios until the workspace owner has configured valid secret references and service access. Capture the bundle validation and job run results in the verification record.
