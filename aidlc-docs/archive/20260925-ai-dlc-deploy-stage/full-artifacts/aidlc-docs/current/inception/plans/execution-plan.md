# Execution Plan: AI-DLC Deploy Handoff Stage

## Approved scope

Replace the placeholder Operations phase/stage with a Deploy phase/stage that prepares a PR request and conditional ordered deployment instructions. Keep compaction/closure separate. “Proceed” approved implementation of the analyzed change.

## Plan

- [x] Requirements — recorded in `aidlc-docs/current/inception/requirements/requirements.md`.
- [x] Workflow design — define the stage boundary, required/conditional artifacts, review gate, waiver language, and deployment authorization boundary.
- [x] Update the skill, Deploy rules, planning templates, overview, welcome, terminology, and Build and Test gate.
- [x] Update compaction validation and default context selection to include `aidlc-docs/current/deploy/`.
- [x] Group active workflow documents, state, audit, and active manifests under `aidlc-docs/current/`; update all path consumers and project guidance.
- [x] Update canonical lifecycle guidance and correct the stale historical P1 handoff.
- [x] Review consistency for obsolete Operations-phase/stage references and check state/audit tracking.

## Verification approach

Perform a static consistency review of workflow references, path rules, required artifact semantics, and state/audit records. Do not deploy assets, execute notebooks, or create a PR. Automated tests are not part of this requested documentation/workflow review.

## Success criteria

- Build and Test clearly leads to Deploy, then separately to compaction/closure.
- Every intent produces `pr_request.md`; deployment instructions are conditional and ordered when needed.
- Documents clearly state the execution/authorization boundary and preserve waived verification limitations.
- Compaction can load, archive, and clean Deploy handoff artifacts only after archiving.
- Active workflow documents are separate from `knowledge/` and `archive/`; archived history is unchanged.

## Review status

Static review found no obsolete root-level active-document paths outside the historical active audit entry. Shared workflow rules, project guidance, script constants, and compaction fixtures use `aidlc-docs/current/`; knowledge and archive paths remain distinct. The compaction utility includes current stage Markdown, the audit, and active manifest JSON in context, and permits cleanup only under workflow directories inside `current/`. Existing archived snapshots were left untouched. Automated tests were not run.
