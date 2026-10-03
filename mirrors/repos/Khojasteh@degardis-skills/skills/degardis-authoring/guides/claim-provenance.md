---
title: Claim provenance
applicability:
- When the work depends on preserving, for later reviewers, evidence that settled a field claim and will not otherwise remain reachable
---

An author's assertion that a claim was verified is not new evidence for that claim. Preserve what a later reviewer can independently inspect: an authorized source-controlled reference, an immutable or versioned locator, a content digest for a preserved record, or an approval/attestation whose issuer has authority over the proposition. If none can remain inspectable, the later reviewer must treat the claim as unverified rather than inherit today's confidence.

Extension metadata may carry provenance, never clearance. For example:

```yaml
x-claim-provenance:
- claim: "<semantic proposition>"
  source: "<inspectable authority or preserved record>"
  scope: "<version/date/jurisdiction/configuration where relevant>"
  digest: "<content digest when one is available>"
```

Use only fields the available evidence can honestly populate, and do not place secrets or disclosure-harmful material in metadata. The record unit is the semantic proposition, not each sentence that repeats it.

A later reviewer re-establishes the claim from the referenced authority or preserved evidence and verifies any digest before relying on it. Matching author-written metadata alone never raises claim status. When the referenced evidence is unavailable, stale for the required scope, or cannot be authenticated enough for the decision, keep the claim unresolved and state the check or authority that would settle it.
