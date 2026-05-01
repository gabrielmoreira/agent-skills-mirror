# Champion-Challenger Hash-and-Cache

**Tags**: `performance` `caching` `llm` `pipeline`
**Currency**: 2026-04-27
**Time saved**: Minutes per pipeline run + significant token costs

---

## The Pattern

When a pipeline stage calls an LLM, hash all inputs → compare to cached champion hash → skip API call if unchanged.

```
[Inputs] → [Hash] → [Compare to cache]
                         ↓
              [Match?] → Yes → Return cached output
                    ↓
                   No → Call LLM → Cache new output + hash
```

---

## Why This Matters

LLM API calls are:

- **Slow** — 1-30 seconds per call
- **Expensive** — $0.01-$0.10+ per call
- **Rate-limited** — Quota exhaustion on frequent runs

If inputs haven't changed, the output won't change. Skip the call.

---

## Implementation

### Basic Pattern

```typescript
import { createHash } from 'crypto';
import { readFileSync, writeFileSync, existsSync } from 'fs';

interface CacheEntry {
  inputHash: string;
  output: unknown;
  timestamp: string;
}

function hashInputs(inputs: Record<string, unknown>): string {
  const content = JSON.stringify(inputs, Object.keys(inputs).sort());
  return createHash('sha256').update(content).digest('hex');
}

async function cachedLLMCall<T>(
  cacheFile: string,
  inputs: Record<string, unknown>,
  llmCall: () => Promise<T>
): Promise<T> {
  const inputHash = hashInputs(inputs);

  // Check cache
  if (existsSync(cacheFile)) {
    const cache: CacheEntry = JSON.parse(readFileSync(cacheFile, 'utf-8'));
    if (cache.inputHash === inputHash) {
      console.log('Cache hit — skipping LLM call');
      return cache.output as T;
    }
  }

  // Cache miss — call LLM
  console.log('Cache miss — calling LLM');
  const output = await llmCall();

  // Update cache
  const entry: CacheEntry = {
    inputHash,
    output,
    timestamp: new Date().toISOString(),
  };
  writeFileSync(cacheFile, JSON.stringify(entry, null, 2));

  return output;
}
```

### Usage

```typescript
const result = await cachedLLMCall(
  '.cache/classification.json',
  {
    systemPrompt: CLASSIFICATION_PROMPT,
    documents: documentList,
    taxonomy: taxonomyVersion,
  },
  async () => {
    return await openai.chat.completions.create({
      model: 'gpt-4',
      messages: [
        { role: 'system', content: CLASSIFICATION_PROMPT },
        { role: 'user', content: JSON.stringify(documentList) },
      ],
    });
  }
);
```

---

## Critical Gotcha

> **The hash must include ALL prompt inputs.**

If you add a field to the prompt but not the hash, the cache returns stale results silently.

### Wrong

```typescript
const inputHash = hashInputs({
  documents: documentList,
  // Missing: systemPrompt, taxonomy, temperature, etc.
});
```

### Right

```typescript
const inputHash = hashInputs({
  systemPrompt: CLASSIFICATION_PROMPT,
  documents: documentList,
  taxonomy: taxonomyVersion,
  model: 'gpt-4',
  temperature: 0.0,
});
```

**Rule**: If it affects the output, it goes in the hash.

---

## Proven Usage

Pattern validated in 3 stages of a content pipeline:

- **Classification** — Document categorization
- **Clustering** — Semantic grouping
- **RAI Review** — Responsible AI assessment

Results:

- 90% cache hit rate on unchanged runs
- 5x faster pipeline execution
- 80% token cost reduction

---

## When NOT to Use

- **Non-deterministic outputs needed** — Temperature > 0 for variety
- **Real-time data** — Inputs change on every call
- **Small/cheap calls** — Overhead exceeds savings

---

## Variations

### Multi-file Cache

```typescript
const cacheDir = '.cache/llm/';
const cacheFile = path.join(cacheDir, `${stageName}-${inputHash.slice(0, 8)}.json`);
```

### TTL-based Expiration

```typescript
const MAX_AGE_MS = 7 * 24 * 60 * 60 * 1000; // 7 days

if (cache.inputHash === inputHash) {
  const age = Date.now() - new Date(cache.timestamp).getTime();
  if (age < MAX_AGE_MS) {
    return cache.output as T;
  }
}
```

### Partial Cache Invalidation

```typescript
// Force refresh for specific stages
const FORCE_REFRESH = ['rai-review'];

if (FORCE_REFRESH.includes(stageName)) {
  // Skip cache check
}
```

---

## Related

- Token cost tracking patterns
