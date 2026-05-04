# apply-patch

## Responsibility

Provide a resilient preprocessor for `tool.execute.before` on `apply_patch` that rewrites recoverable stale hunks, validates workspace boundaries, and blocks unsafe patches before they reach OpenCode’s native patch executor.

## Design

- Entry point is `createApplyPatchHook` in `index.ts`, bound to `tool.execute.before`.
- `rewritePatch` (`operations.ts`) is the main pipeline used by the hook and is backed by:
  - `parseValidatedPatch` / `createPatchExecutionContext` (`execution-context.ts`) for patch parsing and path/state validation.
  - `parsePatch` / `parsePatchStrict` / `formatPatch` (`codec.ts`) for patch AST conversion and serialization.
  - `resolveChunkStart`, `locateChunk`, `resolveUpdateChunks`, `applyHits` (`resolution.ts`) for context matching.
  - `resolveBy...` helpers in `matching.ts` (`seek`, `seekMatch`, `list`, `rescueByPrefixSuffix`, `rescueByLcs`) for tolerant matching.
- `types.ts` defines domain contracts used across modules (`PatchChunk`, `PatchHunk`, `ResolvedChunk`, `ApplyPatchErrorKind`, etc.).
- Error semantics are centralized in `errors.ts` (`ApplyPatchError`, `createApplyPatchBlockedError`, `createApplyPatchVerificationError`, `isApplyPatchError`) and surfaced in hook logging and thrown errors.
- No additional runtime configuration is exposed; behavior is controlled by constant `APPLY_PATCH_RESCUE_OPTIONS` (`prefixSuffix` + `lcsRescue`).

## Flow

1. `createApplyPatchHook` filters only `input.tool === 'apply_patch'`.
2. It requires `output.args.patchText` to be a string.
3. It resolves `root` and `worktree` from `input.directory` / `ctx.directory` / `ctx.worktree`.
4. It calls `rewritePatch(root, patchText, options, worktree)`.
5. On `result.changed`, it replaces `output.args.patchText` with canonicalized patch text.
6. On failure, it normalizes to `ApplyPatchError`, logs `blocked | validation | verification | internal`, and rethrows so native execution is prevented.

## Integration

- Consumed by `src/index.ts` through `createApplyPatchHook`.
- Acts before native tool execution via OpenCode hook point `tool.execute.before`.
- Downstream dependencies include `ctx.client` indirectly only for context, and `utils/logger` for structured hook telemetry.
- Uses `Patch` parser/resolver modules to keep `new_lines` byte-preserving while only mutating stale anchors and chunk context.
