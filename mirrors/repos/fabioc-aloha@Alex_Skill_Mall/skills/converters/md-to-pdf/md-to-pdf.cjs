#!/usr/bin/env node
/**
 * @type muscle
 * @lifecycle stable
 * @muscle md-to-pdf
 * @lifecycle stable
 * @inheritance inheritable
 * @description Convert Markdown to PDF via pandoc (LaTeX or HTML intermediate)
 * @version 1.0.0
 * @skill md-to-word
 * @reviewed 2026-04-21
 * @platform windows,macos,linux
 * @requires node,pandoc,wkhtmltopdf|lualatex
 *
 * Two rendering engines supported:
 *   - html (default): pandoc → HTML → wkhtmltopdf. Lightweight, no LaTeX install needed.
 *   - latex: pandoc → LaTeX → PDF. Best for academic/mathematical content.
 *
 * Reuses the shared markdown preprocessor and Mermaid pipeline from md-to-word.
 *
 * Usage:
 *   node md-to-pdf.cjs SOURCE.md [OUTPUT.pdf] [options]
 *
 * Options:
 *   --engine ENGINE      Rendering engine: html (default), latex
 *   --style PRESET       Style: professional (default), academic, minimal
 *   --toc                Generate table of contents
 *   --cover              Generate cover page from H1 + metadata
 *   --page-size SIZE     Page size: letter (default), a4, 6x9
 *   --strip-frontmatter  Remove YAML frontmatter before conversion
 *   --debug              Save preprocessed markdown as _debug_combined.md
 *   --mermaid-png        Render Mermaid diagrams to PNG (default: true when mmdc available)
 *   --embed-images       Embed local images as base64 data URIs (default: true)
 *
 * Requirements:
 *   - Node.js 18+
 *   - pandoc (Windows: winget install pandoc)
 *   - For html engine: wkhtmltopdf (winget install wkhtmltopdf)
 *   - For latex engine: MiKTeX or TeX Live (winget install MiKTeX.MiKTeX)
 *   - mermaid-cli (optional, npm install -g @mermaid-js/mermaid-cli)
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
const { execSync, execFileSync } = require('child_process');

// ---------------------------------------------------------------------------
// Shared module imports
// ---------------------------------------------------------------------------
const { preprocessMarkdown, validateHeadingHierarchy, embedLocalImages, validateLinks } = require(path.join(__dirname, 'shared', 'markdown-preprocessor.cjs'));
const { findMermaidBlocks } = require(path.join(__dirname, 'shared', 'mermaid-pipeline.cjs'));

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const PAGE_SIZES = {
  letter: { width: '8.5in', height: '11in', margin: '1in' },
  a4: { width: '210mm', height: '297mm', margin: '25mm' },
  '6x9': { width: '6in', height: '9in', margin: '0.75in' },
};

const STYLE_CSS = {
  professional: `
    body { font-family: 'Segoe UI', system-ui, sans-serif; font-size: 10.5pt; color: #1f2328; line-height: 1.6; }
    h1 { color: #0078D4; border-bottom: 2px solid #0078D4; padding-bottom: 4pt; }
    h2 { color: #2B579A; } h3 { color: #3B3B3B; }
    code { font-family: Consolas, monospace; font-size: 9pt; background: #f5f5f5; padding: 1px 4px; border-radius: 3px; }
    pre { background: #f5f5f5; padding: 12px; border-left: 3px solid #ccc; font-size: 9pt; overflow-x: auto; }
    table { border-collapse: collapse; width: 100%; margin: 12px 0; }
    th { background: #0078D4; color: white; padding: 6px 8px; text-align: left; }
    td { padding: 6px 8px; border-bottom: 1px solid #ddd; }
    tr:nth-child(even) td { background: #f0f0f0; }
    img { display: block; margin: 12px auto; max-width: 90%; }
    blockquote { border-left: 4px solid #0078D4; margin: 12px 0; padding: 8px 16px; background: #f0f7ff; }
    a { color: #0563C1; }
  `,
  academic: `
    body { font-family: 'Times New Roman', serif; font-size: 12pt; color: #000; line-height: 2; }
    h1 { color: #1A1A2E; } h2 { color: #2D2D44; } h3 { color: #3B3B3B; }
    code { font-family: 'Courier New', monospace; font-size: 10pt; }
    pre { font-size: 10pt; border: 1px solid #ccc; padding: 10px; }
    table { border-collapse: collapse; width: 100%; margin: 12px 0; }
    th, td { padding: 6px 8px; border: 1px solid #666; }
    img { display: block; margin: 12px auto; max-width: 90%; }
  `,
  minimal: `
    body { font-family: system-ui, sans-serif; font-size: 11pt; color: #333; line-height: 1.5; }
    h1, h2, h3 { color: #222; }
    code { font-family: monospace; font-size: 10pt; background: #f8f8f8; padding: 1px 3px; }
    pre { background: #f8f8f8; padding: 10px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { padding: 4px 8px; border: 1px solid #ddd; }
    img { display: block; margin: 12px auto; max-width: 90%; }
  `,
};

// ---------------------------------------------------------------------------
// Tool detection
// ---------------------------------------------------------------------------
function hasCommand(cmd) {
  try { execSync(`where ${cmd}`, { stdio: 'pipe' }); return true; }
  catch { return false; }
}

// ---------------------------------------------------------------------------
// Mermaid rendering (reused from md-to-word pattern)
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
    source: null, output: null, engine: 'html', style: 'professional',
    toc: false, cover: false, pageSize: 'letter',
    stripFrontmatter: false, debug: false, embedImages: true,
  };
  const positional = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--engine' && i + 1 < args.length) result.engine = args[++i];
    else if (args[i] === '--style' && i + 1 < args.length) result.style = args[++i];
    else if (args[i] === '--toc') result.toc = true;
    else if (args[i] === '--cover') result.cover = true;
    else if (args[i] === '--page-size' && i + 1 < args.length) result.pageSize = args[++i];
    else if (args[i] === '--strip-frontmatter') result.stripFrontmatter = true;
    else if (args[i] === '--debug') result.debug = true;
    else if (args[i] === '--embed-images') result.embedImages = true;
    else if (args[i] === '--no-embed-images') result.embedImages = false;
    else if (!args[i].startsWith('--')) positional.push(args[i]);
  }
  if (positional.length === 0) {
    console.error('Usage: node md-to-pdf.cjs SOURCE.md [OUTPUT.pdf] [options]');
    process.exit(1);
  }
  result.source = positional[0];
  result.output = positional[1] || positional[0].replace(/\.md$/i, '.pdf');
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

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'md-to-pdf-'));
  process.on('exit', () => { try { fs.rmSync(tempDir, { recursive: true, force: true }); } catch { /* ignore */ } });

  console.log(`\u{1f4c4} Converting ${sourcePath} \u2192 ${outputPath}`);
  console.log(`   Engine: ${args.engine} | Style: ${args.style} | Page: ${args.pageSize}`);

  // Preprocess
  let content = fs.readFileSync(sourcePath, 'utf8');
  if (args.stripFrontmatter) {
    const fmMatch = content.match(/^---\r?\n[\s\S]*?\r?\n---\r?\n/);
    if (fmMatch) content = content.slice(fmMatch[0].length);
  }
  content = preprocessMarkdown(content, { format: 'pdf' });

  // Embed images
  if (args.embedImages) {
    content = embedLocalImages(content, sourceDir);
  }

  // Cover page
  if (args.cover) {
    const h1Match = content.match(/^#\s+(.+)$/m);
    const title = h1Match ? h1Match[1].trim() : path.basename(sourcePath, '.md');
    const dateStr = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
    content = `\n<div style="text-align:center;padding-top:3in;">\n\n# ${title}\n\n*${dateStr}*\n\n</div>\n\n\\newpage\n\n` + content;
  }

  // Mermaid diagrams
  const mermaidBlocks = findMermaidBlocks(content);
  if (mermaidBlocks.length > 0) {
    console.log(`\u{1f4ca} Found ${mermaidBlocks.length} Mermaid diagrams`);
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
    for (const replacement of replacements) {
      content = content.replace(mermaidPattern, replacement);
    }
  }

  // Debug output
  if (args.debug) {
    const debugPath = path.join(sourceDir, '_debug_combined.md');
    fs.writeFileSync(debugPath, content, 'utf8');
    console.log(`\u{1f50d} Debug: saved preprocessed markdown to ${debugPath}`);
  }

  const tempMd = path.join(tempDir, '_temp.md');
  fs.writeFileSync(tempMd, content, 'utf8');

  const page = PAGE_SIZES[args.pageSize] || PAGE_SIZES.letter;

  if (args.engine === 'latex') {
    // LaTeX engine
    console.log('\u{1f4dd} Generating PDF via LaTeX...');
    const pandocArgs = [
      `"${tempMd}"`, `-o "${outputPath}"`,
      '--from markdown', '--to pdf', '--pdf-engine=lualatex',
      `-V geometry:margin=${page.margin}`,
      `-V paperwidth=${page.width}`, `-V paperheight=${page.height}`,
      `--resource-path="${path.resolve(sourceDir)}"`,
    ];
    if (args.toc) pandocArgs.push('--toc', '--toc-depth=3');
    try {
      execSync(`pandoc ${pandocArgs.join(' ')}`, { stdio: ['pipe', 'pipe', 'pipe'], timeout: 120000 });
    } catch (err) {
      console.error(`ERROR: pandoc/latex failed: ${err.stderr ? err.stderr.toString() : err}`);
      process.exit(1);
    }
  } else {
    // HTML engine — pandoc → HTML → wkhtmltopdf (or weasyprint)
    console.log('\u{1f4dd} Generating PDF via HTML...');
    const css = STYLE_CSS[args.style] || STYLE_CSS.professional;
    const cssFile = path.join(tempDir, '_style.css');
    fs.writeFileSync(cssFile, css, 'utf8');

    const tempHtml = path.join(tempDir, '_temp.html');
    const pandocArgs = [
      `"${tempMd}"`, `-o "${tempHtml}"`,
      '--from markdown', '--to html5', '--standalone',
      `--css="${cssFile}"`,
      `--resource-path="${path.resolve(sourceDir)}"`,
    ];
    if (args.toc) pandocArgs.push('--toc', '--toc-depth=3');
    try {
      execSync(`pandoc ${pandocArgs.join(' ')}`, { stdio: ['pipe', 'pipe', 'pipe'], timeout: 120000 });
    } catch (err) {
      console.error(`ERROR: pandoc failed: ${err.stderr ? err.stderr.toString() : err}`);
      process.exit(1);
    }

    // HTML → PDF
    if (hasCommand('wkhtmltopdf')) {
      const wkArgs = [
        '--page-size', args.pageSize === 'a4' ? 'A4' : 'Letter',
        '--margin-top', page.margin, '--margin-bottom', page.margin,
        '--margin-left', page.margin, '--margin-right', page.margin,
        '--enable-local-file-access',
        `"${tempHtml}"`, `"${outputPath}"`,
      ];
      try {
        execSync(`wkhtmltopdf ${wkArgs.join(' ')}`, { stdio: ['pipe', 'pipe', 'pipe'], timeout: 120000 });
      } catch (err) {
        console.error(`ERROR: wkhtmltopdf failed: ${err.stderr ? err.stderr.toString() : err}`);
        process.exit(1);
      }
    } else if (hasCommand('weasyprint')) {
      try {
        execSync(`weasyprint "${tempHtml}" "${outputPath}"`, { stdio: ['pipe', 'pipe', 'pipe'], timeout: 120000 });
      } catch (err) {
        console.error(`ERROR: weasyprint failed: ${err.stderr ? err.stderr.toString() : err}`);
        process.exit(1);
      }
    } else {
      console.error('ERROR: No PDF renderer found. Install wkhtmltopdf or weasyprint.');
      console.error('  Windows: winget install wkhtmltopdf');
      console.error('  macOS: brew install wkhtmltopdf');
      process.exit(1);
    }
  }

  const stats = fs.statSync(outputPath);
  console.log(`\u2705 Done! Output: ${outputPath}`);
  console.log(`   Size: ${(stats.size / 1024).toFixed(1)} KB`);
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
const args = parseArgs(process.argv);
build(args).catch(err => { console.error(`FATAL: ${err.message || err}`); process.exit(1); });
