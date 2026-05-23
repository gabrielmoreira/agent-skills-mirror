---
name: unity-skills
description: "Unity Editor automation via REST API — create scripts, analyze scenes, manage assets, control editor, orchestrate workflows, run batch jobs, and route by Unity version. Triggers: Unity, Unity Skills, in Unity, automate Unity, Unity editor automation, create Unity script, scene summary, analyze Unity scene, Unity GameObject, Unity prefab, Unity asset, Unity workflow, Unity batch, grant Unity skill, Unity allowlist, Unity skill schema, multi-instance Unity, set Unity version, Unity自动化, Unity编辑器, Unity技能, 操作Unity, 在Unity中, Unity工作流, Unity批处理, Unity授权, Unity白名单, Unity多实例, Unity实例切换, Unity场景分析."
---

# Unity Skills

Use this skill when the user wants to automate the Unity Editor through the local UnitySkills REST server.

## Canonical Schema First

For exact skill names, parameters, defaults, and returns, query schema first:
- `unity_skills.get_skill_schema()`
- `GET /skills/schema`
- `GET /skills?category=<Category>`

Use module `SKILL.md` files for routing guidance, guardrails, and minimal examples, not as the canonical source of exact signatures.

Current snapshot: `750` REST skills, `51` functional source modules, `68` module documentation directories (`49` REST/module docs + `19` advisory docs), Unity `2022.3+`, default timeout `15 minutes`.

Python helper: `unity-skills/scripts/unity_skills.py`

## Operating Mode (v1.9.0+)

Operating mode is a **server-side permission gate**, configured in `Window > UnitySkills > Server` and persisted in EditorPrefs per-machine. It is not an AI routing policy and **cannot** be switched via chat or REST — chat-side trigger words no longer apply.

### Boot Handshake

On session start (or before the first skill call), call `GET /health` and read:

- `currentMode` — `"approval"` / `"auto"` / `"bypass"`
- `panelApprovalRequired` — only meaningful under Approval; selects the grant channel
- `pendingCount` — outstanding grant requests

### Three Modes (aligned with Claude Code permission modes)

| Mode | Claude Code 类比 | FullAuto skill | Auto-detected NeverInSemi skill |
|---|---|---|---|
| **Approval** | `default` / `plan` | First call returns `MODE_RESTRICTED`; run the grant protocol below | `MODE_FORBIDDEN` |
| **Auto** | `acceptEdits` | Executes directly (audit written); **you must self-assess** sensitive cases | `MODE_FORBIDDEN` |
| **Bypass** | `bypassPermissions` | Executes directly | Executes directly (only `ConfirmationToken` still gates high-risk) |

`NeverInSemi` is derived automatically by `IsForbiddenInSemi()` — there is no manual marker. See "Skill Mode Annotation" below.

### Approval Mode Grant Protocol

Approval grants are **single-shot one-step execution**: a successful `/permission/grant` call runs the original skill server-side and returns the result in the same response. You do **not** retry the skill after grant. Grants are **not** persisted — calling the same skill a second time will hit `MODE_RESTRICTED` again and must go through grant again. If the user wants permanent bypass for a skill, direct them to the Allowlist (see below).

On `MODE_RESTRICTED`, branch on `details.approvalChannel`:

**Dialog channel** (`"dialog"`, default — `panelApprovalRequired = false`)

1. Tell the user in chat: "要调用 `<skill>` 来 `<目的>`，参数 `<argsSummary>`，请求码 #`<token 前 6 位>`，是否允许？"
2. After explicit user consent, call `POST /permission/grant { skill, token, args }` **once**
3. On success, the response contains `{ ok: true, executed: true, skill, result: <Execute output> }` — the skill has already run server-side. Consume `result` directly; **do not call the original skill endpoint again**

**Panel channel** (`"panel"`, when `panelApprovalRequired = true`)

1. Tell the user in chat: "要调用 `<skill>` 来 `<目的>`，请到 `Window > UnitySkills` 面板的 Pending Grant Requests 点 `[Approve]`（请求码 #`<token 前 6 位>`）"
2. **Do not call `/permission/grant` yet** — calling it before the user clicks Approve returns `GRANT_PENDING_APPROVAL`
3. Poll `GET /permission/status?token=<token>` to observe the request state (look at `focus.approvedByPanel`)
4. Once the user has pressed Approve in the panel, call `POST /permission/grant { skill, token, args }` **once** — this takes the Granted branch and triggers one-step execution, returning `{ ok: true, executed: true, skill, result }`. Consume `result` directly; **do not call the original skill endpoint again**

> Note: panel approval no longer auto-routes the result back to the AI. The Approve click only flips the request into the Granted state; AI must follow up with one `/permission/grant` call to fetch the execution result.

On `MODE_FORBIDDEN`: the skill is auto-classified as NeverInSemi (Delete / Domain Reload / Play Mode / high-risk / fallback list). It is callable only under Bypass, **or** if the user has explicitly added it to the Allowlist (see below). **Do not attempt the grant flow** — tell the user the action requires Bypass mode, an Allowlist entry, or offer an alternative skill.

### Allowlist (user-managed permanent bypass)

The Allowlist is a **user-managed** permanent whitelist of skill names, configured in `Window > UnitySkills > Server` settings drawer (Allowlist Skills section / `+ Add Skill` button). It is independent of Approval grants:

- Allowlisted skills execute directly under any mode — the server skips the Approval/MODE_RESTRICTED gate
- **An Allowlist entry overrides MODE_FORBIDDEN** for that skill (covers Delete / MayEnterPlayMode / MayTriggerReload / `RiskLevel="high"`). This is intentional: the user has explicitly opted in
- **Allowlist does NOT bypass the high-risk ConfirmationToken gate.** When `RequireConfirmation` is enabled (Settings drawer → Runtime → Require Confirmation), high-risk skills still require the `_confirm` token two-step handshake even if allowlisted — Allowlist only covers the mode/approval channel, not the per-call safety confirmation
- The list is **opaque to the AI**: allowlisted skills look like normal successful calls, never returning `MODE_RESTRICTED`
- **The AI should not call `/permission/allowlist/add` on its own initiative.** Only call it when the user has explicitly authorized a session-scoped bulk add (e.g. "把这几个 skill 加白名单方便我后面批量调"); otherwise direct the user to add entries through the panel
- Allowlist endpoints: `GET /permission/allowlist` / `POST /permission/allowlist/add` / `POST /permission/allowlist/remove` (body `{skill}` or `{all: true}`)

> The previous `GrantedSkills` semantics ("after one grant the skill is permanently auto-allowed") has been removed. Grants are now single-shot. Permanent allow == Allowlist; one-shot approval == grant.

### Auto Mode Self-Assessment

Under Auto, FullAuto skills run directly. You **must pause and confirm with the user** in chat when any of the following apply:

- Batch operation touching ≥ `5` objects
- Prefab apply / scene-level mutation / asset overwrite
- Dry-run shows irreversible changes (deletes, overrides, cascading edits)

This confirmation is a chat-level check (explain plan + risk + ask), independent of the server-side mode gate. The server will not stop you in Auto — the audit log records the call regardless.

### Relationship with `ConfirmationTokenService`

Mode authorization (persistent, per-skill) and `ConfirmationToken` (single-shot, per-call) are **orthogonal**:

- Mode check runs first; if allowed, the existing confirmation gate may still issue `CONFIRMATION_REQUIRED` with a dry-run for `RiskLevel=high` or `Operation.Delete` skills
- Granted skills still flow through `ConfirmationToken` when triggered — continue using the original dry-run → user consent → retry with `_confirm` loop
- Neither replaces the other

### Skill Mode Annotation

The REST surface (~`750` skills) is partitioned by `[UnitySkill]` `Mode` and runtime metadata. Use schema endpoints for the canonical list:

| Annotation | Count | Source |
|---|---|---|
| `SkillMode.SemiAuto` | ~`270` | Manually annotated. Covers read-only / query / analyze skills across `script` / `perception` / `scene` / `editor` / `asset` / `workflow` / `debug` / `console` and most modules' info / list / get / find skills |
| Auto-detected NeverInSemi | ~`40+` | `IsForbiddenInSemi()` derives from `Operation.Delete`, `MayEnterPlayMode`, `MayTriggerReload`, `RiskLevel="high"`, plus an explicit fallback list (`scene_clear`, `scene_new`, `batch_apply`) |
| `SkillMode.FullAuto` (default) | remainder | Unannotated skills (write / mutate by default). Approval requires grant; Auto / Bypass execute directly |

SemiAuto category overview (use `GET /skills?category=<Category>` for the exact callable list; only SemiAuto skills are listed below — write skills in the same modules remain FullAuto):

| Category | Modules | Representative SemiAuto Skills |
|----------|---------|--------------------------------|
| Script | script | script_read, script_list, script_get_info, script_find_in_file, script_get_compile_feedback |
| Perception | perception | scene_analyze, scene_context, scene_health_check, scene_find_hotspots, project_stack_detect |
| Scene Mgmt | scene | scene_get_info, scene_get_hierarchy, scene_get_loaded, scene_find_objects |
| Editor | editor | editor_get_context, editor_get_state, editor_get_selection, editor_get_tags, editor_get_layers |
| Asset Basic | asset | asset_find, asset_get_info |
| Workflow | workflow | workflow_list, workflow_session_list, workflow_session_status, workflow_plan; use workflow/batch helpers for planning, preview, jobs, and rollback, not free-form scene construction |
| Debug | debug, console | debug_check_compilation, debug_get_errors, debug_get_system_info, debug_get_memory_info, console_get_logs |
| Advisory | 19 modules | Design-only guidance modules (no REST skills) |

## Core Rules

1. If the user specifies a Unity version or editor line, set instance/version routing first with `unity_skills.set_unity_version(...)`.
2. Under Auto / Bypass modes (or after grant under Approval), prefer `*_batch` skills whenever the task touches `2+` objects.
3. For multi-step editor mutations, prefer workflow wrappers instead of free-form mutation sequences.
4. Script edits, define changes, package changes, some imports, and test template creation can trigger compilation or Domain Reload. Wait and retry on transient unavailability.
5. `test_*` skills are async. They return a `jobId` and must be polled with `test_get_result(jobId)`.

## Route

- Module index: `unity-skills/skills/SKILL.md`
- Script guidance: `unity-skills/skills/script/SKILL.md`
- Advisory guidance: load advisory modules on demand from the module index

> **XR rule**: Before calling any `xr_*` skill in a session, load `skills/xr/SKILL.md` first. XR is reflection-based; wrong property names can fail silently.
