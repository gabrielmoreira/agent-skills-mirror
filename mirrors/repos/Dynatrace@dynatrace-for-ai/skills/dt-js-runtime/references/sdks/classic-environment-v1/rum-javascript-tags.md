# `rumJavaScriptTagManagementClient`

Manage RUM JavaScript tags, snippets, and versions for manual web instrumentation. Import:

```ts
import { rumJavaScriptTagManagementClient } from "@dynatrace-sdk/client-classic-environment-v1";
```

| Method | Purpose |
|---|---|
| `getJsTagComplete` | Get the complete RUM JavaScript tag. |
| `getJsTagSri` | Get the RUM tag with Subresource Integrity. |
| `getJsScript` | Get the RUM JS script. |
| `getJsInlineScript` | Get the inline RUM script. |
| `getAsyncCodeSnippet` / `getSyncCodeSnippet` | Async / sync code snippets. |
| `getJsLatestVersion` | Latest available RUM JS version. |
| `getJsAllAvailableVersions` | All available RUM JS versions. |
| `getJsConfiguredVersions` | Configured RUM JS versions. |
| `getAppRevision` | Get the application revision. |
| `getManualApps` | List manually-instrumented applications. |
