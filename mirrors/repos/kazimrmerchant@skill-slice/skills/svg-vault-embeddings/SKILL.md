---
name: svg-vault-embeddings
description: "Adds local CLIP visual search, near-duplicate detection, and more-like-this to an SVG vault.sqlite embedding BLOB via resvg PNG render and transformers.js Xenova CLIP. Use when the gallery needs semantic or visual query over tagged SVGs. Not for tags-first FTS indexing (svg-vault-index), creating SVG markup (svg-creator), or general JS ML pipelines (transformers-js)."
version: 1.0.1
alwaysApply: false
---

# svg-vault-embeddings — Semantic Search via Local CLIP Image Embeddings

Vault v2 enhancement. Adds visual/semantic search, near-dup detection, and "more like this" over
`assets/consolidated/all_fixed/` (17,348 SVGs, 99.6% valid). Tags-first search (svg-vault-index)
stays the v1 default; this layers on top of the same `vault.sqlite` — the `embedding BLOB` column
already exists (NULL in v1), so **no schema migration is needed to start**.

Everything runs local. No API calls, no vector DB, no GPU required.

**Model:** `Xenova/clip-vit-base-patch32` via transformers.js — 512-dim joint text/image space,
~80 MB one-time download, cached locally, offline after first run.

**Node vs browser:** run everything in **Node** (onnxruntime CPU backend). The batch build must read
17k files and write SQLite — that's a Node job. Queries also stay Node-side (builder-ui already has a
server); the browser only receives ranked results. In-browser CLIP (WASM/WebGPU) only makes sense if
you later want a serverless static gallery — don't start there. The RTX 3090 Ti is unnecessary: CLIP
base on CPU embeds ~10–20 img/s, and brute-force cosine over 17k × 512 floats is single-digit
milliseconds. Total index footprint: 17,348 × 512 × 4 B ≈ **36 MB** of BLOBs.

---

## When to Use

- Adding semantic/visual search ("cozy autumn farm", "something spooky but cute") to the SVG vault gallery.
- Detecting near-duplicate assets across generator batches.
- Implementing "more like this" strips in svg-vault-builder-ui.
- Any task involving CLIP image embeddings, `vault.sqlite`'s `embedding` BLOB column, or brute-force cosine similarity over the vault corpus.
- Trigger keywords: CLIP, embedding, semantic search, near-duplicate, dedup, more like this, visual similarity, cosine, resvg render, transformers.js.

---

## Prerequisites

1. **Existing vault.sqlite** from svg-vault-index with the `embedding BLOB` column already in the `assets` table (NULL in v1 — no migration needed).
2. **`@resvg/resvg-js`** already in `node_modules` (installed by svg-vault-index).
3. **Node.js** with CPU backend (onnxruntime). No GPU required.
4. **Windows host (PowerShell primary).** All commands below are PowerShell-compatible. Use `node` directly; no shell-specific quoting needed for arguments.
5. **One-time dependency install:**

```powershell
npm i @huggingface/transformers better-sqlite3
```

6. **Add `.hf-cache` to `.gitignore`** (the ~80 MB model downloads here on first run).

---

## Procedure

### Step 1 — Build the embedding index

This skill folder does not ship Node helpers. Save the recipes below in the **vault project** (for example `build-embeddings.mjs`, `find-dups.mjs`, `query-embeddings.mjs`, `lib/semantic.mjs`) and run them from that repo.

Run `build-embeddings.mjs`. This renders each valid SVG to 512×512 PNG on a **white** background via resvg, embeds with CLIP vision tower, L2-normalizes, and stores raw Float32Array bytes in `assets.embedding`.

```powershell
node build-embeddings.mjs --db vault.sqlite
```

**Resumable:** only processes rows `WHERE embedding IS NULL AND valid = 1`. Re-run after a crash; it skips done work. Never wrap the whole run in one transaction.

**Expected wall clock:** ~25–50 min on CPU for the full 17k (resvg ~20–40 ms + CLIP ~50–100 ms per asset). Run it once in the background and forget it.

**Core logic of `build-embeddings.mjs`:**

```js
// Usage: node build-embeddings.mjs --db vault.sqlite
import Database from 'better-sqlite3';
import { Resvg } from '@resvg/resvg-js';
import { readFileSync, appendFileSync } from 'node:fs';
import path from 'node:path';
import {
  env, AutoProcessor, CLIPVisionModelWithProjection, RawImage,
} from '@huggingface/transformers';

env.cacheDir = path.resolve('.hf-cache'); // keep the ~80MB model inside the repo dir, gitignored

const dbPath = process.argv[process.argv.indexOf('--db') + 1] ?? 'vault.sqlite';
const db = new Database(dbPath);
db.pragma('journal_mode = WAL');

const MODEL = 'Xenova/clip-vit-base-patch32';
const processor = await AutoProcessor.from_pretrained(MODEL);
// dtype MUST be pinned — corpus and queries must use the same weights (Pitfall 4)
const vision = await CLIPVisionModelWithProjection.from_pretrained(MODEL, { dtype: 'fp32' });

const todo = db.prepare(
  `SELECT id, path FROM assets WHERE embedding IS NULL AND valid = 1`
).all();
const put = db.prepare(`UPDATE assets SET embedding = ? WHERE id = ?`);

console.log(`${todo.length} assets to embed (already done: skipped via embedding IS NULL)`);

function l2(vec) {
  let n = 0;
  for (const x of vec) n += x * x;
  n = Math.sqrt(n) || 1;
  return vec.map((x) => x / n);
}

let done = 0, failed = 0;
const t0 = performance.now();
for (const row of todo) {
  try {
    const svg = readFileSync(row.path, 'utf8');
    const png = new Resvg(svg, {
      fitTo: { mode: 'width', value: 512 },
      background: '#ffffff',              // consistent bg — changing this invalidates the corpus
    }).render().asPng();
    const image = await RawImage.fromBlob(new Blob([png]));
    const inputs = await processor(image);
    const { image_embeds } = await vision(inputs);
    const vec = l2(Float32Array.from(image_embeds.data)); // 512 dims
    put.run(Buffer.from(vec.buffer), row.id);
  } catch (err) {
    failed++;
    appendFileSync('embed-failures.log', `${row.id}\t${row.path}\t${err.message}\n`);
    continue; // one bad SVG must not kill a 30-minute run
  }
  if (++done % 200 === 0) {
    const rate = done / ((performance.now() - t0) / 1000);
    const eta = Math.round((todo.length - done) / rate / 60);
    console.log(`${done}/${todo.length}  (${rate.toFixed(1)}/s, ~${eta} min left, ${failed} failed)`);
  }
}
console.log(`Done. ${done} embedded, ${failed} failed (see embed-failures.log).`);
```

### Step 2 — Mark near-duplicates

Run `find-dups.mjs` after every `build-embeddings.mjs` pass over new assets.

```powershell
node find-dups.mjs --db vault.sqlite
```

**Rule:** cosine > 0.98 (image↔image) **AND** matching structural fingerprint from the genomes table: drawable count within ±10% **and** same dominant palette. Both conditions required.

**Speed strategy:** bucket by fingerprint first, then run cosine only within buckets. Naive all-pairs is 150M dot products (minutes); bucketed is seconds.

**Core logic of `find-dups.mjs`:**

```js
import Database from 'better-sqlite3';
const db = new Database('vault.sqlite');
db.exec(`ALTER TABLE assets ADD COLUMN duplicate_of TEXT`); // wrap in try/catch if it exists

const rows = db.prepare(`
  SELECT a.id, a.tier, a.embedding, g.drawable_count, g.dominant_palette
  FROM assets a JOIN genomes g ON g.asset_id = a.id
  WHERE a.embedding IS NOT NULL
`).all();

const band = (c) => Math.round(Math.log(Math.max(c, 1)) / Math.log(1.1)); // 10% bands
const buckets = new Map();
for (const r of rows) {
  r.vec = new Float32Array(r.embedding.buffer, r.embedding.byteOffset, 512);
  for (const b of [band(r.drawable_count), band(r.drawable_count) + 1]) {
    const key = `${r.dominant_palette}|${b}`;
    (buckets.get(key) ?? buckets.set(key, []).get(key)).push(r);
  }
}

const TIER_RANK = { S: 4, A: 3, B: 2, C: 1 };
const mark = db.prepare(`UPDATE assets SET duplicate_of = ? WHERE id = ?`);
const seen = new Set();
for (const group of buckets.values()) {
  for (let i = 0; i < group.length; i++) for (let j = i + 1; j < group.length; j++) {
    const a = group[i], b = group[j];
    const pair = a.id < b.id ? `${a.id}|${b.id}` : `${b.id}|${a.id}`;
    if (seen.has(pair)) continue; seen.add(pair);
    if (Math.abs(a.drawable_count - b.drawable_count) / Math.max(a.drawable_count, 1) > 0.10) continue;
    let dot = 0; for (let d = 0; d < 512; d++) dot += a.vec[d] * b.vec[d];
    if (dot > 0.98) {
      const [keep, dup] = (TIER_RANK[a.tier] ?? 0) >= (TIER_RANK[b.tier] ?? 0) ? [a, b] : [b, a];
      mark.run(keep.id, dup.id);
    }
  }
}
```

**Hook into svg-vault-index:** v1 gallery/search queries add `AND duplicate_of IS NULL` so dups disappear from browse and search but stay on disk and in the DB (reversible — clear the column to undo).

### Step 3 — Query from the terminal

```powershell
node query-embeddings.mjs "cozy autumn farm" --k 24 --db vault.sqlite
```

**`lib/semantic.mjs`** (shared library for text embedding, corpus loading, and top-k cosine):

```js
import {
  env, AutoTokenizer, CLIPTextModelWithProjection,
} from '@huggingface/transformers';
import path from 'node:path';

env.cacheDir = path.resolve('.hf-cache');
const MODEL = 'Xenova/clip-vit-base-patch32';

let tokenizer, textModel;
export async function textEmbed(query) {
  tokenizer ??= await AutoTokenizer.from_pretrained(MODEL);
  textModel ??= await CLIPTextModelWithProjection.from_pretrained(MODEL, { dtype: 'fp32' });
  const inputs = tokenizer([query], { padding: true, truncation: true });
  const { text_embeds } = await textModel(inputs);
  const v = Float32Array.from(text_embeds.data);
  let n = 0; for (const x of v) n += x * x; n = Math.sqrt(n) || 1;
  return v.map((x) => x / n);
}

// Load the whole corpus into one flat matrix ONCE (36 MB), reuse across queries.
export function loadCorpus(db) {
  const rows = db.prepare(
    `SELECT id, embedding FROM assets WHERE embedding IS NOT NULL`
  ).all();
  const n = rows.length;
  const matrix = new Float32Array(n * 512);
  const ids = new Array(n);
  rows.forEach((r, i) => {
    ids[i] = r.id;
    matrix.set(new Float32Array(r.embedding.buffer, r.embedding.byteOffset, 512), i * 512);
  });
  return { ids, matrix, n };
}

// Brute-force top-k cosine. Both sides L2-normalized → cosine === dot.
export function topK(corpus, qvec, k = 24) {
  const scores = new Array(corpus.n);
  for (let i = 0; i < corpus.n; i++) {
    let dot = 0;
    const off = i * 512;
    for (let d = 0; d < 512; d++) dot += corpus.matrix[off + d] * qvec[d];
    scores[i] = { id: corpus.ids[i], score: dot };
  }
  scores.sort((a, b) => b.score - a.score);
  return scores.slice(0, k);
}
```

**`query-embeddings.mjs`** (CLI wrapper):

```js
// Usage: node query-embeddings.mjs "cozy autumn farm" --k 24 --db vault.sqlite
import Database from 'better-sqlite3';
import { textEmbed, loadCorpus, topK } from './lib/semantic.mjs';

const [query] = process.argv.slice(2);
const k = Number(process.argv[process.argv.indexOf('--k') + 1] || 24);
const dbPath = process.argv.includes('--db')
  ? process.argv[process.argv.indexOf('--db') + 1] : 'vault.sqlite';

const db = new Database(dbPath, { readonly: true });
const corpus = loadCorpus(db);
const results = topK(corpus, await textEmbed(query), k);
const getPath = db.prepare(`SELECT path FROM assets WHERE id = ?`);
for (const r of results) console.log(r.score.toFixed(3), r.id, getPath.get(r.id).path);
```

### Step 4 — Gallery integration (svg-vault-builder-ui)

Add a `tags | semantic` toggle to the search box. `tags` mode hits the existing v1 FTS/tag query untouched. `semantic` mode hits `GET /api/search?mode=semantic&q=...`, which the server answers with `topK(corpus, await textEmbed(q), 24)`.

**Load `loadCorpus(db)` once at server startup** (36 MB, ~100 ms) and keep the text model warm after the first query.

**"More like this" strip:** from an open asset, its embedding is already in the DB — no re-render needed. Fetch its vector, run `topK`, drop self, surface top 12.

```js
export function moreLikeThis(db, corpus, assetId, k = 12) {
  const row = db.prepare(`SELECT embedding FROM assets WHERE id = ?`).get(assetId);
  if (!row?.embedding) return [];
  const qvec = new Float32Array(row.embedding.buffer, row.embedding.byteOffset, 512);
  return topK(corpus, qvec, k + 1).filter((r) => r.id !== assetId).slice(0, k);
}
```

Builder-ui server: `GET /api/similar/:id` → `moreLikeThis(...)` → gallery renders the strip under the asset detail view. Image↔image scores are interpretable: >0.9 near-variant, 0.75–0.9 same subject/style, <0.6 unrelated.

**Best default UX:** tags for exact vocabulary ("barn", "acoustic-guitar"), semantic for vibes ("cozy autumn farm", "something spooky but cute").

---

## Pitfalls

1. **Transparent vs white background changes embeddings.** An alpha canvas rasterizes to *some* composite (often black) inside the vision preprocessor; white-bg and transparent-bg renders of the same SVG can land >0.1 cosine apart. This skill standardizes on `background: '#ffffff'`. Changing it — or the 512 render size — **invalidates the entire corpus**: NULL every embedding and rebuild. Never mix.

2. **resvg renders CSS/SMIL animations as the static base state.** An animated asset and its static twin embed near-identically, so near-dup detection may pair them at cosine > 0.99. Before marking `duplicate_of`, exempt pairs where exactly one side is animated (check the v1 `animated` flag / genome; if both survive, they're legitimately different assets).

3. **Batch cost is real but one-time.** ~25–50 min CPU for 17k. Don't parallelize into multiple Node processes hammering one SQLite writer — WAL helps but the model is the bottleneck anyway. Resumability (`embedding IS NULL`) is the safety net; never wrap the whole run in one transaction.

4. **Pin the dtype (and model revision).** transformers.js picks different default quantizations per backend; a corpus built at `fp32` queried with a `q8` text tower gives silently degraded rankings. Both scripts here pass `{ dtype: 'fp32' }` — keep them in lockstep, and rebuild if you ever change model or dtype.

5. **Text↔image cosines don't live on the image↔image scale.** A *great* text match scores ~0.3; 0.98-style thresholds only apply image↔image (dedup). For text search, use rank order only — never filter text results by absolute score, or every query returns empty.

6. **BLOB byteOffset trap.** BLOBs are raw little-endian Float32 bytes — always read with `new Float32Array(buf.buffer, buf.byteOffset, 512)`. better-sqlite3 Buffers can be pooled; ignoring `byteOffset` reads garbage.

---

## Verification

After any full build, run the three gates below in the vault repo (this skill folder does not ship a verifier):

### Gate 1 — Similar pairs

50 known-similar pairs (variant families from theme pilot batches, e.g. same subject slug with different palettes) in `verify-pairs-similar.json` as `[["id_a","id_b"], ...]` → assert cosine **> 0.9** for ≥ 45/50.

### Gate 2 — Different pairs

50 cross-theme pairs (e.g. mythology vs. sports assets) in `verify-pairs-different.json` → assert cosine **< 0.7** for ≥ 45/50.

### Gate 3 — Smoke query

`textEmbed("cozy autumn farm")` → top-10 must be thematically close (eyeball or assert ≥ 6/10 carry farm/autumn/rural tags via the v1 tags table).

**Cosine helper:**

```js
function cos(a, b) { let d = 0; for (let i = 0; i < 512; i++) d += a[i] * b[i]; return d; }
// load both vectors from assets.embedding, vectors are pre-normalized → cos === dot
```

**Quick checkable command — count embedded assets:**

```powershell
node -e "const db=require('better-sqlite3')('vault.sqlite'); const c=db.prepare('SELECT COUNT(*) AS n FROM assets WHERE embedding IS NOT NULL').get(); console.log(c.n + ' embedded');"
```

Expected output: a number close to 17,348 (minus invalid assets and failures logged in `embed-failures.log`).

**Quick checkable command — verify a single query returns results:**

```powershell
node query-embeddings.mjs "cozy autumn farm" --k 5 --db vault.sqlite
```

Expected: 5 lines of `score id path`, with top scores in the 0.25–0.35 range (text↔image scale).

**If gate 1 or 2 fails broadly** (not just a few pairs), suspect a pipeline inconsistency — background color, dtype, or render size drift — before suspecting the model.

---

## Related skills

- **svg-vault-index** — v1 tags-first search and FTS. The `embedding BLOB` column was reserved in the v1 schema precisely so this v2 skill needs no migration. Gallery queries with `AND duplicate_of IS NULL` integrate here.
- **svg-vault-builder-ui** — Gallery UI server. Add the `tags | semantic` toggle and `GET /api/similar/:id` endpoint here.

---

## Roadmap tie-in (v2)

Per the governing plan, **tags-first search (svg-vault-index) is v1 and stays the default**; this skill is the v2 enhancement it was designed for.

- **v2.0** — `build-embeddings.mjs` full pass + verification gates. DB gains 36 MB, nothing else changes.
- **v2.1** — `find-dups.mjs` + `duplicate_of` filtering in v1 queries; feeds curation (dups cluster heavily inside generator batches).
- **v2.2** — builder-ui: semantic toggle on the search box + "more like this" strip.
- **v3 (later)** — hybrid ranking: v1 tag filter narrows the candidate set, semantic score re-ranks it (`WHERE tag-match AND duplicate_of IS NULL` → dot-product only the survivors). Best of both: tag precision, embedding recall. Only revisit ANN/vector-DB if the vault grows past ~500k assets; at 17k–100k, brute force stays under 50 ms.
