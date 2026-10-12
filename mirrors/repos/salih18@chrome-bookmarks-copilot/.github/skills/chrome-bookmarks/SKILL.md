---
name: chrome-bookmarks
description: Read, organize, clean up and edit Google Chrome (or Chromium/Brave/Edge) bookmarks on this computer - list, search, add, rename, move, delete, deduplicate, sort, remove empty folders, find dead links, renew redirected URLs, and reorganize into folders. Use whenever the user mentions bookmarks, favorites, the bookmarks bar, or tidying saved links.
---

# Chrome bookmarks skill

All work goes through one stdlib-only Python script that edits the browser's
`Bookmarks` file safely (backup -> checksum -> atomic replace):

```
python .github/skills/chrome-bookmarks/scripts/bookmarks.py <command> [options]
```

(From the repo root `python bmk.py <command>` is a shortcut for the same thing.
Use `python3` on macOS/Linux if `python` is not found.)

## Golden rules

1. **Read before you write.** Start with `info`, then `stats` / `tree` / `export`.
   Never guess ids - get them from `tree`, `list --json` or `export`.
2. **Chrome must be fully closed before any write.** The script refuses to write
   while it runs. If it refuses, ask the user to quit Chrome (including the tray /
   "continue running background apps") - do NOT add `--force` on your own.
3. **Preview, then confirm, then apply.** Bulk/destructive commands (`delete`,
   `dedupe`, `prune`, `renew`, `organize`, `apply`, `restore`) only preview unless
   `--yes` is passed. Show the user the preview and get an explicit "yes" before
   re-running with `--yes`. Single edits (`add`, `mkdir`, `rename`, `set-url`,
   `move`, `sort`) apply immediately - use `--dry-run` first when unsure.
4. **Batch big reorganizations into one plan** (`apply plan.json`) so they are
   atomic: if any operation fails, nothing is written.
5. **Never delete "dead" links without user review.** `blocked` and `error`
   verdicts are NOT dead (bot protection, timeouts, login walls).
6. Every save prints a backup path. If the user is unhappy: `restore --yes`
   (latest backup) or `restore <file> --yes`.
7. Prefer `--json` output when you need to reason over results.

## Choosing the profile

Defaults: `--browser chrome --profile Default`. Run `profiles` to list others,
then pass e.g. `--profile "Profile 1"` or `--browser edge`. If the file lives
somewhere unusual (WSL, portable install) pass `--file <path>` or set `BMK_FILE`.
On WSL the Windows file is typically
`/mnt/c/Users/<user>/AppData/Local/Google/Chrome/User Data/Default/Bookmarks`.

## Addressing items

- By **id**: `42` or `id:42` (stable, preferred)
- By **path**: `"Bookmarks bar/Dev/Tools"`. First segment is a root; aliases
  `bar`, `other`, `mobile` work in any language.

## Command cheat-sheet

| Goal | Command |
|---|---|
| Where is the file, is Chrome running? | `info` |
| Overview, duplicates, empty folders, top domains | `stats --json` |
| Folder tree with ids | `tree [folder] [--depth 2] [--folders-only] [--urls]` |
| Find bookmarks | `search "python docs"` / `search "^https?://localhost" --regex --field url` |
| Filter | `list --scope bar/Dev --domain github.com --unused-days 365 --json` |
| Full dump for analysis | `export --format json -o bookmarks-export.json` |
| Add | `add <url> --name "Title" --folder "bar/Reading" --create` |
| Create folders | `mkdir "bar/Dev/Docs" "bar/Media"` |
| Rename | `rename <id> "New title"` |
| Change URL | `set-url <id> <new-url>` |
| Move | `move <id> [<id>...] --to "bar/Dev" [--create] [--index 0]` |
| Delete | `delete <id> [<id>...]` -> preview -> `--yes` |
| Sort | `sort "bar/Dev" [--by name/url/date/domain] [-r] [--mixed]` |
| Remove duplicates | `dedupe [--keep deepest/oldest/newest/used]` -> `--yes` |
| Remove empty folders | `prune` -> `--yes` |
| Dead-link scan | `check [--scope X] --only dead redirect -o link-report.json` |
| Renew moved URLs | `renew --report link-report.json [--https]` -> `--yes` |
| Rule-based organize | `organize rules.json [--sort]` -> `--yes` |
| Arbitrary batch plan | `apply plan.json` -> `--yes` |
| Backups | `backup`, `backups`, `restore [file] --yes` |

## Workflows

- **Smart reorganization** (you decide categories): see
  [references/organize-workflow.md](references/organize-workflow.md).
- **Plan file format** (all ops): see
  [references/plan-format.md](references/plan-format.md).
- **Link health / renew**: `check -o link-report.json` -> summarize by verdict ->
  `renew --report link-report.json` preview -> confirm -> `--yes`. Offer to delete
  only `dead` items, listing them first.

## Interpreting `check` verdicts

| verdict | meaning | suggested action |
|---|---|---|
| `ok` | 2xx | none |
| `redirect` | URL moved; `permanent` = all 301/308 | `renew` (skips `suspicious` = login/home-page redirects) |
| `dead` | 404/410 or domain doesn't resolve | offer delete or archive folder |
| `blocked` | 401/403/429/451 - site blocks bots or needs login | keep |
| `error` | timeout, 5xx, TLS problem | keep; maybe re-check later |
| `skipped` | non-http (chrome://, javascript:, file:) | keep |

## Chrome Sync caveat

If `info` shows `sync_metadata_present: true`, Chrome Sync may re-apply the
server copy and undo offline edits (or bring deleted items back). Tell the user
before large changes, and suggest testing a small change first. See README.
