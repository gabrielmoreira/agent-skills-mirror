---
name: omniflow-gui-runtime
description: Install the pinned OmniFlow GUI runtime used by the Omni VLM plugin.
compatibility: Android arm64-v8a with the Omnibot Alpine runtime
metadata:
  owner: omnimind
  runtime: omniflow
---

# OmniFlow GUI Runtime

This Skill is managed by the OmniFlow plugin. OpenOmniBot's built-in
Streamable HTTP MCP endpoint exposes the Runtime to any standard MCP host. No
Agent-specific installer, Python MCP SDK, branch, or private protocol is
required on the phone.

The Skill owns usage guidance. The versioned GitHub Release asset owns the
runtime implementation: pinned OmniFlow, canonical OmniTransfer v9, checkpoint,
and the small bundled pure-Python dependency. OpenOmniBot owns Android
permissions, observations, actions, model access, RunLogs, the process bridge,
and the standard MCP endpoint. There is no nested runtime ZIP, virtual
environment, dependency resolver, or private dependency installer.

Use `run_gui` for a new task, `run_function` for a registered Function,
`list_functions` for discovery, and `register_function` to register a successful
`run_gui` RunLog. Observation, action, model, RunLog persistence, and destructive
management operations remain internal to OpenOmniBot.
