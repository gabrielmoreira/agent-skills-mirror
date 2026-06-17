# Navigation — Functions

> ⚠️ BROWSER-ONLY — frontend (React) use only; no effect in the server-side JS runtime.

Import from `@dynatrace-sdk/navigation`.

| Function | Returns | Purpose |
|---|---|---|
| `openApp(appId, pageToken?)` | `void` | Navigate the user to an app (or an internal route via `pageToken`). |
| `getAppLink(appId, pageToken?)` | `string` | Build a link that launches an app (optional internal route). |
| `openDocument(documentId)` | `void` | Navigate the user to a document. |
| `getDocumentLink(documentId)` | `string` | Build a link that opens a document. |
| `sendIntent(intentPayload, options?)` | `void` | Send an `IntentPayload` to the platform; user picks the destination app among those whose declarations match. Undeclared properties are stripped. `options`: `recommendedAppId`, `recommendedIntentId`, `keyProperties`. |
| `sendIntentWithResponse(intentPayload, options?)` | `Promise<…>` | Like `sendIntent` but requests `responseProperties` back from the handling app. |
| `getIntent()` | `Intent \| null` | Retrieve the intent passed to this app; only valid on the intent-handling route `/intent/:intentId` (else `null`). |
| `getIntentLink(intentPayload, appId?, intentId?)` | `string` | Build a link that launches the App Shell (or a specific app) to handle an intent. |
| `setPathChangeHandler(handler)` | `void` | Register a custom handler for externally-triggered URL path changes (default: reload via document location). |

## Notes

- App/document availability varies across environments — links aren't guaranteed to resolve.
- To receive intents, declare them in the app manifest and add an `/intent/:intentId` route — see [receiving intents](https://developer.dynatrace.com/develop/intents/receive-intents/).
