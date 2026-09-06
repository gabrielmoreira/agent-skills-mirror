# One NotFair MCP connection

Use one HTTP server named `NotFair` at `https://notfair.co/api/mcp/notfair`.
The connection is bound to the NotFair workspace selected during OAuth. Connect
Google Ads, Meta Ads, X Ads, LinkedIn Ads, Google Search Console, Google Analytics,
and GoHighLevel inside that workspace; do not add an MCP server per platform.

## Use the live capability descriptions

Choose tools from the connected server's current instructions, descriptions,
input schemas, and returned guidance. Use whatever discovery mechanism the host
or server provides when the needed capability is not already visible. These
skills describe the work and evidence required; they do not prescribe tool names,
MCP namespaces, operation IDs, argument shapes, batching limits, or call sequences.

Verify the requested workspace, platform, and account or property from live
connection information before claiming access. Follow returned setup guidance
when authorization or a platform connection is missing. Do not create a second
NotFair MCP connection to reach another platform.

Use the smallest set of reads that answers the user's question. An account-list
request needs an account list, not a full marketing audit. Preserve the user's
chosen scope and reuse existing context where it is sufficient.

For changes, establish the exact target and intended effect, stay within the
user's authorization, respect host and server approval controls, and verify the
result. Do not route writes through a read-only capability. Only claim success,
rollback support, stored history, or account access when the live result supports
it. If a capability is unavailable, explain that limitation rather than inventing
a tool or declaring the entire platform unsupported.

## Upgrade an existing installation

Update or reinstall the plugin through your host and start a new session. Keep
one `NotFair` connection at the URL above. If you manually added older per-platform
NotFair connections, remove those redundant host entries after the new connection
works. Plugin updates cannot remove entries you created outside the plugin.
Reauthorize the new connection when prompted; existing dedicated-platform tokens
do not grant the new `notfair` resource audience. Connect any missing platforms
inside the selected NotFair workspace.

For a manual host configuration:

```json
{
  "mcpServers": {
    "NotFair": {
      "type": "http",
      "url": "https://notfair.co/api/mcp/notfair"
    }
  }
}
```

## Host manifests

Claude Code, Codex, and Cursor's native manifest load `.mcp.json` with transport
type `http`. Agent Plugins hosts load the standards-based `mcp.json`, whose schema
requires transport type `streamable-http`. Gemini CLI embeds the native `http`
configuration in `gemini-extension.json`. These host-specific transport labels
all describe the same single NotFair Streamable HTTP connection and endpoint.

## Registry metadata

`server.json` is the single MCP Registry listing and the source used by the
registry publish workflow. Platform-specific registry manifests are retired;
they must not be reintroduced as plugin connections or publish targets.
