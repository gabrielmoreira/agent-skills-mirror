---
applyTo: "**/GraphQL/**/*.cs"
---

# GraphQL Layer Rules

These rules apply exclusively to the `GraphQL` project layer.

## Layer Separation
- **Zero business logic** — resolvers delegate to `Core` services
- HotChocolate packages (`HotChocolate.*`) belong in this layer only — never reference them from `Core`, `DataAccess`, or `Worker`
- Input/Output types are defined here, separate from domain entities in `Abstractions`

## Implementation-First Approach
- Use annotation-based (implementation-first) type definitions — not schema-first SDL
- Leverage HotChocolate's built-in mutation conventions (`[UseMutationConvention]` + `[Error<T>]`) for consistent error handling

## Attribute Stacking Order
When combining data attributes on a resolver, stack in this exact order (top to bottom):

```csharp
[UsePaging]        // 1. Pagination (outermost)
[UseProjection]    // 2. Projection
[UseSorting]       // 3. Sorting
[UseFiltering]     // 4. Filtering (innermost)
```

Wrong order causes silent misbehavior.

## DataLoader Convention
- Name: `{Entity}By{Key}DataLoader`
- Every resolver that fetches child entities must use a DataLoader — no `GetByIdAsync` in a loop
- DataLoaders live in this layer, not in `Core`

## Type Registration
- Ensure `AddTypes()` includes all required types
- Use `[Module]` attribute for automatic type discovery where applicable

## Resolver Parameters
- Use `[Service]` attribute on injected service parameters
- Use `[Parent]` attribute in type extension resolvers
- Always propagate `CancellationToken`
