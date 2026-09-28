# Execution Plan: Canonical Knowledge Impact in AI-DLC Planning

**Intent**: `20260927-aidlc-knowledge-impact-planning`
**Project type**: Brownfield workflow/documentation change
**Risk**: Low; active canonical docs and workflow instructions change, while archived records remain immutable.

## Analysis: Planning Gap

The workflow has a canonical-knowledge convention and asks Functional Design to read existing canonical designs, but its Workflow Planning instructions do not require loading those documents or listing their impacts in the approval plan. Unit Generation can therefore define a new unit before checking whether existing component contracts should be revised. Functional Design and compaction rules act too late to prevent a cross-cutting change from being promoted as a new canonical component.

In the P1 timestamp intent, timestamp writes were owned by existing U1 bronze and U2 silver processing. The resulting canonical U1/U2 documents already contain much of that behavior, while a standalone U4 canonical design and U4 component entry duplicate the responsibility. U3's job sequencing stayed unchanged but its canonical integration design was not explicitly reconciled. The older U4 archive remains valid history and will not be edited.

## Canonical Knowledge Impact Inventory

| Canonical document | Planned action | Reason |
|---|---|---|
| `aidlc-docs/knowledge/P1/application-design.md` | UPDATE | Remove U4 as a component; assign timestamp write/schema responsibilities to U1 and U2; state orchestration stays in U3. |
| `aidlc-docs/knowledge/P1/functional-design/U1-bronze-ingestion.md` | UPDATE | Consolidate the full bronze timestamp acceptance, nullable migration, and replay/no-op rules under the component that writes bronze. |
| `aidlc-docs/knowledge/P1/functional-design/U2-silver-processing-and-quarantine.md` | UPDATE | Consolidate silver timestamp acceptance, migration, winner/no-op, and quarantine boundaries under the component that writes silver. |
| `aidlc-docs/knowledge/P1/functional-design/U3-p1-integration.md` | UPDATE | Record that U1/U2 own their respective layer timestamps and U3 task order/parameters remain unchanged; no new job task is introduced. |
| `aidlc-docs/knowledge/P1/functional-design/U4-p1-layer-timestamp-metadata.md` | RETIRE | It represents cross-cutting implementation work as a standalone component. Preserve its source history in the immutable U4 archive; remove only the current canonical file. |
| `aidlc-docs/knowledge/p1-databricks-workload.md` | UPDATE | Remove U4 from the canonical-document index and summarize timestamp behavior under U1/U2. |
| `aidlc-docs/knowledge/P2/**` | RETAIN | P2 component boundaries and designs are unaffected by this process correction. |
| `aidlc-docs/archive/20260924-p1-layer-timestamp-columns/**` | RETAIN | Immutable evidence of the prior approved intent; never rewrite historical artifacts. |
| `.agents/skills/aidlc-workflows/SKILL.md` | UPDATE | Require loading and approving the knowledge-impact inventory before implementation planning proceeds. |
| `.agents/skills/aidlc-workflows/references/inception/workflow-planning.md` | UPDATE | Add mandatory inventory and a template table that classifies each relevant knowledge document. |
| `.agents/skills/aidlc-workflows/references/inception/units-generation.md` | UPDATE | Map requirements/work items to existing components and canonical paths before defining units; distinguish coordination tasks from components. |
| `.agents/skills/aidlc-workflows/references/construction/functional-design.md` | UPDATE | Require updating an existing component design when its behavior changes; justify a new component boundary before creating a new canonical design. |
| `aidlc-docs/knowledge/aidlc-intent-lifecycle.md` | UPDATE | Align durable workflow knowledge with the new plan-time inventory and mapping requirements. |

## Planned Workflow

### Inception
- [x] Workspace detection and targeted reverse engineering of workflow instructions and canonical P1/P2 docs.
- [x] Requirements analysis for the planning-rule and P1 knowledge correction.
- [x] Workflow Planning review and approval (approved by user).
- [x] Application Design — SKIP; no runtime component or system architecture is introduced.
- [x] Units Generation — SKIP; the implementation changes workflow guidance and updates existing canonical docs only.

### Construction
- [x] Update the AI-DLC entrypoint, workflow-planning, units-generation, functional-design instructions, and lifecycle knowledge reference.
- [x] Update P1 application design, U1/U2/U3 functional designs, and P1 workload index/summary; retire the canonical U4 file.
- [x] Validate links, component naming, timestamp ownership, and archived-history immutability; review the final diff. `git diff --check` passed and targeted references were reviewed.

### Deploy
- [x] Prepare a PR request for the workflow and canonical-document changes. No runtime deployment instructions are needed.

## Success Criteria
- New plans must show which canonical documents will be updated before the plan can be approved.
- Existing component designs are the default destination for changes to their responsibilities; a new component requires a separately justified boundary.
- P1 current canonical knowledge reflects U1/U2 ownership and U3 orchestration, with no standalone U4 canonical functional design.
- Archived P1 and P2 intent records remain unchanged.
