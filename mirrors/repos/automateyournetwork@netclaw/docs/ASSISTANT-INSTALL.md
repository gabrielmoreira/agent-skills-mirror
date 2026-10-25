# Assistant-guided installation

Open **NetClaw: Set Up a New NetClaw**, then **NetClaw: Connect assistant for new setup**. Copilot uses the extension's setup MCP definition. Claude Code and Codex receive a native registration preview using the editor runtime, so setup does not depend on a Node executable in the terminal's PATH. Review the registration before running it. Keep the owning VS Code window open.

Use **NetClaw: Add setup skill to project** to place the stamped [shared install skill](../installer/assistant-skills/netclaw-install/SKILL.md) in the selected deployment project: `.github/skills` for Copilot, `.claude/skills` for Claude Code, or `.agents/skills` for Codex. A different existing skill is preserved and reported as a collision. This deployment skill is separate from NetClaw's development Spec Kit skills and operational skill inventory.

The eight closed setup tools observe, browse the catalog, draft, validate, explain, stage native review, request native secret entry and observe status. They do not apply, resume, clean up, send messages, return secret values or accept shell commands. Client auto-approval cannot authorize installation. Secret entry returns presence only; reports use structural redaction.

An assistant should state the existing-claw disclosure, ask only missing decisions in wizard order, and record assumptions/unresolved choices. Start with an [intent example](INTENT-PROMPTS.md). After validation, **stage** the current plan hash, inspect the visible wizard, and use its **Review installation** button yourself. Review always names each home, provider, service and source revision.

Without an active editor/broker, reopen setup. The assistant must not work around that boundary with terminal installation commands. This is an API authority boundary, not an OS sandbox for other tools the assistant already possesses. Actual three-client UI qualification remains separate from the passing protocol/transcript fixtures.
