---
name: media-search
description: Find and play music/videos via youtube_search + open_url
category: media
version: 1.3.2
origin: aiden
license: Apache-2.0
tags: music, video, youtube, play, song, listen, media, autoplay
required_tools: [youtube_search, open_url]
---


# Media Search & Play

Resolve "play X" / "listen to X" / "find me a song" requests by chaining
`web_search` (optional, for fuzzy intent) → `youtube_search` (REQUIRED,
returns real watch URLs) → `open_url` (REQUIRED, must use a URL that
came back from `youtube_search`). The user hears the song in their
default browser without you having to drive a controlled browser
session.

<execute_action>
"Play X" is the authorization. You're not asking permission, you're
confirming the action by doing it. Once `youtube_search` returns a URL
that clears the rules below, fire `open_url` in the same turn — no
deliberation step between picking and opening.

If any of these phrases form in your reply draft, you have stopped
short of the action:

- "say go ahead"
- "should I"
- "I can do that for you"
- "let me know if"
- "if you want"
- "want me to"
- "shall I"

Replace the offer with the call: invoke `open_url`, then write
the report. The user's default browser is the feedback channel —
not your prose.
</execute_action>

<selection_rule>
How strict you should be about picking a candidate from
`youtube_search` depends on how specific the user's query is.

**VAGUE query** — no specific song or artist named. Examples:
"play me a popular song", "play me a hindi song", "play
something upbeat", "put on some jazz", "play a sad song".

→ Walk the `youtube_search` candidates **top-down** and pick
   the **first one** whose `title` does NOT match any of the
   anti-patterns below. That is the answer. Do not score
   candidates further; do not look for "the most official one";
   do not compare view counts. The first non-anti-pattern wins.

   **Anti-pattern keywords** (match case-insensitively against
   `title`):

   - "reaction", "reacting to", "react to", "first time hearing"
   - "they know every word", "knows every word"
   - "lyric video", "lyrics video"
   - "cover", "covered by", "cover by"
   - "compilation", "best of", "mashup", "mix"
   - "livestream", "live stream", "LIVE", "24/7", "stream"
   - "shorts" (the `#shorts` format)
   - "fan edit", "fan made", "fanmade", "edit by"
   - "version of", "remake", "tribute"
   - "1 hour", "10 hours", "loop", "extended"

   Why this matters: vague queries on YouTube often surface
   reaction clips or lyric videos near the top because they
   pull engagement. The user said "play a popular song" —
   they want to hear the song, not someone reacting to it.
   The anti-pattern filter is what keeps the vague rule from
   opening "the way they know every word! 🧡" instead of the
   actual track.

   If every candidate in the top 5 matches at least one
   anti-pattern, that is a legitimate fallback: take the
   honest-fallback path (results page).

**SPECIFIC query** — the user named a song or artist. Examples:
"play Bohemian Rhapsody", "play Despacito", "play Tum Hi Ho",
"play Sabrina Carpenter".

→ Require a substring match between the candidate's `title`
   field and either the song title (preferred) or the artist
   name (acceptable when artist-only was given). Pick the
   highest-ranked candidate that matches. Then open. Do not
   keep looking once a match is found — the top match is the
   answer.

**Honest fallback (`youtube.com/results`) is for one situation
only**: `youtube_search` returned **zero** candidates, OR every
candidate is structurally wrong (channel page only, livestream
when the user wanted a song). It is NOT for "results exist but
they don't feel polished enough." If `youtube_search` returned a
list and you can't pick one, the rule above failed — re-read it.
</selection_rule>

## REQUIRED tool sequence (read this first)

Every successful run of this skill calls these tools, in order:

1. `web_search` — **OPTIONAL pass 1**: identify the specific song
   title + artist. Skip this when the user already named a song.
2. `youtube_search` — **REQUIRED pass 2**: get real `/watch?v=` URLs
   for that specific song. Query: `<title> <artist> official audio`.
3. `open_url` — exactly **once**, with a URL that came back from
   `youtube_search` (verbatim — copy the `url` field from the tool
   result, do not retype it from memory).

Then you report. **A run that stops after `youtube_search` is a
FAILED run** — the user does not hear anything until `open_url`
fires. The runtime enforces both conditions:

- **Skill enforcement** (Phase 23.1): if you emit a final message
  without calling every tool in `required_tools`, your reply is
  discarded and you are asked to retry. Cap of 2 corrective retries.
- **URL provenance gate** (Phase 23.4a): if `open_url` receives a
  `youtube.com/watch?v=<id>` URL whose `<id>` was NOT returned by
  any `youtube_search` call this turn, the call is **blocked before
  the browser opens**, an error is fed back to you, and you are
  asked to call `youtube_search` and pick a real URL. Cap of 2
  corrective retries; on exceed the user sees an honest-failure
  message, not a confabulated open.

Anti-patterns the planner sometimes drifts into — do NOT do these:

- ❌ **Composing a `/watch?v=ID` URL from memory or prose.** The 11
  characters after `v=` are NEVER something you type — they are
  always copied verbatim from a `youtube_search` result. The
  provenance gate exists precisely because the model has been
  caught inventing IDs. Don't.
- ❌ Skipping `youtube_search`. `web_search` returns prose snippets
  and articles ABOUT songs, not autoplay-friendly URLs.
  `youtube_search` is the only tool whose results clear the
  provenance gate.
- ❌ Re-entering the `media-search` skill mid-run after the
  searches returned. The skill is already loaded; re-viewing
  wastes a turn and signals a hung agent. Run `youtube_search`,
  then `open_url`.
- ❌ Stopping after the searches and asking the user to confirm. The
  user's "play me a song" request is the consent — proceed to
  `open_url`.
- ❌ Picking a `youtube_search` result whose **title** does not
  contain the song you committed to. Artist-only match is not
  enough; "Alex Warren live stream" is not "Alex Warren — Ordinary."
- ❌ Picking a result whose title says "live stream", "24/7",
  "lyric", "cover", "reaction", "best of", "compilation", "mashup",
  "1 hour", or "loop". Those don't match what the user asked for.

## When to use

The user's request matches any of these patterns:

- **Direct play:** "play Despacito", "play Bohemian Rhapsody"
- **Fuzzy play:** "play me a popular song", "play something upbeat",
  "play a sad song"
- **Listen intent:** "I want to listen to jazz", "put on some music"
- **Artist intent:** "play kendrick lamar", "play some abba"
- **Video intent:** "show me the latest Marvel trailer", "play that
  cooking video about ramen"

If the user says "open spotify" or "open youtube" without a specific
piece, that's an `open_url` direct call — not this skill.

## How to use

### Pass 1 — Identify the song

The goal of pass 1 is to **commit to a specific `<title>` and
`<artist>` before you pick any URL**. Build the query from what the
user actually said:

| User said | Pass-1 query |
|---|---|
| "play me a popular song" | `Billboard Hot 100 #1 this week` |
| "play me something upbeat" | `top upbeat pop songs 2026` |
| "play me a sad song" | `top ballads 2026 spotify` |
| "play me kendrick lamar" | `kendrick lamar most popular song 2025` |
| "play me a hindi song" | `bollywood top hindi songs this week` |
| "play me jazz" | `jazz standards essential listening` |
| "play Despacito" | (skip pass 1 — title already given) |
| "play Bohemian Rhapsody" | (skip pass 1 — title already given) |

After pass 1, **announce your commitment in your reasoning** (this is
NOT yet shown to the user — that comes after `open_url`):

> Picked: `<title>` by `<artist>` (reason: e.g. "currently #1 on
> Billboard Hot 100").

If the user already named a specific song, pass 1 is unnecessary —
the title and artist are already given. Skip directly to pass 2.

### Pass 2 — Get real YouTube watch URLs (`youtube_search`)

Call `youtube_search` with a query of the form:

```
"<title>" <artist> official audio
```

Wrap the title in double quotes. `youtube_search` hits the public
YouTube results page, parses real `/watch?v=` URLs out of the
response, and returns a list of `{ videoId, url, title, channel,
durationText? }` objects. The URLs in that list are the only URLs
the **URL provenance gate** will let `open_url` consume — anything
else is blocked before the browser opens.

**URL-selection rules (apply in order to the `youtube_search`
results, not to `web_search` snippets):**

1. **The result's `title` field MUST explicitly contain the song
   title** you committed to in pass 1. Artist-only mention is not
   enough. If the title doesn't name the song, skip it.
2. Prefer results whose `title` contains "Official Audio",
   "Official Music Video", "Official Video", or "Official Lyric
   Video". These are usually the artist's verified upload.
3. **Reject** results whose `title` contains any of: "live stream",
   "LIVE", "24/7", "lyric video" (unless specifically requested),
   "cover", "covered by", "reaction", "react to", "best of",
   "compilation", "mashup", "remix" (unless specifically requested),
   "hour" (e.g. "1 hour version"), "loop". These don't match what
   the user asked for.
4. If no result in the top 5 satisfies rules 1–3, fall through to
   the honest-fallback path (below). Do **not** loosen the rules to
   force a pick.

### Step 3 — Open the URL

Call `open_url` with the **`url` field** of the chosen
`youtube_search` result — copy it verbatim, do not retype. Exactly
once, in the same turn that `youtube_search` returned. Don't print
the URL and ask. Don't list the candidates. Don't pause for
confirmation. YouTube's `/watch?v=` pages autoplay in the user's
browser; the autoplay is the answer to "did it work?", not your
prose. This step is REQUIRED.

The URL provenance gate validates `open_url`'s `url` argument
against this turn's `youtube_search` results before the browser
launches. If you somehow type a watch URL that wasn't in the
result list (you composed an ID, you reused one from training
data, you typo'd while copying), the call is rejected, an error
is fed back to you, and you are asked to try again with a real
URL from `youtube_search`. The user's browser does not open until
the URL clears the gate.

### Step 4 — Report (after `open_url` has fired, not before)

Format your reply so the user sees what you picked AND why. The title
must be **announced together with the URL in a single message that
follows the `open_url` call**, never as an offer before it:

> Picked: `<title>` by `<artist>` — `<one-line reason>`. Opened
> `<url>`.

For a fuzzy intent ("popular song") the reason explains your
substitution ("currently #1 on Billboard"). For a specific request
("play Despacito") the reason can be brief ("the official video").

### Honest-fallback: no verifying URL found

If pass 2 returns no result that satisfies all the URL-selection
rules above, the fallback **executes** in the same turn — it is not
something you offer to the user.

1. `open_url` to
   `https://www.youtube.com/results?search_query=<title>+<artist>`
   (URL-encoded). Same turn. No "want me to?" question. No "let
   me know if".
2. **After** `open_url` fires, report what executed:
   > Couldn't find a verified official upload for `<title>` by
   > `<artist>`. Opened
   > `youtube.com/results?search_query=<title>+<artist>` — autoplay
   > doesn't fire on results pages, so pick a tile to start
   > playback.

Do NOT claim "now playing" — that would be the same fabrication
Phase 23.1 was built to catch. Do NOT ask "should I open the
search page?" — that's the offer-style anti-pattern Phase 23.3
specifically forbids.

## Examples

### Example 1 — vague query, walk top-down with anti-pattern filter

User prompt: "play me a popular song"

The `<selection_rule>` block says: vague query → walk
`youtube_search` candidates top-down, skip anti-patterns, take
the first clean one. No officialness scoring beyond that.

Expected flow:
- Aiden may run an optional `web_search` to commit to a current
  chart-topper (e.g. "Opalite" by Taylor Swift). This is for
  query construction, not for filtering YouTube results.
- Aiden runs: `youtube_search("Opalite Taylor Swift")` →
  returns 5 candidates:

  1. `{ title: "the way they know every word! 🧡 Opalite by Taylor Swift", channel: "Krystal" }` — title contains "they know every word" → **anti-pattern match, skip**.
  2. `{ title: "Taylor Swift - Opalite (Official Audio)", channel: "Taylor Swift" }` — no anti-pattern keyword → **first clean candidate, pick**.
  3. (rest of list ignored — once a clean candidate is found, stop)

- Aiden runs: `open_url(<candidate 2 .url>)` — copy the `url`
  field verbatim. The provenance gate sees the id in the ledger,
  lets the call through.
- Aiden reports: "Picked: '<title>' from '<channel>'. Opened
  `<url>`."

If every candidate in the top 5 hits an anti-pattern keyword —
e.g. all reactions, all lyric videos — that is the legitimate
fallback case (Example 5). Do not loosen the anti-pattern
filter to force a pick.

### Example 2 — specific title, match required

User prompt: "play Tum Hi Ho"

The `<selection_rule>` block says: specific query → require a
title or artist substring match in the candidate before opening.

Expected flow:
- Title given (Tum Hi Ho). Aiden skips `web_search`.
- Aiden runs: `youtube_search("Tum Hi Ho")` → list of candidates.
- Aiden walks the candidates top-down looking for the first one
  whose `title` field contains "Tum Hi Ho" (case-insensitive
  substring is fine). The highest-ranked match is the answer —
  not "the most official-looking one further down the list."
- Aiden runs: `open_url(<that result's url, verbatim>)`.
- Aiden reports: "Picked: '<title>' from '<channel>'. Opened `<url>`."

If the very top result's title contains "Tum Hi Ho", that's the
match. Stop looking. Open it.

### Example 3 — specific song, top result is the match

User prompt: "play Despacito"

Expected flow:
- Title and artist already given (Despacito, Luis Fonsi).
- Aiden skips `web_search`.
- Aiden runs: `youtube_search("Despacito Luis Fonsi")` → top
  result's title contains "Despacito". Match found at rank 1.
- Aiden runs: `open_url(<top result.url>)`.
- Aiden reports: "Picked: '<title>' from '<channel>'. Opened
  `<url>`."

### Example 4 — artist-only, hybrid

User prompt: "play me kendrick lamar"

This is between vague and specific: the artist is named, so "Not
Like Us by random tribute act" is wrong, but the song isn't —
so the bar is "any candidate whose channel or title is Kendrick
Lamar's actual catalog."

Expected flow:
- Aiden may run `web_search("kendrick lamar most popular song
  2025")` to commit to a likely song (e.g. "Not Like Us"). This
  step is optional but useful for query construction.
- Aiden runs: `youtube_search("Kendrick Lamar Not Like Us")` →
  list of candidates.
- Aiden picks the top candidate whose `title` or `channel` names
  Kendrick Lamar. Top result usually qualifies.
- Aiden runs: `open_url(<that result's url, verbatim>)`.
- Aiden reports: "Picked: '<title>' from '<channel>'. Opened
  `<url>`."

### Example 5 — fallback to results page

User prompt: "play that lo-fi beats stream"

Expected flow:
- Pass 1: `web_search("popular lo-fi beats stream 2026")` → top
  result is "lofi hip hop radio — beats to relax/study to" channel.
- Aiden commits: title="lofi hip hop radio", artist="Lofi Girl".
- Pass 2: `youtube_search("\"lofi hip hop radio\" Lofi Girl official
  audio")` → top results are channel pages and livestreams. Every
  watch URL whose title contains "live" or "24/7" fails reject rule
  3. No top-5 result satisfies the rules.
- Aiden runs:
  `open_url("https://www.youtube.com/results?search_query=lofi+hip+hop+radio+Lofi+Girl")`
  — this is a `/results?` URL, not a `/watch?v=` URL, so the
  provenance gate does not apply (it's only scoped to watch URLs).
- Aiden reports honestly: "Couldn't find a single verified upload —
  Lofi Girl's stream is a 24/7 livestream, not a single video.
  Opened YouTube search results; click any livestream tile to start
  playback."

## Cautions

- **Never call `open_url` more than once per request.** If the first
  call succeeded, the URL is open in the user's browser. Re-launching
  is duplicate noise.
- **`/watch?v=` autoplays; `/results?` and `/c/` do NOT.** Only claim
  "now playing" when you launched a watch URL.
- **`youtube_search` is required, not optional.** Skipping it means
  the URL provenance gate has no candidates and any `open_url` call
  to a watch URL gets blocked. The gate is structural — there is no
  way to bypass it from the prompt side.
- **`web_search` (pass 1) is optional, but valuable for fuzzy
  intents.** It helps you commit to a specific title before
  `youtube_search`. For "play Despacito" you can skip it; for "play
  me a popular song" you almost certainly need it.
- **Don't search verbatim for fuzzy phrases.** "popular song" verbatim
  returns articles ABOUT popular songs, not the songs themselves. The
  whole point of pass 1 is to substitute fuzzy → specific BEFORE
  `youtube_search`.
- **Title match is non-negotiable.** If the `youtube_search` result's
  `title` doesn't literally contain the song title you committed to,
  that result is not the song you said you'd play. Skip it. If
  nothing matches, take the honest fallback.
- **No Spotify integration in v4.0.** If the user explicitly asks for
  Spotify ("play X on spotify"), tell them: "Spotify integration ships
  in v4.1. For now I can open the song on YouTube instead — want me
  to?"

## Requirements

- `web_search` tool (always available — registered at boot)
- `youtube_search` tool (always available — registered at boot)
- `open_url` tool (always available, BUILTIN_SAFE_TOOLS, auto-approves)
- The user's default browser must be installed (every desktop has one).
- No API keys, no credentials, no plugins.
