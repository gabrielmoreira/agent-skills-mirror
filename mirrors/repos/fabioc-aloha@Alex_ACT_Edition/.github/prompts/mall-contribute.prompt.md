---
description: "Propose a local skill for contribution to the Plugin Mall — strip project specifics, format as a Mall-compatible proposal, submit via feedback channel"
lastReviewed: 2026-05-26
---

# Contribute a Skill to the Plugin Mall

Propose a local skill (from `.github/skills/local/`) for inclusion in the Alex ACT Plugin Mall so other heirs can benefit from it.

## Steps

1. **Identify the candidate skill.** If the user named one, locate it under `.github/skills/local/`. If not, list local skills and ask which one to propose.

2. **Validate generalizability.** The skill must pass this test: "Would a brand-new heir on a completely different project find this useful on day 1?" If the skill is locked to one vertical, one framework, or one team's workflow, it belongs in `local/`, not the Mall.

3. **Strip project specifics** per `cross-project-isolation.instructions.md`:
   - Remove file paths with project structure (replace with generic descriptors)
   - Remove project/repo/product names (anonymize or omit)
   - Remove domain-specific identifiers (account IDs, ticket numbers)
   - Generalize niche tech references (`a vector database`, not `PineconeDB v3.2 on our staging cluster`)
   - Keep: skill/instruction names, categories, severity, abstract patterns, ACT references

4. **Rewrite into Mall plugin structure.** Produce three artifacts:

   **plugin.json:**
   ```json
   {
     "name": "<kebab-case-name>",
     "title": "<Human Title>",
     "category": "<one of: academic-research, ai-agents, architecture-patterns, cloud-infrastructure, code-quality, communication-people, converters, data-analytics, devops-process, documentation, domain-expertise, media-graphics, platform-tooling, reasoning-metacognition, security-privacy, supervisor-fleet>",
     "shape": ["SKILL.md"],
     "tier": "standard",
     "description": "<one sentence: what it does AND when it fires>",
     "token_cost": "<estimated token count of SKILL.md>",
     "source_store": "heir-contribution",
     "artifacts": ["SKILL.md"]
   }
   ```

   **README.md:**
   ```markdown
   # <Title>

   <2-3 sentence description of what the skill does and why it's useful.>

   ## Source

   Contributed from real project experience by an ACT-Edition heir.

   ## Skills

   - `SKILL.md` — <one-line summary>

   ## Install

   `/mall-install <name>`
   ```

   **SKILL.md:** The generalized skill body with proper frontmatter (`type: skill`, `lifecycle: stable`, `inheritance: inheritable`, `name`, `description`, `tier`, `applyTo`, `currency`, `lastReviewed`).

5. **Write the proposal to the feedback channel.** Create a markdown file at `AI-Memory/feedback/alex-act/<YYYY-MM-DD>-mall-proposal-<name>.md` with this structure:

   ```markdown
   ---
   category: feature-request
   severity: low
   skill: mall-contribute
   date: <YYYY-MM-DD>
   ---

   # Mall Contribution Proposal: <Title>

   ## Summary

   <One paragraph: what the skill does, why it generalizes.>

   ## Proposed plugin.json

   <paste>

   ## Proposed README.md

   <paste>

   ## Proposed SKILL.md

   <paste>

   ## Generalizability Evidence

   - <Why this applies beyond the originating project>
   - <What class of tasks it serves>
   ```

6. **Report result.** Confirm the proposal was written and explain what happens next: the user's Supervisor (if running) or the user themselves will triage the proposal and decide whether to promote it to the Mall.

## Notes

- Resolve the shared memory bus via `resolveMemoryBus()` (sibling `../Alex_ACT_Memory`). CLI: `node .github/scripts/_registry.cjs --resolve .`
- If the memory bus is not set up, offer to run `/initialize` first.
- Never submit a skill that contains PII, credentials, or project-identifying information.
- The Supervisor evaluates proposals against the Mall's 5-dimension scorecard (maintenance, adoption, license, fit, documentation). Writing a quality proposal with clear generalizability evidence increases acceptance odds.
- Token cost estimate: count characters in the SKILL.md body, divide by 4.

## Would Revise If

Revisit this prompt by **2026-08-26** (90 days) or sooner if any of the following fires: the workflow it invokes ceases to produce its intended output (skill body changed but prompt steps stale); the visible markers / verification steps in its body are consistently skipped; or the slash-command name is no longer discoverable in the prompt picker.
