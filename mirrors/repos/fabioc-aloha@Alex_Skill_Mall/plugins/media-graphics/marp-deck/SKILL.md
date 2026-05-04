---
type: skill
lifecycle: stable
inheritance: inheritable
name: build-deck
description: Convert a Marp Markdown file to HTML, PDF, or PowerPoint using marp-cli. Use when asked to "build slides", "export presentation", "convert to PDF", "generate PPTX", "marp build", or "export deck". ...
tier: standard
applyTo: '**/*marp*,**/*presentation*,**/*slide*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Build Deck

Convert a Marp Markdown file into a polished presentation in HTML, PDF, PPTX, or image format using `marp-cli`.

## When to Use

- User asks to "build", "export", or "convert" a Marp deck
- User wants a PDF, PPTX, or HTML from their Markdown slides
- User says "generate slides", "export to PowerPoint", "make PDF"

---
type: skill
lifecycle: stable
inheritance: inheritable
name: marp-deck-skill-1
description: Skill from marp-deck plugin
tier: standard
applyTo: '**/*marp*,**/*presentation*,**/*slide*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Advanced Options

### Watch Mode (Live Preview)
```powershell
marp -w slides.md
```
Rebuilds automatically on save. Great for iterating.

### Server Mode (Browser Preview)
```powershell
marp -s .
```
Serves all `.md` files in the directory with live reload.

### Batch Conversion
```powershell
# All .md files in a directory → PDF
marp -I ./slides/ --pdf
```

### Custom Theme
```powershell
# Single theme file
marp slides.md --theme ./my-theme.css --pdf

# Theme directory
marp slides.md --theme-set ./themes/ --pdf
```

---
type: skill
lifecycle: stable
inheritance: inheritable
name: marp-deck-skill-2
description: Skill from marp-deck plugin
tier: standard
applyTo: '**/*marp*,**/*presentation*,**/*slide*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

---
type: skill
lifecycle: stable
inheritance: inheritable
name: create-deck
description: Generate a Marp Markdown presentation from a topic, outline, or codebase analysis. Use when asked to "create a presentation", "make slides", "generate a deck", "presentation from code", "slides abo...
tier: standard
applyTo: '**/*marp*,**/*presentation*,**/*slide*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Create Deck

Generate a complete Marp Markdown presentation deck from a topic, outline, or codebase.

## When to Use

- User asks to "create a presentation", "make slides", "build a deck"
- User wants a technical presentation derived from their codebase
- User provides a topic, outline, or bullet points and wants a structured deck
- User says "slides about X" or "presentation from this repo"

---
type: skill
lifecycle: stable
inheritance: inheritable
name: marp-deck-skill-4
description: Skill from marp-deck plugin
tier: standard
applyTo: '**/*marp*,**/*presentation*,**/*slide*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Slide Generation Rules

### Frontmatter
Always include valid Marp frontmatter:

```yaml
---
type: skill
lifecycle: stable
inheritance: inheritable
name: marp-deck-skill-5
description: Skill from marp-deck plugin
tier: standard
applyTo: '**/*marp*,**/*presentation*,**/*slide*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---
```

Suggest `gaia` theme for bold/keynote style, `uncover` for minimal, `default` for general.

### Slide Structure Guidelines

1. **Title slide** — Use `<!-- _class: lead -->` with title, subtitle, author, date
2. **Agenda/Overview** — 3-5 bullet points of what's covered
3. **Content slides** — One idea per slide, 3-6 bullet points max
4. **Code slides** — Use fenced code blocks with language specifiers
5. **Diagram slides** — Use Mermaid or describe the diagram for the user to add
6. **Image slides** — Use `![bg right:40%]()` for split layouts with placeholder paths
7. **Summary slide** — Key takeaways
8. **Closing slide** — Thank you / Q&A / contact info

### Content Quality Rules

- **One idea per slide** — if a slide has two topics, split it
- **6x6 rule** — max 6 bullets, max 6 words per bullet (guideline, not strict)
- **Progressive disclosure** — build complexity gradually
- **Mix layouts** — alternate between text, code, images, and split slides
- **Add speaker notes** — use `<!-- Speaker note text -->` after slide content
- **Use headings** — every slide should have an `h1` or `h2`

### Code Slides Best Practices

- Show only relevant code snippets (10-20 lines max)
- Add comments highlighting the key parts
- Use `<!-- _class: lead -->` before a code slide for context
- For codebase presentations, use actual code from the repo

### Technical Presentation Patterns

For codebase-driven decks, use these slide patterns:

```markdown
<!-- _class: lead -->
# Architecture Overview
How the system fits together

---
type: skill
lifecycle: stable
inheritance: inheritable
name: marp-deck-skill-6
description: Skill from marp-deck plugin
tier: standard
applyTo: '**/*marp*,**/*presentation*,**/*slide*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Key Module: Authentication

```typescript
// src/auth/middleware.ts
export function authenticate(req, res, next) {
  const token = req.headers.authorization;
  // ... actual code from repo
}
```

<!-- Authentication middleware validates JWT tokens and attaches user context -->
```

---
type: skill
lifecycle: stable
inheritance: inheritable
name: marp-deck-skill-7
description: Skill from marp-deck plugin
tier: standard
applyTo: '**/*marp*,**/*presentation*,**/*slide*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Reference

Read `references/marp-syntax.md` for the full Marp Markdown syntax reference when generating slides.


---
type: skill
lifecycle: stable
inheritance: inheritable
name: review-deck
description: Review a Marp Markdown presentation for content quality, structure, syntax correctness, and accessibility. Use when asked to "review slides", "check my presentation", "improve my deck", "review dec...
tier: standard
applyTo: '**/*marp*,**/*presentation*,**/*slide*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Review Deck

Review an existing Marp Markdown presentation and provide actionable feedback on content quality, structure, Marp syntax, visual variety, and accessibility.

## When to Use

- User asks to "review my slides", "check my presentation"
- User wants feedback on an existing Marp deck
- User says "improve my deck", "what's wrong with my slides"
- Before final export, to catch issues

---
type: skill
lifecycle: stable
inheritance: inheritable
name: marp-deck-skill-9
description: Skill from marp-deck plugin
tier: standard
applyTo: '**/*marp*,**/*presentation*,**/*slide*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Reference

Read `references/marp-syntax.md` for the Marp Markdown syntax reference when validating syntax.


---
type: skill
lifecycle: stable
inheritance: inheritable
name: theme-deck
description: Apply or customize Marp themes for presentations. Use when asked to "theme my slides", "customize presentation style", "create a custom theme", "change deck colors", "marp theme", or "style my pres...
tier: standard
applyTo: '**/*marp*,**/*presentation*,**/*slide*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

# Theme Deck

Apply built-in Marp themes, generate custom CSS themes, or customize the visual styling of a Marp presentation.

## When to Use

- User asks to "theme my slides", "change the look of my deck"
- User wants custom colors, fonts, or layouts
- User says "create a custom theme", "make it look professional"
- User wants brand-aligned styling (corporate colors, fonts)
- User asks about available themes

---
type: skill
lifecycle: stable
inheritance: inheritable
name: marp-deck-skill-11
description: Skill from marp-deck plugin
tier: standard
applyTo: '**/*marp*,**/*presentation*,**/*slide*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---
marp: true
theme: default
style: |
  section {
    background-color: #1a1a2e;
    color: #eaeaea;
    font-family: 'Segoe UI', sans-serif;
  }
  h1, h2, h3 {
    color: #0078d4;
  }
  code {
    background: #2d2d2d;
    color: #d4d4d4;
  }
  a {
    color: #00bcf2;
  }
---
type: skill
lifecycle: stable
inheritance: inheritable
name: marp-deck-skill-12
description: Skill from marp-deck plugin
tier: standard
applyTo: '**/*marp*,**/*presentation*,**/*slide*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---
marp: true
theme: custom-theme
---
type: skill
lifecycle: stable
inheritance: inheritable
name: marp-deck-skill-13
description: Skill from marp-deck plugin
tier: standard
applyTo: '**/*marp*,**/*presentation*,**/*slide*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---
marp: true
theme: custom-theme
paginate: true
---
type: skill
lifecycle: stable
inheritance: inheritable
name: marp-deck-skill-14
description: Skill from marp-deck plugin
tier: standard
applyTo: '**/*marp*,**/*presentation*,**/*slide*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Regular Content
- Bullet point one
- Bullet point two
- **Bold text** and *italic text*

> A blockquote for emphasis

---
type: skill
lifecycle: stable
inheritance: inheritable
name: marp-deck-skill-15
description: Skill from marp-deck plugin
tier: standard
applyTo: '**/*marp*,**/*presentation*,**/*slide*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

<!-- _class: invert -->
## Dark Slide
Testing the inverted color scheme
```

Build with: `marp test-theme.md --theme ./theme-custom.css --html`

---
type: skill
lifecycle: stable
inheritance: inheritable
name: marp-deck-skill-16
description: Skill from marp-deck plugin
tier: standard
applyTo: '**/*marp*,**/*presentation*,**/*slide*'
currency: 2026-05-03
lastReviewed: 2026-05-03
---

## Reference

Read `references/marp-themes.md` for built-in themes, custom theme authoring details, and community themes.
