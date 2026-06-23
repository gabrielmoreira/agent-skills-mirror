---
name: error-boundary
description: ''
---

# Skill: error-boundary

Provides React Error Boundary component and Next.js App Router error handling patterns.

## When to use
- Any page section that fetches data and might fail
- Setting up global error handling for the Next.js app router
- Integrating Sentry for client-side error tracking

## Files
- `error-boundary.template.tsx` — Reusable React error boundary component
- `error-page.template.tsx` — Next.js `error.tsx` page template

## Rules
- Every major page section that fetches data must be wrapped in an error boundary
- Error boundaries must show a user-friendly message — never raw error details
- Client-side errors should be reported to Sentry with the error and component stack
- The Next.js `global-error.tsx` must be the outermost fallback
