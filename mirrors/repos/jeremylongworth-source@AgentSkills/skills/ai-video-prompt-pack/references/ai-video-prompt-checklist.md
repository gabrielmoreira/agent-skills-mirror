# AI Video Prompt Pack Checklist

## Prompt Fields

- Tool or model: Gemini/Veo, Sora, Runway, Pika, Luma, or unspecified.
- Distribution: YouTube Shorts, Reels, TikTok, X, LinkedIn, website, ad, deck.
- Format: aspect ratio, duration, resolution target, silent or audio.
- Goal: awareness, proof, product demo, launch, conversion, education.
- Subject: one clear main subject or system.
- Action: one visual transformation or narrative beat.
- Scene: setting, background, environment, props, and interface type.
- Style: realistic, cinematic, product mockup, UI animation, documentary, etc.
- Camera: shot scale, movement, angle, lens feel, stabilization.
- Pacing: calm, urgent, premium, playful, instructional, reveal-driven.
- Audio: voiceover, sound design, music mood, ambient sound.
- Final frame: hold, CTA space, brand mark, product state.

## Current Platform Notes To Verify

These facts were checked against official docs during May 2026 work, but should
be re-verified before exact recommendations:

- Gemini Apps with Veo create 8-second videos. Google AI Plus and Pro use Veo
  3.1 Lite; Ultra uses Veo 3.1. Gemini video generation supports audio and can
  use uploaded images when the user has rights to them.
- Google states Veo in Gemini includes a visible watermark and SynthID.
- YouTube Shorts accepts square or vertical videos up to three minutes for
  standard channels, with special music and Content ID restrictions for Shorts
  over one minute.

## 8-Second Prompt Template

```text
Create an 8-second [aspect ratio] [platform/use] video for [brand/topic].

Scene: [single scene with one setting].
Action: [one clear visual transformation or reveal].
Style: [visual style, palette, realism, lighting].
Camera: [one camera move, stable framing, safe area needs].
Pacing: [beat timing and final hold].
Audio: [voiceover, music, ambient sound, sound design].
Final frame: [CTA space or end state].
```

## Negative Prompt Patterns

Use only the relevant items:

- unreadable text, fake words, fake logos, distorted UI
- generic stock office, smiling stock people, humanoid robots
- over-busy scene, fast cuts, shaky camera, motion blur
- sci-fi cliches, neon cyberpunk, glowing AI brain, random code rain
- watermark, low resolution, malformed hands or faces
- protected characters, living artist style, celebrity likeness

## Review Gates

- Does the clip communicate the intended single idea in the first two seconds?
- Does the visual transformation complete before the final second?
- Does the output match brand tone and audience expectations?
- Are there unusable text artifacts, fake logos, distorted UI, or visual errors?
- Are rights, disclosure, and platform-policy concerns resolved?
- Is the final frame usable for manual captions or CTA overlays?
