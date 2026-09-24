# U2 Silver Processing and Quarantine — NFR Design Plan

## Unit context

- **Unit**: U2 — Silver Processing and Quarantine.
- **Approved NFRs**: Daily processing with no numeric capacity/window target; visible task failure and safe retry/replay; fail on partial silver/quarantine persistence; existing Databricks access controls; job status and task logs; existing retention policies.
- **Fixed logical platform**: Databricks notebook execution, bronze/silver/quarantine Delta tables, environment configuration, and U3 daily orchestration.
- **Functional reliability contract**: Silver and quarantine writes are independently idempotent by `(topic, partition, offset)`; no cross-table transaction or platform-wide exactly-once guarantee is claimed.
- **Scope**: Specify logical resilience, scalability, performance, security, and observability patterns without selecting infrastructure topology or cluster sizing.

## NFR design checklist

- [x] Define failure, retry, and partial-output recovery patterns.
- [x] Define a scale-out and data-processing approach suitable for the daily batch without inventing capacity targets.
- [x] Define performance optimization boundaries in the absence of numeric SLAs.
- [x] Define secure data and diagnostic handling consistent with existing access controls.
- [x] Define the logical components and their responsibilities; confirm whether additional components are needed.
- [x] Generate `nfr-design-patterns.md` and `logical-components.md`.
- [x] Validate the design against approved U2 Functional Design and NFR Requirements.

## Answers applied

Questions 1–5 selected A: independently idempotent output writes with visible task failure and safe replay; use existing distributed daily processing and defer capacity tuning; avoid unmeasured optimization; keep raw payloads out of logs; use only the existing job/notebook/Delta components.

## Question 1 — Resilience and output recovery

The NFR Requirements require U2 to fail if either output write fails and retry safely, while the Functional Design does not claim a transaction across silver and quarantine. Which logical write/recovery pattern should the design specify?

A) Write each output idempotently, fail the task on any write error, and rely on retry to reconcile partial completion; do not promise atomic visibility across the two tables (Recommended; matches the approved NFRs).

B) Require an atomic transaction spanning silver and quarantine; treat inability to provide it as a deployment blocker.

X) Other (please describe after `[Answer]:`)

[Answer]: A

## Question 2 — Scalability pattern

No numeric daily volume or growth target exists. Which scale approach should U2 use?

A) Use the distributed processing capacity of the existing Databricks job and process only the daily bronze increment; defer sizing and tuning until volumes are measured (Recommended).

B) Establish an explicit capacity assumption or scaling trigger now; specify daily volume/growth and the trigger after `[Answer]:`.

X) Other (please describe after `[Answer]:`)

[Answer]:A

## Question 3 — Performance optimization

Without a completion-window SLA or known volume, what optimization policy should be designed?

A) Use bounded daily batch processing and avoid caching, partitioning, or layout tuning without measured evidence; record performance metrics only if they are already available from the platform (Recommended).

B) Add a specific optimization or benchmark target now; describe it after `[Answer]:`.

X) Other (please describe after `[Answer]:`)

[Answer]: A

## Question 4 — Security and diagnostic data

The quarantine table retains raw payloads, while current observability relies on task logs. How should diagnostics handle event data?

A) Keep raw payloads and full parse/validation diagnostics in the access-controlled quarantine table; task logs should contain operational status and non-sensitive counts/source identifiers, not raw payloads (Recommended data-minimization pattern).

B) Include raw payloads in task logs to simplify troubleshooting.

X) Other (please describe after `[Answer]:`)

[Answer]: A

## Question 5 — Logical components

Which logical component set should the NFR design use?

A) Existing Databricks job/notebook plus bronze, silver, and quarantine Delta tables; do not add queues, caches, services, or external monitoring components in this scope (Recommended; matches approved technology boundaries).

B) Add a logical component for retry coordination, alerting, or other operations; describe its responsibility after `[Answer]:`.

X) Other (please describe after `[Answer]:`)

[Answer]: A

## Fixed constraints and applicability

- Security Baseline, Property-Based Testing, and Resiliency Baseline extensions are disabled in `aidlc-state.md`; no extension-specific patterns are required.
- Infrastructure topology and compute sizing belong to the subsequent Infrastructure Design stage.
- Existing access controls and platform protections remain the security baseline; no new policy or compliance framework was specified.
