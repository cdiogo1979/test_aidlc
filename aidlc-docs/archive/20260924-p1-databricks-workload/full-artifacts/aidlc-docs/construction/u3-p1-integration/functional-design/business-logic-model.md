# U3 P1 Integration — Business Logic Model

## Purpose

Run the approved P1 bronze ingestion and silver processing workflow as one daily integration run, with a clear dependency between the two notebook tasks.

## Inputs and outputs

| Kind | Description |
|---|---|
| Trigger | The configured daily P1 job invocation. |
| Environment | One environment name, such as `prod`, supplied to both notebook tasks. |
| Bronze task | U1 reads Kafka using the selected environment configuration and persists source records to the bronze Delta table. |
| Silver task | U2 reads bronze Delta Change Data Feed and writes current valid events to silver and malformed events to quarantine. |
| Outcome | Overall job success only when required tasks complete successfully; failed bronze prevents silver from running. |

## Main flow

1. Receive the selected environment value for the P1 job run.
2. Start U1 Bronze Ingestion and pass it the environment value.
3. If U1 succeeds, start U2 Silver Processing and Quarantine with the same environment value.
4. U1 and U2 independently load `configs/{environment}.yaml`; no credentials or event payloads are passed through job parameters.
5. U2 consumes the bronze Delta table as the persisted handoff from U1. The job does not transfer records directly between tasks.
6. Report the overall run as successful only after both tasks succeed. Surface a failed task as a failed job run.

## Alternate and failure flows

- **Bronze succeeds with no new Kafka records**: U1 completes normally and U2 runs. U2 completes if there are no unprocessed CDF records.
- **Bronze fails**: Do not start U2; the job run is unsuccessful.
- **Silver fails**: The job run is unsuccessful. Recovery follows the task/job retry policy and the durable Kafka and CDF checkpoints defined by U1 and U2.
- **Missed or delayed daily run**: A later successful run uses the existing checkpoints to resume available work, subject to the approved Kafka and CDF retention limits.
- **Invalid environment configuration**: The relevant notebook fails its task; the overall job run is unsuccessful.

## Unit boundary

U3 owns orchestration and environment parameter propagation. U1 owns Kafka ingestion and bronze persistence. U2 owns CDF consumption, JSON validation, silver current-state updates, and quarantine. The bronze Delta table is the inter-task data contract. Gold outputs are outside P1 scope.

## Traceability

- **FR-01**: Place the P1 job definition under `jobs/P1/` and use the P1 notebook paths.
- **FR-03**: Schedule one daily incremental run.
- **FR-08**: Pass one environment value so both notebooks load the matching configuration.
- **US-P1-01 / US-P1-02**: Run the complete ordered pipeline that produces silver and quarantine outcomes.
