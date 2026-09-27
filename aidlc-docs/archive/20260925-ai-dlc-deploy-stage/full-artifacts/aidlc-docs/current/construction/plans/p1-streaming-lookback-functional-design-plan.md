# Functional Design Plan: P1 Streaming Lookback

## Unit

`p1-streaming-lookback` — add operator-selected replay windows to the existing P1 bronze and silver streaming tasks.

## Design Steps

- [x] Confirm the user-approved requirements and timestamp basis for both sources.
- [x] Model the normal checkpoint-resume and positive-lookback replay paths.
- [x] Define validation and checkpoint reset ordering so invalid parameters or unmet prerequisites do not remove checkpoint state.
- [x] Define handling and reporting when source retention is shorter than the requested lookback.
- [x] Confirm replay outputs remain idempotent under existing target merge keys.
- [x] Record domain concepts and business rules.

## Clarifications

No additional questions are required. Requirements Analysis resolved lookback semantics, independent controls, timestamp basis, and expired-history behavior.

## Artifacts

- `aidlc-docs/current/construction/p1-streaming-lookback/functional-design/business-logic-model.md`
- `aidlc-docs/current/construction/p1-streaming-lookback/functional-design/business-rules.md`
- `aidlc-docs/current/construction/p1-streaming-lookback/functional-design/domain-entities.md`

## Review Status

Functional design was approved by the user with “Continue to Next Stage” on 2026-09-25. NFR Requirements is now in progress.
