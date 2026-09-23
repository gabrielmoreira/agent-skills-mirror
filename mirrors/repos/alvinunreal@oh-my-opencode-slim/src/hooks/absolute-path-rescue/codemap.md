# src/hooks/absolute-path-rescue/

## Responsibility

Prevents agent-side absolute-path misguessing by detecting and rewriting incorrect absolute paths that appear inside tool arguments. When an agent incorrectly guesses an absolute path with dropped directory segments (e.g., `/home/u/Work/Project` when the workspace is `/home/u/Work/Parent/Child/Project`), this hook:

- Identifies absolute path arguments in read/list/glob/grep tools that are plain ENOENT (stat errors) 
- Validates that the path is NOT already anchored under the workspace (legitimate missing paths are surfaced, not silently redirected)
- Matches against existing filesystem paths to ensure candidates exist (any stat error rejects the candidate)
- Re-anchors paths using the longest contiguous suffix of the workspace path that appears in the guess, preserving the full relative tail
- Prevents ambiguous matches (multiple anchor occurrences) and resolves exactly one candidate

The hook never invents paths; without a valid, existing, confined candidate the call proceeds as written.

## Design

### Core Architecture
- **Path Detection**: Monitors tool.execute.before events for tools `['read', 'list', 'glob', 'grep']` and path arguments `['filePath', 'path']`
- **Candidate Validation**: Uses longest workspace suffix anchoring algorithm to find the best match
- **Error Handling**: Distinguishes ENOENT (candidate) from other stat errors (pass-through)
- **Path Operations**: Supports configurable path operations (isAbsolute, resolve, join, sep) for different host tool behavior
- **State Isolation**: Process-local hook instance, no shared state across generations

### Algorithm
1. Normalize workspace and guess paths using configurable path operations
2. Reject absolute guesses already under workspace root
3. Split paths into segments, reject any `..` or `.` segments
4. Find longest contiguous workspace suffix appearing in guess
5. Validate single unambiguous occurrence of anchor
6. Construct candidate by re-anchoring to workspace root
7. Verify candidate exists via `exists()` check (stat)

### Error Handling
- **Original path ENOENT**: rescue eligible — the only trigger; ENOENT is detected on the guess via `isMissing()`
- **Candidate check**: the reconstructed candidate must stat successfully via `exists()`; a missing candidate means no rewrite
- **ENOTDIR/EACCES/EIO** on the original path: pass through unchanged (environment issue, not an absent path)
- **Ambiguous anchor**: No rescue (multiple matches)
- **Missing anchor**: No rescue (no workspace suffix matches)

## Flow

### Hook Execution Flow
```
Tool execution (read/list/glob/grep)
    ↓
Tool execute before hook
    ↓
Validate tool type and path argument
    ↓
Check if path is absolute string and missing (ENOENT)
    ↓
Find rescued suffix via findRescuedSuffix()
    ├─ null → no rescue, pass through unchanged
    └─ candidate → rewrite path argument
    ↓
Log rewrite operation
    ↓
Continue with original tool execution (post-rescue)
```

### Path Resolution Flow
```
Input: raw absolute path, workspace path
    ↓
Normalize with pathOperations (respecting host flavor)
    ↓
Check workspace containment
    ↓
Split into segments, reject special segments
    ↓
Iterate anchor lengths from longest to shortest
    ↓
Find exact segment matches in guess
    ↓
Validate single occurrence, construct candidate
    ↓
Verify existence via exists()
    ↓
Return candidate or null
```

## Integration

### Consumers
- **Main Plugin** (`src/index.ts`): Registers the hook during plugin initialization
- **Task Execution**: Intercepts all file system tool calls for path validation
- **Configuration**: Uses `createAbsolutePathRescueHook(ctx, options)` factory

### Dependencies
- **Node.js**: `fs.statSync` for path existence checking
- **Path Operations**: Host-specific path utilities (isAbsolute, resolve, join, sep)
- **Logger**: Structured logging for rewrite operations (`log('absolute-path-rescue rewrote tool path')`)

### Configuration
- **pathOperations**: Override path utilities for testing
- **exists**: Custom existence checker (default: `statSync` based)
- **No external configuration**: All behavior controlled via runtime options

### Performance
- **Lazy evaluation**: Only runs for absolute paths in targeted tools
- **Early rejection**: Fast path for non-absolute paths and non-ENOENT errors
- **Bounded processing**: Anchor iteration stops at first match
- **Stat optimization**: Uses efficient segment matching algorithm