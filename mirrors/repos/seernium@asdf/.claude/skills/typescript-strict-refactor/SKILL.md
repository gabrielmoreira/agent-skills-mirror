# Skill: Strict TypeScript Refactoring

Eliminates loose type definitions, placeholder interfaces, and type escape hatches.

## Steps
1. Run `pnpm tsc --noEmit` to identify compiler warnings
2. Replace `any` with explicit generics, interfaces, or type assertions
3. Introduce runtime type guards for dynamic input responses