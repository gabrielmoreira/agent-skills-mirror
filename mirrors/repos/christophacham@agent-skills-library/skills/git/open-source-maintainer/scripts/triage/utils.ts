import fs from 'node:fs';

import { NormalizedReactionCounts } from './types';

export function ensureDir(dirPath: string) {
  fs.mkdirSync(dirPath, { recursive: true });
}

export function writeJson(filePath: string, data: unknown) {
  fs.writeFileSync(filePath, `${JSON.stringify(data, null, 2)}\n`, 'utf8');
}

export function writeText(filePath: string, content: string) {
  fs.writeFileSync(filePath, `${content}\n`, 'utf8');
}

export function getArgValue(args: string[], name: string): string | null {
  const index = args.indexOf(name);
  if (index === -1) return null;
  const value = args[index + 1];
  return value ?? null;
}

export function hasFlag(args: string[], name: string): boolean {
  return args.includes(name);
}

export function formatReactionCounts(counts: NormalizedReactionCounts): string {
  const entries = Object.entries(counts);
  if (entries.length === 0) return 'none';
  return entries
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([name, count]) => `${name}:${count}`)
    .join(', ');
}

export function getDatetimeString(): string {
  return new Date().toISOString().replace(/:/g, '-').replace(/\.\d{3}Z$/, '');
}
