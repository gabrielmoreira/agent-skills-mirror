---
name: typescript-strict-refactor
description: Refactor existing JavaScript or loosely-typed TypeScript code to strict TypeScript - eliminating 'any', adding explicit types, and using zod-derived types. Use when asked to "type this", "convert to TypeScript", "fix type errors", or "make this strict-mode compliant".
---

# TypeScript Strict Refactor Skill

## Process

1. Run `pnpm tsc --noEmit` to get the current list of errors before touching anything — fix in the order TypeScript reports them, since later errors often resolve once earlier ones are fixed.
2. For each `any`:
   - If it's a known shape, define an `interface`/`type`.
   - If it's an external API response, define the shape via `zod` and use `z.infer`, then validate the response with `.parse()`/`.safeParse()` at the network boundary.
   - If it's genuinely unknown, use `unknown` and add a type guard before use — never leave it as `any`.
3. For function parameters/returns lacking types, infer from usage (call sites, what's returned) and add explicit annotations — don't just widen to `unknown` to silence the compiler.
4. Replace `// @ts-ignore` with either a real fix or, if truly unavoidable (e.g. a broken third-party type), `// @ts-expect-error` with a comment explaining why and a link to the upstream issue if one exists.
5. After each file, re-run `pnpm tsc --noEmit` to confirm error count decreased and nothing new broke.

## Common patterns

```ts
// Before
function handle(data: any) { return data.user.name; }

// After
import { z } from "zod";
const dataSchema = z.object({ user: z.object({ name: z.string() }) });
type Data = z.infer<typeof dataSchema>;
function handle(data: Data): string { return data.user.name; }
```

## Checklist
- [ ] `pnpm tsc --noEmit` passes with zero errors
- [ ] No remaining `any` (search confirms zero hits outside of `node_modules`/generated files)
- [ ] No new `@ts-ignore` introduced
- [ ] External data validated with `zod`, not just type-asserted
