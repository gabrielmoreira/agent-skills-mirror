# Registry Format (`registry.json`)

## Purpose

The local registry is a user-maintained JSON file that maps skill names to their
source GitHub repositories. It is consulted at **Step 4** of the provenance resolution
order (see `references/provenance-routing.md`) after frontmatter, manifests, and
vendored config all fail to identify the destination.

---

## Location

| Source | Path |
|---|---|
| Default | `$SKILL_REFLECT_HOME/registry.json` (default: `~/.skill-reflect/registry.json`) |
| Config override | `destination.registryMapPath` in `skill-reflect.config.json` |

If `destination.registryMapPath` is set in the config, it takes precedence over the
default path.

---

## Schema

A flat JSON object. Each key is a skill name (exact, case-sensitive). The value is
either a plain string or an object:

### String form (simple)

```json
{
  "<skill-name>": "owner/repo"
}
```

### Object form (with optional ref)

```json
{
  "<skill-name>": {
    "repo": "owner/repo",
    "ref": "main"
  }
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `repo` | string | Yes | `owner/repo` on GitHub (no scheme, no `.git`) |
| `ref` | string | No | Branch or tag; informational only (issues are always filed on the default branch) |

Both forms may be mixed in the same file. See `examples/registry.example.json`.

---

## Precedence vs Config

The full resolution order (highest → lowest priority):

1. `source_repo` in the skill's **SKILL.md frontmatter** (installer-written) — **Confirmed**
2. `repository` / `source_repo` field in a **plugin/extension manifest** — **Confirmed/Likely**
3. `destination.repo` in **vendored-mode config** — **Confirmed**
4. **`registry.json`** lookup ← this file — **Likely**
5. Ask the user / local-only fallback

The registry is only consulted after steps 1–3 all fail.

---

## Confidence Note

Registry entries are classified as **Likely** (not **Confirmed**) because they are
user-maintained and not cryptographically attested by an installer. This is still
sufficient to proceed with a strict send flow once the user grants destination-specific
remote-send authorization.

---

## Maintaining the Registry

Add an entry when:

- A skill was installed without provenance metadata (no `source_repo` in SKILL.md).
- The skill author's repo is known but absent from any manifest.
- You use a skill frequently and want reliable routing without being prompted.

When `skill-reflect` offers to persist a repo supplied during remote routing, that registry
change is a separate local-write action. It must preview the exact skill-name → `owner/repo`
mapping and receive explicit confirmation; approval to send an issue does not authorize a
registry edit.

Edit the file directly — it is plain JSON:

```sh
# Default location
$EDITOR ~/.skill-reflect/registry.json

# Custom path (from skill-reflect.config.json → destination.registryMapPath)
$EDITOR <destination.registryMapPath>
```

Create the file (and `~/.skill-reflect/` directory) if it does not yet exist:

```sh
mkdir -p ~/.skill-reflect
echo '{}' > ~/.skill-reflect/registry.json
```

---

## Notes

- Skill names are matched **exactly** (case-sensitive). Use the canonical name as
  reported by the agent or as it appears in the skill's `SKILL.md` `name:` field.
- The resolver silently skips missing or malformed registry files — a parse error
  never blocks the skill from running.
- The registry file is never read by the extension/automation layer; only the core
  skill invokes the provenance resolver.
