# Unit of Work Plan — P1 Layer Timestamp Columns

## Purpose

Decompose the approved timestamp change across the existing P1 bronze and silver components. The approved execution plan calls for one coordinated cross-layer unit because the bronze-to-silver data contract changes, while preserving the existing daily job and deployment boundary.

## Existing Design Context

Application Design was skipped in the approved execution plan because this change introduces no component, service, or method boundary. Units Generation requires application-design context; the previously approved P1 application and unit design is therefore reused from:

- `aidlc-docs/archive/20260924-p1-databricks-workload/full-artifacts/aidlc-docs/inception/application-design/application-design.md`
- `aidlc-docs/archive/20260924-p1-databricks-workload/full-artifacts/aidlc-docs/inception/application-design/unit-of-work.md`
- `aidlc-docs/archive/20260924-p1-databricks-workload/full-artifacts/aidlc-docs/inception/application-design/unit-of-work-dependency.md`
- `aidlc-docs/archive/20260924-p1-databricks-workload/full-artifacts/aidlc-docs/inception/application-design/unit-of-work-story-map.md`

That design identifies the bronze ingestion notebook, silver processing notebook, and P1 daily job. They remain the applicable ownership and deployment context. This intent does not change the job or introduce a separately deployable unit.

## Proposed Unit

### U4 — P1 Layer Timestamp Metadata

- **Objective**: Add distinct, replay-safe UTC processing-time columns to the existing bronze and silver Delta write paths, including additive nullable schema migration for existing tables.
- **Scope**: `notebooks/P1/bronze/bronze_ingestion.py`, `notebooks/P1/silver/silver_processing.py`, and focused local tests where practical.
- **Bronze responsibility**: Add and populate `bronze_ingestion_timestamp` on first insert only; preserve it on duplicate/replayed identities.
- **Silver responsibility**: Add and populate `silver_processing_timestamp` on valid inserts and winning latest-event updates only; preserve it for no-op replays and losing older events.
- **Data contract**: Silver continues consuming bronze through the existing Delta/CDF path. The bronze migration and emitted field must be in place before silver reads the updated contract.
- **Explicit exclusions**: No job, checkpoint, CDF mode, latest-event ordering, quarantine behavior, source timestamp, or live table deployment change.
- **Delivery boundary**: U4 is one coordinated planning and implementation unit within the existing P1 workload, not a separate service or deployment.

## Decomposition Question Assessment

The required categories were reviewed against the approved requirements, execution plan, and archived P1 design:

- **Story grouping**: User Stories were explicitly skipped in the approved execution plan because this is an internal schema and processing-time change without a user workflow. The two requirements map together because they change one cross-layer persisted data contract; no story-based grouping choice is unresolved.
- **Dependencies**: The bronze-to-silver dependency is established in the existing design. U4 implements bronze schema/write behavior before silver consumes the new bronze contract. The existing job ordering remains unchanged.
- **Team alignment**: Reuse the existing single P1 ownership context. No new ownership boundary is introduced by this request.
- **Technical considerations**: Requirements explicitly retain the current daily job and deployment. No independent release, schedule, or scaling boundary was requested.
- **Business domain**: The change remains within the existing P1 event data workload; no new domain boundary is introduced.
- **Code organization**: Preserve the existing project layout under `notebooks/P1/bronze/`, `notebooks/P1/silver/`, and the established test location. This is a brownfield change, so no greenfield organization decision is needed.

No clarification questions are needed: the number of units, responsibilities, dependency order, deployment boundary, and source locations follow directly from the approved requirements and execution plan plus the existing P1 design. There are no unanswered `[Answer]:` tags.

## Plan Checklist

- [x] Generate `aidlc-docs/inception/application-design/unit-of-work.md` with U4's definition and responsibilities, preserving the existing P1 deployment context.
- [x] Generate `aidlc-docs/inception/application-design/unit-of-work-dependency.md` with the bronze-before-silver contract dependency.
- [x] Generate `aidlc-docs/inception/application-design/unit-of-work-story-map.md` mapping approved requirements to U4 and recording that User Stories were skipped.
- [x] Validate the unit boundary, dependency, requirement coverage, and relationship to the existing P1 units.
- [x] Update `aidlc-docs/aidlc-state.md` with Units Generation completion and the next approved stage.

## Generation Outputs

After this plan is approved, generate the three mandatory unit artifacts under `aidlc-docs/inception/application-design/`. Existing U1–U3 definitions and their prior story mappings will be preserved as historical P1 context; this new intent adds U4 and maps FR-01 through FR-09 to it. The current intent has no new user stories to assign.

Part 2 generation began after the user's explicit approval. Generated unit artifacts now await review and approval before Construction.
