# Skill: Node.js Secure Route Handler Synthesis

Creates standardized Next.js App Router API endpoints protected by Zod schemas and structured error catch blocks.

## Steps
1. Create endpoint at `src/app/api/<endpoint>/route.ts`
2. Implement Zod validation schemas for incoming JSON bodies or search params
3. Build structured error catch blocks mapping exceptions to JSON responses

## Template
- See `route-handler-template.ts` — POST handler with Zod safeParse and 400/500 responses