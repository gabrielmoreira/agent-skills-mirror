---
title: Effects a command leaves behind
applicability:
- Before a command runs
---

A capable agent judges a command by its kind or purpose, such as a build or a command meant only to inspect, and runs it as harmless, leaving behind a change the requester must repair or someone else will notice.

Whether a command exercises the software and what it leaves behind are separate questions. An effect is disposable output only when nothing outside this run depends on it, it stays outside maintained material and the material under analysis, and removing it returns everything the command changed, whether files, processes, services, data, accounts, or remote systems, to its state before the run, with nothing anyone else made or relies on lost or altered. Judge every effect a command can have by that test rather than by the command's kind, its usual purpose, or the fact that it was invoked from a software workspace, and treat an effect the evidence cannot show to pass as going beyond disposable output. For example, a fresh build directory, cache, or report usually passes, as does an environment, container, or test database created for the run from the project's own declarations, while code generation or a fix mode writing into maintained material, replacing an existing dependency install, writing to a developer database, leaving a process running, calling a remote system under a credential, or incurring spend fails.

A command with any effect beyond disposable output changes the project or its environment. Each task's approach and guides decide which kinds of command it may run, and with which effects, if any; a check a guide prescribes never overrides a limit the approach or the task's authority sets, though one outside that limit still sets the evidence its claim needs.
