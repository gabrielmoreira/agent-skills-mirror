---
name: conductor-revert
version: 1.1.1
description: "Maps Conductor track, phase, and task ids to commit SHAs, applies git revert newest-first, then realigns plan.md checkboxes, metadata.json counts, and tracks.md. Use when undoing a Conductor work unit on a branch others may already have pulled. Not for rebase history-tidying, unpushed reset --hard drops, force-push, or starting a revert while MERGE_HEAD/REBASE_HEAD/CHERRY_PICK_HEAD exists."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Revert Track

Revert changes by logical work unit — a whole track, a single phase, or one task — using git's history-preserving tools. The skill maps Conductor work units (tracked in `conductor/tracks.md` plus a per-track `plan.md` and `metadata.json`) to the commits that implemented them, then undoes those commits with `git revert` rather than `git reset`.

Why `git revert` and never `git reset --hard`? A revert adds *new commits* that invert the originals. That keeps the undo fully auditable (the original commit and its inverse both remain visible in `git log`), itself reversible (you can revert the revert), and safe to push to a branch other people share. A hard reset rewrites history instead: anyone who already pulled the commits you erase will diverge from you, and the undone work is unrecoverable unless someone still has it in a reflog. Because reverts are purely additive, this skill is safe to run even after the work has been pushed to a shared remote.

## When to Use

- **Undo a feature track, phase, or task without rewriting history** — the default, safe choice whenever the commits might already be shared.
- **Roll back work that has been pushed to a shared remote** — `git reset` is unsafe here because it would force-rewrite history other people depend on; `git revert` is the correct tool.
- **Reset `plan.md` and `tracks.md` to match the reverted code** — keeping the Conductor metadata in step with the actual code is the whole point; stale `[x]` checkboxes lie about what is done.
- **Roll back one logical unit while leaving concurrent work intact** — targeting specific commits lets you undo, say, the dashboard track without touching an unrelated auth track on the same branch.

### Do Not Use

- **To "clean up" or tidy history.** Use an interactive rebase instead. A revert *adds* commits, so it makes history longer and noisier, not shorter — the opposite of cleanup.
- **To permanently delete commits from a local, unpushed branch.** There `git reset` is appropriate and a revert would just leave the original commits behind. Only reach for reset when the commits are confirmed local-only.
- **When the changes are interleaved with critical hotfixes you cannot separate.** Reverting the feature commits would also undo or conflict with the hotfix. Separate the concerns first (e.g. cherry-pick the hotfix out) before reverting.
- **In the middle of a merge, rebase, or cherry-pick.** The working tree is already in a partial state; layering a revert on top corrupts the in-progress operation. Finish or abort it first.

## Prerequisites

1. **Conductor must be initialized.** The file `conductor/tracks.md` must exist. If it is missing, the skill has no map from work units to commits — stop and suggest `/conductor:setup`.
2. **Clean git working tree.** A revert stages its own changes into the index; pre-existing uncommitted edits would become impossible to review or unwind separately. Stash or commit first.
3. **No in-progress git operation.** A merge, rebase, or cherry-pick mid-flight leaves sentinel files in the git directory; reverting on top of them corrupts that operation.
4. **Windows host (primary).** This skill's bash scripts run under Git Bash or WSL on Windows. In PowerShell, use `bash` as the wrapper or translate `set -euo pipefail` scripts to `$ErrorActionPreference = 'Stop'` equivalents. Git commands themselves are identical across shells.

## Procedure

### Step 1 — Pre-flight Checks

Validate the environment before touching history, because a revert started from a bad state is far harder to unwind than one that never started.

```bash
#!/usr/bin/env bash
set -euo pipefail

# Must actually be in a work tree; otherwise every later git call fails opaquely.
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "error: not inside a git work tree" >&2
  exit 1
fi

# Conductor state must exist so we can map work units to commits.
if [[ ! -f conductor/tracks.md ]]; then
  echo "error: conductor/tracks.md not found; run /conductor:setup first" >&2
  exit 1
fi

# A revert mixes its changes into the index, so any pre-existing edits would
# become impossible to review or unwind on their own. Fail loudly.
if [[ -n "$(git status --porcelain)" ]]; then
  echo "error: uncommitted changes detected; stash or commit them before reverting" >&2
  git status --short >&2
  exit 1
fi

# A revert during an in-progress merge/rebase/cherry-pick corrupts that
# operation. Detect the marker files git writes for each and bail.
git_dir="$(git rev-parse --git-dir)"
for marker in MERGE_HEAD REBASE_HEAD CHERRY_PICK_HEAD; do
  if [[ -e "$git_dir/$marker" ]]; then
    echo "error: $marker present; finish or abort the in-progress operation first" >&2
    exit 1
  fi
done

echo "pre-flight checks passed"
```

### Step 2 — Target Selection

Pick the scope of the revert. The three scopes exist because work has a dependency order, and undoing the wrong amount either leaves the build broken or undoes more than intended.

| Scope | Argument format | Example | What gets reverted |
|---|---|---|---|
| **Full track** | `{trackId}` | `auth_20260115` | Every commit associated with the track |
| **Specific phase** | `{trackId}:phase{N}` | `auth_20260115:phase2` | Phase N **and every later phase** (cascade is deliberate) |
| **Specific task** | `{trackId}:task{X.Y}` | `auth_20260115:task2.3` | Only that one task — finest-grained undo |

> **Phase cascade rationale:** Phases are built in order and later phases assume the earlier ones exist. Leaving phase 3 sitting on top of a reverted phase 2 would almost certainly break the build. If you genuinely need to keep a later phase, revert task-by-task instead.

If no argument is supplied, present a guided menu listing the track's "In Progress" and "Recently Completed" units so the human can choose without memorizing ids.

### Step 3 — Commit Discovery

Find the exact commit SHAs to revert. Conductor encodes the track id and task number in every commit subject, which is what makes precise discovery possible.

```bash
#!/usr/bin/env bash
set -euo pipefail

# An empty track id would match every commit and could revert unrelated work,
# so require it explicitly and fail fast rather than guess.
track_id="${1:?usage: discover-commits <trackId> [taskId]}"
task_id="${2:-}"

# Match on literal substrings (--fixed-strings) so a task id like "2.3" is never
# read as a regex (where "." would match any character). --all-match requires
# every --grep pattern to hit, narrowing the result to this track's commits.
discover_commits() {
  local -a grep_args=(--grep "$track_id")
  if [[ -n "$task_id" ]]; then
    grep_args+=(--grep "Task $task_id")
  fi

  # %H = full SHA, %x1f = unit-separator byte, %s = subject. The separator keeps
  # subjects that contain spaces intact when the caller splits each line.
  git log --all-match --fixed-strings --format='%H%x1f%s' "${grep_args[@]}"
}

mapfile -t commit_lines < <(discover_commits)

if [[ "${#commit_lines[@]}" -eq 0 ]]; then
  echo "error: no commits found for track '$track_id'${task_id:+, task $task_id}" >&2
  exit 1
fi

printf '%s\n' "${commit_lines[@]}"
```

For a **phase revert**, first read the task ids that belong to the phase out of `plan.md`, then run the discovery above once per task (and include the phase's "mark complete" / plan-update commits). For a **full track revert**, also pick up any commits that only touched the track's own files, since those may not mention a task number:

```bash
# Commits that modified files under the track directory but might omit a task id
# in the subject — e.g. a plan.md edit committed on its own.
git log --format='%H%x1f%s' -- "conductor/tracks/$track_id/"
```

### Step 4 — Execution Plan Display

Show the human exactly what will happen and require an explicit, typed `YES`. Why insist on the full word rather than a bare `y` or Enter? Reverting touches history; a single keystroke is too easy to hit reflexively. Typing `YES` forces the operator to read the plan and consciously consent.

```text
================================================================================
                           REVERT EXECUTION PLAN
================================================================================
Target: dashboard_20260112:phase2 (phase 2 and all later phases)

Commits to revert (reverse chronological — newest first):
  1. 9f3a1c7 - feat: add chart rendering (dashboard_20260112)
  2. 7b2e4d9 - chore: mark task 2.3 complete (dashboard_20260112)
  3. 4c8a0f2 - feat: implement fetch hook (dashboard_20260112, Task 2.2)
  4. 1d6b9e5 - chore: mark task 2.2 complete (dashboard_20260112)

Affected files:
  - src/components/Dashboard.tsx   (modified)
  - src/hooks/useData.ts           (deleted)
  - conductor/tracks/dashboard_20260112/plan.md      (modified)
  - conductor/tracks/dashboard_20260112/metadata.json (modified)

Plan updates:
  - Task 2.2: [x] -> [ ]
  - Task 2.3: [~] -> [ ]

metadata.json updates:
  - tasks.completed: 5 -> 3
  - status: in_progress (unchanged)
  - updated: 2026-06-14T09:12:44.000Z -> <now>

================================================================================
                                  !! WARNING !!
================================================================================
This will create 4 revert commits. The operation is non-destructive (history is
preserved) but it does change the current branch state.

Type 'YES' to proceed, or anything else to cancel:
```

### Step 5 — Revert Execution

Revert in **reverse chronological order** — newest commit first. Later commits build on earlier ones, so undoing the newest first means each revert is applied while the code it depends on still exists, which minimizes conflicts. Reverting oldest-first would pull the rug out from under the later commits and almost guarantee conflicts.

```bash
#!/usr/bin/env bash
set -euo pipefail

# SHAs must be passed newest-first (see ordering rationale above).
if [[ "$#" -eq 0 ]]; then
  echo "usage: run-reverts <sha> [<sha> ...]   # newest commit first" >&2
  exit 1
fi

# Validate every SHA up front so we never start a partial sequence on a typo.
for sha in "$@"; do
  if ! git rev-parse --verify --quiet "${sha}^{commit}" >/dev/null; then
    echo "error: '$sha' is not a valid commit" >&2
    exit 1
  fi
done

for sha in "$@"; do
  echo ">> reverting $sha"
  if ! git revert --no-edit "$sha"; then
    # A conflict (or any failure) leaves the revert mid-flight. Halt now: the
    # only safe recovery is human-reviewed resolution or `git revert --abort`.
    echo "error: revert of $sha failed (likely a conflict); halting" >&2
    echo "       inspect with 'git status', then resolve and 'git revert --continue'" >&2
    echo "       or back out entirely with 'git revert --abort'" >&2
    exit 1
  fi
done

echo "all reverts applied"
```

**Conflict handling.** If a conflict occurs, halt immediately and surface the conflicted files. Offer the human three choices: show details, abort the sequence (`git revert --abort`), or open a manual resolution guide. **Never auto-resolve** — the skill cannot know which side of a conflict reflects the intended outcome, and guessing risks silently corrupting code.

### Step 6 — State Synchronization

After the code is reverted, bring the Conductor metadata back in step with it. If `plan.md` still shows `[x]` for work whose code no longer exists, every later decision built on that lie. Update three things, then commit them as the final step of the sequence so the metadata change travels with the reverts:

1. **`plan.md`** — flip each reverted task's checkbox from `[x]` (done) or `[~]` (in progress) back to `[ ]` (not started).
2. **`metadata.json`** — decrement `tasks.completed` by the number of reverted tasks, recompute `status`, and refresh the `updated` timestamp.
3. **`tracks.md`** — set the track's roll-up status to `[ ]` or `[~]` to match.

A concrete `metadata.json` before the revert:

```json
{
  "trackId": "dashboard_20260112",
  "status": "in_progress",
  "tasks": {
    "total": 8,
    "completed": 5
  },
  "updated": "2026-06-14T09:12:44.000Z"
}
```

And the matching `plan.md` excerpt:

```markdown
## Phase 2: Data layer
- [x] Task 2.1: define the data schema
- [x] Task 2.2: implement the fetch hook
- [~] Task 2.3: render the chart component
```

The transforms below do this safely. They are written as pure functions over the file *contents* (no hidden I/O) so the result can be diffed and unit-tested, with a thin async wrapper that performs the reads and writes. Every value is explicitly typed, untrusted JSON is narrowed through type guards rather than cast to `any`, and any unexpected shape throws instead of silently writing garbage — because a half-updated `metadata.json` is worse than no update at all.

```typescript
import { readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";

interface TaskCounts {
  total: number;
  completed: number;
}

const TRACK_STATUSES = ["not_started", "in_progress", "completed"] as const;
type TrackStatus = (typeof TRACK_STATUSES)[number];

interface TrackMetadata {
  trackId: string;
  status: TrackStatus;
  tasks: TaskCounts;
  updated: string; // ISO 8601 timestamp
}

function isTrackStatus(value: unknown): value is TrackStatus {
  return (
    typeof value === "string" &&
    (TRACK_STATUSES as readonly string[]).includes(value)
  );
}

// Narrow parsed JSON (typed `unknown`) down to TrackMetadata. Returning a type
// predicate lets the caller treat the value as fully typed afterwards, with no
// `any` and no unchecked cast.
function isTrackMetadata(value: unknown): value is TrackMetadata {
  if (typeof value !== "object" || value === null) {
    return false;
  }
  const record = value as Record<string, unknown>;
  const tasks = record.tasks;
  if (typeof tasks !== "object" || tasks === null) {
    return false;
  }
  const taskRecord = tasks as Record<string, unknown>;
  return (
    typeof record.trackId === "string" &&
    isTrackStatus(record.status) &&
    typeof record.updated === "string" &&
    typeof taskRecord.total === "number" &&
    typeof taskRecord.completed === "number" &&
    Number.isInteger(taskRecord.total) &&
    Number.isInteger(taskRecord.completed)
  );
}

// Status is derived from the counts rather than set by hand, so it can never
// drift out of agreement with tasks.completed.
function deriveStatus(counts: TaskCounts): TrackStatus {
  if (counts.completed <= 0) {
    return "not_started";
  }
  if (counts.completed < counts.total) {
    return "in_progress";
  }
  return "completed";
}

function applyRevertToMetadata(
  rawJson: string,
  revertedTaskCount: number,
  nowIso: string,
): string {
  if (!Number.isInteger(revertedTaskCount) || revertedTaskCount < 0) {
    throw new RangeError(
      `revertedTaskCount must be a non-negative integer, received: ${revertedTaskCount}`,
    );
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(rawJson);
  } catch (cause) {
    throw new Error("metadata.json is not valid JSON; refusing to overwrite it", {
      cause,
    });
  }

  if (!isTrackMetadata(parsed)) {
    throw new Error("metadata.json does not match the expected TrackMetadata shape");
  }

  if (revertedTaskCount > parsed.tasks.completed) {
    throw new RangeError(
      `cannot revert ${revertedTaskCount} task(s); only ${parsed.tasks.completed} are marked complete`,
    );
  }

  const nextCounts: TaskCounts = {
    total: parsed.tasks.total,
    completed: parsed.tasks.completed - revertedTaskCount,
  };

  const next: TrackMetadata = {
    ...parsed,
    tasks: nextCounts,
    status: deriveStatus(nextCounts),
    updated: nowIso,
  };

  // Trailing newline matches how editors and `git` expect text files to end.
  return `${JSON.stringify(next, null, 2)}\n`;
}

// Escape regex metacharacters so a task id such as "2.3" matches literally
// (the "." must not act as a wildcard).
function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function resetTasksInPlan(planText: string, taskIds: readonly string[]): string {
  if (taskIds.length === 0) {
    throw new Error("resetTasksInPlan requires at least one task id");
  }

  let nextPlan = planText;

  for (const taskId of taskIds) {
    if (!/^\d+\.\d+$/.test(taskId)) {
      throw new Error(
        `invalid task id "${taskId}"; expected "<phase>.<task>", e.g. "2.3"`,
      );
    }

    // Match "- [x] Task 2.3 ..." or "- [~] 2.3 ..." and flip only the checkbox,
    // leaving indentation, the "Task" label, and the description untouched.
    const checkbox = new RegExp(
      `^(?<indent>\\s*[-*]\\s+)\\[(?:x|~)\\](?<rest>\\s+(?:Task\\s+)?${escapeRegExp(
        taskId,
      )}\\b)`,
      "m",
    );

    if (!checkbox.test(nextPlan)) {
      throw new Error(
        `task ${taskId} was not found as a completed/in-progress item in plan.md; ` +
          "aborting so plan state cannot silently drift from the reverted code",
      );
    }

    nextPlan = nextPlan.replace(checkbox, "$<indent>[ ]$<rest>");
  }

  return nextPlan;
}

interface SyncRevertOptions {
  trackDir: string; // e.g. "conductor/tracks/dashboard_20260112"
  revertedTaskIds: readonly string[];
}

async function syncRevertState(options: SyncRevertOptions): Promise<void> {
  const { trackDir, revertedTaskIds } = options;
  if (revertedTaskIds.length === 0) {
    throw new Error("syncRevertState requires at least one reverted task id");
  }

  const planPath = join(trackDir, "plan.md");
  const metadataPath = join(trackDir, "metadata.json");
  const nowIso = new Date().toISOString();

  // Read both files first; if either is missing or unreadable we throw before
  // writing anything, so plan.md and metadata.json never end up half-updated.
  const [planText, metadataJson] = await Promise.all([
    readFile(planPath, "utf8"),
    readFile(metadataPath, "utf8"),
  ]);

  // Compute (and validate) both new contents before any write. A failure in
  // either transform throws here, leaving the originals on disk untouched.
  const nextPlan = resetTasksInPlan(planText, revertedTaskIds);
  const nextMetadata = applyRevertToMetadata(
    metadataJson,
    revertedTaskIds.length,
    nowIso,
  );

  await Promise.all([
    writeFile(planPath, nextPlan, "utf8"),
    writeFile(metadataPath, nextMetadata, "utf8"),
  ]);
}
```

## Examples

**Scenario: revert a single task.**
Input: `/revert auth_20260115:task1.2`

1. **Discovery** — `git log --all-match --fixed-strings --grep "auth_20260115" --grep "Task 1.2"` finds two commits: the feature commit and the "mark task 1.2 complete" commit.
   ```text
   a1b2c3d - feat: validate login form (auth_20260115, Task 1.2)
   e4f5a6b - chore: mark task 1.2 complete (auth_20260115)
   ```
2. **Plan** — display both SHAs, the affected files, and the planned `plan.md` change (Task 1.2 `[x] -> [ ]`). Wait for the operator to type `YES`.
3. **Execution** — revert newest-first:
   ```bash
   git revert --no-edit e4f5a6b   # the "mark complete" commit
   git revert --no-edit a1b2c3d   # the feature commit
   ```
4. **Sync** — run `syncRevertState` with `revertedTaskIds: ["1.2"]`: `plan.md` Task 1.2 becomes `[ ]`, `metadata.json` `tasks.completed` drops by one, `updated` is refreshed, then commit those metadata edits as the final commit of the sequence.

## Pitfalls

### HARD RULES — Never Violate

1. **Use `git revert`, never `git reset --hard`.** Revert preserves history and stays safe on shared branches; a hard reset erases commits other people may already have.
2. **Never `git push --force` as part of this skill.** Reverts are ordinary commits, so a normal push suffices. Force-pushing would rewrite shared history — the exact outcome reverting is meant to avoid.
3. **Never auto-resolve conflicts.** The skill cannot know which side reflects intent; a wrong guess silently corrupts code. Halt and hand control to a human.
4. **Always show the full plan before acting.** The operator must be able to see every commit, file, and metadata change before consenting — surprises during a history operation are expensive.
5. **Require the literal word `YES`.** A bare `y` or Enter is too easy to hit by reflex; the full word forces a deliberate read of the plan.
6. **Halt on any error.** Continuing past a failed revert compounds a partial, inconsistent state. Stop so the situation can be inspected while it is still small.
7. **Prefer revert commits over any history rewrite.** Additive, auditable, reversible undo is the safe default; reach for history-rewriting tools only on confirmed-local branches and only when explicitly intended.

### Edge Cases

- **Track never committed.** If discovery finds zero commits, there is nothing to revert — offer to delete the track directory only (a file operation, not a git history change), and confirm before removing it.
- **Commit already reverted.** If a target commit was already reverted, re-reverting would *reapply* the change. Detect this and offer to skip that commit or cancel the sequence.
- **Already pushed to a remote.** This is fine and expected — the new revert commits are themselves pushed with a normal `git push`, which is precisely the safe way to undo shared history. Tell the operator new commits will be created so they are not surprised by the extra history.

### Undo the Revert

Sometimes the revert itself was a mistake. Two ways to back it out:

- **Safe (shared branches): revert the reverts.** This creates new commits that restore the changes, so it is safe even after the reverts were pushed:
  ```bash
  # Re-apply the changes undone by the last N revert commits.
  git revert --no-edit HEAD~"$N"..HEAD
  ```
- **Local only: drop the revert commits.** Only when the revert commits have *not* been pushed, since this rewrites history:
  ```bash
  # Discard the last N (revert) commits but keep their changes staged so nothing
  # is lost if N was wrong.
  git reset --soft HEAD~"$N"
  ```
  Prefer the safe method on any branch that might be shared; use the local-only reset solely when you have confirmed the commits never left your machine.

## Verification

Confirm the revert actually landed and the metadata matches the code:

- [ ] `git log` shows a new "Revert ..." commit for every targeted SHA.
- [ ] `conductor/tracks/{trackId}/plan.md` shows the reverted tasks reset to `[ ]`.
- [ ] `conductor/tracks/{trackId}/metadata.json` shows `tasks.completed` decremented and a refreshed `updated` timestamp.
- [ ] `conductor/tracks.md` reflects the updated track status.
- [ ] The application still builds: `npm run build` (or the project equivalent).
- [ ] Regression tests pass: `npm test` (or the project equivalent).
- [ ] No conflict markers or unresolved files remain: `git status` is clean.

### Quick Verification Commands

```bash
# Confirm revert commits exist in the log
git log --oneline -10 --grep "Revert"

# Confirm working tree is clean
git status --porcelain

# Confirm metadata.json is valid JSON and counts are correct
cat conductor/tracks/{trackId}/metadata.json | python -m json.tool

# Confirm plan.md checkboxes are reset
grep -n '\[x\]\|\[~\]' conductor/tracks/{trackId}/plan.md
# Expected: no output (all reverted tasks should be [ ])
```

## Related Skills

- `conductor-setup` — initializes the track structure (`tracks.md`, per-track `plan.md` and `metadata.json`) that this skill reads and updates.
- `git-branch-management` — manages the branches the reverts are applied to.
