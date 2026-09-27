# P1 Streaming Lookback NFR Questions

Please answer each question after its `[Answer]:` tag. These choices set safeguards and observability for potentially large replays.

## Question 1 — Lookback limit
What is the maximum permitted lookback?

A) Do not add a configured day-count maximum; source retention bounds the replay. Log the requested cutoff and observed start so a larger replay is visible. (Recommended)

B) Add a fixed maximum day count. Specify the maximum after selecting this option.

C) Add an environment-specific maximum to configuration. Provide the desired setting/value after selecting this option.

D) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 2 — Replay throughput
How should the notebooks handle the extra processing volume from a large replay?

A) Keep the existing `AvailableNow` processing behavior and do not add new per-trigger rate limits; replay duration and compute usage may increase with the source range. (Recommended)

B) Add configurable per-trigger limits for Kafka offsets and Delta files; provide desired values or configuration names after selecting this option.

C) Require replays to be run in a designated maintenance window, while retaining existing throughput settings.

D) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 3 — Run visibility
Where should the requested and observed replay window be reported?

A) Emit a concise structured summary to the Databricks task logs, including requested days/cutoff, first observed source timestamp, and whether no source records were observed. (Recommended)

B) Also persist replay summaries to a Delta operations/audit table for querying across runs.

C) Other (please describe after [Answer]: tag below)

[Answer]: A
