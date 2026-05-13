# Design Direction Advisor — Extended Reference

Read this when the request is vague ("make something nice", "I don't know what style I want") and no design context exists. The main `SKILL.md` already covers the **mechanism** (3 differentiated directions, named designer references, hard rule against same-school picks). This file provides the **library** — concrete philosophies you can pull from, per-direction visual recipes, and prompt templates.

---

## How to Use This File

1. Read the user's request and the four positioning questions (narrative role / viewing distance / visual temperature / capacity)
2. Pick **3 directions from different rows** below (the school table) that genuinely fit the user's context
3. Recommend each with: named designer/studio + 2–3 lines of "why this fits you" + 3–4 signature visual cues + (optional) one famous touchstone work
4. Wait for the user to pick one (or remix two)
5. The chosen direction becomes the design context — write it into `brand-spec.md` and proceed to the main workflow

---

## The Five Schools (1 of 3 must come from each different row)

### 1. Information Architecture

**Vibe**: Rational, data-driven, restrained, hierarchy-led
**Best for**: Safe / professional / B2B / data products / institutional
**Why it works**: Treats the page as a *system* of typographic and grid relationships. The "design" disappears so the information speaks.

| Anchor | What to borrow |
|---|---|
| **Pentagram** (Paula Scher, Michael Bierut) | Bold typography as image; identity through type relationships; sparing color use |
| **Edward Tufte** | Maximum data-ink ratio; small multiples; smallest sufficient difference |
| **Massimo Vignelli** | Helvetica-style restraint; strict grid; 6 typefaces is enough for a lifetime |
| **NB Studio / Spin** | Editorial restraint applied to corporate identity |

**Visual recipe**:
- Type: large-scale display headlines (often Helvetica / Suisse / Söhne / Neue Haas Grotesk family); body in the same family at small sizes
- Color: 1 ink + 1 accent + 1 background — that's it
- Layout: strict 12-column grid, generous gutters, baseline-grid alignment
- No: gradients, shadows, decorative icons, illustrations
- Motion: minimal — fades and slides only, never bouncy

**Sample copy when recommending**:
> "Pentagram-style information architecture — your dashboard becomes a system of typographic relationships rather than a UI. Headlines do the heavy visual lifting; everything else recedes. Best when you want institutional credibility and your data is the hero."

---

### 2. Editorial / Minimalist

**Vibe**: Whitespace, refined typography, quiet luxury, considered
**Best for**: Premium / high-end / quiet / lifestyle / prestige B2C
**Why it works**: Treats whitespace as the primary design material. The reader/viewer gets room to breathe; restraint reads as confidence.

| Anchor | What to borrow |
|---|---|
| **Kenya Hara (MUJI)** | Whiteness as a value; *ex-formation*; emptiness as fullness |
| **Apple HIG / Marketing** | Generous negative space; hero product on white; one-thought-per-screen |
| **Dieter Rams (Braun)** | "Less but better"; honest materials; functional decoration is a contradiction |
| **Aesop** | Cream/sage palette; serif copy as conversation; product as protagonist |

**Visual recipe**:
- Type: editorial serif display (Newsreader / Source Serif / EB Garamond / GT Sectra) + clean sans body (Söhne / Inter Tight / Geist Sans)
- Color: warm off-white + ink + 1 muted accent (sage, ochre, terracotta) — no pure black, no pure white
- Layout: asymmetric, lots of margin, single column for body, oversized hero
- No: bento grids, multiple cards per row, busy navigation
- Motion: slow Ken Burns, subtle parallax, never snap

**Sample copy when recommending**:
> "Kenya Hara-style editorial minimalism — the page is mostly whitespace, with one serif headline carrying emotional weight and the product anchored in a single hero shot. Best when premium positioning matters more than feature density."

---

### 3. Motion / Experimental

**Vibe**: Bold, generative, sensory, kinetic, technical
**Best for**: Distinctive / launch films / brand moments / awwwards-style / tech storytelling
**Why it works**: Movement and surprise are the brand. Static screenshots can't capture the experience.

| Anchor | What to borrow |
|---|---|
| **Field.io** | Generative type and form; data-driven motion; the page is a system that *makes* itself |
| **Active Theory** | WebGL hero moments; physics-driven interactions; cinematic transitions |
| **Resn** | Storytelling through scroll; payoff for exploration; surprise is the reward |
| **Vercel / Linear marketing** (recent) | Subtle but everywhere motion; glass + gradient meshes used with restraint |

**Visual recipe**:
- Type: variable fonts that *do something* (axis transitions on hover/scroll); often display-weight grotesque
- Color: high-contrast, often dark base + 1–2 saturated accents; or generative gradients
- Layout: full-bleed canvases, content emerges through scroll, CTAs deliberately delayed
- Motion: choreographed, multi-stage, eased — `cubic-bezier(0.83, 0, 0.17, 1)` style "expo" curves
- Required: a concrete motion language declared up-front (which easings, which durations, which trigger types)

**Sample copy when recommending**:
> "Field.io-style motion-led identity — the page generates itself in front of the visitor through choreographed scroll-driven sequences. Best when the launch *moment* matters and your audience will share clips. Note: this is the most labor-intensive of the three; budget accordingly."

---

### 4. Brutalist / Raw

**Vibe**: Anti-design, honest, unpolished, confrontational
**Best for**: Differentiated / confident / counter-culture / publishing / artist platforms
**Why it works**: Ugly-on-purpose reads as authentic in a sea of polished AI defaults. The lack of consensus aesthetic *is* the aesthetic.

| Anchor | What to borrow |
|---|---|
| **Are.na** | Raw HTML feel; system fonts on purpose; content > chrome |
| **Bloomberg Businessweek covers** (Richard Turley era) | Typographic violence; magazine grid abused; copy as image |
| **Balenciaga** (post-2017) | Default browser styling weaponized; hero text in Helvetica at absurd scale |
| **Craigslist (yes, really)** | Information density without apology; everything is a link |

**Visual recipe**:
- Type: monospace + system serif; or one display font abused at every size
- Color: 1–2 colors max, often fluorescent or muddy on white; never "tasteful"
- Layout: visible grid breaks, intentional misalignment, density without hierarchy where appropriate
- Required: commit fully — half-brutalism reads as broken design, not a statement
- No: drop shadows, gradients, rounded corners > 4px, "polish"

**Sample copy when recommending**:
> "Are.na/Bloomberg-style brutalism — system fonts, harsh type contrast, no rounded corners, no shadows. Confrontational on purpose. Best when you're a strong contrarian voice and want to repel the crowd that wants 'modern SaaS.' Warning: half-measures here look broken, not bold."

---

### 5. Warm Humanist

**Vibe**: Approachable, organic, hand-touched, friendly without being childish
**Best for**: Lifestyle / education / approachable B2C / community products / health
**Why it works**: Conveys that real humans made this for real humans. Counters the "robot wrote my landing page" perception.

| Anchor | What to borrow |
|---|---|
| **Mailchimp** (early Freddie era) | Hand-drawn marks; warm illustration; personality in microcopy |
| **Stripe Press** | Editorial serif + warm palette + tactile object photography |
| **Studio Dumbar** | Identity through movement and personality, not through restraint |
| **Notion** (pre-AI era) | Emoji as first-class design element; soft shadows; rounded everything but not in a cookie-cutter way |

**Visual recipe**:
- Type: humanist serif (Tiempos / GT Sectra / Sentinel) + rounded sans (Söhne Breit / Inter Tight); one decorative script for accent (Caveat used sparingly)
- Color: warm neutrals (cream, sand, sage) + saturated friendly accent (caramel, coral, terracotta)
- Layout: rounded cards (16–24px radius), soft shadows, illustrations *replace* hero photos
- Motion: gentle, never snappy; bouncy easing curves welcome
- Required: at least one element of intentional human warmth (real photo of the team, a hand-drawn mark, a microcopy joke)

**Sample copy when recommending**:
> "Stripe Press / early Mailchimp warmth — humanist serifs, cream palette, illustrations that feel hand-touched. Best when you want trust and approachability over institutional polish. Tone is 'friend who happens to be expert,' not 'expert addressing client.'"

---

## When the User Picks (or Remixes)

Common user responses:

- **"I'll go with #2."** → Direction confirmed. Write it into `brand-spec.md`. Proceed to Step 2 with this as design context.
- **"I like A's color but C's layout."** → Confirm the remix in writing ("So: minimalist editorial palette + motion-led layout choreography. Right?"), then proceed.
- **"None of these feel right — show me more."** → Ask one targeted question to narrow ("Are you closer to formal/institutional or playful/expressive?"), then offer 3 fresh directions from rows you didn't show before.
- **"I don't know, you pick."** → Pick the safest one (usually Editorial / Minimalist), state your reasoning, and propose a 5-minute v0 to validate before committing.

---

## AI-Prompt Templates (when generating imagery to support a direction)

Format: `[philosophy DNA] + [content description] + [technical params]`

✅ **Good** (specific characteristics):
> "Kenya Hara-influenced minimalism with 80% whitespace, single muted terracotta (#C04A1A) accent, GT Sectra serif headline, single product hero on warm off-white (#F2EFE8) ground, soft top-down lighting, 3:2 aspect"

❌ **Bad** (style names without DNA):
> "minimalist style, premium feel, high quality"

Always include:
- Color HEX (not "warm" / "cool")
- Aspect ratio and dimensions
- Composition rules (rule-of-thirds, centered, asymmetric)
- What to *avoid* (e.g., "no purple gradient, no emoji, no rounded cards")

---

## Anti-Patterns in Direction Recommendation

❌ **Recommending 3 picks from the same row** — the user can't tell them apart; the entire point of "differentiated directions" collapses

❌ **Recommending "minimalism" / "modern" / "clean"** as the direction name — these are not directions, they are AI-default words. Always anchor on a named designer/studio.

❌ **Recommending without any "why this fits you"** — the user wanted *guidance*, not a multiple-choice quiz. Each option must explain its fit to their context (audience, purpose, budget, brand maturity).

❌ **Showing 5+ directions** — choice paralysis. 3 is the sweet spot. If the first 3 all miss, ask one narrowing question and offer 3 fresh ones.

❌ **Asking the user to score each direction 1–10** — that's offloading the recommendation back to them. Make a recommendation; the user will agree or push back.
