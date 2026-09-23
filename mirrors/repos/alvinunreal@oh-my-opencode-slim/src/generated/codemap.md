# src/generated/

## Responsibility

Generated build metadata for the oh-my-opencode-slim plugin, specifically the build identity stamp that identifies which exact build produced each plugin artifact. This directory contains runtime-only metadata never sent to models.

## Design

Generated files are produced by scripts during the build process:
- **Build identity**: Version and timestamp for diagnostics/logs
- **Runtime-only data**: Never used in prompt payloads or model interactions
- **Build fidelity**: Pinpoints which build a plugin artifact came from
- **CI-friendly**: Commit-tracked with `postversion` and `bun run build`

## Flow

The generation pipeline:
1. `bun run build` executes scripts/gen-build-info.ts first
2. It reads package.json for the current version
3. Generates `src/generated/build-info.ts` with two constants:
   - BUILD_VERSION: plugin version from package.json
   - BUILD_TIME: ISO timestamp of the build
4. Only writes if version changed or file missing (keeps existing on local dev builds)
5. Output is imported at runtime by `src/index.ts` and `src/v2/setup.ts` via `getBuildInfo()` for diagnostics

## Integration

### Consumers

- **Build system**: `bun run build` orchestration
- **Runtime**: `src/index.ts` and `src/v2/setup.ts` import `getBuildInfo()`
- **Diagnostics**: Used by logging/analysis for build identity
- **CI**: Packagers inspect build-info for artifact tracking

### Dependencies

- **Scripts**: `scripts/gen-build-info.ts` generation logic
- **Filesystem**: Package version from package.json
- **Time**: System timestamp

### Publishing

- **commit-tracked**: Generated file is committed (static identity)
- **postversion**: Updated during release process with `--force`
- **dev-safe**: Doesn't dirty source on local dev builds unless version changes