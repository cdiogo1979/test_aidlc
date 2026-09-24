# P1 Personas — P1 Event Data

## Persona: Downstream Data Engineer

**Role**: Builds further data products from the P1 silver table.

**Goals**

- Query current event data from `test_prod.p1_test`.
- Use one latest valid event per `event_key` as the basis for downstream processing.
- Rely on malformed Kafka messages being isolated from the silver data they consume.

**Needs**

- A queryable silver table populated by the daily incremental workload.
- Expanded JSON fields and stable key-based current-state behavior.
- Confidence that malformed messages are quarantined and do not appear as valid silver records.

**Scope boundaries**

- This persona represents the only user role selected for P1 stories.
- The persona consumes silver data; the stories do not add an operator workflow or gold-layer output.
- Specific downstream products, business domain beyond the neutral `P1 event data` label, and success metrics have not been provided.

**Related stories**: US-P1-01, US-P1-02.
