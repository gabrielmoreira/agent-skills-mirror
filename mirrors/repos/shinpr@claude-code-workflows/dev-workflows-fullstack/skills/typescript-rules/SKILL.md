---
name: typescript-rules
description: React/TypeScript frontend development rules including type safety, component design, state management, and error handling. Use when implementing React components, TypeScript code, or frontend features.
---

# TypeScript Development Rules (Frontend)

## Basic Principles

- **Aggressive Refactoring** - Prevent technical debt and maintain health
- **Delete code when no current caller exists** - YAGNI principle (Kent Beck)

## Comment Writing Rules
Code first: names and types carry meaning; a comment must add what code cannot, and one comment per decision is enough. Frontend specifics:
- **Comment intent, not markup**: explain why a component memoizes, guards, or re-renders — not what the JSX renders
- **Timeless content only**: Record decisions and rationale; leave chronological history to version control

## Type Safety

**Default Rule**: Prefer `unknown`, generics, or union types over `any`. Retain `any` only when an existing external, generated, or legacy public signature requires it, or when replacing it prevents the project type check from expressing a safe generic relationship. Record the declaration path or type-check result that proves the constraint. When a local adapter can preserve compatibility and expose a safer type within the user request or current task/design artifact, implement the adapter; otherwise confine `any` to the smallest adapter or public-signature boundary, document the reason, and validate untrusted data before it enters typed application code.

**any Type Alternatives (Priority Order)**
1. **unknown Type + Type Guards**: Use for validating external input (API responses, localStorage, URL parameters)
2. **Generics**: When type flexibility is needed
3. **Union Types・Intersection Types**: Combinations of multiple types
4. **Type Assertions (Last Resort)**: Only when type is certain

**Type Guard Implementation Pattern**
```typescript
function isUser(value: unknown): value is User {
  return typeof value === 'object' && value !== null && 'id' in value && 'name' in value
}
```

**Modern Type Features**
- **satisfies Operator**: `const config = { apiUrl: '/api' } satisfies Config` - Preserves inference
- **const Assertion**: `const ROUTES = { HOME: '/' } as const satisfies Routes` - Immutable and type-safe
- **Branded Types**: `type UserId = string & { __brand: 'UserId' }` - Distinguish meaning
- **Template Literal Types**: `type EventName = \`on\${Capitalize<string>}\`` - Express string patterns with types

**Type Safety in Frontend Implementation**
- **React Props/State**: TypeScript manages types, unknown unnecessary
- **External API Responses**: Treat unvalidated payloads as `unknown` and validate at the boundary. A generated client may retain its declared type when it also enforces the contract at runtime
- **localStorage/sessionStorage**: Handle `string | null` at the browser boundary; treat parsed data as `unknown` until validated
- **URL Parameters**: Handle the router or platform's `string | null` shape, then parse and validate before converting to a domain type
- **Form Input (Controlled Components)**: Type-safe with React synthetic events

**Type Safety in Data Flow**
- **Frontend → Backend**: Props/State (Type Guaranteed) → API Request (Serialization)
- **Backend → Frontend**: API Response (`unknown`) → Type Guard → State (Type Guaranteed)

**Type Complexity Review Signals**

Use the following as prompts to review a design, not as pass/fail thresholds. Existing project conventions and a component's actual responsibility take precedence.

- **Props Design**:
  - Props count: 3-7 props ideal (consider component splitting if exceeds 10)
  - Optional Props: 50% or less (consider default values or Context if excessive)
  - Nesting: Up to 2 levels (flatten deeper structures)
- Type Assertions: Review design if used 3+ times
- **External API Types**: Relax constraints and define according to reality (convert appropriately internally)

## Coding Conventions

**Component Design Criteria**
- **Function components for new code**: Prefer function components and Hooks. Preserve working class components unless the user request or current task/design artifact requires migration; a class component remains valid when implementing an Error Boundary directly
- **Custom Hooks**: Standard pattern for logic reuse and dependency injection
- **Component Hierarchy**: Use the project's adopted component architecture. When the project uses Atomic Design: Atoms → Molecules → Organisms → Templates → Pages. When the project uses Feature-based, Container-Presenter, or another structure: follow that structure consistently and document the chosen layering in the project README or design doc
- **File placement**: Follow the repository's existing component, test, and style layout. Co-locate related files only when that is the established convention or an approved new structure

**Server/Client Boundary (RSC frameworks only — e.g., Next.js App Router)**
- Default to server components for data fetching and rendering; isolate interactivity behind a `"use client"` boundary at the smallest scope that needs it
- Keep browser-only APIs (`window`, `localStorage`, event handlers) inside client components; calling them in a server component breaks the render
- N/A for client-only SPAs (e.g., Vite) — skip when the project has no server-component runtime

**State Management Patterns**
- **Local State**: `useState` for component-specific state
- **Context API**: For sharing state across component tree (theme, auth, etc.)
- **Custom Hooks**: Encapsulate state logic and side effects
- **Server State**: Follow the project's existing server-state layer; React Query and SWR are common options when already adopted

**Data Flow Principles**
- **Single Source of Truth**: Each piece of state has one authoritative source
- **Unidirectional Flow**: Data flows top-down via props
- **Immutable Updates**: Use immutable patterns for state updates

```typescript
// Immutable state update — always create new arrays/objects
setUsers(prev => [...prev, newUser])
```

**Function Design**
- Prefer 0-2 parameters. For 3+ related values, use an object when it clarifies names or represents one domain input; preserve a positional signature when the repository convention or external API requires it
  ```typescript
  function createUser({ name, email, role }: CreateUserParams) {}
  ```

**Props Design (Props-driven Approach)**
- Props are the interface: Define all necessary information as props
- Declare data dependencies through props, hooks, Context, or injected modules according to the project's established state and dependency boundaries
- Type-safe: Always define Props type explicitly

**Environment Variables**
- **Use the build tool's env accessor**: read client-side env through the bundler's exposed accessor — Vite via `import.meta.env`, Next.js/CRA via prefixed `process.env`. Raw, unprefixed access is `undefined` in the browser bundle
- **Only prefixed vars reach the client**: build tools expose only vars carrying their public prefix; an unprefixed var is `undefined` in the browser. The prefix differs per tool — match the project's bundler (Vite `VITE_`, Next.js public `NEXT_PUBLIC_`, CRA `REACT_APP_`)
- Centrally validate env through a typed config layer. Fail fast for missing required values; provide defaults only for optional values or an explicitly defined local-development mode

```typescript
// Vite example. Use the project's existing schema validator when one is configured.
const apiUrl = import.meta.env.VITE_API_URL
if (!apiUrl) {
  throw new Error('Missing required client environment variable: VITE_API_URL')
}

const config = {
  apiUrl,
  appName: import.meta.env.VITE_APP_NAME ?? 'My App' // optional: intentional product default
}
```

**Security (Client-side Constraints)**
- **CRITICAL**: All frontend code is public and visible in browser
- **All secrets stay server-side**: Store API keys, tokens, and secrets on the backend only
- Exclude `.env` files via `.gitignore`
- Limit error messages to non-sensitive context

```typescript
// Backend manages secrets, frontend accesses via proxy
const response = await fetch('/api/data') // Backend handles API key authentication
```

**Dependency Injection**
- **Custom Hooks for dependency injection**: Ensure testability and modularity

**Asynchronous Processing**
- Promise Handling: Follow the repository's established style; prefer `async`/`await` when it makes sequencing and error propagation clearer
- Error Handling: Handle event-handler and asynchronous failures with `try-catch`, a typed `Result`, or user-visible error state. Error Boundaries cover rendering failures in descendant components, not event handlers or ordinary asynchronous callbacks
- Type Definition: Explicitly define return types at exported APIs and important boundaries (e.g., `Promise<Result>`); allow inference for local implementations when the contract remains clear
- Effect race/cleanup: guard `useEffect` data fetches against out-of-order responses and post-unmount state updates — abort or ignore stale results (`AbortController` or a mounted flag), or use a server-state library (React Query/SWR) that cancels and dedupes. `try-catch` alone does not cover this

**Format Rules**
- Semicolon usage follows the project's formatter settings
- Types in `PascalCase`, variables/functions in `camelCase`
- Imports follow the repository's existing TypeScript, bundler, and package-boundary configuration. Use aliases only when the project config resolves them; do not invent a `src/` alias

**Clean Code Principles**
- Delete unused code immediately
- Delete debug `console.log()`
- Delete commented-out code (retrieve from version control when needed)
- Comments explain "why" (not "what")

## Error Handling

**Handling Rule**: Every caught error must be intentionally propagated, converted to a typed error result, or represented as user-facing error state. Log it once at the boundary that owns diagnosis or recovery, with sensitive data redacted; avoid duplicate logging while propagating the same failure.

**Fail-Fast Principle**: Fail quickly on errors to prevent continued processing in invalid states
```typescript
catch (error) {
  logger.error('Processing failed', error)
  throw error // Handle with Error Boundary or higher layer
}
```

**Result Type Pattern**: Express errors with types for explicit handling
```typescript
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E }

// Example: Express error possibility with types
function parseUser(data: unknown): Result<User, ValidationError> {
  if (!isValid(data)) return { ok: false, error: new ValidationError() }
  return { ok: true, value: data as User }
}
```

**Custom Error Classes**
```typescript
export class AppError extends Error {
  constructor(message: string, public readonly code: string, public readonly statusCode = 500) {
    super(message)
    this.name = this.constructor.name
  }
}
// Purpose-specific: ValidationError(400), ApiError(502), NotFoundError(404)
```

**Layer-Specific Error Handling (React)**
- Error Boundary: Place at meaningful UI recovery boundaries to catch descendant rendering errors and display fallback UI
- Custom Hook: Detect business rule violations, propagate AppError as-is
- API Layer: Convert fetch errors to domain errors

**Structured Logging and Sensitive Information Protection**
Redact sensitive fields (password, token, apiKey, secret, creditCard) before logging

**Asynchronous Error Handling in React**
- Add an Error Boundary where a rendering failure needs localized recovery; use the application's top-level boundary when localized recovery adds no value
- Handle expected failures in event handlers and async workflows with `try-catch`, typed results, or rejected-promise propagation to the owning layer
- Preserve the failure context and choose one observable outcome: propagate it, return an error variant, or display error state

## Refactoring Techniques

**Basic Policy**
- Small Steps: Maintain always-working state through gradual improvements
- Safe Changes: Minimize the scope of changes at once
- Behavior Guarantee: Ensure existing behavior remains unchanged while proceeding

**Implementation Procedure**: Understand Current State → Gradual Changes → Behavior Verification → Final Validation

**Priority**: Duplicate Code Removal > Large Function Division > Complex Conditional Branch Simplification > Type Safety Improvement

## Performance Optimization

- Automatic memoization: when React Compiler is enabled, rely on it; reach for manual `React.memo`/`useMemo`/`useCallback` only as a profiler- or identity-justified escape hatch (a measured bottleneck, or stable reference identity for third-party APIs / effect dependencies)
- State Optimization: Minimize re-renders with proper state structure
- Lazy Loading: Use `React.lazy` and `Suspense` for code splitting
- Bundle Size: Monitor via the build script against the project's budget

## Non-functional Requirements

- **Browser Compatibility**: Implement against the support policy in the PRD, Design Doc, Browserslist, or build configuration. When none is defined, preserve the repository's current transpilation/polyfill baseline and surface any new browser-dependent API as an unresolved compatibility decision
- **Performance**: Verify against project-defined budgets and the metric that represents the affected experience (for example Web Vitals, interaction latency, bundle size, or a profiler trace). When no budget exists, measure the changed path and report the observed result instead of inventing a threshold
