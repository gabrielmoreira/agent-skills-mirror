---
kind: guidance
title: Grounding work in the project that owns it
requires:
- indirect-consumers
---

Establish the project's languages, resolved versions, build and test entry points, generators, formatting rules, and ownership declarations from its manifests, lock or resolved state, configuration, scripts, and nearby code. Ecosystem custom and memory are candidates only; project evidence decides what this project adopted.

When it applies, read [[guide:technology-freshness]] before the decision that turns on it.

When it applies, read [[guide:requester-supplied-material]] after governing project instructions and before substituting other evidence.

Search from the request's terms, public symbols, contracts, configuration keys, and recorded failures. Use the result to choose files rather than traversing the tree. Read an implicated unit in enough context to understand its behavior, then follow only the callers, registrations, generated consumers, schemas, or tests a concrete question requires. When the question is whether behavior departs from its contract, trace boundary inputs, failure and cleanup paths, cancellation, retries, partial completion, and state transitions, where defects become observable. Close any consumer set the question needs over the mechanisms that bind consumers without a textual reference, not over textual references alone.
