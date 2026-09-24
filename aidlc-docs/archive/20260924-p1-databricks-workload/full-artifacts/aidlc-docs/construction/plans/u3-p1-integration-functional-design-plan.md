# U3 P1 Integration — Functional Design Plan

## Unit context

- **Unit**: U3 — P1 Integration.
- **Purpose**: Assemble the approved U1 and U2 notebook interfaces into one daily P1 workload.
- **Responsibilities**: Define the job's task sequence, pass a common environment name to both tasks, and report the overall run result.
- **Dependencies**: U1 bronze ingestion notebook; U2 silver processing notebook; `configs/{environment}.yaml`.
- **Requirements**: FR-01, FR-03, FR-08.
- **Stories supported**: US-P1-01 and US-P1-02 by running the full bronze-to-silver workflow.
- **Code location**: Job definition under `jobs/P1/`; configuration remains under `configs/`.
- **Approved application contract**: One daily job, U1 first, U2 only after U1 succeeds, same environment parameter for both tasks, and persisted bronze Delta as the unit boundary.

## Clarification assessment

The approved application design and the U1/U2 functional contracts determine U3's business orchestration. No unresolved functional choices were found. Exact schedule time/timezone, job compute, retries, identity grants, and notifications are deployment or Infrastructure Design details and are deferred to those stages.

## Functional design checklist

- [x] Define the P1 integration run and its environment input.
- [x] Specify the U1-to-U2 task dependency and success/failure behavior.
- [x] Specify the shared environment configuration contract.
- [x] Confirm the persisted bronze Delta table is the task handoff; no in-memory data passing.
- [x] Preserve the approved daily cadence and exclude gold-layer work.
- [x] Generate U3 business logic, business rules, and domain entity artifacts.
- [x] Validate coverage against FR-01, FR-03, FR-08, US-P1-01, US-P1-02, and U1/U2 contracts.

## Deferred decisions

Infrastructure Design records the deployment schedule time/timezone, compute selection, access grants, retry policy, and notification configuration. Code Generation creates the P1 Declarative Automation Bundle job under `jobs/P1/` and updates configuration only if the approved designs require it.
