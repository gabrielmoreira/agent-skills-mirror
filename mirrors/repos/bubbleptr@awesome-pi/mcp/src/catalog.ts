import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import type { CatalogSource, LoadedCatalog, PublicCatalog, PublicCategory, PublicKind, PublicPackage } from './types.js';
import { directoryLink, matchesResource } from './filter.js';

export const DEFAULT_CATALOG_URL = 'https://piindex.dev/catalog.json';
export const DEFAULT_TTL_MS = 15 * 60 * 1000;
const MAX_BYTES = 8_000_000;
const PAGE_DEFAULT = 20;
const PAGE_MAX = 50;

export function packageVersion(): string {
  const version = JSON.parse(readFileSync(new URL('../package.json', import.meta.url), 'utf8')).version;
  if (typeof version !== 'string' || !version) throw new Error('package.json version is missing');
  return version;
}

export function bundledSnapshotPath(): string {
  return fileURLToPath(new URL('../catalog.snapshot.json', import.meta.url));
}

export function isCatalog(value: unknown): value is PublicCatalog {
  if (!value || typeof value !== 'object') return false;
  const doc = value as Partial<PublicCatalog>;
  return doc.schemaVersion === 1
    && typeof doc.statsGeneratedAt === 'string'
    && doc.site === 'https://piindex.dev'
    && Array.isArray(doc.kinds)
    && Array.isArray(doc.categories)
    && Array.isArray(doc.guides)
    && Array.isArray(doc.packages)
    && doc.packages.length > 0
    && doc.categories.length > 0
    && doc.kinds.length > 0
    && doc.packages.every(pkg => Boolean(pkg)
      && typeof pkg.name === 'string'
      && typeof pkg.id === 'string'
      && typeof pkg.searchText === 'string'
      && typeof pkg.piindexUrl === 'string'
      && pkg.piindexUrl.startsWith('https://piindex.dev/'));
}

export function parseCatalog(text: string): PublicCatalog {
  const value: unknown = JSON.parse(text);
  if (!isCatalog(value)) throw new Error('response is not a Pi Index catalog');
  return value;
}

export function readCatalog(path: string | URL): PublicCatalog {
  return parseCatalog(readFileSync(path, 'utf8'));
}

export type LoadOptions = {
  env?: NodeJS.ProcessEnv;
  fetchImpl?: typeof fetch;
  snapshot?: string | URL;
};

export async function loadCatalog(options: LoadOptions = {}): Promise<LoadedCatalog> {
  const env = options.env ?? process.env;
  const snapshot = options.snapshot ?? bundledSnapshotPath();
  const file = env.PIINDEX_CATALOG_FILE?.trim();
  if (file) return { catalog: readCatalog(file), source: 'file' };
  const url = env.PIINDEX_CATALOG_URL?.trim() || DEFAULT_CATALOG_URL;
  try {
    return { catalog: await fetchCatalog(url, options.fetchImpl ?? fetch), source: 'remote' };
  } catch (error) {
    const reason = error instanceof Error ? error.message : 'unknown error';
    console.error(`piindex-mcp: remote catalog unavailable (${reason}); using bundled snapshot`);
    return { catalog: readCatalog(snapshot), source: 'snapshot' };
  }
}

async function fetchCatalog(url: string, fetchImpl: typeof fetch): Promise<PublicCatalog> {
  const response = await fetchImpl(url, {
    headers: {
      accept: 'application/json',
      'user-agent': `piindex-mcp/${packageVersion()} (+https://piindex.dev)`,
    },
    signal: AbortSignal.timeout(5000),
    redirect: 'follow',
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const text = await response.text();
  if (text.length > MAX_BYTES) throw new Error('response exceeds 8MB');
  return parseCatalog(text);
}

let cache: { at: number; value: Promise<LoadedCatalog> } | undefined;

export function resetCatalogCache(): void {
  cache = undefined;
}

export function getCatalog(): Promise<LoadedCatalog> {
  const ttl = Number(process.env.PIINDEX_CATALOG_TTL_MS ?? DEFAULT_TTL_MS);
  const now = Date.now();
  if (cache && Number.isFinite(ttl) && ttl > 0 && now - cache.at < ttl) return cache.value;
  const pending = loadCatalog().catch(error => {
    if (cache?.value === pending) cache = undefined;
    throw error;
  });
  cache = { at: now, value: pending };
  return pending;
}

export function knownCategories(catalog: PublicCatalog): Set<string> {
  return new Set(['all', ...catalog.kinds.map(kind => kind.id), ...catalog.categories.map(category => category.id)]);
}

export function categoryError(catalog: PublicCatalog, category: string) {
  return {
    error: `Unknown category "${category}".`,
    piindexUrl: 'https://piindex.dev/',
    kinds: catalog.kinds.map(summarizeKind),
    categories: catalog.categories.map(summarizeCategory),
  };
}

export function summarize(pkg: PublicPackage, catalog: PublicCatalog) {
  const byId = new Map(catalog.categories.map(category => [category.id, category]));
  return {
    id: pkg.id,
    name: pkg.name,
    description: pkg.descriptions.en.join(' '),
    descriptionZh: pkg.descriptions.zh.join(' '),
    kind: pkg.kind,
    kindName: pkg.kindName,
    kindNameZh: pkg.kindNameZh,
    categories: pkg.categories.map(id => {
      const category = byId.get(id);
      return category ? summarizeCategory(category) : { id, name: id, nameZh: id, kind: pkg.kind, count: 0, piindexUrl: directoryLink('', id), guideUrl: null };
    }),
    install: pkg.install,
    projectUrl: pkg.projectUrl,
    repoUrl: pkg.repoUrl,
    npmPackage: pkg.npmPackage,
    npmUrl: pkg.npmUrl,
    stars: pkg.stars,
    weeklyDownloads: pkg.weeklyDownloads,
    weeklyTrendPercent: pkg.weeklyTrendPercent,
    piindexUrl: pkg.piindexUrl,
    directoryUrl: pkg.directoryUrl,
    guideUrl: pkg.guideUrl,
    guides: pkg.guides,
  };
}

export function detail(pkg: PublicPackage, catalog: PublicCatalog) {
  return { ...summarize(pkg, catalog), descriptions: pkg.descriptions };
}

function summarizeKind(kind: PublicKind) {
  return { id: kind.id, name: kind.name, nameZh: kind.nameZh, count: kind.count, piindexUrl: kind.piindexUrl };
}

function summarizeCategory(category: PublicCategory) {
  return {
    id: category.id, name: category.name, nameZh: category.nameZh, kind: category.kind,
    count: category.count, piindexUrl: category.piindexUrl, guideUrl: category.guideUrl,
  };
}

export type Page<T> = { items: T[]; total: number; limit: number; offset: number; hasMore: boolean };

export function page<T>(items: T[], limit?: number, offset?: number): Page<T> {
  const size = Math.min(Math.max(limit ?? PAGE_DEFAULT, 1), PAGE_MAX);
  const start = Math.max(offset ?? 0, 0);
  const slice = items.slice(start, start + size);
  return { items: slice, total: items.length, limit: size, offset: start, hasMore: start + slice.length < items.length };
}

export function resolveCategory(catalog: PublicCatalog, category?: string): string | { error: ReturnType<typeof categoryError> } {
  const value = category?.trim() || 'all';
  if (!knownCategories(catalog).has(value)) return { error: categoryError(catalog, value) };
  return value;
}

export function searchPackages(catalog: PublicCatalog, query: string, category: string): PublicPackage[] {
  return catalog.packages.filter(pkg => matchesResource(pkg, { q: query, category }));
}

export function suggestions(catalog: PublicCatalog, query: string) {
  return searchPackages(catalog, query, 'all').slice(0, 5).map(pkg => ({ id: pkg.id, name: pkg.name, piindexUrl: pkg.piindexUrl }));
}

export function findPackage(catalog: PublicCatalog, input: { name?: string; id?: string }):
  | { ok: true; pkg: PublicPackage }
  | { ok: false; body: Record<string, unknown> } {
  const id = input.id?.trim();
  const name = input.name?.trim();
  if (!id && !name) return { ok: false, body: { error: 'Provide a package name or id.', piindexUrl: 'https://piindex.dev/' } };
  if (id) {
    const pkg = catalog.packages.find(item => item.id === id);
    if (!pkg) return { ok: false, body: { error: `No package with id "${id}".`, piindexUrl: 'https://piindex.dev/', suggestions: suggestions(catalog, id) } };
    if (name && pkg.name !== name && pkg.name.toLowerCase() !== name.toLowerCase()) {
      return { ok: false, body: { error: `id "${id}" is ${pkg.name}, which does not match name "${name}".`, piindexUrl: pkg.piindexUrl } };
    }
    return { ok: true, pkg };
  }
  const exact = catalog.packages.filter(item => item.name === name);
  const matches = exact.length ? exact : catalog.packages.filter(item => item.name.toLowerCase() === name!.toLowerCase());
  if (matches.length === 1) return { ok: true, pkg: matches[0]! };
  if (matches.length > 1) {
    return {
      ok: false,
      body: {
        error: `More than one package is named "${name}". Call get_package again with id.`,
        piindexUrl: 'https://piindex.dev/',
        matches: matches.map(pkg => ({ id: pkg.id, name: pkg.name, piindexUrl: pkg.piindexUrl, projectUrl: pkg.projectUrl })),
      },
    };
  }
  return { ok: false, body: { error: `No package named "${name}".`, piindexUrl: directoryLink(name!), suggestions: suggestions(catalog, name!) } };
}

export function catalogMeta(loaded: LoadedCatalog) {
  return { catalogSource: loaded.source, statsGeneratedAt: loaded.catalog.statsGeneratedAt, piindexUrl: 'https://piindex.dev/' as const };
}
