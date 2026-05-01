# Install Guide — operator-identity-context (Global Skill)

## Scope

User-level global skill. Applies to ALL repositories on this machine.
Must be registered in `~/.copilot/instructions/operator-identity-context.instructions.md`
and referenced in the global skills list.

## Location

`~/.copilot/skills/operator-identity-context/SKILL.md`

## Purpose

Encodes the operator authority model, automation mandate, and machine/account inventory so the
agent never asks the user to perform manual tasks and always has the right context about who has
what access.

## Registration

This skill should auto-apply via the global instruction file:
`~/.copilot/instructions/operator-identity-context.instructions.md`

The instruction file must include an `applyTo: "**"` directive so it loads on every task.

## Update Triggers

Update this skill whenever:

- New automation capabilities are added to publish scripts
- New accounts/services are added to the project
- The machine hardware changes
- A new "automation gap" is discovered and resolved
