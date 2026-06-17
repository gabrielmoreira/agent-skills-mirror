// Загрузка mm-config.json по алгоритму docs/CONFIG-LOADING.md.
// Порядок резолва repoRoot: env MM_REPO_ROOT → junction (~/.claude/skills/mm-bridge) → fallback (module-relative).
// Deep-merge mm-config.local.json (local wins), инъекция _repo_root. Read-only.

import { readFileSync, existsSync, realpathSync } from 'node:fs';
import { homedir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export type ConfigSource = 'env' | 'junction' | 'fallback';

export interface MmConfig {
  [key: string]: unknown;
  paths?: Record<string, unknown>;
  _repo_root?: string;
}

export interface LoadedConfig {
  config: MmConfig;
  repoRoot: string;
  source: ConfigSource;
}

function isPlainObject(v: unknown): v is Record<string, unknown> {
  return typeof v === 'object' && v !== null && !Array.isArray(v);
}

// Deep merge: overlay (local) выигрывает на уровне ключей; вложенные объекты сливаются рекурсивно.
function deepMerge(
  base: Record<string, unknown>,
  overlay: Record<string, unknown>,
): Record<string, unknown> {
  const out: Record<string, unknown> = { ...base };
  for (const key of Object.keys(overlay)) {
    const b = out[key];
    const o = overlay[key];
    out[key] = isPlainObject(b) && isPlainObject(o) ? deepMerge(b, o) : o;
  }
  return out;
}

function hasConfig(root: string): boolean {
  return existsSync(path.join(root, 'config', 'mm-config.json'));
}

// Резолв repoRoot строго по CONFIG-LOADING.md (env → junction), плюс детерминированный
// module-relative fallback (dist/config-loader.js → repoRoot), т.к. MCP-сервер живёт внутри репо.
function resolveRepoRoot(): { repoRoot: string; source: ConfigSource } {
  // Шаг 1. env MM_REPO_ROOT
  const envRoot = process.env.MM_REPO_ROOT;
  if (envRoot && hasConfig(envRoot)) {
    return { repoRoot: envRoot, source: 'env' };
  }

  // Шаг 2. Резолв через junction ~/.claude/skills/mm-bridge → parent(parent(real))
  const skillDir = path.join(homedir(), '.claude', 'skills', 'mm-bridge');
  try {
    if (existsSync(skillDir)) {
      const real = realpathSync(skillDir);
      const candidate = path.dirname(path.dirname(real));
      if (hasConfig(candidate)) {
        return { repoRoot: candidate, source: 'junction' };
      }
    }
  } catch {
    // экзотический reparse-point / нет прав — деградируем к fallback
  }

  // Шаг 3. Fallback: относительно самого модуля (dist/config-loader.js → ../../ = repoRoot/mcp → ../ )
  // dist лежит в <repoRoot>/mcp/dist, значит repoRoot = dirname(dirname(dirname(thisFile))).
  const here = path.dirname(fileURLToPath(import.meta.url));
  const candidate = path.resolve(here, '..', '..', '..');
  if (hasConfig(candidate)) {
    return { repoRoot: candidate, source: 'fallback' };
  }

  throw new Error(
    'mm-config.json не найден: задайте MM_REPO_ROOT или запустите npx markdown-memory.',
  );
}

// Загружает эффективный конфиг. Бросает Error с понятным текстом, если ничего не нашлось
// или JSON невалиден (вызывающая сторона ловит и деградирует мягко).
export function loadMmConfig(): LoadedConfig {
  const { repoRoot, source } = resolveRepoRoot();

  const base = JSON.parse(
    readFileSync(path.join(repoRoot, 'config', 'mm-config.json'), 'utf8'),
  ) as Record<string, unknown>;

  let merged: Record<string, unknown> = base;
  const localPath = path.join(repoRoot, 'config', 'mm-config.local.json');
  if (existsSync(localPath)) {
    const local = JSON.parse(readFileSync(localPath, 'utf8')) as Record<string, unknown>;
    merged = deepMerge(base, local);
  }

  merged._repo_root = repoRoot;
  return { config: merged as MmConfig, repoRoot, source };
}
