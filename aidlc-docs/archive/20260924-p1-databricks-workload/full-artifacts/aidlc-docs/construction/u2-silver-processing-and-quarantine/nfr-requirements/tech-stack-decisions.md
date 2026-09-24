# U2 Silver Processing and Quarantine — Technology Decisions

## Decisions

| Concern | Decision | Rationale / constraint |
|---|---|---|
| Compute and execution | Databricks notebook in the P1 daily job. | Established by the approved P1 application design and repository conventions. U3 owns job integration. |
| Input persistence | Read the bronze Delta table `test_prod.p1_test_kfk_brz`. | U1 owns Kafka ingestion; the Delta table is the approved boundary between U1 and U2. |
| Silver persistence | Write the Delta table `test_prod.p1_test`. | Approved U2 output and table technology. |
| Quarantine persistence | Write the Delta table `test_prod.p1_test_kfk_quarantine`. | Approved quarantine destination and table technology. |
| Environment configuration | Use `configs/{environment}.yaml` and existing shared configuration helpers where applicable. | Keeps environment-specific values out of shared notebook logic and follows the repository convention. |
| Credentials and access | Use existing approved Databricks access controls and secret storage; do not embed secret material in code or checked-in configuration. | No additional security or compliance policy was specified. |
| Retry and data integrity | Make silver and quarantine writes idempotent by `(topic, partition, offset)` and order current-state updates according to the approved Kafka timestamp/partition/offset rule. | Supports retry after partial output persistence without asserting a cross-table transaction or platform-wide exactly-once guarantee. |
| Event shape | Persist `event_key` and all other JSON properties in an `attributes VARIANT` object. | User selected Delta `VARIANT` in Code Generation planning to preserve arbitrary nested JSON values. Requires Databricks Runtime 15.4 LTS or later and Delta variant support enabled; the writer protocol upgrade may affect older external Delta clients. |

## Technology scope

This stage records existing technology constraints. It does not select infrastructure topology, Databricks cluster sizing, Delta table layout/optimization settings, or implementation-specific APIs. Those details belong to subsequent design and code-generation stages and must remain consistent with the approved functional and NFR requirements.
