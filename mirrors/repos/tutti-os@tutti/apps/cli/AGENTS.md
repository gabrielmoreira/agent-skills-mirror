# AGENTS.md

## Scope

This file applies to `apps/cli/*`.

`apps/cli` owns the bundled `tutti` terminal entrypoint.

The CLI should stay thin:

- discover the local daemon endpoint
- authenticate with the endpoint bearer token
- parse terminal arguments
- render daemon command output

Business rules, workspace resolution, permission filtering, command metadata, and command execution belong in `services/tuttid`.

## Setup Commands

- Run CLI tests: `go test ./...`
- Build the CLI: `go build ./...`
- Check generated defaults from the repository root: `pnpm check:defaults-generated`

## Action Rules

- keep daemon HTTP contract changes in `services/tuttid/api/openapi/tuttid.v1.yaml` first
- keep the hand-written daemon transport model covered by contract tests against the OpenAPI spec
- derive local state paths from generated defaults instead of adding new hardcoded `$HOME` paths
- do not expose workspace flags or workspace help copy in personal edition commands
- do not duplicate domain validation in the CLI; return daemon errors with clear terminal wording

## Related Docs

- [docs/architecture/project-structure.md](../../docs/architecture/project-structure.md)
- [docs/architecture/desktop-transport.md](../../docs/architecture/desktop-transport.md)
- [docs/conventions/local-state-storage.md](../../docs/conventions/local-state-storage.md)
