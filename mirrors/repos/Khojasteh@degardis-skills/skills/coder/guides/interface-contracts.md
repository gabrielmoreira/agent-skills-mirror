---
title: Interface and integration contracts
applicability:
- When a software boundary has an independently changing consumer
x-claim-provenance:
- claim: API design and integration/interoperability are distinct software design and construction concerns.
  source: https://www.computer.org/education/bodies-of-knowledge/software-engineering/topics
---

Name the provider, every independently changing consumer in scope, and the observation that makes this a boundary rather than an internal call. Define operation semantics before transport details: valid inputs, outputs, side effects, state transitions, errors, permissions, ordering, duplication, idempotency, cancellation, timeouts, streaming or pagination, and any delivery or consistency guarantee the consumer can rely on. Keep unspecified behavior explicitly free rather than accidentally freezing an implementation detail into the contract.

Separate the semantic contract from each representation that carries it. Give schemas, command syntax, generated clients, wire formats, event names, file layouts, and adapters one authoritative owner where the project has one, then carry their concrete encodings through [[guide:value-boundaries]]. A serializer, client stub, or framework binding proves only that it can encode its model; it does not establish that provider and consumer agree on meaning, defaults, unknown values, failure behavior, or lifecycle.

When independently deployed or externally consumed parties can move at different times, establish the compatibility window before changing the boundary. Define what older and newer sides may send and receive, how unknown fields or operations behave, how negotiation or capability discovery works when the project uses it, and which side owns deprecation. Retiring an existing contract goes through [[guide:removal-and-compatibility]] rather than silently turning an incompatible change into a new version.

Verify at the narrowest real boundary that can expose a mismatch. Prefer schema or contract checks, serialization round trips, generated-client compilation, provider/consumer integration, protocol fixtures, or focused end-to-end execution over mocks that only repeat one side's assumptions. Exercise material success and failure cases from both sides of the boundary, including an older or alternate consumer when compatibility depends on it. A passing provider unit test cannot establish an integration contract no consumer observed.

Keep documentation, examples, generated descriptions, and discovery metadata aligned with the same owner. Do not publish, register, or contact an external consumer merely to verify a local change unless the task already has authority for that effect.
