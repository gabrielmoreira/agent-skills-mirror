---
name: useragent-post-batch
api: User Agent Parser
method: POST
path: /v1/technology/useragent/batch
base_url: https://api.requiems.xyz
description: Parses up to 50 user agents in a single request.
---

## Endpoint

**POST https://api.requiems.xyz/v1/technology/useragent/batch**

## Batch Parse User Agents

Parses up to 50 user agents in a single request.

## Parameters

| Name | Type | Required | Location | Description |
| ---- | ---- | -------- | -------- | ----------- |
| `user_agents` | array | yes | body | Array of user agents to parse (min: 1, max: 50). |

## Request Example

```json
{
   "user_agents": [
     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
     "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"
   ]
 }
```

## Response Example

```json
{
  "data": {
    "results": [
      {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "data": {
          "browser": "Chrome",
          "browser_version": "124.0",
          "os": "Windows",
          "os_version": "10/11",
          "device": "desktop",
          "is_bot": false
        }
      },
      {
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
        "data": {
          "browser": "Safari",
          "browser_version": "",
          "os": "iOS",
          "os_version": "17.0",
          "device": "mobile",
          "is_bot": false
        }
      }
    ],
    "total": 2
  },
  "metadata": {
    "timestamp": "2026-05-19T05:33:14Z"
  }
}
```

## Response Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `results` | array | List of parsed user agents results returned in the same order as the input user agents. |
| `results[].user_agent` | string | The original user agent string from the input. |
| `results[].data` | object | Parsed user agent details. |
| `results[].data.browser` | string | Detected browser name (e.g. Chrome, Firefox, Safari, Edge, Opera, Internet Explorer, Other). Empty if not detected. |
| `results[].data.browser_version` | string | Detected browser version (major.minor). Empty if not detected. |
| `results[].data.os` | string | Detected operating system (e.g. Windows, macOS, Linux, Android, iOS, ChromeOS, Other). Empty if not detected. |
| `results[].data.os_version` | string | Detected OS version (format varies by platform). Empty if not detected. |
| `results[].data.device` | string | Device type — one of desktop, mobile, tablet, bot, or unknown |
| `results[].data.is_bot` | boolean | True when the user agent matches a known bot or crawler pattern |
| `total` | integer | Total number of parsed user agent results returned. |

## Errors

- `422` **validation_failed** — The user_agents array is missing, empty, or contains more than 50 items.
- `400` **bad_request** — Invalid JSON, malformed request body, or unexpected field types.
