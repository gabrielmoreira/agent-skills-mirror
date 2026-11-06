# Styles: the look of every edit

Every edit has the same layout: the **split-screen paper look** ([style.md](style.md)). A textured paper on top with one board at a time, the camera as a card under one seam, hard cuts between split, paper only and full camera. A style only changes how it looks and sounds: colors, fonts, captions, paper, grade, pace, music and sound, the creator's handle and CTA, their logos.

A style is one folder in the creator's project:

```text
video-agent/
├── style.json            {"default": "default"}: the style every edit uses when none is named
└── styles/
    ├── default/
    │   ├── style.json    the keys (all in style-schema.md)
    │   └── assets/
    │       ├── logos/    real logos of the tools the creator talks about (notion.png, claude.png...)
    │       └── fonts/    an own font file, optional
    └── <name>/           other styles (made by /steal or copied from default/)
```

`short.mjs init` snapshots the style into the project (`source/style.json`) and copies its `assets/` there, so a board logo is `assets/logos/notion.png`. `--style <name>` picks another one. No style at all: the engine defaults, already finished.

## The five tested looks

[`assets/looks.json`](../assets/looks.json) holds five starting points, each a `style` patch to copy into `style.json` and adjust:

| look | says | for |
|---|---|---|
| `default` | minimal: textured paper, the system font (San Francisco on a Mac, Segoe UI on Windows), the camera full width under one straight seam, captions in mono capitals (JetBrains Mono), white on a black rounded band sitting on the seam | anyone, nothing to choose |
| `classique` | textured paper, sticker captions, blue accent | a more playful paper look |
| `papier` | deep shadows, the camera as a framed photo, `rise` captions (the said word on an accent block), Bricolage Grotesque | tech, explainers, premium |
| `pop` | off-white, black and a loud yellow, big `hard` captions with a hard shadow | podcast, opinion, energy |
| `poster` | flat orange background, hard cuts, the key word huge in condensed capitals on the camera | fast, viral, very readable |

## A style.json

```json
{
  "version": 1,
  "name": "Default",
  "creator": { "name": "Léa", "handle": "@lea.ia", "lang": "fr", "niche": "IA pour les indépendants" },
  "colors": { "accent": "#258EFF" },
  "captions": { "style": "rise", "size": 82 },
  "display": { "font": "Bricolage Grotesque", "weight": 800, "text": "Bricolage Grotesque", "flat": true },
  "font": { "family": "Bricolage Grotesque" },
  "pace": { "speed": 1.15 },
  "sfx": { "accents": 0 },
  "notes": ["Comment word: GUIDE", "Never zoom on my face"]
}
```

Only the keys that differ from the engine defaults. `notes` are rules: follow them on every edit (the comment word of the CTA lives there).

## Checking a change

Edit the file by hand, then look at it on a real short: `node <skill>/engine/short.mjs stills <project> 1,4,8` on any edit (after `init` with that style), and read the JPGs. The accent must stay readable on the paper, white caption text readable on its block, logos crisp, nothing cut at the edges.

## Logos

Every tool named on screen shows its real logo: the press kit, the App Store icon, the official repo or site. Save it as a PNG (512 px, transparent if possible) in `styles/<name>/assets/logos/<tool>.png`. A logo you can't find for sure: ask the creator for the file, never draw a look-alike.
