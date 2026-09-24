# U4 NFR Requirements — P1 Layer Timestamp Metadata

## Quality Requirements

| ID | Area | Requirement | Measure or acceptance condition |
|---|---|---|---|
| NFR-01 | Data correctness | Both fields represent UTC processing instants and remain distinct from Kafka `source_timestamp` and from each other. | Code and local checks demonstrate the intended projection; Databricks runtime verification remains pending. |
| NFR-02 | Idempotency | Bronze duplicate Kafka identity and silver no-op replay must not change a committed timestamp. | Focused local checks cover insert/update versus duplicate/no-op merge decisions where practical. |
| NFR-03 | Compatibility | Schema evolution is additive; existing fields, rows, table properties, checkpoints, and CDF configuration remain intact. | New nullable column is added only when absent; no existing field is removed or renamed. Delta/CDF migration behavior requires runtime validation. |
| NFR-04 | Historical data | Existing rows remain NULL in the newly added fields. | No backfill or inference from `source_timestamp`; table migration does not rewrite historical values. |
| NFR-05 | Failure behavior | Unsafe migration, inability to inspect the schema, or incompatible field type fails clearly before batch writes. | Notebook task fails rather than silently processing against an invalid schema. |
| NFR-06 | Performance | Timestamp handling does not add a separate per-row action, scan, or new full-table pass beyond existing processing. | Use the existing DataFrame/merge flow; no new numeric throughput or latency objective is set. |
| NFR-07 | Operational continuity | Job schedule/order, checkpoint paths, CDF use, silver ordering, and quarantine behavior remain unchanged. | No changes to the job or those existing contracts. |
| NFR-08 | Maintainability | Changes remain localized and documented using project conventions; generated functions include Google-style docstrings. | Review changed notebook/helper functions and focused test coverage during Code Generation/Build and Test. |

## Category Findings and Limits

- **Scalability**: No new workload, capacity, or growth target is specified. Existing behavior is retained.
- **Performance**: No numeric latency or throughput objective is specified. Avoid separate per-row work or a new table scan.
- **Availability and recovery**: No uptime, RPO, RTO, or disaster-recovery change is requested. Existing scheduled task behavior remains.
- **Security and compliance**: No new data category, privilege, secret, or external integration is introduced. Security Baseline is disabled per the approved project baseline; existing controls remain applicable.
- **Usability**: Not applicable; no user interface or interactive operation is changed.
- **Runtime verification**: No Databricks workspace is available. Local validation cannot establish Delta schema-evolution/CDF compatibility, actual UTC session behavior, or live table migration success.

## Traceability

These NFRs refine the approved requirements FR-01 through FR-09 and functional rules BR-01 through BR-12. NFR-01 through NFR-05 are correctness and compatibility constraints; NFR-06 and NFR-07 constrain implementation impact; NFR-08 supports maintainability.
