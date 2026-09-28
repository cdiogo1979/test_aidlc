# Requirements: Canonical Knowledge Impact in AI-DLC Planning

## User Need
AI-DLC planning must analyze which canonical knowledge documents need updates and include that inventory in the reviewed plan. Existing component designs should be updated when a change modifies behavior owned by those components. A cross-cutting change should not automatically become a new component or standalone functional-design document.

## Functional Requirements
1. During Workflow Planning, read relevant canonical application and functional-design knowledge alongside requirements and reverse-engineering context.
2. Add a reviewed knowledge-impact inventory to the execution plan. For each relevant canonical document, classify it as UPDATE, RETAIN, CREATE, or RETIRE, give a reason, and identify the requirement/component it supports.
3. Map each affected requirement and work item to an existing component and its canonical functional-design document before creating new units.
4. Create a new component/unit functional design only when analysis establishes a distinct functional responsibility or component boundary; a cross-cutting implementation task alone is not sufficient.
5. During Functional Design and intent closure, update existing affected component designs and reconcile their architecture/index references. Preserve old intent archives as immutable history.
6. Correct P1 canonical knowledge by distributing layer timestamp behavior into U1 and U2, recording U3 orchestration impact/unchanged behavior, and retiring the separate canonical U4 timestamp design. Keep the archived U4 intent intact.

## Acceptance Criteria
- The Workflow Planning instructions require the canonical-knowledge impact inventory before approval.
- Unit Generation and Functional Design instructions carry the mapping forward and guard against creating a new canonical design for work owned by existing components.
- The reviewed plan lists exact P1 canonical docs to update/retain/retire.
- P1 canonical design index and architecture contain U1-U3 only; U1/U2 retain their layer timestamp contracts; U3 describes the unchanged job boundary; no canonical U4 design remains.
- Archived P1 intent history is unchanged.
