# U2 Code Generation Clarification — Bronze Progress Tracking

## Question 1 — Identifying the daily bronze increment

The approved NFR design says U2 processes the daily bronze increment. The bronze table has no ingestion-time field, and silver/quarantine do not retain every processed valid source identity: silver keeps only the current event per `event_key`, while quarantine contains invalid events. Therefore those two outputs cannot reliably identify all valid source records already processed.

How should U2 find records to process on each daily run?

A) Add a small Delta progress table keyed by `(topic, partition)` that stores the last fully processed offset. Select newer bronze offsets, write silver and quarantine, then advance progress only after both outputs succeed. A failed output or progress update leaves the task failed; replay is safe through idempotent writes. This adds a persistent U2 control table (Recommended for daily incremental processing).

B) Reprocess the full bronze table on each run. This avoids a control table but work grows with retained history; latest-event ordering and output idempotency preserve results.

X) Other (please describe after `[Answer]:`)

[Answer]: X - using delta cdc from the bronze table
