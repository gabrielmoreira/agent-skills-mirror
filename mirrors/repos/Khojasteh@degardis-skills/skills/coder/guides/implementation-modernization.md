---
title: Implementation modernization
applicability:
- When a legacy mechanism the project relies on is replaced
---

Establish what makes the existing mechanism legacy for this work: the constraint, cost, failure mode, ownership problem, or unsupported model the outcome must retire. Define the behavior and operational contract to preserve, the target responsibility and owner, and the completion evidence. Modernization is not established by newer names, syntax, types, files, or interfaces alone.

Map the legacy mechanism's responsibilities, consumers, dependencies, representations, mutation paths, configuration, tests, and operational effects before designing its replacement. Decide which responsibilities still belong in the target, which move to another established owner, and which disappear with the obsolete constraint.

How far the outcome retires the legacy model is part of its contract. Replacing a mechanism can leave the project's own code written against the legacy model and only adapted to the target, or re-express that code in the target's model. When the request leaves that depth open and the mapping shows code that would only be adapted, the depth is the requester's choice: present the viable levels, each with what it retires, what keeps depending on the legacy model, its cost and risk, and recommend one. A plan carries the choice as an open requester decision; a change waits for it before editing the code it affects.

Design the target from current requirements, the project's present architecture, and the target's native model. Do not make the legacy representation, control flow, or source of truth the backbone of the replacement merely to reduce the diff. A wrapper, adapter, facade, or translated copy is not modernization when correctness still depends on the model the work is meant to retire. Reuse an old component only when it independently fits the target responsibility and constraints; record that reason in re-readable working state rather than treating all surviving code as inherently compatible.

A bridge between the legacy and target paths follows [[guide:temporary-coexistence]].

Complete the work only when the target path owns correctness and the retired path can no longer change its result. Search for surviving legacy entry points, representations, configuration, tests, and terminology. Remove each obsolete survivor; justify any intentional survivor against the target design and ensure it is not an alternate authority or hidden fallback.
