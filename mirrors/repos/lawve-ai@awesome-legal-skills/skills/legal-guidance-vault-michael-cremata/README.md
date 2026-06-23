# What Is This?

The Legal Vault is a skill for Claude that gives it a long-term memory for the legal guidance you give — wherever it happens. After any meeting, Slack thread, email, or Google Doc, you can ask Claude to archive it. Claude extracts the legally relevant content, produces a short structured summary, and saves it. You review and confirm before anything is stored.

From that point on, you can ask Claude to find that guidance by topic, issue, product, who was involved, or roughly when it happened — even a year later.

## What You Can Archive

- Meetings — Claude pulls notes from Granola (your AI meeting recorder) and extracts the legal substance.
- Slack threads — Paste a thread URL into Claude, or react to any message with :file-cabinet: and Claude will find it automatically.
- Email — Paste a Gmail link or describe the email ("the Kirkland memo about biometric consent") and Claude finds and extracts it. Works best for outside counsel memos and opinions.
- Google Docs — Paste a doc URL. Claude asks whether to archive the whole doc or just the legally relevant sections.

## What You Need Before You Start

1. Cowork

The Claude desktop app. It's what runs the skill.

2. Granola (for meeting archiving)

Granola is a free Mac app that records and summarizes your meetings. It integrates with Google Calendar and captures audio from your computer — no bot joins your calls. Download at granola.so. Sign in with your work Google account.

3. Connected accounts (for Slack, Gmail, and Drive)

Slack, Gmail, and Google Drive must each be connected to Cowork before Claude can access them. Here's how to connect each one:

1. Open Claude Desktop on your Mac.
2. Click the plug icon (⚡) in the bottom-left corner to open Integrations.
3. Find Slack, Gmail, and Google Drive in the list.
4. Click Connect next to each one and complete the sign-in flow in the browser window that opens.

If a connection drops later (e.g., Claude says it can't reach Slack), go back to Integrations and reconnect. You only need to do this once per service.

4. The skill file

A file called "legal-guidance-vault.skill" — provided by whoever shared this guide. Install it once by double-clicking.

## Installation (One Time Only)

### Step 1 — Import existing meeting notes (optional)

If you have Google Drive meeting notes from the @meetingnotes template, bulk-import them first. Download legal-guidance-vault-import.skill from the same Drive folder as this guide and install it by double-clicking. Then ask Claude: "import my existing meeting notes from Drive." Run once only.

### Step 2 — Install Granola

Download and open Granola from granola.so. Sign in with your Google account and grant calendar and microphone permissions.

### Step 3 — Install the skill

Double-click "legal-guidance-vault.skill." Cowork will ask you to confirm — click Install.

## How to Archive

### From a Meeting (Granola)

After a meeting ends, tell Claude: "Archive my meeting with [team/person]." Claude finds it in Granola, extracts the legal substance, shows you a draft, and saves it after you confirm.

You can also just say "archive my last meeting" and Claude will identify it and confirm the title before proceeding.

To set this up as a daily or weekly automated scan, tell Claude: "Set up a daily/weekly scan for Granola meeting notes." Claude will configure a scheduled task that prompts you each day/week. [See sample instructions here]

### From Slack — Manual

Copy the link to any Slack thread (right-click a message → Copy link) and paste it into Claude with "archive this thread." Claude fetches the thread and surrounding channel context, synthesizes the full exchange including business context, shows you a draft, and saves it on confirmation.

### From Slack — Emoji Scan (set up once)

React to any Slack message with :file-cabinet: to flag it for archiving. To process flagged messages, tell Claude: "scan for my emoji-flagged Slack threads." Claude finds all messages you've reacted to with that emoji, fetches each thread, and presents them one at a time for review.

To set this up as a daily or weekly automated scan, tell Claude: "Set up a weekly scan for my :file-cabinet: Slack reactions." Claude will configure a scheduled task that prompts you each week. [See sample instructions here]

### From Email

Paste a Gmail link into Claude and say "archive this email." Or describe the email — "the Wilson Sonsini opinion on the data transfer issue from March" — and Claude will search your inbox, confirm the match, extract the guidance, and save it.

### From a Google Doc

Paste a Google Doc URL and say "archive this doc." Claude will ask: "Archive the whole doc or just the relevant sections?" Either way, a link back to the original doc is always included in the saved entry.

## How to Find Past Guidance

Just ask Claude naturally:

- "Find the guidance I gave about BIPA to the Tasks team."
- "What did I say about two-party consent?"
- "Have I dealt with geo expansion for the Commerce Platform before?"
- "What email guidance did I get from outside counsel about data transfers?"
- "What did I say about IP ownership — it was maybe a year ago."

Claude searches your vault and returns matching entries with the TL;DR and key guidance for each. If there are multiple matches, it synthesizes across them: "You've addressed this three times. The consistent position has been X."

## How to Tweak or Update the Skill

Just tell Claude: "I want to update my Legal Vault skill. Can we change [X]?" Claude will edit it, show you what changed, and give you an updated .skill file to reinstall by double-clicking.

## Tips

Archive selectively — only threads, emails, and docs where you gave or received guidance worth finding later. The vault is most useful when it's signal-dense.

The vault is plain text files on your Mac. Nothing is shared externally.

When archiving a Slack thread, Claude captures the full conversation including the business context — not just your messages. That context is often critical for understanding why you said what you said.

For outside counsel emails with long memos, archiving just the conclusion and key reasoning is usually enough. Claude will ask you if you want the whole thing or the relevant sections.

---

## Appendix

### Granola Scan Instructions

Set up a weekly scheduled task to scan my Granola meeting notes.

Schedule: every [Friday] at [11AM] [Mountain Time]

Each run should:

1. Check a state file at ~/Claude Cowork/Data/legal-guidance-vault/.scan-state.json for the last run date and already-archived meeting IDs (default to 7 days ago on first run)
2. Fetch all Granola meetings since the last run
3. Filter out any already archived
4. Show me a numbered list — meeting title, date, attendees, 1-line summary
5. Ask which ones I want to archive to the legal guidance vault
6. For each one I pick: show full notes, draft a vault entry using the legal-guidance-vault skill format, confirm with me, then save to ~/Claude Cowork/Data/legal-guidance-vault/
7. Update the state file with today's date and newly archived meeting IDs Use the legal-guidance-vault skill for the archive format and the Granola CLI for fetching meetings.

### Slack Scan Instructions

Set up a weekly scheduled task to scan Slack for threads I've flagged with the 🗄️ emoji.

Schedule: every [Friday] at [11AM] [Mountain Time]

My Slack ID: [find yours: click your profile photo in Slack → Profile → three-dot menu → Copy member ID]

Each run should:

1. Check ~/Claude Cowork/Data/legal-guidance-vault/.scan-state.json for the last Slack scan date and already-archived thread IDs
2. Search Slack for 🗄️-flagged messages since the last scan — try has::file_cabinet:, has::filing_cabinet:, and the emoji character in text, scoped to my messages
3. Filter out already-archived threads
4. Show me a numbered list — channel, date, participants, 1-line summary
5. Ask which ones I want to archive to the legal guidance vault
6. For each one I pick: show the full thread, draft a vault entry using the legal-guidance-vault skill format, confirm with me, then save to ~/Claude Cowork/Data/legal-guidance-vault/
7. Update the state file without overwriting other keys (Granola scan data should be preserved)

Use the legal-guidance-vault skill for the archive format.
