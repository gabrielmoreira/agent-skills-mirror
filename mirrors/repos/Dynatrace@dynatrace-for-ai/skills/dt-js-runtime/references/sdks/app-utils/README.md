# App Utils (`@dynatrace-sdk/app-utils`)

> Env: ✅ Server runtime
> Status: current

Utilities for app function executions — call a named app function programmatically.

## Key exports

| Export | Signature | Purpose |
|---|---|---|
| `functions.call` | `(functionName: string, options: { abortSignal?, data? }) => Promise<Response>` | Invoke an app function (one declared in the app's `app.config.json`) with an optional payload and cancellation signal. Returns a `Response`; use `.json()` / `.text()` to read the body. |

## Example

```ts
import { functions } from "@dynatrace-sdk/app-utils";

const res = await functions.call("my-function", { data: { foo: "bar" } });
const result = await res.json();
```

## Notes

- Returns a standard `Response`; supports cancellation via `abortSignal`.

Canonical reference: https://developer.dynatrace.com/develop/sdks/app-utils/
