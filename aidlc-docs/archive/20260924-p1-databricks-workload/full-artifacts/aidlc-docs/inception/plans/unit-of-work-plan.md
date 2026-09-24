# P1 Unit of Work Plan

## Purpose

Decompose the approved P1 workload into development units that align with its stories, components, and shared daily Databricks deployment. The units are planning boundaries; the approved application design remains one job with sequential bronze and silver notebook tasks.

## Candidate unit boundaries

The current proposal is:

1. **Bronze Ingestion** — Kafka access, incremental reads, and bronze Delta persistence.
2. **Silver Processing** — JSON expansion, current-state merge, and malformed-message quarantine.
3. **P1 Integration** — daily Databricks Bundle job, environment configuration, task dependencies, and cross-unit validation.

The answers below will confirm or change this decomposition.

## Category assessment

- **Story grouping**: Relevant. Both stories serve one downstream data engineer in the `P1 event data` domain, but describe separate consumer outcomes. Ask how to cluster the supporting implementation work.
- **Dependencies**: Known at application-design level. Silver reads the persisted bronze Delta table; the job runs bronze before silver. Plan these as explicit unit dependencies; no new integration mechanism is needed.
- **Team alignment**: Not specified. Ask whether one P1 team or separate owners will develop the units.
- **Technical considerations**: No separate scaling or deployment needs are documented. Ask whether any unit must be released or scaled independently.
- **Business domain**: Already established as the neutral `P1 event data` domain; no further domain split is currently indicated.
- **Code organization**: Existing project guidance already defines `notebooks/P1/{bronze,silver,gold}/`, `jobs/P1/`, and `configs/`. Preserve this layout; no alternate directory structure is proposed.

## Planning checklist

- [x] Confirm the number and responsibilities of units.
- [x] Confirm team ownership and any independent scaling/deployment needs.
- [x] Map stories and requirements to units.
- [x] Establish unit dependency order and shared Delta/configuration contracts.
- [x] Document greenfield code organization using the repository's established folders.
- [x] Generate `aidlc-docs/inception/application-design/unit-of-work.md`.
- [x] Generate `aidlc-docs/inception/application-design/unit-of-work-dependency.md`.
- [x] Generate `aidlc-docs/inception/application-design/unit-of-work-story-map.md`.
- [x] Validate unit boundaries, dependencies, and complete story coverage.

## Questions

### Question 1 — Unit grouping
Which decomposition should be used?

A) Three units: Bronze Ingestion; Silver Processing and Quarantine; P1 Integration for job, configuration, and cross-unit validation (Recommended; matches the approved components and execution plan)

B) One end-to-end P1 unit with bronze and silver as internal modules

C) Two units: Bronze Ingestion; Silver Processing with job/configuration integration

X) Other (please describe after `[Answer]:`)

[Answer]: A

### Question 2 — Team ownership
How will development ownership be organized?

A) One P1 team owns all units (Recommended for the currently defined single workload)

B) Separate teams own ingestion and silver/data processing

X) Other (please describe after `[Answer]:`)

[Answer]: A

### Question 3 — Independent deployment or scaling
Do any units need different release boundaries, schedules, or scaling from the single daily P1 job in the approved design?

A) No — develop the units as one P1 deployment with the approved daily job (Recommended; consistent with Application Design)

B) Yes — specify which unit needs an independent schedule, deployment, or scaling policy

X) Other (please describe after `[Answer]:`)

[Answer]:A

## Confirmed decomposition

The selected plan has three units owned by one P1 team and developed for one shared daily P1 deployment. Units are work boundaries, not separately deployable jobs.

| Unit | Responsibility | Requirements | Story relationship |
|---|---|---|---|
| U1 — Bronze Ingestion | Read incremental Kafka events and write source payload plus Kafka metadata to bronze. | FR-02, FR-03, FR-04 | Supports US-P1-01 and US-P1-02 by providing persisted source events. |
| U2 — Silver Processing and Quarantine | Parse JSON, maintain latest current row per `event_key`, and quarantine malformed messages. | FR-05, FR-06, FR-07 | Primary implementation unit for US-P1-01 and US-P1-02. |
| U3 — P1 Integration | Provide the daily Declarative Automation Bundle job, environment configuration, bronze-before-silver dependencies, and cross-unit validation. | FR-01, FR-03, FR-08 | Integrates the units that deliver US-P1-01 and US-P1-02. |

## Dependency and organization decisions

- U2 reads the bronze Delta table produced by U1; the bronze table is the inter-unit data contract.
- U3 integrates U1 and U2 in one daily Databricks job; its runtime task order is U1 then U2.
- All units are owned by one P1 team and released together. No separate schedules or scaling policies are required.
- Preserve `notebooks/P1/bronze/`, `notebooks/P1/silver/`, `notebooks/P1/gold/` (empty for this scope), `jobs/P1/`, and `configs/`.
- No independent services or separately deployable packages are introduced.

## Generation outputs after plan approval

- `unit-of-work.md`: unit definitions, responsibilities, dependencies, and the greenfield code organization strategy.
- `unit-of-work-dependency.md`: dependency matrix and execution order.
- `unit-of-work-story-map.md`: mapping of every approved story and relevant requirement to one or more units.

Part 2 generation begins only after the answers are complete, ambiguities are resolved, and the user explicitly approves this plan.
