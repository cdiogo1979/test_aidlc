# Requirements Clarification Questions

Please answer each item after its `[Answer]:` tag. For open-ended answers, provide a short description. For extension questions, select an option or describe another preference.

## Question 1 — Subproject identity
What name should be used for this first subproject under `notebooks/` and `jobs/` (for example, `P1`)?

[Answer]: P1

## Question 2 — Workload goal
What business or data problem should the Databricks workload solve? Describe the desired outcome and who or what will consume it.

[Answer]: ingest a kafka topic events to bronze and then considate events by key in silver table

## Question 3 — Source data and ingestion
What are the source system(s), data location(s), formats, and expected ingestion mode (batch, streaming, or other)? Include any known volume or cadence.

[Answer]: kafka topic

## Question 4 — Data transformations and outputs
What should be stored or produced at the bronze, silver, and gold layers? Include important business rules, target tables/locations, and expected consumers where known.

[Answer]: bronze 1:1  from source, silver expand message payload and merge by key 

## Question 5 — Job execution
Should this workload run as a Databricks job? If yes, describe the desired trigger or schedule, dependencies, and failure/notification expectations if known.

[Answer]: yes , once a day 

## Question 6 — Environments and constraints
Which environments must be supported, and are there known security, privacy, performance, retention, or compliance requirements? The current `configs/prod.yaml` contains `database: test_prod` and `data_path: s3://test_prod`; clarify whether these are placeholders or intended production values.

[Answer]: you can use this values

## Question 7 — Security Baseline extension
Should security extension rules be enforced as blocking constraints?

A) Yes — enforce the security baseline (recommended for production-grade workloads)

B) No — skip the security baseline

X) Other (please describe after `[Answer]:`)

[Answer]: B

## Question 8 — Property-Based Testing extension
Should property-based testing rules be enforced for this project?

A) Yes — enforce the full property-based testing rules

B) Partial — enforce them for pure functions and serialization round-trips

C) No — skip property-based testing rules

X) Other (please describe after `[Answer]:`)

[Answer]: C

## Question 9 — Resiliency Baseline extension
Should the resiliency baseline be applied as directional, design-time guidance?

A) Yes — apply resiliency guidance (recommended for business-critical workloads)

B) No — skip the resiliency baseline

X) Other (please describe after `[Answer]:`)

[Answer]: B
