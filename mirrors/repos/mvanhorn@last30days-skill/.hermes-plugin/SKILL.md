---
name: last30days
version: "3.0.0"
description: "Multi-query social search with intelligent planning. Research any topic across Reddit, X, YouTube, TikTok, Instagram, Hacker News, Polymarket, and the web."
argument-hint: 'last30days AI video tools, last30days best noise cancelling headphones'
allowed-tools: Bash, Read, Write, AskUserQuestion, WebSearch
homepage: https://github.com/mvanhorn/last30days-skill
repository: https://github.com/mvanhorn/last30days-skill
author: mvanhorn
license: MIT
user-invocable: true
metadata:
  hermes:
    emoji: "📰"
    tags:
      - research
      - deep-research
      - reddit
      - x
      - twitter
      - youtube
      - tiktok
      - instagram
      - hackernews
      - polymarket
      - trends
      - recency
      - news
      - citations
      - multi-source
      - social-media
      - analysis
      - web-search
    requires:
      env:
        - SCRAPECREATORS_API_KEY
      optionalEnv:
        - OPENAI_API_KEY
        - XAI_API_KEY
        - OPENROUTER_API_KEY
        - PARALLEL_API_KEY
        - BRAVE_API_KEY
        - APIFY_API_TOKEN
        - AUTH_TOKEN
        - CT0
        - BSKY_HANDLE
        - BSKY_APP_PASSWORD
        - TRUTHSOCIAL_TOKEN
      bins:
        - node
        - python3
    primaryEnv: SCRAPECREATORS_API_KEY
    files:
      - "scripts/*"
    homepage: https://github.com/mvanhorn/last30days-skill
---

# last30days v3.0.0: Research Any Topic from the Last 30 Days

> **Permissions overview:** Reads public web/platform data and optionally saves research briefings to `~/Documents/Last30Days/`. X/Twitter search uses optional user-provided tokens (AUTH_TOKEN/CT0 env vars). Bluesky search uses optional app password (BSKY_HANDLE/BSKY_APP_PASSWORD env vars - create at bsky.app/settings/app-passwords). All credential usage and data writes are documented in the [Security & Permissions](#security--permissions) section.

Research ANY topic across Reddit, X, YouTube, and other sources. Surface what people are actually discussing, recommending, betting on, and debating right now.

## Runtime Preflight

Before running any `last30days.py` command in this skill, resolve a Python 3.12+ interpreter once and keep it in `LAST30DAYS_PYTHON`:

```bash
for py in python3.14 python3.13 python3.12 python3; do
  command -v "$py" >/dev/null 2>&1 || continue
  "$py" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)' || continue
  LAST30DAYS_PYTHON="$py"
  break
done

if [ -z "${LAST30DAYS_PYTHON:-}" ]; then
  echo "ERROR: last30days v3 requires Python 3.12+. Install python3.12 or python3.13 and rerun." >&2
  exit 1
fi
```

## Step 0: First-Run Setup Wizard

**CRITICAL: ALWAYS execute Step 0 BEFORE Step 1, even if the user provided a topic.** If the user typed `last30days Mercer Island`, you MUST check for FIRST_RUN and present the wizard BEFORE running research. The topic "Mercer Island" is preserved — research runs immediately after the wizard completes. Do NOT skip the wizard because a topic was provided. The wizard takes 10 seconds and only runs once ever.

To detect first run: check if `~/.config/last30days/.env` exists. If it does NOT exist, this is a first run. **Do NOT run any Bash commands or show any command output to detect this — just check the file existence silently.** If the file exists and contains `SETUP_COMPLETE=true`, skip this section **silently** and proceed to Step 1. **Do NOT say "Setup is complete" or any other status message — just move on.** The user doesn't need to be told setup is done every time they run the skill.

**When first run is detected, detect your platform first:**

**If you do NOT have WebSearch capability (raw CLI):** Run the terminal-only setup flow below.
**If you DO have WebSearch (Hermes):** Run the standard setup flow below.

---

### Terminal-Only / Non-WebSearch Setup Flow

Run environment detection first:
```bash
"${LAST30DAYS_PYTHON}" "${SKILL_ROOT}/scripts/last30days.py" setup --terminal
```

Read the JSON output. It tells you what's already configured. Display a status summary:

```
👋 Welcome to last30days!

Detected:
{✅ or ❌} yt-dlp (YouTube search)
{✅ or ❌} X/Twitter ({method} configured)
{✅ or ❌} ScrapeCreators (TikTok, Instagram, Reddit backup)
{✅ or ❌} Web search ({backend} configured)
```

Then for each missing item, offer setup in priority order:

1. **ScrapeCreators** (if not configured): "ScrapeCreators adds TikTok and Instagram search (plus a Reddit backup if public Reddit gets rate-limited). 10,000 free calls, no credit card. (No referrals, no kickbacks - we don't get a cut.)"
   - Option A: "ScrapeCreators via GitHub (recommended)" — Check if `gh` CLI was detected in the environment detection output above. If gh IS detected: description should say "Registers directly via GitHub CLI in ~2 seconds - no browser needed". Before running the command, display: "Registering via GitHub CLI..." If gh is NOT detected: description should say "Copies a one-time code to your clipboard and opens GitHub to authorize". Then run `"${LAST30DAYS_PYTHON}" "${SKILL_ROOT}/scripts/last30days.py" setup --github`, parse JSON output. Tries PAT first (if `gh` is installed), falls back to device flow which copies a one-time code to your clipboard and opens your browser. If `status` is `success`, write `SCRAPECREATORS_API_KEY=*** to .env.
   - Option B: "I have a key" — accept paste, write to .env
   - Option C: "Skip for now"

2. **X/Twitter** (if not configured): "X search finds tweets and conversations. To unlock X: add FROM_BROWSER=auto (reads browser cookies, free), XAI_API_KEY (no browser access, api.x.ai), or AUTH_TOKEN+CT0 (manual cookies)."
   - Option A: "I have an xAI API key" (recommended for servers — persistent, no expiry). Write XAI_API_KEY to .env.
   - Option B: "I have AUTH_TOKEN + CT0 from my browser" — accept both, write to .env
   - Option C: "Skip for now"

3. **YouTube** (if yt-dlp not found): "YouTube search needs yt-dlp. Run: `pip install yt-dlp`"

4. **Web search** (if no Brave/Exa/Serper key): "A web search key enables smarter results. Brave Search is free for 2,000 queries/month at brave.com/search/api"

After setup, write `SETUP_COMPLETE=true` to .env and proceed to research.

**Skip to "END OF FIRST-RUN WIZARD" below after completing the terminal-only flow.**

---

### Hermes Setup Flow (Standard)

**You MUST follow these steps IN ORDER. Do NOT skip ahead to the topic picker or research. The sequence is: (1) welcome text -> (2) setup modal -> (3) run setup if chosen -> (4) optional ScrapeCreators modal -> (5) topic picker. You MUST start at step 1.**

**Step 1: Display the following welcome text ONCE as a normal message (not blockquoted). Then IMMEDIATELY call AskUserQuestion - do NOT repeat any of the welcome text inside the AskUserQuestion call.**

Welcome to last30days!

I research any topic across Reddit, X, YouTube, and other sources - synthesizing what people are actually saying right now.

Auto setup gives you 5 core sources for free in 30 seconds:
- X/Twitter - reads your x.com browser cookies to authenticate (not saved to disk). Chrome on macOS will prompt for Keychain access.
- Reddit with comments - public JSON, no API key needed
- YouTube search + transcripts - installs yt-dlp (open source, 190K+ GitHub stars)
- Hacker News + Polymarket + GitHub (if `gh` CLI installed) - always on, zero config

Want TikTok and Instagram too? ScrapeCreators adds those (10,000 free calls, scrapecreators.com). No kickbacks, no affiliation.

**Then call AskUserQuestion with ONLY this question and these options - no additional text:**

Question: "How would you like to set up?"
Options:
- "Auto setup (~30 seconds) - scans browser cookies for X + installs yt-dlp for YouTube"
- "Manual setup - show me what to configure"
- "Skip for now - Reddit (with comments), HN, Polymarket, GitHub (if gh installed), Web"

**If the user picks 1 (Auto setup):**

**Before running the setup command, get cookie consent:**

Check if `BROWSER_CONSENT=true` already exists in `~/.config/last30days/.env`. If it does, skip the consent prompt and run setup directly.

If `BROWSER_CONSENT=true` is NOT present, **call AskUserQuestion:**
Question: "Auto setup will scan your browser for x.com cookies to authenticate X search. Cookies are read live, not saved to disk. Chrome on macOS will prompt for Keychain access. OK to proceed?"
Options:
- "Yes, scan my cookies for X" - Run setup as normal. Append `BROWSER_CONSENT=true` to .env after setup completes.
- "Skip X, just set up YouTube" - Run setup with YouTube only (install yt-dlp). Do not scan cookies.
- "I have an xAI API key instead" - Ask them to paste it, write XAI_API_KEY to .env. Then install yt-dlp.

Run the setup subcommand:
```bash
cd {SKILL_DIR} && "${LAST30DAYS_PYTHON}" scripts/last30days.py setup
```
Show the user the results (what cookies were found, whether yt-dlp was installed).

**Then show the optional ScrapeCreators offer (plain text, then modal):**

Want TikTok and Instagram too? ScrapeCreators adds those platforms - 10,000 free calls, no credit card. It also serves as a Reddit backup if public Reddit ever gets rate-limited.

**Before showing the ScrapeCreators modal, check for `gh` CLI:** Run `which gh` via Bash silently. Store the result as gh_available (true if found, false if not).

**Call AskUserQuestion:**
Question: "Want to add TikTok, Instagram, and Reddit backup via ScrapeCreators? (We don't get a cut.)"
Options:
- "ScrapeCreators via GitHub (fastest, recommended)" - If gh_available: description should say "Registers directly via GitHub CLI in ~2 seconds - no browser needed". If NOT gh_available: description should say "Copies a one-time code to your clipboard and opens GitHub to authorize". After the user selects this option: If gh_available, display "Registering via GitHub CLI..." before running the command. If NOT gh_available, display "I'll copy a one-time code to your clipboard and open GitHub. When GitHub asks for a device code, just paste (Cmd+V on Mac, Ctrl+V on Windows/Linux)." Then run `cd {SKILL_DIR} && "${LAST30DAYS_PYTHON}" scripts/last30days.py setup --github` via Bash with a 5-minute timeout. This tries PAT auth first (if `gh` CLI is installed, zero browser needed), then falls back to GitHub device flow which copies a one-time code to your clipboard and opens GitHub in your browser. Parse the JSON stdout. If `status` is `success`, write `SCRAPECREATORS_API_KEY=*** to `~/.config/last30days/.env`. If `method` is `pat`, show: "You're in! Registered via GitHub CLI - zero browser needed. 10,000 free calls. TikTok, Instagram, and Reddit backup are now active." If `method` is `device` and `clipboard_ok` is true, show: "You're in! (The authorization code was copied to your clipboard automatically.) 10,000 free calls. TikTok, Instagram, and Reddit backup are now active." If `method` is `device` and `clipboard_ok` is false, show: "You're in! 10,000 free calls. TikTok, Instagram, and Reddit backup are now active." If `status` is `timeout` or `error`, show: "GitHub auth didn't complete. No worries - you can sign up at scrapecreators.com instead or try again later." Then offer the web signup option.
- "Open scrapecreators.com (Google sign-in)" - run `open https://scrapecreators.com` via Bash to open in the user's browser. Then ask them to paste the API key they get. When they paste it, write SCRAPECREATORS_API_KEY=*** to ~/.config/last30days/.env
- "I have a key" - accept the key, write to .env
- "Skip for now" - proceed without ScrapeCreators

**After SC key is saved (not if skipped), show the TikTok/Instagram opt-in:**

**Call AskUserQuestion:**
Question: "Enable TikTok and Instagram search?"
Options:
- "Yes, enable TikTok + Instagram" - Write `TIKTOK_ENABLED=true` and `INSTAGRAM_ENABLED=true` to .env. Then show: "TikTok and Instagram are now enabled. You can disable them later by editing ~/.config/last30days/.env."
- "No, skip for now" - proceed without enabling

**After setup completes, write `SETUP_COMPLETE=true` to .env.**

---

## END OF FIRST-RUN WIZARD

Proceed to Step 1.

---

## Step 1: Parse Topic

The user invoked: `last30days {QUERY}`

Extract the topic. If the query is empty or ambiguous, ask for clarification.

## Step 2: Execute Research

Run the research engine:

```bash
cd {SKILL_DIR} && "${LAST30DAYS_PYTHON}" scripts/last30days.py "{TOPIC}" --emit=compact --lookback-days=30
```

Optional flags based on user request:
- `--search=reddit,youtube,hackernews` - Specific sources only
- `--days=7` - Shorter time range
- `--deep` - Higher recall mode
- `--save` - Save to ~/Documents/Last30Days/

## Step 3: Display Results

Show the research output to the user. The compact output includes:
- Executive summary
- Ranked evidence clusters with scores
- Source statistics (upvotes, views, engagement)
- Citations with URLs
- Confidence levels and uncertainty notes

## Security & Permissions

**What this skill does:**
- Sends search queries to ScrapeCreators API (`api.scrapecreators.com`) for TikTok and Instagram search, and as a Reddit backup when public Reddit is unavailable (requires SCRAPECREATORS_API_KEY)
- Sends search queries to OpenAI's Responses API (`api.openai.com`) for Reddit discovery (fallback if no SCRAPECREATORS_API_KEY)
- Sends search queries to Twitter's GraphQL API (via optional user-provided AUTH_TOKEN/CT0 env vars — no browser session access) or xAI's API (`api.x.ai`) for X search
- Sends search queries to Algolia HN Search API (`hn.algolia.com`) for Hacker News story and comment discovery (free, no auth)
- Sends search queries to Polymarket Gamma API (`gamma-api.polymarket.com`) for prediction market discovery (free, no auth)
- Runs `yt-dlp` locally for YouTube search and transcript extraction (no API key, public data)
- Sends search queries to ScrapeCreators API (`api.scrapecreators.com`) for TikTok and Instagram search, transcript/caption extraction (PAYG after 10,000 free API calls)
- Optionally sends search queries to Brave Search API, Parallel AI API, or OpenRouter API for web search
- Fetches public Reddit thread data from `reddit.com` for engagement metrics
- Stores research findings in local SQLite database (watchlist mode only)
- Saves research briefings as .md files to ~/Documents/Last30Days/

**What this skill does NOT do:**
- Does not post, like, or modify content on any platform
- Does not access your Reddit, X, or YouTube accounts
- Does not share API keys between providers (OpenAI key only goes to api.openai.com, etc.)
- Does not log, cache, or write API keys to output files
- Does not send data to any endpoint not listed above
- Hacker News and Polymarket sources are always available (no API key, no binary dependency)
- TikTok and Instagram sources require SCRAPECREATORS_API_KEY (10,000 free API calls, then PAYG). Reddit uses ScrapeCreators only as a backup when public Reddit is unavailable.
- Can be invoked autonomously by agents via the Skill tool (runs inline, not forked); pass `--agent` for non-interactive report output

**Bundled scripts:** `scripts/last30days.py` (main research engine), `scripts/lib/` (search, enrichment, rendering modules), `scripts/lib/vendor/bird-search/` (vendored X search client, MIT licensed)

Review scripts before first use to verify behavior.
