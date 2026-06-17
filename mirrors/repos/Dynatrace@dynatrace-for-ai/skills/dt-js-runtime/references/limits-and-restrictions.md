# Runtime Limits & Restrictions

Hard quotas and unavailable capabilities of the Dynatrace server-side JS runtime.

## Limits

| Limit | Value |
|---|---|
| Execution timeout | 120 s |
| Memory | 256 MB RAM |
| Input size | 5 MB max |
| Output size | 5 MB max |
| Outbound network | Allowlisted external hosts only (full URLs); relative `/platform/...` paths unrestricted — see [fetch.md](fetch.md) |

## Not available

- **Inter-app function calls** — a function cannot invoke another app's function.
- **Binary responses** — functions cannot return raw binary payloads.
- **WebSocket API** — not available.
- **Raw TCP/UDP sockets** — not available; only HTTP(S) via `fetch` / the Node `http`/`https` client.
- **Filesystem access** — not available. Third-party packages that rely on sockets or the filesystem will not work.

## Forbidden constructs

- `eval()` — disabled (security).
- `new Function()` — disabled (security).
- `globalThis.window` — deprecated; unreliable for browser detection and should not be used.

Deprecated properties of otherwise-supported Web APIs may also be unavailable — see [apis-and-modules.md](apis-and-modules.md).

Full reference: https://developer.dynatrace.com/develop/reference/javascript-runtime/
