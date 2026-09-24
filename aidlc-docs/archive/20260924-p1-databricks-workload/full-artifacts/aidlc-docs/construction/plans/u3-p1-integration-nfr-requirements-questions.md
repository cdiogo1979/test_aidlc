# U3 P1 Integration — NFR Requirements Questions

Please answer the question below by filling in the `[Answer]:` field, then reply `done`.

## Question 1 — Overlapping job runs

If a scheduled or manual P1 run is triggered while another P1 run is still active, what should happen? U1 and U2 share persistent streaming checkpoints, so the recommended policy is to keep their task runs serialized. Databricks supports a maximum concurrency setting and optional run queueing; queued runs can wait up to 48 hours under the documented behavior ([Databricks job queueing](https://docs.databricks.com/aws/en/jobs/configure-job)).

A) Allow at most one active P1 run and enable queueing so another trigger waits for capacity (Recommended; avoids simultaneous use of shared task state and avoids immediately skipping the trigger).

B) Allow at most one active P1 run and disable queueing; overlapping triggers are skipped, and later scheduled runs resume from the durable checkpoints.

C) Allow multiple concurrent P1 runs.

X) Other (please describe after `[Answer]:`)

[Answer]: A
