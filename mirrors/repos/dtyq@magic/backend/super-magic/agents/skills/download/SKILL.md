---
name: download
description: Use when external HTTP or HTTPS files must be downloaded reliably into the workspace, especially for multiple files, large videos or archives, resumable transfers, custom Referer or Origin headers, or downloads that may take a long time.
---

# Download

Use `download_from_urls` through Code Mode with `run_sdk_snippet`. Use the same tool for one or multiple files. It handles batch concurrency, progress, retries, transfer timeouts, partial files, and HTTP Range internally.

## Normal Call

Usually pass only `url` and `file_path`:

```python
from sdk.tool import tool

result = tool.call("download_from_urls", {
    "downloads": [
        {
            "url": "https://example.com/media/video.mp4",
            "file_path": "media/video.mp4",
        },
        {
            "url": "https://example.com/data/archive.zip",
            "file_path": "data/archive.zip",
        },
    ],
})
print(result.content)
```

Always check `result.ok` and read `result.content`. A batch may contain both successful and failed items, so keep the full summary.

## Request Headers

Omit `headers` by default. The download engine automatically sends browser-compatible headers and a same-origin `Referer`. If a first request receives a likely source-validation rejection, it retries once with a same-origin `Origin`.

Provide headers only when the task already supplies a more accurate access context:

```python
result = tool.call("download_from_urls", {
    "downloads": [{
        "url": "https://cdn.example.com/assets/report.pdf",
        "file_path": "reports/report.pdf",
        "headers": {
            "Referer": "https://www.example.com/reports/latest",
            "Origin": "https://www.example.com",
        },
    }],
})
print(result.content)
```

- Use a full page URL for `Referer` and only its scheme plus host for `Origin`.
- Pass `Cookie` or `Authorization` only when the user explicitly provided the value for this download.
- Never invent credentials or attempt to bypass login, CAPTCHA, WAF, DRM, or access controls.

## Existing Files

`overwrite` defaults to `true` and is normally omitted. Set it to `false` only when the user wants to keep an existing complete target file.

If the requested destination may contain user-authored content and overwrite intent is unclear, call `ask_user` before starting Code Mode. `ask_user` cannot be called from inside a `run_sdk_snippet` script. Do not ask again when the user explicitly requested that destination or requested a replacement download.

## Resume Behavior

On a recoverable failure, repeat the same `url`, `file_path`, and headers. The engine finds the preserved partial state and resumes automatically when the server supports HTTP Range. If the server does not safely support the saved range, the engine restarts that file without appending incompatible bytes.

Do not:

- read or pass internal `.part` or `.part.meta` paths;
- calculate offsets or send `Range` or `If-Range`;
- create resume tokens;
- pass download timeout, retry, concurrency, or chunk-size controls;
- change the destination path when the intent is to resume the same file.

When a failed item reports `next action: retry_same_request`, retry the unchanged item. If it reports `review_request`, inspect the URL, destination, or required access context before retrying.
