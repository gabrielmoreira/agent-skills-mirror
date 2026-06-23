---
name: prisma-schema-designer
description: ''
---

# Skill: prisma-schema-designer

Provides reference patterns for Prisma schema design, safe migration sequencing, and seed data.

## When to use
- Designing a new data model
- Adding fields or relations to existing models
- Planning a migration strategy for backward-compatible and breaking schema changes

## Files
- `schema.template.prisma` — Reference Prisma model with documentation conventions
- `migration-checklist.md` — Pre-migration safety checklist
- `seed.template.ts` — Idempotent seed script pattern

## Conventions
- All models use `id String @id @default(cuid())` as the primary key.
- All models include `createdAt DateTime @default(now())` and `updatedAt DateTime @updatedAt`.
- Use `deletedAt DateTime?` for soft-deletable user data.
- Enum alternatives: use `String` fields with Zod enum validation at the application layer.
- Foreign keys always have an explicit `@@index` unless included in a unique constraint.
