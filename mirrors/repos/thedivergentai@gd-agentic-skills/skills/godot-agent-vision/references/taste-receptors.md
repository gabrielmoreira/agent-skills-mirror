# Taste Receptor Atlas v2 (micro-scoring)

> **MANDATORY** for every vision review. This is the granular scoring layer under [vision-review-rubric.md](vision-review-rubric.md).
>
> Score **each applicable receptor 0 / 1 / 2**. Skip with `N/A` only if that pixel class is absent (never N/A to dodge bad taste).
>
> **Grade** = sum(scores) / sum(max of applicable) → percentage.
>
> | Grade | % of applicable |
> |-------|-----------------|
> | **A** | **≥ 90%** |
> | **B** | **75–89%** |
> | **C** | **58–74%** |
> | **F** | **&lt; 58%** |
>
> Optional legacy rollup **/120** via family → V-map at bottom.
>
> Default capture: short-edge **512**. If any **TYPE-*** / **CTRST-*** micro-seam is ≤1 for illegibility (not taste), re-capture `--detail` / crop before locking scores.
> For **MOT-*** / peak hit FX, capture a short 2–8 frame sequence when a single still is ambiguous.

**Companion deep loads (score micro-checklists inside):**
[typography-sight.md](typography-sight.md) · [hier-contrast-receptors.md](hier-contrast-receptors.md) · [space-affordance-receptors.md](space-affordance-receptors.md) · [color-icon-receptors.md](color-icon-receptors.md) · [composition-fx-receptors.md](composition-fx-receptors.md) · [anti-slop-sight.md](anti-slop-sight.md) · [originality-sight.md](originality-sight.md) · [identity-sight.md](identity-sight.md) · [ui-taste-sight.md](ui-taste-sight.md)

**Inventory (all families applicable):** **237 receptors × 2 = 474 pts** across 13 families.

---

## How to score a receptor

| Pts | Meaning |
|----:|---------|
| **2** | Clearly satisfied in the WebP |
| **1** | Partial / mixed / only some instances pass |
| **0** | Failed / inverted / AI-default / absent when required |
| **N/A** | Pixel class not in frame (state in notes) |

### Hard gates (any trip ⇒ cannot be **A**; some force **F**)

| Gate | Condition | Effect |
|------|-----------|--------|
| G-TYPE | `TYPE-GLYPH-INTEGRITY`=0 **or** `TYPE-DISPLAY-HUD-SPLIT`=0 on UI/HUD/menu | Max **B**; both 0 → max **C** |
| G-TYPE2 | `TYPE-FACE-CAP`=0 **and** `TYPE-OPSZ-MATCH`=0 | Max **C** |
| G-HIER | `HIER-WEIGHT-MATH`=0 **and** `HIER-URGENCY-LADDER`=0 | Max **C** |
| G-CTRST | `CTRST-BODY-45`=0 on critical HUD crop | Max **B** |
| G-SAFE | `SPACE-SAFE-TV` or `SPACE-SAFE-NOTCH`=0 when platform implied | Max **B** |
| G-SLOP | ≥4 of `SLOP-*` = 0 **or** `SLOP-STACK`=0 with T≥3 | Verdict **F** |
| G-ORIG | `ORIG-EXPR`=0 on final hero/marketing | Verdict **F** / ESCALATE |
| G-ID | `ID-BRIDGE`=0 when ≥2 surfaces visible | Max **C** |
| G-COLOR | `COLOR-ONLY`=0 (color-only meaning) on critical status | Max **B** |
| G-LIGHT | `LIGHT-BLOOM-ABUSE`=0 **and** `LIGHT-PART-OCCLUDE`=0 | Max **B** |
| G-COMP | `COMP-POWER-CONFLICT`=0 **and** `COMP-CENTER-CLEAR`=0 | Max **C** |

---

## Family HIER — Hierarchy & attention (24 × 2 = 48)

Deep: [hier-contrast-receptors.md](hier-contrast-receptors.md)

| ID | Receptor | 2 | 1 | 0 |
|----|----------|---|---|---|
| HIER-WEIGHT-MATH | Composite weight rank (size×contrast×motion×sat) | One dominant squint blob | Dual soft | Equal accents, no rank |
| HIER-FOVEAL-CLEAR | Center playfield open for foveal task | ≥~60% center clear | Mild intrusion | Center chrome stack |
| HIER-PERIPH-READ | Edge HUD readable without foveation | Shape/bar change in periphery | Soft | Micro numerals only |
| HIER-URGENCY-LADDER | Urgency→prominence monotonic | Crit > persist > meta | One loud meta | Social/shop = HP |
| HIER-FREQ-PLACEMENT | High-freq stats stable anchors | Same corners every crop | One drift | Relocates per state |
| HIER-DIEGETIC-SPLIT | Diegetic subordinate to combat HUD | Wrist/prop quieter | Blurry | Diegetic = critical HUD |
| HIER-NOTIF-STACK | Toast priority + recency | Lanes + dim older | Soft pile | Equal toasts over objective |
| HIER-OBJ-MARKER | Active objective wins POI clutter | One pulse; others grey | Soft | All POI equal |
| HIER-MINIMAP-RANK | Minimap ≤ combat readouts | Squint: HP > map | Tied | Map glow = boss frame |
| HIER-TOOLTIP-Z | Tooltip above HUD, below modal | Correct z | Soft | Under HP / over modal CTA |
| HIER-MODAL-TOAST | Modal blocks toasts | No toast on Confirm | Soft | Achievement covers quit |
| HIER-BOSS-BAR | Boss telegraph elevates | Wide top bar; player demoted | Soft | Boss = ammo width |
| HIER-COMBO-FLASH | Ephemeral score > currency | Big flash then collapse | Soft | Permanent display size |
| HIER-INTERACT-SING | One interact prompt | Single near reticle | Soft dual | Three equal prompts |
| HIER-INPUT-HINT | Platform glyph matches primary | Pad/keyboard hierarchy OK | Mixed | Wrong-platform dominate |
| HIER-SUBTITLE-LANE | Caption band isolated | Safe bottom; no overlap | Soft | Covers cooldowns |
| HIER-QUEST-ACTIVE | Active quest > log lines | Title loud; log dim | Soft | All lines equal |
| HIER-CURRENCY-DEMOTE | Currency secondary in combat | Small corner; no pulse | Soft | SALE = objective |
| HIER-PAUSE-SCRIM | Pause lifts with clear scrim | Dim + menu primary | Soft | Gameplay still competes |
| HIER-TUTORIAL-CALLOUT | Tutorial without hijack | Arrow+plate; HP readable | Soft | Full-screen tutorial = title |
| HIER-MARKETING-PLAY | Play path > marketing | Continue largest | Tied | Wishlist > New Game |
| HIER-PROGRESSIVE-FADE | Idle HUD demotes | Non-crit fades | Soft | Always 100% noise |
| HIER-DEAD-EMPTY | Empty/locked demoted | Lock+label | Dim only | Identical to filled |
| HIER-SCAN-PATH | F/Z/edge scan intentional | Predictable | Awkward | Random scatter |

---

## Family CTRST — Pressure contrast (18 × 2 = 36)

Deep: [hier-contrast-receptors.md](hier-contrast-receptors.md)

| ID | Receptor | 2 | 1 | 0 |
|----|----------|---|---|---|
| CTRST-BODY-45 | Body/HUD ~4.5:1 vs local plate | Holds at 512 | Mixed | Critical fails floor |
| CTRST-LARGE-30 | Large/display ~3:1+ | Holds | Spotty | Fails |
| CTRST-PLATE-OPACITY | Plate opacity tuned | ~70–85%; crisp | Soft | Useless haze / sticker block |
| CTRST-SCRIM-DEPTH | Modal scrim separates | 50–70% dim; isolated | Soft | Bleed-through |
| CTRST-OUTLINE-WEIGHT | Outline 1–2px policy | Shared weight | Drift | Glow lottery |
| CTRST-SIMULTANEOUS | Simultaneous contrast controlled | Plate over busy BG | Soft | Raw on snow/sky |
| CTRST-GRAD-WORST | Gradient worst-stop checked | All stops pass | One fail | Crosses failing band |
| CTRST-TV-LOUNGE | TV 2–3m viable | Couch-readable | Borderline | Pixel-peep primary |
| CTRST-HANDHELD-SUN | Handheld high ambient | Extra plate/shadow | Soft | Thin white on sky |
| CTRST-FX-BLOOM | Bloom does not erase UI | UI plate intact | Soft | Numerals washed |
| CTRST-FX-CHROMA | FX hue ≠ semantic UI | Distinct | Soft | Explosion = damage hex |
| CTRST-ICON-30 | Non-text chrome ≥~3:1 | Focus/slider clear | Soft | Grey-on-grey toggle |
| CTRST-DISABLED-30 | Disabled still legible | Readable grey+cue | Soft | Equals background |
| CTRST-FOCUS-30 | Focus ≥~3:1 | Outline/pip clear | Soft | Hue-only focus |
| CTRST-HC-MODE | HC path (if shown) | Borders+text ≥7:1 intent | Cosmetic | Recolor only |
| CTRST-SEMANTIC-NONCOLOR | Status not hue-only | Shape/icon/label | Weak | Color alone |
| CTRST-PLATE-EDGE | Plate edge cue | Shadow/bevel vs world | Soft | Same luminance as sky |
| CTRST-OVERLAP-LEG | Overlaps legible | Offset layers | Minor | Glyph collision |

---

## Family TYPE — Typography (41 × 2 = 82) — **heaviest family**

Deep: [typography-sight.md](typography-sight.md) — score **every** row when text is visible.

| ID | Receptor | 2 | 1 | 0 |
|----|----------|---|---|---|
| TYPE-ROLE-TOKEN | Named roles visible | HUD/Tooltip/Header/Display clear | 2 mushy | One size everywhere |
| TYPE-SCALE-RATIO | Modular steps | ~1.2–1.33 ladder | Soft jumps | Arbitrary sizes |
| TYPE-HUD-FLOOR | Floor = lowest device | Handheld/TV floor | Desktop-only | 4K-copied micro |
| TYPE-ANGULAR-SIZE | ~0.3°+ critical HUD | Couch angle OK | Soft | Illegible at distance |
| TYPE-OPSZ-MATCH | Optical size matches render | Open micro cuts | Marginal | Display cut at 11px HUD |
| TYPE-FACE-CAP | ≤2 families (+mono) | Disciplined | 3 faces | ≥4 tourist |
| TYPE-PAIR-DNA | Pairing stable | Same across surfaces | One drift | New face/screen |
| TYPE-GENRE-SIGNAL | Genre vs art | Matches + legible | Mild fight | Blackletter ammo |
| TYPE-DISPLAY-HUD-SPLIT | Display ≠ HUD data | Split clean | Bleed | Script on ammo/HP |
| TYPE-DIEGETIC-DISTRESS | Distress overlay, not replace | Overlay on scale | Soft | Incompatible scale |
| TYPE-WEIGHT-STEPS | 2–3 weights | Intentional | Soft | 1 or 5+ noise |
| TYPE-WEIGHT-OPSZ | Heavy @ small open | Semibold HUD OK | Soft | Black 10px clog |
| TYPE-XHEIGHT | Open apertures @ HUD | Counters open | Soft | Filled/spindly |
| TYPE-GLYPH-INTEGRITY | Real language | Readable | Soft artifacts | Garbled/fake |
| TYPE-NUM-TABULAR | Tabular feel (`tnum`) | Columns align | Soft | 1 vs 8 wobble |
| TYPE-NUM-LINING | Lining figures HUD | Baseline row | Soft | OSF in timer |
| TYPE-NUM-OSF-OK | Oldstyle flavor-only | Marketing OK | Soft | OSF in stats |
| TYPE-NUM-SLASH-ZERO | Slashed 0 if needed | Clear in codes | Soft | 0/O collide |
| TYPE-NUM-DISTINCT | 0/O 1/l 5/S | Clear under pressure | Soft | Confusable |
| TYPE-NUM-WEIGHT | Numerals ≥ label weight | HP digits bold | Soft | Thin decorative |
| TYPE-MONO-DATA | Mono/tabular codes/timers | Stable columns | Soft | Proportional hack |
| TYPE-STAT-ALIGN | Stat block grid | Labels+values align | Soft | Ragged |
| TYPE-TIMER-STABLE | Timer no width jitter | Digits hold | Soft | Layout jumps |
| TYPE-TRACK-BODY | Body track ≤~0.05em | Normal | Soft | Spaced-out body |
| TYPE-TRACK-DISPLAY | Display track intentional | Logo OK | Soft | Accidental collision |
| TYPE-TRACK-HUD | HUD slight tight OK | Clean caps | Soft | Crushed % |
| TYPE-LEAD-BODY | Body ~1.5–1.65 | Airy | Soft | Colliding |
| TYPE-LEAD-DENSE | Dense UI ~1.3–1.4 | Rhythm | Soft | Double gaps |
| TYPE-LEAD-DISPLAY | Display ~1.05–1.2 | Tight title | Soft | Huge voids |
| TYPE-KERN-LOGO | Logo kerning | Clean pairs | One bad | Exploded |
| TYPE-ALLCAPS-BODY | Caps not for body | Spare titles | Overused | Caps walls |
| TYPE-CASE-SENTENCE | Sentence case body | Descriptions OK | Soft | Title Case Every Word |
| TYPE-CASE-MICRO | Micro legal sized | True small | Soft | 8px caps paragraph |
| TYPE-ITALIC-UI | Italic rare | Flavor only | Mild | Every emphasis |
| TYPE-LIGA-DISPLAY | Ligatures display-only | Chapter OK | Soft | Ligatures in timer |
| TYPE-LOC-EXPAND | ~30%+ string room | DE/FR fit | Tight | Hard EN truncate |
| TYPE-LOC-RTL | RTL mirror room | Anchors OK | Soft | LTR-locked clip |
| TYPE-MICRO-LEGAL | Micro = legal/meta | Corner only | Soft | Primary CTA micro |
| TYPE-PLATE-TYPE | Plate over chaos | Objective plated | Soft | Raw on foliage |
| TYPE-HINT-RASTER | Pixel fonts integer | Crisp 1:1 | Soft | Non-integer blur |
| TYPE-MARKETING-DISPLAY | Store ≥1.5 step | Hero big | Soft | HUD-size tagline |

---

## Family AFF — Affordances & states (14 × 2 = 28)

Deep: [space-affordance-receptors.md](space-affordance-receptors.md)

| ID | Receptor | 2 | 1 | 0 |
|----|----------|---|---|---|
| AFF-OPERABLE | Looks clickable | Chrome ≠ static art | Ambiguous | Identical |
| AFF-SELECTED | Selected non-color | Outline/pip/fill | Weak hue | Hue-only / invisible |
| AFF-FOCUS | Focus language | Visible ≥3:1 | Soft | None |
| AFF-DISABLED | Disabled language | Dim+lock/label | Dim only | Looks broken |
| AFF-PRESSED | Pressed/active | Distinct | Subtle | Missing |
| AFF-HOVER | Hover (if pointer) | Lift ≠ only focus | Soft | Hover-only focus |
| AFF-HIT | Hit target scale | Pad/TV viable | Borderline | Tiny corners |
| AFF-CTA-VIS | CTA chrome singular | Strong plate | Competing | Lost in art |
| AFF-DEPTH | Tactile depth language | Consistent bevel/shadow | Random | Flat+3D lottery |
| AFF-CURSOR-PAD | Input-model match | Matches brief | Mixed | Dense pointer-only for pad |
| AFF-FEEDBACK | State change readable | Instant read | Partial | Static forever |
| AFF-FALSE | No false affordance | Art ≠ button look | Soft | Props look clickable |
| AFF-DRAG | Drag handles (if any) | Visible grip | Soft | Invisible drag |
| AFF-TOGGLE | Toggle on/off shape | Distinct shapes | Soft | Hue-only switch |

---

## Family SPACE — Spacing / Gestalt / safe area (18 × 2 = 36)

Deep: [space-affordance-receptors.md](space-affordance-receptors.md)

| ID | Receptor | 2 | 1 | 0 |
|----|----------|---|---|---|
| SPACE-8PT-RHYTHM | 8pt (4pt micro) rhythm | Clear scale | Soft | Arbitrary gaps |
| SPACE-4PT-MICRO | Icon–label micro gap | Consistent 4pt | Soft | Touch or orphan |
| SPACE-PROX-CLUSTER | Proximity clusters | Related tighter | Weak | Equal grid soup |
| SPACE-REGION-PANEL | Common region binds | Panel wraps group | Soft | Title far from stats |
| SPACE-ALIGN-COL | Column alignment | Prices/axes hold | Drift | Zigzag |
| SPACE-ALIGN-BASELINE | Baseline shared | Label+value | Soft | Float |
| SPACE-ALIGN-GRID | Shared left edges | Forms flush | Soft | Staggered |
| SPACE-GUTTER | Inter-col ≥ intra | Clear columns | Soft | Columns merge |
| SPACE-SAFE-TV | Title safe ~90% | Critical inside | Tight | Clipped edge |
| SPACE-SAFE-NOTCH | Notch/cutout inset | Below inset | Soft | Under island |
| SPACE-SAFE-OVERSCAN | Overscan-aware | BG bleed; UI inset | Soft | CTA in kill zone |
| SPACE-EDGE-HUD | Bezel inset | 16–24px feel | Soft | Glued to bezel |
| SPACE-PLAYFIELD | Center clear ring | Combat open | Mild creep | Creep inward |
| SPACE-DENSITY-BUDGET | Density vs class | ≤~7 primary rows pause | Soft | 15 equal tiles |
| SPACE-PANEL-PAD | Internal pad consistent | Even card pad | Mixed | Colliding internals |
| SPACE-STACK-MODAL | Modal stack rhythm | Title→body→CTA gaps | Soft | CTA glued |
| SPACE-NEST-DEPTH | ≤2 nest levels | Panel→row→control | 3 | Card-in-card-in-card |
| SPACE-RESP-COLLAPSE | Groups survive shrink | Mobile stacks OK | Soft | Unrelated merge |

---

## Family COLOR — Color as language (14 × 2 = 28)

Deep: [color-icon-receptors.md](color-icon-receptors.md)

| ID | Receptor | 2 | 1 | 0 |
|----|----------|---|---|---|
| COLOR-ROLES | 4–6 semantic roles | Danger/reward/neutral/interact/… | Soft | Random equal hues |
| COLOR-LAYERS | Base/panel/info/action stack | Value separation | Soft | Mud / rainbow chrome |
| COLOR-RED | Red reserved | Damage/danger | Mild leak | Accent everywhere |
| COLOR-GOLD | Gold = reward | Currency/XP/loot | Mixed | Gold as hazard |
| COLOR-BUDGET | Accent ~5–15% surface | Accents rare | Busy | Saturated spam |
| COLOR-ACC-JOB | Accents on urgency/CTA/special | Jobs clear | Soft | Decorative spam |
| COLOR-ONLY | Not color-only meaning | Shape/size/motion | Weak | Color alone critical |
| COLOR-CB | CVD survivability | Shapes if R/G | Risky | R/G-only status |
| COLOR-DL | Competing meanings ΔL | Value differs ~3:1 | Soft | Same-value hue swap |
| COLOR-SIM | Simultaneous contrast | Roles hold on BG | Spot | Washes out |
| COLOR-TOK | States = tints of roles | Token system | Soft | Per-widget lottery |
| COLOR-UI-WORLD | UI tied to world | Same family | Mild SaaS | Detached kit |
| COLOR-FX | VFX obey accent rules | Hits on-brand | Soft | Second brand |
| COLOR-COUNT | Palette restraint | ~8–16 feel | Soft | Infinite lottery |

---

## Family ICON — Iconography & chrome set (14 × 2 = 28)

Deep: [color-icon-receptors.md](color-icon-receptors.md)

| ID | Receptor | 2 | 1 | 0 |
|----|----------|---|---|---|
| ICON-GRID | Shared canvas/padding | Even set | Mild jitter | Random canvases |
| ICON-KEYLINE | Optical keyline weight | Circles optically larger | Soft | Measured-equal mush |
| ICON-STROKE | Stroke parity | One weight policy | Drift | Lottery |
| ICON-CORNER | Corner/terminal policy | Shared | Soft | Per-icon |
| ICON-SIL | Silhouette test | IDs in black fill | Two collide | Mush/clones |
| ICON-META | Metaphor dial | Same skeuomorph | Mixed | Engraved+sticky+neon |
| ICON-PERSP | Perspective agreement | Front/¾ shared | Soft | Mixed tilt+flat |
| ICON-DETAIL | Detail @ game size | Survives small | Busy | Only huge |
| ICON-PIXEL-LOCK | On-pixel @ HUD size | Crisp | Soft | Half-pixel shimmer |
| ICON-CAT | Category frame | Shape+color | Color-only | None/random |
| ICON-LUCIDE | Generic soup | Owned metaphors | Mild stock | Lucide-in-gradients |
| ICON-CHROME | Button/panel chrome | Shared radius/border | Drift | Per-screen reinvent |
| ICON-STATE | Icon states | Default/sel/dis clear | Partial | None |
| ICON-OPSZ | Heavier stroke when small | Opsz idea | Soft | Hairlines at 16 |

---

## Family COMP — Composition & framing (20 × 2 = 40)

Deep: [composition-fx-receptors.md](composition-fx-receptors.md)

| ID | Receptor | 2 | 1 | 0 |
|----|----------|---|---|---|
| COMP-THIRD-ACTION | Action on thirds / framed | Intentional focal | Soft center | Dead center no reason |
| COMP-THIRD-HUD | HUD off power points | Corners/edges | One intrusion | HP on intersection |
| COMP-POWER-CONFLICT | Power point conflict | No HUD+boss same locus | Minor | Crosshair+tele+CTA fight |
| COMP-CENTER-CLEAR | ~60% center free | Clear | Mild | Center cluttered |
| COMP-LEAD-ENV | Env leading lines | Aim at objective | Weak | Aim away |
| COMP-LEAD-UI | UI rails to CTA | Clear | Soft | Competing rails |
| COMP-VALUE-GROUP | B/W subject pops | Thumbnail read | Hue-reliant | Flat value soup |
| COMP-FOCAL-SINGLE | One primary in &lt;1s | Clear | Dual weak | Flat |
| COMP-FOCAL-WORLD | World focal vs UI | Action wins | Tied | Shop beats combat |
| COMP-DEPTH-LAYERS | FG/MG/BG separate | Depth clear | Soft | Flat plane |
| COMP-SIL-ACTION | Action silhouette | Limbs readable | Soft | Merge BG |
| COMP-SIL-THREAT | Threat silhouette | Telegraph distinct | Soft | Blob |
| COMP-NEG-SPACE | Breath around focal | Intentional | Uneven | Packed noise |
| COMP-BALANCE | Mass balance | Intentional | Soft | Accidental top-heavy |
| COMP-MASS-EDGE | Heavy chrome at edges | Center for play | Mild | Edge+center heavy |
| COMP-HORIZ-LEVEL | Horizon / dutch | Level or intentional | Soft | Accidental dutch |
| COMP-FRAME-ENV | Env framing | Arch/door frames subject | Loose | Lost in noise |
| COMP-SCAN-PATH | Scan path | Predictable | Awkward | Scatter |
| COMP-DIEG-META | Diegetic vs meta split | Grammar clear | Blurry | Overlay soup |
| COMP-SAFE-EDGE | Critical inside safe | Clear | Tight | Clipped |

---

## Family LIGHT — Lighting / post / particles / hit FX (20 × 2 = 40)

Deep: [composition-fx-receptors.md](composition-fx-receptors.md)

| ID | Receptor | 2 | 1 | 0 |
|----|----------|---|---|---|
| LIGHT-MOTIV | Motivated key | Shared vector | Soft | Sourceless wash |
| LIGHT-KEY-FILL | Key/fill ratio | Form readable | Mixed | Mud |
| LIGHT-RIM-OWN | Rim owned | Supports sep | Soft | Rim lottery |
| LIGHT-PLAY-SEP | Play layer separation | Interactive pops | Soft | Melts into BG |
| LIGHT-BLOOM-HIER | Bloom ≠ hierarchy | Structure intact | Mild | Bloom = hierarchy |
| LIGHT-BLOOM-ABUSE | Bloom abuse | Edges hold | Soft | Mush smear |
| LIGHT-DOF-SUBJ | DOF subject plane | Subject sharp | Soft | Gameplay blurred |
| LIGHT-DOF-UI | DOF vs UI | HUD sharp | Mild | UI illegible |
| LIGHT-POST-STACK | Post clutter | ≤2 dominant | 3 | AO+bloom+DOF+CA scream |
| LIGHT-PART-READ | Particles semantic | Direction/material | Busy | Noise |
| LIGHT-PART-OCCLUDE | Particles vs UI | UI clear | Fringe | Occlude HP/crosshair |
| LIGHT-PART-OVER | Occupancy budget | Impact ≤~12–18% | Border | Screen soft quads |
| LIGHT-FX-LANE | VFX lane ownership | Tele ≠ flourish hue | Soft | Same lane |
| LIGHT-HIT-SPARK | Hit spark language | Consistent type color | Mixed | Rainbow lottery |
| LIGHT-HIT-FLASH | Flash brief | Center not obliterated | Lingering | Full white block |
| LIGHT-HIT-SCALE | Hit tier scaling | L/M/H distinct | Soft | Uniform max |
| LIGHT-VIGN-DMG | Damage vignette | Edge only; center clear | Heavy | Eats UI/center |
| LIGHT-VIGN-META | Meta FX backup | Shape+color | Soft | Color-only low HP |
| LIGHT-EMISS-HIER | Emissive hierarchy | Danger/interact only | Overused | Every prop emissive |
| LIGHT-SPEC-LOT | Specular lottery | Consistent | Drift | Random shiny slop |

---

## Family MOT — Motion tells in stills (14 × 2 = 28)

Deep: [composition-fx-receptors.md](composition-fx-receptors.md). Prefer 2–8 frame sequence when flagged.

| ID | Receptor | 2 | 1 | 0 |
|----|----------|---|---|---|
| MOT-BLUR-READ | Motion blur aids | Direction clear | Heavy | Silhouette mush |
| MOT-SMEAR | Smear frames | Follows vector | Soft | Omni noise |
| MOT-TRAIL-SOUP | Trails | Short/tiered | Long | Obscure hitboxes |
| MOT-GHOST | Afterimages | Sparse readable | Many | Unreadable clones |
| MOT-SQUASH | Squash (if mid-pose) | Volume OK | Subtle | Missing expected |
| MOT-STRETCH | Stretch | Follows vector | Soft | Missing |
| MOT-VOL | Volume law | Mass preserved | Cheat | Inflating blob |
| MOT-ANTIC | Anticipation pose | Wind-up readable | Short | No telegraph |
| MOT-SHAKE-OFF | Shake vs UI | UI re-anchors | Medium | HUD floats off grid |
| MOT-SHAKE-TIER | Shake tier | Matches weight | Ambiguous | Coin = boss |
| MOT-SHAKE-ROT | Rotational shake | Minimal roll | Visible | Sickness roll |
| MOT-HITSTOP | Hit-stop | Micro-freeze sells | Long | Slideshow freeze |
| MOT-TWEEN-OS | UI overshoot | Settles on grid | Mid float | Buttons off baseline |
| MOT-UI-BOUNCE | Bounce scale | ≤~1.05/0.95 | Exaggerated | Oversized mid-bounce |

---

## Family SLOP — Anti-AI / median defaults (14 × 2 = 28)

Score **0** if tell present without ownership; **2** if absent or clearly world-owned.

| ID | Receptor | 2 (clean/owned) | 0 (default tell) |
|----|----------|-----------------|------------------|
| SLOP-PURPLE | Purple/indigo/pink wash | Absent/owned | Default hero wash |
| SLOP-NEON | Neon glow-as-hierarchy | Glow not hierarchy | Card glow everywhere |
| SLOP-CREAM | Cream+terracotta+serif | Absent/diegetic | Second-wave median |
| SLOP-CARD | Cardocalypse | Hierarchy uses cards | Equal nested cards |
| SLOP-GLASS | Glassmorphism spam | Rare | Everywhere muddy |
| SLOP-HOLO | Holo mesh / iridescent | Absent | Template hero |
| SLOP-LUCIDE | Icon soup | Owned set | Stock outline soup |
| SLOP-FAKE-TEXT | Fake glyphs | Clean | Garbled text |
| SLOP-SMOOTH | AI key-art smoothness | Crafted materials | Over-smooth SSS blob |
| SLOP-RIM | Sourceless rim set | Motivated light | Identical rim lottery |
| SLOP-EQUAL | Equal visual weight | Urgency map | Everything screams |
| SLOP-BLOOM | Bloom mush stack | Controlled | Post mush + neon |
| SLOP-SPEC | Interchangeable crop | Owned specificity | Paste onto any AI game |
| SLOP-STACK | Co-occurrence T | T≤1 or owned | T≥3 stacked tells |

---

## Family ORIG — Originality & construction (12 × 2 = 24)

Deep: [originality-sight.md](originality-sight.md)

| ID | Receptor | 2 | 1 | 0 |
|----|----------|---|---|---|
| ORIG-EXPR | Expression distance | Distinct after tropes | Soft | Franchise silhouette/mark |
| ORIG-REF | Reference transform | Multi-source → new | Unclear | Near-trace |
| ORIG-STRUCT | Construction integrity | Contacts/materials hold | Soft smear | Melt/grip failure |
| ORIG-TILE | Tiling/seam logic | Planned | Weak | Mirrored noise break |
| ORIG-SET | Set authorship | One rule set | Mixed | Kitbash lottery |
| ORIG-READ | Silhouette @ game size | Clear in ~2s | Soft | Only huge |
| ORIG-VALUE | Value shapes | B/W grouping | Hue-reliant | Color mush |
| ORIG-SYN | Synthetic density | ≤1 weak | Escalate | Stacked AI tells |
| ORIG-MARK | Marks/logos | Distinct | Soft | Appropriated |
| ORIG-LIGHT | Light logic | Motivated | Soft | Sourceless uniform rim |
| ORIG-HAND | Hand-authored tells | Toolmarks/asymmetry | Soft | Perfect symmetry mush |
| ORIG-SCENES | Scènes à faire filtered | Tropes transformed | Soft | Stock pose copy |

---

## Family ID — Graphic identity system (14 × 2 = 28)

Deep: [identity-sight.md](identity-sight.md)

| ID | Receptor | 2 | 1 | 0 |
|----|----------|---|---|---|
| ID-PAL | Palette roles | Limited + roles | Soft | Infinity |
| ID-SHAPE | Edge grammar | Repeated | Drift | Lottery |
| ID-MOTIF | Motif recurrence | 2–4 controlled echoes | One-off sticker | 0 or spam |
| ID-TYPE | Typographic identity | Stable pairing | Mild tourism | Tourism |
| ID-ICON | Icon system | Grid/stroke/sil OK | Soft | Mixed packs |
| ID-LINE | Line-weight policy | Global | Drift | Random |
| ID-RENDER | Render dial | One realism policy | Clash | Cel+PBR+paper |
| ID-LIGHT | Light continuity | Shared direction | Soft | Private rigs |
| ID-BRIDGE | HUD↔menu↔key art | Shared DNA | Soft split | Different products |
| ID-UIWORLD | UI↔world | Same family | Mild SaaS | Divorced |
| ID-SPEC | Owned specificity | Non-median | Mild default | Gradient-only brand |
| ID-DRIFT | Side-by-side drift | Adjacent shots match | Soft | Other game |
| ID-EDGE | Edge DNA shared | Motif↔panel↔logo | Soft | Random garnish |
| ID-TOKEN | Semantic tokens stable | Across surfaces | Soft | Per-screen recolor |

---

## Output schema (receptor-level — required)

```markdown
## Vision review — Taste Receptor Atlas v2
- **Paths / budget / sequence?:** …
- **Applicable max:** __ pts (N receptors × 2)
- **Score:** __ / __ (**__%**) — Grade A|B|C|F
- **Hard gates:** …

### Family subtotals
| Family | Score | Max | % |
|--------|------:|----:|--:|
| HIER | | 48 | |
| CTRST | | 36 | |
| TYPE | | 82 | |
| AFF | | 28 | |
| SPACE | | 36 | |
| COLOR | | 28 | |
| ICON | | 28 | |
| COMP | | 40 | |
| LIGHT | | 40 | |
| MOT | | 28 | |
| SLOP | | 28 | |
| ORIG | | 24 | |
| ID | | 28 | |

### Zeroes only (fix fuel) — every receptor scored 0
- `TYPE-DISPLAY-HUD-SPLIT` — ammo uses display face
- …

### Ordered fixes (map to receptor IDs)
1. `TYPE-DISPLAY-HUD-SPLIT` / `TYPE-NUM-TABULAR` — …
2. …
```

**Invalid review:** PASS/FAIL only · V1–V8 without receptor zeroes · skips TYPE when text visible · skips SLOP on UI/marketing · “looks good” without % + zero list.

---

## Rollup map → legacy V1–V8 /120 (optional)

| V | Max | From families (scaled) |
|---|-----|-------------------------|
| V1 Hierarchy | 15 | mean(HIER%, COMP%) × 15 |
| V2 Contrast | 15 | mean(CTRST%, LIGHT% pressure subset) × 15 |
| V3 Typography | 20 | TYPE % × 20 |
| V4 Affordances | 10 | AFF % × 10 |
| V5 Spacing | 10 | SPACE % × 10 |
| V6 Anti-slop | 15 | SLOP % × 15 |
| V7 Originality | 15 | mean(ORIG%, MOT% craft) × 15 |
| V8 Identity | 20 | mean(ID%, COLOR%, ICON%) × 20 |

Prefer **receptor % grade** as primary; publish V-rollup only if a consumer expects /120.
