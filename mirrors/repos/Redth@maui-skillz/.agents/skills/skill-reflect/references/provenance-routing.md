# Provenance Routing

`skill-reflect` must route feedback to the **correct upstream repository** so that a
`gh issue create` call lands in the right place. Routing must **never guess**: if
provenance cannot be resolved with at least `Likely` confidence, fall back to a local
`.md` artifact and note the suggested destination for manual action.

---

## Scope gate (CONTRACT §9)

Automatic review candidates must be **distributed** — installed from a plugin,
marketplace, or external repo. An explicit user request may review a local/user-owned
skill. The skills `skill-reflect` and `skill-reflect-auto` are always excluded.

Local review does not imply remote eligibility. Technical-local output is always
`remote_eligible: false`; regenerate strict content before any later send.

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
following files in the skill's installation directory for a repo URL. The resolver accepts
explicit manifest paths and also performs a bounded, local-only search from the supplied
`SKILL.md` up through at most eight ancestors (or to an explicit installation root):

- `.claude-plugin/plugin.json`
- `plugin.json`
- `.claude-plugin/marketplace.json`
- `marketplace.json`

Do not probe package managers, search unrelated global directories, make network calls, or
display any installation path.

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

A marketplace file is an object with a **`plugins[]` array**. It may identify the
marketplace repository at the top level; each plugin may list multiple skills:

```json
{
  "name": "example-marketplace",
  "repository": "https://github.com/owner/skills",
  "plugins": [
    {
      "name": "skill-bundle",
      "source": "./",
      "skills": ["./skills/my-skill", "./skills/other-skill"],
      "version": "1.0.0"
    }
  ]
}
```

Match the entry whose **`name`** equals the requested skill/plugin name. For multi-skill
plugins, also match the basename of each string in `skills[]` (for example,
`./skills/my-skill` or `./skills/my-skill/SKILL.md`). Never use a marketplace's top-level
repository unless an entry matches. Then read the entry's `source` (or an explicit
`repository`/`homepage`, which win if present):

| `source` form | Meaning | Result |
|---|---|---|
| `"https://github.com/owner/repo"` / `"owner/repo"` | absolute repo | `owner/repo` → **Likely** |
| `{ "source": "github", "repo": "owner/repo" }` (object) | absolute repo | `owner/repo` → **Likely** |
| `"./plugins/x"` / `"../x"` / `"/abs/x"` (**relative path**) | plugin lives **inside the marketplace repo itself** | provenance = the **marketplace repo** |

**Relative `source` is the common case.** Resolve the marketplace repo in this order:

1. `--marketplace-repo owner/repo` (if already known),
2. the top-level marketplace `repository` or `homepage` field, or
3. `--allow-git` so the resolver derives it from `git -C <dir-of-marketplace.json>
   config --get remote.origin.url`.

If neither is available, the resolver returns
`{"source": "marketplace-relative", "confidence": "Possible"}` (with a `note`) —
which does **not** clear the never-guess bar; ask the user before sending.

Per-plugin **`.claude-plugin/plugin.json`** (when present) may carry `repository`,
`source`, or `homepage`; treat those as **Likely**. If both a `plugin.json` and a
`marketplace.json` are available, prefer an explicit `repository` on `plugin.json`.

The resolver may return display-safe metadata alongside the repository:
`install_scope`, `plugin`, `marketplace`, `version`, `ref`, and `sha`. It validates and
bounds those values and never returns the installation root or manifest path. Callers may
provide a trusted `project`, `user`, `vendored`, or `unknown` install scope; otherwise the
resolver classifies only known project/user locations and reports `unknown` when uncertain.

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

### Step 5 — Remote-intent clarification / local fallback

**Confidence: `None` → human input**

If no prior step yielded a result:

1. In analysis/artifact mode, report `unknown` and continue locally. Do not interrupt
   the review with a provenance question.
2. Only after explicit remote-send intent, display what was checked and ask the user
   to confirm or supply an `owner/repo` destination.
3. If the user provides one → treat as **Likely** and continue with the send flow.
4. Offer registry persistence only as a separate local-write action. Show the exact skill
   name and `owner/repo` mapping and obtain explicit confirmation before changing the
   registry; send authorization does not authorize this write.
5. If the user declines or is unsure → keep or write a **local-only artifact** in
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
Require at least `Likely` + destination-specific remote-send authorization before any `gh` call.
When in doubt, produce a local artifact only.

---

## The Send Flow

After provenance is resolved, strict content is ready, and the user has explicitly
requested remote filing:

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

If `--fail-on-secret` exits non-zero, no output file is written; redraft. Otherwise
show the exact scrubbed issue body, title, destination, provenance confidence, and
scrub report.

### 3. Obtain remote-send authorization and file

Ask for fresh authorization for that exact body and destination. Silence or ambiguity
means no send. Then run:

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
Review authorized for announced scope?
├─ No  → stop; write and send nothing
└─ Yes
    ├─ Analysis mode → scrubbed chat findings; stop
    └─ Artifact/remote mode
        └─ Local-write authorized?
            ├─ No  → show summary preview; ask once
            └─ Yes → write scrubbed artifact
                └─ Explicit remote intent?
                    ├─ No  → stop locally
                    └─ Yes
                        └─ strict + remote_eligible + provenance ≥ Likely?
                            ├─ No  → regenerate/resolve or remain local
                            └─ Yes → show exact body + destination
                                └─ remote-send authorized?
                                    ├─ No  → remain local
                                    └─ Yes → gh issue create
```

Remote mode uses a strict local artifact as the durable source. Analysis mode never
creates one.
