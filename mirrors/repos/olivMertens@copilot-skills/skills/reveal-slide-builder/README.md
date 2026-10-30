# Reveal.js Slide Builder Skill

An interactive skill for creating engaging, accessible presentations with reveal.js through structured guidance on animations, plugins, layouts, and design patterns.

## Overview

This skill helps you design and build reveal.js presentations by asking targeted questions about:

- **Audience** — Who will see your presentation (executives, technical specialists, designers, end-users)
- **Intent** — What you want the audience to do (learn, decide, take action)
- **Content structure** — Narrative arc, interaction points, media mix
- **Animations** — Frame-appropriate transitions and progressive reveals
- **Plugins** — Recommended reveal.js plugins matched to use case
- **Layout patterns** — Slide structures (title, comparison, code, data, quotes)
- **Design & accessibility** — Color, typography, spacing, contrast, WCAG compliance

## Use Cases

✅ Design a new presentation deck from scratch  
✅ Choose animations and transitions for your slides  
✅ Select plugins (Highlight, Chalkboard, Animate, etc.)  
✅ Plan slide layouts and reveal sequencing  
✅ Build accessible, audience-focused presentations  
✅ Choose brand-agnostic colors and typography  
✅ Walk an audience through an architecture or flow diagram, step by step, with a facilitator script  

## Quick Start

Invoke the skill when you need to:

- "Create a presentation for executives"
- "Build slides for a technical deep-dive"
- "Design animated slides for a design conference"
- "What animations work best for my audience?"
- "Which reveal.js plugins should I use?"
- "Walk the room through this architecture diagram step by step, with facilitator notes"

## Key Features

### Guided Diagram Walkthrough (step-by-step facilitation)

The whole diagram first, then one step per key press:

- the view zooms on the components named by the step, and dims the rest;
- dashes move along the active connectors;
- failed components turn red with a label;
- an optional evidence screenshot appears beside the diagram;
- the last step is a recap of the whole picture.

The speaker view shows the facilitator notes of the current step. The walkthrough works with an inline SVG that
follows a simple id contract, or with a pre-rendered Mermaid flowchart. It respects reduced motion and exports to
PDF as the full diagram plus the numbered list of steps. Tested with reveal.js 6.0.2 and Mermaid 12.2.

See [`references/diagram-walkthrough.md`](references/diagram-walkthrough.md) and the working example in `assets/`.

### 6-Phase Workflow

1. **Audience & Intent Discovery** — Understanding and persona gathering
2. **Content Map** — Narrative structure and interaction points
3. **Animation & Plugin Recommendations** — Tailored suggestions by audience type
4. **Layout & Pacing Strategy** — Slide structures and timing guidelines
5. **Design & Accessibility** — Color palettes, typography, spacing, contrast
6. **Implementation** — HTML structure, code examples, validation checklist

### Animation Patterns by Audience

- **Executive**: Fade, Slide (directional), Scale (emphasis on metrics)
- **Technical**: Fade, Code line-by-line (data-line), guided diagram walkthrough (zoom, dim, moving flows)
- **Creative**: SVG animation, smooth transitions, custom CSS
- **End-user**: Gentle fades, progressive reveals, whitespace emphasis

### Plugin Recommendations

| Plugin | Best For | Audience |
|--------|----------|----------|
| Appearance | General styling, themes | All |
| Highlight | Code syntax coloring | Tech, Dev |
| Chalkboard | Live speaker markup | Tech, Sales, Design |
| Animate | SVG & CSS animation | Design, Creative |
| TouchControls | Mobile, smartboard | Any |

### Design System Foundation

- **Brand-agnostic, accessible color palettes** — High contrast, colorblind-safe
- **Typography guidance** — Sans-serif for body, serif for emphasis
- **Spacing & whitespace** — Consistent gaps, breathing room
- **Accessibility checklist** — WCAG AA/AAA compliance, alt text, keyboard navigation

### Code Examples

- Basic reveal.js setup
- Fragment animations (progressive reveal)
- Speaker notes
- Lightbox for images/videos
- Code highlighting with line steps
- Design system CSS snippets

### Decision Tree

Quick reference for choosing animations and plugins based on audience and use case.

## Files Included

- **SKILL.md** — Full skill documentation with all workflows, recommendations, and examples
- **references/diagram-walkthrough.md** — Step-by-step diagram walkthrough: intake, markup, id contract, Mermaid recipe, facilitation template, QA
- **assets/diagram-walkthrough.js / .css** — Drop-in script and styles (no plugin dependency)
- **assets/diagram-walkthrough-example.html** — Working 7-step example with a failure step, a recap and per-step facilitator notes

## Resources

- [Reveal.js Documentation](https://revealjs.com/)
- [Reveal.js Plugins & Tools](https://github.com/hakimel/reveal.js/wiki/Plugins,-Tools-and-Hardware)
- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [Colorblind-Safe Palettes](https://colorblindok.com/)

## Integration

This skill works standalone or alongside:
- reveal.js HTML deck authoring
- Copilot Studio topic design
- Presentation authoring workflows

## Notes

- All recommendations are **brand-agnostic** and grounded in accessibility best practices
- The skill emphasizes **offline-first design** (no CDN dependencies, local assets)
- Animations are chosen for **clarity and purpose**, not gratuitous visual effects
