---
title: Operational dependencies of the child agent
applicability:
- When the work depends on a capability the child agent needs
---

This page is about what the child skill must teach the child agent.

For every required capability, make the dependency contract derivable from the final bundle: what capability is needed, how the child agent can recognize that it is available, how it is invoked or opened in that host, what inputs and permissions it needs, what observable result establishes success, and what happens when it is missing, partial, or fails.

A capability this run's own host offered, a location on its own machine, an access it held, an extension it had installed, or a service it remembers from elsewhere reaches the child agent only as [[principle:cold-reader-derivation]] allows, through the bundle or the host contract. Teach the child agent to recognize and discover a capability rather than to call it by a name remembered from the author's host. For shipped scripts and assets, use the bundle-relative references the compiler checks, and state any runtime need the bundle does not itself provide.

Required dependencies stop the dependent branch when unavailable; optional dependencies need an explicit fallback that still meets the narrower claimed outcome. Never let an unavailable capability silently turn work the child agent was to perform into advice while reporting the original outcome as complete.
