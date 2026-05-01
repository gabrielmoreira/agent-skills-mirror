#!/usr/bin/env node
/**
 * @type muscle
 * @lifecycle stable
 * @muscle pptx-to-md
 * @lifecycle stable
 * @inheritance inheritable
 * @description Convert PowerPoint (.pptx) to Markdown via pandoc
 * @version 1.0.0
 * @reviewed 2026-04-21
 * @platform windows,macos,linux
 * @requires node,pandoc
 *
 * Extracts slide content, speaker notes, and images from .pptx files
 * and produces clean Markdown. Each slide becomes an H2 section.
 *
 * Usage:
 *   node pptx-to-md.cjs SOURCE.pptx [OUTPUT.md] [options]
 *
 * Options:
 *   --extract-images     Extract images to images/ dir (default: true)
 *   --no-extract-images  Keep images embedded
 *   --wrap N             Line wrap width (default: 0 = no wrap)
 *
 * Requirements:
 *   - Node.js 18+
 *   - pandoc 2.19+
 * @currency 2026-04-21
 */

'use strict';

process.on("uncaughtException", (err) => {
  console.error(`\x1b[31m[FATAL] ${err.message}\x1b[0m`);
  process.exit(1);
});

const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');

// ---------------------------------------------------------------------------
// CLI argument parsing
// ---------------------------------------------------------------------------
function parseArgs(argv) {
  const args = argv.slice(2);
  const result = {
    source: null, output: null, extractImages: true, wrap: 0,
  };
  const positional = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--extract-images') result.extractImages = true;
    else if (args[i] === '--no-extract-images') result.extractImages = false;
    else if (args[i] === '--wrap' && i + 1 < args.length) result.wrap = parseInt(args[++i], 10);
    else if (!args[i].startsWith('--')) positional.push(args[i]);
  }
  if (positional.length === 0) {
    console.error('Usage: node pptx-to-md.cjs SOURCE.pptx [OUTPUT.md] [options]');
    process.exit(1);
  }
  result.source = positional[0];
  result.output = positional[1] || positional[0].replace(/\.pptx$/i, '.md');
  return result;
}

// ---------------------------------------------------------------------------
// Post-processing
// ---------------------------------------------------------------------------
function cleanupMarkdown(md) {
  let result = md;
  // Remove excessive blank lines
  result = result.replace(/\n{4,}/g, '\n\n\n');
  // Remove trailing whitespace
  result = result.replace(/[ \t]+$/gm, '');
  // Clean up div remnants
  result = result.replace(/^:::\s*\{[^}]*\}\s*$/gm, '');
  result = result.replace(/^:::\s*$/gm, '');
  return result.trim() + '\n';
}

// ---------------------------------------------------------------------------
// Image extraction from pandoc media dir
// ---------------------------------------------------------------------------
function extractAndRewriteImages(md, mediaDir, outputDir) {
  const imagesDir = path.join(outputDir, 'images');
  let result = md;

  if (!fs.existsSync(mediaDir)) return result;

  const imgPattern = /!\[([^\]]*)\]\(([^)]+)\)/g;
  let match;
  let idx = 0;

  while ((match = imgPattern.exec(md)) !== null) {
    const [full, alt, src] = match;
    const srcPath = path.resolve(mediaDir, '..', src);
    if (!fs.existsSync(srcPath)) continue;

    if (!fs.existsSync(imagesDir)) fs.mkdirSync(imagesDir, { recursive: true });

    const ext = path.extname(srcPath) || '.png';
    const destName = `slide-image-${++idx}${ext}`;
    const destPath = path.join(imagesDir, destName);
    fs.copyFileSync(srcPath, destPath);
    result = result.replace(full, `![${alt}](images/${destName})`);
  }

  return result;
}

// ---------------------------------------------------------------------------
// Build
// ---------------------------------------------------------------------------
async function build(args) {
  const sourcePath = path.resolve(args.source);
  if (!fs.existsSync(sourcePath)) { console.error(`ERROR: Source file not found: ${sourcePath}`); process.exit(1); }

  const outputPath = path.resolve(args.output);
  const outputDir = path.dirname(outputPath);

  console.log(`\u{1f4ca} Converting ${sourcePath} \u2192 ${outputPath}`);

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'pptx-to-md-'));
  process.on('exit', () => { try { fs.rmSync(tempDir, { recursive: true, force: true }); } catch { /* ignore */ } });

  const tempMd = path.join(tempDir, '_temp.md');

  console.log('\u{1f4dd} Converting PowerPoint to Markdown...');
  const pandocArgs = [
    `"${sourcePath}"`, `-o "${tempMd}"`,
    '--from pptx', '--to markdown',
    '--markdown-headings=atx',
    `--extract-media="${tempDir}"`,
  ];
  if (args.wrap > 0) {
    pandocArgs.push(`--wrap=auto`, `--columns=${args.wrap}`);
  } else {
    pandocArgs.push('--wrap=none');
  }

  try {
    execSync(`pandoc ${pandocArgs.join(' ')}`, { stdio: ['pipe', 'pipe', 'pipe'], timeout: 120000 });
  } catch (err) {
    console.error(`ERROR: pandoc failed: ${err.stderr ? err.stderr.toString() : err}`);
    process.exit(1);
  }

  let md = fs.readFileSync(tempMd, 'utf8');
  md = cleanupMarkdown(md);

  // Extract images from pandoc media directory
  if (args.extractImages) {
    const mediaDir = path.join(tempDir, 'media');
    md = extractAndRewriteImages(md, mediaDir, outputDir);
  }

  fs.writeFileSync(outputPath, md, 'utf8');

  const stats = fs.statSync(outputPath);
  console.log(`\u2705 Done! Output: ${outputPath}`);
  console.log(`   Size: ${(stats.size / 1024).toFixed(1)} KB`);
}

const args = parseArgs(process.argv);
build(args).catch(err => { console.error(`FATAL: ${err.message || err}`); process.exit(1); });
