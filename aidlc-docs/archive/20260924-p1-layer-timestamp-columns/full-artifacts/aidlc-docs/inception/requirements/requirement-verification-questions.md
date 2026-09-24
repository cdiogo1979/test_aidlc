# Requirements Verification Questions — P1 Timestamp Columns

The current P1 code already has Kafka `source_timestamp` in bronze and silver, and quarantine has `ingestion_timestamp`. No Databricks runtime was available during the previous intent, so the tables are defined by notebook code but were not confirmed created in a live workspace. Please answer the following before requirements are finalized.

## Question 1: What should the new timestamp represent?

A) The time a Kafka record is first accepted/written by bronze (ingestion time; recommended)

B) The original event/source time (already represented by `source_timestamp`)

C) The time each layer writes the record (bronze ingestion time and silver processing time are distinct)

X) Other (please describe after `[Answer]:` below)

[Answer]: C

## Question 2: Which timestamp value should silver store?

A) Carry the timestamp assigned in bronze unchanged into silver, so both layers show the original ingestion time (recommended if Question 1 selects ingestion time)

B) Generate a separate timestamp when silver processes/upserts the event

C) Store both the original bronze ingestion timestamp and a separate silver processing timestamp

X) Other (please describe after `[Answer]:` below)

[Answer]: B

## Question 3: What column name should be used?

A) `ingestion_timestamp` in both bronze and silver, matching the existing quarantine column (recommended for one shared ingestion timestamp)

B) `bronze_ingestion_timestamp` and `silver_processing_timestamp` for separate layer times

C) `created_at` in both tables

X) Other (please describe after `[Answer]:` below)

[Answer]: B

## Question 4: How should existing table rows be handled if the tables already exist?

A) Add the column as nullable and leave historical values `NULL`, because the original ingestion time is unknown (recommended)

B) Backfill from `source_timestamp`, treating Kafka source time as the best available approximation

C) Set all existing rows to the migration/run time

D) Require a manual migration and fail notebook startup when the column is missing

X) Other (please describe after `[Answer]:` below)

[Answer]: A

## Question 5: Which timestamp type and time basis should the column use?

A) Spark/Delta `TIMESTAMP`, with values representing UTC instants (recommended)

B) Spark/Delta `TIMESTAMP_NTZ`, with values interpreted in a named local timezone

C) ISO-8601 UTC text (`STRING`)

X) Other (please describe after `[Answer]:` below)

[Answer]: A

## Existing project extension selections

These choices are carried forward from the prior approved P1 project baseline. Change an answer if you want different extension behavior for this intent.

### Question 6: Security Baseline

A) Yes — enforce all SECURITY rules as blocking constraints

B) No — skip all SECURITY rules

X) Other (please describe after `[Answer]:` below)

[Answer]: B — carried forward from the approved P1 project baseline

### Question 7: Property-Based Testing

A) Yes — enforce all PBT rules as blocking constraints

B) Partial — enforce only for pure functions and serialization round-trips

C) No — skip PBT rules

X) Other (please describe after `[Answer]:` below)

[Answer]: C — carried forward from the approved P1 project baseline

### Question 8: Resiliency Baseline

A) Yes — apply the resiliency baseline as directional design-time guidance

B) No — skip the resiliency baseline

X) Other (please describe after `[Answer]:` below)

[Answer]: B — carried forward from the approved P1 project baseline
