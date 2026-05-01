# Safe Install Checklist

## Pre-Install

- Source and publisher identified
- Commit, tag, or release pinned
- License acceptable
- `SKILL.md` reviewed
- References reviewed
- Scripts reviewed or disabled
- Dependencies reviewed
- Secrets handling reviewed
- Data movement reviewed
- MCP/tool scopes reviewed

## Least-Privilege Install

- Prefer read-only first run.
- Enable only needed skills.
- Keep write tools disabled until needed.
- Keep network tools disabled unless required.
- Use a test workspace before production or customer data.
- Keep host-specific adapters separate from portable skill content.

## Post-Install

- Confirm expected routing.
- Run one safe scenario.
- Review loaded files and tool use.
- Document approval gates.
- Re-review after updates.

## Recommendation

Use one:

- approve
- approve with changes
- block
- defer
