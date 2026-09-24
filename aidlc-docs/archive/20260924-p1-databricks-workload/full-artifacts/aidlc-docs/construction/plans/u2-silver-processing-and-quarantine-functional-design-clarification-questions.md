# U2 Silver Processing and Quarantine — Functional Design Clarification

## Ambiguity — Silver event columns

For Question 1 in `u2-silver-processing-and-quarantine-functional-design-plan.md`, you selected A, which calls for a representative JSON message. No sample was included, and no payload example is present in the project requirements or design artifacts. Without an example, the event-specific silver columns and extensible representation cannot be defined without making up fields.

How should we resolve the missing payload example?

A) Paste a representative production JSON event after `[Answer]:` (Recommended; this lets the design name the actual fields and types while preserving your permissive type-validation and extensible-field decisions).

B) No representative event is available; define silver with `event_key` plus an extensible map for all other JSON properties, preserving parsed value types and validating JSON syntax only.

X) Other (please describe after `[Answer]:`)

[Answer]: B
