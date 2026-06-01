---
name: useragent-get-useragent
api: User Agent Parser
method: GET
path: /v1/technology/useragent
base_url: https://api.requiems.xyz
description: Parses a user agent string and returns structured information about the browser, OS, device, and bot status.
---

## Endpoint

**GET https://api.requiems.xyz/v1/technology/useragent**

## Parse User Agent

Parses a user agent string and returns structured information about the browser,
OS, device, and bot status.

## Parameters

| Name | Type   | Required | Location | Description                     |
| ---- | ------ | -------- | -------- | ------------------------------- |
| `ua` | string | yes      | query    | The user agent string to parse. |

## Response Example

```json
{
  "data": {
    "browser": "Chrome",
    "browser_version": "120.0",
    "os": "Windows",
    "os_version": "10/11",
    "device": "desktop",
    "is_bot": false
  },
  "metadata": {
    "timestamp": "2026-01-01T00:00:00Z"
  }
}
```

## Response Fields

| Field             | Type    | Description                                                                                 |
| ----------------- | ------- | ------------------------------------------------------------------------------------------- |
| `browser`         | string  | Detected browser name (e.g. Chrome, Firefox, Safari, Edge, Opera, Internet Explorer, Other) |
| `browser_version` | string  | Detected browser version (major.minor)                                                      |
| `os`              | string  | Detected operating system (e.g. Windows, macOS, Linux, Android, iOS, ChromeOS, Other)       |
| `os_version`      | string  | Detected OS version (format varies by platform)                                             |
| `device`          | string  | Device type — one of desktop, mobile, tablet, bot, or unknown                               |
| `is_bot`          | boolean | True when the user agent matches a known bot or crawler pattern                             |

## Errors

- `400` **bad_request** — The ua query parameter is missing.
