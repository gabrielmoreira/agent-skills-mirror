# Docker DOX

## Purpose

- Own Docker build contexts and runtime container definitions.
- Keep framework runtime, agent execution runtime, exposed ports, mounted paths, and image build assumptions explicit.

## Ownership

- `base/` owns the base image context.
- `run/` owns the runnable image context and compose file.
- Root `DockerfileLocal` is owned by the root contract but must stay compatible with this directory.

## Local Contracts

- Preserve the two-runtime model documented in the root contract: framework runtime under `/opt/venv-a0` and agent execution runtime under `/opt/venv`.
- Do not bake secrets, local `.env` values, or user data into images.
- Keep compose mounts aligned with `usr/`, `logs/`, and other runtime-state expectations.
- Image changes that affect GitHub publishing must stay synchronized with `.github/workflows/docker-publish.yml`.

## Work Guidance

- Keep Dockerfile steps cache-friendly and explicit about which runtime they target.
- Avoid broad copies of ignored runtime folders.
- Update setup docs when ports, volumes, startup commands, or runtime layout change.

## Verification

- Build the affected Docker context when Docker behavior changes.
- Run Docker-related tests or startup smoke checks when changing runtime entrypoints.

## Child DOX Index

No child DOX files.
