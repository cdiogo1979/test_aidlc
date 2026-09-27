# U3 P1 Integration — Functional Design

## Purpose and boundary

Orchestrate the P1 bronze and silver workload as one daily Databricks job. U3 owns task dependency, environment/parameter propagation, and overall run outcome. U1 owns ingestion; U2 owns silver processing and quarantine.

## Inputs and outputs

- **Trigger**: Scheduled daily invocation or manual run following the same task order.
- **Parameters**: One environment value and layer-specific lookback parameters, with each lookback defaulting to zero.
- **Tasks**: U1 Bronze Ingestion followed by U2 Silver Processing and Quarantine.
- **Outcome**: Job success only when both required tasks succeed.

## Business logic

1. Start U1 with the selected environment and bronze lookback.
2. Start U2 with the same environment and silver lookback only after U1 succeeds.
3. Each notebook independently loads `configs/{environment}.yaml`; secrets and event records are not passed as job parameters.
4. Use bronze Delta as the durable task-to-task handoff.
5. Propagate any task failure as an unsuccessful job run. Retries and later scheduled runs rely on each unit's checkpoint and idempotency behavior.

## Business rules

- U1 precedes U2; U1 failure prevents U2 from running.
- Both tasks receive the same environment setting, but retain independent lookback controls and checkpoints.
- Normal runs do not reset checkpoints; only a positive layer lookback requests that layer's replay/reset behavior.
- Daily schedule time, timezone, compute, service principal, retry policy, and other environment deployment parameters are supplied by the deployment target.
- Gold transformations are outside the current job scope.

## Domain entities

### P1 integration run

One invocation with a trigger, environment, task outcomes, and overall outcome. A successful run requires successful U1 and U2 tasks.

### Bronze and silver tasks

The bronze task owns its Kafka checkpoint and bronze write. The dependent silver task owns its CDF checkpoint and silver/quarantine writes. Bronze Delta is their persisted data contract.

## Failure and recovery

Bronze failure blocks silver and fails the job. Silver failure fails the job. A later run relies on unit-level checkpoints, retention, and idempotency; it must not label an incomplete pipeline successful.

## Historical source

- `aidlc-docs/archive/20260924-p1-databricks-workload/full-artifacts/aidlc-docs/construction/u3-p1-integration/functional-design/`
