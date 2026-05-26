# Save Path Conventions

## Default: Display Only

By default, `read` and `learn` show converted content inline. No file is created unless the user explicitly requests it.

## When to Save

Save to the user-specified directory, or to a per-session temp directory when no directory was specified, when any of these are true:

- User explicitly asks: "save", "download", "保存", "下载", "keep this"
- Called from within `/learn` Phase 1 (expects a file path to organize into a sub-topic directory)
- User says "save" or "保存" after seeing the output (do not re-fetch, use thread content)

## Naming

- Use the page title, sanitized: lowercase, spaces to hyphens, strip special chars
- If the file already exists, append `-1`, `-2`, etc. Never overwrite without confirmation
- Tell the user the full saved path

## Learn Phase Integration

When `/read` is called from `/learn` Phase 1:

1. Save to the research project's source directory when `/learn` provides one; otherwise use a per-session temp directory
2. Return the saved path so `/learn` can move or index the file in the research project
3. Do not re-fetch if the content is already in the thread

## What Not to Save

- Do not save login pages, paywalled content stubs, or empty responses
- Do not save without telling the user the path
- Do not create directories unless the user asks
