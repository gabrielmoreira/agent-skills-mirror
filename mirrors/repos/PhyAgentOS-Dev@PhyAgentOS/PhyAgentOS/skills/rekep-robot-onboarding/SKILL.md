---
name: rekep-robot-onboarding
description: Integrate a new robot into the PhyAgentOS ReKep plugin when the user says things like "帮我接入新机器人 XXX", "接入 ReKep 新机器人", or "help me onboard a new robot into ReKep". Inspect the SDK dropped into the ReKep plugin runtime, generate or update the adapter/factory/docs, and finish with deployment and startup instructions.
---

# ReKep Robot Onboarding

Use this skill when the user wants PhyAgentOS to wire a new robot backend into the external ReKep plugin.

## What This Skill Owns

- Keep robot-specific runtime work inside the external plugin repo, not the PhyAgentOS core.
- Read the SDK that the user placed under the plugin runtime.
- Implement or update the adapter, factory wiring, docs, and usage guide.
- Validate safely with syntax checks and dry-run or preflight commands before suggesting real motion.

Before making edits, read these references:

- `references/01_target_resolution.md`
- `references/02_edit_targets.md`
- `references/03_validation_and_delivery.md`

## Default Workflow

1. Resolve the writable ReKep plugin checkout.
2. Resolve the robot name, slug, and SDK path.
3. Inspect the SDK with `rg`, `find`, `sed`, and example scripts before designing the adapter.
4. Decide whether to create a dedicated adapter file or extend `runtime/cellbot_adapter.py`.
5. Update runtime wiring, docs, and tests.
6. Produce deployment and startup guidance for the new robot.
7. Verify with safe commands only unless the user explicitly asks for hardware execution.

## Editing Rules

- Prefer a dedicated adapter such as `runtime/<robot_slug>_adapter.py` when the SDK is real and non-trivial.
- Only rewrite `runtime/cellbot_adapter.py` when the user explicitly wants to keep using the generic template.
- Update `runtime/robot_factory.py` so the new family can be selected with `--robot_family <robot_slug>`.
- If the SDK needs new install steps or environment variables, update plugin docs in the same turn.
- Keep third-party SDK contents untouched except for vendor-approved wrapper code around them.
- Do not move robot-specific code into the PhyAgentOS main repo unless the change is a doc or skill entry point.

## Trigger Phrases

Examples that should trigger this skill:

- `帮我接入新机器人 <机器人名>`
- `帮我把这个机器人 SDK 接进 ReKep`
- `Help me onboard a new robot into ReKep`
- `Use this SDK to add a new ReKep robot`

## Expected Outcome

By the end of the task, the user should have:

- A clear SDK placement path
- Adapter and factory code wired into the ReKep plugin
- Updated deployment and startup documentation
- A dry-run or preflight verification path
- Ready-to-copy commands for `dobot_bridge.py` and `hal/hal_watchdog.py`
