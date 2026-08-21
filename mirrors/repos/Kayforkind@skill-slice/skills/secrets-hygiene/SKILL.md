---
name: secrets-hygiene
description: Keeps API keys in one gitignored place, redacts logs before model pastes, and rotates leaked credentials. Use when handling .env files, commits that might contain secrets, or before pasting scripts or errors to a model. Not for Vercel env pull or OIDC (env-vars) and not for inventing an XAI_API_KEY for browser Grok OAuth. Do not read or echo .env values into chat.
version: 1.0.1
alwaysApply: false
---

# Secrets Hygiene

## Overview

**Every key lives in exactly ONE place** — an env var loaded from a gitignored `.env`, or the OS credential store. Never:

- in the repo (tracked file, script literal, committed `.env`)
- in chat / a prompt to a cloud model (fable, opus, any provider)
- in memory notes or persisted context
- in a command line as plaintext (other processes can read it)

**A key pasted into a prompt has left your machine.** The provider received it, logged it, and may retain it. There is no "unsend" — the only remedy at that point is rotation (§Rotation). This applies to keys embedded in error messages, stack traces, `curl -v` output, and script snippets you paste for debugging, not just deliberate pastes.

### Credential inventory for this environment

| Credential | Form | Where it lives | Notes |
|---|---|---|---|
| OpenRouter | `sk-or-v1-...` | `.env` → `OPENROUTER_API_KEY` | Was once pasted into chat — treat as burned; rotate if still in use |
| Kilo Code | provider key | Kilo Code app/extension settings | Rotate at provider dashboard, update in app UI |
| OpenCode | provider key | OpenCode auth store (`opencode auth`) | Not in a project file |
| Grok | xai-oauth | Browser OAuth session | **No key exists** — never invent/store an `XAI_API_KEY` |
| Ollama | none | local daemon | Nothing to protect |

## When to Use

Load this skill when any of the following are about to happen:

- Writing or editing a script that references an API key or `.env` file
- Preparing to paste any script, log, error output, stack trace, or `curl` output into a chat prompt or subagent context
- Committing changes that might contain credentials (`.env`, config files, scripts with literals)
- Rotating a leaked or suspected-leaked key
- Auditing a repo or notes directory for secret contamination
- Delegating a task to a subagent that involves API-calling code

**Trigger keywords:** API key, secret, `.env`, credential, token, Bearer, `sk-or-v1`, `xai-`, OpenRouter, Kilo Code, OpenCode, Grok, Ollama, redaction, scrub, rotate, gitleaks, pre-commit, gitignore

## Prerequisites

- Windows host with MSYS bash (Git Bash) available
- `git` installed and on PATH
- Optional but recommended: `gitleaks` or `git secrets` for pre-commit scanning
- Optional: `git filter-repo` or `bfg` for history purging after rotation
- PowerShell available for Credential Manager operations

## Procedure

### 1. Store keys correctly (Windows + MSYS bash)

**Dev keys used by scripts: `.env` at project root**

```bash
# .env  (project root, NEVER committed — see Git hygiene below)
OPENROUTER_API_KEY=sk-or-v1-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Reference by name, never by value:

```bash
# bash — value never appears in the script file
curl -sS https://openrouter.ai/api/v1/chat/completions \
  -H @<(printf 'Authorization: Bearer %s\n' "$OPENROUTER_API_KEY") \
  ...
```

```python
# python — os.environ, fail loud if missing
import os
key = os.environ["OPENROUTER_API_KEY"]  # KeyError beats a silent empty string
```

**Long-term / non-dev secrets: Windows Credential Manager**

The key never touches a file or command line — `/pass` with no value prompts interactively:

```bash
cmdkey /generic:OpenRouter /user:api /pass    # prompts for the secret
cmdkey /list:OpenRouter                        # confirm stored (does NOT display it)
```

Retrieval from scripts requires the PowerShell `CredentialManager` module or Win32 CredRead — so in practice: **scripts read `.env`, humans store spares/rarely-used keys in Credential Manager or a password manager.** Don't duplicate a key in both; one place per key.

**Keys that don't exist:**

- **Ollama** is local: no key, no `.env` entry, nothing to leak.
- **Grok (xai-oauth)** authenticates via browser OAuth: there is no `XAI_API_KEY` to store. If you find one written down somewhere, that's a mistake — delete it.

### 2. Never read `.env` contents — load into environment

Hermes opus-mcp settings **explicitly deny** `Read(./.env)`, `Read(./.env.*)`, `Read(./secrets/**)`. This is a guardrail, not an obstacle: reading the file would put the raw key into model context (= a paste, = a leak). **Do not try to Read, cat, grep, or otherwise print `.env` contents.**

Load it into the environment instead — values become env vars without ever entering conversation text:

```bash
# safe load: export everything in .env into this shell only
set -a; . ./.env; set +a
```

To check a key is loaded **without printing it**:

```bash
[ -n "$OPENROUTER_API_KEY" ] && echo "OPENROUTER_API_KEY set (${#OPENROUTER_API_KEY} chars)" || echo "MISSING"
```

Never `echo "$OPENROUTER_API_KEY"` — that puts it in terminal scrollback, and scrollback gets pasted into chats.

### 3. Git hygiene

**Verify `.gitignore` (don't assume — see Verification):**

```gitignore
.env
.env.*
secrets/
*.key
*.pem
__pycache__/
```

**Pre-commit scan — use `gitleaks protect --staged` or `git secrets` if installed.**

Minimal built-in fallback — `.git/hooks/pre-commit` (note: it prints **filenames only**, never the matched text, or the hook itself would echo the key):

```bash
#!/usr/bin/env bash
PAT='sk-or-v1-[A-Za-z0-9]{16,}|sk-[A-Za-z0-9_-]{20,}|xai-[A-Za-z0-9_-]{16,}|Bearer [A-Za-z0-9._~+/=-]{16,}|(API_KEY|SECRET|TOKEN)[[:space:]]*=[[:space:]]*[^[:space:]${}<>]{12,}'
if git diff --cached -U0 | grep -qiE "$PAT"; then
  echo "BLOCKED: possible credential in staged changes. Offending files:" >&2
  git diff --cached --name-only >&2
  exit 1
fi
```

**If a key WAS committed:**

1. **Rotate immediately. This is the only real fix.** Purging history does not un-leak — the push already reached the remote, clones exist, forges cache objects. Deleting the line in a new commit fixes nothing; the key is still in history.
2. Then purge history so the dead key stops tripping scanners:
   ```bash
   # expressions.txt:  sk-or-v1-THEACTUALKEY==>[REDACTED]
   git filter-repo --replace-text expressions.txt
   # or: bfg --replace-text expressions.txt
   ```
3. Force-push only after rotation is confirmed (see Rotation verify step).

**Standing note:** the OpenRouter key was once pasted into chat. If that key (or any key derived by "rotating" to a key you'd also pasted) is still active, rotate it now.

### 4. Redact before sending to any model

Anything you paste to fable/opus/any cloud model — script, traceback, `curl` output, log — must pass through a scrubber first. Errors are the classic vector: an HTTP client happily prints `Authorization: Bearer sk-or-v1-...` in its debug output.

**bash (MSYS, GNU sed):**

```bash
scrub() {
  sed -E \
    -e 's/sk-or-v1-[A-Za-z0-9]{16,}/sk-or-v1-[REDACTED]/g' \
    -e 's/sk-[A-Za-z0-9_-]{20,}/sk-[REDACTED]/g' \
    -e 's/xai-[A-Za-z0-9_-]{16,}/xai-[REDACTED]/g' \
    -e 's/(Bearer[[:space:]]+)[A-Za-z0-9._~+\/=-]{16,}/\1[REDACTED]/g' \
    -e 's/((API_?KEY|SECRET|TOKEN|PASSWORD)[[:space:]"'"'"']*[:=][[:space:]"'"'"']*)[^[:space:]"'"'"']{8,}/\1[REDACTED]/gI'
}

# usage — scrub BEFORE it hits your clipboard/chat:
python generate_svgs.py 2>&1 | scrub
scrub < error.log            # file → stdout, scrubbed
```

**python:**

```python
import re

_PATTERNS = [
    (re.compile(r"sk-or-v1-[A-Za-z0-9]{16,}"), "sk-or-v1-[REDACTED]"),
    (re.compile(r"sk-[A-Za-z0-9_-]{20,}"), "sk-[REDACTED]"),
    (re.compile(r"xai-[A-Za-z0-9_-]{16,}"), "xai-[REDACTED]"),
    (re.compile(r"(Bearer\s+)[A-Za-z0-9._~+/=-]{16,}"), r"\1[REDACTED]"),
    (re.compile(r"((?:API_?KEY|SECRET|TOKEN|PASSWORD)\s*[:=]\s*)\S{8,}", re.I), r"\1[REDACTED]"),
]

def scrub(text: str) -> str:
    for pat, repl in _PATTERNS:
        text = pat.sub(repl, text)
    return text
```

Rule of thumb: if you're not sure something in a paste is a secret, scrub it anyway. `[REDACTED]` never breaks a debugging session; a leaked key breaks everything.

### 5. Sharing with subagents

`delegate_task` context is isolated from your conversation, **but it is still sent to a model** — the isolation protects your context window, not your secrets. Same rule as redaction: a key in a subagent prompt has left the machine.

- **Strip keys from any context you hand over.** Run the scrubber over file excerpts and logs before including them.
- **Pass references, not secrets.** Per the svg-vault-api convention: pass the sha256 cache key / cache file path (`cache/<sha256>.json`), never the API key that produced it.
- If the subagent must call an API, its **tool calls execute locally** — instruct it to load the key from the environment at execution time (`os.environ["OPENROUTER_API_KEY"]`, `$OPENROUTER_API_KEY`), never write the key into the task prompt so it "has" it.
- A subagent never needs a raw key in its prompt. If a design seems to require it, the design is wrong.

### 6. Rotation playbook

Rotate when: a key appeared in chat/a prompt, was committed, showed up in a log you shared, or you simply can't remember whether it's clean.

**Order matters: create new → deploy new → verify new works → revoke old → verify old is dead.** (Revoking first causes an outage; skipping the last step is pitfall #4.)

| Credential | Rotate at | Update where | Verify old is dead |
|---|---|---|---|
| OpenRouter | openrouter.ai → Settings → Keys: create new, then delete old | `.env` → `OPENROUTER_API_KEY`, re-run `set -a; . ./.env; set +a` | See curl check below — expect **401** |
| Kilo Code | Provider dashboard for whichever key Kilo is configured with | Kilo Code extension/app settings UI (not a file) | Old key rejected on next request from a test call |
| OpenCode | Underlying provider's dashboard | `opencode auth login` (re-auth its store) | Same — test call with old key fails |
| Grok (xai-oauth) | Nothing to rotate — revoke the OAuth session at your xAI account's security/sessions page, then re-auth in browser | Nowhere; no key on disk | Old session can no longer call |
| Ollama | N/A — local, keyless | — | — |

Verify the old OpenRouter key is dead **without putting it on a command line** (MSYS process substitution keeps it out of `ps`/Process Explorer):

```bash
OLD_KEY='paste-only-into-this-shell-var'   # leading space if HISTCONTROL=ignorespace
curl -s -o /dev/null -w '%{http_code}\n' \
  -H @<(printf 'Authorization: Bearer %s\n' "$OLD_KEY") \
  https://openrouter.ai/api/v1/key
# 401 = dead (good). 200 = STILL LIVE — you deleted the wrong key.
unset OLD_KEY
```

After rotating: if the leak was a commit, do the history purge (Git hygiene step 3). If the leak was a chat paste, also confirm the key isn't sitting in memory/notes files (Verification checklist).

## Pitfalls

| # | Pitfall | Why it burns you | Instead |
|---|---|---|---|
| 1 | Pasting a key (or a log containing one) to a model | It's transmitted and logged off-machine; unrecoverable | Scrub first (Redaction step); rotate if it happened |
| 2 | Committing `.env` | Key enters history forever; deleting the line doesn't remove it | `.gitignore` + pre-commit hook (Git hygiene); rotate + filter-repo if committed |
| 3 | Keys in memory/notes | Notes get loaded into model context later — a delayed paste | Only `[REDACTED]` in notes; check #4 in Verification |
| 4 | "Rotating" but never verifying the old key is dead | Deleted the wrong key / provider kept it live; leak window stays open | 401-check the old key (Rotation playbook) |
| 5 | Echoing keys to terminal/logs | Scrollback and log files get copied into chats and commits | Length-check pattern (Never-read guardrail); scrub log pipelines |
| 6 | Key in a plaintext command line (`curl -H "Bearer $K"` expands it) | Other processes see full command lines (Process Explorer, `ps`) | `-H @<(printf ...)` header file / process substitution (Rotation playbook) |
| 7 | Handing a raw key to a subagent | delegate_task context goes to a model — same as pitfall #1 | Pass cache keys / env-var *names*; agent loads value locally (Subagents) |
| 8 | Trusting `.gitignore` without testing | A file tracked *before* the ignore rule stays tracked forever | `git check-ignore .env` must print it; `git rm --cached .env` if tracked |

## Verification

Run before committing, and periodically:

```bash
# 1. .env is actually ignored (prints ".env" if ignored; SILENCE = TRACKED = fix now)
git check-ignore .env .env.local 2>/dev/null

# 2. nothing key-shaped staged or in the working diff (prints matching FILENAMES only)
git diff HEAD --name-only \
  --diff-filter=ACM -z | xargs -0 grep -lIiE 'sk-or-v1-|sk-[A-Za-z0-9_-]{20,}|xai-[A-Za-z0-9_-]{16,}|Bearer [A-Za-z0-9._~+/=-]{16,}' 2>/dev/null \
  && echo "^^ POSSIBLE KEY IN THESE FILES" || echo "diff clean"

# 3. no key in tracked files at rest
git grep -lIiE 'sk-or-v1-|xai-[A-Za-z0-9_-]{16,}' -- . && echo "^^ KEY IN REPO" || echo "repo clean"

# 4. memory/notes are clean (they must only ever contain [REDACTED])
grep -rlIE 'sk-or-v1-[A-Za-z0-9]{16,}' memory/ notes/ 2>/dev/null && echo "^^ KEY IN NOTES" || echo "notes clean"
```

Two manual checks with no command:

- **Chat audit:** skim the last messages you sent to any cloud model this session. If a raw key appears in any of them, it's burned — rotate now.
- **One-place audit:** each key exists in exactly one place. A key in `.env` *and* pasted in a script *and* in Credential Manager means three places to leak from and two you'll forget to rotate.

### Quick reference

```bash
set -a; . ./.env; set +a                          # load keys (never Read/cat .env)
[ -n "$OPENROUTER_API_KEY" ] && echo "set"        # presence check, no value printed
cmd 2>&1 | scrub                                  # anything bound for a model
git check-ignore .env                             # must print ".env"
gitleaks protect --staged                         # before every commit (or pre-commit hook)
# leaked? → rotate → verify 401 → then purge history
```

**One place per key. Scrub before every paste. Rotate on any doubt — rotation is cheap, a leak is not.**
