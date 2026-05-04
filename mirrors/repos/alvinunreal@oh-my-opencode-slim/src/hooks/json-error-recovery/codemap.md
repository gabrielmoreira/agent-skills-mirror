# src/hooks/json-error-recovery/

## Responsibility

- Detect likely JSON syntax/parse failures in tool outputs and append a strong, non-redundant recovery prompt so the model replays corrected JSON on retry.

## Design

- `hook.ts` contains the implementation with exported constants:
  - `JSON_ERROR_TOOL_EXCLUDE_LIST`
  - `JSON_ERROR_PATTERNS`
  - `JSON_ERROR_REMINDER`
- `createJsonErrorRecoveryHook(_ctx)` returns a `tool.execute.after` handler that appends reminder text when parsing failed.
- `JSON_ERROR_REMINDER_MARKER` prevents recursive duplicate injection.
- Exclusion is by lowercase tool name (`bash`, `read`, `glob`, web tools) through a `Set`.
- Matching uses regex literals in `JSON_ERROR_PATTERNS` and short-circuits for non-string output.
- `index.ts` only re-exports hook/constant surface.

## Flow

1. In `tool.execute.after`, normalize `input.tool` to lowercase and skip excluded tools.
2. Skip when `output.output` is not a string.
3. Skip if output already contains `JSON_ERROR_REMINDER_MARKER`.
4. Evaluate all `JSON_ERROR_PATTERNS`; on match, append `\n${JSON_ERROR_REMINDER}` to `output.output`.

## Integration

- Exported from `src/hooks/index.ts` and attached to tool output lifecycle at plugin registration.
- Only consumes hook payload contracts (`ToolExecuteAfterInput`, `ToolExecuteAfterOutput`) and standard string checks, making it generic across tools.
- No direct dependency on tool internals; integrates by observing tool-call results before they are surfaced to the model.
