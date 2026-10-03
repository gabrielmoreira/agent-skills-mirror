---
title: Removal and compatibility
applicability:
- When a change removes or alters something a consumer outside the change may rely on
---

The surviving contract a removal keeps is fixed under [[guide:change-contract]] before anything is removed. Establish from repository and release evidence whether the behavior was published, deployed, documented as supported, or exists only in unreleased work; keep the status unknown when evidence does not settle it, and never use unreleased status as proof that no consumer exists. Compatibility includes source, binary, data, protocol, schema, serialization, configuration, operational, and behavioral consumers that exist in this project, including rolling deployments and independently versioned components. Distinguish reliance on current behavior, even defective behavior, from an intended guarantee.

Identify generated sources and edit their source of truth. Treat absence as established only within the searched and authorized surface, and exercise runtime discovery or registration after a change; no static-search result alone proves code dead.

Prefer adding beside an existing surface and preserving current defaults where compatibility is required. Obtain explicit approval before each compatibility break; name the affected consumers and give every approved break a migration or rollback path. An instruction that explicitly replaces one identified observable contract approves only that exact replacement, not adjacent consumer effects. Stop at an unapproved break.

Sequence migration before removal when consumers or stored state cannot move atomically. Define the abandoned identity and search for it again at completion. Cover declarations, imports, code, adapters, flags, configuration, pipelines, generators and artifacts, tests and fixtures, infrastructure, jobs, telemetry, documentation, runbooks, package sources, plugins, registries, build steps, runtimes, and installed tooling found by that search. Remove items serving only the abandoned side, disposing of tests under [[guide:existing-test-maintenance]]. Retain a bridge or abandoned-side element only under [[guide:temporary-coexistence]]. Do not broaden a requested withdrawal to adjacent overloads, options, shared paths, or still-supported values.

Verify what remains, not merely that a symbol disappeared. Confirm intended paths execute rather than a compatibility fallback, and observe the destination build, start, operate, and recover with the abandoned side removed or disabled. A shim that builds, a permanent dual path, ownerless follow-up cleanup, or any unjustified survivor leaves the withdrawal incomplete.
