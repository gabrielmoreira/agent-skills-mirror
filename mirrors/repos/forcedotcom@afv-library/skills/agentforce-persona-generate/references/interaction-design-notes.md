---
version: "1.0.0"
date: 2026-07-15
---

# Interaction Design Notes

Cross-surface UX guidelines for running the persona skill. These apply across all surfaces —
CLI, TUI, web, IDE.

**Output before questions.** Show generated content first, then ask a concise question with short options.

**Batch independent questions.** When multiple questions have no dependency relationship, present together. Examples:
- Context essentials (channel + company + audience + use case) — ask together
- Voice dimensions (Formality, Warmth, Personality Intensity, Reading Level) — ask together
- Chatting Style dimensions (Emoji, Formatting, Punctuation, Capitalization) — ask together

Do NOT batch across dependency boundaries. Identity → Personification → Register → Voice → Tone → Delivery → Chatting Style is sequential.

**Short labels, descriptions underneath.** Options scannable in under 2 seconds.

**Multi-select when appropriate.** Phrase book entries to keep, subagents to encode, surfaces to target — allow multiple selections.

**Compact output formats.** Tables for dimensions, lists for phrases, no walls of prose.

**Progress awareness.** Before showing the HUB after a phase/spoke, show a one-line status:
> "Clover: [+] Identity · [+] Dimensions · [+] Phrase book (18) · [+] Never-say (8) · pending: name, encoding"

**Confidence callouts.** After presenting a drafted persona, highlight 1-2 lowest-confidence dimensions:
> "Least certain: Humor (defaulted) and Emoji (defaulted). Adjust these first if they matter."
