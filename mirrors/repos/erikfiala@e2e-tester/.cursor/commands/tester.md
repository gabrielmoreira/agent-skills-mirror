Run the E2E tester workflow from `.cursor/skills/tester/SKILL.md`.

Required behavior:
1. Start from the current workspace root and run discovery first:
   - `python3 .cursor/skills/tester/scripts/discover_audit_targets.py . --json`
2. Prefer existing package scripts and checked-in runners before ad-hoc commands.
3. Execute Playwright + Lighthouse checks non-interactively when possible.
4. Run Lighthouse across this matrix when technically possible:
   - `light-desktop`
   - `light-mobile`
   - `dark-desktop`
   - `dark-mobile`
5. Attempt categories `performance`, `accessibility`, `best-practices`, `seo`, and `pwa` when supported.
6. End with a structured report:
   - Commands run (native vs adapted)
   - Playwright findings
   - Lighthouse scores for each matrix slice
   - 100/100 gap analysis
   - Explicit coverage gaps and blockers

If this workspace is not a web app, state that clearly and stop.
