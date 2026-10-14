# Source Material Import

Used by Step 2 of `prompts/flows/create.md` and by the append flow in `prompts/flows/evolve.md`. Resolve every `prompts/...` and `tools/...` path against `{distilly_skill_root}` (see `SKILL.md`).

| Task | Tool |
|------|------|
| Read PDF documents | `Read` tool (native PDF support) |
| Read image screenshots | `Read` tool (native image support) |
| Read MD/TXT files | `Read` tool |
| Parse Lark message JSON export | `Bash` → `python3 "{distilly_skill_root}/tools/feishu_parser.py"` |
| Lark auto-collect (recommended) | `Bash` → `python3 "{distilly_skill_root}/tools/feishu_auto_collector.py"` |
| Lark docs (browser session) | `Bash` → `python3 "{distilly_skill_root}/tools/feishu_browser.py"` |
| Lark docs (MCP App Token) | `Bash` → `python3 "{distilly_skill_root}/tools/feishu_mcp_client.py"` |
| DingTalk auto-collect | `Bash` → `python3 "{distilly_skill_root}/tools/dingtalk_auto_collector.py"` |
| Parse email .eml/.mbox | `Bash` → `python3 "{distilly_skill_root}/tools/email_parser.py"` |

**Credential rules (Lark / DingTalk / Slack)**: App Secrets, user_access_token, refresh_token, Bot Tokens and OAuth codes must never enter the conversation context.
- **Never** ask the user to send you these values, and never put them in command arguments, script source, output files or replies.
- For setup, ask the user to run the script's `--setup` **in their own terminal** (plus `--login` for Lark private chats). Secrets are typed with hidden input and stored in the OS keychain (when `keyring` is installed) or in `~/.distilly/*_config.json` (mode 0600). The user may instead export environment variables (`FEISHU_APP_ID` / `FEISHU_APP_SECRET` / `FEISHU_USER_ACCESS_TOKEN` / `DINGTALK_APP_KEY` / `DINGTALK_APP_SECRET` / `SLACK_BOT_TOKEN`). `--setup` / `--login` refuse to run without an interactive terminal, so you cannot run them on the user's behalf.
- Use `--check` to see whether credentials are ready; it shows only the source (env / keychain / config file), never the values.
- If you write your own script against the APIs, load credentials from environment variables or `credentials.resolve(...)` in `tools/credentials.py`, and never print them.
- If the user pastes a secret into the chat anyway: do not repeat or use it, tell them to rotate it on the open platform, then reconfigure as above.

The Lark-labelled compatibility collectors currently connect to the China-region `open.feishu.cn` / `feishu.cn` endpoints. International `larksuite.com` tenant routing is not implemented yet.

## Choose a source

Ask the user how they'd like to provide materials:

```
How would you like to provide source materials?

  [A] Lark Auto-Collect (recommended)
      Enter name, auto-pull messages + docs + spreadsheets

  [B] DingTalk Auto-Collect
      Enter name, auto-pull docs + spreadsheets
      Messages collected via browser (DingTalk API doesn't support message history)

  [C] Lark Link
      Provide doc/Wiki link (browser session or MCP)

  [D] Upload Files
      PDF / images / exported JSON / email .eml

  [E] Paste Text
      Copy-paste text directly

Can mix and match, or skip entirely (generate from manual info only).
```

---

### Option A: Lark Auto-Collect (Recommended)

First-time setup. Check whether credentials are ready:
```bash
python3 "{distilly_skill_root}/tools/feishu_auto_collector.py" --check
```
If not, ask the user to run this **in their own terminal** (do not run it yourself, and do not ask for the App Secret in chat):
```bash
python3 "{distilly_skill_root}/tools/feishu_auto_collector.py" --setup
```

**Group chat collection** (uses tenant_access_token, bot must be in the group):
```bash
python3 "{distilly_skill_root}/tools/feishu_auto_collector.py" \
  --name "{name}" \
  --output-dir ./knowledge/{slug} \
  --msg-limit 1000 \
  --doc-limit 20
```

**Private chat (P2P) collection** (requires user_access_token + p2p chat_id):

Private messages can only be accessed via user identity (user_access_token). App identity cannot access private chats.

**Prerequisites** (the user completes these on the Open Platform and in their own terminal; you only guide):
1. **Lark app credentials**: `app_id` / `app_secret` configured via `--setup` or environment variables (confirm with `--check`)
2. **User scopes**: The app must have these user scopes enabled:
   - `im:message` — read/send messages as user
   - `im:chat` — read chat list as user
3. **Redirect URL**: add `http://www.example.com` under the app's "Security Settings → Redirect URLs"

If the user is missing any of these, guide them through setup. Don't assume anything is pre-configured.

**Getting user_access_token**: ask the user to run this **in their own terminal**:
```bash
python3 "{distilly_skill_root}/tools/feishu_auto_collector.py" --login
```
The script prints the authorization URL; after authorizing in the browser, the user pastes the callback URL into the terminal (hidden input) and the token goes straight into the keychain or config file. Never ask the user to send the code or token in chat.

When the token expires (about 2 hours), you can refresh it yourself with no secret input:
```bash
python3 "{distilly_skill_root}/tools/feishu_auto_collector.py" --refresh
```

**Getting the p2p chat_id**:

Users typically don't know their chat_id. The user can open the private chat in Lark and find the `oc_` chat_id in the chat link or developer tools. If you write a script to obtain it, the script must read the token from `credentials.resolve("feishu", ...)` or environment variables and must not print it:

- **Method**: Send a message to the other user's open_id — the response includes the chat_id (this really sends a message, so ask the user first)
  ```python
  POST https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id
  Header: Authorization: Bearer <read via credentials.resolve, never hard-coded>
  Body: {"receive_id": "{target_open_id}", "msg_type": "text", "content": "{\"text\":\"hello\"}"}
  # The chat_id in the response is the p2p chat ID
  ```
- **Important**: `GET /im/v1/chats` does NOT return p2p chats — this is an API limitation, not a permission issue. Do not try to use it for finding private chats.
- If the user doesn't know the target's open_id, use tenant_access_token to search contacts:
  ```python
  GET https://open.feishu.cn/open-apis/contact/v3/scopes
  # Returns open_ids of all users visible to the app
  ```

**Running collection**:

Once credentials are ready and you have the chat_id (the script loads the token itself; it never appears on the command line):
```bash
python3 "{distilly_skill_root}/tools/feishu_auto_collector.py" \
  --open-id {target_open_id} \
  --p2p-chat-id {chat_id} \
  --name "{name}" \
  --output-dir ./knowledge/{slug} \
  --msg-limit 1000
```

**Flexibility principle**: The above API calls don't have to go through the collector script. If the script doesn't work or doesn't fit the scenario, write Python scripts directly against the same endpoints, but load credentials through `credentials.resolve("feishu", feishu_auto_collector.load_config())` or environment variables; they must never appear in script source, command arguments or output. Key API reference:
- Get token: `POST /auth/v3/tenant_access_token/internal` (wrapped by `get_tenant_token` in the collector)
- Send message (get chat_id): `POST /im/v1/messages?receive_id_type=open_id`
- Fetch messages: `GET /im/v1/messages?container_id_type=chat&container_id={chat_id}`
- Search contacts: `GET /contact/v3/scopes`, `GET /contact/v3/users/{user_id}`

Auto-collected content:
- Group chats: messages sent by them (system messages and stickers filtered)
- Private chats: full conversation with both parties (for context understanding)
- Lark docs and Wikis they created/edited
- Related spreadsheets (if accessible)

After collection, `Read` the output files:
- `knowledge/{slug}/messages.txt` → messages (group + private)
- `knowledge/{slug}/docs.txt` → document content
- `knowledge/{slug}/collection_summary.json` → collection summary

If collection fails, diagnose the error and attempt to fix it. Common issues:
- Group chat: bot not added to the group
- Private chat: user_access_token expired (2-hour TTL; run `--refresh`, or ask the user to re-run `--login` in their own terminal if there is no refresh_token)
- Insufficient permissions: guide user to enable scopes and re-authorize
- Or switch to Option B/C

---

### Option B: DingTalk Auto-Collect

First-time setup. Run `--check` first; if not configured, ask the user to run `--setup` **in their own terminal** (hidden AppSecret input), or to export `DINGTALK_APP_KEY` / `DINGTALK_APP_SECRET`. Never ask for the AppSecret in chat:
```bash
python3 "{distilly_skill_root}/tools/dingtalk_auto_collector.py" --check
python3 "{distilly_skill_root}/tools/dingtalk_auto_collector.py" --setup   # run by the user
```

Then enter the name:
```bash
python3 "{distilly_skill_root}/tools/dingtalk_auto_collector.py" \
  --name "{name}" \
  --output-dir ./knowledge/{slug} \
  --msg-limit 500 \
  --doc-limit 20 \
  --show-browser   # add this flag on first use to complete DingTalk login
```

Collected content:
- DingTalk docs and knowledge bases they created/edited
- Spreadsheets
- Messages (⚠️ DingTalk API doesn't support message history — auto-switches to browser scraping)

After collection, `Read`:
- `knowledge/{slug}/docs.txt`
- `knowledge/{slug}/bitables.txt`
- `knowledge/{slug}/messages.txt`

If message collection fails, prompt user to upload chat screenshots.

---

### Option C: Lark Link

When the user provides a Lark doc/Wiki link, ask which method to use:

```
Lark link detected. Choose read method:

  [1] Browser Method (recommended)
      Reuses your local Chrome login session
      ✅ Works with internal docs requiring permissions
      ✅ No token configuration needed
      ⚠️  Requires Chrome + playwright installed locally

  [2] MCP Method
      Uses a Lark App Token via the official API
      ✅ Stable, no browser dependency
      ✅ Can read messages (needs chat ID)
      ⚠️  Requires App ID / App Secret setup
      ⚠️  Internal docs need admin authorization for the app

Choose [1/2]:
```

**Option 1 (Browser)**:
```bash
python3 "{distilly_skill_root}/tools/feishu_browser.py" \
  --url "{feishu_url}" \
  --target "{name}" \
  --output /tmp/feishu_doc_out.txt
```
First use will open a browser window for login (one-time).

**Option 2 (MCP)**:

First-time setup (shares Lark credentials with Option A). Run `--check` first; if not configured, ask the user to run `--setup` **in their own terminal**:
```bash
python3 "{distilly_skill_root}/tools/feishu_mcp_client.py" --check
python3 "{distilly_skill_root}/tools/feishu_mcp_client.py" --setup   # run by the user
```

Then read directly:
```bash
python3 "{distilly_skill_root}/tools/feishu_mcp_client.py" \
  --url "{feishu_url}" \
  --output /tmp/feishu_doc_out.txt
```

Read messages (needs chat ID, format `oc_xxx`):
```bash
python3 "{distilly_skill_root}/tools/feishu_mcp_client.py" \
  --chat-id "oc_xxx" \
  --target "{name}" \
  --limit 500 \
  --output /tmp/feishu_msg_out.txt
```

Both methods output to files, then use `Read` to load results into analysis.

---

### Option D: Upload Files

- **PDF / Images**: `Read` tool directly
- **Lark message JSON export**:
  ```bash
  python3 "{distilly_skill_root}/tools/feishu_parser.py" --file {path} --target "{name}" --output /tmp/feishu_out.txt
  ```
  Then `Read /tmp/feishu_out.txt`
- **Email files .eml / .mbox**:
  ```bash
  python3 "{distilly_skill_root}/tools/email_parser.py" --file {path} --target "{name}" --output /tmp/email_out.txt
  ```
  Then `Read /tmp/email_out.txt`
- **Markdown / TXT**: `Read` tool directly

---

### Option E: Paste Text

User-pasted content is used directly as text material. No tools needed.
