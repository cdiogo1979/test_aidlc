# P2 Pipeline — Business Rules

1. P2 consumes only Kafka topic `my-test-p2`; do not alter P1's topic or configuration.
2. Preserve Kafka payload and selected metadata unchanged in P2 bronze. Deduplicate by `(topic, partition, offset)`.
3. Enable and retain CDF for P2 bronze; silver consumes that P2-owned table only.
4. Preserve P1 lookback semantics independently per layer: zero resumes the corresponding P2 checkpoint; positive lookback intentionally resets and replays only that P2 layer.
5. Silver accepts object JSON with a present, nonblank string `event_key`; preserve valid keys and arbitrary JSON attributes as P1 does.
6. Route invalid payloads to P2 quarantine, preserving payload, source identity, and diagnostic context.
7. Preserve P1 event ordering, processing timestamp, nullable schema migration, retry, and error behavior.
8. P2 uses P2-specific table and checkpoint identifiers. It must not read, write, reset, or depend on P1 tables or checkpoints.
9. P2's job runs bronze before silver and reports failure if either task fails.
10. Deployment-provided schedule, timezone, runtime, compute policy, identity, and retry values follow the P1 bundle contract.
