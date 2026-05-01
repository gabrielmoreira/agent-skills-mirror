---
type: skill
lifecycle: stable
inheritance: inheritable
name: "brand-asset-management"
description: Brand hierarchy, visual identity, asset deployment, platform-specific branding guidelines
tier: extended
applyTo: '**/*brand*,**/*asset*,**/*management*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Brand Asset Management Skill


Expert in the AI assistant brand hierarchy, visual identity systems, asset deployment, and platform-specific branding guidelines.

> **Staleness Watch**: See [EXTERNAL-API-REGISTRY.md](../../EXTERNAL-API-REGISTRY.md) for source URLs and recheck cadence

## Capabilities

- Manage brand hierarchy (CorreaX → the AI assistant → Platform heirs)
- Deploy and maintain visual assets (banners, logos, icons)
- Apply platform-specific branding guidelines
- Generate persona-based marketing copy
- Maintain GK premium branding (space station metaphor)
- Ensure brand consistency across heirs

## When to Use This Skill

- User mentions "branding", "logo", "banner", or "assets"
- Creating or updating marketplace listings
- Deploying visual identity to new platforms
- Reviewing brand consistency across heirs
- Generating persona-targeted copy

## Core Concepts

### Brand Hierarchy

| Level | Brand | Symbol | Usage |
|-------|-------|--------|-------|
| Parent | CorreaX | C split X mark | Footer attribution, legal |
| Product | the AI assistant | A Negative Space Rocket | All the AI assistant-specific assets |
| Platform | Per-heir | Logo variants | VS Code, M365, GitHub |

### Locked Brand Elements

| Element | Value |
|---------|-------|
| Tagline | "Strap a Rocket to Your Back" |
| Subtitle Template | "Take Your [NOUN] to New Heights" |
| Primary Icon | `$(rocket)` codicon |
| Colors | sky blue (#38bdf8) + coral (#f97316) + indigo (#6366f1) — CorreaX dark palette |

### GK Premium Branding

| Tier | Symbol | Meaning |
|------|--------|---------|
| Standard | A Negative Space Rocket | Individual project acceleration |
| Premium (GK) | Knowledge Graph Network | Cross-project knowledge hub |
| GK Tagline | "Your MISSION CONTROL for Cross-Project Wisdom" |
| GK Colors | teal (#0d9488) + teal-light (#2dd4bf) — CorreaX knowledge tier |

### Asset Locations

| Asset | Path | Purpose |
|-------|------|---------|
| Animated Banner | `assets/banner.svg` | GitHub READMEs |
| Static Banner | `assets/banner.png` | Marketplace fallback |
| Extension Icon | `assets/icon.png` | Marketplace icon |
| Mono Logo | `assets/logo-mono.svg` | Activity bar |

### Platform Guidelines

| Platform | Format | Key Requirement |
|----------|--------|-----------------|
| GitHub | Animated SVG | 20s cycle, 10 personas, crossfade |
| VS Code Marketplace | Static PNG | `icon.png` (A Negative Space Rocket) |
| M365 Teams | Static PNG | color.png (192×192), outline.png (32×32) |

### Store Description Pattern

```
🚀 STRAP A ROCKET TO YOUR BACK
[Hook]
━━━ [PLATFORM] vs [PLATFORM] + ALEX ━━━
▸ Capability: Before → After
━━━ WHY ALEX? ━━━
━━━ TAKE YOUR [NOUN] TO NEW HEIGHTS ━━━
[Persona → Benefit mappings]
━━━ LAUNCH SEQUENCES ━━━
[Bottom line. Stop walking. Start flying.]
```

### Persona Copy Mapping

| Persona | Pain | the AI assistant Benefit |
|---------|------|--------------|
| Developer | Re-explaining context | Ship faster, skills remember architecture |
| Researcher | Literature scattered | Hypothesis → publication, accelerated |
| Grad Student | Thesis overwhelm | Literature review on autopilot |
| Tech Writer | Docs fall behind code | Docs that write themselves |
| DevOps | Manual infra, config drift | Same infra, every time |
| PM | Status chasing | 4-6× faster estimates |
| Content Creator | Ideas scattered | Ideas → posts in minutes |

### Heir-Specific Positioning

| Heir | Compares Against | Bottom Line |
|------|------------------|-------------|
| VS Code | GitHub Copilot | "GitHub Copilot = Powerful autocomplete → + the AI assistant = Rocket strapped to your back" |
| M365 | M365 Copilot | "M365 Copilot = Powerful AI toolbox → + the AI assistant = Personal AI that grows with you" |

## PNG Generation

```bash
npx sharp-cli --input source.svg --output output.png -f png --density 150
```

## Example Prompts

- "Update the marketplace description"
- "Generate persona copy for the VS Code store"
- "Check brand consistency across heirs"
- "Create a banner for the new platform"

## Input Expectations

- Platform target (VS Code, M365, GitHub, GK)
- Asset type (banner, logo, icon, copy)
- Persona focus (optional)

## Output Format

- Asset files deployed to correct locations
- Brand guideline compliance report
- Generated copy following store description pattern
