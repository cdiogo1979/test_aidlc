# P1 Streaming Lookback Requirements

## Intent Analysis

- **User request**: Add a day-based widget to both P1 bronze and silver notebooks so an operator can replay Kafka and bronze Change Data Feed history from a selected point in time.
- **Request type**: Enhancement to existing Databricks streaming notebooks.
- **Scope estimate**: Two notebooks, their checkpoints, the two corresponding P1 job-task parameters, and workflow/deployment documentation.
- **Complexity estimate**: Moderate, because a rewind changes Structured Streaming checkpoint state and relies on source retention.

## Functional Requirements

1. Both notebooks expose an integer lookback widget with visible label `Lookback days`. Bronze uses parameter key `bronze_lookback_days`; silver uses `silver_lookback_days`. Both default to `0`; negative values are rejected.
2. With `lookback_days = 0`, each notebook uses its existing checkpoint and resumes normally. A first-ever run retains the notebook's established initial-source behavior.
3. With `lookback_days > 0`, the notebook resets its own existing checkpoint and begins a new replay from the computed cutoff. Afterward, a run with `lookback_days = 0` resumes from the checkpoint advanced by that replay.
4. Bronze computes the cutoff relative to the Kafka record timestamp. Silver computes it relative to the bronze Delta CDF commit timestamp.
5. The widgets are independent. An operator may set matching values for an end-to-end replay or use different values to replay one layer independently.
6. If the requested cutoff predates retained source history, processing starts at the earliest source history still available and reports that the effective replay window is shorter than requested.
7. Reset/replay output remains idempotent under the existing bronze Kafka identity merge, silver latest-event merge, and quarantine identity merge.
8. The P1 job exposes independent `bronze_lookback_days` and `silver_lookback_days` parameters, with both defaulting to `0`, while retaining the existing job-level `environment` parameter.
9. The Deploy handoff must explain the widget parameter and replay behavior, including the order for replaying both layers and the source-history retention limitation.

## Non-Functional Requirements and Constraints

- Log the requested lookback and effective cutoff for each notebook run so operators can distinguish the requested window from the retained window.
- Validate the widget as a non-negative integer before deleting or replacing any checkpoint data.
- Do not claim Databricks runtime behavior is verified without access to a Databricks environment.
- Security baseline: disabled by user choice for this request.
- Property-based testing extension: disabled by user choice for this request.
- Resiliency baseline: disabled by user choice for this request.

## Clarified Decisions

- `0` means checkpoint continuation; a positive number intentionally resets that notebook's checkpoint and replays.
- Bronze uses Kafka record timestamps; Silver uses Delta CDF commit timestamps.
- Each notebook owns an independent lookback widget, displayed as `Lookback days`; the P1 job uses separate parameter keys for the bronze and silver tasks.
- If history is no longer retained, replay begins at the earliest available history and reports the shortened window.

## Approval Status

Requirements were approved by the user with “Approve & Continue” on 2026-09-25. During approved Code Generation planning, the job parameter keys were made layer-specific to preserve independent overrides with the existing Bundle parameter structure; both notebook widgets retain the same visible label.
