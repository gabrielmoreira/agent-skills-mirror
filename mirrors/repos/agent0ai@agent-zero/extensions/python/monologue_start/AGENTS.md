# Monologue Start Extensions DOX

## Purpose

- Own core backend behavior that runs when a monologue starts.

## Ownership

- Ordered Python files own core monologue-start setup.

## Local Contracts

- Keep start-of-monologue work bounded and non-blocking where appropriate.
- Plugin-specific behavior belongs in the owning plugin's `extensions/python/monologue_start/` directory.

## Work Guidance

- Coordinate lifecycle changes with the message loop and relevant plugin hooks.

## Verification

- Smoke-test the first monologue after a new user message.

## Child DOX Index

No child DOX files.
