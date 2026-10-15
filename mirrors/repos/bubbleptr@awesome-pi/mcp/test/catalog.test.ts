import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { describe, test } from 'node:test';
import { fileURLToPath } from 'node:url';
import { isCatalog, loadCatalog, parseCatalog, readCatalog, searchPackages } from '../dist/catalog.js';

const snapshot = fileURLToPath(new URL('../catalog.snapshot.json', import.meta.url));

describe('catalog loading', () => {
  test('reads the bundled snapshot of the real directory', () => {
    const catalog = readCatalog(snapshot);
    assert.equal(isCatalog(catalog), true);
    assert.ok(catalog.packages.length > 100);
    assert.equal(catalog.packages.find(pkg => pkg.name === 'pi-web-access')?.piindexUrl, 'https://piindex.dev/packages/pi-web-access/');
    const brave = searchPackages(catalog, 'Brave', 'all');
    assert.deepEqual(brave.map(pkg => pkg.name), ['@juicesharp/rpiv-web-tools']);
    assert.equal(searchPackages(catalog, 'Brave missing', 'all').length, 0);
    const chinese = searchPackages(catalog, '子代理', 'subagents');
    assert.ok(chinese.some(pkg => pkg.name === 'pi-subagents'));
    assert.ok(chinese.every(pkg => pkg.categories.includes('subagents')));
  });

  test('uses PIINDEX_CATALOG_FILE and does not fetch', async () => {
    let called = false;
    const loaded = await loadCatalog({
      env: { PIINDEX_CATALOG_FILE: snapshot, PIINDEX_CATALOG_URL: 'https://piindex.dev/catalog.json' },
      fetchImpl: async () => { called = true; throw new Error('network should not be used'); },
    });
    assert.equal(called, false);
    assert.equal(loaded.source, 'file');
    assert.equal(loaded.catalog.packages.length > 100, true);
  });

  test('falls back to the snapshot when the remote catalog is unavailable', async () => {
    const loaded = await loadCatalog({
      env: { PIINDEX_CATALOG_URL: 'https://piindex.dev/catalog.json' },
      snapshot,
      fetchImpl: async () => new Response('nope', { status: 404 }),
    });
    assert.equal(loaded.source, 'snapshot');
    assert.ok(loaded.catalog.packages.some(pkg => pkg.name === 'pi-mcp-adapter'));
  });

  test('accepts a remote catalog and sends no credentials', async () => {
    const catalog = readCatalog(snapshot);
    let headers = new Headers();
    const loaded = await loadCatalog({
      env: { PIINDEX_CATALOG_URL: 'https://example.test/catalog.json' },
      fetchImpl: async (_url, init) => {
        headers = new Headers(init?.headers);
        return new Response(JSON.stringify(catalog), { status: 200, headers: { 'content-type': 'application/json' } });
      },
    });
    assert.equal(loaded.source, 'remote');
    assert.equal(loaded.catalog.packages.length, catalog.packages.length);
    assert.equal(headers.get('authorization'), null);
    assert.equal(headers.get('cookie'), null);
    assert.match(headers.get('user-agent') ?? '', /^piindex-mcp\/0\.1\.0/);
  });

  test('rejects a document that is not the Pi Index catalog', () => {
    assert.throws(() => parseCatalog(JSON.stringify({ schemaVersion: 2, packages: [] })), /not a Pi Index catalog/);
  });

  test('a configured file that cannot be read is an error', async () => {
    const dir = mkdtempSync(join(tmpdir(), 'piindex-mcp-'));
    const missing = join(dir, 'missing.json');
    writeFileSync(join(dir, 'present.json'), '{');
    await assert.rejects(() => loadCatalog({ env: { PIINDEX_CATALOG_FILE: missing }, fetchImpl: async () => { throw new Error('unused'); } }), /ENOENT/);
    await assert.rejects(() => loadCatalog({ env: { PIINDEX_CATALOG_FILE: join(dir, 'present.json') } }), /JSON/);
  });
});
