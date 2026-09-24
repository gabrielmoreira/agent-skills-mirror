# ZCode goal mode

LoopX adapter for [ZCode](https://zcode.z.ai/) — a terminal coding agent
supporting [skills](https://zcode.z.ai/en/docs/skill), [Goal Mode](https://zcode.z.ai/en/docs/goal),
and [Automations](https://zcode.z.ai/en/docs/automations).

## What this surface is

ZCode discovers user skills from `~/.zcode/skills/<skill-name>/SKILL.md`.
While ZCode provides native Goal Mode and Automations, LoopX currently
integrates through the managed `$loopx` skill facade. In this mode, the loop
driver is the agent's own turn loop gated by LoopX quota — every continuation
enters through `quota should-run`, and a stop decision ends the session loop.

Direct machine binding to ZCode native Goal Mode or Automations is not yet
integrated and will be supported through dedicated provider contracts in the
future.

## Install

```bash
loopx slash-commands --install --surface zcode
```

Writes the managed LoopX skill facades (`loopx`, `loopx-global-*`, …) into
`ZCODE_HOME/skills` (default `~/.zcode/skills`; override with `ZCODE_HOME`).
Managed files carry the `loopx-managed-slash-command` marker and are refreshed by
rerunning the installer; user-owned files are never overwritten.

After installation, refresh or read back installed skills in ZCode via Settings → Skills.

## Use

From a ZCode session in a connected project, invoke the `$loopx` skill (or type
`/loopx <complex task>`). The facade instructs the agent to run:

```bash
loopx start-goal --guided --project . --slash-command-arguments="<task>" --host-surface zcode
```

After todo writeback, carry the generated heartbeat task body as the session
objective and start every following turn with `quota should-run`.

## Layout

- `__init__.py` — host facts: install surface id, skills root resolution, and
  the env override used by the installer and the activation packet.
