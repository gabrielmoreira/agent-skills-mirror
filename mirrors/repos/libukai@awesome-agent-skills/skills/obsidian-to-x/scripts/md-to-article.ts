import fs from 'node:fs';
import { mkdir, writeFile } from 'node:fs/promises';
import https from 'node:https';
import os from 'node:os';
import path from 'node:path';
import process from 'node:process';
import { createHash } from 'node:crypto';

import frontMatter from 'front-matter';
import hljs from 'highlight.js/lib/common';
import { Lexer, Marked, type RendererObject, type Tokens } from 'marked';
import { unified } from 'unified';
import remarkCjkFriendly from 'remark-cjk-friendly';
import remarkParse from 'remark-parse';
import remarkStringify from 'remark-stringify';

import {
  readObsidianConfig,
  resolveLocalImagePath,
  stripObsidianWikiLink,
} from './obsidian-resolver.js';

// ─── Types ───────────────────────────────────────────────────────────

interface ImageInfo {
  placeholder: string;
  localPath: string;
  originalPath: string;
  blockIndex: number;
}

interface CodeBlockInfo {
  placeholder: string;
  language: string;
  code: string;
  blockIndex: number;
}

interface ParsedMarkdown {
  title: string;
  coverImage: string | null;
  contentImages: ImageInfo[];
  codeBlocks: CodeBlockInfo[];
  html: string;
  totalBlocks: number;
}

type FrontmatterFields = Record<string, unknown>;

// ─── Frontmatter helpers ─────────────────────────────────────────────

function parseFrontmatter(content: string): { frontmatter: FrontmatterFields; body: string } {
  try {
    const parsed = frontMatter<FrontmatterFields>(content);
    return {
      frontmatter: parsed.attributes ?? {},
      body: parsed.body,
    };
  } catch {
    return { frontmatter: {}, body: content };
  }
}

function stripWrappingQuotes(value: string): string {
  if (!value) return value;
  const doubleQuoted = value.startsWith('"') && value.endsWith('"');
  const singleQuoted = value.startsWith("'") && value.endsWith("'");
  const cjkDoubleQuoted = value.startsWith('\u201c') && value.endsWith('\u201d');
  const cjkSingleQuoted = value.startsWith('\u2018') && value.endsWith('\u2019');
  if (doubleQuoted || singleQuoted || cjkDoubleQuoted || cjkSingleQuoted) {
    return value.slice(1, -1).trim();
  }
  return value.trim();
}

function toFrontmatterString(value: unknown): string | undefined {
  if (typeof value === 'string') {
    return stripWrappingQuotes(value);
  }
  if (typeof value === 'number' || typeof value === 'boolean') {
    return String(value);
  }
  return undefined;
}

function pickFirstString(frontmatter: FrontmatterFields, keys: string[]): string | undefined {
  for (const key of keys) {
    const value = toFrontmatterString(frontmatter[key]);
    if (value) return value;
  }
  return undefined;
}

function findCoverImageNearMarkdown(baseDir: string): string | null {
  const candidateDirs = [baseDir, path.join(baseDir, 'imgs')];
  const coverPattern = /^cover\.(png|jpe?g|webp)$/i;

  for (const dir of candidateDirs) {
    try {
      if (!fs.existsSync(dir) || !fs.statSync(dir).isDirectory()) {
        continue;
      }

      const match = fs.readdirSync(dir).find((entry) => coverPattern.test(entry));
      if (match) {
        return path.join(dir, match);
      }
    } catch {
      continue;
    }
  }

  return null;
}

function extractTitleFromMarkdown(markdown: string): string {
  const tokens = Lexer.lex(markdown, { gfm: true, breaks: true });
  for (const token of tokens) {
    if (token.type === 'heading' && token.depth === 1) {
      return stripWrappingQuotes(token.text);
    }
  }
  return '';
}

// ─── Image download helpers ──────────────────────────────────────────

function downloadFile(url: string, destPath: string, maxRedirects = 5): Promise<void> {
  return new Promise((resolve, reject) => {
    if (!url.startsWith('https://')) {
      reject(new Error(`Refusing non-HTTPS download: ${url}`));
      return;
    }
    if (maxRedirects <= 0) {
      reject(new Error('Too many redirects'));
      return;
    }
    const file = fs.createWriteStream(destPath);

    const request = https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (response) => {
      if (response.statusCode === 301 || response.statusCode === 302) {
        const redirectUrl = response.headers.location;
        if (redirectUrl) {
          file.close();
          fs.unlinkSync(destPath);
          downloadFile(redirectUrl, destPath, maxRedirects - 1).then(resolve).catch(reject);
          return;
        }
      }

      if (response.statusCode !== 200) {
        file.close();
        fs.unlinkSync(destPath);
        reject(new Error(`Failed to download: ${response.statusCode}`));
        return;
      }

      response.pipe(file);
      file.on('finish', () => {
        file.close();
        resolve();
      });
    });

    request.on('error', (err) => {
      file.close();
      fs.unlink(destPath, () => {});
      reject(err);
    });

    request.setTimeout(30000, () => {
      request.destroy();
      reject(new Error('Download timeout'));
    });
  });
}

function getImageExtension(urlOrPath: string): string {
  const match = urlOrPath.match(/\.(jpg|jpeg|png|gif|webp)(\?|$)/i);
  return match ? match[1]!.toLowerCase() : 'png';
}

// ─── Image path resolution (async, handles URLs + local) ────────────

async function resolveImagePath(
  imagePath: string,
  projectRoot: string,
  tempDir: string,
  options?: {
    attachmentFolder?: string;
    sourceFileDir?: string;
  }
): Promise<string> {
  const cleanPath = stripObsidianWikiLink(imagePath);

  // HTTP URLs: skip (non-HTTPS)
  if (cleanPath.startsWith('http://')) {
    console.error(`[md-to-article] Skipping non-HTTPS image: ${cleanPath}`);
    return '';
  }

  // HTTPS URLs: download to tempDir
  if (cleanPath.startsWith('https://')) {
    const hash = createHash('md5').update(cleanPath).digest('hex').slice(0, 8);
    const ext = getImageExtension(cleanPath);
    const localPath = path.join(tempDir, `remote_${hash}.${ext}`);

    if (!fs.existsSync(localPath)) {
      console.error(`[md-to-article] Downloading: ${cleanPath}`);
      await downloadFile(cleanPath, localPath);
    }
    return localPath;
  }

  // Local paths: delegate to shared Obsidian-aware resolver
  return resolveLocalImagePath(cleanPath, projectRoot, options);
}

// ─── Obsidian syntax preprocessing ──────────────────────────────────

const IMAGE_EXTENSIONS = /\.(png|jpg|jpeg|gif|webp|svg)$/i;

/**
 * Preprocess Obsidian-specific syntax before Marked parser.
 * Converts wiki-link images, removes callouts, resolves local image paths.
 */
function preprocessObsidianSyntax(
  content: string,
  projectRoot: string,
  attachmentFolder: string | undefined,
  sourceFileDir: string,
): string {
  let result = content;
  const resolverOpts = { attachmentFolder, sourceFileDir };

  // 1. Convert 封面 field: "![[path]]" → absolute path
  //    Must happen BEFORE image syntax conversion
  const coverMatch = result.match(
    /^封面:\s*"?(?:\[#\d+\]\s*)?!\[\[([^\]]+)\]\]"?/m
  );
  if (coverMatch) {
    const coverPath = coverMatch[1]!;
    const resolved = resolveLocalImagePath(coverPath, projectRoot, resolverOpts);
    result = result.replace(/^封面:.*$/m, `封面: ${resolved}`);
  }

  // 2. Convert Obsidian wiki-link images to standard Markdown
  //    ![[img.png]] → ![](resolved_path)
  //    ![[img.png|alt text]] → ![](resolved_path)
  //    ![[wechatAccountCard]] → removed (non-image extension)
  result = result.replace(
    /!\[\[([^\]]+)\]\]/g,
    (_match, inner: string) => {
      const cleaned = stripObsidianWikiLink(`![[${inner}]]`);
      // Non-image wikilinks (no image extension) → remove
      if (!IMAGE_EXTENSIONS.test(cleaned)) {
        return '';
      }
      const resolved = resolveLocalImagePath(cleaned, projectRoot, resolverOpts);
      return `![](${resolved})`;
    }
  );

  // 3. Remove Obsidian callout syntax lines: > [!type] Title
  result = result.replace(/^> \[![a-z]+\] .+\n/gm, '');

  // 4. Fix existing standard Markdown image paths (non-URL, non-absolute)
  //    ![alt](relative/path) → ![alt](resolved_absolute_path)
  result = result.replace(
    /!\[([^\]]*)\]\(([^)]+)\)/g,
    (match, alt: string, imagePath: string) => {
      // Skip URLs and already-absolute paths
      if (/^https?:\/\//i.test(imagePath) || path.isAbsolute(imagePath)) {
        return match;
      }
      const resolved = resolveLocalImagePath(imagePath, projectRoot, resolverOpts);
      return `![${alt}](${resolved})`;
    }
  );

  return result;
}

// ─── HTML helpers ────────────────────────────────────────────────────

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function preprocessCjkMarkdown(markdown: string): string {
  try {
    const processor = unified()
      .use(remarkParse)
      .use(remarkCjkFriendly)
      .use(remarkStringify);

    const result = String(processor.processSync(markdown));
    return result.replace(/&#x([0-9A-Fa-f]+);/g, (_, hex: string) => String.fromCodePoint(parseInt(hex, 16)));
  } catch {
    return markdown;
  }
}

// ─── Markdown → HTML conversion ─────────────────────────────────────

function convertMarkdownToHtml(
  markdown: string,
  imageCallback: (src: string, alt: string) => string,
  codeBlockCallback: (lang: string, code: string) => string
): { html: string; totalBlocks: number } {
  const preprocessedMarkdown = preprocessCjkMarkdown(markdown);
  const blockTokens = Lexer.lex(preprocessedMarkdown, { gfm: true, breaks: true });

  const renderer: RendererObject = {
    heading({ depth, tokens }: Tokens.Heading): string {
      if (depth === 1) {
        return '';
      }
      return `<h2>${this.parser.parseInline(tokens)}</h2>`;
    },

    paragraph({ tokens }: Tokens.Paragraph): string {
      const text = this.parser.parseInline(tokens).trim();
      if (!text) return '';
      return `<p>${text}</p>`;
    },

    blockquote({ tokens }: Tokens.Blockquote): string {
      // Handle annotation format: [#number] title → **title**
      if (tokens.length > 0 && tokens[0]?.type === 'paragraph') {
        const firstPara = tokens[0] as Tokens.Paragraph;
        if (firstPara.tokens && firstPara.tokens.length > 0) {
          const firstToken = firstPara.tokens[0];
          if (firstToken?.type === 'text') {
            const textToken = firstToken as Tokens.Text;
            const match = textToken.text.match(/^\[#\d+\]\s+(.*)$/);
            if (match) {
              const titleText = match[1]?.trim();
              if (titleText) {
                textToken.text = `**${titleText}**`;
              } else {
                firstPara.tokens.shift();
              }
            }
          }
        }
      }
      return `<blockquote>${this.parser.parse(tokens)}</blockquote>`;
    },

    code({ text, lang = '' }: Tokens.Code): string {
      const language = lang.split(/\s+/)[0]!.toLowerCase();
      const source = text.replace(/\n$/, '');
      return codeBlockCallback(language, source);
    },

    image({ href, text }: Tokens.Image): string {
      if (!href) return '';
      return imageCallback(href, text ?? '');
    },

    link({ href, title, tokens, text }: Tokens.Link): string {
      const label = tokens?.length ? this.parser.parseInline(tokens) : escapeHtml(text || href || '');
      if (!href) return label;

      const titleAttr = title ? ` title="${escapeHtml(title)}"` : '';
      return `<a href="${escapeHtml(href)}"${titleAttr} rel="noopener noreferrer nofollow">${label}</a>`;
    },
  };

  const parser = new Marked({
    gfm: true,
    breaks: true,
  });
  parser.use({ renderer });

  const rendered = parser.parse(preprocessedMarkdown);
  if (typeof rendered !== 'string') {
    throw new Error('Unexpected async markdown parse result');
  }

  const totalBlocks = blockTokens.filter((token) => {
    if (token.type === 'space') return false;
    if (token.type === 'heading' && token.depth === 1) return false;
    return true;
  }).length;

  return {
    html: rendered,
    totalBlocks,
  };
}

// ─── Main export: parseMarkdown ─────────────────────────────────────

export async function parseMarkdown(
  markdownPath: string,
  options?: {
    coverImage?: string;
    title?: string;
    tempDir?: string;
    projectRoot?: string;
  },
): Promise<ParsedMarkdown> {
  const projectRoot = options?.projectRoot ?? process.cwd();
  const sourceFileDir = path.resolve(path.dirname(markdownPath));
  const tempDir = options?.tempDir ?? path.join(os.tmpdir(), 'x-article-images');

  await mkdir(tempDir, { recursive: true });

  // Read Obsidian config for attachment folder
  const obsConfig = readObsidianConfig(projectRoot);
  const attachmentFolder = obsConfig.attachmentFolderPath;
  const resolverOpts = { attachmentFolder, sourceFileDir };

  // Preprocess: convert Obsidian syntax before parsing
  const rawContent = fs.readFileSync(markdownPath, 'utf-8');
  const preprocessed = preprocessObsidianSyntax(rawContent, projectRoot, attachmentFolder, sourceFileDir);

  const { frontmatter, body } = parseFrontmatter(preprocessed);

  // Resolve title
  let title = stripWrappingQuotes(options?.title ?? '') || pickFirstString(frontmatter, ['title', '标题']) || '';
  if (!title) {
    title = extractTitleFromMarkdown(body);
  }
  if (!title) {
    title = path.basename(markdownPath, path.extname(markdownPath));
  }

  // Resolve cover image
  let coverImagePath = stripWrappingQuotes(options?.coverImage ?? '') || pickFirstString(frontmatter, [
    'cover_image',
    'coverImage',
    'cover',
    'image',
    'featureImage',
    'feature_image',
    '封面',
    '配图',
  ]) || null;
  if (!coverImagePath) {
    coverImagePath = findCoverImageNearMarkdown(sourceFileDir);
  }

  // Convert Markdown body to HTML with placeholders
  const images: Array<{ src: string; alt: string; blockIndex: number }> = [];
  let imageCounter = 0;
  const codeBlocks: CodeBlockInfo[] = [];
  let codeBlockCounter = 0;

  const { html, totalBlocks } = convertMarkdownToHtml(
    body,
    (src, alt) => {
      const placeholder = `XIMGPH_${++imageCounter}`;
      images.push({ src, alt, blockIndex: -1 });
      return placeholder;
    },
    (lang, code) => {
      const placeholder = `XCODEPH_${++codeBlockCounter}`;
      codeBlocks.push({ placeholder, language: lang, code, blockIndex: -1 });
      return placeholder;
    }
  );

  // Track which HTML line each image placeholder appears on
  const htmlLines = html.split('\n');
  for (let i = 0; i < images.length; i++) {
    const placeholder = `XIMGPH_${i + 1}`;
    for (let lineIndex = 0; lineIndex < htmlLines.length; lineIndex++) {
      const regex = new RegExp(`\\b${placeholder}\\b`);
      if (regex.test(htmlLines[lineIndex]!)) {
        images[i]!.blockIndex = lineIndex;
        break;
      }
    }
  }

  // Resolve image paths (local paths are already absolute from preprocessing,
  // but URL images still need downloading)
  const contentImages: ImageInfo[] = [];
  let firstImageAsCover: string | null = null;

  for (let i = 0; i < images.length; i++) {
    const img = images[i]!;
    const localPath = await resolveImagePath(img.src, projectRoot, tempDir, resolverOpts);

    if (i === 0 && !coverImagePath) {
      firstImageAsCover = localPath;
    }

    contentImages.push({
      placeholder: `XIMGPH_${i + 1}`,
      localPath,
      originalPath: img.src,
      blockIndex: img.blockIndex,
    });
  }

  const finalHtml = html.replace(/\n{3,}/g, '\n\n').trim();

  // Resolve cover image path
  let resolvedCoverImage: string | null = null;
  if (coverImagePath) {
    resolvedCoverImage = await resolveImagePath(coverImagePath, projectRoot, tempDir, resolverOpts);
  } else if (firstImageAsCover) {
    resolvedCoverImage = firstImageAsCover;
  }

  return {
    title,
    coverImage: resolvedCoverImage,
    contentImages,
    codeBlocks,
    html: finalHtml,
    totalBlocks,
  };
}

// ─── CLI ─────────────────────────────────────────────────────────────

function printUsage(): never {
  console.log(`Convert Obsidian/Markdown to HTML for X Article publishing

Usage:
  bun md-to-article.ts <markdown_file> [options]

Options:
  --title <title>       Override title from frontmatter
  --cover <image>       Override cover image from frontmatter
  --output <json|html>  Output format (default: json)
  --html-only           Output only the HTML content
  --save-html <path>    Save HTML to file

Supports Obsidian syntax:
  - ![[image.png]] wiki-link images
  - 封面 / 配图 / cover_image frontmatter fields
  - 标题 / title frontmatter fields
  - [!callout] blockquote syntax (removed)
  - [#annotation] blockquote syntax (converted to bold)

Example:
  bun md-to-article.ts article.md --output json
  bun md-to-article.ts article.md --html-only > /tmp/article.html
  bun md-to-article.ts article.md --save-html /tmp/article.html
`);
  process.exit(0);
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    printUsage();
  }

  let markdownPath: string | undefined;
  let title: string | undefined;
  let coverImage: string | undefined;
  let outputFormat: 'json' | 'html' = 'json';
  let htmlOnly = false;
  let saveHtmlPath: string | undefined;

  for (let i = 0; i < args.length; i++) {
    const arg = args[i]!;
    if (arg === '--title' && args[i + 1]) {
      title = args[++i];
    } else if (arg === '--cover' && args[i + 1]) {
      coverImage = args[++i];
    } else if (arg === '--output' && args[i + 1]) {
      outputFormat = args[++i] as 'json' | 'html';
    } else if (arg === '--html-only') {
      htmlOnly = true;
    } else if (arg === '--save-html' && args[i + 1]) {
      saveHtmlPath = args[++i];
    } else if (!arg.startsWith('-')) {
      markdownPath = arg;
    }
  }

  if (!markdownPath) {
    console.error('Error: Markdown file path required');
    process.exit(1);
  }

  if (!fs.existsSync(markdownPath)) {
    console.error(`Error: File not found: ${markdownPath}`);
    process.exit(1);
  }

  const result = await parseMarkdown(markdownPath, { title, coverImage });

  if (saveHtmlPath) {
    await writeFile(saveHtmlPath, result.html, 'utf-8');
    console.error(`[md-to-article] HTML saved to: ${saveHtmlPath}`);
  }

  if (htmlOnly) {
    console.log(result.html);
  } else if (outputFormat === 'html') {
    console.log(result.html);
  } else {
    console.log(JSON.stringify(result, null, 2));
  }
}

await main().catch((err) => {
  console.error(`Error: ${err instanceof Error ? err.message : String(err)}`);
  process.exit(1);
});
