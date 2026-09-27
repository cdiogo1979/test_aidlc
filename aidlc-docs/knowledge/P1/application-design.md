# P1 Application Design

## Purpose and scope

P1 is a daily Databricks workload that ingests Kafka records into bronze Delta, processes valid JSON events into a silver current-state table, and quarantines malformed records. Gold processing is outside the current P1 scope.

## Components and responsibilities

- **P1 Daily Job (U3)**: Databricks Declarative Automation Bundle job that runs bronze before silver, passes the same environment and task parameters, and reports failure if either required task fails.
- **Bronze Ingestion (U1)**: Reads the configured Kafka topic, preserves payload and source metadata, and writes incrementally to the bronze Delta table. U1 assigns the UTC `bronze_ingestion_timestamp` on first insertion and owns its nullable additive schema handling.
- **Silver Processing and Quarantine (U2)**: Reads the bronze table through Delta Change Data Feed (CDF), validates and shapes JSON events, maintains one latest current-state row per `event_key`, and stores invalid records in quarantine. U2 assigns the UTC `silver_processing_timestamp` on accepted inserts/winning updates and owns its nullable additive schema handling.
- **Environment configuration**: `configs/{environment}.yaml` is shared by projects and provides database, storage, Kafka, and secret-reference settings. P1 continues to use the configured `kafka.topic` default; project-specific topic overrides may be added without changing that default. Each notebook resolves its own selected configuration.
- **Databricks Secrets**: Supplies Kafka credential material at runtime. Secrets are not passed in job parameters or checked-in source.
- **Delta tables**: Bronze is the persisted U1-to-U2 handoff. Silver and quarantine are outputs owned by U2.

## Interfaces and data flow

```text
Daily P1 job (U3)
  └─ U1 Bronze Ingestion ──> bronze Delta + CDF ──> U2 Silver Processing
                                                       ├─> silver current state
                                                       └─> quarantine
```

- U1 consumes the configured Kafka topic and writes `<database>.p1_test_kfk_brz`.
- U2 consumes bronze snapshot/CDF and writes `<database>.p1_test` and `<database>.p1_test_kfk_quarantine`.
- The job runs U2 only after U1 succeeds. Records are handed off through bronze Delta, not job parameters.
- Both notebooks receive `environment`; the job supplies independent bronze and silver lookback parameters, defaulting to zero for checkpoint continuation.

## Component interfaces

- U1 accepts the environment and bronze lookback parameters; its outputs are persisted bronze data and checkpoint progress.
- U2 accepts the environment and silver lookback parameters; its outputs are silver current state, quarantine rows, and CDF checkpoint progress.
- U3 accepts a scheduled or manual job invocation; overall success requires both dependent tasks to succeed.

Concrete runtime contracts, record semantics, and business rules are maintained in the per-component functional-design documents. U1 and U2 own their respective layer processing timestamps and additive nullable schema behavior; U3 continues to orchestrate the same bronze-then-silver task graph and does not implement timestamp writes.

## Architecture decisions and constraints

- Keep one daily job with sequential bronze and silver tasks.
- Keep Kafka ingestion in U1 and payload validation/current-state logic in U2.
- Use bronze Delta and CDF as the durable inter-component contract.
- Keep separate checkpoints for Kafka ingestion and bronze CDF consumption. A positive layer lookback deliberately resets that layer's checkpoint and replays from its cutoff; zero continues from its checkpoint.
- Silver uses Delta `VARIANT` for extensible JSON properties and requires Databricks Runtime 15.4 LTS or later.
- The current prod target still requires deployment-provided schedule/timezone, compute, run-as identity, and retry settings. See `p1-databricks-workload.md` for configuration and verification limits.

## Current verification status

P1 runtime behavior has not been verified in a Databricks environment. The workload knowledge document and archived intent summaries describe accepted verification limitations. This architecture records the approved design and is not evidence of successful deployment or runtime execution.

## Historical sources

- `aidlc-docs/archive/20260924-p1-databricks-workload/full-artifacts/aidlc-docs/inception/application-design/application-design.md`
- `aidlc-docs/archive/20260924-p1-layer-timestamp-columns/full-artifacts/aidlc-docs/inception/application-design/` (historical source)
