---
name: api-rate-limiter
description: ''
---

# Skill: api-rate-limiter

Provides a rate limiting middleware pattern for Next.js API routes and Server Actions.
Uses Upstash Redis (serverless-compatible) with sliding window algorithm.

## When to use
- Any public-facing API route
- Auth endpoints (login, signup, password reset) — most critical
- Any endpoint that triggers expensive operations (email, payment, AI inference)

## Files
- `rate-limiter.template.ts` — Rate limiter middleware

## Setup
1. Install: `pnpm add @upstash/ratelimit @upstash/redis`
2. Add to `.env.example`:
   ```
   UPSTASH_REDIS_REST_URL=   # Upstash Redis REST URL
   UPSTASH_REDIS_REST_TOKEN= # Upstash Redis REST token
   ```
3. Import and use in route handlers following the `route-handler-template.ts` pattern.

## Limits (starting point — tune to your traffic)
- Auth endpoints: 5 requests / 15 minutes per IP
- General API: 60 requests / minute per IP or user ID
- AI/expensive endpoints: 10 requests / hour per user
