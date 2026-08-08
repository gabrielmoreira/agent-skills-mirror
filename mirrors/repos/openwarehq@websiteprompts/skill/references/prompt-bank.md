# The video prompt formula, and 37 prompts that work

Clips look "AI" when the prompt describes a *thing* — "a futuristic glowing
background, high-tech, 8k, vibrant". That wording pushes every model toward the
same over-saturated, over-busy, aimless-motion slop. The fix is **specificity,
restraint, and a cinematic reference.**

---

## The 5-part formula — every good clip has all five

1. **A specific subject in a specific place.** Not "abstract shapes" — *"a single
   drop of black ink blooming in clear water"*, *"an empty highway at night seen
   through a windshield."*
2. **A named light source.** "Backlit", "glowing street lamps", "a soft key light
   raking across it", "god-rays through fog". Light is 80% of "cinematic".
3. **An explicit colour grade.** "Dark blue cinematic grade", "warm amber",
   "desaturated teal". Name the mood; do not hope for it.
4. **ONE slow camera move, spelled out.** "Slow steady forward push", "slow orbit".
   Never "dynamic", never two moves. AI motion looks fake when it is fast or does
   too much — **restraint is what reads as expensive.**
5. **A reference register, last.** "Premium car commercial", "luxury perfume ad",
   "premium nature film". This single clause drags the whole render toward real
   cinema.

**Always end with:** `shallow depth of field, one continuous shot, no cuts, no
on-screen text, no watermarks`. That kills garbled lettering and jump-cut
artifacts, and the shallow depth of field adds instant premium.

### Fill-in template

```
Cinematic <shot type> of <specific subject> in <specific place>,
<named light>, <colour grade>, <ONE slow camera move>,
<reference register>, shallow depth of field,
one continuous shot, no cuts, no on-screen text, no watermarks
```

### Before → after

❌ `a futuristic neural network, glowing, high tech, hyper-detailed, 8k, vibrant`

✅ `Cinematic macro flight through a vast glowing neural network in deep space,
luminous nodes firing electric blue and violet, volumetric glow, one slow forward
glide, premium AI film, shallow depth of field, one continuous shot, no cuts, no
on-screen text, no watermarks`

---

## Tips that actually matter

- **Real-world physics beats abstraction.** Ink in water, silk in wind, molten
  gold, fog, a car on a wet road — these render beautifully because the model has
  seen them filmed a million times. "Energy / particles / abstract" screams AI.
  Give it something real to simulate.
- **Delete the quality tags.** "8k, ultra-realistic, hyper-detailed, vibrant,
  masterpiece" push *toward* slop. Go the opposite way: "minimal, restrained,
  muted, cinematic grade."
- **One subject, one move, one idea.** Do not stack concepts.
- **Generate three, keep one.** The formula stacks the odds; it does not remove
  variance.
- **Keyframes are the seed.** A clip inherits the look of its start frame, so put
  the *whole* formula into the still prompt first. Cinematic still → cinematic
  clip. Generic still → AI clip, every time.
- **Match the clip to the UI.** Dark clips want a black or near-black page; warm
  clips want cream or dusk; cool nature is flexible. Decide this before you build,
  not after.

## Anti-patterns

| Symptom | Cause → fix |
|---|---|
| Looks fake, over-rendered | "8k, hyper-detailed, vibrant" → delete them, add "muted, cinematic grade" |
| Motion jittery or random | asked for fast, or for two moves → ONE slow move, spelled out |
| Garbled text or logos appear | → add "no on-screen text, no watermarks"; name empty areas rather than banning marks |
| Flat, cheap lighting | no named light → add one ("backlit", "god-rays", "rim light") |
| Generic "AI" subject | abstract subject → swap in a real physical thing in a real place |

---

# The bank

Copy one, swap the subject. **Every prompt below assumes the tail clause** —
append `shallow depth of field, one continuous shot, no cuts, no on-screen text,
no watermarks` to any of them.

## Automotive and motion

1. **Night drive** — Cinematic point-of-view driving down an empty highway at
   night, view through the windshield, glowing street lamps passing and a crescent
   moon, light fog on the glass, dark blue cinematic grade, dashboard softly lit,
   slow steady forward motion, premium car commercial
2. **Coastal dawn drive** — Cinematic low aerial tracking a single car on an empty
   cliffside coastal road at first light, calm ocean below, soft pink-and-gold sky,
   long shadows, warm cinematic grade, slow smooth follow, luxury automotive film
3. **Tunnel of light** — Cinematic first-person drive through a long modern tunnel
   at night, rows of ceiling lights streaking past into motion blur, cool
   teal-and-white grade, reflective wet asphalt, smooth forward glide, premium EV
   commercial
4. **Wet-track braking** — Cinematic low tracking shot alongside a formula car
   braking into a corner on a wet track at dusk, spray kicking off the tyres, brake
   discs glowing hot, reflections on the asphalt, cold blue grade with hot orange
   glow, one smooth follow, premium motorsport film

## Nature and landscape

5. **Valley bridge** — Cinematic slow aerial glide toward an ancient stone arch
   bridge crossing a misty green mountain valley at golden hour, soft god-rays
   through fog, lush forest, warm grade, serene, premium travel film
6. **Island above clouds** — Cinematic slow orbit around a small grassy
   cliff-island floating above a vast golden sea of sunset clouds, a lone tree on
   it, dreamlike, warm volumetric haze, surreal premium
7. **Redwood light** — Cinematic slow push through a towering redwood forest at
   dawn, thick shafts of sunlight cutting through mist between the trunks, deep
   green grade, calm and vast, premium nature film
8. **Aurora lake** — Cinematic still mountain lake at night under a rippling
   green-and-violet aurora, perfect mirror reflection, stars, cold cinematic grade,
   slow drift, premium
9. **Desert dunes** — Cinematic slow aerial over endless golden sand dunes at low
   sun, razor-sharp ridgelines, long soft shadows shifting, warm minimal grade,
   premium expedition film
10. **Powder line** — Cinematic aerial tracking a lone skier carving down an
    untouched powder slope at golden hour, a plume of snow spray backlit by the low
    sun, long blue shadows across the white, crisp cold grade with warm rim light,
    one slow smooth follow, premium ski-resort film
11. **Glass wave** — Cinematic aerial following a lone surfer riding the face of a
    huge glassy turquoise wave, spray peeling off the crest into sunlight, deep
    blue ocean, bright airy grade, one smooth follow, premium surf film
12. **Painted valley** — Cinematic slow aerial over a lush painterly green valley
    with a winding blue river, wildflowers in the grass, soft rolling hills and
    distant hazy blue mountains, bright soft daylight, serene and expansive,
    premium

## Product and luxury

13. **Perfume bottle** — Cinematic macro of a faceted glass perfume bottle slowly
    rotating on black glass, a single soft key light raking across it, amber liquid
    glowing inside, reflections and caustics, luxury fragrance ad, extreme shallow
    depth of field
14. **Watch macro** — Cinematic macro of a luxury automatic watch slowly turning on
    a dark surface, soft studio light gliding over the polished steel case and an
    empty undecorated dial, tiny specular glints, premium horology film
15. **Chrome object** — A single liquid-chrome sculptural form slowly morphing in a
    pitch-black void, mirror reflections of a soft studio softbox sliding across
    it, minimal, premium design-studio render
16. **Sneaker turntable** — Cinematic studio shot of a hero sneaker slowly rotating
    on an invisible turntable, ice-blue rim light and a soft key, faint haze, clean
    gradient backdrop, premium streetwear drop
17. **Origami fold** — Cinematic macro of a single sheet of white paper slowly
    folding itself into a crisp geometric origami crane on a soft grey seamless
    background, gentle rim light catching each crease, minimal and precise, elegant
    slow motion, premium design-studio film

## Abstract texture — calm, premium, very reliable

18. **Ink bloom** — Cinematic macro of a single drop of black ink blooming and
    unfurling in clear water, backlit, soft tendrils, on a white-to-grey gradient,
    elegant slow motion, minimal premium
19. **Silk in wind** — A single sheet of cream silk rippling and folding in slow
    motion on a soft warm-grey background, gentle rim light catching the folds,
    minimal, luxury textile ad
20. **Molten gold** — Cinematic macro of molten gold slowly folding over itself,
    glowing hot core, dark background, embers and shimmer, rich warm grade, premium
    craft film, extreme shallow depth of field

## Architecture and lifestyle

21. **Glass tower dusk** — Cinematic slow aerial rising alongside a single
    minimalist glass skyscraper at golden-hour dusk, warm interior lights flicking
    on, calm clear sky, reflections of clouds in the facade, elegant, premium
    real-estate film
22. **Infinity pool** — Cinematic slow glide across a rooftop infinity pool at dusk
    merging into a city skyline, still water mirroring a warm sky, minimal luxury,
    premium hospitality film
23. **City in the trees** — Cinematic slow aerial over a modern glass-tower skyline
    rising out of a lush green forest with a calm river winding through it, soft
    drifting clouds, warm golden daylight, harmony of city and nature, premium
24. **Sky estate** — Cinematic slow aerial orbit around an ornate multi-tiered
    mansion perched on a floating rock island in a sea of soft pink and lavender
    clouds at dusk, warm windows glowing, dreamlike and ethereal, premium fantasy
    real-estate film

## Technology and the ethereal

25. **Neural flight** — Cinematic macro flight through a vast glowing neural
    network in deep space, luminous nodes and filaments firing electric blue and
    violet, data pulses travelling along threads, volumetric glow, premium AI film
26. **Server aisle** — Cinematic slow tracking shot down an endless dark
    data-centre aisle, rows of servers pulsing with cool blue and cyan indicator
    lights, faint volumetric haze, a reflective floor, cold cinematic grade, steady
    forward glide, premium tech film
27. **Diver descent** — Cinematic wide shot of a lone figure descending slowly into
    deep blue water, a single shaft of sunlight from the surface above, drifting
    particles, silent and vast, cold cinematic grade, premium
28. **Holo globe** — A minimalist holographic globe of thin glowing light-lines
    slowly turning in a dark room, soft particles drifting, faint city-node glows
    on its surface, premium network-tech film
29. **Jellyfish drift** — Cinematic macro drifting among glowing translucent
    jellyfish pulsing in deep dark water, bioluminescent blues and violets, tiny
    drifting particles, serene and weightless, cold ethereal grade, slow float,
    premium biotech film, extreme shallow depth of field
30. **Launch at dawn** — Cinematic wide shot of a sleek white rocket rising off the
    pad at dawn, brilliant orange engine plume and billowing smoke, a calm pastel
    sky, slow majestic vertical climb tracked from below, cool-and-warm cinematic
    grade, premium spaceflight film

## Craft, food and place

31. **Espresso pour** — Cinematic macro of hot espresso streaming into a white
    ceramic cup, crema swirling into a caramel spiral, steam rising through a warm
    shaft of window light, dark moody café backdrop, rich amber grade, slow gentle
    push-in, premium coffee commercial, extreme shallow depth of field
32. **Vineyard rows** — Cinematic slow low aerial gliding over endless rolling
    vineyard rows at golden hour, mist settling in the valley, warm sun raking
    across the vines, a lone stone estate in the distance, rich warm grade, smooth
    forward drift, premium winery film
33. **Barrel cellar** — Cinematic slow glide down a dim underground whiskey cellar,
    rows of oak barrels lit by warm hanging bulbs, soft dust and haze in the air,
    deep amber-and-black grade, steady forward move, premium spirits commercial
34. **Greenhouse push** — Cinematic slow push through a sunlit tropical greenhouse,
    thick green foliage and hanging vines, warm shafts of light and drifting dust
    motes, water droplets on broad leaves, lush verdant grade, gentle forward
    drift, premium wellness film
35. **Temple steps** — Cinematic slow ascent up ancient stone temple steps
    disappearing into thick morning fog, soft god-rays through the mist, stone
    lanterns glowing faintly, muted serene grade, gentle upward drift, premium
    meditative film

## Figure in a landscape — the "deep work" look

Warm screen-light against a huge quiet world. Reliable, and it carries a headline
well because the figure sits low in the frame.

36. **Field of light** — Cinematic wide shot from behind of several seated figures
    in a vast field of glowing golden wildflowers at night, each working on a
    softly glowing laptop, tall stacks of books beside them, beneath an immense
    deep-blue starry sky with the Milky Way arcing overhead, warm laptop glow
    against cool starlight, drifting fireflies, dreamlike and serene, rich
    cinematic grade, slow gentle push-in, premium surreal film
37. **Cliff-island desk** — Cinematic slow push-in toward a small grassy
    cliff-island floating above an endless golden cloud sea at sunset, a lone
    seated figure working on a glowing laptop near a small wooden hut, warm
    god-rays and drifting haze, serene and vast, warm cinematic grade, gentle
    forward drift, premium surreal film

> If a prompt with a person in it gets flagged, "a person" → "a seated figure"
> clears it almost every time. It is a false positive, not a content judgement.
