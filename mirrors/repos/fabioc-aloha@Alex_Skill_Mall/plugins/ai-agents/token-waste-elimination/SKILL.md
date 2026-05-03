---
type: skill
lifecycle: stable
inheritance: inheritable
name: token-waste-elimination
description: Audit and eliminate token waste from cognitive architecture memory files -- instructions, prompts, skills, and agents
tier: standard
applyTo: '**/*token*,**/*waste*,**/*elimination*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Token Waste Elimination


Memory files are LLM context, not human documentation. Every line costs tokens. Optimize for my consumption, not human readability.

## Loading Tiers

| Tier | What Loads | When | Cost |
|------|-----------|------|------|
| **Always-on** | `copilot-instructions.md` body, `AGENTS.md`/`CLAUDE.md` (if present), ALL instruction descriptions, ALL skill name+descriptions, ALL agent descriptions | Every request | Fixed |
| **Match-loaded** | Instruction bodies with `applyTo` | File context matches glob | Predictable |
| **Agent-loaded** | Instruction bodies without `applyTo` | I judge description relevant (not automatic) | Variable |
| **On-demand** | Skill bodies, prompt bodies | I load skill when needed; prompt on `/command` | Near-zero |

## Core Rules

**Instructions thin, skills thick**: Instructions = decision tables + routing. Skills = procedures + examples + references.

**applyTo gates cost**: Add `applyTo` to domain-specific instructions (file-type triggered). Omit for conversational/universal instructions.

**No-applyTo != auto-load**: Without `applyTo`, the description is always visible but I choose whether to load the body. Not deterministic.

## Size Thresholds

| File Type | Has Matching Skill | Max | Over Threshold |
|-----------|-------------------|-----|----------------|
| Instruction | Yes | 50 lines | Trim to rules + routing pointer |
| Instruction | No | 200 lines | Review for splitting |
| Skill body | Any | 400 lines | Move detail to resource files |
| Prompt | Any | 60 lines | Slim to steps + skill reference |

## Waste Patterns

| Pattern | Fix |
|---------|-----|
| `%%{init` in Mermaid | Delete line (rendering directive I can't use) |
| Legacy `## Related Skills` sections with separate JSON | Delete section (connections now use frontmatter `applyTo`) |
| `Microsoft Entra ID` | Replace with `Microsoft Entra ID` |
| `Classification:` / `Activation:` / `Priority:` in instruction body | Delete (duplicates YAML frontmatter) |
| Instruction >50 lines with matching skill | Trim: keep decision tables, move procedures to skill |
| Code blocks >20 lines in instructions | Move to `.github/muscles/` or `scripts/` |
| Templates >15 lines inline | Move to resource file |
| Hardcoded counts (e.g., "150 skills") | Replace with "See catalog" references |
| Stale dates/versions | Update or remove |
| Human-tutorial prose in memory files | Compress to rule statements (LLM doesn't need tutorials) |

## Audit Procedure

1. **Baseline**: Run `node .github/muscles/audit-token-waste.cjs` for automated scan
2. **Overlap**: Find instructions with matching skills >50 lines. Trim to rules + routing pointer
3. **Patterns**: Fix every waste pattern hit (muscle `--fix` handles safe patterns automatically)
4. **applyTo**: Add globs to domain-specific instructions missing them
5. **Always-on cost**: Sum instruction descriptions + skill descriptions + copilot-instructions.md. Target: minimize
6. **Prompt check**: Prompts should be workflow steps only (20-40 lines). No code blocks or reference tables that exist in skills
7. **Savings**: Re-run muscle, compare before/after

## Waste Triage Decision Table (AC3)

Not all scanner findings are actionable. Triage before fixing:

| Finding | True Waste? | Action | Rationale |
|---|---|---|---|
| Mermaid in a Mermaid-teaching skill | **No** — instructional content | Skip | The diagram IS the lesson |
| Mermaid in a non-diagram skill | **Yes** — rendering directive | Remove or replace with table | LLM can't render Mermaid in chat |
| Code block in a muscle-authoring skill | **No** — reference example | Skip | Shows correct muscle patterns |
| Code block >20 lines in instruction | **Yes** — belongs in muscle | Move to `.github/muscles/` | Instructions should be thin |
| Instruction >50 lines WITH matching skill | **Yes** — overlap | Trim to decision tables + routing pointer | Skill holds the detail |
| Instruction >50 lines WITHOUT matching skill | **Maybe** — review | Split if two concerns; keep if single dense domain | No skill to defer to |
| Duplicate content across instruction + skill | **Yes** — redundancy | Keep in skill, trim from instruction | Single source of truth |
| Template >15 lines inline | **Yes** — bloat | Move to resource file | Templates rarely change |
| Hardcoded count that matches reality | **Yes** — future drift | Replace with "see catalog" or remove | Counts rot on next edit |
| Historical note in a plan/ADR | **No** — archival | Skip | Plans are point-in-time records |

**Rule**: When uncertain, check if the content helps the LLM make better decisions. If yes → keep. If it's for human eyes only → remove or move.

## When to Run

- After harvesting skills (inherited waste)
- Before a release (clean context = better responses)
- When response quality degrades (context bloat is often the cause)
- Quarterly maintenance (drift accumulates silently)

## Audit Script Example

```javascript
// .github/muscles/audit-token-waste.cjs
const fs = require('fs');
const path = require('path');

function auditInstructions(dir) {
  const files = fs.readdirSync(dir);
  const oversize = [];
  
  for (const file of files) {
    if (!file.endsWith('.instructions.md')) continue;
    const content = fs.readFileSync(path.join(dir, file), 'utf8');
    const lines = content.split('\n').length;
    
    // Check for matching skill
    const skillPath = `.github/skills/${file.replace('.instructions.md', '')}/SKILL.md`;
    const hasSkill = fs.existsSync(skillPath);
    const threshold = hasSkill ? 50 : 200;
    
    if (lines > threshold) {
      oversize.push({ file, lines, threshold, hasSkill });
    }
  }
  return oversize;
}

const results = auditInstructions('.github/instructions');
console.log(`Found ${results.length} oversize instructions`);
results.forEach(r => console.log(`  ${r.file}: ${r.lines} lines (max: ${r.threshold})`));
```

## Optimization Before/After Example

```markdown
## Before (45 tokens, wastes context)
When generating visualizations, use the chart-interpretation skill.
This skill provides patterns for reading charts and extracting insights.
The skill covers various chart types including bar charts, line charts, pie charts.

## After (12 tokens, same information)
Chart generation → chart-interpretation skill.
```

## Quality Metrics

| Metric | Target | Measure |
|--------|--------|---------|
| Instruction avg lines | <40 | `dir .github/instructions/ \| measure-object` |
| Instructions with applyTo | >80% | Grep frontmatter |
| Skill body avg lines | <250 | Brain-qa bounds dimension |
| Total always-on cost | <2000 tokens | Manual count of descriptions |
| Waste patterns found | 0 | Muscle `--check` mode |
