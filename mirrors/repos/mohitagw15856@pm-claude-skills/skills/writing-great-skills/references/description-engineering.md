# Description Engineering: the 300 Characters That Decide Everything

A skill's frontmatter description is its entire existence at routing time — the only thing a model sees when deciding whether to load it. Most weak skills aren't weak at the method; they're invisible at the router. This is the engineering discipline for that one field.

## The three-part contract (and why each part exists)

1. **What it does** (one clause) — the capability, concrete: "Write a blameless incident postmortem" not "Helps with incidents". The router matches capabilities, not vibes.
2. **"Use when…"** — trigger phrases in the USER'S vocabulary, not yours. Users say "my boss wants an update", "we got rejected again", "what went wrong friday" — not "stakeholder communication artifact". Mine real requests (support logs, your own asks) for the phrasing; three concrete triggers beat one abstract one.
3. **"Produces…"** — the artifact, named: "a postmortem with timeline, root cause, and owned action items". This is how the model weighs payoff AND how the user recognises they got the right thing.

## Trigger-phrase craft

- Include the emotional/situational phrasings ("keeps getting rejected", "before the board sees it") — that's how tasks actually arrive
- Include the artifact's aliases ("postmortem, incident report, RCA") — different orgs, different words
- If sibling skills exist, the description arbitrates: "For X use [sibling] instead" — one sentence prevents every misroute between you
- Test empirically: give a model five realistic asks and the description list; does yours win the asks it should and LOSE the ones it shouldn't? Over-matching is as broken as under-matching.

## Length physics

Under ~150 chars: probably missing triggers or the artifact. Over ~500: diluting the match signal and crowding the context every routing pass pays for. The sweet band is 250-400 — every word earning its routing weight.

## The gallery

| Weak | Why | Engineered |
|---|---|---|
| "Helps with meetings" | no artifact, no triggers | "Turn a raw transcript into decisions, owners & next steps. Use when asked for meeting notes, a recap, or 'what did we decide'. Produces…" |
| "A comprehensive framework for strategic analysis" | says nothing concrete | (delete; start from what it OUTPUTS) |
| "Write OKRs" | under-triggered | "+ Use when setting quarterly goals, reviewing existing OKRs, or when KRs read like task lists. Produces…" |
