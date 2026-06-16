// Загрузка канона config/secret-patterns.json и компиляция RegExp.
// Путь резолвится относительно расположения этого файла (dist/patterns.js), не от cwd.

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import type { CompiledPattern } from './scan.js';

interface RawPattern {
  id: string;
  description: string;
  class: 'A' | 'B';
  regex: string;
  flags: string;
  source: string;
}

interface PatternsFile {
  version: number;
  patterns: RawPattern[];
}

// dist/patterns.js → repo_root/config/secret-patterns.json
const CONFIG_PATH = resolve(
  dirname(fileURLToPath(import.meta.url)),
  '../../config/secret-patterns.json',
);

export function loadPatterns(): CompiledPattern[] {
  const file = JSON.parse(readFileSync(CONFIG_PATH, 'utf8')) as PatternsFile;
  return file.patterns.map((p) => ({
    id: p.id,
    class: p.class,
    regex: new RegExp(p.regex, p.flags),
  }));
}
