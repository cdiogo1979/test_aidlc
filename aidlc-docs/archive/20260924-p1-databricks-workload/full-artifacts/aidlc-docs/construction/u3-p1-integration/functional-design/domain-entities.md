# U3 P1 Integration — Domain Entities

## P1 Integration Run

Represents one invocation of the daily P1 workload.

| Attribute | Description |
|---|---|
| Environment | Environment name supplied to the run and passed unchanged to both notebook tasks. |
| Trigger | Scheduled daily invocation; manual invocation follows the same task flow when used. |
| Task outcomes | Result of the bronze task and, when permitted by dependency success, the silver task. |
| Overall outcome | Successful only when both required tasks succeed; otherwise failed. |

## Bronze Task

The U1 task that reads the configured Kafka source and writes source payload plus metadata to bronze Delta. It is the first task in the integration run and owns its Kafka checkpoint.

## Silver Task

The U2 task that reads bronze Delta CDF and writes silver and quarantine outputs. It depends on successful completion of the Bronze Task and owns its CDF checkpoint.

## Relationships

- One P1 Integration Run contains one Bronze Task and one dependent Silver Task.
- The Bronze Task precedes the Silver Task; the Silver Task is eligible to run only after Bronze succeeds.
- Both tasks receive the same environment value and independently resolve their configuration.
- Bronze Delta is the persisted data handoff between the tasks; no event payload is part of the job-level parameter entity.
