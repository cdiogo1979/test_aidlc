# Performance Test Instructions

## Applicability

No daily volume, completion-window, throughput, or latency target was specified in the approved requirements. A performance pass/fail threshold therefore cannot be set without inventing requirements. Performance testing is **not applicable for this stage** and was not run.

## Future measurement approach

After a representative non-production dataset and workload targets are approved:

1. Use the isolated Databricks workspace and test topic described in `integration-test-instructions.md`.
2. Record the input record count/bytes, malformed-record ratio, runtime version, compute policy, and table/checkpoint configuration.
3. Measure end-to-end duration and per-task duration, records processed, input/output bytes, retries, and queue wait.
4. Repeat at representative and peak approved volume without reusing production data or checkpoints.
5. Compare results to an approved daily completion window and volume target. Do not declare pass/fail until those targets exist.

## Required inputs for a performance gate

- Expected and peak daily record counts and payload sizes.
- Required completion window and schedule time.
- Approved compute sizing/policy and cost constraints.
- Required performance evidence retention and acceptance owner.
