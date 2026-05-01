#!/usr/bin/env bun
/**
 * Extract plain text and images from Obsidian Markdown for X posts
 *
 * Usage:
 *   bun extract-post-content.ts <input.md>
 */

import { readFileSync, mkdirSync, existsSync } from 'node:fs';
import { resolve, join, basename, dirname } from 'node:path';
import process from 'node:process';
import { spawn } from 'node:child_process';
import frontMatter from 'front-matter';

import {
  readObsidianConfig,
  resolveLocalImagePath,
} from './obsidian-resolver.js';

interface PostContent {
  text: string;
  images: string[];
}

/**
 * Check if a path is a URL
 */
function isUrl(path: string): boolean {
  return /^https?:\/\//i.test(path);
}

/**
 * Download a single image from URL
 */
async function downloadImage(url: string, outputPath: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const curl = spawn('curl', ['-s', '-L', '-o', outputPath, url]);
    curl.on('close', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`curl failed with code ${code}`));
      }
    });
    curl.on('error', reject);
  });
}

/**
 * Download multiple images in parallel
 */
async function downloadImagesParallel(urls: string[], outputDir?: string): Promise<Map<string, string>> {
  const downloadDir = outputDir ?? join(process.cwd(), '.temp', `x-post-images-${Date.now()}`);
  mkdirSync(downloadDir, { recursive: true });

  const urlToPath = new Map<string, string>();
  const downloadPromises = urls.map(async (url, index) => {
    // Extract extension from URL or default to .jpg
    const urlPath = new URL(url).pathname;
    const ext = urlPath.match(/\.(png|jpg|jpeg|gif|webp)(\?|$)/i)?.[1] || 'jpg';
    const filename = `image${index + 1}.${ext}`;
    const outputPath = join(downloadDir, filename);

    try {
      await downloadImage(url, outputPath);
      urlToPath.set(url, outputPath);
      console.error(`[download] ✓ ${basename(outputPath)}`);
    } catch (error) {
      console.error(`[download] ✗ Failed to download ${url}: ${error}`);
    }
  });

  await Promise.all(downloadPromises);
  return urlToPath;
}

async function extractPostContent(markdownPath: string, projectRoot: string = process.cwd(), options?: { outputDir?: string }): Promise<PostContent> {
  const content = readFileSync(markdownPath, 'utf-8');

  // Read Obsidian configuration
  const config = readObsidianConfig(projectRoot);
  const attachmentFolder = config.attachmentFolderPath;

  if (attachmentFolder) {
    console.error(`[config] Using attachment folder: ${attachmentFolder}`);
  }

  // Parse frontmatter
  let body: string;
  try {
    const parsed = frontMatter(content);
    body = parsed.body;
  } catch {
    body = content;
  }

  // Extract images and convert to absolute paths
  const imagePaths: string[] = [];
  const imageUrls: string[] = [];

  // Match standard Markdown: ![alt](path)
  const standardImageRegex = /!\[([^\]]*)\]\(([^)]+)\)/g;
  let match;

  while ((match = standardImageRegex.exec(body)) !== null) {
    const imagePath = match[2];
    if (isUrl(imagePath)) {
      imageUrls.push(imagePath);
    } else {
      // Use resolveImagePath to find the correct path
      const absolutePath = resolveLocalImagePath(imagePath, projectRoot, { attachmentFolder });
      imagePaths.push(absolutePath);
    }
  }

  // Match Obsidian syntax: ![[path]]
  const obsidianImageRegex = /!\[\[([^\]]+)\]\]/g;
  while ((match = obsidianImageRegex.exec(body)) !== null) {
    const imagePath = match[1];
    if (isUrl(imagePath)) {
      imageUrls.push(imagePath);
    } else {
      // Use resolveImagePath to find the correct path
      const absolutePath = resolveLocalImagePath(imagePath, projectRoot, { attachmentFolder });
      imagePaths.push(absolutePath);
    }
  }

  // Download network images in parallel
  let urlToPath = new Map<string, string>();
  if (imageUrls.length > 0) {
    console.error(`[download] Downloading ${imageUrls.length} image(s) in parallel...`);
    urlToPath = await downloadImagesParallel(imageUrls, options?.outputDir);
  }

  // Combine local paths and downloaded paths (preserve order)
  const images: string[] = [];

  // Re-parse to maintain original order
  const allImageRegex = /!\[([^\]]*)\]\(([^)]+)\)|!\[\[([^\]]+)\]\]/g;
  while ((match = allImageRegex.exec(body)) !== null) {
    const imagePath = match[2] || match[3];
    if (isUrl(imagePath)) {
      const downloadedPath = urlToPath.get(imagePath);
      if (downloadedPath) {
        images.push(downloadedPath);
      }
    } else {
      // Use resolveImagePath to find the correct path
      const absolutePath = resolveLocalImagePath(imagePath, projectRoot, { attachmentFolder });
      images.push(absolutePath);
    }
  }

  // Remove all Markdown syntax to get plain text
  let text = body;

  // Remove images (both standard Markdown and Obsidian syntax)
  text = text.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, ''); // ![alt](path)
  text = text.replace(/!\[\[([^\]]+)\]\]/g, ''); // ![[path]]

  // Remove links but keep text: [text](url) -> text
  text = text.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');

  // Remove bold/italic: **text** or *text* -> text
  text = text.replace(/\*\*([^*]+)\*\*/g, '$1');
  text = text.replace(/\*([^*]+)\*/g, '$1');

  // Remove headers: ## Header -> Header
  text = text.replace(/^#{1,6}\s+(.+)$/gm, '$1');

  // Remove code blocks
  text = text.replace(/```[\s\S]*?```/g, '');

  // Remove inline code: `code` -> code
  text = text.replace(/`([^`]+)`/g, '$1');

  // Remove blockquotes: > text -> text
  text = text.replace(/^>\s*/gm, '');

  // Remove horizontal rules
  text = text.replace(/^[-*_]{3,}$/gm, '');

  // Remove HTML tags
  text = text.replace(/<[^>]+>/g, '');

  // Unescape escaped periods in numbered lists at line start: 1\. -> 1.
  // Only match at the beginning of lines (with optional whitespace before)
  text = text.replace(/^(\s*)(\d+)\\\.\s/gm, '$1$2. ');

  // Clean up multiple blank lines
  text = text.replace(/\n{3,}/g, '\n\n');

  // Trim
  text = text.trim();

  return { text, images };
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    console.log(`
Usage: bun extract-post-content.ts <input.md>

Extract plain text and images from Obsidian Markdown for X posts.

Arguments:
  input.md   Input Markdown file

Output:
  JSON with { text, images }

Example:
  bun extract-post-content.ts Articles/my-post.md
`);
    process.exit(0);
  }

  const inputFile = args[0];
  const projectRoot = process.cwd();

  // Parse --output-dir option
  const outputDirIndex = args.indexOf('--output-dir');
  const outputDir = outputDirIndex !== -1 ? resolve(projectRoot, args[outputDirIndex + 1]) : undefined;

  try {
    const result = await extractPostContent(resolve(projectRoot, inputFile), projectRoot, { outputDir });
    console.log(JSON.stringify(result, null, 2));
  } catch (error) {
    console.error('Error:', error instanceof Error ? error.message : error);
    process.exit(1);
  }
}

main();
