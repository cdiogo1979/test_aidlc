# U1 Bronze Ingestion — NFR Design Patterns

## Resilience and recovery

- Treat Kafka read and bronze write failures as task failures; never skip failed input to keep the task running.
- Use the Databricks job's configured retry behavior. Retry count and delay/backoff belong to deployment configuration and remain unspecified here.
- Keep the durable Structured Streaming checkpoint as the source of incremental progress. A retry or later run resumes from the last committed checkpoint.
- Apply the source identity `(topic, partition, offset)` to prevent duplicate logical bronze records when a retry or replay presents an already-persisted record.
- Do not add notebook-level retry loops. Avoid stacking independent retry policies that could obscure task failure or exceed any later-defined recovery window.
- This pattern supports restart and replay but does not claim platform-wide exactly-once processing.

## Scalability and compute

- Run U1 as the bronze task in the existing daily Databricks job.
- Use the deployment's approved Databricks compute policy; do not set workload-specific fixed sizing or autoscaling bounds while volume and growth are unknown.
- Review actual run duration and volume after representative operation before setting capacity limits or scaling targets.
- Keep the source read incremental so each run handles available new records rather than intentionally rescanning all source history.

## Performance

- Use the standard incremental Structured Streaming path and preserve source values and required Kafka metadata.
- Avoid adding transformations or parsing in U1; JSON validation belongs to U2 and would add work outside U1's responsibility.
- Do not introduce numeric throughput, latency, or completion targets. Tune only after representative volume and measurements are available.

## Security

- Resolve Kafka credentials through the configured Databricks secret reference. Secret values must not appear in repository files, notebook/job artifacts, or logs.
- Grant the Databricks job only the access provided by the existing approved deployment access controls for its Kafka source, checkpoint location, and bronze destination.
- Resolve environment-specific hosts and references through `configs/{environment}.yaml`; keep the secret value itself in Databricks Secrets.
- No additional classification, encryption, or compliance pattern was specified. Do not imply that this design independently configures those platform controls.

## Observability

- Use Databricks task/job outcome and task logs as the initial operational signal.
- A failed Kafka read or bronze write must remain visible as a failed task, with available exception context in task logs.
- No custom metrics, alert destinations, thresholds, or separate monitoring service are introduced because none were specified.

## Deferred design/deployment values

Compute profile, job retry count and delay, concrete checkpoint URI and retention, runtime version, and any alert configuration are supplied by infrastructure or deployment design. Any later values must preserve the failure, checkpoint, source identity, and secret-protection rules above.
