#!/usr/bin/env node
/**
 * @type muscle
 * @lifecycle stable
 * @muscle md-to-gamma
 * @lifecycle stable
 * @inheritance inheritable
 * @description Pre-process a markdown file into a Gamma-import-ready version (name.md → name-gamma.md)
 * @version 1.0.0
 * @skill gamma-presentation
 * @reviewed 2026-04-23
 * @platform windows,macos,linux
 * @requires node
 *
 * Reads a regular markdown file and emits a sibling `<name>-gamma.md` file
 * optimized for Gamma's importer (https://gamma.app):
 *   - Inserts `---` card breaks before every H2 (idempotent, won't duplicate)
 *   - Demotes secondary H1s to H2 (Gamma expects a single title card)
 *   - Adds inline `<!-- Gamma: ... -->` recommendation comments next to issues
 *   - Prepends a header summarizing detected issues + workflow tips
 *
 * The output is *not* sent to the Gamma API. The user takes the resulting
 * `-gamma.md` file to https://gamma.app, imports it, and refines the deck
 * via Gamma's built-in chat agent (see skills/gamma-presentation).
 *
 * Usage:
 *   node md-to-gamma.cjs SOURCE.md [OUTPUT.md]
 *
 * Options:
 *   --quiet         Suppress progress output (still prints final path)
 *   --no-comments   Skip inline recommendation comments (clean output)
 *   --print         Print result to stdout instead of writing a file
 *
 * Exit codes:
 *   0 success
 *   1 fatal error (missing file, write failure)
 *
 * @currency 2026-04-23
 */

'use strict';

process.on('uncaughtException', (err) => {
  console.error(`\x1b[31m[FATAL] ${err.message}\x1b[0m`);
  process.exit(1);
});

const fs = require('fs');
const path = require('path');

// ---------------------------------------------------------------------------
// CLI parsing
// ---------------------------------------------------------------------------
const args = process.argv.slice(2);
if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
  console.log('Usage: node md-to-gamma.cjs SOURCE.md [OUTPUT.md] [--quiet] [--no-comments] [--print]');
  process.exit(args.length === 0 ? 1 : 0);
}

const flags = new Set(args.filter((a) => a.startsWith('--')));
const positional = args.filter((a) => !a.startsWith('--'));
const sourcePath = path.resolve(positional[0]);
const explicitOutput = positional[1] ? path.resolve(positional[1]) : null;
const QUIET = flags.has('--quiet');
const NO_COMMENTS = flags.has('--no-comments');
const PRINT = flags.has('--print');

if (!fs.existsSync(sourcePath)) {
  console.error(`\x1b[31m[ERROR] Source file not found: ${sourcePath}\x1b[0m`);
  process.exit(1);
}
if (!sourcePath.toLowerCase().endsWith('.md')) {
  console.error(`\x1b[31m[ERROR] Source must be a .md file: ${sourcePath}\x1b[0m`);
  process.exit(1);
}

const log = (msg) => { if (!QUIET) console.log(msg); };

// ---------------------------------------------------------------------------
// Output path: name.md → name-gamma.md (avoid double-suffix)
// ---------------------------------------------------------------------------
function deriveOutputPath(src) {
  const dir = path.dirname(src);
  const ext = path.extname(src);
  const base = path.basename(src, ext);
  const stripped = base.endsWith('-gamma') ? base.slice(0, -'-gamma'.length) : base;
  return path.join(dir, `${stripped}-gamma${ext}`);
}
const outputPath = explicitOutput || deriveOutputPath(sourcePath);

// ---------------------------------------------------------------------------
// Preprocess
// ---------------------------------------------------------------------------
function preprocess(input) {
  const issues = [];
  const lines = input.split(/\r?\n/);
  const out = [];

  // Track fenced code blocks so we don't touch their innards
  let inFence = false;
  let fenceMarker = '';
  let h1Count = 0;
  let cardCount = 0;
  let currentCardLine = -1; // index in `out` where current card body starts
  let currentCardWords = 0;
  let currentCardImages = 0;
  let lastHeadingLevel = 0;

  const wordsIn = (s) => (s.trim().match(/\S+/g) || []).length;
  const isHr = (s) => /^\s*---\s*$/.test(s);

  const flushCardBudget = () => {
    if (currentCardLine >= 0 && currentCardWords > 140 && !NO_COMMENTS) {
      // insert recommendation comment right after the card heading
      out.splice(currentCardLine + 1, 0,
        `<!-- Gamma: card body ~${currentCardWords} words exceeds 140-word budget — consider splitting -->`);
      issues.push(`Dense card (~${currentCardWords} words) near line ${currentCardLine + 1}`);
    }
    if (currentCardLine >= 0 && currentCardImages === 0 && currentCardWords < 12 && cardCount > 1 && !NO_COMMENTS) {
      // very short card with no image — likely a divider, leave alone
    }
    currentCardWords = 0;
    currentCardImages = 0;
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Fence detection (```)
    const fenceMatch = line.match(/^(\s*)(`{3,}|~{3,})/);
    if (fenceMatch) {
      if (!inFence) {
        inFence = true;
        fenceMarker = fenceMatch[2][0];
      } else if (line.trim().startsWith(fenceMarker)) {
        inFence = false;
      }
      out.push(line);
      continue;
    }
    if (inFence) {
      out.push(line);
      continue;
    }

    // Heading detection
    const headingMatch = line.match(/^(#{1,6})\s+(.+?)\s*#*\s*$/);
    if (headingMatch) {
      let level = headingMatch[1].length;
      const text = headingMatch[2];

      // H1 demotion: keep first H1, demote subsequent to H2
      if (level === 1) {
        h1Count++;
        if (h1Count > 1) {
          level = 2;
          issues.push(`Demoted secondary H1 to H2: "${text}"`);
        }
      }

      // Heading-skip detection (e.g., H2 → H4)
      if (lastHeadingLevel > 0 && level > lastHeadingLevel + 1 && !NO_COMMENTS) {
        out.push(`<!-- Gamma: heading skipped from H${lastHeadingLevel} to H${level} — Gamma's outline expects sequential levels -->`);
        issues.push(`Heading-level skip H${lastHeadingLevel} → H${level} at "${text}"`);
      }
      lastHeadingLevel = level;

      // Insert card break before H2 if missing
      if (level === 2) {
        flushCardBudget();
        // walk back through trailing blank lines in `out` to find prior non-blank
        let k = out.length - 1;
        while (k >= 0 && out[k].trim() === '') k--;
        const prior = k >= 0 ? out[k] : '';
        const isFirstH2 = cardCount === 0 && h1Count === 0; // no title card preceding
        if (!isHr(prior) && k >= 0 && !isFirstH2) {
          // ensure blank line, then ---, then blank line
          if (out.length > 0 && out[out.length - 1].trim() !== '') out.push('');
          out.push('---');
          out.push('');
        } else if (!isHr(prior) && k < 0) {
          // file starts directly with H2 — no break needed
        }
        cardCount++;
      }

      out.push('#'.repeat(level) + ' ' + text);
      currentCardLine = out.length - 1;
      continue;
    }

    // Image detection (markdown ![alt](src))
    const imgMatches = line.match(/!\[([^\]]*)\]\(([^)]*)\)/g);
    if (imgMatches && !NO_COMMENTS) {
      for (const m of imgMatches) {
        const parts = m.match(/!\[([^\]]*)\]\(([^)]*)\)/);
        const alt = (parts[1] || '').trim();
        const src = (parts[2] || '').trim();
        currentCardImages++;
        if (!src && alt.length < 12) {
          out.push(`<!-- Gamma: image has empty src and short alt — Gamma's AI needs a richer prompt (subject, framing, lighting, mood) -->`);
          issues.push(`Image with thin alt-text prompt: "${alt}"`);
        }
      }
    }

    // Word counting for card budget
    if (line.trim() !== '' && !line.startsWith('<!--')) {
      currentCardWords += wordsIn(line);
    }

    out.push(line);
  }
  flushCardBudget();

  // Header summary block
  const header = buildHeader({
    sourceName: path.basename(sourcePath),
    h1Count,
    cardCount,
    issues,
  });

  return { content: header + out.join('\n').replace(/\n{3,}/g, '\n\n').trimEnd() + '\n', issues, cardCount };
}

function buildHeader(meta) {
  const lines = [];
  lines.push('<!--');
  lines.push('  Gamma-ready markdown — generated by md-to-gamma.cjs');
  lines.push(`  Source: ${meta.sourceName}`);
  lines.push(`  Cards: ${meta.cardCount}  H1s: ${meta.h1Count}`);
  lines.push('');
  lines.push('  Workflow:');
  lines.push('    1. Open https://gamma.app → Create new → Import → upload this file');
  lines.push('    2. Choose theme + page format (16:9 fixed for presentations)');
  lines.push('    3. Click Generate');
  lines.push('    4. Refine each card via the sparkle ✨ chat agent');
  lines.push('    5. Export as PPTX or PDF');
  lines.push('');
  if (meta.issues.length === 0) {
    lines.push('  No structural issues detected.');
  } else {
    lines.push(`  Recommendations (${meta.issues.length}):`);
    for (const issue of meta.issues.slice(0, 20)) {
      lines.push(`    - ${issue}`);
    }
    if (meta.issues.length > 20) {
      lines.push(`    - ... ${meta.issues.length - 20} more (see inline <!-- Gamma: ... --> comments)`);
    }
  }
  lines.push('-->');
  lines.push('');
  return lines.join('\n');
}

// ---------------------------------------------------------------------------
// Run
// ---------------------------------------------------------------------------
const source = fs.readFileSync(sourcePath, 'utf8');
const { content, issues, cardCount } = preprocess(source);

if (PRINT) {
  process.stdout.write(content);
  process.exit(0);
}

fs.writeFileSync(outputPath, content, 'utf8');
log(`\x1b[32m✔\x1b[0m Wrote ${path.relative(process.cwd(), outputPath)}`);
log(`  Cards: ${cardCount}  Issues flagged: ${issues.length}`);
if (issues.length > 0 && !QUIET) {
  log('  Top recommendations:');
  for (const issue of issues.slice(0, 5)) log(`    - ${issue}`);
  if (issues.length > 5) log(`    - ... ${issues.length - 5} more (see file header)`);
}
log('');
log('  Next: open https://gamma.app → Import → upload this file');
