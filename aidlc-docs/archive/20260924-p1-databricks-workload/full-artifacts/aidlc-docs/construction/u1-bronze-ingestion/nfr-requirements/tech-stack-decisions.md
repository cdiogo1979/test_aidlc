# U1 Bronze Ingestion — Technology Decisions

## Decisions and constraints

| Concern | Decision | Basis/status |
|---|---|---|
| Workload platform | Databricks | Established by the approved P1 requirements and repository purpose. |
| Notebook language and artifact form | Python Databricks notebooks under `notebooks/P1/bronze/` | Established by repository `AGENTS.md`; exact notebook/runtime version is not selected here. |
| Source transport | Kafka, topic `my-topic` | Approved requirement FR-02. Production bootstrap host comes from `kafka.hosts` in environment configuration. |
| Incremental ingestion | Structured Streaming with durable checkpointing | Existing approved requirements assumption and U1 Functional Design progress contract. Checkpoint path is a later infrastructure/deployment decision beneath the configured storage location. |
| Bronze persistence | Delta table `test_prod.p1_test_kfk_brz` | Approved requirement FR-04 and U1 unit contract. |
| Configuration | Load selected environment values from `configs/{environment}.yaml` | Approved application design and repository conventions. |
| Credential storage | Databricks secret reference; secret values stay outside the repository | Approved requirement FR-02. Secret scope name remains a deployment/environment setting. |
| Job orchestration | The P1 Databricks job runs U1 as the bronze task before U2 | Approved application design; U3 owns the Declarative Automation Bundle job definition. |

## Decisions deferred

- Databricks Runtime version and compatible library versions.
- Concrete checkpoint path and checkpoint lifecycle/retention policy.
- Exact table/catalog naming resolution and deployment-specific permissions.
- Job retry count, timeout, concurrency, and alert configuration.
- Numeric workload capacity, performance, and recovery objectives.

These values are intentionally deferred to NFR Design, Infrastructure Design, or deployment configuration. This assessment does not introduce an unapproved version, capacity, or operational target.

## Rejected or unselected alternatives

No alternatives were compared in this assessment because the platform, source, storage format, and access approach are already constrained by approved requirements and design. No new technology preference was needed from the user.
