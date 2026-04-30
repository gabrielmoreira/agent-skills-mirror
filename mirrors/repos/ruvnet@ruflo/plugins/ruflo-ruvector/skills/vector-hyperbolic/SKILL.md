---
name: vector-hyperbolic
description: Embed hierarchical data in hyperbolic space via npx ruvector Poincare ball model, compute geodesic distances
argument-hint: "<text> [--model poincare]"
allowed-tools: Bash Read mcp__claude-flow__memory_store mcp__claude-flow__memory_search
---

# Vector Hyperbolic

Embed hierarchical data in the Poincare ball model using `ruvector`.

## When to use

Use this skill when your data has inherent hierarchy — dependency trees, module structures, taxonomies, org charts, ontologies. Hyperbolic space captures hierarchical distances with far fewer dimensions than Euclidean embeddings.

## Steps

1. **Ensure ruvector is available**:
   ```bash
   npm ls ruvector 2>/dev/null || npm install ruvector
   ```
2. **Embed in Poincare ball**:
   ```bash
   npx ruvector embed --model poincare "hierarchical concept"
   ```
   Coordinates near origin = generic/root; near boundary = specific/leaf.
3. **Search in hyperbolic space**:
   ```bash
   npx ruvector search --model poincare "query" --limit 10
   ```
4. **Geodesic distance**: `d(u, v) = arcosh(1 + 2 * ||u-v||^2 / ((1-||u||^2)(1-||v||^2)))`
   Distance grows logarithmically with tree depth, preserving hierarchy.
5. **Store results**:
   `mcp__claude-flow__memory_store({ key: "hyperbolic-CONCEPT", value: "COORDINATES_AND_NEIGHBORS", namespace: "hyperbolic-embeddings" })`

## Poincare ball properties

| Property | Meaning |
|----------|---------|
| Norm close to 0 | Generic, root-level concept |
| Norm close to 1 | Specific, leaf-level concept |
| Small geodesic distance | Closely related in hierarchy |
| Large geodesic distance | Distant or different subtrees |

## Use cases

- **Dependency analysis**: embed module imports to find tightly coupled subtrees
- **Code architecture**: map class hierarchies to discover structural patterns
- **Knowledge organization**: embed concepts to reveal taxonomic relationships
- **Codebase navigation**: find most specific/general modules relative to a query
