---
name: sherlock
description: "Runs the Sherlock CLI to find where a username exists across 400+ social sites (--print-found, optional --tor/--site). Use when the user asks which networks a handle is registered on, or to check username availability. Not for email, phone, or domain OSINT, credential stuffing, or acting on discovered accounts."
version: 1.0.1
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [osint, security, username, social-media, reconnaissance]
    category: security
prerequisites:
  commands: [sherlock]
---

# Sherlock OSINT Username Search

Hunt down social media accounts by username across 400+ social networks using the [Sherlock Project](https://github.com/sherlock-project/sherlock).

## When to Use

- User asks to find accounts associated with a specific username
- User wants to check username availability across platforms
- User is conducting OSINT or reconnaissance research
- User asks "where is this username registered?" or similar
- User wants to enumerate a target's social media footprint

## Prerequisites

- **Sherlock CLI installed** — verify before first run (see Procedure step 1)
- **Network access** to query social platforms
- **Optional:** Docker available as fallback (`docker run -it --rm sherlock/sherlock`)
- **Optional:** Tor daemon running if user requests `--tor` anonymity mode

### Installation (if not present)

Pick **one** method and proceed — do not try multiple installation methods:

```powershell
# pipx (recommended — isolated environment)
pipx install sherlock-project

# pip (fallback)
pip install sherlock-project
```

Docker alternative:

```powershell
docker pull sherlock/sherlock
docker run -it --rm sherlock/sherlock <username>
```

Linux packages: available on Debian 13+, Ubuntu 22.10+, Homebrew, Kali, BlackArch.

## Procedure

### 1. Verify Sherlock is Installed

**Before doing anything else**, confirm sherlock is available:

```powershell
sherlock --version
```

If the command fails:
- Offer to install via `pipx install sherlock-project` (recommended) or `pip install sherlock-project`
- **Do NOT** try multiple installation methods — pick one and proceed
- If installation fails, inform the user and stop

### 2. Extract Username

**Extract the username directly from the user's message if clearly stated.** Do not ask for clarification when the username is obvious.

Examples where you should **NOT** use clarify:
- "Find accounts for nasa" → username is `nasa`
- "Search for johndoe123" → username is `johndoe123`
- "Check if alice exists on social media" → username is `alice`
- "Look up user bob on social networks" → username is `bob`

**Only use clarify if:**
- Multiple potential usernames mentioned ("search for alice or bob")
- Ambiguous phrasing ("search for my username" without specifying)
- No username mentioned at all ("do an OSINT search")

When extracting, take the **exact** username as stated — preserve case, numbers, underscores, etc.

### 3. Build Command

**Default command** (use this unless user specifically requests otherwise):

```powershell
sherlock --print-found --no-color "<username>" --timeout 90
```

**Optional flags** (only add if user explicitly requests):
- `--nsfw` — Include NSFW sites (only if user asks)
- `--tor` — Route through Tor (only if user asks for anonymity)
- `--site <name>` — Limit to a specific site (useful for timeout mitigation)
- `--timeout 120` — Increase wait time for slow/blocked sites

**Do NOT ask about options via clarify** — just run the default search. Users can request specific options if needed.

### 4. Execute Search

Run via the terminal tool. The command typically takes 30–120 seconds depending on network conditions and site count.

**Example terminal call:**

```powershell
sherlock --print-found --no-color "target_username" --timeout 90
```

Set a terminal timeout of at least 180 seconds to accommodate slow sites.

### 5. Parse and Present Results

Sherlock outputs found accounts in a simple format. Parse the output and present:

1. **Summary line:** "Found X accounts for username 'Y'"
2. **Categorized links:** Group by platform type if helpful (social, professional, forums, etc.)
3. **Output file location:** Sherlock saves results to `<username>.txt` by default

**Example output:**

```
[+] Instagram: https://instagram.com/username
[+] Twitter: https://twitter.com/username
[+] GitHub: https://github.com/username
```

Present findings as clickable links when possible.

**Example response format:**

> Found 12 accounts for username 'johndoe123':
>
> • https://twitter.com/johndoe123
> • https://github.com/johndoe123
> • https://instagram.com/johndoe123
> • [... additional links]
>
> Results saved to: johndoe123.txt

## Pitfalls

### No Results Found
If Sherlock finds no accounts, this is often correct — the username may not be registered on checked platforms. Suggest:
- Checking spelling/variation
- Trying similar usernames with `?` wildcard: `sherlock "user?name"`
- The user may have privacy settings or deleted accounts

### Timeout Issues
Some sites are slow or block automated requests. Use `--timeout 120` to increase wait time, or `--site` to limit scope to specific platforms.

### Tor Configuration
`--tor` requires Tor daemon running. If user wants anonymity but Tor isn't available, suggest:
- Installing Tor service
- Using `--proxy` with an alternative proxy

### False Positives
Some sites always return "found" due to their response structure. Cross-reference unexpected results with manual checks before reporting as confirmed.

### Rate Limiting
Aggressive searches may trigger rate limits. For bulk username searches, add delays between calls or use `--local` with cached data.

### Ethical Use
This tool is for legitimate OSINT and research purposes only. Remind users:
- Only search usernames they own or have permission to investigate
- Respect platform terms of service
- Do not use for harassment, stalking, or illegal activities
- Consider privacy implications before sharing results

## Verification

After running sherlock, verify:

1. **Output lists found sites with URLs** — lines prefixed with `[+]` indicate matches
2. **`<username>.txt` file created** (default output) if using file output mode
3. **`--print-found` filter working** — output should only contain `[+]` lines for matches, not `[-]` misses

```powershell
# Verify output file exists and contains results
Get-Content "<username>.txt" | Select-String "\[\+\]"

# Count found accounts
(Get-Content "<username>.txt" | Select-String "\[\+\]").Count
```

## Examples

### Basic username search

**User:** "Can you check if the username 'johndoe123' exists on social media?"

**Agent procedure:**
1. Check `sherlock --version` (verify installed)
2. Username provided — proceed directly
3. Run: `sherlock --print-found --no-color "johndoe123" --timeout 90`
4. Parse output and present links

### Search with NSFW sites

**User:** "Search for username 'alice' including NSFW sites"

**Agent procedure:**
1. Check sherlock installed
2. Username + NSFW flag both provided
3. Run: `sherlock --print-found --no-color --nsfw "alice" --timeout 90`
4. Present results

### Wildcard search

**User:** "Search for variations of 'user?name'"

**Agent procedure:**
1. Check sherlock installed
2. Run: `sherlock --print-found --no-color "user?name" --timeout 90`
3. Present all matched variations
