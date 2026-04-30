---
name: vector-cluster
description: Cluster vectors by similarity using npx ruvector k-means or density-based methods with labeled group summaries
argument-hint: "<namespace> [--k N]"
allowed-tools: Bash Read mcp__claude-flow__memory_search mcp__claude-flow__memory_store mcp__claude-flow__memory_list
---

# Vector Cluster

Cluster vectors in a namespace by semantic similarity using `ruvector`.

## When to use

Use this skill when you have a collection of embeddings and want to discover natural groupings. Clustering reveals themes, identifies outliers, and helps organize large vector collections.

## Steps

1. **Ensure ruvector is available**:
   ```bash
   npm ls ruvector 2>/dev/null || npm install ruvector
   ```
2. **Run clustering**:
   - With known cluster count: `npx ruvector cluster --namespace NAMESPACE --k N`
   - With auto-detection: `npx ruvector cluster --namespace NAMESPACE --density`
3. **Review output** -- ruvector reports: cluster ID, label, member count, cohesion score, and outliers (for density mode)
4. **Store results**:
   `mcp__claude-flow__memory_store({ key: "clusters-NAMESPACE-TIMESTAMP", value: "CLUSTER_ASSIGNMENTS", namespace: "vector-clusters" })`

## Interpreting results

- **High cohesion** (>0.85): tight, well-defined cluster
- **Medium cohesion** (0.6-0.85): related but diverse content
- **Low cohesion** (<0.6): loose grouping, try higher k
- **Outliers**: novel or anomalous entries worth investigating

## Graph-based clustering (ruvector v2.1+)

ruvector supports Louvain community detection and spectral clustering for graph-structured data:
```bash
npx ruvector hooks graph-cluster --namespace NAMESPACE
npx ruvector hooks graph-mincut --namespace NAMESPACE
```
