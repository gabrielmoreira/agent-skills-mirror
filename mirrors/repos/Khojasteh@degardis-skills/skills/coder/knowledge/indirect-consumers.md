---
kind: concept
title: Consumers a reference search misses
---

A search for textual references to a symbol closes no consumer set, because software binds names and behavior through mechanisms that carry no direct reference: subclasses and overrides; registries, dependency injection, and other construction paths; reflection, naming conventions, and runtime discovery; routes, templates, and selectors; serialization, persisted records, and stored configuration; generated code, generated clients, and their generators; plugins, scripts, commands, and deployment declarations; examples, documentation, and tests; jobs, telemetry, and runbooks; and an externally published interface whose consumers live outside the repository. The list is common rather than exhaustive: any project mechanism that can bind a name or a behavior at build, load, or run time is a consumer path by the same test.
