---
name: trader-portfolio-cg
description: Mean-variance portfolio optimization via Conjugate Gradient — 40-60× faster than the legacy Neumann path (ADR-126 Phase 3, ADR-123 Wedge 8)
allowed-tools: Bash Read mcp__ruflo-sublinear__solve mcp__claude-flow__memory_store mcp__claude-flow__memory_retrieve mcp__claude-flow__memory_search mcp__claude-flow__agentdb_pattern-search
argument-hint: "[--portfolio-id ID] [--tolerance 1e-6]"
---
Solve the mean-variance optimization `Σ · x = μ` via Conjugate Gradient instead of the legacy Neumann series.

**Why CG instead of Neumann (ADR-123 Wedge 8):**
- Neumann series: ~50 µs at n=256 (legacy `npx neural-trader --portfolio optimize`)
- Conjugate Gradient: ~816 ns at n=256 (this skill)
- Measured speedup: 40-60×; parity within 1e-4 on a fixed seed.

The covariance matrix Σ is symmetric positive-definite by construction (it's a Gram matrix on real returns), so CG is provably optimal — it converges in at most n iterations with no preconditioning, and typically far fewer when eigenvalues cluster.

**Disable flag**: set `RUFLO_NEURAL_TRADER_DISABLE_CG=1` to skip the CG path entirely and fall through to step 4's legacy Neumann route. Useful for A/B validation or when an upstream covariance regression breaks SPD.

Steps:

1. **Ensure neural-trader is available**:
   ```bash
   npm ls neural-trader 2>/dev/null || npm install --ignore-scripts neural-trader
   ```

2. **Read the current covariance matrix Σ and expected-return vector μ** from neural-trader's portfolio API:
   ```bash
   # Primary path (preferred — clean JSON):
   npx neural-trader --portfolio current --json
   # Fallback paths if the --json flag is unavailable on the installed version:
   npx neural-trader --portfolio current  # parse the text output
   # OR pull from AgentDB if a prior run stored the matrix there:
   ```
   ```text
   mcp__claude-flow__memory_search({ query: "covariance matrix current", namespace: "trading-risk", limit: 1 })
   ```
   The skill expects the response to include `covariance: number[][]` (n × n) and `expectedReturns: number[]` (length n).

3. **Solve Σ · x = μ via CG** (preferred path) when `RUFLO_NEURAL_TRADER_DISABLE_CG` is unset and the MCP tool is available:
   ```text
   mcp__ruflo-sublinear__solve({
     matrix: COVARIANCE,
     rhs: EXPECTED_RETURNS,
     algorithm: "cg",
     tolerance: 1e-6,
     maxIterations: 200
   })
   ```
   The tool's expected output shape:
   ```ts
   { solution: number[], iterations: number, residual: number }
   ```
   The skill's adapter (`plugins/ruflo-neural-trader/src/sublinear-adapter.ts`) detects MCP availability and falls back transparently to the embedded CG kernel (~50 LOC) when `mcp__ruflo-sublinear__solve` is not registered in the running runtime. Either way the math is identical — CG, dense form, n × n SPD covariance.

4. **Fallback (legacy Neumann)** — if step 3 reports `degraded: true` (non-SPD input, non-square matrix, MCP error) OR if `RUFLO_NEURAL_TRADER_DISABLE_CG=1`:
   ```bash
   npx neural-trader --portfolio optimize
   ```
   Capture the weights output and tag the artifact metadata with `method: 'neumann-fallback'` and a `reason` field.

5. **Store the optimal weights** to `trading-risk` namespace with full provenance metadata:
   ```text
   mcp__claude-flow__memory_store({
     key: "portfolio-weights-PORTFOLIO_ID-TIMESTAMP",
     namespace: "trading-risk",
     value: JSON.stringify({
       weights: SOLUTION,                  // number[] from step 3 or 4
       method: 'cg-sublinear' | 'cg-local' | 'neumann-fallback',
       solver: 'ruflo-sublinear@0.1.0',    // or 'neural-trader-cli' on fallback
       iterations: ITERATIONS,
       residual: RESIDUAL,
       latencyMs: LATENCY_MS,
       capturedAt: NEW_DATE_ISO,
       reason: FALLBACK_REASON || null
     })
   })
   ```
   The `trading-risk` namespace is canonical (ADR-126 Phase 1; the five-namespace alignment). Long-lived — no TTL — because portfolio weights are the audit trail Phase 4 will Ed25519-sign.

6. **Cross-check against historical patterns** (optional but recommended):
   ```text
   mcp__claude-flow__agentdb_pattern-search({
     query: "portfolio weights Sharpe regime:CURRENT_REGIME",
     namespace: "trading-risk"
   })
   ```
   If the new weights differ by more than 30% in any single asset from the historical median, flag for human review before applying. This is a guard-rail, not a hard block.

**Acceptance criteria (ADR-126 Phase 3):**
- Latency < 1 ms on n = 256 covariance.
- Parity with legacy Neumann within `||cg − neumann||_∞ < 1e-4` on a fixed seed.
- Fallback path engages cleanly when MCP unavailable / covariance non-SPD.
- Artifact metadata distinguishes `cg-sublinear`, `cg-local`, and `neumann-fallback`.

**Refs**:
- ADR-126 Phase 3 (this skill's authoring ADR)
- ADR-123 §162 Row 8 (Wedge 8 speedup claim)
- ADR-123 §262-289 (the SublinearAdapter contract)
- `plugins/ruflo-neural-trader/src/sublinear-adapter.ts` (the adapter)
- `plugins/ruflo-neural-trader/benchmarks/portfolio-cg.bench.ts` (the measured numbers)
