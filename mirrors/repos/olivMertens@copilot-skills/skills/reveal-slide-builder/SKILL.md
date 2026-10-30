---
name: reveal-slide-builder
title: "Reveal.js Slide Builder — Mastermind Edition"
description: |
  Create world-class, audience-focused presentations with reveal.js through expert guidance on
  animations, transitions, fragments, auto-animate, layouts, accessibility, offline delivery, and PDF export.
  Includes a tested guided diagram walkthrough: an inline architecture SVG or Mermaid flowchart explained
  step by step (zoom on the named components, dim the rest, moving flows on active connectors, failure
  states, evidence cards), with a facilitator script per step in speaker view. Use for "walk through this
  architecture step by step", "animate my diagram part by part", "facilitation per step", "schéma pas à pas".
category: presentation
tags:
  - reveal.js
  - presentation
  - slides
  - html
  - speaker-view
  - animations
  - accessibility
  - offline
triggers:
  - "create a presentation"
  - "build slides"
  - "new reveal.js deck"
  - "plan a talk"
  - "structure slide flow"
  - "narrative arc"
  - "progressive reveal"
  - "animate my slides"
  - "add movement"
  - "animation transitions"
  - "auto-animate elements"
  - "custom fragments"
  - "speaker view"
  - "presenter notes"
  - "offline deck"
  - "PDF export"
  - "accessible presentation"
  - "code walkthroughs"
  - "diagram animations"
  - "reveal.js plugins"
  - "step-by-step architecture walkthrough"
  - "walk through a diagram"
  - "animate an architecture diagram part by part"
  - "guided diagram tour"
  - "facilitation per step"
  - "facilitator script"
  - "schéma pas à pas"
  - "animer un schéma d'architecture"
  - "facilitation par étape"
useCases:
  - Design a new presentation deck
  - Architect slide flow & interactivity
  - Master animations & transitions
  - Leverage reveal.js plugins
  - Build accessible, audience-focused presentations
  - Export for different formats
  - Plan reveal.js special features
  - Master advanced patterns
  - Walk an audience through an architecture or flow diagram, step by step, with a facilitator script
features:
  - Speaker view with notes and timer
  - Auto-animate for smooth transitions between elements
  - Fragments for progressive reveals
  - Guided diagram walkthrough (zoom, dim, moving flows, failure states, per-step notes)
  - PDF export support
  - Offline delivery (file://)
  - Multiple theme options
  - Code highlighting
  - Plugin architecture
  - Accessibility checklist
technologies:
  - HTML/CSS/JavaScript
  - Reveal.js 6.0.2
  - Markdown
  - Mermaid (pre-rendered SVG)
  - Speaker view
  - PDF export
difficulty: intermediate
estimatedTime: 30-60 minutes per deck
---

# Reveal.js Slide Builder — Mastermind Edition

Create world-class, audience-focused presentations with reveal.js through expert guidance on **animations, transitions, fragments, auto-animate, layouts, accessibility, offline delivery, and PDF export**.

## When to Use This Skill

Use this skill whenever you need to:
- **Design a new presentation deck** — "create a presentation", "build slides", "new reveal.js deck", "plan a talk"
- **Architect slide flow & interactivity** — "how should I structure this", "what's the narrative arc", "flow for comparison", "progressive reveal"
- **Master animations & transitions** — "animate my slides", "add movement to", "what animations work for this", "transition between concepts"
- **Leverage reveal.js plugins** — "add interactivity", "enable annotations", "embed live demos", "highlight code", "search across slides"
- **Build accessible, audience-focused presentations** — "tailor to executives", "tech audience", "offline deck", "make it visual"
- **Export for different formats** — "prepare for PDF", "optimize for print", "create presenter notes", "multi-page export"
- **Plan reveal.js special features** — "auto-animate elements", "custom fragments", "iframe backgrounds", "video backgrounds", "background transitions"
- **Master advanced patterns** — "nested fragments", "staggered reveals", "code walkthroughs", "diagram animations", "speaker markup"
- **Walk through a diagram, step by step** — "explain this architecture step by step", "animate the schema part by part", "facilitation per step", "schéma pas à pas" → [Guided Diagram Walkthrough](#guided-diagram-walkthrough--step-by-step-facilitation)

---

## Workflow Overview — Five Phases

The skill follows a structured 5-phase workflow optimized for audience impact:

1. **Audience & Intent Discovery** — Who? Why? What's your outcome?
2. **Content Mapping & Narrative Arc** — Structure, flow, interaction needs
3. **Animation & Plugin Strategy** — Match features to message
4. **Layout, Pacing, & Accessibility** — Visual hierarchy, readability, inclusive design
5. **Implementation & Export** — HTML structure, reveal.js config, PDF & speaker notes

---

# PHASE 1: Audience & Intent Discovery

## Critical Questions (Ask These First)

### 1. **Primary Audience** (Select one or more; tailor recommendations)
- **Executives / C-level** → Focus on outcome, ROI, risk, decision-making speed
- **Technical specialists** → Focus on architecture, internals, tradeoffs, live proof
- **End-users / customers** → Focus on value, simplicity, benefits, confidence
- **Mixed** → Multi-layered content, optional advanced slides, branch logic by role
- **Self-directed viewer** → Assume no speaker; design for clarity without narration

### 2. **Presentation Intent** (What do you want them to do or believe after?)
- **Inform/Educate** — Knowledge transfer, understanding a concept or system
- **Persuade/Sell** — Conviction, urgency, commitment, call-to-action
- **Report/Review** — Facts, metrics, accountability, tracking performance
- **Demonstrate/Explore** — Live interaction, discovery, workshop, problem-solving
- **Inspire/Motivate** — Emotion, vision, narrative arc, journey
- **Hybrid** — Multiple intents at different points; signpost transitions clearly

### 3. **Delivery Context**
- **Live presentation** with speaker (room interaction, pausing, speaker notes, speaker view)
- **Self-guided viewer** (kiosk, online, download, watch alone) → no external dependencies
- **Hybrid** (share online + present live at different times) → works offline AND via link
- **Async recording** (video of you presenting; slides viewed after) → optimize for solo viewing

### 4. **Duration & Pacing**
- **Timeboxed** (e.g., 20-minute pitch, 5-minute teaser) → plan fragments and slide count
- **Self-paced** (viewer controls speed) → more content per slide, progressive reveal
- **Live with Q&A** (speaker controls flow) → leave pauses, design for interruptions
- **Workshop / Interactive** (multiple stops for activities) → embed polls, time-sensitive prompts

### 5. **Key Outcomes** (Rank top 3)
- Understand concept X (knowledge)
- Decide on option Y (choice)
- Take action Z (behavior)
- Remember insight A (retention)
- Feel confidence / emotion B (trust / motivation)

### 6. **Diagrams & Step-by-Step Facilitation** (ask when a slide holds an architecture or flow diagram)
- Will you **explain a diagram step by step** (architecture, request or data flow, process, failure scenario)? → plan a [Guided Diagram Walkthrough](#guided-diagram-walkthrough--step-by-step-facilitation)
- Diagram source: drawio/SVG with stable ids, Mermaid, or an image only (needs a redraw as SVG)?
- Which **single thread** do we follow (one request, order, claim, user)? Any failure path? Evidence screenshots per step?
- **Facilitation:** live presenter or self-guided? A **facilitator script per step** (language, time budget, questions for the room)?

**Action**: After answering these, state your audience & intent in 1–2 sentences so I can tailor everything that follows.

---

# PHASE 2: Content Mapping & Narrative Arc

## Narrative Structures — Choose the One That Fits

### 1. **Problem → Solution → Proof → Call-to-Action**
*Best for: Persuasion, product pitches, change management*
- **Slide 1–2**: Establish the problem (pain, constraint, opportunity cost)
- **Slide 3–4**: Introduce your solution (how it solves the problem)
- **Slide 5–7**: Show proof (case study, metric, demo, customer testimonial)
- **Slide 8**: Call-to-action (next step, commitment, decision point)

### 2. **Current State → Desired State → Path → Commitment**
*Best for: Roadmaps, transformation, strategy*
- **Slide 1–2**: Where we are now (baseline, as-is, constraint)
- **Slide 3–4**: Where we want to be (vision, desired outcome)
- **Slide 5–7**: How we get there (steps, timeline, dependencies, risks)
- **Slide 8–9**: What we commit to (next milestone, resources, accountability)

### 3. **Why → How → What → When**
*Best for: Technical deep dives, system design*
- **Slide 1–2**: Why this matters (motivation, context, urgency)
- **Slide 3–5**: How it works (architecture, mechanism, tradeoffs)
- **Slide 6–7**: What it looks like (code, demo, configuration, interface)
- **Slide 8**: When you can use it (prerequisites, constraints, availability)

### 4. **Hook → Data → Insight → Decision → Action**
*Best for: Reports, analytics, data-driven decisions*
- **Slide 1**: Hook (striking number, unexpected fact, question)
- **Slide 2–4**: Data (charts, metrics, trends, comparisons)
- **Slide 5**: Insight (interpretation, what the data means, why it matters)
- **Slide 6–7**: Decision options (go/no-go, which path, tradeoffs)
- **Slide 8**: Action (next review, monitoring, accountability)

### 5. **Observe → Predict → Control → Act**
*Best for: Demos, live workflows, hands-on learning*
- **Slide 1–2**: Observe (show the current state, walk through a workflow)
- **Slide 3–4**: Predict (annotate, show what happens when, draw hypotheses)
- **Slide 5–6**: Control (demonstrate variables, show options, test edge cases)
- **Slide 7–8**: Act (conclude, make a decision, set next steps)

## Content Mapping Checklist

### Questions to Ask Yourself

1. **Main Message** — One sentence that captures your core idea
   - ✓ *If you could say only ONE thing, what is it?*

2. **Content Density** (average per slide)
   - **Minimal**: Headline + 1 visual (title, opening, transitions)
   - **Light**: 3–5 bullet points + visual (high level, executive)
   - **Moderate**: Comparison table, diagram, 6–8 items (detailed explanation)
   - **Dense**: Code, SQL, API spec, data table (technical audience, optional deep dive)

3. **Interaction Needs**
   - **Read-only** — No interaction needed; audience watches passively
   - **Click-to-reveal** — Progressive disclosure; speaker clicks to reveal next point
   - **Annotate/draw** — Speaker marks up live during presentation (live debate, whiteboarding)
   - **Poll/Q&A** — Audience input during presentation (engagement, feedback)
   - **Embedded live content** — Dashboard, code playground, live feed (requires network if not offline)

4. **Media Mix**
   - **Text-dominant** — Words, quotations, data (reports, policy, academic)
   - **Visual-dominant** — Photos, diagrams, illustrations (design, architecture, brand)
   - **Hybrid** — Balanced text + visuals (most effective for mixed audiences)
   - **Rich media** — Video, animated SVG, embedded widgets (creative, hands-on)

5. **Offline Requirement**
   - **Fully offline** → All assets bundled locally; no CDN, no network fetch; works from `file://`
   - **Online OK** — Can use CDN, network embeds (iframes, live dashboards), videos from YouTube
   - **Hybrid** — Offline by default (`file://`), but supports `?online` mode for live embeds

---

# PHASE 3: Animation & Plugin Strategy

## Animation Philosophy: Match the Message, Not the Mode

**Principle**: Every animation should serve a purpose — guide attention, clarify relationships, emphasize pacing. Avoid motion that distracts or confuses.

---

## Core Animations & When to Use Them

### **Fade** — The Safe Default
```html
<p class="fragment">Fade in</p>
<p class="fragment fade-out">Fade out</p>
```
- **Use for**: Introducing text, subtly revealing points, emphasizing sequence
- **Best audience**: All (executives, technical, end-users)
- **Pacing**: 0.5–0.8s (fast enough to feel active, slow enough to follow)
- **Pro tip**: Combine fade-out on previous point with fade-in on next for "turn the page" feel

---

### **Grow / Shrink** — Changing Importance
```html
<li class="fragment grow">Important point</li>
<li class="fragment shrink">De-emphasized option</li>
```
- **Use for**: Showing hierarchy, moving focus, eliminating alternatives, building a funnel
- **Best audience**: Technical (architects, product), Business (decision makers)
- **Pacing**: 0.6–0.8s (moderate, not too sudden)
- **Pro tip**: Pair with color change (`fragment highlight-red`) to reinforce choice

---

### **Highlight (Color Change)** — Drawing Attention
```html
<p class="fragment highlight-red">Critical issue</p>
<p class="fragment highlight-green">Success metric</p>
<p class="fragment highlight-blue">New feature</p>
```
- **Use for**: Identifying problems (red), successes (green), new info (blue), reversible callouts
- **Best audience**: Business, Technical, End-users
- **Pacing**: Immediate (no delay) or paired with fade-in
- **Pro tip**: Use semantic colors (red=danger, green=success, blue=info) so color is self-explanatory

---

### **Slide Directions** — Spatial Flow
```html
<p class="fragment fade-up">Bottom-to-top entry (positive, building momentum)</p>
<p class="fragment fade-down">Top-to-bottom entry (heavy, serious)</p>
<p class="fragment fade-left">Right-to-left (coming from future, retrospective)</p>
<p class="fragment fade-right">Left-to-right (natural reading, returning)</p>
```
- **Use for**: Directing eye flow, signaling progression (up = growth, down = decline)
- **Best audience**: Visual learners, design-conscious audiences
- **Pacing**: 0.6–0.9s (momentum matters)
- **Pro tip**: Use consistently (all growth slides fade-up, all concerns fade-down) to build muscle memory

---

### **Strike & Semi-Fade** — Invalidation & Uncertainty
```html
<p class="fragment strike">This approach no longer works</p>
<p class="fragment semi-fade-out">Previous assumption (now 50% visible, less important)</p>
<p class="fragment fade-in-then-semi-out">Point made, then de-emphasized for next point</p>
```
- **Use for**: Invalidating assumptions, showing what NOT to do, shifting focus, old vs. new
- **Best audience**: Technical, Business (design thinking, retrospectives)
- **Pacing**: 0.5s (quick, definitive)
- **Pro tip**: Pair strike with new recommendation on same slide for "then we tried this" narrative

---

### **Stagger / Fragment Index** — Controlled Pacing
```html
<ul>
  <li class="fragment" data-fragment-index="1">First (appears on step 1)</li>
  <li class="fragment" data-fragment-index="2">Second (appears on step 2)</li>
  <li class="fragment" data-fragment-index="3">Third (appears on step 3)</li>
</ul>

<!-- Or: same index for simultaneous reveal -->
<p class="fragment" data-fragment-index="1">Title</p>
<img class="fragment" data-fragment-index="1" src="image.png" />
```
- **Use for**: Building lists one-by-one, controlling audience pace, combining elements on same step
- **Best audience**: All (gives speaker control over pacing)
- **Pacing**: 1–2 steps per 30 seconds (readable, not rushed)
- **Pro tip**: For executives, show 1 point per 30 seconds. For technical, 1 point per 15 seconds.

---

### **Current-Visible / Highlight-Current** — Focus + Context
```html
<p class="fragment highlight-current-red">Step 1 (highlighted, then fades to normal color)</p>
<p class="fragment highlight-current-red">Step 2 (highlighted, then fades back)</p>
<p class="fragment highlight-current-red">Step 3 (highlighted, then fades back)</p>
```
- **Use for**: Walking through options, step-by-step guides, "now look here" moments
- **Best audience**: End-users, workshops, tutorials
- **Pacing**: 0.5s highlight, 1s pause before next step
- **Pro tip**: Pairs well with speaker notes ("Notice how X changes…")

---

## Advanced: Nested Fragments — Sequential Effects

Wrap fragments inside fragments to apply multiple animations to the same element.

```html
<!-- Effect 1: Fade in. Effect 2: Turn red. Effect 3: Fade out. -->
<span class="fragment fade-in">
  <span class="fragment highlight-red">
    <span class="fragment fade-out">
      Complex animation sequence
    </span>
  </span>
</span>
```

- **Use for**: Emphasizing then de-emphasizing, building tension, multi-step transformations
- **Best audience**: Creative, design, storytelling-focused
- **Pro tip**: Limit to 2–3 nesting levels; beyond that, it's hard to follow on screen

---

## Advanced: Auto-Animate — Magic Element Transitions

Auto-Animate automatically animates matching elements between adjacent slides. Elements match by:
1. **Text content** (if identical)
2. **Image/video `src`** (if identical)
3. **`data-id` attribute** (explicit matching, takes priority)

### Example 1: Simple Text Movement
```html
<section data-auto-animate>
  <h1>Concept</h1>
</section>

<section data-auto-animate>
  <h1 style="margin-top: 200px; color: red;">Concept</h1>
</section>
```
Result: The `<h1>` smoothly moves down and changes to red.

### Example 2: Adding Elements (Implicit Animation)
```html
<section data-auto-animate>
  <ul>
    <li>Point A</li>
  </ul>
</section>

<section data-auto-animate>
  <ul>
    <li>Point A</li>
    <li>Point B</li>
    <li>Point C</li>
  </ul>
</section>
```
Result: Point A stays in place; Points B and C fade in below.

### Example 3: Explicit Data-ID Matching (for non-text elements)
```html
<section data-auto-animate>
  <div data-id="box" style="width: 100px; height: 100px; background: salmon;"></div>
</section>

<section data-auto-animate>
  <div data-id="box" style="width: 300px; height: 100px; background: steelblue;"></div>
</section>
```
Result: The box smoothly expands horizontally and changes color.

### Example 4: Code Walkthrough (with `data-line-numbers`)
```html
<section data-auto-animate>
  <pre data-id="code"><code data-trim data-line-numbers>
    function add(a, b) {
      return a + b;
    }
  </code></pre>
</section>

<section data-auto-animate>
  <pre data-id="code"><code data-trim data-line-numbers>
    function add(a, b) {
      const sum = a + b;
      console.log(`Sum: ${sum}`);
      return sum;
    }
  </code></pre>
</section>
```
Result: Code smoothly expands to show the new lines.

### Auto-Animate Configuration
```js
Reveal.initialize({
  autoAnimateEasing: 'ease-out',        // CSS easing function
  autoAnimateDuration: 0.8,             // Seconds per animation
  autoAnimateUnmatched: false,          // true = fade in unmatched; false = appear instantly
});
```

### When to Use Auto-Animate
- **Code walkthroughs** — Add variables, error handling, refactoring step-by-step
- **Architecture evolution** — Show system growing from simple to complex
- **Diagram morphing** — Transform one diagram into another (e.g., flat list → tree structure)
- **Data transformation** — Show input → processing → output
- **NOT recommended** for: Fast pacing (auto-animate can feel slow); simple list reveals (fragments are simpler)

**Pro tip**: Combine auto-animate with speaker notes for "As we add error handling..." narration.

---

## Transition Styles — Between Slides

### **Default Transition: Slide**
Slides come in from right by default. Smooth, familiar, low cognitive load.

### **Alternative Transitions**
```html
<section data-transition="fade">Subtle, formal</section>
<section data-transition="zoom">Dramatic, expanding</section>
<section data-transition="convex">3D angle in</section>
<section data-transition="concave">3D angle out (receding)</section>
```

### **Asymmetric Transitions** — Different in/out
```html
<section data-transition="slide-in fade-out">Enter from left, exit with fade</section>
```

### **Transition Speed**
```html
<section data-transition-speed="fast">Snappy (300ms)</section>
<section data-transition-speed="slow">Deliberate (1000ms)</section>
<!-- default: 600ms -->
```

### **Background Transitions** — Separate from slide transition
```html
<section data-background="#ffffff" data-background-transition="slide">
  Slide content transitions in, background transitions separately
</section>
```

### When to Use What
- **Slide (default)**: Most presentations; directional, familiar, fast
- **Fade**: Formal, serious, executive (soft, understated)
- **Zoom**: Dramatic moments, emphasis, crescendos
- **Convex/Concave**: Design-forward, creative audiences (don't overuse)
- **None**: Rapid-fire content, quiz-like pacing (no delay between slides)

**Pro tip**: Vary transitions subtly (3–4 different types across a 40-minute deck) to keep energy up without being distracting.

---

## Plugin Recommendations — Power & Purpose

### **Appearance** (Built-in, always enabled)
Toggles for light/dark theme, serif/sans-serif, and visual adjustments.
```js
Reveal.initialize({
  plugins: [RevealAppearance],
});
```
- **Use for**: Supporting accessibility (dark mode for low-light rooms), brand switching
- **Audience impact**: All (gives viewers choice)
- **Offline**: ✓ Yes (fully self-contained)

---

### **Highlight** (Syntax coloring for code)
```js
Reveal.initialize({
  plugins: [RevealHighlight],
});
```

```html
<!-- With line number ranges (step through code) -->
<pre><code data-trim data-line-numbers="1-3|5-7|9">
  function example() {
    // Lines 1-3 highlighted first
    const x = 1;
    
    // Then lines 5-7
    const y = x + 2;
    return y;
    
    // Then line 9
    console.log(y);
  }
</code></pre>
```

- **Use for**: Code walkthroughs, error analysis, diff comparisons
- **Best audience**: Technical, developers
- **Pro tip**: Syntax highlighting makes code 40% more scannable for audiences

---

### **Chalkboard** (Live speaker markup — offline)
Press **C** to draw, **B** for blackboard, **X/Y** to change colors, **DEL** to clear, **D** to download.

```js
Reveal.initialize({
  plugins: [RevealChalkboard],
});
```

- **Use for**: Live debates, whiteboarding, annotating live during presentation
- **Best audience**: Technical workshops, problem-solving sessions, design critiques
- **Offline**: ✓ Yes (full offline, no server)
- **Pro tip**: Turn off on-screen buttons for offline decks; keyboard-only works fine

---

### **Animate** (SVG & CSS animation)
Animate SVG elements and custom CSS within slides.

```js
Reveal.initialize({
  plugins: [RevealAnimate],
});
```

- **Use for**: Animated diagrams, system flow visualization, custom motion effects
- **Best audience**: Design, technical architecture, creative
- **Offline**: ✓ Yes (if SVG is embedded)
- **Warning**: Heavyweight if you only use 1–2 animations; prefer pure CSS for simple effects

---

### **Search** (Ctrl+F across all slides)
```js
Reveal.initialize({
  plugins: [RevealSearch],
});
```

- **Use for**: Long decks (40+ slides), reference materials, searchable archives
- **Audience impact**: Helpful for self-paced or shared decks
- **Offline**: ✓ Yes (lightweight)

---

### **Zoom** (Alt+click to magnify)
```js
Reveal.initialize({
  plugins: [RevealZoom],
});
```

- **Use for**: Dense diagrams, small text, detailed code, data tables
- **Audience impact**: Accessibility feature; helps those in back of room
- **Offline**: ✓ Yes

---

### **TouchControls** (On-screen control bar for smartboards/mobile)
*Only load when NOT exporting to PDF*

```js
Reveal.initialize({
  plugins: [
    ...(params.has('export') ? [] : [RevealTouchControls()]),
  ],
});
```

- **Use for**: Smartboard presentations, touch-based delivery
- **Offline**: ✓ Yes (but exclude from PDF export)

---

### **Speaker Notes** (Press S for speaker view)
Built-in to reveal.js; Notes plugin displays in popup window.

```html
<section>
  <h1>Slide Title</h1>
  <aside class="notes">
    Speaker: Emphasize the urgency here. Pause for questions.
    Show the live demo at this point.
  </aside>
</section>
```

- **Use for**: Presenter guidance, timing cues, live demo reminders
- **Audience impact**: Invisible to audience; speaker-only
- **Offline**: ✓ Yes (popup window, no external fetch)
- **Pro tip**: Speaker view shows next slide, timer, notes; press S in reveal.js

---

### **Avoid (Not Offline-Compatible)**
- **Reveal Remote** (server-based remote control) ✗
- **PubNub** (real-time sync across devices) ✗
- **Notell** (audience participation service) ✗
- These require external servers → incompatible with offline (`file://`) delivery

---

## Plugin Selection Checklist

| Need | Plugin | Offline? | Notes |
|------|--------|----------|-------|
| Code highlighting | Highlight | ✓ | Essential for tech audiences |
| Live annotation | Chalkboard | ✓ | Keyboard-only (C, B, X, Y, DEL, D) |
| Animated diagrams | Animate | ✓ | For custom SVG motion |
| Search across deck | Search | ✓ | Lightweight, useful for archives |
| Zoom detail | Zoom | ✓ | Alt+click to magnify |
| Smartboard/touch | TouchControls | ✓ | Exclude from PDF export mode |
| Speaker guidance | Notes | ✓ | Press S for popup speaker view |
| Themes/appearance | Appearance | ✓ | Light/dark, serif/sans-serif toggles |
| Step-by-step diagram walkthrough | `assets/diagram-walkthrough.js` (this skill) | ✓ | Inline SVG or Mermaid; per-step notes; see next section |

---

## Guided Diagram Walkthrough — Step-by-Step Facilitation

**Use it** whenever a slide explains an architecture, request, data or process flow, or a failure scenario, and the
user wants it presented part by part or asks for step-by-step facilitation. **Read
[`references/diagram-walkthrough.md`](references/diagram-walkthrough.md) before building**: it has the intake,
markup, id contract, Mermaid recipe, facilitation template and QA checklist. Start from the tested assets:
`assets/diagram-walkthrough.js`, `assets/diagram-walkthrough.css` and `assets/diagram-walkthrough-example.html`
(tested with reveal.js 6.0.2 and Mermaid 12.2).

**What the audience sees.** The whole diagram first, with a hint to press →. Then, at each press:
- one numbered sentence appears under the diagram;
- the view **zooms** smoothly on the components that sentence names;
- the rest **dims**, but the containers holding the focus stay as context;
- dashes **move along the active connectors**;
- failed components turn red with a label;
- an optional evidence screenshot appears beside the diagram.

The last step zooms back out for the recap. In speaker view, the presenter reads **the notes of the current step**.

**How it works.** Each step is a reveal.js fragment (`.dw-step`, `fade-in-then-out`). Its `data-focus` lists diagram
ids. The script listens to `fragmentshown` and `fragmenthidden`, then sets state classes on the inline SVG,
animates its `viewBox` and overlays a dashed flow on the active connectors. It needs no plugin, and
`DiagramWalkthrough.audit()` lists unknown ids.

```html
<section class="dw-slide" data-keep="c-platform">
  <h2>Follow one request through the governed path</h2>
  <div class="dw-stage"><svg class="dw-svg" data-diagram="demo" viewBox="…">…</svg></div>
  <div class="dw-steps r-stack" aria-live="polite">
    <p class="dw-intro">The whole picture first · press <kbd>→</kbd> to follow the flow</p>
    <div class="fragment fade-in-then-out dw-step" data-focus="app gateway agent">
      <span class="n">1</span>Every call goes through the API gateway before it reaches the agent.
      <aside class="notes"><p><b>~40 s · Point at:</b> the gateway. <b>Say:</b> … <b>Ask the room:</b> … <b>Next:</b> …</p></aside>
    </div>
    <div class="fragment fade-in-then-out dw-step" data-focus="gateway agent" data-fail="model">…</div>
    <div class="fragment fade-in dw-step" data-focus=""><span class="n">3</span>Recap: one door, one identity, one trace.</div>
  </div>
  <aside class="notes">Before step 1: name the zones, then the thread we follow.</aside>
</section>
```

**Non-negotiables**
- The SVG is **inline**: `<img>` cannot be driven. Ids follow the contract (`KEY-node`, `KEY-c-container`,
  `KEY-e-connector` with `data-from`/`data-to`). For Mermaid, pre-render to SVG with `htmlLabels: false` and use
  Mermaid's node and subgraph ids.
- Steps are `<div>` elements when they hold `<aside class="notes">` (a `<p>` would be closed before the aside).
- Follow **one thread**: one idea per step, about 20 words at most, 3 to 9 steps, 1 to 5 components each. Consecutive
  steps share a component, so the zoom glides instead of jumping.
- The last step has an empty focus and uses `fade-in`, for the recap.
- **Facilitation:** when asked, write each step's `<aside class="notes">` as timing + point at + say (1 to 3 sentences)
  + optional question for the room + bridge to the next step. Write slide notes for "before step 1", and set
  `data-timing` on the section. Apply the user's own speaker-notes conventions if they have them.
- Respect `prefers-reduced-motion` (handled by the assets). In `?print-pdf` the slide shows the whole diagram and
  lists every step. Localise the hint line and the failure label (`data-fail-label`).

---

# PHASE 4: Layout, Pacing, & Accessibility

## Reveal.js Layout Helpers

### **`r-fit-text`** — Responsive Heading Scaling
Automatically sizes text to fit the slide width without overflow.

```html
<h1 class="r-fit-text">BIG IMPACTFUL HEADLINE</h1>
```

- **Use for**: Title slides, key takeaways, quotes, callouts
- **Pro tip**: Works for multiple lines; pairs well with auto-sizing for dynamic headlines
- **Avoid**: Body text (small fonts become unreadable)

---

### **`r-stretch`** — Fill Remaining Vertical Space
Resizes an element to fill available space after title and footer.

```html
<section>
  <h2>Title</h2>
  <img class="r-stretch" src="diagram.png" alt="Architecture" />
  <small>Image byline</small>
</section>
```

- **Use for**: Full-bleed images, large diagrams, video content
- **Limitation**: Only one per slide section; must be a direct child of `<section>`

---

### **`r-stack`** — Center & Layer Elements
Stack multiple elements on top of each other; use with fragments to reveal one at a time.

```html
<div class="r-stack">
  <img class="fragment fade-out" src="1.png" />
  <img class="fragment current-visible" src="2.png" />
  <img class="fragment" src="3.png" />
</div>
```

Result: Images fade in/out on top of each other (morphing effect).

---

### **`r-frame`** — Border/Highlight Container
Adds a stylized border or frame around an element.

```html
<img class="r-frame" src="logo.png" />
```

- **Use for**: Emphasizing logos, highlighting important visuals, framing focus

---

## Slide Layout Patterns by Content Type

### **Pattern 1: Title Slide**
```html
<section>
  <h1 class="r-fit-text">Your Core Message</h1>
  <p class="subtitle" style="font-size: 1.5em; margin-top: 2rem;">
    Subtitle or tagline
  </p>
  <small style="margin-top: 4rem; color: #999;">
    Speaker Name | Date | Venue
  </small>
</section>
```

- **Animation**: Fade in title, then subtitle (2-step reveal, 0.5s apart)
- **Design**: Vertical center, ample whitespace, 60–72px for title
- **Duration**: Pause 5–10 seconds; let it breathe

---

### **Pattern 2: Content + Image (60/40 Split)**
```html
<section>
  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: center;">
    <div>
      <h2>Title</h2>
      <ul>
        <li class="fragment fade-in-then-semi-out">Point 1</li>
        <li class="fragment fade-in-then-semi-out">Point 2</li>
        <li class="fragment fade-in-then-semi-out">Point 3</li>
      </ul>
    </div>
    <div>
      <img src="image.png" alt="Description" style="width: 100%; height: auto;" />
    </div>
  </div>
</section>
```

- **Animation**: Staggered list (one point per step), image fades in first
- **Design**: Left-to-right reading; 2rem gap; consistent height
- **Pacing**: 1 point per 15–30 seconds depending on audience

---

### **Pattern 3: Comparison / Two-Column**
```html
<section>
  <h2 style="margin-bottom: 2rem;">Option A vs. Option B</h2>
  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 3rem;">
    <div style="padding: 2rem; background: #f0f0f0; border-radius: 8px;">
      <h3>Option A</h3>
      <ul>
        <li class="fragment" data-fragment-index="1">✓ Fast implementation</li>
        <li class="fragment" data-fragment-index="1">✗ Limited scalability</li>
      </ul>
    </div>
    <div style="padding: 2rem; background: #e0e0e0; border-radius: 8px;">
      <h3>Option B</h3>
      <ul>
        <li class="fragment" data-fragment-index="1">✓ Highly scalable</li>
        <li class="fragment" data-fragment-index="1">✗ Longer setup</li>
      </ul>
    </div>
  </div>
  <p class="fragment" data-fragment-index="2" style="margin-top: 2rem; font-size: 1.2em;">
    <strong>Recommendation: Option B (long-term ROI)</strong>
  </p>
</section>
```

- **Animation**: Both columns' points appear together (same index), recommendation appears last
- **Design**: Equal width, distinct backgrounds, clear pro/con labels
- **Pacing**: Pause 30 seconds for digestion, then reveal recommendation

---

### **Pattern 4: Code Walkthrough with Auto-Animate**
```html
<!-- Step 1: Initial code -->
<section data-auto-animate>
  <h2>Error Handling</h2>
  <pre data-id="code"><code data-trim data-line-numbers>
    const data = await fetch(url);
    const result = data.json();
    return result;
  </code></pre>
  <p class="fragment" data-fragment-index="1">Problem: No error handling</p>
</section>

<!-- Step 2: Add try-catch -->
<section data-auto-animate>
  <h2>Error Handling</h2>
  <pre data-id="code"><code data-trim data-line-numbers>
    try {
      const data = await fetch(url);
      const result = data.json();
      return result;
    } catch (error) {
      console.error('Fetch failed:', error);
      return null;
    }
  </code></pre>
  <p class="fragment" data-fragment-index="1">Solution: Wrap in try-catch</p>
</section>
```

- **Animation**: Auto-animate expands code smoothly; fragment shows explanation
- **Design**: Monospace font (16–18px minimum), syntax highlighted, line numbers
- **Pacing**: 20–30 seconds per code step; pause for understanding

---

### **Pattern 5: Quote / Callout**
```html
<section style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
  <blockquote style="font-size: 2rem; text-align: center; color: white; line-height: 1.4;">
    <p>"Impressive is easy. Trusted is hard."</p>
    <small style="font-style: italic; margin-top: 1rem;">— Your Name</small>
  </blockquote>
</section>
```

- **Animation**: Fade in; pause 5–10 seconds for emphasis
- **Design**: High contrast, large serif font (2–3rem), gradient or solid background
- **Use for**: Opening/closing, thematic breaks, memorable takeaways

---

### **Pattern 6: Data Dashboard / Metrics**
```html
<section>
  <h2>Q3 Performance</h2>
  <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-top: 2rem;">
    <div class="fragment" style="text-align: center; padding: 2rem; background: #e3f2fd; border-radius: 8px;">
      <div style="font-size: 3rem; font-weight: bold; color: #1976d2;">42%</div>
      <small style="color: #555;">Growth YoY</small>
    </div>
    <div class="fragment" style="text-align: center; padding: 2rem; background: #f3e5f5; border-radius: 8px;">
      <div style="font-size: 3rem; font-weight: bold; color: #7b1fa2;">$2.3M</div>
      <small style="color: #555;">Revenue</small>
    </div>
    <div class="fragment" style="text-align: center; padding: 2rem; background: #e8f5e9; border-radius: 8px;">
      <div style="font-size: 3rem; font-weight: bold; color: #388e3c;">89%</div>
      <small style="color: #555;">Customer Satisfaction</small>
    </div>
  </div>
</section>
```

- **Animation**: Staggered card reveal (each metric appears separately)
- **Design**: Colored backgrounds, large numbers, minimal text, clear units
- **Pacing**: 1 metric per 10–15 seconds; let numbers sink in

---

## Pacing Strategy by Audience

| Audience | Slides/Min | Content/Slide | Pause | Best Suited For |
|----------|-----------|---------------|-------|-----------------|
| **Executive** | 0.5–0.8 | Minimal (headline + visual) | 30–60s | Decisions, outcomes, next steps |
| **Technical** | 1–1.5 | Moderate (code, diagram, 6–8 bullet points) | 15–30s | Deep dives, architecture, proofs |
| **End-user** | 0.75–1 | Light (3–5 points + visual) | 20–45s | Clarity, benefits, confidence-building |
| **Self-paced** | Variable | Dense (viewer reads at own speed) | N/A | Reference, archive, training material |
| **Workshop** | 0.3–0.5 | Minimal (high interaction) | 2–5 min per activity | Problem-solving, hands-on learning |

---

## Accessibility & Inclusive Design

### **Color Contrast**
- Foreground text: at least **4.5:1 contrast** against background (WCAG AA standard)
- Use a tool like [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- Avoid red-only or green-only coding; always pair with text labels ("✓ Pass" vs. "✗ Fail")

### **Font Size**
- **Minimum 18–24px** for body text (audience in back of room)
- **60–72px** for titles
- **Monospace 14–18px** for code (not smaller; small code becomes unreadable)

### **Dyslexia-Friendly Fonts**
- **Good**: Helvetica, Arial, Segoe UI, Verdana (sans-serif, clear letterforms)
- **Avoid**: Cursive, decorative, thin/light weights
- **Pair serif + sans**: Serif for headings (formality), sans-serif for body (readability)

### **Animation Considerations**
- Avoid rapid flashing (3+ flashes per second) → seizure risk
- Provide `prefers-reduced-motion` support:
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
  }
}
```
- Document any photo-sensitive content (flashing, strobing effects)

### **Audio & Captions**
- Embed **speaker notes** in reveal.js (press S for speaker view)
- If recording a video, include **SRT subtitles** (especially for non-English speakers)
- Transcript available for async viewing

### **Keyboard Navigation**
- Space/Arrow keys to navigate (built-in)
- Alt+click to zoom (built-in)
- Ensure all interactive elements are focusable (Tab key)
- Avoid relying on mouse-only interactions

---

# PHASE 5: Implementation & Export

## Reveal.js Configuration

### **Minimal Setup**
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Your Presentation</title>
  <link rel="stylesheet" href="reveal.js/dist/reveal.css">
  <link rel="stylesheet" href="reveal.js/dist/theme/black.css">
</head>
<body>
  <div class="reveal">
    <div class="slides">
      <section>
        <h1>Your Presentation</h1>
      </section>
      <section>
        <h2>Slide 2</h2>
        <p>Content here</p>
      </section>
    </div>
  </div>
  <script src="reveal.js/dist/reveal.js"></script>
  <script src="reveal.js/dist/plugin/notes/notes.js"></script>
  <script src="reveal.js/dist/plugin/highlight/highlight.js"></script>
  <script>
    Reveal.initialize({
      hash: true,
      transition: 'slide',
      plugins: [RevealNotes, RevealHighlight]
    });
  </script>
</body>
</html>
```

### **Common Configuration Options**
```js
Reveal.initialize({
  // Transitions
  transition: 'slide',                  // fade, slide, convex, concave, zoom
  transitionSpeed: 'default',           // default, fast, slow
  backgroundTransition: 'fade',         // For slide backgrounds

  // Auto-Animate (Added in 4.0.0)
  autoAnimateEasing: 'ease-out',
  autoAnimateDuration: 0.8,
  autoAnimateUnmatched: false,          // false = instant appear for unmatched; true = fade in

  // Presentation Size
  width: 960,
  height: 700,
  margin: 0.1,
  minScale: 0.2,
  maxScale: 2.0,

  // Accessibility & Interaction
  keyboard: true,                       // Arrow keys to navigate
  hash: true,                           // URL hash for deep links (#slide=3,2)
  touch: true,                          // Swipe to navigate on touch devices

  // PDF Export
  showNotes: false,                     // or 'separate-page' to print notes on separate page
  pdfMaxPagesPerSlide: 1,               // Max pages per slide when printing
  pdfSeparateFragments: false,          // false = all fragments on one slide; true = separate pages

  // Plugins
  plugins: [
    RevealNotes,
    RevealHighlight,
    RevealChalkboard,
    RevealSearch,
    RevealZoom
  ]
});
```

---

## PDF Export Best Practices

### **Step 1: Prepare Your Deck**
1. Ensure all content fits on slides (test locally)
2. For fragments, decide: print all states or one state?
   - `pdfSeparateFragments: false` (default) = each fragment step on a separate page (more pages, clearer progression)
   - `pdfSeparateFragments: true` = all fragments visible on one page (fewer pages, but crowded)

### **Step 2: Export to PDF**
1. Open your presentation with `?print-pdf` in URL
   - Example: `file:///C:/path/to/presentation.html?print-pdf`
2. Open browser print dialog (`Ctrl+P` / `Cmd+P`)
3. Set destination: **Save as PDF**
4. Set layout: **Landscape** (revealjs defaults to horizontal)
5. Set margins: **None** (or minimal)
6. Enable: **Background graphics** (colors, gradients, images)
7. Enable: **Headers and footers** if desired (optional)
8. Click **Save**

### **Step 3: Verify PDF**
- Check that all animations are visible (fragments as separate pages)
- Check colors and backgrounds rendered correctly
- Check speaker notes (if enabled; they appear as overlay text)
- Check page count matches expectations

### **Troubleshooting PDF Export**
| Issue | Cause | Solution |
|-------|-------|----------|
| Slides not fitting page | Margins too large | Set margins to None |
| Background colors missing | "Background graphics" unchecked | Enable in print dialog |
| Fragments stacked on one page | `pdfSeparateFragments: false` | Set to `true` if you want separate pages per fragment |
| Speaker notes cluttering PDF | `showNotes: true` | Set to `false` or `'separate-page'` |
| Text too small to read | Slide margins taking up space | Set `margin: 0.05` in config |

---

## Markdown Support (External Files)

If you prefer to write slides in Markdown instead of HTML:

```html
<section data-markdown>
  <textarea data-template>
    ## Slide Title
    
    - Point 1
    - Point 2
    
    ---
    
    ## Next Slide
    
    Different content here
  </textarea>
</section>
```

### External Markdown File
```html
<section data-markdown="slides.md" data-separator="^\n---\n$"></section>
```

### Markdown Attributes (via HTML comments)
```html
<section data-markdown>
  <textarea data-template>
    <!-- .slide: data-background="#ff0000" -->
    ## Red Background Slide
    
    - Item <!-- .element: class="fragment highlight-red" -->
    - Another item <!-- .element: data-fragment-index="2" -->
  </textarea>
</section>
```

---

## Embedding Media

### **Background Video**
```html
<section data-background-video="video.mp4" data-background-video-loop data-background-video-muted>
  <h1>Video Background</h1>
</section>
```

### **Background Image**
```html
<section data-background-image="image.jpg" data-background-size="cover" data-background-position="center">
  <h1>Image Background</h1>
</section>
```

### **Background Iframe** (Interactive)
```html
<section data-background-iframe="https://example.com" data-background-interactive>
  <h1>Embedded Website</h1>
</section>
```
*Note: `data-background-interactive` allows mouse/keyboard to interact with the iframe but disables slide interaction.*

### **Video Inline**
```html
<section>
  <video width="640" height="480" controls>
    <source src="video.mp4" type="video/mp4">
  </video>
</section>
```

---

## Offline Delivery Checklist

✓ All assets (images, videos, fonts, plugin JS/CSS) are local files
✓ No CDN links (no `https://cdn.jsdelivr.net/…`)
✓ No remote iframes (use data-background-iframe only for `?online` mode)
✓ Test opening via `file://` in browser (no server needed)
✓ Verify with `Ctrl+Shift+I` → Network tab (zero remote requests)
✓ Plugin remotes (Highlight, Chalkboard, Notes) work offline by default
✓ Plugins like TouchControls excluded from PDF export mode

---

## Speaker View & Notes

### **Using Speaker View**
1. Open presentation
2. Press **S** (capital S)
3. Speaker view opens in new popup window showing:
   - Current slide
   - Next slide
   - Speaker notes
   - Timer / clock

### **Adding Speaker Notes**
```html
<section>
  <h1>Slide Title</h1>
  
  <aside class="notes">
    Speaker guidance here. Emphasize this point.
    Pause for questions. Live demo at this step.
  </aside>
</section>
```

### **Including Notes in PDF**
```js
Reveal.initialize({
  showNotes: true,          // Overlay notes on slides
  // OR
  showNotes: 'separate-page' // Print notes on separate pages after each slide
});
```

---

## Advanced: Custom CSS & Styling

### **Override Slide Dimensions**
```css
.reveal .slides {
  width: 100%;
  height: 100%;
}

.reveal .slides > section {
  min-height: 100%;
}
```

### **Custom Fragment Animation**
```css
.fragment.custom-pulse {
  opacity: 1;
}

.fragment.custom-pulse.visible {
  animation: pulse 1s ease-in-out;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}
```

### **Dark Mode Override**
```css
.reveal {
  background: #1e1e1e;
  color: #f0f0f0;
}

.reveal h1, .reveal h2, .reveal h3 {
  color: #fff;
}

.reveal pre {
  background: #2d2d2d;
  border: 1px solid #555;
}
```

---

# Quick Reference: Reveal.js Feature Matrix

| Feature | Built-in? | Config Required? | Offline? | Best For |
|---------|-----------|------------------|----------|----------|
| **Slide Transitions** | ✓ | ✗ (defaults work) | ✓ | All presentations |
| **Fragments** | ✓ | ✗ | ✓ | Progressive reveal |
| **Auto-Animate** | ✓ | ✓ (in config) | ✓ | Code/diagram morphing |
| **Markdown** | Plugin | ✓ | ✓ | If you prefer .md syntax |
| **Syntax Highlight** | Plugin | ✓ | ✓ | Code-heavy talks |
| **Chalkboard** | Plugin | ✓ | ✓ | Live annotation |
| **Speaker Notes** | Plugin | ✗ | ✓ | Presenter guidance |
| **Search** | Plugin | ✓ | ✓ | Long decks |
| **Zoom** | Plugin | ✓ | ✓ | Detail inspection |
| **PDF Export** | ✓ | ✓ (for notes) | ✓ | Offline reference |
| **Appearance Switcher** | Built-in | ✗ | ✓ | Theme toggling |
| **Touch Controls** | Plugin | ✓ | ✓ | Smartboards (exclude from PDF) |

---

# Workflow Checklist — From Idea to Delivery

### Phase 1: Discovery ✓
- [ ] Identify primary audience
- [ ] Define intent (inform, persuade, report, demonstrate, inspire)
- [ ] Establish delivery context (live, self-paced, hybrid)
- [ ] Set duration and pacing expectations
- [ ] List top 3 key outcomes

### Phase 2: Content Mapping ✓
- [ ] Choose narrative arc (Problem→Solution, Current→Desired, Why→How, Hook→Data, Observe→Control)
- [ ] Write main message (1 sentence)
- [ ] Estimate slides needed and content density per slide
- [ ] Identify interaction needs (read-only, click-to-reveal, annotate, poll)
- [ ] Decide media mix (text, visual, hybrid, rich media)

### Phase 3: Animation & Plugins ✓
- [ ] Select 3–5 animation types (fade, grow, highlight, slide direction, stagger)
- [ ] Plan auto-animate sequences (if applicable)
- [ ] Choose transition style (slide, fade, zoom, etc.)
- [ ] Select plugins (Highlight, Chalkboard, Search, etc.)
- [ ] Verify all plugins are offline-compatible (if needed)

### Phase 4: Layout & Pacing ✓
- [ ] Design 2–3 slide layout templates (title, content+image, comparison, code, quote, metrics)
- [ ] Set pacing guidelines per audience (0.5–1.5 slides/min)
- [ ] Audit color contrast (4.5:1 minimum)
- [ ] Verify font sizes (18px+ body, 60px+ titles)
- [ ] Check accessibility (no rapid flashing, keyboard navigable, captions if video)

### Phase 5: Implementation & Export ✓
- [ ] Create HTML structure with plugins
- [ ] Test locally (open via `file://`, no external requests)
- [ ] Add speaker notes for each slide
- [ ] Test PDF export with proper settings
- [ ] Verify offline delivery (no CDN, no remote iframes)
- [ ] Do final accessibility pass (contrast, font, keyboard nav, color blindness)

---

# Common Pitfalls & How to Avoid Them

### **Pitfall 1: Animation Overload**
*Symptom*: Every slide has 5+ animations; audience gets dizzy; message is lost.
*Fix*: Limit to 1–2 animations per slide. Each animation should serve the message.

### **Pitfall 2: Dense Text Slides**
*Symptom*: Audience reads instead of listens; cognitive overload.
*Fix*: Minimal text (3–5 bullet points max). Use visuals to carry meaning.

### **Pitfall 3: Inconsistent Pacing**
*Symptom*: First 10 slides in 5 minutes; last 10 slides in 30 minutes.
*Fix*: Plan slides-per-minute upfront; rehearse to match.

### **Pitfall 4: No Offline Fallback**
*Symptom*: WiFi drops mid-presentation; deck becomes unviewable.
*Fix*: Bundle all assets locally; test opening via `file://`; avoid remote iframes.

### **Pitfall 5: Unreadable Code**
*Symptom*: 8pt monospace code; audience can't read it from the back.
*Fix*: Minimum 14–18px for code; use syntax highlighting; highlight key lines only.

### **Pitfall 6: No Speaker Notes**
*Symptom*: Presenter fumbles, loses timing, forgets key talking points.
*Fix*: Add notes to every complex slide; include timing, demos, Q&A cues.

### **Pitfall 7: Accessible to Some, Not All**
*Symptom*: Red/green colors only (red-blind can't distinguish); text too small; rapid flashing.
*Fix*: Audit contrast, font size, color pairs (pair red+green with ✓/✗ or labels).

---

# Expert Tips — Level Up Your Presentations

### **Tip 1: Use Data-IDs for Precise Auto-Animate**
Don't rely on text content matching. Explicit `data-id` is more predictable:
```html
<div data-id="metric" style="font-size: 2rem;">42%</div>
<!-- Next slide -->
<div data-id="metric" style="font-size: 3rem; color: red;">42%</div>
```

### **Tip 2: Stagger Lists with Fragment Index**
Control the order and timing:
```html
<li class="fragment" data-fragment-index="1">First</li>
<li class="fragment" data-fragment-index="2">Second</li>
```
Or simultaneous reveal (same index):
```html
<h2 class="fragment" data-fragment-index="1">Title</h2>
<img class="fragment" data-fragment-index="1" src="image.png" />
```

### **Tip 3: Combine Fragments for Multi-Step Effects**
```html
<span class="fragment fade-in">
  <span class="fragment highlight-red">
    <span class="fragment fade-out">
      Step-by-step transformation
    </span>
  </span>
</span>
```

### **Tip 4: Use Speaker Notes as a Script**
Write exactly what you'll say. Helps with:
- Consistent messaging across multiple presentations
- Training new speakers
- Sharing presentation material without over-explaining on slides

### **Tip 5: Test PDF Export Early**
Export to PDF early in your design process:
1. Opens with `?print-pdf` in URL
2. Print to PDF with correct settings (landscape, no margins, background graphics)
3. Verify fragment handling and page count
   - If fragments create too many pages, adjust `pdfSeparateFragments`

### **Tip 6: Use R-Fit-Text for Impact**
Let titles scale responsively instead of hard-coding font sizes:
```html
<h1 class="r-fit-text">BIG HEADLINE THAT SCALES</h1>
```
Works for multi-line text too.

### **Tip 7: Pair Auto-Animate with Fragments**
Auto-Animate handles element morphing; Fragments handle step-by-step reveals.
Combine them for sophisticated slide transitions:
```html
<section data-auto-animate>
  <code data-id="code">const x = 1;</code>
  <p class="fragment">Step 1</p>
</section>

<section data-auto-animate>
  <code data-id="code">const x = 1; const y = 2;</code>
  <p class="fragment">Step 1</p>
  <p class="fragment">Step 2</p>
</section>
```

### **Tip 8: Preload Iframes for Smooth Transitions**
If using iframes, preload them so they're ready:
```html
<section data-preload data-background-iframe="https://example.com">
  <h1>Embedded Site</h1>
</section>
```

### **Tip 9: Use Gradient Backgrounds for Visual Interest**
```html
<section data-background-gradient="linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
  <h1 style="color: white;">Striking section break</h1>
</section>
```

### **Tip 10: Leverage Speaker View for Multi-Monitor Setup**
Press **S** to open speaker view in popup (separate monitor):
- Shows current + next slide
- Displays speaker notes
- Includes timer
- Ideal for two-monitor setup (presenter view on laptop, slides on projector)

---

# Reference Templates

## Minimal Reveal.js Template with Speaker View

Use this as a starting point for any deck:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Presentation Title</title>
    <link rel="stylesheet" href="reveal.js/dist/reveal.css">
    <link rel="stylesheet" href="reveal.js/dist/theme/black.css">
    <style>
        .reveal h1, .reveal h2, .reveal h3 { text-transform: none; }
        .speaker-notes { font-size: 1.2em; }
    </style>
</head>
<body>
    <div class="reveal">
        <div class="slides">
            <!-- Slide 1: Title -->
            <section>
                <h1>Presentation Title</h1>
                <p>Subtitle or tagline</p>
                <aside class="notes">
                    This is your speaker note for slide 1.
                    It appears only in speaker view (press S).
                    Use it to remember talking points, transitions, or timing.
                </aside>
            </section>

            <!-- Slide 2: Content with fragments -->
            <section>
                <h2>Main Concept</h2>
                <ul>
                    <li class="fragment">First point</li>
                    <li class="fragment">Second point</li>
                    <li class="fragment">Third point</li>
                </ul>
                <aside class="notes">
                    Elaborate on each point. Fragments advance one per click.
                </aside>
            </section>

            <!-- Slide 3: Two-column layout -->
            <section>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div>
                        <h3>Left Column</h3>
                        <p>Content here</p>
                    </div>
                    <div>
                        <h3>Right Column</h3>
                        <p>Content here</p>
                    </div>
                </div>
            </section>
        </div>
    </div>

    <script src="reveal.js/dist/reveal.js"></script>
    <script src="reveal.js/plugin/notes/notes.js"></script>
    <script>
        Reveal.initialize({
            hash: true,
            slideNumber: true,
            transition: 'slide',
            plugins: [ RevealNotes ]
        });
    </script>
</body>
</html>
```

**To use speaker view:**
- Open in browser
- Press **S** to open speaker view in a new window
- Drag the new window to your presenter monitor
- First monitor shows current + next slide + notes
- Projector shows only the current slide

---

## Microsoft Fluent Design Template

Professional style with Fluent Design principles (clean, accessible, modern):

```html
<head>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
            background: #f5f5f5;
        }
        
        .reveal {
            font-family: 'Segoe UI', sans-serif;
        }
        
        .reveal h1, .reveal h2, .reveal h3 {
            font-weight: 300;
            letter-spacing: -0.02em;
        }
        
        .reveal section {
            padding: 60px !important;
        }
        
        /* Microsoft brand colors (no personal info) */
        .section-blue { background: linear-gradient(135deg, #0078d4 0%, #1084d7 100%); }
        .section-teal { background: linear-gradient(135deg, #00a4a4 0%, #00b9b9 100%); }
        .section-accent { background: linear-gradient(135deg, #e74c3c 0%, #e67e22 100%); }
        
        .reveal section h1 { font-size: 3.5em; margin: 0; }
        .reveal section h2 { font-size: 2.2em; }
        .reveal section p { font-size: 1.2em; line-height: 1.6; }
        
        .metric-box {
            display: inline-block;
            background: rgba(0, 120, 212, 0.1);
            border-left: 4px solid #0078d4;
            padding: 20px 30px;
            margin: 10px;
            border-radius: 2px;
        }
        
        .metric-box .number {
            font-size: 2.5em;
            font-weight: 300;
            color: #0078d4;
        }
        
        .metric-box .label {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }
    </style>
</head>

<body>
    <!-- Title Slide -->
    <section class="section-blue" style="color: white;">
        <h1>Presentation Topic</h1>
        <p style="font-size: 1.5em; margin-top: 40px; opacity: 0.9;">
            Short description or tagline
        </p>
    </section>

    <!-- Content Slide with Metrics -->
    <section>
        <h2>Key Results</h2>
        <div style="margin-top: 60px;">
            <div class="metric-box">
                <div class="number">42%</div>
                <div class="label">Improvement</div>
            </div>
            <div class="metric-box">
                <div class="number">3x</div>
                <div class="label">Faster</div>
            </div>
            <div class="metric-box">
                <div class="number">98%</div>
                <div class="label">Satisfaction</div>
            </div>
        </div>
    </section>

    <!-- Accent Section -->
    <section class="section-accent" style="color: white;">
        <h2>Key Takeaway</h2>
        <p style="font-size: 1.4em; margin-top: 40px;">
            Main message or call-to-action
        </p>
    </section>
</body>
```

---

## Auto-Animate Code Walkthrough Template

Template for demonstrating code with progressive reveal:

```html
<section>
    <h2>Code Evolution</h2>
    
    <!-- Step 1: Basic function -->
    <section data-auto-animate>
        <pre data-id="code"><code class="language-javascript">
function processData(items) {
    return items;
}
        </code></pre>
        <aside class="notes">
            Start with a simple skeleton.
        </aside>
    </section>

    <!-- Step 2: Add logic -->
    <section data-auto-animate>
        <pre data-id="code"><code class="language-javascript">
function processData(items) {
    return items
        .filter(item => item.active)
        .map(item => item.value);
}
        </code></pre>
        <aside class="notes">
            Filter and transform. The code position animates smoothly.
        </aside>
    </section>

    <!-- Step 3: Add error handling -->
    <section data-auto-animate>
        <pre data-id="code"><code class="language-javascript">
function processData(items) {
    if (!items || items.length === 0) return [];
    
    return items
        .filter(item => item.active)
        .map(item => item.value)
        .catch(error => console.error(error));
}
        </code></pre>
        <aside class="notes">
            Add validation and error handling.
        </aside>
    </section>
</section>
```

**Usage:**
- Each `<section data-auto-animate>` animates smoothly from one to the next
- Elements with `data-id="code"` animate position/size automatically
- Perfect for showing code iterations, design refinements, or algorithm steps

---

## Comparison Layout Template (Two-Column)

```html
<section>
    <h2>Approach Comparison</h2>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 40px; margin-top: 50px;">
        
        <!-- Left column -->
        <div style="text-align: left;">
            <h3 style="color: #0078d4; border-bottom: 3px solid #0078d4; padding-bottom: 10px;">
                Option A
            </h3>
            <ul style="margin-top: 30px; font-size: 0.9em; line-height: 1.8;">
                <li class="fragment">✓ Benefit 1</li>
                <li class="fragment">✓ Benefit 2</li>
                <li class="fragment">✗ Drawback 1</li>
                <li class="fragment">Best for: Use case X</li>
            </ul>
        </div>
        
        <!-- Right column -->
        <div style="text-align: left;">
            <h3 style="color: #e74c3c; border-bottom: 3px solid #e74c3c; padding-bottom: 10px;">
                Option B
            </h3>
            <ul style="margin-top: 30px; font-size: 0.9em; line-height: 1.8;">
                <li class="fragment">✓ Benefit 3</li>
                <li class="fragment">✓ Benefit 4</li>
                <li class="fragment">✗ Drawback 2</li>
                <li class="fragment">Best for: Use case Y</li>
            </ul>
        </div>
    </div>
</section>
```

---

## Accessibility Checklist Template

```html
<section style="text-align: left;">
    <h2>Accessibility Verification</h2>
    <ul style="font-size: 1.1em; line-height: 2; margin-top: 40px;">
        <li>☐ Color contrast ≥ 4.5:1 (WCAG AA)</li>
        <li>☐ Font size ≥ 18px body, ≥ 60px titles</li>
        <li>☐ Dyslexia-friendly font (Segoe UI, Open Sans, or similar)</li>
        <li>☐ Alt text for all images</li>
        <li>☐ Keyboard navigation tested (arrow keys, space, enter)</li>
        <li>☐ No motion auto-play; prefers-reduced-motion respected</li>
        <li>☐ Slide notes for all transitions</li>
        <li>☐ Tested with screen reader</li>
    </ul>
    <aside class="notes">
        Run through this checklist before final delivery.
    </aside>
</section>
```

---

# Decision Tree — Quick Guidance

```
START: What are you building?

0. Does a slide explain an architecture, request/data flow or failure scenario?
   → YES: Guided Diagram Walkthrough (inline SVG or Mermaid, one step per press, per-step facilitator notes)
   → Also go to 1

1. Is it a code-heavy talk?
   → YES: Use Highlight plugin, plan code walkthrough with auto-animate
   → NO: Go to 2

2. Do you need live annotation?
   → YES: Enable Chalkboard plugin (keyboard: C=draw, B=board, X=color, DEL=clear)
   → NO: Go to 3

3. Is it a long deck (40+ slides)?
   → YES: Add Search plugin (Ctrl+F to find)
   → NO: Go to 4

4. Will you present live with speaker notes?
   → YES: Add Notes plugin (press S for speaker view)
   → NO: Go to 5

5. Do you need PDF export?
   → YES: Configure showNotes, test with ?print-pdf, adjust margins
   → NO: Go to 6

6. Will it be viewed offline?
   → YES: Bundle all assets locally, verify file:// access, zero external requests
   → NO: You can use CDN plugins and remote iframes

DONE: Implement, test, rehearse.
```

---

# Final Checklist Before Presenting

- [ ] **Rehearse** — Practice in front of audience or mirror; time yourself
- [ ] **Test offline** — Open presentation via `file://` (no server); verify all assets load
- [ ] **Speaker notes** — Review all speaker notes; mark timing and demo cues
- [ ] **PDF backup** — Export to PDF (in case tech fails); have printed copy in pocket
- [ ] **Video/Demo** — If using live demo, have screen recording backup
- [ ] **Accessibility** — Test keyboard navigation (Tab, Arrow keys), zoom (Alt+click), contrast
- [ ] **Browser** — Use Chrome/Chromium (most reliable); test zoom level (100%)
- [ ] **Projector** — Test connection; display resolution; font readability from back of room
- [ ] **Audio** — If video/audio embedded, test speakers; have captions available
- [ ] **Contingency** — Backup plan if WiFi fails, projector dies, speaker can't attend

---

# Resources & Further Reading

- **Official Reveal.js Docs**: https://revealjs.com/
- **Reveal.js Demo**: https://revealjs.com/demo/
- **Markdown Guide**: https://revealjs.com/markdown/
- **Auto-Animate**: https://revealjs.com/auto-animate/
- **Fragments & Animations**: https://revealjs.com/fragments/
- **PDF Export**: https://revealjs.com/pdf-export/
- **Accessibility**: https://www.w3.org/WAI/tutorials/presentations/
- **Color Contrast Checker**: https://webaim.org/resources/contrastchecker/

---

**You're now equipped to build world-class presentations with reveal.js. Start with Phase 1 (audience discovery), follow the workflow, and refer back to this skill as needed. Good luck! 🎯**

#### Executive / Business Audience
- **Goal**: Clarity, pace, emphasis on key numbers
- **Recommended animations**:
  - Fade in (subtle, professional)
  - Slide in from left/right (directional flow)
  - Highlight / scale pulse (draw attention to metrics)
  - Staggered list reveal (one point at a time, controlled pacing)
  - Grow / shrink (show/hide alternatives)
- **Avoid**: Spinning, bouncing, strobe, or playful effects (distract from message)
- **Best plugins**: Appearance (polished), Highlight (code if needed)

#### Technical / Developer Audience
- **Goal**: Detail, precision, traceability, live interaction
- **Recommended animations**:
  - Fade (neutral, lets content speak)
  - Grow (reveal complexity incrementally)
  - Code syntax highlight (show errors/solutions step-by-step)
  - Diagram animation (trace architecture, flow)
  - Speaker annotations (draw on live code/diagram)
- **Avoid**: Cartoon-like effects, oversimplification
- **Best plugins**: Highlight (syntax coloring), Chalkboard (live markup), Appearance
- **Consider**: Embed live demos, code playgrounds, vs. slides

#### Creative / Design Audience
- **Goal**: Inspiration, emotion, narrative flow
- **Recommended animations**:
  - Fade, slide, scale (smooth transitions)
  - Custom CSS animations (personality, brand)
  - Video backdrop (cinematic)
  - Animated SVG diagrams (show relationships, process)
  - Interactive elements (hover, click to explore)
- **Avoid**: Overuse; keep hierarchy clear
- **Best plugins**: Animate (SVG motion), Appearance (themes), custom CSS

#### End-User / Customer Audience
- **Goal**: Engagement, clarity, comfort
- **Recommended animations**:
  - Gentle fade / zoom (familiar, welcoming)
  - Progressive reveal of benefits (build confidence)
  - Interactive polls / click-through (participation)
  - Whitespace + breathing room (not cluttered)
  - Consistent timing (predictable, not jarring)
- **Avoid**: Rapid flashing, overwhelming motion
- **Best plugins**: Appearance (accessible themes), TouchControls (mobile-friendly)

---

### Plugin Recommendations by Use Case

| Plugin | Best For | Audience | Notes |
|--------|----------|----------|-------|
| **Appearance** | General styling, themes | All | Built-in, no config. Provides dark/light/serif/sans-serif toggles. Always include. |
| **Highlight** | Code syntax coloring | Tech, Dev | Integrates highlight.js. Show errors, diffs, traces. Use `data-line` to step through code. |
| **Chalkboard** | Live speaker markup | Tech, Sales, Design | Draw on slides in real-time (C=draw, B=board, X=color, D=download). Keyboard only; turn off UI buttons for offline. |
| **Animate** | SVG & CSS animation | Design, Creative | Animate SVG paths, transitions. Requires custom SVG + CSS. Heavyweight if used lightly. |
| **TouchControls** | Mobile, smartboard | Any | On-screen control bar (pen, present, timer, overview). Exclude from `?export` (PDF export mode). |
| **Search** | Find text across slides | Any | Ctrl+F to search. Lightweight. Useful for long decks. |
| **Zoom** | Detail inspection | Tech, Data | Alt+click to zoom into a region. Helpful for dense diagrams, small text. |
| **Math** | Equations, formulas | Academic, Research, Finance | KaTeX or MathJax rendering. Lightweight. Use `$$...$$` or `` `\(...\)` ``. |
| **Speaker Notes** | Speaker view | Presenter | Built-in via Notes plugin. Press S to open speaker view in popup. Offline; no external server. |

### Plugin Patterns for Offline Delivery

- **Always inline**: Appearance, Highlight, Speaker Notes (no external fetch)
- **Conditionally load**: TouchControls (exclude from `?export` mode to prevent PDF clutter)
- **Niche plugins**: Wrap in `...(window.RevealX ? [RevealX()] : [])` so missing globals don't break boot
- **Avoid**: Reveal Remote, PubNub, notell (require relay server → breaks offline guarantee)

---

## Phase 4: Layout & Pacing Recommendations

### Slide Layouts by Content Type

#### Title Slide
```html
<section>
  <h1>Main Message</h1>
  <p class="subtitle">Context or tagline</p>
  <small>Speaker name | Date | Venue</small>
</section>
```
- **Animation**: Fade in for title, then subtitle (2-step reveal)
- **Spacing**: Vertical center, ample whitespace
- **Design**: Large type (60-72px), strong contrast

#### Content + Image
```html
<section>
  <div style="display: flex; gap: 2rem;">
    <div style="flex: 1;">
      <h2>Title</h2>
      <ul>
        <li class="fragment fade-in-then-semi-out">Point 1</li>
        <li class="fragment fade-in-then-semi-out">Point 2</li>
      </ul>
    </div>
    <div style="flex: 1;">
      <img src="image.png" alt="Description" />
    </div>
  </div>
</section>
```
- **Animation**: Staggered list + image (fade-in-then-semi-out grays previous points)
- **Spacing**: 2rem gap, 1:1 ratio or 60/40 split
- **Design**: Left text, right visual (left-to-right reading)

#### Comparison / Two-Column
```html
<section>
  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
    <div>
      <h3>Option A</h3>
      <ul>
        <li>✓ Benefit 1</li>
        <li>✗ Cost 1</li>
      </ul>
    </div>
    <div>
      <h3>Option B</h3>
      <ul>
        <li>✓ Benefit 2</li>
        <li>✗ Cost 2</li>
      </ul>
    </div>
  </div>
</section>
```
- **Animation**: Reveal each column separately (build decision process)
- **Spacing**: Equal columns, 2rem gap
- **Design**: Consistent styling per column, clear labels

#### Code / Technical Detail
```html
<section>
  <h2>How It Works</h2>
  <pre><code data-line="5-7|9-11" data-trim>
    function example() {
      // Step 1
      const data = fetch(url);
      
      // Highlighted first
      const result = process(data);
      return result;
      
      // Then this part
      console.log(result);
    }
  </code></pre>
</section>
```
- **Animation**: `data-line="5-7|9-11"` steps through code sections
- **Spacing**: Monospace font, syntax highlight, visible line numbers
- **Design**: Dark background for readability, increase font size (16-18px minimum)

#### Quote / Callout
```html
<section style="background: linear-gradient(135deg, #f5f5f5, #e0e0e0);">
  <blockquote style="font-size: 2.5rem; text-align: center;">
    <p>"The hard part isn't writing code—it's reviewing and releasing it safely."</p>
    <small>— Your speaker</small>
  </blockquote>
</section>
```
- **Animation**: Fade in, pause for emphasis
- **Spacing**: Large type, centered, ample padding
- **Design**: High contrast background, serif font for formality (optional)

#### Data / Dashboard
```html
<section>
  <h2>Q3 Metrics</h2>
  <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem;">
    <div class="fragment" style="text-align: center; padding: 1rem; border: 2px solid #0066cc;">
      <div style="font-size: 3rem; font-weight: bold;">42%</div>
      <small>Growth YoY</small>
    </div>
    <!-- repeat for other metrics -->
  </div>
</section>
```
- **Animation**: Staggered reveal of metric cards
- **Spacing**: Grid layout, 1.5rem gaps, consistent card size
- **Design**: Numerical hierarchy (large numbers, small labels), border or background for emphasis

### Pacing Strategy

| Audience | Slides Per Minute | Notes |
|----------|-------------------|-------|
| Executive | 0.5–1 | Plenty of time to digest, pause for Q&A |
| Technical | 1–1.5 | Code, diagrams need time; skip verbose bullet points |
| End-user | 0.75–1.25 | Balanced: not too fast, not too slow |
| Self-paced | N/A | Viewer controls (no time pressure) |

---

## Phase 5: Design & Accessibility

### Color Palette Strategy

#### Brand-Agnostic, Accessible Foundation

**Neutral Base** (background + text):
- Light: Off-white (#f8f8f8, #fafafa) or white (#ffffff)
- Dark: Near-black (#1a1a1a, #222222) or true dark gray (#2c2c2c)
- Text on light: #1a1a1a or #2c2c2c (contrast ratio ≥ 7:1)
- Text on dark: #f8f8f8 or #ffffff (contrast ratio ≥ 7:1)

**Accent Colors** (call-to-action, emphasis, hierarchy):
- Primary accent: #0066cc (mid-blue, high contrast on light/dark)
- Success: #0d8659 (teal-green, WCAG AA)
- Warning: #d97706 (amber, not pure yellow)
- Critical: #cc0000 (red, reserved for errors only)

**Usage**:
- Headings: Primary accent or text color
- Links: Primary accent + underline
- Highlights: Accent color with semi-transparent background `rgba(0, 102, 204, 0.1)`
- Data viz: Use colorblind-safe palette (blue, orange, gray)

### Typography

| Use | Font | Size (px) | Weight | Notes |
|-----|------|-----------|--------|-------|
| Headings (h1, h2) | Sans-serif (Barlow, Source Sans Pro, System) | 48–72 | 600–700 (bold) | Hierarchy, strong contrast |
| Body text | Sans-serif (Barlow, Source Sans Pro, System) | 24–32 | 400 (regular) | Readable at distance (~8ft for 1080p) |
| Small text (labels, captions) | Sans-serif | 14–18 | 400 | Only for secondary info; avoid tiny text |
| Code / monospace | Courier New, Monaco, Fira Code | 16–20 | 400 | Syntax highlight for readability |
| Quotes / emphasis | Serif (Garamond, Georgia) or sans-serif italic | 28–36 | 400 italic | Visually distinct from body |

### Spacing & Whitespace

- **Slide padding**: 3–5% of slide width on all sides (build breathing room)
- **Vertical rhythm**: 1.5–2x line height for body text (24–32px for 16px base)
- **Between elements**: Use consistent gaps (0.5rem, 1rem, 1.5rem, 2rem)
- **List indentation**: 1.5rem per level
- **Content width**: Max 90% of slide width; center content

### Contrast Checklist

- [ ] Headings vs. background: contrast ratio ≥ 7:1 (WCAG AAA)
- [ ] Body text vs. background: contrast ratio ≥ 4.5:1 (WCAG AA)
- [ ] Data labels vs. chart background: ratio ≥ 4.5:1
- [ ] Interactive elements (buttons, links): visible focus indicator (outline, underline, or color change)
- [ ] Color-only coding: Never use color alone to convey info; add icons, text, or patterns

### Accessibility Best Practices

1. **Alt text for images**: `<img src="..." alt="Specific, descriptive text" />`
2. **Semantic HTML**: Use `<h2>`, `<h3>` (not `<div>` + CSS) for structure
3. **Keyboard navigation**: Ensure all interactive elements (buttons, links) are keyboard-accessible
4. **Focus indicators**: Default blue outline or custom style visible at ≥ 3:1 contrast
5. **Screen reader support**: Use `aria-label`, `aria-describedby` for complex diagrams
6. **Captions & transcripts**: For video and audio content
7. **Readable fonts**: Avoid decorative fonts for body text; use sans-serif for screen readability

---

## Phase 6: Implementation & Code Examples

### Basic Reveal.js Setup

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Presentation Title</title>
  <link rel="stylesheet" href="reveal.js/dist/reveal.css" />
  <link rel="stylesheet" href="assets/deck-theme.css" />
</head>
<body>
  <div class="reveal">
    <div class="slides">
      <!-- Slides go here -->
    </div>
  </div>
  <script src="reveal.js/dist/reveal.js"></script>
  <script src="assets/deck-behavior.js"></script>
</body>
</html>
```

### Fragment Animations (Progressive Reveal)

```html
<!-- Fade in -->
<li class="fragment fade-in">Point 1</li>

<!-- Fade in, then semi-transparent (previous points gray out) -->
<li class="fragment fade-in-then-semi-out">Point 2</li>

<!-- Grow (scale up with fade) -->
<li class="fragment grow">Point 3</li>

<!-- Highlight (blink color or background) -->
<span class="fragment highlight-red">Important</span>

<!-- Stagger: reveal order (step 1, step 2, ...) -->
<li class="fragment" data-fragment-index="1">First</li>
<li class="fragment" data-fragment-index="2">Second</li>
<li class="fragment" data-fragment-index="3">Third</li>
```

### Speaker Notes

```html
<section>
  <h2>Slide Title</h2>
  <p>Slide content</p>
  <aside class="notes">
    - Emphasize key insight here
    - Pause for questions
    - Transition to next topic with: "Now, let's explore..."
  </aside>
</section>
```

Press **S** to open speaker view (popup with notes + timer).

### Lightbox for Images / Videos

```html
<!-- Image preview -->
<img src="thumbnail.png" data-preview-image="full.png" alt="Description" />

<!-- Video preview (click to play in fullscreen) -->
<img src="poster.png" data-preview-video="https://example.com/video.mp4" alt="Video" />
```

### Code Highlighting with Line Steps

```html
<pre><code data-line="2,4|6-8|10">
  function calculate(x) {
    const step1 = x * 2;      // Line 2 highlighted first
    
    const step2 = step1 + 1;  // Line 4 highlighted next
    
    // Then lines 6-8
    if (step2 > 10) {
      return step2;
    }
    console.log(step2);       // Finally line 10
  }
</code></pre>
```

Press spacebar to advance through `data-line` groups.

---

## Design System Recommendations by Audience

### Executive Deck
```css
/* Professional, minimal, high-contrast */
.reveal {
  --color-bg: #ffffff;
  --color-text: #1a1a1a;
  --color-accent: #0066cc;
  --font-main: "Source Sans Pro", sans-serif;
  font-size: 28px;
}
.reveal h2 { color: var(--color-accent); font-size: 56px; }
.reveal li { margin-bottom: 1rem; }
```

### Technical Deck
```css
/* Dark mode, syntax-friendly, code-forward */
.reveal {
  --color-bg: #1a1a1a;
  --color-text: #f8f8f8;
  --color-accent: #00d4ff;
  --font-main: "Source Sans Pro", sans-serif;
  font-size: 24px;
}
.reveal pre { background: #0d1117; padding: 1.5rem; }
.reveal code { color: #58a6ff; }
```

### Creative Deck
```css
/* Bold, dynamic, visual-first */
.reveal {
  --color-bg: linear-gradient(135deg, #f5f5f5, #e8e8e8);
  --color-text: #1a1a1a;
  --color-accent: #ff6b6b;
  --font-main: "Barlow", sans-serif;
  font-size: 32px;
}
.reveal section { text-align: center; }
.reveal img { max-width: 90%; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
```

---

## Quick Decision Tree

Use this flowchart to quickly recommend animations and plugins:

```
START: "What's your primary audience?"

├─ EXECUTIVE
│  ├─ Animation: Fade, Slide (directional), Scale (for emphasis)
│  ├─ Plugins: Appearance, Highlight (if code)
│  └─ Layout: Minimal text, large numbers, one idea per slide
│
├─ TECHNICAL
│  ├─ Animation: Fade, Code line-step (data-line), Diagram trace
│  ├─ Plugins: Highlight (syntax), Chalkboard (live markup), Zoom
│  └─ Layout: Code blocks, architecture diagrams, detailed captions
│
├─ CREATIVE / DESIGN
│  ├─ Animation: Fade, Scale, SVG motion (Animate plugin), CSS custom
│  ├─ Plugins: Animate, Appearance, custom CSS
│  └─ Layout: Visual-dominant, asymmetric, whitespace emphasis
│
└─ END-USER / CUSTOMER
   ├─ Animation: Gentle fade, Zoom, Progressive reveal
   ├─ Plugins: TouchControls, Appearance (accessible theme)
   └─ Layout: Centered, large type, ample breathing room
```

---

## File Structure for a Reveal Deck

```
my-presentation/
├── index.html               # Main deck
├── assets/
│   ├── deck-theme.css       # Custom styles
│   ├── deck-behavior.js     # Boot + plugin config
│   ├── diagram-walkthrough.css  # Step-by-step diagrams (from this skill's assets/)
│   ├── diagram-walkthrough.js   # Load after Reveal.initialize()
│   ├── fonts/               # Local fonts (Barlow, Source Sans Pro)
│   ├── icons/               # SVG icons (Lucide or custom)
│   ├── images/              # Presentation images
│   ├── diagrams/            # Mermaid or SVG diagrams
│   ├── video/               # Video files + subtitles (*.srt)
│   └── vendor/
│       ├── appearance/      # appearance.js, appearance.css
│       ├── plugins/         # chalkboard, highlight, animate, etc.
│       └── reveal.js/       # reveal.js library (dist/)
├── qa/                      # Quality assurance scripts
│   ├── verify-decks.cjs     # Check offline, remoteRequests, structure
│   ├── export-presentations.cjs  # Generate PPTX
│   └── package-offline.cjs  # Bundle for offline ZIP
└── README.md                # Deck documentation
```

---

## Validation Checklist

Before finalizing your deck, confirm:

- [ ] **Offline ready**: No remote CDN fetches; all assets local (`remoteRequests === 0`)
- [ ] **Animations purposeful**: Each animation supports the message (not gratuitous)
- [ ] **Plugin load**: All plugins in `deck-behavior.js` `plugins:[]` array; optional plugins wrapped in `...(window.X ? [X()] : [])`)
- [ ] **Accessibility**: Contrast ≥ 4.5:1, alt text for images, semantic HTML, keyboard navigation
- [ ] **Pacing**: Slide count / speaker duration matches intended pace (e.g., 20 slides ÷ 20 min = 1 slide/min)
- [ ] **Speaker notes**: Key talking points in `<aside class="notes">` for each slide
- [ ] **Diagram walkthroughs** (if any): `DiagramWalkthrough.audit()` returns `[]`; every step frames what it names; stepping back restores the whole diagram; reduced motion, `?print-pdf` and per-step speaker notes checked (see `references/diagram-walkthrough.md`)
- [ ] **Export readiness**: TouchControls excluded from `?export` mode (PDF export)
- [ ] **Tested on target device**: Preview on projector, mobile, or intended viewing context

---

---

## Presenter Slide Setup

If your deck includes a **title slide with presenter credentials** (speaker intro slide), gather this information upfront:

### Presenter Slide Questions

1. **Presenter Photo**
   - Do you have a headshot or profile photo? (JPG, PNG recommended)
   - Preferred size/format (square, circular crop, full-body?)
   - Permission/rights confirmed?

2. **Branding Elements**
   - Include Microsoft logo? (If yes, which variant: full logo, icon-only, or monochrome?)
   - Company/organization logo? (If yes, provide file)
   - Logo placement (top-left, top-right, bottom, centered?)

3. **Interactive Elements**
   - Generate LinkedIn QR code / flashcode linking to your profile?
   - If yes, provide LinkedIn URL
   - Position on slide (bottom-right, bottom-left, or separate QR slide?)
   - Display URL text or QR only?

4. **Presenter Notes Generation**
   - Do you want speaker notes auto-generated? (Yes/No)
   - If yes, what **language** for speaker notes?
     - English
     - French (Français)
     - Spanish (Español)
     - German (Deutsch)
     - Other (specify)
   - What **scope** should notes cover?
     - Key talking points only (bullets, 1–2 lines per slide)
     - Full narration (complete sentences, natural speech rhythm)
     - Timing cues (pause points, how long to dwell on each slide)
     - Q&A prompts (suggested audience questions + answers)
     - Transitions (bridge language between slides)

### Presenter Slide HTML Template

```html
<section id="presenter-slide">
  <div class="presenter-grid">
    <!-- Photo -->
    <img src="assets/images/presenter-photo.jpg" alt="Your Name" class="presenter-photo" />
    
    <!-- Credentials -->
    <div class="presenter-info">
      <h2>Your Name</h2>
      <p>Title / Role</p>
      <p>Company / Organization</p>
      
      <!-- LinkedIn QR -->
      <img src="assets/images/linkedin-qr.png" alt="LinkedIn QR Code" class="qr-code" />
      <p class="qr-label">linkedin.com/in/yourprofile</p>
    </div>
    
    <!-- Logos -->
    <div class="logos">
      <img src="assets/images/microsoft-logo.svg" alt="Microsoft" class="logo" />
      <img src="assets/images/company-logo.svg" alt="Company" class="logo" />
    </div>
  </div>
  
  <aside class="notes">
    Welcome everyone. I'm [Name], [title]. Today we'll explore [topic].
    Pause here to let people settle in.
  </aside>
</section>
```

### Presenter Slide CSS Starter

```css
#presenter-slide {
  background: linear-gradient(135deg, #ffffff, #f5f5f5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.presenter-grid {
  display: grid;
  grid-template-columns: 1fr 1.5fr 1fr;
  gap: 2rem;
  align-items: center;
  max-width: 90%;
}

.presenter-photo {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #0066cc;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.presenter-info h2 {
  font-size: 48px;
  margin: 0 0 0.5rem 0;
  color: #1a1a1a;
}

.presenter-info p {
  font-size: 24px;
  margin: 0.5rem 0;
  color: #555555;
}

.qr-code {
  width: 120px;
  height: 120px;
  margin-top: 1rem;
  border: 1px solid #ccc;
}

.qr-label {
  font-size: 14px;
  color: #999;
  margin-top: 0.5rem;
}

.logos {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  justify-self: center;
}

.logos .logo {
  height: 60px;
  width: auto;
  object-fit: contain;
}
```

---

## Resources

- **Reveal.js Docs**: https://revealjs.com/
- **Reveal.js Plugins & Tools**: https://github.com/hakimel/reveal.js/wiki/Plugins,-Tools-and-Hardware
- **Rajgoel Reveal.js Plugins** (Chalkboard, Animate, Appearance): https://github.com/rajgoel/reveal.js-plugins
- **Accessibility (WCAG 2.1)**: https://www.w3.org/WAI/WCAG21/quickref/
- **Colorblind-Safe Palettes**: https://colorblindok.com/
- **Typography for Presentations**: https://www.typewolf.com/
- **Icon Libraries**: Lucide, Feather, Material Design Icons (all available as SVG)
- **QR Code Generators**: https://www.qr-code-generator.com/ (SVG export for integration)

---

## When to Hand Off

Delegate specific implementation to other skills:

- **Slide creation**: Use `new-topic` or `add-node` for Copilot Studio; adapt for reveal.js HTML
- **Animation fine-tuning**: Reference reveal.js docs for fragment types and timing
- **Plugin debugging**: Check plugin repo (GitHub) for known issues and configuration
- **PPTX export**: Use your build script (e.g., `export-presentations.cjs`) or reveal.js `?print-pdf`
- **Offline verification**: Run `qa/verify-decks.cjs` to confirm zero remote requests

