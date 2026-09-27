# AI-DLC Deploy Stage Requirements

## Problem

Active workflow artifacts currently sit directly beside canonical knowledge and archived history under `aidlc-docs/`. This mixes documents with different lifecycles. The workflow also ends Build and Test with a placeholder Operations stage and does not reliably prepare a pull request description or an ordered release handoff.

## Solution

Replace the final Operations placeholder with an always-executed Deploy handoff stage after Build and Test. Preserve artifact compaction and intent closure as a separate lifecycle action after the Deploy handoff is approved.

## Requirements

1. Every intent's Deploy stage generates `aidlc-docs/current/deploy/pr_request.md` with the problem, solution, main changes, verification status, deployment summary, and material risks/limitations.
2. Generate `aidlc-docs/current/deploy/deploy_instructions.md` only when deployment or operational steps are required.
3. When present, deployment instructions list environment actions in dependency order, including assets, `ops/` migration/patch notebooks, `deploy/` asset notebooks, prerequisites, parameters, validation, and failure/rollback guidance where known.
4. Unknown details are identified as inputs or blockers; no environment values, execution order, verification results, or rollback behavior are invented.
5. The Deploy stage prepares documentation only. It never creates a PR, deploys assets, or executes notebooks. Handoff approval is not execution authorization.
6. Accepted verification waivers and unverified scope remain explicit and prominent. A waiver is not a passed verification, release approval, or production-readiness claim.
7. Handoff artifacts are included in intent archives and are eligible for cleanup only after archival.
8. Keep active intent documents, state, audit, and active compaction manifests under `aidlc-docs/current/`, separate from `aidlc-docs/knowledge/` and `aidlc-docs/archive/`.

## Scope

Update the shared AI-DLC skill and its planning, stage-gate, terminology, overview, welcome, and compaction references; update the compaction utility's workflow paths; document the new Deploy handoff and folder convention in canonical/project guidance. Do not execute a deployment or create a pull request.
