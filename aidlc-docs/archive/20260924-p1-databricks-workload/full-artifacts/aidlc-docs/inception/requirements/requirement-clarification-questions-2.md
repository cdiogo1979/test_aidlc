# Requirements Clarification — Follow-up 2

Please answer below. If a detail is undecided, write `TBD` and I will capture an explicit assumption in the requirements for review.

## Question 1 — Kafka configuration
You said to use the Kafka server configuration, but the repository currently contains only `configs/prod.yaml` with `database` and `data_path`. Where is the Kafka configuration, or which non-secret Kafka settings should be added to `configs/prod.yaml`? Include authentication secret reference/key names only, never secret values.

[Answer]: secrets i will be done by using the databricks secret "my-secret". the host is on kafka.hosts 

## Question 2 — Table mapping and message format
Should `p1_test_kfk_brz` be the bronze table and `p1_test` the silver table? What is the Kafka message payload format and schema (for example, JSON with field names/types)?

[Answer]: table mappng is correct , is the payload is json

## Question 3 — Silver consolidation semantics
For each `event_key`, should silver keep the latest event as the current row, or apply another rule? If latest wins, which payload field identifies event order (for example, event timestamp or Kafka offset)?

[Answer]: latest event

## Question 4 — Quarantine and job recovery
Where should malformed messages be quarantined (table/path), and should the daily job retry failed runs from the last successfully processed Kafka offsets? If the volume or processing window is not known, answer `TBD`.

[Answer]: TBD
