# U3 P1 Integration — NFR Requirements Plan

## Unit context

- **Unit**: U3 — P1 Integration.
- **Scope**: One daily Databricks job integrating U1 Bronze Ingestion and U2 Silver Processing and Quarantine.
- **Functional design**: One environment value is passed to both tasks; U2 starts only after U1 succeeds; task failures fail the overall job.
- **Dependencies**: U1 and U2 notebooks and their durable streaming checkpoints; `configs/{environment}.yaml`; existing Databricks workspace and access controls.
- **Requirements**: FR-01, FR-03, FR-08, plus shared P1 security and reliability requirements.
- **Technology constraint**: Databricks job under `jobs/P1/`, with Python notebook tasks; Declarative Automation Bundle packaging was selected during U3 Code Generation clarification.

## Inherited NFR decisions

The following are already established by approved project/U1/U2 NFR decisions and will be carried into U3 without reopening them:

- No numeric daily volume, completion deadline, uptime, or recovery-time target was supplied.
- Task failures must remain visible; retries follow the deployment-configured policy and durable task checkpoints.
- The job and notebooks use existing Databricks access controls. Secrets are not job parameters or checked-in values.
- Databricks job/task status and logs provide initial operational visibility; no custom monitoring, recipients, or thresholds were requested.
- Retention and recovery horizons follow platform policy and must not undermine the U1/U2 checkpoint and CDF contracts.
- Databricks is the approved platform; no alternative job orchestration technology is in scope.
- User-interface usability requirements do not apply to this backend integration unit.

## Assessment checklist

- [x] Review U3 Functional Design and inherited U1/U2 NFR decisions.
- [x] Assess scalability and performance targets; none were supplied for P1.
- [x] Assess availability and failure visibility; inherit approved task/job failure behavior.
- [x] Assess reliability, recovery, and observability; inherit U1/U2 checkpoint, retention, retry, and Databricks status/log decisions.
- [x] Assess security, access, and secret handling; inherit approved Databricks controls and secret-reference rules.
- [x] Assess maintainability; use the approved repository paths and existing notebook/job interfaces.
- [x] Assess usability; N/A because U3 is a backend job with no user interface.
- [x] Assess technology selection; Databricks job and notebook tasks are fixed by approved design, with Bundle YAML packaging selected during Code Generation clarification.
- [x] Resolve whether overlapping runs are prevented and whether a new trigger is queued or skipped; user selected one active run with queueing enabled.
- [x] Generate U3 NFR requirements and technology decision artifacts.
- [x] Validate requirements against FR-01, FR-03, FR-08, and the U1/U2 checkpoint contracts.

## Resolved concurrency decision

The user selected A in `u3-p1-integration-nfr-requirements-questions.md`: allow at most one active run and enable queueing for later scheduled or manual triggers. This prevents concurrent use of shared streaming checkpoints. Databricks queueing retains a queued run for up to 48 hours; a later successful run can resume via checkpoints, subject to the U1/U2 source retention contracts.

## Stage status

- [x] NFR Requirements generated and validated.
- [x] User approved the NFR Requirements on 2026-09-24; approval is recorded in `aidlc-docs/audit.md`.

## Deferred deployment details

Exact schedule time/timezone, compute configuration, identity grants, retry counts/delays, and notification settings remain for Infrastructure Design or deployment policy. This NFR assessment does not invent values for those settings.
