# Navigation (`@dynatrace-sdk/navigation`)

> Env: ⚠️ **BROWSER-ONLY — do NOT use in server-side JS runtime functions.**
> Status: current

This SDK drives navigation within the browser app shell (opening apps/documents, sending intents between apps). It depends on the browser runtime and has **no effect in the server-side JS runtime**. Use it only in app frontend (React) code.

## Key exports (frontend use only)

`getAppLink` / `openApp`, `getDocumentLink` / `openDocument`, `sendIntent` / `sendIntentWithResponse`, `getIntent`, `getIntentLink`, `setPathChangeHandler`.

Full detail: [functions.md](functions.md) (per-function signatures + examples) · [types.md](types.md) (`Intent`, `IntentPayload`, `IntentResponseOkEnvelope`, `IntentResponseErrorEnvelope`).

## Notes

- Page tokens are app-manifest identifiers used as a public navigation API (distinct from URL routes) — see [registering page tokens](https://developer.dynatrace.com/develop/page-tokens/).
- Don't hardcode app IDs — availability isn't guaranteed across platform instances.

Canonical reference: https://developer.dynatrace.com/develop/sdks/navigation/
