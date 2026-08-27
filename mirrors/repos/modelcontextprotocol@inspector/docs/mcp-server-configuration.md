# MCP server configuration

How to tell the Inspector **which MCP server(s) to connect to**. This model is shared by the Web, CLI, and TUI clients — the flags below are defined separately by each client but resolved by the same code in `core/mcp/node/config.ts`, so they behave identically everywhere except where noted.

Client-specific options (the web server port, the CLI method to invoke, TUI navigation) live in each client's README: [web](../clients/web/README.md) · [cli](../clients/cli/README.md) · [tui](../clients/tui/README.md).

## Two ways to specify a server

1. **From a file** — a catalog or session file listing one or more servers.
2. **Ad-hoc** — a command (stdio) or a URL (SSE / Streamable HTTP) on the command line.

The two do not mix. `--catalog` and `--config` are mutually exclusive with each other, and neither combines with an ad-hoc target. All three clients apply the same **source-selection** rules — the CLI and TUI through the shared `serverSourceConflict` helper (`core/mcp/node/config.ts`), web through an equivalent inline matrix in `clients/web/server/run-web.ts`. The two implementations diverge on two narrow axes, in opposite directions:

- **Web is stricter on `--header`:** it also rejects `--header` alongside `--catalog`/`--config`, because the CLI and TUI merge `--header` into per-server settings and web does not.
- **Web is looser on `--transport stdio`:** the CLI and TUI treat _any_ `--transport` as an ad-hoc marker, so `--catalog c.json --transport stdio` is rejected as a catalog/ad-hoc conflict there; web excludes `stdio` from that test and accepts the same combination, silently ignoring the flag.

## From a file: `--catalog` vs. `--config`

These look interchangeable and are not. The difference is **who owns the file**.

|                           | `--catalog <path>`                                 | `--config <path>`                                    |
| ------------------------- | -------------------------------------------------- | ---------------------------------------------------- |
| Writable by the Inspector | Yes — this is the Inspector's own server list      | No. Served as-is; never written, seeded, or migrated |
| When the file is missing  | Created and seeded (see below)                     | **Errors**                                           |
| Default path              | `~/.mcp-inspector/mcp.json`, or `MCP_CATALOG_PATH` | none — must be passed                                |
| Editable in the web UI    | Yes                                                | No (catalog CRUD is hidden)                          |
| Use it for                | your own working set of servers                    | a read-only session against a file you didn't write  |

Use `--config` when pointing the Inspector at a config file belonging to something else — a coworker's, a client application's, one checked into a repo. It guarantees the Inspector will not touch the bytes on disk, including any plaintext secrets in them.

### What a seeded catalog contains

A missing **writable** catalog is created on first use, but **what gets written differs by client**:

- **Web** seeds two sample servers (`DEFAULT_SEED_CONFIG` in `core/mcp/serverList.ts`) so a first launch has something to connect to immediately:

  ```json
  {
    "mcpServers": {
      "filesystem-server-default": {
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
      },
      "everything-server-default": {
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-everything"]
      }
    }
  }
  ```

- **CLI and TUI** seed an empty `{ "mcpServers": {} }` (`seedEmptyCatalog` in `core/mcp/node/config.ts`). They are non-interactive or list-driven, so sample entries would be noise rather than a starting point.

Seeding happens **once per file**, only when that file is absent — not once per client. All three surfaces default to the _same_ path (`~/.mcp-inspector/mcp.json`, `getDefaultMcpConfigPath()` in `core/storage/store-io.ts`), so whichever client runs first decides the contents: run `--cli` first and a later `--web` opens the empty catalog it wrote, with no sample servers. An existing catalog is never re-seeded, and a read-only `--config` is never seeded on any surface.

## Ad-hoc servers

Instead of a file, name one server directly:

```bash
# stdio — everything positional is the command to spawn
mcp-inspector node build/index.js

# HTTP / SSE
mcp-inspector --server-url https://api.example.com/mcp --transport http
```

Those run as written in the default (web) mode. Under `--cli` two extra rules apply:

- A `--method` is required — a CLI invocation with no method exits with `Method is required.`
- **The target must come first.** The CLI reads the leading run of non-dash tokens as the target, so anything after the first flag is no longer part of it:

  ```bash
  mcp-inspector --cli node build/index.js --method tools/list   # ✅ target, then flags
  mcp-inspector --cli --method tools/list node build/index.js   # ❌ target is dropped
  ```

  The second form does not error — `node build/index.js` is silently discarded and the Inspector falls back to your catalog, so it "works" against the wrong server. `--tui` has no such rule; Commander parses its arguments in any order.

### The `--` separator

A bare `--` is meaningful on every surface, but **web/tui and cli split it in opposite directions**. Read the one you're using.

**Web and TUI — everything _after_ `--` goes to the target command.** This is how you pass a flag the Inspector would otherwise consume:

```bash
mcp-inspector node build/index.js -- --config /etc/myserver.conf --verbose
```

Without the separator, `--config` would be read as the Inspector's own read-only-session flag. Web splits explicitly (`clients/web/server/run-web.ts`); the TUI has no split of its own but Commander's default end-of-options handling appends the remainder to the target, so post-`--` tokens land in the same place.

They differ on **when you need it**, though. Web sets `allowUnknownOption()` + `allowExcessArguments()`, so a dash flag the Inspector does not define (`--verbose`) already falls through to the target without a separator — on web `--` is only needed for a flag the Inspector _does_ define. The TUI sets neither, so any unrecognized dash flag is a parse error: on the TUI you need `--` for **every** dash argument meant for the server.

**CLI — reversed: everything _before_ `--` is the server target, everything _after_ is the Inspector's own options.**

```bash
mcp-inspector --cli node build/index.js -- --method tools/list
```

So under `--cli` the separator does **not** protect an argument from the Inspector — it does the opposite, and the web example above, run verbatim, would have `--config /etc/myserver.conf` consumed as a read-only-session flag (then rejected as a catalog/ad-hoc conflict). Leading-dash arguments for the server still get through; they just go on the other side of the separator, where the whole pre-`--` run is taken as the target verbatim:

```bash
mcp-inspector --cli node build/index.js --config /etc/myserver.conf --verbose -- --method tools/list
```

Without a `--` on the line the target is only the leading run of **non-dash** tokens, so the separator is required whenever the server itself takes flags.

## The shared flags

| Flag                     | Meaning                                             | Notes                                                                                                                                                                                |
| ------------------------ | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `--catalog <path>`       | Writable catalog file                               | Env fallback `MCP_CATALOG_PATH`                                                                                                                                                      |
| `--config <path>`        | Read-only session file                              | Errors if absent                                                                                                                                                                     |
| `--server <name>`        | Select one named server from the file               | **Selects only under `--cli`.** Web ignores it — warning with `--catalog`/`--config`, silently with an ad-hoc target; the TUI does not define it and rejects it as an unknown option |
| `--transport <type>`     | `stdio`, `sse`, or `http`                           | Ad-hoc targets only — enforced on cli/tui; web exempts `--transport stdio` (see above)                                                                                               |
| `--server-url <url>`     | Server URL for SSE / Streamable HTTP                | Ad-hoc targets only                                                                                                                                                                  |
| `--cwd <path>`           | Working directory for a stdio server process        |                                                                                                                                                                                      |
| `-e <KEY=VALUE>`         | Environment variable for a stdio server; repeatable |                                                                                                                                                                                      |
| `--header "Name: Value"` | HTTP header for an HTTP/SSE server; repeatable      | On web, requires an ad-hoc HTTP/SSE server                                                                                                                                           |
| `[target...]`            | Positional command or URL for one ad-hoc server     |                                                                                                                                                                                      |

**`MCP_CATALOG_PATH` and ad-hoc targets differ by client.** The **CLI** ignores the env var when an ad-hoc target is given (a positional command, `--server-url`, or `--transport`), so a shell that exports it can still run one-off ad-hoc invocations without tripping the catalog/ad-hoc conflict. **Web and TUI read it unconditionally** — with it exported, an ad-hoc invocation such as `mcp-inspector --tui node build/index.js` is rejected as `--catalog cannot be combined with an ad-hoc server URL/command`. Unset the variable for that invocation on those two surfaces.

## File format

The file is the familiar MCP client-config shape — an `mcpServers` object keyed by server name — plus Inspector-specific per-server settings.

**stdio**

```json
{
  "mcpServers": {
    "my-server": {
      "type": "stdio",
      "command": "node",
      "args": ["build/index.js"],
      "env": { "API_KEY": "…" },
      "cwd": "/path/to/server"
    }
  }
}
```

**Streamable HTTP / SSE**

```json
{
  "mcpServers": {
    "my-http-server": {
      "type": "http",
      "url": "https://api.example.com/mcp",
      "headers": { "X-Tenant": "acme" }
    }
  }
}
```

`type` may be `stdio`, `http` (Streamable HTTP), or `sse`.

### Inspector-specific per-server fields

These have no analog in the broader `mcp.json` ecosystem. Each is **omitted on write when it equals its default**, so a round-trip through the Inspector keeps the file diff minimal.

| Field                                  | Default    | Meaning                                                                                                                                                                                     |
| -------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `protocolEra`                          | `"legacy"` | `"legacy"` \| `"auto"` \| `"modern"` — which protocol era to negotiate, orthogonal to the transport                                                                                         |
| `modernLogLevel`                       | `"debug"`  | Per-request log level stamped on modern connections, or `"off"`. Legacy connections ignore it                                                                                               |
| `roots`                                | —          | Roots advertised via the `roots` client capability; each is `{ uri, name? }`                                                                                                                |
| `metadata`                             | —          | Default `_meta` payload merged into every outgoing request — a JSON object; values may be any JSON except for the reserved keys noted below. Sent by all three clients |
| `connectionTimeout` / `requestTimeout` | —          | Timeouts in ms                                                                                                                                                                              |
| `taskTtl`                              | `60000`    | TTL in ms for tasks created via "Run as task" (`DEFAULT_TASK_TTL_MS`)                                                                                                                       |
| `autoRefreshOnListChanged`             | `false`    | Refresh lists automatically on `*/list_changed` instead of only flagging the indicator                                                                                                      |
| `paginatedLists`                       | `false`    | Fetch tools/resources/prompts one page at a time instead of auto-aggregating                                                                                                                |
| `advertisedExtensions`                 | —          | Per-extension overrides for what the Inspector declares in `capabilities.extensions`                                                                                                        |
| `maxFetchRequests`                     | `1000`     | Network-log retention for this server (`DEFAULT_MAX_FETCH_REQUESTS`); `0` means unlimited                                                                                                   |
| `oauth`                                | —          | `{ clientId, clientSecret, scopes, requestRefreshToken, authorizationParams, authorizationUrl, tokenUrl, enterpriseManaged, onInsufficientScope }`                                                               |

`metadata` is a JSON **object**, and its values may be any JSON — an object, an array, a number, a boolean, `null` — not only a string. The MCP spec does not restrict `_meta` value types in general, and the SDK models the field as a passthrough object, so the Inspector does not narrow it either ([#1910](https://github.com/modelcontextprotocol/inspector/issues/1910)). Edit it in Server Settings → Request Metadata, which is a JSON editor rather than the key/value rows `headers` and `env` use; text that is not a JSON object is flagged inline and not applied.

```jsonc
"metadata": {
  "tenant": "acme",
  "trace": { "id": "abc123", "sampled": true },
  "features": ["apps", "tasks"]
}
```

> **A few keys are reserved and keep their own shape.** "Any JSON" holds for keys you invent, not for the ones the protocol defines. In the current SDK those are `progressToken` (a string or a **safe** integer — one JavaScript represents exactly, so nothing past `Number.MAX_SAFE_INTEGER`) and `io.modelcontextprotocol/related-task` (`{ "taskId": "<string>" }`). A reserved key whose value does not match is **dropped from the outgoing request**, with a warning naming the key — because a conforming server rejects the _entire_ request over one bad reserved member, rather than ignoring that key. Everything else in the payload is sent unchanged.

> **All three clients send it.** Web, TUI, and CLI alike merge this payload into every outgoing request — the setting belongs to the server, not to the client that happens to read it. The CLI was the exception until [#2093](https://github.com/modelcontextprotocol/inspector/issues/2093): it never passed the persisted value to its client, so a `metadata` entry was silently inert for `--cli` runs. The CLI's per-invocation `--metadata` flag still applies on top, and its keys win on a collision.

> **Reading an older file.** Before #1910 this field was a `[{ "key": …, "value": … }]` pair array. That shape is still **read**, so an existing `mcp.json` keeps working unchanged; it is never written back, so the field is rewritten as an object the next time the Inspector saves the entry.

`oauth.requestRefreshToken` (default `true`) controls whether the Inspector declares the `refresh_token` grant when it registers its OAuth client. Set it to `false` — or uncheck **Request refresh token** in Server Settings → Authorization — when that grant costs you more than it buys.

The chain it breaks runs through the SDK. `determineScope()` appends `offline_access` to the requested scope when the authorization server advertises that scope **and** the client metadata declares `refresh_token`; `startAuthorization()` then appends `prompt=consent` whenever `offline_access` is in the effective scope. On Microsoft Entra ID a forced `prompt=consent` from a non-admin user, for an app whose permissions require admin consent, is routed into the admin-consent workflow and rejected with `AADSTS90094` — even after a tenant admin has already granted consent ([#2068](https://github.com/modelcontextprotocol/inspector/issues/2068)). Only `false` is written to disk, so a server that never touched the setting keeps a minimal entry.

The setting suppresses the grant declaration and the SDK's scope augmentation — that is the whole of what it controls. It does not decide what the authorization server issues: token issuance is the AS's call, and a preconfigured client is reused with whatever its server-side registration already permits, so a refresh token can still come back and the Inspector will store and use it. Expect a fresh interactive sign-in on expiry where the AS honors the narrowed request; don't rely on it.

> **It removes the SDK's *automatic* `offline_access`, and nothing more.** `prompt=consent` keys off `offline_access` being in the effective scope; it never looks at `grant_types`. So the prompt still goes out if `offline_access` reaches that scope by another route — you listed it yourself in **Scopes**, or you left Scopes blank and the resource server's metadata advertises it in `scopes_supported`. Unchecking this box is not on its own a guarantee that the consent prompt is gone: check the Scopes field too. The web form flags the first case inline.

> **Not applied to the enterprise-managed authorization request** (`oauth.enterpriseManaged`). The setting does reach the OAuth client metadata under EMA — that flow wraps the same provider and forwards its metadata — but the leg you actually sign in through authorizes against the enterprise IdP with a fixed `openid offline_access` scope that this setting cannot change. So it cannot affect EMA's consent behavior, which is what the checkbox is for. The web form says so inline when EMA is on.

> **It applies on the next connect, not to the live connection.** OAuth is connection-time configuration here — like the client credentials, the scopes, and the endpoint overrides beside it — so a client that is already connected keeps the metadata it was built with. Reconnect for the change to reach the authorization flow.

> **A scope inherited from an earlier grant is dropped from the request.** A successful authorization persists the scope the authorization server granted, which for a default-on client includes `offline_access`. Left alone, that value would come straight back on the next connect and re-trigger `prompt=consent` with the box unchecked. So when the grant is declined the Inspector filters `offline_access` out of what it *requests* — unless you configured it in **Scopes** yourself, in which case it is requested regardless of what storage holds (honoring it has to mean *adding* it when the persisted scope predates your change, not merely declining to strip it). The stored scope is not rewritten at filter time: re-checking the box restores the previous behavior instead of finding the value destroyed. It does update on the next successful grant — the Inspector records what it actually requested, so an authorization server that omits `scope` from the token response (RFC 6749 §5.1, meaning it granted what was asked) still leaves storage agreeing with the narrowed request rather than keeping the old value.

> **Two pieces of state outlive the setting, and neither is cleared by unchecking it.** A refresh token issued before the opt-out stays usable — the SDK's refresh path posts the stored token with `grant_type=refresh_token` without consulting the client metadata, so such a server can keep refreshing silently and you may not observe the cost described above at all. And the registration already held at the authorization server still lists the grant, because turning the setting off changes what the Inspector *declares*, not what the AS has recorded.
>
> **Clear stored OAuth state** (Server Settings → Authorization) clears the Inspector's **local** copies — the tokens and the client information — which is enough for the first. It is not a revocation: it cannot reach the authorization server. For the second, what happens next depends on how the client was obtained. A **dynamically registered** client is registered afresh on the next connect, and the new registration declares only `authorization_code`; the old one still exists at the AS, unused. A **preconfigured `oauth.clientId`** is reused as-is, so changing what that client declares is done at the authorization server, not here.

`oauth.authorizationParams` is a string→string record of extra query parameters merged into the OAuth **authorization request** URL only — never the token request. Use it for provider-specific hints the core specs don't standardize (Keycloak's `kc_idp_hint`, OIDC's `login_hint` / `prompt` / `acr_values`, Auth0's `audience`). The protocol-critical parameters — `client_id`, `code_challenge`, `code_challenge_method`, `redirect_uri`, `resource`, `response_type`, `scope`, `state` — are **reserved**: the web form rejects them inline, and any that reach the merge anyway are dropped with a warning rather than overriding what the flow set (overriding them breaks PKCE, the CSRF state binding, or RFC 8707). Edit them in Server Settings → Authorization ("Additional authorization parameters"), beside Scopes.

`oauth.authorizationUrl` and `oauth.tokenUrl` override the `authorization_endpoint` and `token_endpoint` that authorization-server metadata discovery resolved. The Inspector deliberately has no such fields by default — it resolves both from the AS's metadata document, exactly as a real MCP host does — but a server under development often advertises its _production_ authorization server while you want to hit staging. Set either (they are independent) to an absolute `http(s)` URL and it replaces what the metadata returned, for both the authorization request and the token request; leave blank to use discovery. A malformed value is flagged inline in the form and dropped with a warning at connect time rather than failing the connection. Edit them in Server Settings → Authorization ("Authorization URL override" / "Token URL override").

They redirect the **endpoints**, not the authorization server's identity: `issuer` is left exactly as discovery returned it, because that is what RFC 9207 / SEP-2352 validate the callback's `iss` against to defend against an authorization-server mix-up. So they fit alternate endpoints of the _same_ logical issuer — a staging deployment fronting the same issuer, a local proxy. Point one at an authorization server advertising a **different** issuer and the callback is rejected as an issuer mismatch before the code is redeemed; that is the mix-up defense working, and it is not disabled to make the override succeed.

They are **not applied under enterprise-managed authorization** (`oauth.enterpriseManaged`), for the same reason `oauth.authorizationParams` isn't: that flow authorizes against the enterprise IdP — a different authorization server, whose OIDC discovery would otherwise be rewritten too, pointing the IdP login (or the IdP code exchange) at the resource server's authorization server.

> Because the override is applied to the _discovered metadata document_, a server whose authorization server publishes no metadata at all is unaffected — there the SDK falls back to `/authorize` and `/token` on the AS origin, and there is nothing to override.

A catalog carrying these fields:

```json
{
  "mcpServers": {
    "my-modern-server": {
      "type": "http",
      "url": "https://api.example.com/mcp",
      "protocolEra": "modern",
      "modernLogLevel": "info",
      "roots": [{ "uri": "file:///Users/me/project", "name": "project" }]
    }
  }
}
```

## Per-client behavior

|                              | Web                                                           | CLI                                     | TUI                                              |
| ---------------------------- | ------------------------------------------------------------- | --------------------------------------- | ------------------------------------------------ |
| Seeds a missing catalog with | two sample servers                                            | `{}`                                    | `{}`                                             |
| `--server`                   | a no-op — warns with a file source, silent with an ad-hoc one | yes — the only surface where it selects | not defined — `error: unknown option '--server'` |
| `--` separator               | yes — after `--` → target                                     | **reversed** — before `--` → target     | yes — after `--` → target (Commander default)    |
| OAuth client flags           | no (uses the Client Settings dialog)                          | yes                                     | yes                                              |
| Catalog CRUD                 | yes                                                           | read-only consumer                      | read-only consumer                               |

The CLI and TUI do not perform catalog CRUD yet — they are read consumers — so the writable/read-only split currently surfaces there only as **seed-if-missing** (`--catalog` / default) vs. **error-if-missing** (`--config`). Full writable persistence is tracked in [#1482](https://github.com/modelcontextprotocol/inspector/issues/1482) / [#1432](https://github.com/modelcontextprotocol/inspector/issues/1432).

## Related

- [Migrating from v1 to v2](./v1-to-v2-migration.md) — why `--config` means something narrower than it did in v1, and what `--catalog` replaced.
- [Launcher and config consolidation](./launcher-config-consolidation-plan.md) — how the launcher and the shared config processor fit together.
- [Reviewing an MCP App](./mcp-app-review.md) — the CLI-first App review recipe.
