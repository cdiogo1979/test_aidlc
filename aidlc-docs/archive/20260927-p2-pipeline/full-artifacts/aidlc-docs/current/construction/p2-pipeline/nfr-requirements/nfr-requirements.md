# P2 Pipeline — NFR Requirements

## Inherited Workload Constraints

P2 inherits P1's Databricks Runtime 15.4 LTS or later requirement, deployment-provided compute policy and identity, Kafka TLS/SASL secret-reference pattern, retry settings, daily schedule inputs, and separate per-layer checkpoints. No new availability, throughput, or latency target was requested; P2 uses P1's configured schedule and job policy.

## Partial Property-Based Testing Requirements

- Framework: Hypothesis for Python.
- Scope: Generated tests for applicable pure functions, including P2 topic-override selection and the copied `_jaas_quote` helper. Spark/Delta stateful processing remains outside the user's selected partial scope.
- Properties: Generated project/topic mappings must select the P2 override without changing the shared default; generated text containing arbitrary Unicode, quotes, and backslashes must be escaped according to the helper contract while preserving all original characters.
- Round-trip rule PBT-02: N/A; this workload adds no serialization/deserialization or inverse pair.
- PBT-03: Applicable to escaping invariants for `_jaas_quote`.
- PBT-07: Use a domain-appropriate generated string strategy that includes quote and backslash cases.
- PBT-08: Keep Hypothesis shrinking enabled and set deterministic generation for CI; failures remain reproducible.
- PBT-09: Pin Hypothesis in development requirements, document it, and execute property tests in CI.

## Verification Boundary

Local tests can verify the pure helper property and static artifact relationships. Kafka, Databricks Jobs, Delta CDF, secret resolution, and S3 checkpoint behavior require the deployment environment and cannot be inferred from local checks.
