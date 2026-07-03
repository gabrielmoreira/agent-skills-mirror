# `[METHOD] /path/{param}`

[One sentence: what it does + when you'd call it.]

## Example
```bash
curl -X [METHOD] https://api.example.com/v1/path/{{ID}} \
  -H "Authorization: Bearer sk_test_..." \
  -d '{ "field": "value" }'
```
```json
// 200 — real captured response
{ "id": "...", "status": "..." }
```

## Parameters
| Name | Type | Required | Default | Constraints |
|---|---|---|---|---|

## Errors (what to DO about each)
| Code | Body `error.type` | Means | Your move |
|---|---|---|---|
| 401 | | | |
| 422 | | | |
| 429 | | retry with backoff; see `Retry-After` |

## Gotchas
- [idempotency / pagination / eventual consistency / rate notes]

## Changes
| Date | Change | Breaking? |
|---|---|---|
