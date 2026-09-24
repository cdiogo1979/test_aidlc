# U3 P1 Integration — Business Rules

1. **Single workload**: Run U1 and U2 as tasks in one P1 integration job; the units are not separately deployed workloads.
2. **Daily cadence**: The job is configured for one scheduled run per day. Exact execution time and timezone are deployment settings.
3. **Task order**: Run U1 Bronze Ingestion first. U2 Silver Processing and Quarantine may start only after U1 succeeds.
4. **Failure propagation**: A U1 failure prevents U2 from starting and fails the job run. A U2 failure also fails the job run.
5. **Shared environment**: Supply the same environment name to both tasks. Each notebook independently loads `configs/{environment}.yaml`.
6. **Persisted handoff**: U1 and U2 communicate through the bronze Delta table. Do not pass event records or secrets through job parameters.
7. **Checkpoint ownership**: U1 owns its Kafka checkpoint; U2 owns its bronze CDF checkpoint. The job does not reset either checkpoint during normal runs.
8. **Recovery**: Configured retries or later scheduled runs rely on the U1/U2 checkpoint and idempotency contracts. Do not mark a failed task or incomplete pipeline as successful.
9. **Scope**: The P1 job runs only bronze ingestion and silver processing/quarantine. Gold transformations are excluded.
10. **Run outcome**: The job is successful only when all required tasks in the configured dependency chain succeed.
