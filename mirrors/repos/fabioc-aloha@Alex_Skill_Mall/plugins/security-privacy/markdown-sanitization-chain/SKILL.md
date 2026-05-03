---
type: skill
lifecycle: stable
inheritance: inheritable
name: markdown-sanitization-chain
description: Markdown sanitization order matters — marked.js then DOMPurify then Mermaid to prevent XSS
tier: standard
applyTo: '**/*markdown*,**/*sanitization*,**/*chain*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Markdown Sanitization Chain

**Category**: Security
**Time Saved**: 2-4 hours debugging XSS vulnerabilities
**Battle-tested**: Yes — production incident

---

## The Problem

You're rendering user-supplied markdown with a diagram library. The app works great until someone submits markdown containing malicious scripts that bypass your rendering.

## Why It Happens

Markdown renderers (marked.js, markdown-it) convert markdown to HTML but don't sanitize it. Diagram renderers (Mermaid, PlantUML) execute after sanitizers run, potentially introducing new attack vectors. The order of operations matters critically.

## The Rule

**Always: marked.js → DOMPurify → Mermaid (post-render)**

```
1. Parse markdown to HTML (marked.js)
2. Sanitize HTML (DOMPurify)
3. Render diagrams on sanitized DOM (Mermaid.run())
```

Never skip the sanitizer even if content is "trusted."

## Implementation

```javascript
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import mermaid from 'mermaid';

async function renderMarkdown(content, container) {
  // Step 1: Parse markdown to HTML
  const rawHtml = marked.parse(content);
  
  // Step 2: Sanitize (BEFORE inserting into DOM)
  const cleanHtml = DOMPurify.sanitize(rawHtml, {
    ADD_TAGS: ['mermaid'],  // Allow mermaid tags through
  });
  
  // Step 3: Insert sanitized HTML
  container.innerHTML = cleanHtml;
  
  // Step 4: Render diagrams on sanitized DOM
  await mermaid.run({ nodes: container.querySelectorAll('.mermaid') });
}
```

## Common Mistakes

| Mistake | Consequence |
|---------|-------------|
| Skip DOMPurify ("it's internal content") | XSS from any content source |
| Sanitize after Mermaid renders | Mermaid-injected scripts execute |
| Use innerHTML without sanitization | Classic XSS |
| Trust localStorage/URL params | User-controlled XSS payloads |

## DOMPurify Configuration

```javascript
const config = {
  ADD_TAGS: ['mermaid'],           // Preserve diagram tags
  ADD_ATTR: ['onclick'],           // Only if absolutely needed
  FORBID_TAGS: ['style', 'script'], // Explicit blocklist
  FORBID_ATTR: ['onerror', 'onload'],
};
```

## Verification Checklist

- [ ] Markdown parser runs first
- [ ] DOMPurify runs before DOM insertion
- [ ] Diagram renderer runs after sanitization
- [ ] No raw innerHTML without sanitization anywhere
- [ ] Test with `<img src=x onerror=alert(1)>` payload

## Related Skills

- `allowlist-over-blocklist` — Validation patterns
- `shell-injection-prevention` — Command execution safety
