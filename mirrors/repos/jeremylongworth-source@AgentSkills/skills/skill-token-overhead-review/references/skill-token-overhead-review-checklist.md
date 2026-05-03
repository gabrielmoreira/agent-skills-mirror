# Skill Token Overhead Review Checklist

## Inspect

- Frontmatter description breadth
- SKILL.md length and specificity
- Reference files loaded by default
- Duplicate guidance across skills
- Scripts or dependencies invoked
- Shell injection or command output size
- MCP servers, tool discovery mode, and tool result size
- Repeated-run or batch workflow compounding
- Host-specific details inside portable files
- Repeated safety text that could live in bundle docs

## Measure

- Same prompt and source material for baseline and skill-enabled runs
- Activated skills and routing path
- Loaded `SKILL.md` files and references
- Scripts, commands, MCP tools, and result sizes
- Turns, validation output, and artifacts produced
- Context before/after or token counts only when the host exposes reliable data
- Qualitative overhead notes when exact token counts are unavailable

## Value Check

Keep overhead when it:

- prevents a known failure
- improves acceptance criteria pass rate
- adds needed safety or approval boundaries
- provides domain-specific process
- reduces repeated manual correction
- prevents repeated-run context compounding in batch workflows

Trim overhead when it:

- repeats generic model knowledge
- duplicates another skill
- loads irrelevant references
- explains repo history instead of workflow
- includes stale platform facts without a freshness rule
- treats host-specific features as portable defaults

## Recommendation Options

- Keep
- Trim SKILL.md
- Move details to references
- Move deterministic work to scripts
- Split skill
- Merge with existing skill
- Compose through a skillset or orchestrator
- Move host-specific behavior to an adapter note
- Narrow trigger description
- Defer until more scenarios prove value
