# P1 Streaming Lookback Requirements Questions

Please answer each question using the `[Answer]:` tag. These decisions define what a positive lookback value does to the existing stream checkpoints and source history.

## Question 1 — Lookback behavior
What should the `lookback_days` widget do?

A) `0` continues from the existing checkpoint. A positive number resets that notebook's existing checkpoint and replays from the computed source-time cutoff; after replay, later runs with `0` continue from the newly advanced checkpoint. (Recommended)

B) Always continue from the existing checkpoint; use the widget only to filter records newer than the cutoff. This does not rewind the source or reset checkpoint offsets.

C) Add a separate reset control. `lookback_days` chooses the cutoff, while a second widget explicitly authorizes checkpoint reset.

D) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 2 — Timestamp meaning
Which timestamps should define “N days ago” for each source?

A) Bronze uses the Kafka record timestamp; Silver uses the bronze Delta CDF commit timestamp. Each uses the source's native timestamp to replay the corresponding streaming history. (Recommended)

B) Both use the Kafka record timestamp, including Silver records, and Silver filters replayed CDF changes by the Kafka timestamp stored in bronze.

C) Both use the time the record was first ingested into bronze, including Silver CDF replay.

D) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 3 — Coordination
Should the two notebook widgets share one value or allow separate lookbacks?

A) Give both notebooks an independent `lookback_days` widget. Set the same value when replaying the pipeline end to end, or different values when intentionally replaying one layer only. (Recommended)

B) Use a single job parameter passed to both notebooks so their lookback is always coordinated.

C) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 4 — Source history unavailable
If the requested cutoff is older than the source history still available (Kafka retention or Delta CDF history), what should the notebook do?

A) Fail with a clear error explaining that the requested lookback cannot be met. (Recommended)

B) Start at the earliest source history still available and report that the replay window is shorter than requested.

C) Other (please describe after [Answer]: tag below)

[Answer]: B

## Question: Security Extensions
Should security extension rules be enforced for this project?

A) Yes — enforce all SECURITY rules as blocking constraints (recommended for production-grade applications)

B) No — skip all SECURITY rules (suitable for PoCs, prototypes, and experimental projects)

C) Other (please describe after [Answer]: tag below)

[Answer]: B

## Question: Property-Based Testing Extension
Should property-based testing (PBT) rules be enforced for this project?

A) Yes — enforce all PBT rules as blocking constraints (recommended for projects with business logic, data transformations, serialization, or stateful components)

B) Partial — enforce PBT rules only for pure functions and serialization round-trips (suitable for projects with limited algorithmic complexity)

C) No — skip PBT rules (suitable for simple CRUD applications, UI-only projects, or thin integration layers with no significant business logic)

D) Other (please describe after [Answer]: tag below)

[Answer]: C

## Question: Resiliency Extensions
Should the resiliency baseline be applied to this project?

**What this extension is.** Enabling it applies directional, design-time best practices for building resilient systems. It does not certify or guarantee production readiness, availability, RTO, or RPO.

A) Yes — apply the resiliency baseline as directional best practices and design-time guidance (recommended for business-critical workloads)

B) No — skip the resiliency baseline (suitable for PoCs, prototypes, and experimental projects)

C) Other (please describe after [Answer]: tag below)

[Answer]: B
