#!/usr/bin/env node
/**
 * @type muscle
 * @lifecycle stable
 * @muscle md-to-epub
 * @lifecycle stable
 * @inheritance inheritable
 * @description Convert Markdown to EPUB 3 e-book via pandoc
 * @version 1.0.0
 * @reviewed 2026-04-21
 * @platform windows,macos,linux
 * @requires node,pandoc
 *
 * Generates EPUB 3 output with embedded images, cover, TOC, and metadata
 * from YAML frontmatter. Mermaid diagrams rendered to PNG and embedded.
 *
 * Usage:
 *   node md-to-epub.cjs SOURCE.md [OUTPUT.epub] [options]
 *
 * Options:
 *   --title TITLE          Book title (default: H1 or filename)
 *   --author AUTHOR        Author name
 *   --cover-image PATH     Cover image for the e-book
 *   --toc                  Generate table of contents
 *   --strip-frontmatter    Remove YAML frontmatter
 *   --debug                Save preprocessed markdown
 *
 * Requirements:
 *   - Node.js 18+
 *   - pandoc 2.19+
 *   - mermaid-cli (optional)
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

const { preprocessMarkdown, embedLocalImages, extractFrontmatter } = require(path.join(__dirname, 'shared', 'markdown-preprocessor.cjs'));
const { findMermaidBlocks } = require(path.join(__dirname, 'shared', 'mermaid-pipeline.cjs'));

// ---------------------------------------------------------------------------
// Mermaid rendering
// ---------------------------------------------------------------------------
function convertMermaidToPng(mmdContent, outputPath) {
  const tmpFile = path.join(os.tmpdir(), `alex-mmd-${Date.now()}-${Math.random().toString(36).slice(2)}.mmd`);
  try {
    fs.writeFileSync(tmpFile, mmdContent, 'utf8');
    execSync(`npx mmdc -i "${tmpFile}" -o "${outputPath}" -b white -s 4 -w 1200`, {
      stdio: ['pipe', 'pipe', 'pipe'], timeout: 60000,
    });
    return true;
  } catch { return false; }
  finally { try { fs.unlinkSync(tmpFile); } catch { /* ignore */ } }
}

// ---------------------------------------------------------------------------
// CLI argument parsing
// ---------------------------------------------------------------------------
function parseArgs(argv) {
  const args = argv.slice(2);
  const result = {
    source: null, output: null, title: null, author: null,
    coverImage: null, toc: false, stripFrontmatter: false, debug: false,
  };
  const positional = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--title' && i + 1 < args.length) result.title = args[++i];
    else if (args[i] === '--author' && i + 1 < args.length) result.author = args[++i];
    else if (args[i] === '--cover-image' && i + 1 < args.length) result.coverImage = args[++i];
    else if (args[i] === '--toc') result.toc = true;
    else if (args[i] === '--strip-frontmatter') result.stripFrontmatter = true;
    else if (args[i] === '--debug') result.debug = true;
    else if (!args[i].startsWith('--')) positional.push(args[i]);
  }
  if (positional.length === 0) {
    console.error('Usage: node md-to-epub.cjs SOURCE.md [OUTPUT.epub] [options]');
    process.exit(1);
  }
  result.source = positional[0];
  result.output = positional[1] || positional[0].replace(/\.md$/i, '.epub');
  return result;
}

// ---------------------------------------------------------------------------
// Build
// ---------------------------------------------------------------------------
async function build(args) {
  const sourcePath = path.resolve(args.source);
  if (!fs.existsSync(sourcePath)) { console.error(`ERROR: Source file not found: ${sourcePath}`); process.exit(1); }

  const outputPath = path.resolve(args.output);
  const sourceDir = path.dirname(sourcePath);
  const imagesDir = path.join(sourceDir, 'images');
  if (!fs.existsSync(imagesDir)) fs.mkdirSync(imagesDir, { recursive: true });

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'md-to-epub-'));
  process.on('exit', () => { try { fs.rmSync(tempDir, { recursive: true, force: true }); } catch { /* ignore */ } });

  console.log(`\u{1f4d6} Converting ${sourcePath} \u2192 ${outputPath}`);

  let content = fs.readFileSync(sourcePath, 'utf8');

  // Extract metadata from frontmatter
  let metadata = {};
  try { metadata = extractFrontmatter(content) || {}; } catch { /* ignore */ }

  if (args.stripFrontmatter) {
    const fmMatch = content.match(/^---\r?\n[\s\S]*?\r?\n---\r?\n/);
    if (fmMatch) content = content.slice(fmMatch[0].length);
  }
  content = preprocessMarkdown(content, { format: 'epub' });
  content = embedLocalImages(content, sourceDir);

  // Derive title
  const h1Match = content.match(/^#\s+(.+)$/m);
  const title = args.title || metadata.title || (h1Match ? h1Match[1].trim() : path.basename(sourcePath, '.md'));
  const author = args.author || metadata.author || '';

  // Mermaid diagrams
  const mermaidBlocks = findMermaidBlocks(content);
  if (mermaidBlocks.length > 0) {
    console.log(`   Found ${mermaidBlocks.length} Mermaid diagrams`);
    const replacements = [];
    for (const block of mermaidBlocks) {
      const pngName = `diagram-${block.index + 1}.png`;
      const pngPath = path.join(imagesDir, pngName);
      process.stdout.write(`   Converting diagram ${block.index + 1}... `);
      if (convertMermaidToPng(block.content, pngPath)) {
        replacements.push(`![Diagram ${block.index + 1}](images/${pngName})`);
        console.log('\u2713');
      } else {
        replacements.push(`*[Diagram ${block.index + 1} — rendering failed]*`);
        console.log('\u2717');
      }
    }
    const mermaidPattern = /```mermaid\r?\n[\s\S]*?```/;
    for (const r of replacements) content = content.replace(mermaidPattern, r);
  }

  if (args.debug) {
    fs.writeFileSync(path.join(sourceDir, '_debug_combined.md'), content, 'utf8');
  }

  const tempMd = path.join(tempDir, '_temp.md');
  fs.writeFileSync(tempMd, content, 'utf8');

  console.log('\u{1f4dd} Generating EPUB...');
  const pandocArgs = [
    `"${tempMd}"`, `-o "${outputPath}"`,
    '--from markdown', '--to epub3',
    `--metadata title="${title.replace(/"/g, '\\"')}"`,
    `--resource-path="${path.resolve(sourceDir)}"`,
  ];
  if (author) pandocArgs.push(`--metadata author="${author.replace(/"/g, '\\"')}"`);
  if (args.toc) pandocArgs.push('--toc', '--toc-depth=3');
  if (args.coverImage) {
    const coverPath = path.resolve(args.coverImage);
    if (fs.existsSync(coverPath)) pandocArgs.push(`--epub-cover-image="${coverPath}"`);
  }

  try {
    execSync(`pandoc ${pandocArgs.join(' ')}`, { stdio: ['pipe', 'pipe', 'pipe'], timeout: 120000 });
  } catch (err) {
    console.error(`ERROR: pandoc failed: ${err.stderr ? err.stderr.toString() : err}`);
    process.exit(1);
  }

  const stats = fs.statSync(outputPath);
  console.log(`\u2705 Done! Output: ${outputPath}`);
  console.log(`   Size: ${(stats.size / 1024).toFixed(1)} KB`);
}

const args = parseArgs(process.argv);
build(args).catch(err => { console.error(`FATAL: ${err.message || err}`); process.exit(1); });
