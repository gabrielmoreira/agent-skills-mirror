# Instruction File Method

Load this while writing or updating an agent instruction file. OMH prepares the text; the executor runs the commands and writes the file, and only inside the marked region.

## 1. Which file, where

| File | Read by | Note |
| --- | --- | --- |
| `AGENTS.md` | Codex, and most agents that follow the open format | nested files apply to their directory; the closest file wins |
| `CLAUDE.md` | Claude Code | may point at `AGENTS.md` instead of repeating it |
| `GEMINI.md` | Gemini CLI | |
| `.cursor/rules/*.mdc`, `.cursorrules` | Cursor | rules carry their own globs |
| `.github/copilot-instructions.md` | GitHub Copilot | |

When several exist, keep one source and point the others at it, so two files cannot disagree.

## 2. The marked region

```text
<!-- omh:agent-instructions:begin -->
... prepared content ...
<!-- omh:agent-instructions:end -->
```

- Replace only the text between the markers. Everything before and after is hand-written and stays byte-for-byte.
- When the markers are absent, insert them once, around the new section, and change nothing else.
- Never nest a second pair, and never move hand-written text into the region.

## 3. Sections, in order

1. **Build and test**: the exact commands, each marked `verified (exit 0, <date>)` or `unverified`, with the environment they need (`PYTHONPATH`, a service, a toolchain version file).
2. **Generated files**: for each one, its source, the command that regenerates it, and the gate that checks it. Say "never hand-edit" once, here.
3. **Gates**: which checks are byte-exact, and which fail on a count the author must re-derive.
4. **Pitfalls**: each entry names the symptom, the cause, and what it cost, so a reader can tell a scar from a preference.
5. **Conventions** the code cannot show: branch names, commit trailers, the language of the text.

## 4. What never goes in

| Tempting line | Why it drifts | Write instead |
| --- | --- | --- |
| "the suite has 4,100 tests" | the next merge changes it | the command that runs the suite |
| "the router is at line 212 of `chat.py`" | any edit above it moves it | the symbol name |
| "we have 134 skills" | the catalog grows | the command or file that counts them |
| a restatement of what a function does | the code already says it, and the two diverge | nothing |
| a secret, a token, or a private hostname | the file is read by every agent and often published | the name of the variable that holds it |

The injected copy of an instruction file is a snapshot of the session start. A long session re-reads the file from the default branch before relying on it.
