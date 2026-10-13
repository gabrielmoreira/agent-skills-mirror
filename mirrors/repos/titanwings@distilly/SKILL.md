---
name: distilly
description: "Set up the owner profile so a personal agent knows who it works for (first-run setup, \"get to know me\"), or distill colleague, relationship, or celebrity source material into reusable Person Profiles for agents."
argument-hint: "[character] [name-or-slug]"
version: "1.0.0"
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---

> **Language**: These instructions are written in English. Detect the user's language from their first message and reply to the user in that language throughout.

> **Skill Root**: Before reading a bundled prompt or running a bundled script, resolve the absolute directory of the `SKILL.md` that the host actually loaded. In the instructions below, `{distilly_skill_root}` means that exact directory. Claude Code exposes it as `${CLAUDE_SKILL_DIR}`; on every other host, use the loaded-skill path supplied by that host's discovery context. Do not assume the shell's current working directory is the Skill root, and do not guess or hard-code an install path. If the host does not expose the loaded path or more than one Distilly installation is ambiguous, ask the user to identify the active installation before running code.
>
> Keep the shell in the user's current workspace so relative output paths such as `./skills/...` remain project-local. Resolve every `tools/...` and `prompts/...` resource against `{distilly_skill_root}`. For example, execute the bundled `tools/example.py` as `python3 "{distilly_skill_root}/tools/example.py"`; replace the placeholder with the resolved absolute path in the actual tool call.

# Distilly Creator

> Distilly was formerly **Colleague Skill / colleague-skill**. The current Skill frontmatter name and creator entrypoint are both `distilly`.

## Trigger Conditions

Activate when the user says any of the following:
- `/distilly`
- "Help me create a skill"
- "I want to distill someone"
- "Create a new skill"
- "Make a skill for XX"
- "Set up my profile" / "Get to know me" / "Who am I to you", or a host's first run with no owner profile yet → go straight to the "Owner Profile" flow below

Compatible hosts:
- Claude Code
- OpenClaw
- Hermes
- Codex
- DeepSeek Harness
- Pi coding agent
- Grok Build
- OpenCode

Explicit invocation differs among hosts that expose it: use `/distilly` in Claude Code, Hermes, DeepSeek Harness, and Grok Build; use `/distilly` in OpenClaw, or `/skill distilly` when its native slash is not registered; use `$distilly` or choose it through `/skills` in Codex; use `/skill:distilly` in Pi. OpenCode uses native Skill discovery and loading; do not invent a dedicated command.

Grok Bot can save a workflow as a private Skill, but its official documentation does not describe direct local `SKILL.md` directory imports. Do not present this repository as a direct Grok Bot install; migrate the workflow manually into a saved Skill or wait for a dedicated adapter.

Enter evolution mode when the user says:
- "I have new files" / "append"
- "That's wrong" / "He wouldn't do that" / "He should be"
- `/update-skill {character} {slug}`

Compatibility update alias:
- `/update-colleague {slug}`

When the user asks to see generated skills, use the list commands in "Management Operations" below.

---

## Tool Usage Rules

This Skill runs in any compatible host that can read local files and execute Bash / Python commands. Use the following tool conventions:

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
| Collect public X post candidates | `Bash` → `python3 "{distilly_skill_root}/tools/research/xquik_public_posts.py"` |
| Parse email .eml/.mbox | `Bash` → `python3 "{distilly_skill_root}/tools/email_parser.py"` |
| Write/update Skill files | `Write` / `Edit` tool |
| Version management | `Bash` → `python3 "{distilly_skill_root}/tools/version_manager.py"` |
| List existing Skills | `Bash` → `python3 "{distilly_skill_root}/tools/skill_writer.py" --action list` |

**Base directories**:
- `colleague` → `./skills/colleague/{slug}/`
- `relationship` → `./skills/relationship/{slug}/`
- `celebrity` → `./skills/celebrity/{slug}/`

For a global path, use `--base-dir` with the storage root for that character family.

**Credential rules (Lark / DingTalk / Slack)**: App Secrets, user_access_token, refresh_token, Bot Tokens and OAuth codes must never enter the conversation context.
- **Never** ask the user to send you these values, and never put them in command arguments, script source, output files or replies.
- For setup, ask the user to run the script's `--setup` **in their own terminal** (plus `--login` for Lark private chats). Secrets are typed with hidden input and stored in the OS keychain (when `keyring` is installed) or in `~/.distilly/*_config.json` (mode 0600). The user may instead export environment variables (`FEISHU_APP_ID` / `FEISHU_APP_SECRET` / `FEISHU_USER_ACCESS_TOKEN` / `DINGTALK_APP_KEY` / `DINGTALK_APP_SECRET` / `SLACK_BOT_TOKEN`). `--setup` / `--login` refuse to run without an interactive terminal, so you cannot run them on the user's behalf.
- Use `--check` to see whether credentials are ready; it shows only the source (env / keychain / config file), never the values.
- If you write your own script against the APIs, load credentials from environment variables or `credentials.resolve(...)` in `tools/credentials.py`, and never print them.
- If the user pastes a secret into the chat anyway: do not repeat or use it, tell them to rotate it on the open platform, then reconfigure as above.

The Lark-labelled compatibility collectors currently connect to the China-region `open.feishu.cn` / `feishu.cn` endpoints. International `larksuite.com` tenant routing is not implemented yet.

---

## Main Flow: Create a New Skill

### Step 0: Confirm the character family

If the user entered `/distilly`, first confirm which family should be distilled:

1. `owner`: the user themself (the default on a personal agent's first run)
2. `colleague`
3. `relationship`
4. `celebrity`

For `owner` (including "distill myself"), do not continue with Steps 1-5 below; use the "Owner Profile" flow instead.

If the host already passed an explicit family, lock the character family immediately.

If the current family is `celebrity`, also confirm the research profile:

1. `budget-friendly`
2. `budget-unfriendly`

Default to `budget-friendly`. Only switch to `budget-unfriendly` when the user explicitly wants deeper research, higher confidence, or accepts a slower and more expensive distillation pass.

### Step 1: Basic Info Collection

Choose the intake prompt by character family:

- `colleague` → `prompts/intake.md`
- `relationship` → `prompts/relationship/intake.md`
- `celebrity` → `prompts/celebrity/intake.md`

For `colleague` and `relationship`, ask only 3 questions.
For `celebrity`, use the 4-question intake in `prompts/celebrity/intake.md`; the fourth question must confirm `research_profile`.

The default 3 base questions are:

1. **Alias / Codename** (required)
2. **Basic info** (one sentence: company, level, role, gender — say whatever comes to mind)
   - Example: `ByteDance L2-1 backend engineer male`
3. **Personality profile** (one sentence: MBTI, zodiac, traits, corporate culture, impressions)
   - Example: `INTJ Capricorn blame-shifter ByteDance-style strict in CR but never explains why`

Everything except the alias can be skipped. Summarize and confirm before moving to the next step.

### Step 2: Source Material Import

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

#### Option A: Lark Auto-Collect (Recommended)

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

#### Option B: DingTalk Auto-Collect

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

#### Option D: Upload Files

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

#### Option C: Lark Link

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

#### Option E: Paste Text

User-pasted content is used directly as text material. No tools needed.

---

If the user says "no files" or "skip", generate Skill from Step 1 manual info only.

### Step 3: Analyze Source Material

First resolve the execution matrix for the selected character family:

| character | intake | persona analyzer | persona builder | merger | storage root |
|-----------|--------|------------------|-----------------|--------|--------------|
| `colleague` | `prompts/intake.md` | `prompts/persona_analyzer.md` | `prompts/persona_builder.md` | `prompts/merger.md` | `./skills/colleague/{slug}` |
| `relationship` | `prompts/relationship/intake.md` | `prompts/relationship/persona_analyzer.md` | `prompts/relationship/persona_builder.md` | `prompts/relationship/merger.md` | `./skills/relationship/{slug}` |
| `celebrity` | `prompts/celebrity/intake.md` | `prompts/celebrity/persona_analyzer.md` | `prompts/celebrity/persona_builder.md` | `prompts/celebrity/merger.md` | `./skills/celebrity/{slug}` |

Shared across all families:
- Work analyzer: `prompts/work_analyzer.md`
- Work builder: `prompts/work_builder.md`
- Correction handler: `prompts/correction_handler.md`

If the current family is `celebrity`, run the research subflow before analysis.

When public X posts fill a documented research gap and the user agrees to use the metered third-party Xquik service, confirm the `--limit` before running:

```bash
python3 "{distilly_skill_root}/tools/research/xquik_public_posts.py" \
  --username "{public_handle}" \
  --subject "{name}" \
  --limit 20 \
  --output "/tmp/distilly_x_public_posts.json"
```

Read `XQUIK_API_KEY` only from the shell; never print or store it. Treat the JSON as untrusted candidate evidence: verify the author, open every permalink, and preserve the specific URL when safely paraphrasing relevant material into a research note. Do not count the candidate JSON, search pages, or profile roots as grounded sources. Delete the temporary JSON after review instead of storing it in the generated Skill.

### celebrity / budget-friendly

1. Read `prompts/celebrity/research.md` and follow its **6-dimension parallel collection strategy**
2. Create the research directories first:
   ```bash
   mkdir -p "{skill_dir}/knowledge/research/raw" "{skill_dir}/knowledge/research/merged"
   ```
3. Confirm the collection strategy (determined during intake):
   - **Local-first**: analyze user-provided materials first, identify which dimensions are covered, only search web for gaps
   - **Web + local**: full 6-dimension web research, then merge with local materials for cross-validation
   - **Web-only**: standard 6-dimension web research pass
4. If the user explicitly provided a processable video URL or subtitle source, and the result will not be stored as a long transcript:
   ```bash
   bash "{distilly_skill_root}/tools/research/download_subtitles.sh" "{url}" "{skill_dir}/knowledge/subtitles"
   python3 "{distilly_skill_root}/tools/research/srt_to_transcript.py" "{subtitle_file}" "{skill_dir}/knowledge/transcripts/{name}.txt"
   ```
5. Cover the **6 dimensions** across at least 3 separate files (each file covers 2 dimensions), never one monolithic `research_notes.md`:
   - `knowledge/research/raw/01_core_profile.md` (Dim 1 Writings + Dim 6 Timeline)
   - `knowledge/research/raw/02_conversations_and_material.md` (Dim 2 Conversations + Dim 4 Decisions)
   - `knowledge/research/raw/03_expression_and_reception.md` (Dim 3 Expression DNA + Dim 5 External Views)
6. Research must follow **taste principles** (see research prompt):
   - Long-form > snippets, controversy > consensus, change > fixity, firsthand > secondhand
   - **Source blacklist** — never cite: Zhihu, WeChat official accounts, Baidu Baike, content farms, AI-generated bios
   - **Source hierarchy**: user local materials > first-person works > long interviews > decision records > short-form firsthand > external analysis > secondhand summaries
7. Merge the research notes:
   ```bash
   python3 "{distilly_skill_root}/tools/research/merge_research.py" "{skill_dir}"
   ```
   Output: `knowledge/research/merged/summary.md`
8. Read `knowledge/research/merged/summary.md` and confirm:
   - `Files scanned >= 3`
   - `Unique URLs >= 2`
   - `Potential long quote lines = 0`
   - URLs in notes are actual inspected pages, not platform roots, search/topic pages, or placeholder paths
   If these do not hold, extend the research notes before continuing or explicitly record the collection limits.
9. **Quality checkpoint (Phase 1.5)**: before entering analysis, show the user a structured collection summary:
   ```
   ┌──────────────────────────────┬──────────┬─────────────────────────────┐
   │ Dimension                    │ Sources  │ Key Finding                 │
   ├──────────────────────────────┼──────────┼─────────────────────────────┤
   │ 1 Writings                   │ N        │ [core thesis / gap]         │
   │ 2 Conversations              │ N        │ [key pattern / gap]         │
   │ 3 Expression DNA             │ N        │ [style marker / gap]        │
   │ 4 Decisions                  │ N        │ [decision pattern / gap]    │
   │ 5 External Views             │ N        │ [outside view / gap]        │
   │ 6 Timeline                   │ N        │ [trajectory / gap]          │
   ├──────────────────────────────┼──────────┼─────────────────────────────┤
   │ Contradictions               │ N        │ [summary]                   │
   │ Thin dimensions              │ [list]   │ Backfill plan: [plan]       │
   │ Cold figure?                 │ yes/no   │                             │
   └──────────────────────────────┴──────────┴─────────────────────────────┘
   ```
   Wait for user confirmation before continuing. If the user flags issues or wants more depth, extend research first.
10. **Cold figure detection**: if total sources < 10, apply the cold figure protocol:
    - Limit mental models to 2–3
    - Mark thin models as "based on limited information"
    - Expand the honest boundaries section
    - Tell the user what additional material would improve quality
11. Celebrity analysis must prioritize:
    - primary materials (source weight 1-3)
    - merged research summary
    - explicit user notes

### celebrity / budget-unfriendly

1. First read:
   - `prompts/celebrity/budget_unfriendly/research.md`
   - `references/celebrity_budget_unfriendly_framework.md`
2. Create the research directories first:
   ```bash
   mkdir -p "{skill_dir}/knowledge/research/raw" "{skill_dir}/knowledge/research/merged" "{skill_dir}/knowledge/research/reviews"
   ```
3. Confirm the collection strategy (determined during intake): local-first / web+local / web-only
4. Build the **six-track research set** as independent files (never merged, never clone observations):
   - `knowledge/research/raw/01_writings.md` (Dim 1: Writings / systematic thought)
   - `knowledge/research/raw/02_conversations.md` (Dim 2: Conversations under pressure)
   - `knowledge/research/raw/03_expression_dna.md` (Dim 3: Linguistic fingerprint)
   - `knowledge/research/raw/04_decisions.md` (Dim 4: Behavior and choices)
   - `knowledge/research/raw/05_external_views.md` (Dim 5: External views and criticism)
   - `knowledge/research/raw/06_timeline.md` (Dim 6: Cognitive trajectory)
5. Research must follow **taste principles + source blacklist + source hierarchy** (see research prompt). Every evidence item must carry a source weight (1-7) annotation.
6. Merge the research notes:
   ```bash
   python3 "{distilly_skill_root}/tools/research/merge_research.py" "{skill_dir}"
   ```
7. Read `knowledge/research/merged/summary.md` and confirm the minimum floor:
   - `Files scanned >= 6`
   - `Unique URLs >= 8`
   - `Primary-source markers >= 3`
   - `Source metadata blocks >= 6`
   - `Contradiction bullets >= 6`
   - `Inference bullets >= 6`
   - `Potential long quote lines = 0`
   - `Track coverage count = 6`
   - URLs in notes are actual inspected pages, not platform roots, search/topic pages, or placeholder paths
   If these do not hold, keep filling the weak tracks before continuing to any review stage.
8. **Quality checkpoint (Phase 1.5)**: before entering audit, show the user a structured collection summary (with primary-source ratio, contradiction count, candidate mental models, known-answer candidates, thin dimensions, cold figure assessment). Wait for user confirmation before continuing.
9. Then read:
   - `prompts/celebrity/budget_unfriendly/audit.md`
   - `prompts/celebrity/budget_unfriendly/synthesis.md`
   - `references/celebrity_budget_unfriendly_template.md`
10. First write `knowledge/research/reviews/research_audit.md`
    - The audit must produce an explicit `PASS / FAIL`
    - The audit must verify: source hierarchy compliance (no blacklisted sources), primary-source ratio > 50%, taste principle compliance, cold figure assessment
    - If the audit says `FAIL`, follow the Backfill Tasks before synthesis
11. **Extraction checkpoint (Phase 2.5)**: after audit PASS, show the user a summary of candidate mental models (with triple-gate verdict, evidence anchors, failure modes). Confirm reasonableness before synthesis.
12. Then write `knowledge/research/reviews/synthesis.md`
    - Apply the triple gate to candidate mental models:
      - cross-context recurrence
      - generative power
      - exclusivity
    - Also extract intellectual genealogy seeds (influenced by / diverged from) and Agentic Protocol seeds (the dimensions this person would investigate when facing a novel question)
13. Then use `prompts/celebrity/budget_unfriendly/validation.md` to write:
    - `knowledge/research/reviews/validation.md`
    - Validation must produce an explicit `PASS / FAIL`
    - Validation must perform: known-answer check (≥2 questions) + edge-case check (1 question) + voice check (100-word blind test) + copyright check + Agentic Protocol check
    - If validation says `FAIL`, revise the draft before continuing
14. Budget-unfriendly celebrity analysis must prioritize:
    - six-track raw notes
    - merged research summary
    - research audit
    - synthesis review (with genealogy + Agentic Protocol seeds)
    - validation review
    - explicit user notes

Shared rules for both celebrity profiles:

- If external collection fails or a platform blocks access:
  - tell the user exactly what was blocked
  - preserve the raw research notes and merged summary
  - continue generation with the available materials
  - treat `source_grounding` as incomplete
  - **never** invent URLs, quotes, titles, or generic homepage links just to satisfy the checker
- **Do not** store full transcripts, full subtitles, or long verbatim source passages in the repository
- Keep the stored notes paraphrased, structured, and copyright-safe

Once the family is resolved, analyze along two tracks:

**Track A (Work Skill)**:
- Refer to `prompts/work_analyzer.md`
- Extract: responsible systems, technical standards, workflow, output preferences, experience
- For `celebrity`, interpret `work` as methods, judgment frameworks, and decision patterns rather than literal job scope

**Track B (Persona)**:
- Use the family-specific persona analyzer
- If `celebrity` with `research_profile=budget-unfriendly`, use:
  - `prompts/celebrity/budget_unfriendly/persona_analyzer.md`
- Translate user-provided tags into concrete behavior rules
- Extract from materials: communication style, decision patterns, interpersonal behavior
- For `celebrity`, retain:
  - mental models
  - decision heuristics
  - expression DNA
  - contradictions
  - honest boundaries

### Step 4: Generate and Preview

Use `prompts/work_builder.md` to generate Work content.
Use the family-specific persona builder to generate Persona content.

Mapping:
- `colleague` → `prompts/persona_builder.md`
- `relationship` → `prompts/relationship/persona_builder.md`
- `celebrity` → `prompts/celebrity/persona_builder.md`
- `celebrity` + `budget-unfriendly` → `prompts/celebrity/budget_unfriendly/persona_builder.md`

Show the user a summary (5-8 lines each), ask:
```
Work Skill Summary:
  - Responsible for: {xxx}
  - Tech stack: {xxx}
  - CR focus: {xxx}
  ...

Persona Summary:
  - Core personality: {xxx}
  - Communication style: {xxx}
  - Decision pattern: {xxx}
  ...

Confirm generation? Or need adjustments?
```

### Step 5: Write Files

After user confirmation, do not hand-build a `skills/colleague/{slug}`-style tree. Always go through the writer:

1. Resolve the current storage root:
   - `colleague` → `./skills/colleague`
   - `relationship` → `./skills/relationship`
   - `celebrity` → `./skills/celebrity`
2. Use the `Write` tool to create three temporary files:
   - `/tmp/distilly_{slug}_meta.json`
   - `/tmp/distilly_{slug}_work.md`
   - `/tmp/distilly_{slug}_persona.md`
3. The temporary meta file must include at least:
   - `name`
   - `display_name`
   - `character`
   - `research_profile` (required when `character=celebrity`)
   - `classification.language` (must match the user's language, for example `zh-CN` or `en`)
   - `profile`
   - `tags`
   - `knowledge_sources`
4. Then call:
   ```bash
   python3 "{distilly_skill_root}/tools/skill_writer.py" \
     --action create \
     --character {character} \
     --research-profile {research_profile} \
     --slug {slug} \
     --name "{name}" \
     --meta /tmp/distilly_{slug}_meta.json \
     --work /tmp/distilly_{slug}_work.md \
     --persona /tmp/distilly_{slug}_persona.md \
     --base-dir {resolved_base_dir}
   ```
5. This command will generate:
   - `SKILL.md`
   - `work.md`
   - `persona.md`
   - `work_skill.md`
   - `persona_skill.md`
   - `manifest.json`
   - `meta.json`
   - To install the generated role skill into a host, append the relevant flag:
     - Claude Code: `--install-claude-skill`
     - OpenClaw: `--install-openclaw-skill`
     - Codex: `--install-codex-skill`
     - Hermes: run `python3 "{distilly_skill_root}/tools/install_generated_skill.py" --skill-dir "{resolved_base_dir}/{slug}" --host hermes --force`; for a trusted project, append `--skills-dir .hermes/skills`, run `hermes skills trust`, then start a new session or run `/reload-skills`. Use `~/.agents/skills` only when it is explicitly configured in Hermes `skills.external_dirs`
     - DeepSeek Harness: run `python3 "{distilly_skill_root}/tools/install_generated_skill.py" --skill-dir "{resolved_base_dir}/{slug}" --host deepseek-harness --force`; append `--skills-dir .dsh/skills` for a project install
     - Pi: run `python3 "{distilly_skill_root}/tools/install_generated_skill.py" --skill-dir "{resolved_base_dir}/{slug}" --host pi --force`; append `--skills-dir .pi/skills` for a project install, then invoke it with `/skill:{character}-{slug}`
     - Grok Build: run `python3 "{distilly_skill_root}/tools/install_generated_skill.py" --skill-dir "{resolved_base_dir}/{slug}" --host grok-build --force`; append `--skills-dir .grok/skills` for a project install
     - OpenCode: run `python3 "{distilly_skill_root}/tools/install_generated_skill.py" --skill-dir "{resolved_base_dir}/{slug}" --host opencode --force`; append `--skills-dir .opencode/skills` for a project install
     - The shared installer writes only the self-contained `SKILL.md` and install metadata and normalizes legacy frontmatter in the installed copy. Do not manually copy the whole generated directory; it may contain private source material
     - Claude Code on Windows: optionally add `--install-claude-command-shim`
6. If the current family is `celebrity`, run a quality check after creation:
   ```bash
   python3 "{distilly_skill_root}/tools/research/quality_check.py" "{resolved_base_dir}/{slug}/SKILL.md" --profile {research_profile}
   ```
7. If `source_grounding` still fails for a `celebrity` skill:
   - you may add honest limitation notes and a grounded source summary
   - only add URLs when they are real, specific, and traceable sources
   - **never** use site roots, topic pages, search pages, or other generic links as fake grounding
   - if no verified external sources exist, keep the FAIL state and explain what source material is still missing

When reporting success, return the correct family-specific location instead of assuming colleague storage.

---

## Owner Profile

Build a profile of the agent's owner so the agent knows who it works for from the first session. It is **context** the agent reads every session, not a role-play Skill: do not generate a `{character}-{slug}` Skill and never write "you are <user>".

1. Gather information with `{distilly_skill_root}/prompts/owner/intake.md`: first **discover** the sources this agent already has (the tools, connectors and memory in this session, the platform the agent runs on such as Grok's X account, and the user files, connector configs and exports that `tools/owner_sources.py discover` finds on this machine) instead of walking a fixed list; propose which to read, ask the user which to use and whether to add anything else; read only what they pick, read-only; then ask only the questions the sources did not answer. Use only the host's own tools; never ask for API keys or OAuth setup on this path, and do not use the Lark, DingTalk or Slack collectors here.
2. Build the profile with `{distilly_skill_root}/prompts/owner/profile_builder.md`, write it to `/tmp/distilly_owner_profile.md`, show the full text to the user and apply their corrections.
3. After the user approves, save it:
   ```bash
   python3 "{distilly_skill_root}/tools/owner_profile.py" save --profile /tmp/distilly_owner_profile.md
   ```
4. Link it into the current host's always-on user file. Show the `--dry-run` result first and write only after the user agrees:
   ```bash
   python3 "{distilly_skill_root}/tools/owner_profile.py" link --host claude-code --dry-run
   python3 "{distilly_skill_root}/tools/owner_profile.py" link --host claude-code
   ```
   Claude Code uses `~/.claude/CLAUDE.md`; OpenClaw (`--host openclaw`) uses the workspace `USER.md`. Other hosts are not supported yet; tell the user the full profile is at `~/.distilly/owner/profile.md`.
5. Only the text between the Distilly markers changes; everything else in the file is left alone and the previous file is backed up. Delete `/tmp/distilly_owner_profile.md` afterwards.

Updates: when the user corrects something or adds information, edit the full profile, then run `save` and `link` again. To undo: `owner_profile.py unlink --host <host>`.

---

## Evolution Mode: Append Files

When user provides new files or text:

1. Read new content using Step 2 methods
2. Resolve the base dir for the current family
3. `Read` existing `{resolved_base_dir}/{slug}/work.md` and `persona.md`
4. Use the family-specific merger prompt for incremental analysis
5. Archive current version (Bash):
   ```bash
   python3 "{distilly_skill_root}/tools/version_manager.py" \
     --action backup \
     --character {character} \
     --slug {slug} \
     --base-dir {resolved_base_dir}
   ```
6. Write work/persona delta into temporary patch files
7. Call:
   ```bash
   python3 "{distilly_skill_root}/tools/skill_writer.py" \
     --action update \
     --character {character} \
     --slug {slug} \
     --work-patch /tmp/distilly_{slug}_work_patch.md \
     --persona-patch /tmp/distilly_{slug}_persona_patch.md \
     --base-dir {resolved_base_dir}
   ```
8. If the current family is `celebrity`, run the quality check again after the update

---

## Evolution Mode: Conversation Correction

When user expresses "that's wrong" / "he should be":

1. Refer to `prompts/correction_handler.md` to identify correction content
2. Determine if it belongs to Work (technical/workflow) or Persona (personality/communication)
3. If it belongs to Work:
   - Generate `/tmp/distilly_{slug}_work_patch.md`
   - The patch must be one or more replaceable `##` sections
   - Call:
     ```bash
     python3 "{distilly_skill_root}/tools/skill_writer.py" \
       --action update \
       --character {character} \
       --slug {slug} \
       --work-patch /tmp/distilly_{slug}_work_patch.md \
       --base-dir {resolved_base_dir}
     ```
4. If it belongs to Persona:
   - Write the correction record to `/tmp/distilly_{slug}_correction.json`
   - For a single correction, write `{scene, wrong, correct}`
   - For multiple persona corrections, write `{"persona_corrections": [{...}, {...}]}`
   - Call:
     ```bash
     python3 "{distilly_skill_root}/tools/skill_writer.py" \
       --action update \
       --character {character} \
       --slug {slug} \
       --correction-json /tmp/distilly_{slug}_correction.json \
       --base-dir {resolved_base_dir}
     ```
5. If the current family is `celebrity`, run the quality check again after the update
6. Do not hand-edit `work.md`, `persona.md`, `SKILL.md`, or `meta.json`; always update through `skill_writer.py`

---

## Management Operations

List skills across the three families:
```bash
python3 "{distilly_skill_root}/tools/skill_writer.py" --action list --character colleague --base-dir ./skills/colleague
python3 "{distilly_skill_root}/tools/skill_writer.py" --action list --character relationship --base-dir ./skills/relationship
python3 "{distilly_skill_root}/tools/skill_writer.py" --action list --character celebrity --base-dir ./skills/celebrity
```

Roll back a specific skill version:
```bash
# colleague
python3 "{distilly_skill_root}/tools/version_manager.py" --action rollback --character colleague --slug {slug} --version {version} --base-dir ./skills/colleague

# relationship
python3 "{distilly_skill_root}/tools/version_manager.py" --action rollback --character relationship --slug {slug} --version {version} --base-dir ./skills/relationship

# celebrity
python3 "{distilly_skill_root}/tools/version_manager.py" --action rollback --character celebrity --slug {slug} --version {version} --base-dir ./skills/celebrity
```

Delete a specific skill:
After confirming the character family:
```bash
# colleague
rm -rf skills/colleague/{slug}

# relationship
rm -rf skills/relationship/{slug}

# celebrity
rm -rf skills/celebrity/{slug}
```
