# P2 Application Design

## Purpose and scope

P2 is a separate daily Databricks pipeline that follows P1 processing behavior while consuming Kafka topic `my-test-p2`. It owns separate bronze, silver, quarantine, and checkpoint state. The shared `configs/prod.yaml` remains common to all projects; P1 retains the existing default topic `my-topic`, and P2 selects its explicit `kafka.topics_by_project.P2` override.

P2 source, configuration, and job artifacts are present in the repository. No PR, deployment, Databricks bundle validation, or Databricks/Kafka/storage runtime execution occurred. Verification limitations were explicitly accepted and are preserved in the archived intent record; this design is not evidence of runtime success.

## Components and responsibilities

- **P2 Daily Job (U3)**: Databricks bundle job that runs P2 bronze before P2 silver, with P1-equivalent schedule, parameters, retry behavior, and deployment inputs.
- **Bronze Ingestion (U1)**: Reads only the configured P2 topic, preserves Kafka payload and metadata, and writes the P2 bronze Delta table.
- **Silver Processing and Quarantine (U2)**: Reads P2 bronze CDF, validates events, maintains P2 current state, and writes invalid records to P2 quarantine.
- **Environment configuration**: Uses the shared `configs/prod.yaml`; the P2 topic resolver fails closed if the P2 override is absent.
- **Databricks Secrets**: Supplies Kafka credential material at runtime through the existing reference pattern. Secret values are not committed.

## Interfaces and data flow

```text
P2 Daily Job (U3)
  └─ P2 Bronze Ingestion (U1) ──> P2 bronze Delta + CDF ──> P2 Silver (U2)
                                                              ├─> P2 silver current state
                                                              └─> P2 quarantine
```

- U1 writes `<database>.p2_test_kfk_brz` and uses `{data_path}/checkpoints/P2/bronze_ingestion`.
- U2 reads that P2-owned bronze table and writes `<database>.p2_test` and `<database>.p2_test_kfk_quarantine`, using `{data_path}/checkpoints/P2/silver_processing`.
- U2 starts only after U1 succeeds. Bronze Delta is the persisted handoff; no payloads or credentials pass through job parameters.
- Both notebooks receive `environment=prod`; each task has its own lookback control and checkpoint.

## Architecture decisions and constraints

- Keep a separate `jobs/P2/` bundle and `notebooks/P2/` sources.
- Preserve P1 processing behavior and orchestration while assigning P2-only table/checkpoint names and paths.
- Keep `configs/prod.yaml` shared across projects; retain the P1 default topic and select P2 through an explicit project override.
- Require Databricks Runtime 15.4 LTS or later and deployment-provided schedule, timezone, compute policy, service identity, and retry values, following P1's contract.
- Deployment requires successful bundle validation and target-workspace checks; the current intent records accepted verification limitations and no deployment.

## Historical source

- `aidlc-docs/archive/20260927-p2-pipeline/intent-summary.md`
