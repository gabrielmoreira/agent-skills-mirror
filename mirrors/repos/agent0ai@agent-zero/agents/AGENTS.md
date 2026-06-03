# Agent Profiles DOX

## Purpose

- Own bundled agent profiles, profile-specific prompts, and profile-local tools.
- Keep profile behavior understandable without requiring edits to core framework prompts.

## Ownership

- Each direct profile directory owns its `agent.yaml`, optional `prompts/`, optional `tools/`, and optional `extensions/`.
- `_example/` demonstrates profile layout and should stay suitable as a reference.
- User-created local profiles belong under `usr/agents/`, not here, unless they are intended to ship with the product.

## Local Contracts

- `agent.yaml` is the profile entry point and must stay valid YAML.
- Profile prompt overrides should be narrow and named to match the core prompt they extend or replace.
- Profile-local tools must follow the same `Tool` contract as root `tools/`.
- Do not put secrets, provider API keys, local paths, or user-specific settings in bundled profiles.

## Work Guidance

- Prefer small profile-specific prompt files over duplicating large core prompts.
- Keep examples generic and runnable in a clean checkout.
- When changing profile behavior, check how the WebUI profile picker and backend profile loader discover profiles.

## Verification

- Run `pytest` or targeted tests covering profile loading when changing `agent.yaml` structure or profile discovery.
- Manually inspect YAML validity for changed profiles if no targeted test exists.

## Child DOX Index

No child DOX files.
