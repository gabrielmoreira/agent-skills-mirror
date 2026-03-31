---
name: sensitive-content-scanner
description: Scan files for sensitive content before sharing. Detects personal info, credentials, private URLs, local paths, and security risks. Use before publishing repos, sharing code, or exporting configs.
---

# Sensitive Content Scanner

## Core Purpose

Examine files for sensitive content that should be sanitized before sharing publicly. This is a safety check to run before publishing repos, sharing code snippets, exporting configurations, or any public sharing of files.

## When to Use

- Before pushing a repo public
- Before sharing code/config snippets
- Before exporting skills, dotfiles, or configs for others
- When reviewing what might leak from a file set
- As part of an automated sanitization workflow

## Invocation

`/sensitive-content-scanner [path]` - Scan a file or directory
`/sensitive-content-scanner` - Prompted for path

**Examples:**

- `/sensitive-content-scanner ~/.claude/skills/`
- `/sensitive-content-scanner ./my-project/`
- `/sensitive-content-scanner ./config.md`

## Personal Context File (Optional)

For better detection of YOUR specific sensitive content, create `~/.claude/sensitive-content-context.md`:

```markdown
# Sensitive Content Context

## Personal Identifiers

- Full name: [Your Name]
- Usernames: [github-handle, twitter-handle, etc.]
- Email patterns: [yourname@, your.name@]
- Company/team name: [Company Name]

## Private Paths (patterns to flag)

- ~/Library/Mobile Documents/com~apple~CloudDocs/
- /Users/[username]/
- Any path containing: [folder names that are private]

## Private URLs (domains/patterns to flag)

- notion.site (personal workspaces)
- [internal-tool].company.com
- Private GitHub org: github.com/[private-org]/

## Known Secrets Patterns

- Project-specific API key prefixes
- Internal service names

## Business/Proprietary Terms

- Client names: [list]
- Internal project codenames: [list]
- Confidential terms: [list]
```

If this file exists, the scanner will use it for personalized detection. If not, it uses generic patterns.

---

## Detection Categories

### 1. Credentials & Secrets (CRITICAL)

**Always flag - these should never be shared:**

| Pattern             | Examples                                     |
| ------------------- | -------------------------------------------- |
| API keys            | `sk-...`, `AKIA...`, `ghp_...`, `xoxb-...`   |
| Private keys        | `-----BEGIN RSA PRIVATE KEY-----`            |
| Passwords           | `password=`, `passwd:`, `pwd=`               |
| Tokens              | `token=`, `bearer ...`, `auth_token`         |
| Connection strings  | `postgres://user:pass@`, `mongodb+srv://`    |
| AWS credentials     | `aws_access_key_id`, `aws_secret_access_key` |
| Environment secrets | `.env` files with real values                |

**Severity:** CRITICAL - Block sharing until resolved

### 2. Personal Identifiers (HIGH)

**Flag for review - may need anonymization:**

| Pattern                       | Examples                       |
| ----------------------------- | ------------------------------ |
| Email addresses               | `user@domain.com`              |
| Phone numbers                 | `+1-555-...`, `(555) 123-4567` |
| Names (from context file)     | Your name, family names        |
| Usernames (from context file) | Social handles, login names    |
| Physical addresses            | Street addresses, ZIP codes    |

**Severity:** HIGH - Review and anonymize or confirm OK to share

### 3. Private URLs (HIGH)

**Flag - often reveal private resources:**

| Pattern                | Examples                                  |
| ---------------------- | ----------------------------------------- |
| Notion URLs            | `*.notion.site/*`, `notion.so/*/...`      |
| Google Docs (private)  | `docs.google.com/document/d/...`          |
| Internal tools         | `*.internal.*`, `*.corp.*`, `localhost:*` |
| Private repos          | `github.com/[private-org]/...`            |
| Figma/design files     | Private design URLs                       |
| Calendar/meeting links | Zoom personal rooms, Calendly             |

**Severity:** HIGH - Replace with placeholder or remove

### 4. Local Paths (MEDIUM)

**Flag - reveal system structure and username:**

| Pattern            | Examples                                          |
| ------------------ | ------------------------------------------------- |
| Home directory     | `/Users/username/`, `/home/username/`             |
| iCloud paths       | `~/Library/Mobile Documents/com~apple~CloudDocs/` |
| Dropbox/OneDrive   | `~/Dropbox/`, `~/OneDrive/`                       |
| App-specific paths | `~/Library/Application Support/[App]/`            |
| Windows user paths | `C:\Users\username\`                              |

**Severity:** MEDIUM - Replace with generic placeholder like `~/path/to/...` or `[YOUR_PATH]`

### 5. Infrastructure & Security (MEDIUM-HIGH)

**Flag - could enable attacks or reveal architecture:**

| Pattern            | Examples                                   |
| ------------------ | ------------------------------------------ |
| Internal IPs       | `10.x.x.x`, `192.168.x.x`, `172.16-31.x.x` |
| Internal hostnames | `*.internal`, `*.local`, `*.corp`          |
| Database hosts     | Specific DB server addresses               |
| Cloud resource IDs | AWS account IDs, GCP project IDs           |
| CI/CD specifics    | Internal Jenkins/GitHub Actions URLs       |

**Severity:** MEDIUM-HIGH depending on context

### 6. Business & Proprietary (MEDIUM)

**Flag if context file specifies - varies by situation:**

| Pattern                | Examples                          |
| ---------------------- | --------------------------------- |
| Client names           | (from context file)               |
| Internal project names | Codenames, internal product names |
| Pricing/financial      | Revenue figures, pricing tiers    |
| Strategy content       | Competitive analysis, roadmaps    |
| Internal comms         | Slack channel names, team names   |

**Severity:** MEDIUM - Requires judgment

---

## Scan Protocol

### Phase 1: Load Context

1. Check for `~/.claude/sensitive-content-context.md`
2. If exists: load personal patterns and terms
3. If not: use generic detection only, note limitations

### Phase 2: File Discovery

1. If path is a file: scan that file
2. If path is a directory:
   - Find all text-based files (md, txt, json, yaml, yml, toml, js, ts, py, sh, etc.)
   - Respect `.gitignore` if present
   - Skip binary files, node_modules, .git, etc.
3. Report file count and types found

### Phase 3: Pattern Scanning

For each file, scan for all detection categories. Use:

- Regex patterns for structured data (emails, IPs, API keys)
- Context file terms for personal/business content
- Heuristics for paths and URLs

### Phase 4: Findings Report

Generate structured report:

```markdown
# Sensitive Content Scan Report

**Path scanned:** [path]
**Files scanned:** [count]
**Scan date:** [timestamp]

## Summary

| Severity | Count | Action Required         |
| -------- | ----- | ----------------------- |
| CRITICAL | X     | Must fix before sharing |
| HIGH     | X     | Review and sanitize     |
| MEDIUM   | X     | Consider sanitizing     |
| LOW      | X     | Informational           |

## CRITICAL Findings

### [Category]: [Brief description]

**File:** `path/to/file.md`
**Line:** [line number]
**Content:** `[snippet with sensitive part highlighted]`
**Risk:** [Why this is sensitive]
**Suggested fix:** [How to sanitize]

---

[Repeat for each finding, grouped by severity]

## Recommendations

1. [Prioritized action items]
2. [...]

## Files Cleared

These files contained no detected sensitive content:

- [list of clean files]
```

---

## Output Modes

### Default: Full Report

Complete findings with context and suggestions.

### Summary Mode

`/sensitive-content-scanner [path] --summary`
Just the summary table and critical findings.

### JSON Mode (for automation)

`/sensitive-content-scanner [path] --json`
Machine-readable output for piping to other tools.

---

## Integration with Other Skills

This skill is designed to be called by other skills/workflows:

**Example - called by sync-skills-public:**

```
1. sync-skills-public invokes sensitive-content-scanner on ~/.claude/skills/
2. Scanner returns findings
3. sync-skills-public uses findings to guide sanitization
4. Scanner re-runs on output to verify clean
```

When called programmatically, return structured findings that the calling skill can act on.

---

## Limitations

- **Cannot detect everything**: Novel patterns or context-dependent sensitivity may be missed
- **False positives**: Some patterns (like example UUIDs) may flag incorrectly
- **Requires context for personal content**: Without the context file, personal names/terms won't be detected
- **No semantic understanding**: Can't detect if content is "confidential" without explicit markers

**Always do a final human review before sharing sensitive materials.**

---

## Quick Reference

| I want to...                  | Command                                         |
| ----------------------------- | ----------------------------------------------- |
| Scan a directory              | `/sensitive-content-scanner ./path/`            |
| Scan a single file            | `/sensitive-content-scanner ./file.md`          |
| Quick summary only            | `/sensitive-content-scanner ./path/ --summary`  |
| Check my skills before export | `/sensitive-content-scanner ~/.claude/skills/`  |
| Set up personal detection     | Create `~/.claude/sensitive-content-context.md` |
