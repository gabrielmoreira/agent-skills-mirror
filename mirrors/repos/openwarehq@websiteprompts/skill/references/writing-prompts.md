# Writing the prompt back out

Once a site is built and verified, distil it into **one block someone else can
paste to regenerate it from nothing.** Every prompt in this repo's `prompts/`
folder was produced this way. Read one alongside this file — the shape will be
obvious in thirty seconds.

The test is simple and it is not negotiable:

> Hand the block to a fresh model with no access to your code. Does it produce
> the site? If it produces *something in the general vicinity*, the prompt is a
> description, not a spec, and it has failed.

---

## What a build prompt is

**It is a specification, not a summary.** The single most common failure is
writing what the page *feels like* — "a moody hero with elegant type" — instead of
what it *is*. A model will happily fill any gap you leave, and it fills it with
defaults. Defaults are exactly what make a page look generated.

So: exact hex values, exact Tailwind classes, exact durations in milliseconds,
exact easing, exact z-index order, exact gradient stops with their percentages.
Anywhere you were tempted to write "subtle", write the number.

**Write down why, for anything counter-intuitive.** Whoever reads it — human or
model — will otherwise "clean up" the strange-looking part, and the strange-looking
part is usually the one you spent an hour on. "Push the video right because the
subject renders dead centre, exactly where the headline runs" survives editing.
"translate-x-[11%]" alone does not.

**Include the mistakes.** Every gotcha you hit belongs in the prompt: the Tailwind
class that lost to the cascade, the property that clobbered centring, the swap that
had to happen after the dissolve rather than on `ended`. These read like noise and
they are the highest-value lines in the file — they are the difference between a
first pass that works and a first pass that needs debugging.

**Host the video and inline the URL.** A prompt that says "add a background video"
is not reproducible. The clip must be at a public URL, written into the block, so
the page works the moment it is generated with nothing to download.

---

## The section order

Not every site needs every section, but this order has been stable across 50+
prompts, and it is roughly the order a model wants to build in.

```
<one opening sentence: what to build, in what stack, and its overall shape>

BACKGROUND VIDEO:          what the footage shows, then the URL, then how it is
                           positioned (z-index, 100vw/100svh, object-cover)

THE LOOP MUST NOT HARD-CUT — THIS IS THE MOST IMPORTANT PART:
                           the crossfade player, spelled out step by step

REFRAMING THE SUBJECT:     scale/translate on the video, and why

SCRIM:                     exact gradient stops, and that it is legibility not decoration

TYPOGRAPHY:                faces, where they load from, sizes per breakpoint, tracking

COLOURS:                   every hex used on the page

NAV:                       structure, contents, and any special treatment

HERO CONTENT:              the exact copy, element by element

ENTRANCE:                  keyframes, durations, stagger delays

REDUCED MOTION:            what happens under prefers-reduced-motion

TEXT DIET:                 what NOT to add
```

**`TEXT DIET` is not optional and goes last.** Without it, models append feature
grids, testimonials, pricing tables and three paragraphs of filler — and a
cinematic hero with a feature grid under it is no longer a cinematic hero. Name the
things you do not want: "no feature grids, no testimonials, no spec tables, no
paragraphs."

**The loop paragraph is the one people delete.** It reads like boilerplate, it is
invisible in a screenshot, and it is the single detail that separates an expensive
hero from a cheap one. Keep it, and label it as the most important part so it
survives.

---

## The file around the block

```markdown
# <Name>

![<Name>](../screenshots/<slug>.webp)

**<Kind>** · <Category>

Paste the whole block below into Claude Code, Cursor, v0 — anything that writes
code. The video is already hosted, so the URL works as-is; nothing to download.

---

```
<the prompt>
```

---

<footer line>
```

- **A screenshot is mandatory.** Nobody reads a prompt to find out what it makes.
  Capture at 1512×860 with the harness, convert to webp.
- **One fenced block**, so the whole thing is one copy. Never split it across
  several blocks or interleave commentary — people copy the first block and stop.
- **Say "paste the whole block".** The second most common failure mode is someone
  pasting the half that looked interesting.

---

## Checklist before publishing one

- [ ] The video URL is public, and you fetched it in a clean shell to prove it
- [ ] Every colour appears as a hex, not a name
- [ ] Every duration has a number and a unit
- [ ] The loop section is present and labelled as the most important part
- [ ] Every gotcha you hit during the build is written down, with its reason
- [ ] `TEXT DIET` names what not to add
- [ ] The screenshot matches what the block currently produces
- [ ] You generated it once from the block alone, in a clean directory, and looked
      at the result
