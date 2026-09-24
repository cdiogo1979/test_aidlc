# U2 Silver Processing and Quarantine — NFR Design Patterns

## Resilience and recovery

- Read the daily bronze Delta Change Data Feed after U1 completes successfully, using a stable Structured Streaming checkpoint under `{data_path}/checkpoints/P1/silver_processing` and `AvailableNow`.
- Classify records into valid events and quarantine candidates without allowing a malformed record to stop processing of other records.
- Persist silver and quarantine outputs as independently idempotent writes keyed by `(topic, partition, offset)`. Do not imply a transaction spanning both Delta tables.
- Treat a failed read or either failed output write as a failed U2 task. A partial output may already be committed; retry/replay processes the same input and reconciles through source-identity deduplication and the silver latest-event ordering rule.
- Depend on configured Databricks job retry or a later scheduled run for retry timing; retry count and timing remain deployment settings.
- Depend on the source table retaining CDF history long enough for the scheduled stream to resume. Keep default failure-on-data-loss behavior. If required table versions have expired, fail and use a deliberate full refresh/rebuild rather than silently skipping changes.
- Do not claim platform-wide exactly-once processing or atomic visibility across silver and quarantine.

## Scalability

- Process only the bronze CDF changes made available by the preceding U1 run; the first stream start processes the current table snapshot as inserts.
- Use the existing Databricks distributed execution model for the batch; do not introduce a separate queue, service, or scaling subsystem.
- Keep transformations distributable by source record and `event_key`; reduce duplicate candidates per key before applying current-state updates.
- Defer worker sizing, partition counts, and growth triggers until representative workload volumes are known.

## Performance

- Keep the work bounded to the available daily increment and avoid repeated full-history scans where the selected implementation can operate from incremental input plus current state.
- Do not add caching, custom partitioning, table layout tuning, or benchmark thresholds without measured evidence or an approved completion-window target.
- Use platform-provided task status/logging; do not add custom metric or alert infrastructure in this scope.

## Security and data minimization

- Rely on existing approved Databricks access controls and platform protections for bronze, silver, and quarantine tables.
- Keep raw payloads and complete parse/validation diagnostics in the access-controlled quarantine table, where they support diagnosis.
- Limit task logs to operational status, non-sensitive counts, and source identifiers needed for troubleshooting. Do not log raw payloads or secrets.
- Keep credentials and secret values out of notebook source, job definitions, and checked-in configuration.

## Operational visibility

- Surface read, classification, and output persistence failures as task failures so they are visible in Databricks job/task status.
- Include concise run-level counts and safe source identity context in task logs when useful; avoid event payload content.
- No alert thresholds, recipients, uptime objective, or custom telemetry service is defined.

## Retention and replay

- Follow existing table/platform retention policies. Retention must preserve current silver state and the quarantine records needed for diagnosis under the approved operating policy.
- Any cleanup policy must account for the replay/recovery horizon; no duration is specified at this stage.

## Applicability summary

Security Baseline, Property-Based Testing, and Resiliency Baseline extensions are disabled. No extension-specific requirements apply. The patterns above come from the approved U2 Functional Design, NFR Requirements, and NFR Design answers.
