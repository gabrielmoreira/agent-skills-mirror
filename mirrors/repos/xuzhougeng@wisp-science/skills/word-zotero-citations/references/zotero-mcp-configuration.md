# Zotero MCP hybrid-mode configuration

The live parts of this Skill require **hybrid mode** in zotero-mcp: local reads
from the running Zotero desktop (`http://127.0.0.1:23119`) plus web-API writes
using a personal API key. Without hybrid mode, every write tool fails with:

```text
Cannot perform write operations in local-only mode.
Add ZOTERO_API_KEY and ZOTERO_LIBRARY_ID to enable hybrid mode.
```

## Where the credentials are read

zotero-mcp loads configuration in this order (see `zotero_mcp/cli.py`):

1. Existing process environment variables (never overridden by files).
2. Standalone config `~/.config/zotero-mcp/config.json` under `client_env`.
3. Claude Desktop config discovery (when not disabled by `ZOTERO_NO_CLAUDE`).

The Skill helper scripts call `load_standalone_env_vars()` +
`apply_environment_variables()` before opening any Zotero client, so the
standalone config is sufficient when the process environment is empty.

## Minimal standalone config

Create or edit `~/.config/zotero-mcp/config.json`:

```json
{
  "client_env": {
    "ZOTERO_API_KEY": "<your zotero.org API key with library write access>",
    "ZOTERO_LIBRARY_ID": "<your numeric Zotero user ID>",
    "ZOTERO_LIBRARY_TYPE": "user",
    "ZOTERO_LOCAL": "true"
  }
}
```

- `ZOTERO_LOCAL=true` keeps reads on the local desktop API (fast, includes
  attachments) while writes use the web API with the key.
- The library ID must be your numeric Zotero **user ID** (visible in
  `zotero_list_libraries` → `My Library` → `libraryID`, or via
  `zotero_switch_library`). The local SQLite convention `0`/`1` is **not** the
  web-API library ID.
- The API key must have **personal library read + write** permission. Create it
  at `https://www.zotero.org/settings/keys`.

## How to apply it

1. **Back up** the existing config first:
   `Copy-Item ~\.config\zotero-mcp\config.json ~\.config\zotero-mcp\config.json.bak`
2. Add only the `client_env` block; leave any existing top-level keys
   (`semantic_search`, etc.) untouched.
3. **Restart the zotero-mcp connector** (in wisp-science: Settings → the Zotero
   MCP/connector entry → reconnect/restart). A running connector will not
   re-read the file.
4. Verify with a read-only probe:
   - `zotero_list_libraries` should still show `My Library`;
   - `zotero_switch_library(library_id=<your user ID>, library_type='user')`
     should succeed;
   - a `zotero_search_collections` call should work.
5. Verify write access with an idempotent action you are prepared to keep:
   - `zotero_create_collection(name='<probe>')`, then read it back, then
     `zotero_delete_collection` only after confirming it is empty. This is the
     step that failed in the 2026-08-15 run when the connector had not been
     restarted.

## Secrets hygiene

- Never paste an API key into chat; write it directly into the config file or
  the connector's secret store.
- The config file and the whole `~/.config/zotero-mcp/` directory should be
  excluded from version control.
- Rotate the key at `https://www.zotero.org/settings/keys` if it has ever been
  exposed in a chat transcript.

## Runtime identity used by the Skill

The Skill scripts derive the Zotero user identity exclusively from
`ZOTERO_LIBRARY_ID` (and the `library_type=user` convention). A task
**collection** is created by name under `My Library`; the collection key is
captured into `zotero-item-selection.json` and later bound into the manifest
and Refresh authorization. Item keys are never guessed; they come from
read-back verification of DOI matches.
