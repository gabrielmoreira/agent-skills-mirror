#!/usr/bin/env node
// ============================================================================
// md2pdf-export: Markdown → PDF/PNG/JPEG Converter
// Uses the same Markdown → HTML → Headless Chrome pipeline as
// Markdown Preview Enhanced (crossnote/mume)
// ============================================================================

const fs = require('fs');
const path = require('path');

// ---------------------------------------------------------------------------
// Dependency resolution: try local node_modules first, then global
// ---------------------------------------------------------------------------
function tryRequire(name) {
  try {
    return require(name);
  } catch {
    // Try from script's local node_modules
    const localPath = path.join(__dirname, 'node_modules', name);
    return require(localPath);
  }
}

const matter = tryRequire('gray-matter');
const markdownIt = tryRequire('markdown-it');
const highlightjs = tryRequire('markdown-it-highlightjs');
const texmath = tryRequire('markdown-it-texmath');
const katex = tryRequire('katex');
const anchor = tryRequire('markdown-it-anchor');
const tocPlugin = tryRequire('markdown-it-toc-done-right');
const footnote = tryRequire('markdown-it-footnote');
const puppeteer = tryRequire('puppeteer');

// ---------------------------------------------------------------------------
// CSS Themes
// ---------------------------------------------------------------------------
const THEMES = {
  github: `
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial,
                   sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
      font-size: 16px;
      line-height: 1.6;
      color: #24292e;
      max-width: 980px;
      margin: 0 auto;
      padding: 2em;
    }
    h1, h2, h3, h4, h5, h6 { margin-top: 24px; margin-bottom: 16px; font-weight: 600; line-height: 1.25; }
    h1 { font-size: 2em; padding-bottom: 0.3em; border-bottom: 1px solid #eaecef; }
    h2 { font-size: 1.5em; padding-bottom: 0.3em; border-bottom: 1px solid #eaecef; }
    h3 { font-size: 1.25em; }
    code { background: #f6f8fa; padding: 0.2em 0.4em; border-radius: 3px; font-size: 85%; }
    pre { background: #f6f8fa; padding: 16px; border-radius: 6px; overflow: auto; }
    pre code { background: none; padding: 0; font-size: 85%; }
    blockquote { padding: 0 1em; color: #6a737d; border-left: 0.25em solid #dfe2e5; margin: 0 0 16px 0; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 16px; }
    table th, table td { padding: 6px 13px; border: 1px solid #dfe2e5; }
    table tr:nth-child(2n) { background: #f6f8fa; }
    table th { font-weight: 600; background: #f1f3f5; }
    img { max-width: 100%; }
    hr { border: none; border-top: 1px solid #eaecef; margin: 24px 0; }
    a { color: #0366d6; text-decoration: none; }
    ul, ol { padding-left: 2em; }
    .footnotes { margin-top: 2em; border-top: 1px solid #eaecef; padding-top: 1em; font-size: 0.9em; }
    .toc { background: #f6f8fa; padding: 1em 1.5em; border-radius: 6px; margin-bottom: 2em; }
    .toc ul { list-style: none; padding-left: 1em; }
    .toc > ul { padding-left: 0; }
    .toc a { color: #0366d6; }
  `,

  'github-dark': `
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
      font-size: 16px;
      line-height: 1.6;
      color: #c9d1d9;
      background: #0d1117;
      max-width: 980px;
      margin: 0 auto;
      padding: 2em;
    }
    h1, h2, h3, h4, h5, h6 { color: #e6edf3; margin-top: 24px; margin-bottom: 16px; font-weight: 600; }
    h1, h2 { padding-bottom: 0.3em; border-bottom: 1px solid #21262d; }
    code { background: #161b22; padding: 0.2em 0.4em; border-radius: 3px; font-size: 85%; }
    pre { background: #161b22; padding: 16px; border-radius: 6px; overflow: auto; }
    pre code { background: none; padding: 0; }
    blockquote { color: #8b949e; border-left: 0.25em solid #30363d; padding: 0 1em; }
    table { border-collapse: collapse; width: 100%; }
    table th, table td { padding: 6px 13px; border: 1px solid #30363d; }
    table tr:nth-child(2n) { background: #161b22; }
    table th { background: #21262d; }
    a { color: #58a6ff; }
    hr { border: none; border-top: 1px solid #21262d; }
  `,

  minimal: `
    body {
      font-family: "Georgia", "Times New Roman", serif;
      font-size: 17px;
      line-height: 1.8;
      color: #333;
      max-width: 700px;
      margin: 0 auto;
      padding: 2em;
    }
    h1, h2, h3, h4, h5, h6 { font-family: "Helvetica Neue", Arial, sans-serif; margin-top: 2em; }
    h1 { font-size: 1.8em; }
    h2 { font-size: 1.4em; }
    code { font-family: "SF Mono", Monaco, Consolas, monospace; background: #f5f5f5; padding: 0.15em 0.3em; border-radius: 2px; font-size: 0.85em; }
    pre { background: #f5f5f5; padding: 1em; border-radius: 4px; overflow: auto; }
    pre code { background: none; padding: 0; }
    blockquote { border-left: 3px solid #ccc; padding-left: 1em; color: #666; font-style: italic; }
    table { border-collapse: collapse; width: 100%; margin: 1em 0; }
    table th, table td { padding: 8px 12px; border-bottom: 1px solid #ddd; text-align: left; }
    table th { font-weight: bold; }
    a { color: #1a0dab; }
    img { max-width: 100%; }
  `,
};

// ---------------------------------------------------------------------------
// KaTeX CSS (inlined to avoid external dependency at render time)
// ---------------------------------------------------------------------------
function getKatexCSS() {
  try {
    const katexCSSPath = require.resolve('katex/dist/katex.min.css');
    return fs.readFileSync(katexCSSPath, 'utf-8');
  } catch {
    // Fallback: minimal katex styling
    return `
      .katex { font-size: 1.1em; }
      .katex-display { display: block; margin: 1em 0; text-align: center; }
    `;
  }
}

// ---------------------------------------------------------------------------
// highlight.js CSS
// ---------------------------------------------------------------------------
function getHighlightCSS() {
  try {
    const hljsPath = path.join(
      path.dirname(require.resolve('highlight.js/package.json')),
      'styles', 'github.css'
    );
    return fs.readFileSync(hljsPath, 'utf-8');
  } catch {
    return '';
  }
}

// ---------------------------------------------------------------------------
// Markdown → HTML
// ---------------------------------------------------------------------------
function renderMarkdown(content, options = {}) {
  const md = markdownIt({
    html: true,
    linkify: true,
    typographer: true,
    breaks: false,
  });

  // Plugins
  md.use(highlightjs, { auto: true, code: true });
  md.use(texmath, { engine: katex, delimiters: 'dollars', katexOptions: { throwOnError: false } });
  md.use(anchor, { permalink: false });
  md.use(footnote);

  if (options.toc) {
    md.use(tocPlugin, {
      containerClass: 'toc',
      listType: 'ul',
    });
    // Prepend TOC placeholder
    content = '${toc}\n\n' + content;
  }

  return md.render(content);
}

// ---------------------------------------------------------------------------
// Build full HTML document
// ---------------------------------------------------------------------------
function buildHTML(markdownBody, options = {}) {
  const theme = THEMES[options.theme] || THEMES.github;
  const katexCSS = getKatexCSS();
  const highlightCSS = getHighlightCSS();

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${options.title || 'Document'}</title>
  <style>${katexCSS}</style>
  <style>${highlightCSS}</style>
  <style>${theme}</style>
  <style>
    /* Print-specific styles */
    @media print {
      body { margin: 0; padding: 1em; }
      pre { white-space: pre-wrap; word-wrap: break-word; }
      a[href]::after { content: none !important; }
    }
    /* Pagebreak support: <!-- pagebreak --> renders as <hr class="pagebreak"> */
    hr.pagebreak {
      page-break-after: always;
      border: none;
      margin: 0;
      padding: 0;
    }
  </style>
</head>
<body>
${markdownBody}
</body>
</html>`;
}

// ---------------------------------------------------------------------------
// Core conversion function
// ---------------------------------------------------------------------------
async function convertMarkdown(options) {
  const {
    inputPath,
    outputPath: userOutputPath,
    type = 'pdf',
    theme = 'github',
    chromePath = null,
    waitTimeout = 0,
    toc = false,
    puppeteerConfig = {},
    screenshotConfig = {},
    noSandbox = false,
  } = options;

  // 1. Read & parse front-matter
  const raw = fs.readFileSync(inputPath, 'utf-8');
  const { data: frontMatter, content: markdownContent } = matter(raw);

  // 2. Merge front-matter puppeteer config with CLI config
  const fmPuppeteer = frontMatter.puppeteer || {};
  const fmScreenshot = frontMatter.screenshot || {};

  // 3. Render Markdown → HTML
  const title = frontMatter.title || path.basename(inputPath, path.extname(inputPath));
  const htmlBody = renderMarkdown(markdownContent, { toc });
  // Support <!-- pagebreak --> syntax
  const htmlBodyProcessed = htmlBody.replace(
    /<!--\s*pagebreak\s*-->/gi,
    '<hr class="pagebreak">'
  );
  const fullHTML = buildHTML(htmlBodyProcessed, { theme, title });

  // 4. Determine output path
  const ext = type === 'pdf' ? '.pdf' : type === 'png' ? '.png' : '.jpeg';
  const outputPath = userOutputPath || inputPath.replace(/\.md$/i, ext);

  // 5. Launch Puppeteer
  const isContainer = fs.existsSync('/.dockerenv') ||
    (fs.existsSync('/proc/1/cgroup') &&
     fs.readFileSync('/proc/1/cgroup', 'utf-8').includes('docker'));

  const launchArgs = [];
  if (isContainer || noSandbox) {
    launchArgs.push('--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage');
  }
  // Merge user-provided puppeteer args
  if (fmPuppeteer.args) {
    launchArgs.push(...fmPuppeteer.args);
  }

  const launchOptions = {
    headless: 'new',
    args: launchArgs,
  };
  if (chromePath) {
    launchOptions.executablePath = chromePath;
  } else if (process.env.PUPPETEER_EXECUTABLE_PATH) {
    launchOptions.executablePath = process.env.PUPPETEER_EXECUTABLE_PATH;
  }

  const browser = await puppeteer.launch(launchOptions);

  try {
    const page = await browser.newPage();

    // 6. Set viewport for screenshots
    if (type !== 'pdf') {
      const width = fmScreenshot.width || screenshotConfig.width || 1200;
      const deviceScaleFactor = fmScreenshot.deviceScaleFactor || screenshotConfig.scale || 2;
      await page.setViewport({ width, height: 800, deviceScaleFactor });
    }

    // 7. Load HTML
    await page.setContent(fullHTML, {
      waitUntil: 'networkidle0',
      timeout: 30000,
    });

    // 8. Extra wait (for async rendering like Mermaid)
    const wait = fmPuppeteer.timeout || waitTimeout;
    if (wait > 0) {
      await new Promise(r => setTimeout(r, wait));
    }

    // 9. Export
    if (type === 'pdf') {
      // Build PDF options
      const pdfOpts = {
        path: outputPath,
        format: fmPuppeteer.format || puppeteerConfig.format || 'A4',
        landscape: fmPuppeteer.landscape || puppeteerConfig.landscape || false,
        printBackground: fmPuppeteer.printBackground !== undefined
          ? fmPuppeteer.printBackground
          : (puppeteerConfig.printBackground !== undefined ? puppeteerConfig.printBackground : true),
        margin: fmPuppeteer.margin || puppeteerConfig.margin || {
          top: '10mm', right: '10mm', bottom: '10mm', left: '10mm',
        },
        scale: fmPuppeteer.scale || puppeteerConfig.scale || 1,
      };

      // Header/Footer
      if (fmPuppeteer.displayHeaderFooter || puppeteerConfig.displayHeaderFooter) {
        pdfOpts.displayHeaderFooter = true;
        pdfOpts.headerTemplate = fmPuppeteer.headerTemplate || puppeteerConfig.headerTemplate || '<span></span>';
        pdfOpts.footerTemplate = fmPuppeteer.footerTemplate || puppeteerConfig.footerTemplate ||
          '<div style="font-size:8px;width:100%;text-align:center;"><span class="pageNumber"></span> / <span class="totalPages"></span></div>';
      }

      await page.pdf(pdfOpts);
    } else {
      // Screenshot
      const screenshotOpts = {
        path: outputPath,
        type: type,
        fullPage: fmScreenshot.fullPage !== undefined ? fmScreenshot.fullPage : true,
      };
      if (type === 'jpeg') {
        screenshotOpts.quality = fmScreenshot.quality || screenshotConfig.quality || 80;
      }

      await page.screenshot(screenshotOpts);
    }

    console.log(`✅ Exported: ${outputPath}`);
    return { outputPath, type, success: true };
  } finally {
    await browser.close();
  }
}

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------
function parseArgs(argv) {
  const args = argv.slice(2);
  const opts = {
    inputPath: null,
    outputPath: null,
    type: 'pdf',
    theme: 'github',
    chromePath: null,
    waitTimeout: 0,
    toc: false,
    noSandbox: false,
    puppeteerConfig: {},
    screenshotConfig: {},
  };

  let i = 0;
  while (i < args.length) {
    const arg = args[i];
    switch (arg) {
      case '--type':
        opts.type = args[++i];
        break;
      case '-o': case '--output':
        opts.outputPath = args[++i];
        break;
      case '--format':
        opts.puppeteerConfig.format = args[++i];
        break;
      case '--landscape':
        opts.puppeteerConfig.landscape = true;
        break;
      case '--no-background':
        opts.puppeteerConfig.printBackground = false;
        break;
      case '--margin':
        { const m = args[++i];
          opts.puppeteerConfig.margin = { top: m, right: m, bottom: m, left: m };
        }
        break;
      case '--margin-top':
        opts.puppeteerConfig.margin = opts.puppeteerConfig.margin || {};
        opts.puppeteerConfig.margin.top = args[++i];
        break;
      case '--margin-bottom':
        opts.puppeteerConfig.margin = opts.puppeteerConfig.margin || {};
        opts.puppeteerConfig.margin.bottom = args[++i];
        break;
      case '--margin-left':
        opts.puppeteerConfig.margin = opts.puppeteerConfig.margin || {};
        opts.puppeteerConfig.margin.left = args[++i];
        break;
      case '--margin-right':
        opts.puppeteerConfig.margin = opts.puppeteerConfig.margin || {};
        opts.puppeteerConfig.margin.right = args[++i];
        break;
      case '--quality':
        opts.screenshotConfig.quality = parseInt(args[++i], 10);
        break;
      case '--scale':
        opts.screenshotConfig.scale = parseFloat(args[++i]);
        break;
      case '--width':
        opts.screenshotConfig.width = parseInt(args[++i], 10);
        break;
      case '--theme':
        opts.theme = args[++i];
        break;
      case '--chrome-path':
        opts.chromePath = args[++i];
        break;
      case '--wait':
        opts.waitTimeout = parseInt(args[++i], 10);
        break;
      case '--toc':
        opts.toc = true;
        break;
      case '--no-sandbox':
        opts.noSandbox = true;
        break;
      case '--header-footer':
        opts.puppeteerConfig.displayHeaderFooter = true;
        break;
      case '--footer-template':
        opts.puppeteerConfig.footerTemplate = args[++i];
        break;
      case '--header-template':
        opts.puppeteerConfig.headerTemplate = args[++i];
        break;
      case '-h': case '--help':
        printHelp();
        process.exit(0);
        break;
      default:
        if (!arg.startsWith('-') && !opts.inputPath) {
          opts.inputPath = arg;
        } else {
          console.error(`Unknown option: ${arg}`);
          process.exit(1);
        }
    }
    i++;
  }

  return opts;
}

function printHelp() {
  console.log(`
md2pdf-export — Convert Markdown to PDF/PNG/JPEG via Puppeteer

Usage:
  node md2pdf.js <input.md> [options]

Options:
  --type <pdf|png|jpeg>     Output type (default: pdf)
  -o, --output <path>       Output file path (default: input.pdf)
  --format <format>         Paper format: A3, A4, A5, Letter, Legal, Tabloid
  --landscape               Landscape orientation
  --no-background           Disable background graphics in PDF
  --margin <size>           Uniform margin (e.g. "20mm")
  --margin-top <size>       Top margin
  --margin-bottom <size>    Bottom margin
  --margin-left <size>      Left margin
  --margin-right <size>     Right margin
  --quality <1-100>         JPEG quality (default: 80)
  --scale <factor>          Device scale factor for screenshots (default: 2)
  --width <px>              Viewport width for screenshots (default: 1200)
  --theme <name>            CSS theme: github, github-dark, minimal
  --chrome-path <path>      Path to Chrome/Chromium executable
  --wait <ms>               Extra wait time after page load
  --toc                     Generate table of contents
  --no-sandbox              Disable Chrome sandbox (Docker)
  --header-footer           Show header and footer in PDF
  --footer-template <html>  Custom footer HTML template
  --header-template <html>  Custom header HTML template
  -h, --help                Show this help
`);
}

// ---------------------------------------------------------------------------
// Module exports + CLI entry
// ---------------------------------------------------------------------------
module.exports = { convertMarkdown, renderMarkdown, buildHTML, THEMES };

if (require.main === module) {
  const opts = parseArgs(process.argv);

  if (!opts.inputPath) {
    console.error('Error: No input file specified');
    printHelp();
    process.exit(1);
  }

  if (!fs.existsSync(opts.inputPath)) {
    console.error(`Error: File not found: ${opts.inputPath}`);
    process.exit(1);
  }

  convertMarkdown(opts)
    .then(() => process.exit(0))
    .catch(err => {
      console.error('Export failed:', err.message);
      process.exit(1);
    });
}
