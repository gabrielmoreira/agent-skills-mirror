# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project summary

Web Quality Skills is a collection of Agent Skills for optimizing web projects based on Google Lighthouse guidelines and Core Web Vitals. The skills are framework-agnostic and follow the [Agent Skills specification](https://agentskills.io/specification).

## Quick reference

### Available skills

| Skill | Location | Triggers |
|-------|----------|----------|
| web-quality-audit | `skills/web-quality-audit/` | "audit", "quality review", "lighthouse" |
| performance | `skills/performance/` | "speed up", "optimize", "load time" |
| core-web-vitals | `skills/core-web-vitals/` | "LCP", "INP", "CLS", "Core Web Vitals" |
| accessibility | `skills/accessibility/` | "a11y", "WCAG", "accessible" |
| seo | `skills/seo/` | "SEO", "meta tags", "search" |
| best-practices | `skills/best-practices/` | "security", "best practices", "modern" |

### Key thresholds

**Core Web Vitals (Good):**
- LCP ≤ 2.5s
- INP ≤ 200ms  
- CLS ≤ 0.1

**Performance Budgets:**
- Total: < 1.5 MB
- JS: < 300 KB
- CSS: < 100 KB

**Lighthouse Targets:**
- Performance: ≥ 90
- Accessibility: 100
- Best Practices: ≥ 95
- SEO: ≥ 95

## Common tasks

### Adding a new skill

1. Create directory: `skills/{skill-name}/`
2. Create `SKILL.md` with YAML frontmatter
3. Add optional `scripts/`, `references/`, `assets/`
4. Update `README.md` skills table

### Updating guidelines

1. Edit relevant `SKILL.md` file
2. Keep under 500 lines
3. Move detailed content to `references/`
4. Update version in frontmatter

### Running tests

```bash
# Validate skill format
npx skills-ref validate skills/

# Lint markdown
npx markdownlint skills/**/*.md
```

## Code style

- Use kebab-case for directories and files
- YAML frontmatter required on all SKILL.md files
- Markdown follows standard formatting
- Code examples should show ❌ bad and ✅ good patterns
- Include specific values/thresholds where applicable

## Dependencies

This project has no runtime dependencies. Skills are pure markdown with optional shell scripts.

For development:
- Node.js 18+ (for validation tools)
- skills-ref (optional, for validation)
