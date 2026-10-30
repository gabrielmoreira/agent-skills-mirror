---
name: linkedin-post
description: >-
  Draft a punchy, ready-to-paste LinkedIn post around a video, demo, repo or
  launch — in the user's own voice. Runs a short intake (language EN or EN+FR,
  target audience, complexity/register, main messages, mandatory links, assets,
  CTA, hashtags, disclaimers), researches the author's tone from their profile/
  articles (or asks for a sample when LinkedIn blocks fetching), applies LinkedIn
  reach best-practices (hook, white space, native video, captions, link
  placement, length, hashtags), and outputs the final copy plus a media checklist
  (poster/cover + FR & EN subtitle files). Use for "write a LinkedIn post",
  "LinkedIn caption for this video", "post this demo on LinkedIn", "rédige un post
  LinkedIn", "poste ma vidéo sur LinkedIn". Not for other social networks or
  long-form articles.
---

# LinkedIn post writer

Produce a **copy-paste-ready LinkedIn post** in the author's voice, tuned for
reach, around a piece of media (usually a video/demo) with the right links,
captions and cover.

## Bundled references
- `references/questionnaire.md` — the intake to run before writing.
- `references/linkedin-playbook.md` — structure, media, links, hashtags, length.
- `references/tone-and-voice.md` — how to capture and mirror the author's voice.

## 1. Intake (ask before writing)
Run `references/questionnaire.md`: **language** (EN, or EN+FR two-part post),
**target audience**, **complexity/register**, **main messages** (2–4), **mandatory
links**, **assets** (video, poster, FR/EN subtitles), **CTA**, **hashtags**,
**disclaimers**. Never invent a link or a disclaimer — ask.

## 2. Capture the author's voice
Follow `references/tone-and-voice.md`. Try to fetch the author's LinkedIn profile/
articles; LinkedIn usually blocks server-side fetches (HTTP 999 / login wall). If
blocked, **ask the user to paste 1–3 recent posts** or pick a tone from the menu —
do not fabricate their style. State which sample you matched.

## 3. Write the post
Apply `references/linkedin-playbook.md`:
- A hook line that earns the "…more" click (no "I'm excited to announce").
- Short paragraphs with white space; 3–5 beats (problem → what → how → proof).
- Name concrete tech where the register calls for it; show, don't boast.
- One clear CTA. 3–5 specific hashtags at the end.
- Target ~1,300–1,900 characters; front-load meaning in the first ~210 chars.
- For EN+FR: EN block, a `— — —` divider, then the FR block (not a literal
  translation — localize idioms).
- **Links**: default to placing mandatory links in the **first comment** (and say
  "link in comments") to protect reach; if the user requires them in-body, honor
  that and note the trade-off. Provide the first-comment text separately.

## 4. Media checklist (deliver alongside the copy)
- **Native video** (upload the MP4 directly, not as a URL).
- **Captions**: FR and EN. LinkedIn takes one SRT per upload (viewer toggle);
  for both languages, deliver two SRT files (user picks per post) or a burned-in
  variant per language. Most feed views are muted — captions are mandatory.
- **Poster/cover**: a strong, muted-legible first frame or a custom cover
  (headline + product name). Offer a 1:1 or 4:5 re-crop for more mobile height.
- **Alt text** for any still image.

## 5. Deliver
Output, clearly separated:
1. The **post body** (per language) ready to paste.
2. The **first-comment** text (links) if links were moved out of body.
3. The **media checklist** with exact file paths for video, poster and SRTs.
4. A one-line note on which voice sample you matched and any assumption to confirm.
