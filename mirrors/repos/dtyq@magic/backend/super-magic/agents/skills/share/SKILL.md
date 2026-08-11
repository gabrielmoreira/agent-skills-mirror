---
name: share
description: Use when a user needs a browser-accessible link to preview, present, or send Agent-generated workspace files, an entire project, or the current topic outside Super Magic—especially rendered output such as HTML that messaging or file-viewing channels cannot display directly—or when they need to find, reuse, change, or delete an existing share.
---

# Share

Use these Code Mode tools from a Python snippet executed with `run_sdk_snippet`. Import `tool` from `sdk.tool` and call tools with `tool.call(...)`.

## Choose the Target

- For workspace files, continue with this document. This is the most common workflow.
- When a file may reference local assets, first read [references/file-dependencies.md](references/file-dependencies.md).
- For the entire current project, first read [references/project-share.md](references/project-share.md).
- For the current topic or conversation, first read [references/topic-share.md](references/topic-share.md).
- To inspect or change an existing share, first read [references/edit-share.md](references/edit-share.md).
- Never infer an entire-project share from a request to share one or more files.

## File Share Workflow

1. Confirm which files the user wants to share. Do not add additional files without the user’s approval.
2. Call `list_file_shares` with the original exact `file_paths` before creating anything.
3. Read the entry and understand its actual local references first. Decide yourself whether `inspect_file_share` would reduce uncertainty; it is optional assistance, not a mandatory step. Treat its output as static candidates only, then verify candidates against the entry and relevant files. If confirmed local dependencies are omitted, explain that images, styles, fonts, video, or interactions may be missing. When the user has not already requested the related files, ask whether to include them, preferably with an interactive question when available. Do not add unrequested files.
4. Read the entry and the files that will actually be shared when content review is needed. Stop for clearly prohibited content. For possible personal data, credentials, internal material, or an apparently wrong file, explain the concrete risk and ask the user whether to exclude it or cancel.
5. Handle the result:
   - One active share and no requested setting change: return its existing URL and password. Do not call `create_file_share`.
   - Multiple active shares: show the candidates and ask which share to reuse, update, or delete.
   - No active share: continue to entry-file and access selection. If dependencies changed the final file set, call `list_file_shares` again with that final set before creating.
6. Select the required entry file:
   - One file: use that file as `entry_file_path`.
   - Multiple files: use the file explicitly named by the user. Ask which file should open first when it is not uniquely clear.
7. If the user did not choose an access method, explain the three choices and ask before creating:
   - Team access is safest because only organization members can open it, but it is less convenient for external recipients.
   - Password access is the recommended balance of safety and convenience. Anyone with both the link and password can open it. Password-protected file and project shares require VIP.
   - Public access is highest risk because anyone with the link can open it. Use it only after the user explicitly chooses public access.
8. Never change a failed password share to public automatically. Explain the VIP restriction and ask the user to choose team access or explicitly approve public access.

When the original file set already has an active share and the user approves adding dependencies, read that share and call `update_file_share` with the complete final `file_paths` and the existing `entry_file_path`. Do not call `create_file_share` for this repair; preserve the original resource ID and settings. The file list is a complete replacement, so retain every existing file that should remain shared.

Use the user's language when asking about access. A concise question is:

```
How should this be shared?

1. Team access: safest; only team members can open it, but it is less convenient for external recipients.
2. Password access: recommended balance of safety and convenience; file and project password shares require VIP.
3. Public access: highest risk; anyone with the link can open it. Use only for intentional public distribution.
```

## File Tools

Use the literal string values shown for fields with alternatives.

```python
list_file_shares(
    file_paths: list[str] = [],
    status: "active" | "expired" | "deleted" | "all" = "active",
    keyword: str | None = None,
    current_project_only: bool = True,
    page: int = 1,
    page_size: int = 20,
)
```

Pass `file_paths` for exact active-share lookup. Omit it only when browsing file shares. Browsing is limited to the current project unless the user explicitly requests a cross-project search. Exact lookup returns the password when one exists; browsing results do not expose passwords.

For list tools, `status="expired"` includes shares that passed their expiry time and shares that were manually disabled. `status="deleted"` means the share record was deleted and the link is unavailable.

```python
create_file_share(
    file_paths: list[str],
    entry_file_path: str,
    access_type: "password" | "team" | "public" = "password",
    password: str | None = None,
    team_scope: "all" | "designated" = "all",
    team_user_ids: list[str] = [],
    team_department_ids: list[str] = [],
    expire_days: int | None = None,
    show_original_info: bool = True,
    allow_download: bool = True,
    allow_copy: bool = True,
    show_file_list: bool = True,
    hide_super_magic_watermark: bool = False,
    immersive: bool = False,
)
```

`file_paths` and `entry_file_path` are required. The entry file must also appear in `file_paths`. Paths must remain inside the current workspace and already have MagicFS file IDs.

## Access and Page Settings

- Password access: use `access_type="password"`. Omit `password` to generate a secure password.
- Team access for everyone: use `access_type="team"` and keep `team_scope="all"`.
- Team access for selected recipients: use `access_type="team"`, `team_scope="designated"`, and provide at least one user or department ID.
- Public access: use `access_type="public"` only after explicit user approval.
- `expire_days=None` means permanent; otherwise use an integer from 1 to 365.
- `show_original_info=False` hides original author information and does not require VIP.
- `allow_copy=False` prevents viewers from copying shared files into their workspace.
- `hide_super_magic_watermark=True` requires VIP and hides only the bottom-right “Created by Super Magic” watermark, not all product branding.
- `immersive=True` opens the entry file in a full-screen immersive presentation and hides both the share-page header and the file-preview header.
- Optional settings already use product defaults. Pass only values that differ from the user's requested behavior.

## Common File Calls

### Find an existing share first

```python
from sdk.tool import tool

result = tool.call("list_file_shares", {
    "file_paths": ["site/index.html", "site/styles.css", "site/app.js"],
})
print(result.content)
```

Read `result.data["items"]`. Reuse one unambiguous result when the user requested no changes. Ask the user to choose when more than one result exists.

### Create a password share after no existing share was found

```python
result = tool.call("create_file_share", {
    "file_paths": ["site/index.html", "site/styles.css", "site/app.js"],
    "entry_file_path": "site/index.html",
})
print(result.content)
```

The omitted password is generated securely. Return both the URL and password.

### Create an explicitly public share

```python
result = tool.call("create_file_share", {
    "file_paths": ["public/product-guide.pdf"],
    "entry_file_path": "public/product-guide.pdf",
    "access_type": "public",
})
```

Use this only when the user clearly accepts public access.

## Delete a Share

```python
delete_share(
    share_ref: str,
    confirmed: bool,
)
```

`share_ref` accepts a numeric resource ID or a complete `/share/files/{id}` or `/share/topic/{id}` URL. For a topic share, pass its topic ID directly because it is the share resource ID.

- If the user provides a specific URL or resource ID and explicitly asks to delete that share, call `delete_share` with `confirmed=True`.
- If the user identifies only files, a project, a topic, or a name, first use the corresponding list tool. Ask the user to choose when more than one candidate matches.
- Set `confirmed=True` only when the user's words clearly authorize deletion of the now-unambiguous share. A question such as “Do we still need this?” is not authorization.
- Deleting a share makes its link unavailable and deletes the share record logically. It does not delete the source topic, files, or project.

```python
result = tool.call("delete_share", {
    "share_ref": "https://example.com/share/files/123456",
    "confirmed": True,
})
print(result.content)
```

## Result Handling

Always check `result.ok`.

- Read `result.content` first to understand what happened.
- When you need an exact value for the next step or for the user, read it from `result.data`:
  - list tools return their shares in `result.data["items"]`;
  - create and reuse tools return `share_url`, `password`, `resource_id`, and `operation`.
- Only show or pass on a `share_url` that is present in `result.data`. Password-share URLs returned by the tools already include the password query parameter when the password is known; pass them through unchanged. Never invent or rewrite a link.
- If a required value is missing, tell the user what is missing and keep the reported operation state. Do not repeat a mutating call just to obtain a complete response.
- When the requested access method cannot be used, explain why and ask the user to choose another method. Do not switch to a different or less secure method automatically.

## Required Rules

- Do not share anything without clear user intent.
- Do not create a new share before checking for an existing one of the same target type.
- Do not create a public share by default.
- Do not guess an entry file when multiple choices are plausible.
- Do not choose among multiple shares without the user.
- Do not update an existing share without an explicit change request.
- Do not set `delete_share.confirmed=True` without explicit user authorization.
- Do not describe watermark hiding as removing all Super Magic branding.
- Do not add files merely because they are in the same directory. Add only files confirmed as page dependencies and approved by the user.
- When the user asks to add files to an existing share, update that share with the complete final file set; do not create a second share.
