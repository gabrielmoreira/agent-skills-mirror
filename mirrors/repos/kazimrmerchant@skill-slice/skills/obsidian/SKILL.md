---
name: obsidian
description: Reads, searches, creates, and edits markdown notes in an Obsidian vault via resolved filesystem paths (OBSIDIAN_VAULT_PATH, else ~/Documents/Obsidian Vault). Use when the user asks to manage vault notes, wikilinks, or Obsidian markdown files. Not for Google Docs or Drive (google-workspace) or git-backed wiki hosting. Do not pass unresolved $OBSIDIAN_VAULT_PATH into file tools.
version: 1.0.1
platforms: [windows, linux, macos]
---

## When to Use
Use this skill for filesystem-first Obsidian vault work: reading notes, listing notes, searching note files, creating notes, appending content, and adding wikilinks. Trigger when the user mentions "Obsidian", "vault", "note", or asks to manage markdown files in an Obsidian context.

## Prerequisites
- The Obsidian vault path must be resolved before calling file tools.
- The documented vault-path convention is the `OBSIDIAN_VAULT_PATH` environment variable.
- If it is unset, use `~/Documents/Obsidian Vault`.
- File tools do not expand shell variables. Do not pass paths containing `$OBSIDIAN_VAULT_PATH` to `read_file`, `write_file`, `patch`, or `search_files`; resolve the vault path first and pass a concrete absolute path. 

## Procedure

### 1. Resolve Vault Path
1. If the vault path is unknown, use `terminal` to resolve `OBSIDIAN_VAULT_PATH` or check whether the fallback path exists.
   - PowerShell (Windows): `$env:OBSIDIAN_VAULT_PATH`
   - Bash (Linux/macOS): `echo $OBSIDIAN_VAULT_PATH`
2. Once the path is known, switch back to file tools. Vault paths may contain spaces, which is another reason to prefer file tools over shell commands.

### 2. Read a Note
1. Use `read_file` with the resolved absolute path to the note.
2. Prefer this over `cat` because it provides line numbers and pagination.

### 3. List Notes
1. Use `search_files` with `target: "files"` and the resolved vault path.
2. To list all markdown notes, use `pattern: "*.md"` under the vault path.
3. To list a subfolder, search under that subfolder's absolute path.

### 4. Search Notes
1. Use `search_files` for both filename and content searches. Prefer this over `grep`, `find`, or `ls`.
2. For filenames: use `search_files` with `target: "files"` and a filename `pattern`.
3. For note contents: use `search_files` with `target: "content"`, the content regex as `pattern`, and `file_glob: "*.md"` to restrict matches to markdown notes.

### 5. Create a Note
1. Use `write_file` with the resolved absolute path and the full markdown content.
2. Prefer this over shell heredocs or `echo` because it avoids shell quoting issues and returns structured results.
3. Use Obsidian wikilinks (`[[Note Name]]`) to link related content.

### 6. Append to a Note
1. Read the target note with `read_file`.
2. Use `patch` for an anchored append when there is stable context, such as adding a section after an existing heading or appending before a known trailing block. Replace the anchor with the anchor plus the new content.
3. Use `write_file` when rewriting the whole note is clearer than constructing a fragile patch.
4. For a simple append with no stable context, `terminal` is acceptable if it is the clearest safe option.

### 7. Targeted Edits
1. Use `patch` for focused note changes when the current content gives you stable context. Prefer this over shell text rewriting.

## Pitfalls
- **Unexpanded Shell Variables:** File tools (`read_file`, `write_file`, `patch`, `search_files`) do not expand shell variables. Passing `$OBSIDIAN_VAULT_PATH` directly will fail. Always resolve to an absolute path first.
- **Spaces in Paths:** Vault paths often contain spaces (e.g., `Obsidian Vault`). Shell commands require complex quoting; file tools handle spaces natively and safely.
- **Fragile Patches:** When appending, if there is no stable anchor, `patch` can fail or corrupt files. Prefer `write_file` for full rewrites or use `terminal` for simple appends if safe.

## Verification
- To verify the vault path is correct, list the root directory:
  - `search_files` with `target: "files"`, `path: "<resolved_vault_path>"`, `pattern: "*.md"`
- To verify a note was created or edited correctly:
  - `read_file` with the absolute path to the note and check the content and wikilinks.
