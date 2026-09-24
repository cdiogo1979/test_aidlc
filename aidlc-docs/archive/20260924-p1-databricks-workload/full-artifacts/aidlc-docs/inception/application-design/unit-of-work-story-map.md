# P1 Unit-to-Story Map

## Story Mapping

| Story | Primary unit | Supporting units | Outcome |
|---|---|---|---|
| US-P1-01 — Query the latest event state | U2 — Silver Processing and Quarantine | U1 provides Kafka events and bronze records; U3 schedules and integrates both tasks. | A downstream data engineer can query the latest valid row per `event_key` from silver. |
| US-P1-02 — Query valid events when malformed messages occur | U2 — Silver Processing and Quarantine | U1 provides source payloads and metadata; U3 runs the ordered pipeline. | Valid events reach silver while malformed events are isolated in quarantine. |

## Requirement Coverage

| Requirement | Assigned unit(s) |
|---|---|
| FR-01 — P1 folders and artifact locations | U3 |
| FR-02 — Kafka topic, hosts, and secret reference | U1, U3 |
| FR-03 — Daily incremental processing | U1, U3 |
| FR-04 — Bronze payload and metadata persistence | U1 |
| FR-05 — JSON parsing and silver expansion | U2 |
| FR-06 — Latest current row per `event_key` | U2 |
| FR-07 — Malformed-message quarantine | U2 |
| FR-08 — Environment configuration | U1, U2, U3 |

## Coverage Check

- Every approved user story is assigned to a primary unit.
- Both stories' cross-layer paths are supported by U1 and U3.
- All functional requirements FR-01 through FR-08 map to at least one unit.
- No unit is an independently deployable service; the units belong to one P1 deployment.
