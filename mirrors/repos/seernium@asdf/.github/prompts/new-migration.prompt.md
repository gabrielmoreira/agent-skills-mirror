---
mode: agent
description: Design and generate a safe Prisma database migration for the requested schema change.
---

Invoke the `database-architect` agent to:
1. Read the current `prisma/schema.prisma` and understand the existing data model.
2. Design the requested schema change following index and naming conventions.
3. Assess backward compatibility — is this additive (safe) or destructive (requires multi-step deploy)?
4. Generate the migration with `pnpm prisma migrate dev --name <descriptive-name>`.
5. Update seed data if new required fields are introduced.
6. Output a migration safety summary and recommended deploy sequence.

The requested change: ${input}
