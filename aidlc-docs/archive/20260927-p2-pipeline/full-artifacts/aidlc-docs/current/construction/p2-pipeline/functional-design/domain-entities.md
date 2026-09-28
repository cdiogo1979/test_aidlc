# P2 Pipeline — Domain Entities

## P2 Kafka source record / bronze record

Carries original payload, key, headers, topic, partition, offset, source timestamp, and nullable bronze processing timestamp. Logical identity is `(topic, partition, offset)`. P2 consumes only `my-test-p2`.

## P2 valid event / silver current event

A valid event has a nonblank string `event_key`, extensible attributes, Kafka source identity and time, and nullable silver processing timestamp. Silver retains at most one latest row per event key, using the P1 ordering contract: source timestamp, partition, then offset.

## P2 quarantined source record

Represents an invalid P2 bronze payload and retains raw payload, source identity/time, existing ingestion timestamp, and diagnostic. Deduplication identity is `(topic, partition, offset)`.

## P2 integration run

One scheduled or manual job invocation with environment, independent bronze/silver lookback parameters, task outcomes, and overall status. Success requires both tasks to succeed in dependency order.
