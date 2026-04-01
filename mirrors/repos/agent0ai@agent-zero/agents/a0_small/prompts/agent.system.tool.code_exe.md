### code_execution_tool
run terminal, python, or nodejs commands.
args:
- `runtime`: `terminal`, `python`, `nodejs`, or `output`
- `code`: command or script code
- `session`: terminal session id (default `0`)
- `reset`: kill session before running (`true`/`false`)
rules:
- `runtime=output` to poll running work.
- `input` for interactive prompts.
- do NOT interleave other tools while waiting.
- ignore framework `[SYSTEM: ...]` info in output.
