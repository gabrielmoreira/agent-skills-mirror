# Plan: Projects Feature for Moltis

## Overview

Add a "Projects" concept so sessions can be bound to a codebase directory, automatically loading `CLAUDE.md` and `AGENTS.md` context files, injecting a custom system prompt, and optionally creating git worktrees for session isolation.

## Ideas from Conductor

Conductor (conductor.build) uses "workspaces" backed by git worktrees. Key ideas to adopt:

- **Branch = identity**: Each session worktree gets a branch that the agent can rename to reflect the work (e.g. `moltis/add-auth-flow`), not just a UUID slug
- **One branch per session**: A branch can only be checked out in one workspace at a time — prevents conflicts
- **Create from branch/PR**: Sessions can start from an existing branch or PR, not just a blank slate
- **Archive over delete**: Sessions are archived (worktree removed, branch kept) rather than destroyed — restorable with full chat history
- **Setup scripts**: Per-project `setup_command` (e.g. `pnpm install`, `cargo build`) runs automatically in new worktrees
- **Git-tracked files only**: Worktrees naturally contain only tracked files; untracked files like `.env` need a setup script to copy them in

---

## New Crate: `crates/projects/`

### Data Model (`types.rs`)

```rust
pub struct Project {
    pub id: String,                    // slug or UUID
    pub label: String,                 // display name (from Cargo.toml name, git repo, or folder)
    pub directory: PathBuf,            // absolute path to project root
    pub system_prompt: Option<String>, // extra system prompt
    pub auto_worktree: bool,           // create git worktrees per session
    pub setup_command: Option<String>, // runs in new worktrees (e.g. "pnpm install")
    pub detected: bool,                // true if auto-detected, false if user-created
    pub created_at: u64,
    pub updated_at: u64,
}
```

### Storage Trait (`store.rs`)

```rust
#[async_trait]
pub trait ProjectStore: Send + Sync {
    async fn list(&self) -> Result<Vec<Project>>;
    async fn get(&self, id: &str) -> Result<Option<Project>>;
    async fn upsert(&self, project: Project) -> Result<()>;
    async fn delete(&self, id: &str) -> Result<()>;
}
```

Two implementations:
1. **`TomlProjectStore`** — reads/writes `~/.config/moltis/projects.toml` (initial)
2. **`SqliteProjectStore`** — future, easy swap via trait

### Context Loader (`context.rs`)

Walks from `project.directory` upward to filesystem root, collecting:
- `CLAUDE.md` / `CLAUDE.local.md` at each level
- `AGENTS.md` at each level
- `.claude/rules/*.md` from project root

Returns a `ProjectContext` struct:
```rust
pub struct ProjectContext {
    pub project: Project,
    pub context_files: Vec<ContextFile>,  // ordered: deepest last (highest priority)
    pub worktree_dir: Option<PathBuf>,    // if worktree active
}

pub struct ContextFile {
    pub path: PathBuf,
    pub content: String,
}
```

### Auto-Detection (`detect.rs`)

When the gateway starts or on-demand via RPC:
- Scan recently-used directories (from session metadata paths, or a configurable list)
- For each directory with `.git`, create a project entry if not already known
- Label resolution order: `Cargo.toml` package name → git remote name → folder name
- Mark `detected: true` so user-created projects are never overwritten

### Git Worktree Manager (`worktree.rs`)

```rust
pub struct WorktreeManager;

impl WorktreeManager {
    /// Creates a worktree + branch for a session
    pub async fn create(project_dir: &Path, session_id: &str) -> Result<PathBuf>;
    /// Removes worktree; deletes branch if pushed
    pub async fn cleanup(project_dir: &Path, session_id: &str) -> Result<()>;
    /// Lists active worktrees for a project
    pub async fn list(project_dir: &Path) -> Result<Vec<WorktreeInfo>>;
}
```

- Branch name: `moltis/<session_id>` initially, renameable by the agent via tool call or auto-renamed from first commit message
- Worktree location: `<project_dir>/.moltis-worktrees/<session_id>/`
- **Create from branch/PR**: `WorktreeManager::create_from_branch` and `create_from_pr` (uses `gh pr checkout` under the hood)
- On cleanup: remove worktree; delete branch if pushed (can be retrieved later). Archive mode: remove worktree but keep branch + session history for later restoration
- After worktree creation, run `project.setup_command` if configured

### Directory Autocomplete (`complete.rs`)

Given a partial path string, return matching directories. Used by the UI when configuring a new project.

---

## Changes to Existing Crates

### `crates/sessions/src/metadata.rs`
- Add `project_id: Option<String>` to `SessionEntry`
- Add `archived: bool` to `SessionEntry` (archive instead of delete for project sessions)
- Add `worktree_branch: Option<String>` to track the git branch name

### `crates/gateway/src/services.rs`
- Add `ProjectService` trait:
  ```rust
  #[async_trait]
  pub trait ProjectService: Send + Sync {
      async fn list(&self) -> ServiceResult;
      async fn get(&self, params: Value) -> ServiceResult;
      async fn upsert(&self, params: Value) -> ServiceResult;
      async fn delete(&self, params: Value) -> ServiceResult;
      async fn detect(&self) -> ServiceResult;
      async fn complete_path(&self, params: Value) -> ServiceResult;
      async fn context(&self, params: Value) -> ServiceResult; // returns loaded context files
  }
  ```
- Add `NoopProjectService`
- Add `project: Arc<dyn ProjectService>` to `GatewayServices`

### `crates/gateway/src/methods.rs`
- Register RPC methods: `projects.list`, `projects.get`, `projects.upsert`, `projects.delete`, `projects.detect`, `projects.complete_path`, `projects.context`
- Add to `READ_METHODS` / `WRITE_METHODS` as appropriate

### `crates/gateway/src/session.rs` (LiveSessionService)
- New session creation accepts optional `project_id`
- Store in metadata

### `crates/agents/src/prompt.rs`
- Extend `build_system_prompt` to accept `Option<&ProjectContext>`
- Inject context files under `# Project Context` section, each as `## <filename>\n<content>`
- Inject project's custom `system_prompt` if set

### `crates/gateway/src/chat.rs`
- Before calling `build_system_prompt`, resolve the active session's project
- Load `ProjectContext` via the context loader
- If project has `auto_worktree`, create worktree on first chat message (lazy)
- Set tool exec `cwd` to worktree path if active

### `crates/gateway/src/state.rs`
- Track `active_projects: Arc<RwLock<HashMap<String, String>>>` (conn_id → project_id)

### `crates/gateway/src/server.rs`
- Wire `LiveProjectService` into `GatewayServices`
- Run project auto-detection on startup

### `crates/gateway/src/assets/app.js`
- Add project picker dropdown in "New Session" flow
- Show active project badge on session items
- Project management UI (list, add with directory autocomplete, edit, remove)

### `crates/gateway/src/assets/index.html`
- Add project picker elements to sidebar

---

## Key Files to Create/Modify

| Action | File |
|--------|------|
| **Create** | `crates/projects/Cargo.toml` |
| **Create** | `crates/projects/src/lib.rs` |
| **Create** | `crates/projects/src/types.rs` |
| **Create** | `crates/projects/src/store.rs` (trait + TomlProjectStore) |
| **Create** | `crates/projects/src/context.rs` (CLAUDE.md + AGENTS.md loader) |
| **Create** | `crates/projects/src/detect.rs` (auto-detection) |
| **Create** | `crates/projects/src/worktree.rs` (git worktree lifecycle) |
| **Create** | `crates/projects/src/complete.rs` (directory autocomplete) |
| **Modify** | `Cargo.toml` (workspace member) |
| **Modify** | `crates/sessions/src/metadata.rs` (add project_id) |
| **Modify** | `crates/gateway/Cargo.toml` (depend on moltis-projects) |
| **Modify** | `crates/gateway/src/services.rs` (ProjectService trait) |
| **Modify** | `crates/gateway/src/methods.rs` (register project methods) |
| **Modify** | `crates/gateway/src/server.rs` (wire LiveProjectService) |
| **Modify** | `crates/gateway/src/state.rs` (active_projects map) |
| **Modify** | `crates/gateway/src/chat.rs` (inject project context) |
| **Modify** | `crates/agents/src/prompt.rs` (accept ProjectContext) |
| **Modify** | `crates/gateway/src/assets/app.js` (project UI) |
| **Modify** | `crates/gateway/src/assets/index.html` (project elements) |

---

## Implementation Order

1. **`crates/projects/` core** — types, store trait, TomlProjectStore, context loader
2. **Context loader** — walk directories for CLAUDE.md + AGENTS.md
3. **Auto-detection** — scan for git repos, derive project name
4. **Gateway integration** — service trait, RPC methods, wire into server
5. **System prompt injection** — extend `build_system_prompt`, wire in chat.rs
6. **Session binding** — add project_id to SessionEntry, track active project per connection
7. **Git worktree manager** — create/cleanup worktrees
8. **UI** — project picker, management, directory autocomplete
9. **Tests** — unit tests for store, context loader, worktree manager, detection

---

## Verification

1. `cargo check` — compiles cleanly
2. `cargo +nightly clippy` — no warnings
3. `cargo test` — all tests pass including new project tests
4. Manual: start gateway, open UI, create a project pointing to a git repo, create a session with that project, verify CLAUDE.md content appears in system prompt
5. Manual: verify worktree created on session start, cleaned up on session delete
6. Manual: verify auto-detection finds git repos and names them correctly
