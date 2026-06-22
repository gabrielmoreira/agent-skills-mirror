# Skill: env-validator

Provides a runtime environment variable validation pattern using Zod.
Validates all required env vars at server startup with descriptive errors — fail fast, not mid-request.

## When to use
- Any new environment variable is added to the project
- Setting up a new service or deployment environment
- Debugging "undefined env var" runtime errors

## Files
- `env.template.ts` — Runtime env validation module

## Usage
Import the validated env object instead of `process.env` directly:
```ts
import { env } from '@/server/env';
// env.DATABASE_URL is typed string, guaranteed to exist
```

## Convention
- The `env.ts` file lives at `src/server/env.ts`
- All server-only env vars (secrets, DB URLs) use `z.string()` with `.min(1)`
- Public env vars (client-safe, prefixed `NEXT_PUBLIC_`) use a separate `clientEnv` export
- Document all vars in `.env.example` with placeholder values and comments
