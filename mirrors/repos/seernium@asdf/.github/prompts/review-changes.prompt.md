---
description: Run a full convention/security/test-coverage review of the current changes
agent: code-reviewer
tools: ['search', 'codebase', 'read', 'runCommands']
---

Review all currently uncommitted changes (`git diff`) against this repo's TypeScript, React, Next.js, Tailwind, and Node.js conventions. Run `pnpm tsc --noEmit` and `pnpm lint` as part of the review. Output findings grouped by Blocking / Should fix / Nit, and end with an overall verdict.
