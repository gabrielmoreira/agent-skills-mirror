#!/usr/bin/env bun
/**
 * Shared Obsidian vault image path resolution utilities.
 *
 * Used by md-to-article.ts and md-to-post.ts to resolve image paths
 * within an Obsidian vault. All functions are synchronous.
 */

import { readFileSync, existsSync } from 'node:fs';
import { join, basename, resolve } from 'node:path';

/**
 * Read Obsidian app.json configuration.
 * Returns the attachmentFolderPath if configured.
 */
export function readObsidianConfig(
  projectRoot: string
): { attachmentFolderPath?: string } {
  const configPath = join(projectRoot, '.obsidian', 'app.json');
  try {
    if (existsSync(configPath)) {
      return JSON.parse(readFileSync(configPath, 'utf-8'));
    }
  } catch (error) {
    console.error('[obsidian-resolver] Failed to read .obsidian/app.json:', error);
  }
  return {};
}

/**
 * Resolve image path using Obsidian CLI (vault-wide wikilink search).
 * Returns absolute path or null if CLI fails.
 */
export function resolveWithObsidianCLI(
  filename: string,
  projectRoot: string
): string | null {
  const { spawnSync } = require('node:child_process');
  const result = spawnSync('obsidian', ['file', `file=${filename}`], {
    encoding: 'utf-8',
  });
  if (result.status !== 0 || !result.stdout) return null;
  const match = result.stdout.match(/^path\t(.+)$/m);
  if (!match) return null;
  return join(projectRoot, match[1].trim());
}

/**
 * Strip Obsidian wiki-link image format and optional alt/pipe text.
 *
 * "![[Attachments/img.png|alt]]" → "Attachments/img.png"
 * "![[img.png]]" → "img.png"
 * "img.png" → "img.png" (no-op for plain paths)
 */
export function stripObsidianWikiLink(imagePath: string): string {
  let clean = imagePath.replace(/^!\[\[/, '').replace(/\]\]$/, '');
  // Remove pipe-separated alt text: "path|alt" → "path"
  const pipeIndex = clean.indexOf('|');
  if (pipeIndex !== -1) {
    clean = clean.substring(0, pipeIndex);
  }
  return clean.trim();
}

/**
 * Resolve a local image path within an Obsidian vault.
 * Synchronous. Does NOT handle URLs.
 *
 * Resolution chain:
 * 1. Absolute path → check exists
 * 2. attachmentFolder + filename
 * 3. Attachments/ + filename
 * 4. projectRoot + relative path (e.g. "Attachments/subdir/img.png")
 * 5. sourceFileDir + relative path (handles "../../Attachments/..." syntax)
 * 6. Obsidian CLI fallback (vault-wide wikilink search)
 * 7. Fallback to Attachments/filename
 */
export function resolveLocalImagePath(
  imagePath: string,
  projectRoot: string,
  options?: {
    attachmentFolder?: string;
    sourceFileDir?: string;
  }
): string {
  const cleanPath = stripObsidianWikiLink(imagePath);
  const filename = basename(cleanPath);
  const { attachmentFolder, sourceFileDir } = options ?? {};

  // 1. Absolute path
  if (cleanPath.startsWith('/')) {
    if (existsSync(cleanPath)) return cleanPath;
  }

  // 2. Configured attachment folder
  if (attachmentFolder) {
    const candidate = join(projectRoot, attachmentFolder, filename);
    if (existsSync(candidate)) return candidate;
  }

  // 3. Attachments/ directory (root only, by filename)
  const inAttachments = join(projectRoot, 'Attachments', filename);
  if (existsSync(inAttachments)) return inAttachments;

  // 4. Relative to project root (e.g. "Attachments/subdir/img.png")
  if (!cleanPath.startsWith('/')) {
    const fullPath = join(projectRoot, cleanPath);
    if (existsSync(fullPath)) return fullPath;
  }

  // 5. Relative to source file directory
  if (sourceFileDir && !cleanPath.startsWith('/')) {
    const relativeToSource = resolve(sourceFileDir, cleanPath);
    if (existsSync(relativeToSource)) return relativeToSource;
  }

  // 6. Obsidian CLI fallback (vault-wide search)
  const cliResolved = resolveWithObsidianCLI(filename, projectRoot);
  if (cliResolved && existsSync(cliResolved)) return cliResolved;

  // 7. Fallback
  return cleanPath.startsWith('/')
    ? cleanPath
    : join(projectRoot, 'Attachments', filename);
}
