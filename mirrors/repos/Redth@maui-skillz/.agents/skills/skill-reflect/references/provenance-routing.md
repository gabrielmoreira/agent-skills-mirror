# Provenance Routing

`skill-reflect` must route feedback to the **correct upstream repository** so that a
`gh issue create` call lands in the right place. Routing must **never guess**: if
provenance cannot be resolved with at least `Likely` confidence, fall back to a local
`.md` artifact and note the suggested destination for manual action.

---

## Distributed-Skill Gate (CONTRACT §9)

Before entering the resolution order, confirm the skill is **distributed** — installed
from a plugin, marketplace, or external repo with resolvable provenance outside the
user's own project. Never file feedback about the user's own in-repo skills unless
explicitly scoped in via `scope.skills`. The skills `skill-reflect` and
`skill-reflect-auto` are always excluded per `scope.excludeSkills`.

If the skill does not qualify as distributed, skip the entire send flow.

---

## Resolution Order

Stop at the **first confident hit**.

---

### Step 1 — `SKILL.md` YAML Frontmatter

**Confidence: `Confirmed`**

When a skill is installed via the `gh skill` CLI (or equivalent installer), the
installer writes a YAML frontmatter block into the skill's `SKILL.md`. The keys are:

| Key | Description |
|---|---|
| `source_repo` | `owner/repo` — the GitHub repository the skill was installed from |
| `source_ref` | Branch or tag at install time (e.g., `main`, `v1.2.0`) |
| `source_sha` | Commit SHA at install time |

**How to find the SKILL.md:**

| Agent | Typical path |
|---|---|
| Copilot CLI | `~/.copilot/skills/<skill-name>/SKILL.md` |
| Project-local | `.github/skills/<skill-name>/SKILL.md` |
| Claude Code | `~/.claude/plugins/<plugin-name>/SKILL.md` |

Parse the `---`-delimited YAML frontmatter at the top of the file. Extract
`source_repo`. If present and non-empty, this is the authoritative destination.

**Resolver field:** `source_repo` (string, `owner/repo` form)

---

### Step 2 — Plugin / Marketplace Manifest

**Confidence: `Confirmed` (if `source_repo` field written by installer) / `Likely` (if `repository` or other author-set field)**

Different agents ship a manifest file alongside installed skills/plugins. Check the
following files in the skill's installation directory for a repo URL:

#### Copilot CLI — no runtime manifest (use frontmatter or registry)

**Verified:** Copilot CLI **extensions are auto-discovered** — the CLI scans for a
subdirectory containing `extension.mjs` and registers hooks/tools *programmatically*
via the session options passed to `joinSession()`. **There is no manifest file the
CLI reads**, and therefore **no manifest field that records a source repo.** Any
`extension.json` you find (including `skill-reflect-auto/extension.json`) is
**metadata-only** and is *not* consumed by the runtime, so do not treat it as an
authoritative provenance source.

Consequently, for a skill installed under Copilot CLI, provenance comes from:

| Preferred source | Step | Confidence |
|---|---|---|
| `source_repo` in the skill's `SKILL.md` frontmatter (installer-written) | Step 1 | Confirmed |
| Local registry map entry | Step 4 | Likely |
| Ask the user | Step 5 | — |

> If a Copilot CLI plugin/marketplace records its install source elsewhere in the
> Copilot config, that MAY be added as a future resolver input — but it is **not**
> an extension manifest field. Until verified, rely on frontmatter + registry.

#### Claude Code — `.claude-plugin/marketplace.json` and per-plugin `plugin.json`

**Verified** against real `.claude-plugin/marketplace.json` files:

A marketplace file is an object with a **`plugins[]` array**; each entry looks like:

```json
{ "plugins": [
  { "name": "my-skill", "source": "./plugins/my-skill",
    "description": "...", "version": "1.0.0", "author": "...", "category": "..." }
] }
```

Match the entry whose **`name`** equals the skill/plugin name, then read its
`source` (or an explicit `repository`/`homepage`, which win if present):

| `source` form | Meaning | Result |
|---|---|---|
| `"https://github.com/owner/repo"` / `"owner/repo"` | absolute repo | `owner/repo` → **Likely** |
| `{ "source": "github", "repo": "owner/repo" }` (object) | absolute repo | `owner/repo` → **Likely** |
| `"./plugins/x"` / `"../x"` / `"/abs/x"` (**relative path**) | plugin lives **inside the marketplace repo itself** | provenance = the **marketplace repo** |

**Relative `source` is the common case** and needs a second step, because the
`owner/repo` is *not in the file*. Resolve the marketplace repo by either:

1. passing `--marketplace-repo owner/repo` (if you already know it), or
2. `--allow-git` so the resolver derives it from `git -C <dir-of-marketplace.json>
   config --get remote.origin.url`.

If neither is available, the resolver returns
`{"source": "marketplace-relative", "confidence": "Possible"}` (with a `note`) —
which does **not** clear the never-guess bar; ask the user before sending.

Per-plugin **`.claude-plugin/plugin.json`** (when present) may carry `repository`,
`source`, or `homepage`; treat those as **Likely**. If both a `plugin.json` and a
`marketplace.json` are available, prefer an explicit `repository` on `plugin.json`.

#### URL → `owner/repo` extraction rule (all manifest sources)

Given a field value of any of these forms, extract `owner/repo`:

| Input | Extracted |
|---|---|
| `"owner/repo"` | `owner/repo` |
| `"https://github.com/owner/repo"` | `owner/repo` |
| `"https://github.com/owner/repo.git"` | `owner/repo` |
| `{"type":"git","url":"https://github.com/owner/repo.git"}` | `owner/repo` |

Only accept `github.com` URLs. Non-GitHub URLs → skip this step (local-only fallback).

---

### Step 3 — Vendored Config (`destination.repo`)

**Confidence: `Confirmed`**

When `skill-reflect.config.json` has `"mode": "vendored"` and
`"destination": { "repo": "owner/repo" }`, the destination is **hardcoded** to that
repo. This is the pattern used when a plugin vendor bundles `skill-reflect` inside
their own plugin repo and wants all feedback routed to them.

**Config field:** `destination.repo` (string, `owner/repo`) — only used when
`mode == "vendored"`.

---

### Step 4 — Local Registry Map (`registry.json`)

**Confidence: `Likely`**

A user-maintained JSON file maps skill names to source repos. See
`references/registry-format.md` for the full schema.

| Source | Path |
|---|---|
| Default | `$SKILL_REFLECT_HOME/registry.json` (default `~/.skill-reflect/registry.json`) |
| Config override | `destination.registryMapPath` in `skill-reflect.config.json` |

If the skill name matches a key, use the mapped repo. Because this file is
user-maintained (not installer-attested), confidence is **Likely**.

---

### Step 5 — Ask the User / Local-Only Fallback

**Confidence: `None` → human input**

If no prior step yielded a result:

1. **Ask the user.** Display what was found (if anything partial) and ask them to
   confirm or supply an `owner/repo` destination.
2. If the user provides one → treat as **Likely**; continue with the send flow.
3. If the user declines or is unsure → write a **local-only artifact** in
   `.skill-feedback/` with the `## Routing` section set to
   `Suggested destination: unknown — manual send required`.

---

## Confidence Levels

| Level | Meaning |
|---|---|
| `Confirmed` | Installer-written SKILL.md frontmatter or explicit `vendored` config |
| `Likely` | Manifest `repository`/`source` field, or user registry entry |
| `Possible` | Inferred from heuristics (partial URL match, etc.) — **do not auto-file** |
| `None` | No provenance found |

**Never-guess rule:** Confidence of `Possible` or `None` blocks the send flow.
Require at least `Likely` + explicit second-consent approval before any `gh` call.
When in doubt, produce a local artifact only.

---

## The Send Flow

After provenance is resolved **and** the user passes the **second consent gate**
(first gate = "review this feedback?"; second gate = "send to the skill author?"):

### 1. Render the issue body

Populate `skill-reflect/templates/github-issue.md` with the findings from the
current artifact. The rendered body must already be PII-free (model-scrubbed at
generation time).

### 2. Run the deterministic scrubber as a backstop

```sh
python3 skill-reflect/scripts/scrub.py .skill-feedback/<artifact>.md \
  --out .skill-feedback/<artifact>.issue-body.md \
  --report \
  --fail-on-secret
```

Show the scrub report to the user. If `--fail-on-secret` exits non-zero, abort and
tell the user.

### 3. File the issue

```sh
gh issue create \
  --repo <owner/repo> \
  --title "[<skill>] Field feedback: <short summary>" \
  --body-file .skill-feedback/<artifact>.issue-body.md \
  --label "skill-feedback"
```

> **Important constraints:**
> - The skill/extension itself **never makes network calls**. Only this explicit,
>   user-approved `gh` invocation touches the network.
> - `gh issue create` uses the user's pre-authenticated `gh` session. No tokens are
>   stored or transmitted by `skill-reflect`.
> - The `--body-file` argument always points to the **scrubbed** rendering, never the
>   raw artifact.

### 4. Update the artifact

After a successful `gh issue create`, update the local artifact's frontmatter:

```
consent: sent:<owner/repo>#<issue-number>
```

Delete the ephemeral `<artifact>.issue-body.md` file.

If `gh issue create` fails (network error, repo not found, permissions), do **not**
retry automatically. Inform the user; leave `consent: review-only` in the artifact.

---

## Decision Tree

```
Is the skill distributed (§9)?
├─ No  → skip entirely (or prompt user to scope in)
└─ Yes
    └─ Resolve provenance (steps 1–4)
        ├─ Confidence ≥ Likely?
        │   ├─ No  → Step 5: ask user
        │   │           ├─ User supplies repo → treat as Likely, continue ↓
        │   │           └─ User declines     → LOCAL ARTIFACT ONLY
        │   │                                   Routing: "destination unknown"
        │   └─ Yes ↓
        └─ User passes first consent gate?
            ├─ No  → LOCAL ARTIFACT ONLY
            └─ Yes → generate & scrub artifact
                        └─ User passes second consent gate?
                            ├─ No  → LOCAL ARTIFACT ONLY
                            └─ Yes → gh issue create --repo <owner/repo> …
                                       update artifact: consent: sent:<owner/repo>#<n>
                                       delete ephemeral issue-body file
```

> A local artifact is **always** created first. The send step is additive, not a
> replacement.
