# Overview

This repository is the Clawket monorepo.

## Workspace Layout

| Path | Role |
|------|------|
| `apps/mobile` | React Native mobile app |
| `apps/relay-registry` | Cloudflare registry worker |
| `apps/relay-worker` | Cloudflare relay worker |
| `apps/bridge-cli` | Publishable bridge CLI |
| `packages/bridge-core` | Bridge shared helpers |
| `packages/bridge-runtime` | Bridge runtime |
| `packages/relay-shared` | Relay shared protocol/types |

## External Dependency

OpenClaw still lives outside this repository. From the monorepo root, its expected sibling path is `../../openclaw` or `/Users/lucy/Desktop/op/openclaw`.

## Mechanical Merge Rule

This monorepo is in the first migration phase:

1. Preserve product behavior.
2. Preserve deploy and publish boundaries.
3. Prefer path fixes and workspace orchestration over logic refactors.
4. Do not mix protocol redesign with structural migration.

## Repository Instruction Rule

When work touches a specific workspace or subdirectory, read the closest applicable `AGENTS.md` for that area before making changes. Do not start implementation based only on the monorepo root instructions when a more specific directory-level instruction file exists.

## Documentation Rule

If you update `README.md`, you must update `README.zh-CN.md` in the same change so the English and Chinese versions stay aligned.
