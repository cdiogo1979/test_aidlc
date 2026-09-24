# U4 NFR Design Plan — P1 Layer Timestamp Metadata

## Scope

Translate approved U4 NFRs into implementation patterns and logical responsibilities without introducing new services, packages, infrastructure, or pipeline stages.

## Category Assessment

- **Resilience**: Reuse the insert-only bronze merge and conditional silver merge. Preserve checkpoint advancement/failure behavior; do not add retries or change resiliency policy.
- **Scalability**: No scaling target or new capacity boundary exists. Keep work in the current microbatch projections and merges.
- **Performance**: Generate timestamps in Spark expressions and avoid per-record Python work, extra scans, and new full-table operations except schema inspection/validation required for migration.
- **Security**: No new access path, data exposure, or secret use is needed. Security Baseline is disabled; existing identity and table access remain unchanged.
- **Logical components**: Reuse existing bronze notebook, silver notebook, Spark session, and Delta tables; no queue, cache, service, or job component is added.

No clarification questions are needed. The approved NFRs establish the stack and constraints; scale and SLO targets are explicitly unchanged; extension baselines are disabled; and the runtime verification limit is known. There are no unresolved pattern or component choices and no blank `[Answer]:` tags.

## Design Checklist

- [x] Translate UTC, replay safety, additive compatibility, fail-fast validation, and performance constraints into patterns.
- [x] Define the responsibilities of existing logical components and the schema-migration boundary.
- [x] Document resilience, scalability, performance, security, and runtime-verification limits.
- [x] Validate no job, checkpoint, CDF mode, ordering, quarantine, or deployment change is introduced.
- [x] Generate `nfr-design-patterns.md`.
- [x] Generate `logical-components.md`.

## Outputs

NFR Design artifacts are under `aidlc-docs/construction/u4-p1-layer-timestamp-metadata/nfr-design/`. They are submitted for review before Code Generation planning.
