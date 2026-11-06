# Grow the watchlist (mode 2)

When `video-agent/competitors.json` doesn't exist yet, is thin in one language, or the creator writes `--search`. Goal: 3 to 6 new usable accounts (8 to 12 on the first run), never a list of 30 unchecked handles.

## The file

```json
{
 "self": "<their handle>",
 "mix": {"en": 70, "fr": 30},
 "accounts": [
  {"handle": "someone", "lang": "en", "tier": "direct", "niche": "a few words", "use": true, "added": "2026-10-16", "why": "one line"},
  {"handle": "someone", "platform": "tiktok", "lang": "en", "tier": "direct", "niche": "a few words", "use": true, "added": "2026-10-16", "why": "one line"}
 ]
}
```

`lang` = the account's language code; `tier` = `direct` (similar size and niche) or `aspirational` (much bigger, or a neighbour niche whose formats transpose); `use: false` = kept so it isn't proposed again; `platform: "tiktok"` = a TikTok account (no field = Instagram; the same creator on both = two entries). `mix` = the language split of the 5 scripts (one language only: leave it out).

## 1. Search

Ask first: "a creator search costs about $0.007, I'll run 2 or 3 per language". Then Exa through Treg, angles from their niche (`video-agent/voice.md`):

```bash
treg call exa.creators.search --method POST --data '{"query":"Instagram creators posting reels about <their niche>, <country or language>, comment-to-get CTA","includeDomains":["instagram.com"],"numResults":20,"contents":{"highlights":{"query":"<2 or 3 niche words>","maxCharacters":400}}}' 2>/dev/null
```

- Angles: the niche's main subject; the tools and methods their viewer uses; the result their viewer wants. For a second language, the same subjects with "creators in <language>".
- Endpoint gone or renamed: `treg catalog search "find Instagram creators by topic"`, then `treg catalog get <id>`.
- Never `category: people` (it returns LinkedIn). Take the handle from the profile URL (`instagram.com/<handle>/`), never from a `/reel/` or `/p/` link. Drop handles already in the file.

**TikTok**: search the videos themselves, about $0.001 a call, and keep the authors that come up with niche videos and real views:

```bash
treg call anyapi.tiktok.search.videos --method POST --data '{"query":"<2 or 3 niche words>"}' 2>/dev/null
```

The handle is in each video's `url` (`tiktok.com/@<handle>/video/...`). The Instagram creators already in the watchlist often have a TikTok under the same handle: fetch it and check.

Accounts that keep coming up in the reels already studied (tagged, remixed, quoted in a caption) are candidates too, for free.

## 2. Check each candidate

Fetch its reels (SKILL.md step 1), then keep it only if:

- its reels are about their niche (read 10 captions), not a one-off on the subject among unrelated reels;
- at least 10 reels in the last 180 days (it posts, so its median means something);
- the language is the one searched.

## 3. Record it

Add each checked account with `platform` (TikTok only), `lang`, `tier`, `niche`, `use`, `added` and `why`. A rejected candidate goes in with `use: false` and its reason, so it isn't searched and checked again.
