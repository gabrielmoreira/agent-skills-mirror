# WorldEdit Safety Checklists

Load this file when the task involves a large, risky, or time-sensitive WorldEdit
operation and you need a preflight checklist.

## Destructive Edit Preflight

- Confirm you are in the correct world and region.
- Run `//size` before any `//set`, `//replace`, `//cut`, or `//paste`.
- Add masks or filtered selections before broad replacements.
- Verify that a rollback path exists: backup, schematic, or fresh clipboard copy.
- Coordinate with any other staff editing the same area.

## Large Paste Workflow

- Load the schematic and inspect rotation/flip before paste.
- Dry-run mentally for terrain clearance, spawn safety, and protected regions.
- Use `//paste -a` when air should not overwrite existing work.
- Take an immediate checkpoint after a successful paste.

## Undo Discipline

- Treat each logical batch as a separate operation.
- Stop and verify after each batch instead of stacking many destructive commands.
- Keep `//undo` headroom by avoiding unrelated edits in the same history window.
- Save a schematic before irreversible cleanup.

## Post-Edit Verification

- Walk the area at player scale, not only from flyover height.
- Check for liquids, lighting issues, exposed voids, and accidental barriers.
- Confirm any linked redstone, command blocks, or arena triggers still function.
- Record the final schematic name or backup checkpoint used for recovery.
