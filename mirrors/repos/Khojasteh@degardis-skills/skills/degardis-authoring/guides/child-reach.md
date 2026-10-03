---
title: What the child agent may reach
applicability:
- When the work depends on what the child agent may read beyond what its request supplies
---

This page is about what the child skill must teach the child agent.

The canonical [[principle:authority-before-effect]] principle owns the separation of read, change, and effect, and the rule that reachability grants nothing. Add subject knowledge only for what the principle cannot supply: which material the child agent may treat as readable. A source saying only "read-only" has said nothing about whether the child agent may open a sibling repository, ambient credentials, another user's files, or a connected service, so state the readable material in terms the child agent can recognize from its own request and context.

Where the request and the skill use the same word, teach the child agent to resolve it from the skill's own constructs first. Otherwise an internal term such as *workspace* or *profile* quietly becomes permission to inspect whatever the host happens to call by that name.

Name a source for the child agent to consult only where the skill ships it or the requester confirmed the child agent will have it, and name it precisely enough that the child agent can tell an unavailable source from one it merely failed to find. A pointer to something that is not there sends an agent looking instead of deciding.
