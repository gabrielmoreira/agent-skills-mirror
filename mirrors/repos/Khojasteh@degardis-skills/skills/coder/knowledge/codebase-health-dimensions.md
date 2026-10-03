---
kind: concept
title: Codebase-health dimensions and the evidence that opens them
x-claim-provenance:
- claim: Software-engineering assessment may need to reason across requirements, architecture/design, construction, testing, operations, maintenance, configuration management, quality, and security rather than code structure alone.
  source: https://www.computer.org/education/bodies-of-knowledge/software-engineering/topics
---

A broad assessment always weighs three dimensions that repository evidence can establish directly:

- **Concrete risk:** evidenced correctness, security, data-integrity, concurrency, compatibility, reliability, resource, or operational failure with a reaching scenario and impact. Leaked or unbounded resources that can make behavior fail belong here; measured cost belongs to performance.
- **Test adequacy:** behavioral coverage, independent oracles, meaningful boundaries and failures, determinism, isolation, and test level, judged from test code, configuration, and recorded results.
- **Structure:** cohesion, coupling, duplicated knowledge, control flow, abstraction cost, testability, granularity, fragmentation, or repetitive layering only when it imposes a demonstrated cost on a real change or behavior path.

Seven more dimensions open only when the request names them or evidence in the assessed surface states their problem or runs through them:

- **Dependency health:** an advisory, support/deprecation issue, graph conflict, constraint, pinning rationale, or dependency lies on an established finding path. Version age, popularity, or a missing audit alone is not a finding.
- **Technology replacement:** an approved requirement cannot be met through a viable supported upgrade or bounded change. Establish the blocked requirement and feasibility gap before proposing replacement.
- **Performance:** a target, budget, service objective, measurement, profile, regression, scalability/resource limit, or recorded cost concern exists. Establish workload and measurement; code appearance is not performance evidence.
- **Documentation:** a required public, operational, migration, compatibility, or maintainer contract is missing, contradictory, stale, or would be invalidated. Establish the reader and concrete discrepancy.
- **Interface and integration health:** an established provider/consumer boundary has a demonstrated semantic, compatibility, ownership, or verification gap. Establish the independent consumer and concrete mismatch.
- **Build and delivery integrity:** project evidence cannot account for dependency selection, generated inputs, artifact identity/integrity/provenance, or required source-to-artifact mapping. Presence or absence of a record alone is not a finding.
- **Operability and observability:** an operational decision is blocked by missing or misleading signals, health semantics, correlation, or recovery evidence. Establish the consuming operator or automation and the decision it cannot make.
