# Available APIs & Modules

What you can `import` and call inside the Dynatrace server-side JS runtime. For quotas and forbidden constructs see [limits-and-restrictions.md](limits-and-restrictions.md); for HTTP details see [fetch.md](fetch.md).

## Standard built-ins

All standard JavaScript (ECMAScript) built-ins are supported, plus the **ECMAScript Internationalization API** (`Intl`).

## Web APIs

Available Web/Web-platform APIs include:

- **Fetch** — `fetch`, `Request`, `Response`, `Headers` (see [fetch.md](fetch.md))
- **Streams** — `ReadableStream`, `WritableStream`, `TransformStream`
- **Compression** — `CompressionStream`, `DecompressionStream`
- **Web Crypto** — `crypto`, `crypto.subtle` (SubtleCrypto)
- **Encoding** — `TextEncoder`, `TextDecoder`, `atob`, `btoa`
- **Performance** — `performance` timing
- **Events & timers** — event handling, `setTimeout`/`setInterval`
- **`structuredClone`**, `URL`, `URLSearchParams`

> Deprecated properties of Web APIs might not be supported.

## Node.js compatibility modules

A compatibility layer exposes a subset of Node.js core modules:

| Module | Notes |
|---|---|
| `assert` | supported |
| `buffer` | supported |
| `crypto` | supported; **some algorithms are unsupported** |
| `http` / `https` | **client requests only — server creation is not available** |
| `path` | supported |
| `stream` | supported |
| `util` | supported |
| `zlib` | supported; **Brotli compression is missing** |

**Not supported:** third-party packages that rely on TCP/UDP sockets or filesystem access.

Full reference: https://developer.dynatrace.com/develop/reference/javascript-runtime/
