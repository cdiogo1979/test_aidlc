# Requirements Follow-up Questions

The initial answers define the workload at a high level. Please answer the remaining implementation questions below. If a detail is not decided yet, write `TBD` and I will record a reasonable assumption for review.

## Question 1 — Kafka access
What Kafka bootstrap servers and topic should P1 use, and how should it authenticate? Provide secret references or configuration key names only; do not put secret values in this file.

[Answer]: use the kafka config for the servers , topic name is "my-topic"

## Question 2 — Daily ingestion behavior
For the once-daily job, should each run process only newly available Kafka records and retain offsets/checkpoints across runs? What should happen if a run fails and is retried?

[Answer]: yes , incremental load

## Question 3 — Event key and silver merge
Which field is the consolidation key, what does “merge by key” mean (for example, keep the latest event per key or maintain one current-state row), and how should event ordering be determined?

[Answer]: event_key

## Question 4 — Payload and table targets
What is the message payload format/schema, and what bronze and silver table names should be created? Should P1 create a gold-layer output now, or leave gold unused until a consumer is defined?

[Answer]: p1_test_kfk_brz and p1_test . no gold layer 

## Question 5 — Data scale and operational expectations
What are the approximate daily event volume and acceptable processing window? How should malformed messages be handled (fail the run, quarantine them, or another approach)?

[Answer]: quarantine messages
