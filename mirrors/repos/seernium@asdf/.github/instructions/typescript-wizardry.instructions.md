---
applyTo: "**/*.ts,**/*.tsx"
description: "Matt Pocock-inspired nominal branding, templates, and strict explicit return types"
---

# Advanced TypeScript Wizardry Rules

- **Strict Nominal Type Safety (Branded Types):** Use branded types for domain primitives (IDs, emails, currencies) to prevent mixed-assignment logic errors.
  ```typescript
  type Brand<K, T> = K & { readonly __brand: T };
  export type UserId = Brand<string, 'UserId'>;
  export type ProductId = Brand<string, 'ProductId'>;
  ```
- **No Type Cast Escape Hatches:** Never use `as any` or `as unknown`. If type casting is necessary, use narrow type assertion functions or type guards.
- **Template Literal Types:** Enforce domain rules (e.g., hex colors, CSS classes, dynamic routes) directly in the type system.
  ```typescript
  export type HexColor = `#${string}`;
  ```
- **Explicit Returns on API / Public Interfaces:** All public functions, modules, and API route Handlers must explicitly define their return types. Do not rely on implicit return inference for public APIs.
- **Discriminated Unions Over Optional Fields:** Instead of an interface with optional fields representing different states, use a union of strict types differentiated by a literal status property.
