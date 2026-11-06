---
name: studio-setup
description: Sets up the creator's video editing studio, for shorts and YouTube videos, on their computer and in their project - tools, the video-agent/ folder, the render engine, the creator's voice.md, their default editing style (an onboarding on their colors, paper, fonts, captions, sound, Instagram CTA, real tool logos, logo and end card, with a preview on their own footage), permissions, and the optional accounts (Treg for Instagram, TikTok and YouTube, an ElevenLabs key, Codex). Use when the user says setup, onboarding, install, "start here", configure, connect my account, Treg, first time using studio-script, short-editing, publish or any video skill, or wants to update their voice, niche, CTA, brand color, look, font, captions, sound effects, logo or tool logos (`/studio-setup style`). Checks Node, ffmpeg, yt-dlp and git with install commands for macOS, Windows and Linux, writes voice.md from their own videos or a short interview, pre-approves the tool commands in .claude/settings.json.
argument-hint: "[tools | engine | voice | style | permissions | treg | keys]"
allowed-tools: Bash(node *) Bash(ffmpeg -version) Bash(ffprobe -version) Bash(yt-dlp --version) Bash(deno --version) Bash(git --version) Bash(codex --version) Bash(treg --version)
---

# Studio Setup

About 15 minutes, once. At the end the creator has:

- the tools the other skills call, installed and checked,
- `video-agent/voice.md`: who they are, how they talk, what they believe, what they can prove. Every script is written from it,
- `video-agent/styles/default/style.json`: their look on top of the split-screen paper layout (their color, fonts, captions, paper, pace, sound, Instagram CTA), with the real logos of the tools they talk about. Every edit uses it,
- the render engine ready (Chrome, whisper.cpp, the music beds), so the first edit starts right away,
- permission rules, so Claude can run ffmpeg, yt-dlp and the engine without asking each time,
- if they want: their accounts connected through Treg (audit and publishing), and the keys for translation and images.

## How to run it

- Talk in the creator's language. Simple words, no jargon.
- One question per message. Offer choices when you can, recommended first.
- Never invent anything about them: a fact you don't have becomes a question or a `{{placeholder}}`.

## 1. Tools

Run the checks and show one line per tool (✓ version, or ✗ missing):

```bash
node -v
ffmpeg -version
yt-dlp --version
deno --version
git --version
```

| Tool | Used by | macOS | Windows | Linux |
|---|---|---|---|---|
| Node 20+ (22 LTS recommended) | short-editing (the render engine) | `brew install node` | `winget install OpenJS.NodeJS.LTS` | nodejs.org or your package manager |
| ffmpeg | short-editing, steal, clips, short-translate, publish | `brew install ffmpeg` | `winget install Gyan.FFmpeg` | `sudo apt install ffmpeg` |
| yt-dlp | studio-script viral, steal, clips, voice.md from videos | `brew install yt-dlp` | `winget install yt-dlp.yt-dlp` | `pipx install "yt-dlp[default]"` |
| deno | yt-dlp on YouTube (it needs a JavaScript runtime) | comes with yt-dlp | `winget install DenoLand.Deno` | `curl -fsSL https://deno.land/install.sh \| sh` |
| git | installing the skills | `xcode-select --install` | `winget install Git.Git` | `sudo apt install git` |
| Codex (optional) | codex-images | `npm i -g @openai/codex`, then `codex login` | same | same |

Give the commands for what is missing and let them run them (or run them yourself if they say so). Scripting-only users (studio-script, its `viral` mode included) only need yt-dlp and deno. Codex is only for `/codex-images` and needs a ChatGPT plan; skip it if they don't want images.

- Windows: after `winget`, close and reopen the terminal (and Claude Code), or the new commands are not found.
- YouTube changes often. When yt-dlp fails on a link that plays in the browser, update it first (`brew upgrade yt-dlp`, `winget upgrade yt-dlp.yt-dlp`, `pipx upgrade yt-dlp`).

## 2. The folder

Create it at the root of the current project:

```text
video-agent/
├── voice.md      who they are and how they talk (step 4)
├── swipe.md      hooks that worked in their niche (`/studio-script viral`)
├── audit.md      what works on their own Instagram (insta-audit)
├── audits/       full Instagram reports, one folder per account and run (insta-audit @handle)
├── log.md        one line per script written, so nothing repeats
├── scripts/      one file per week (studio-script)
├── takes/        raw recordings (phone, camera, webcam, screen)
├── style.json    {"default": "default"}: the style every edit uses (step 5)
├── styles/       default/ (their look, step 5), and styles copied from other creators (steal)
├── edits/        one folder per edited video (short-editing): source/spec.js, output/<name>.mp4 + post.md, cover.jpg, published.md
├── repurpose/    one plan per long video (clips)
├── images/       generated images not tied to a video (codex-images)
├── .env          their API keys, never shared (step 7)
└── .tmp/         scratch files, deleted after each run
```

`log.md` starts with `# Script log`, `swipe.md` with `# Swipe file`.

If the project is in git, add these lines to its `.gitignore` (videos are heavy; the text files stay tracked):

```gitignore
video-agent/takes/
video-agent/edits/**/*.mp4
video-agent/edits/**/assets/
video-agent/edits/**/stills/
.claude/skills/short-editing/.runtime/
.claude/skills/short-editing/engine/node_modules/
video-agent/.tmp/
video-agent/.env
```

`video-agent/.env` holds keys: it must be ignored even if they skip the rest.

## 3. The engine

The render engine ships inside the `short-editing` skill (`<skill>` = that skill's folder, e.g. `.claude/skills/short-editing`). Its first setup installs the engine packages (15 MB), a Chromium when no Chrome is installed (100 MB), whisper.cpp and its speech model (0.5 GB) and the 8 music beds: 3 to 6 minutes, once. Ask: now (recommended if they will edit soon, and it lets step 5 show their style on their own footage), or later (short-editing runs it the first time). Only for short-editing, clips and short-translate; scripting-only users skip it.

```bash
node <skill>/engine/setup.mjs --check || node <skill>/engine/setup.mjs
```

Say what is downloading and how big before starting. ffmpeg missing: it prints the install command.

## 4. voice.md

First the setting at the top of the file: the language they record in (their brand color is asked in step 5). Then ask how to build the rest:

1. **From their videos** (recommended when they have posted before): 3 to 5 links of their best talking videos (YouTube, Shorts, TikTok, Instagram reels). Pull the transcripts (`<lang>` = their language code: `en`, `fr`, `es`):
   ```bash
   yt-dlp --skip-download --write-auto-subs --write-subs --sub-langs "<lang>.*" --sub-format vtt -o "video-agent/.tmp/%(id)s.%(ext)s" "<url>"
   ```
   Read them and fill the template from what they actually say: their real phrases, their pace (words ÷ minutes of speech), the words they repeat, the way they open and close. Then ask only what the transcripts can't tell (positions, proof, off limits, the ask). Delete `video-agent/.tmp/` after.
   YouTube links almost always give a transcript. TikTok sometimes does, Instagram almost never: for those, ask for a YouTube link or switch to the interview.
2. **From an interview**: ask the template's questions one at a time, in plain words ("What do you believe that most people in your niche get wrong?").

Either way, ask them to paste 3 short texts they wrote themselves, before any AI tool (a caption, a message, an email). They go in "Real samples" and teach the scripts their rhythm.

Write `video-agent/voice.md` from [references/voice-template.md](references/voice-template.md). Then read it back to them in 5 lines and ask what is wrong. A voice file is never finished: say they can run `/studio-setup voice` any time to update it.

## 5. Style

Five minutes. Every edit has the same finished layout, the **split-screen paper look**: boards on a textured paper above the camera card, hard cuts between split, paper only and full camera, captions on the seam, a comment-sheet CTA ([style.md](../short-editing/references/style.md)). This step makes it theirs: `video-agent/styles/default/style.json`. The format and the five tested looks: [looks.md](../short-editing/references/looks.md); every key: [style-schema.md](../short-editing/references/style-schema.md). Read both first.

Say it in one line before starting: "The default already looks finished; I'll ask 7 quick questions to make it yours, then show it on your own video." Then **one question per message**, choices with the recommended one first, and their answer can always be "default" or "skip". Use what voice.md already says (niche, tone, the ask) to pick the recommendation and to skip a question it already answers.

1. **Look**: show the five looks of `<skill>/assets/looks.json` in one line each (`label` + `says`): **default** (minimal: the system font, the camera full width, mono caps captions on a black band on the seam, recommended), **classique** (sticker captions), **papier** (framed camera photo, the said word on a color block), **pop** (podcast, opinion), **poster** (fast, hard cuts). Their pick's `style` patch is the start of the file.
2. **Accent color**: "Your brand color? A hex code, or a color in words." They name a color: turn it into a hex → `colors.accent`. None: keep the look's. It marks the accent words, the caption block, numbers, so it must be strong (not a pastel).
3. **Fonts**: "Keep the **system font** (the one of the Mac, San Francisco; Segoe UI on Windows, recommended), or **Bricolage Grotesque** (modern, tight), **Poppins** (round, friendly), **Archivo** (heavy, condensed), **Inter** (neutral)?" The system font is `system-ui, -apple-system, Segoe UI, Helvetica Neue, Arial, sans-serif`. → `font.family`, `display.font` / `display.text`. Their own font file: copy it to `styles/default/assets/fonts/` and set `font.src`.
4. **Captions**: "**Band**: mono capitals, white on a black rounded band on the seam, 3 words at a time (`band` + JetBrains Mono, recommended), **minimal** white words on the video, each one appearing when said (`rise` + `block: false` + `straddle` + `straddleDy: 90`), the **said word on a color block** (`rise`), **hard shadow** (`hard`) or **sticker**?" Then "Normal size, or bigger?" (bigger = `captions.size` 96). UPPERCASE = `captions.upper: true`.
5. **Rhythm**: "**Fast** (1.15x, the default), **Calm** (1.05x) or **Natural** (1x)?" → `pace.speed`.
6. **Instagram CTA**: "Your Instagram handle, and the word you ask people to comment (GUIDE, LINK, the product name)?" → `creator.handle`, `creator.name`, and a note `"Comment word: <WORD>"` in `notes`. Also `creator.lang` (their recording language) and `creator.niche` from voice.md.
7. **Tools you talk about**: "Which apps or tools do you name most in your videos?" Up to 8. For each, fetch the real logo ([looks.md](../short-editing/references/looks.md), "Logos"), save it as `video-agent/styles/default/assets/logos/<tool>.png`. A logo you can't find for sure: ask them for the file, never draw a look-alike.

**Write** `video-agent/styles/default/style.json` (`"version": 1`, `"name"`, the look's patch, then their answers; only keys that differ from the engine defaults) and `video-agent/style.json` = `{"default": "default"}`. Check it parses: `node -e 'JSON.parse(require("fs").readFileSync("video-agent/styles/default/style.json","utf8"))'`.

**Preview**, when the engine is set up (step 3) and they have a take of 10 s or more in `video-agent/takes/`:

```bash
node <skill>/engine/short.mjs init video-agent/edits/short-style-test --source "<take>"
```

Then in its `source/spec.js` add one board around second 1 to 4 of the take (a `text` with their accent word, their first tool's `logo`; [scene-library.md](../short-editing/references/scene-library.md)), and:

```bash
node <skill>/engine/short.mjs words video-agent/edits/short-style-test
node <skill>/engine/short.mjs prepare video-agent/edits/short-style-test
node <skill>/engine/short.mjs stills video-agent/edits/short-style-test 0.5,2,5
```

Read the JPGs in `stills/` yourself first: the accent readable on the paper, white caption text readable on its block, the logo crisp, nothing cut at the edges. Fix what fails, then show them and ask: "Keep it, or change one thing?" A change = edit style.json, `init` again (it snapshots the style), new stills. Trash `short-style-test` after. No take yet: describe the look in 3 lines, the first edit shows it.

They can run `/studio-setup style` any time to change it. A creator's style copied with `/steal` sits next to it (`video-agent/styles/<name>/`) and is used with `/short-editing <take> style <name>`.

## 6. Permissions

The other skills run the same few commands again and again. Pre-approve them for this project. Show the rules, ask, then **merge** them into `.claude/settings.json`. Create the file if it is missing. Keep every key and rule already there, and never remove anything.

```json
{
  "permissions": {
    "allow": [
      "Bash(yt-dlp *)",
      "Bash(ffmpeg *)",
      "Bash(ffprobe *)",
      "Bash(node .claude/skills/short-editing/engine/*)"
    ]
  }
}
```

- Only these. Never add `Bash(*)`, `Bash(rm *)`, `Bash(curl *)` or a rule for a whole interpreter (`Bash(node *)`, `Bash(python *)`).
- Rules in the shared `settings.json` apply once the folder is trusted. A creator who keeps this project in git and doesn't want to share the rules can use `.claude/settings.local.json` instead (same format, personal).
- Each skill also lists its own commands in its `allowed-tools`, which covers the turn the skill runs in. These rules cover every other turn.

## 7. Accounts and keys (optional)

Three things, each only if they want the skill that needs it. Ask once, in one message:

| For | What | Cost |
|---|---|---|
| `/insta-audit` and `/publish` | Treg, with their Instagram, TikTok and YouTube connected | free on their own accounts |
| exact transcripts in `/short-editing` (every retake and false start heard, so they get cut), `/short-translate`, `/steal`'s music level under the voice (sound effects ship with the pack, no key needed) | an ElevenLabs API key (recommended) | their ElevenLabs plan |
| `/codex-images` | Codex logged in with their ChatGPT account | their ChatGPT plan |

**ElevenLabs**: they create a key at elevenlabs.io/app/settings/api-keys and paste it themselves into `video-agent/.env` as `ELEVENLABS_API_KEY=...` (create the empty file and open it for them). Never ask for a key in the chat. Check it is there without printing it: `grep -c ELEVENLABS_API_KEY video-agent/.env`.

**Codex**: `codex --version`, then they run `codex login` (browser, "Sign in with ChatGPT").

### Treg

yt-dlp reads YouTube for free. TikTok and Instagram hide their numbers from scripts, a creator's own stats sit behind their login, and posting needs their accounts. [Treg](https://treg.to) fills that gap: their own accounts connected once (stats and publishing, free), other creators' public numbers for about $0.001 a call. New verified accounts get $1.00 of credit once, enough for hundreds of calls.

Two ways to plug it in:

- **CLI**, macOS and Linux. It needs uv (recommended, it fetches the right Python), or pipx or pip with Python 3.12 or 3.13. There is no Windows installer.
  ```bash
  curl -fsSL https://treg.to/install.sh | sh
  treg login
  ```
  `treg login` opens the browser (GitHub, Google or an email code).
- **MCP**, any OS, nothing to install: `claude mcp add --transport http treg https://treg.to/mcp/`, then `/mcp` to sign in. Each `treg catalog search`, `catalog get`, `call` and `balance` below becomes the MCP tool `catalog_search`, `catalog_get`, `call` or `balance`.

**Their own accounts** (connecting needs the CLI). `--capability post` asks for the rights to read their stats and to post; posting still waits for their yes on each video:

```bash
treg connections connect --provider instagram --capability post
treg connections connect --provider tiktok --capability post
treg connections connect --provider youtube --capability post
treg connections ls
```

Each `connect` opens the platform's own login; they approve it there. Connect only the platforms they post on. Instagram needs a professional account (Creator or Business, a free switch in the app: Profile → menu → Account type and tools). Treg prints tips on stderr: add `2>/dev/null` when you read its JSON.

Instagram connected: offer `/insta-audit` right after, it is the best first look at what works for them.

**How every Treg call works**, the rule for all the skills:

1. `treg catalog search "<what you want to do>"`: describe the job, not a vendor ("list a TikTok account's videos with view counts").
2. `treg catalog get <id>`: the parameters and the **price**. Say the price before calling. Their own connected accounts are marked free.
3. `treg call <id> --query key=value`. A failed call is not charged. `treg balance` shows what is left; a 402 error means the balance is empty.

Permissions: add only the free, read-only commands, so every paid `treg call` still asks first:

```json
"Bash(treg catalog *)",
"Bash(treg balance)",
"Bash(treg connections ls)"
```

## 8. Wrap up

Show what is ready (✓ or skipped, one line each) and the path forward. They can also just type `/editing <what they want>`: it picks the right skill.

The shortest path to a first video: record one take (phone, camera or webcam) into `video-agent/takes/<slug>.mp4`, then `/short-editing`. Then, when they want more:

1. `/studio-script`: this week's scripts, hooks first, humanized (`/studio-script viral` first for what works in their niche).
2. `/insta-audit`: what works on their own Instagram (fills audit.md).
3. `/outliers`: the reels that blew up for their competitors, turned into 5 scripts to record.
4. `/short-editing`: a short (vertical) or a full YouTube video (horizontal), in their style.
5. `/broll`: their own B-roll clips as a library, placed on their edits.
6. `/steal`: a creator's reel they love into a second style.
7. `/clips`: a long video into finished shorts.
8. `/short-translate`: a take in another language, in their voice.
9. `/codex-images`: thumbnails, covers, end cards.
10. `/vox`: a photo into a paper-collage animation.
11. `/publish`: YouTube, Instagram and TikTok.

## Later

`/studio-setup <part>` jumps to one part: `tools`, `engine`, `voice` (rebuild or update voice.md), `style` (their look, sound, CTA, tool logos, logo, end card), `permissions`, `treg`, `keys`.
