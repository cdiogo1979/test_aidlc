# Requirements Verification Questions — P2 Pipeline

The functional scope is clear: create P2 as a functional copy of P1 using Kafka topic `my-test-p2`. Project-specific job, configuration, table, and checkpoint names will be changed to keep P2 isolated; processing behavior remains the same.

## Question 1: Security Baseline Extension

Should security extension rules be enforced for this project?

A) Yes — enforce all security rules as blocking constraints.

B) No — skip the security rules.

X) Other (please describe after [Answer]: tag below)

[Answer]: B

## Question 2: Property-Based Testing Extension

Should property-based testing rules be enforced for this project?

A) Yes — enforce all property-based testing rules.

B) Partial — enforce them for pure functions and serialization round-trips only.

C) No — skip property-based testing rules.

X) Other (please describe after [Answer]: tag below)

[Answer]: B

## Question 3: Resiliency Baseline Extension

Should the resiliency baseline be applied as directional design-time guidance?

A) Yes — apply the resiliency baseline as design-time best practices.

B) No — skip the resiliency baseline.

X) Other (please describe after [Answer]: tag below)

[Answer]: B
