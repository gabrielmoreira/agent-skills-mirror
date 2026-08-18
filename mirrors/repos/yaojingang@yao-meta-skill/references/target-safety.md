# Target Safety

## Invariant

Keep three locations distinct during authoring:

- `engine_root`: the source or installed directory that contains Yao Meta Skill.
- `target_root`: the explicitly selected Skill that may receive task changes.
- `state_root`: the user-level cache and telemetry location.

Treat `engine_root` as read-only during work on another Skill. Allow `target_root == engine_root` only after explicit self authorization.

## Target Lock

Before any operation that may write:

1. Obtain an explicit target path from the user or command. A CLI caller may pass `.` explicitly.
2. Resolve the canonical absolute path, including symbolic links.
3. Read the target identity from `manifest.json` or `SKILL.md` frontmatter when available.
4. Record the target path, Skill name, command policy, and allowed write root in the working context.
5. Stop with `target-required` when the path is missing.
6. Stop with `self-target-blocked` when the path or identity resolves to `yao-meta-skill` without `--self`.
7. Resolve relative report, package, registry, telemetry, install, and command-specific write destinations against the locked target.
8. Stop with `self-target-blocked` when any declared write destination enters the engine subtree without `--self`.

When the user asks to modify another Skill and the resolved target points to Yao Meta Skill, stop before running a writer and surface the conflicting path.

## CLI Policies

- Target-specific commands require an explicit `skill_dir`.
- Workspace commands require an explicit `--workspace-root`.
- Yao maintenance commands require `--self`.
- `init` and `quickstart` resolve their output directory against the caller working directory and may create a new target only when its destination is absent or empty.
- Creating a new Skill inside the Yao source or installed package requires `--self`.
- Global diagnostics may run without a Skill target when they do not write into a Skill source or install directory.
- Standalone writer scripts require their `skill_dir` positional argument. Prefer `scripts/yao.py` for agent-facing operations because it applies the unified target policy.

Stable safety failures use exit code `2` and one of these codes:

- `target-required`
- `target-invalid`
- `self-target-blocked`
- `target-policy-missing`
- `target-exists`

## Runtime State

Update-check cache belongs in the platform user cache directory. Opt-in CLI telemetry belongs in the platform user state directory. `XDG_CACHE_HOME` and `XDG_STATE_HOME` take precedence when present. `YAO_CLI_TELEMETRY_EVENTS` remains the explicit telemetry destination override.

Legacy `.yao/update-check.json` and `reports/telemetry_events.jsonl` files may remain available as local evidence. New default writes must not update them.

## Package Source Boundary

For a Git-backed Skill, including a Skill nested inside a larger repository, build archives from tracked files plus explicitly allowed untracked source roots such as `scripts/`, `references/`, and `tests/`. Exclude untracked reports, registry evidence, portfolio output, and external submission drafts until they are intentionally promoted into version control. Always exclude nested Skills, local state, caches, bytecode, platform noise, and generated package directories. Fail closed when Git metadata is present but Git source enumeration is unavailable.

Before replacing a package output directory, verify that every existing entry matches the cross-packager's generated manifest, adapter, and archive layout. Preserve and reject any non-empty destination that contains unmanaged files or a foreign manifest.

## Verification

For target-safety changes, verify:

- missing targets fail before a command handler runs;
- external target work leaves the Yao source and installed package byte-identical;
- symbolic links cannot bypass self detection;
- self maintenance succeeds only with `--self`;
- repeated initialization preserves all existing bytes;
- relative outputs and default package directories resolve inside the locked target;
- declared output paths cannot enter the Yao engine subtree without `--self`;
- command-specific write paths such as Atlas reports, approval ledgers, generated pattern reports, and annotation templates obey the same guard;
- Git-governed archive filtering works for repository roots and nested Skill directories;
- package regeneration preserves non-empty unmanaged output directories;
- user cache and state paths receive operational files;
- every CLI subcommand has a declared target policy;
- standalone writer scripts have no implicit `skill_dir="."` default.
