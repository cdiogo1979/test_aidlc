# Domain Entities: P1 Streaming Lookback

## Replay Request

Represents one layer task's requested replay behavior.

| Attribute | Type | Meaning |
|---|---|---|
| `lookback_days` | non-negative integer | Number of 24-hour days to replay; zero means continue from the current checkpoint. |
| `task_started_at_utc` | UTC timestamp | Fixed reference instant captured once at the beginning of task execution. |
| `requested_cutoff_utc` | UTC timestamp or absent | `task_started_at_utc - lookback_days`; absent when the value is zero. |
| `layer` | `bronze` or `silver` | Determines the source and checkpoint affected. |

## Source Replay Position

Represents where a replay begins in the layer's source.

| Attribute | Type | Meaning |
|---|---|---|
| `source_kind` | `kafka` or `delta_cdf` | Bronze uses Kafka; silver uses bronze Delta CDF. |
| `requested_cutoff` | UTC timestamp | Source timestamp requested by the operator's day count. |
| `first_observed_timestamp` | nullable UTC timestamp | First observed Kafka record timestamp or CDF commit timestamp. Nullable when no source records were returned. |
| `observed_window_shortened` | boolean or unknown | True when the first observed timestamp is later than the requested cutoff; unknown when no source records were returned. This reports the observed window without asserting that retention, rather than a period with no source activity, caused the gap. |

## Layer Checkpoint

Represents the existing Structured Streaming progress state owned by one notebook.

| Attribute | Type | Meaning |
|---|---|---|
| `checkpoint_uri` | URI | Configured stable S3 checkpoint location for the layer. |
| `layer_owner` | `bronze` or `silver` | Limits reset scope to the selected notebook's checkpoint. |
| `reset_requested` | boolean | True only for a positive `lookback_days` value. |
| `reset_completed` | boolean | True only after successful recursive removal or confirmed absence before query start. |

## Persisted Records

Persisted bronze, silver, and quarantine rows retain their existing schemas and identity rules. Lookback does not introduce a new domain key or schema migration; it changes the source offsets/commits read by a task and relies on existing idempotent merges.
