---
title: Maintaining existing tests
applicability:
- When whether to keep, repair, or remove an existing test is in question
- When the quality of an existing test suite is in question
---

For each test under question, identify the contract it can distinguish, what change should make it fail, and whether that change is forbidden. A passing test is not useful merely because it executes code, and an awkward test is not disposable merely because its value is hard to see.

Establish those answers from the contract, product code and consumers, or version-control history rather than from the test alone. When an assertion supplies a literal being searched, exclude test material from the product-side search and prove the query can match a known product occurrence before treating an empty result as evidence.

Classify a test for repair when its contract remains required but its setup, assertion, fixture, or harness no longer expresses that contract correctly. Classify it for removal only when the contract was intentionally retired, the test cannot distinguish a prohibited change, or another named check demonstrably subsumes its failure space. Keep it when the evidence cannot establish one of those dispositions. State the evidence that decided each disposition and leave an unsettled overlap explicit.

Establish subsumption from the contract or subject: the retained check must fail in every case the candidate would. Similar names, shapes, or targets do not establish that relationship. Keep both when the evidence is short. A linked issue or history is evidence about the regression, not automatic retention. Keep the test when that evidence establishes a distinct surviving failure space or a project requirement for that test; when complete subsumption is established instead, include the history in the disposition evidence without letting it override the subsumption.

Signals such as no discriminating assertion, an expectation sourced from production, tautology, unspecified absence, a misleading name, a framework guarantee, permanent skip or focus, duplicated setup, broad mocks, brittle incidental assertions, nondeterminism, obsolete fixtures, excessive runtime, or unclear names are common but non-exhaustive prompts for investigation, not deletion criteria.

An authorized removal states in its report the coverage removed and the current evidence that still protects the surviving contract. It also accounts for every snapshot, golden file, recorded response, fixture, helper, parameter set, dependency, or configuration entry it makes unowned, after closing that supporting artifact's consumer set. Test count by itself establishes neither quality nor improvement.
