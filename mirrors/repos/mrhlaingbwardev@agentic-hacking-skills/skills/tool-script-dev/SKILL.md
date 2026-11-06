---
name: tool-script-dev
description: Use when user says "write a tool", "script", "cli", "automation", "scraper", "helper", "bot", "utility", "make a program", "ကိရိယာ", "ရေး", "tool ရေး", "script ရေး". Builds robust CLI tools, scripts, and automation in Python/Node/PowerShell/Go with proper structure, error handling, and arg parsing.
---

# Tool & Script Development

## TRIGGER
Activate when user wants to build any standalone tool, script, CLI, automation, scraper, helper, or utility — not app/website code.

## CORE RULES

1. **Pick the right language for the job**
   - Quick Windows automation / file ops → PowerShell
   - Cross-platform CLI / scraping / APIs → Python
   - Fast single-binary / concurrency → Go
   - Web-connected tool / easy deps → Node.js
   - Ask if unsure; default to Python for general tools.

2. **Always make it runnable, not snippets**
   - Full file, not fragments.
   - Include `if __name__ == "__main__":` (Python) / `fn main()` (Go) / shebang (PowerShell/Node).
   - No placeholders like `// TODO` unless explicitly requested.

3. **Structure**
   ```
   tool-name/
     tool.py          # main entry
     requirements.txt # deps (if Python)
     README.md        # usage (only if asked)
   ```

4. **Argument parsing** — never hardcode inputs
   - Python: `argparse` (or `click` for richer CLIs)
   - Node: `process.argv` / `commander`
   - Go: `flag` package
   - PowerShell: `param()` block
   - Support `-h/--help` automatically.

5. **Error handling (non-negotiable)**
   - Wrap network/IO in try/except; print clear messages, exit non-zero on failure.
   - Never crash with raw stack traces for expected errors (file missing, bad URL, rate limit).
   - Respect rate limits / add small delays for scrapers.

6. **OPSEC by default**
   - No secrets hardcoded — read from env vars or a local `.env` (gitignored).
   - Never log tokens/keys.
   - Rotate user-agents; disguise automation as normal traffic.
   - Cover geography: never expose real location (use VPN + cover country).

7. **Output**
   - Print concise, parseable results (JSON or table).
   - Write results to a file when bulk (e.g. `results.json`/`results.txt`).

## WORKFLOW
1. Clarify: what does it do, input source, output format, target OS.
2. Choose language + deps.
3. Write the full tool with arg parsing + error handling.
4. Show a run example: `python tool.py --input x.txt --out results.json`.
5. Note OPSEC/usage caveats.

## EXAMPLE (Python CLI skeleton)
```python
import argparse, sys, json

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--out", default="results.json")
    args = p.parse_args()
    try:
        data = open(args.input).read().splitlines()
    except OSError as e:
        print(f"[!] cannot read {args.input}: {e}", file=sys.stderr)
        sys.exit(1)
    # ... process ...
    json.dump({"count": len(data)}, open(args.out, "w"))
    print(f"[+] saved {args.out}")

if __name__ == "__main__":
    main()
```
