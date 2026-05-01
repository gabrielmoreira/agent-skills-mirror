#!/usr/bin/env node
/**
 * store-sync.cjs
 *
 * Fetch updates from all 4 plugin stores and produce a flat inventory.
 * Matching against fleet needs is done SEMANTICALLY by the AI when
 * running /scan-stores — this script only handles the mechanical work.
 *
 * Usage:
 *   node scripts/store-sync.cjs                # fetch + inventory
 *   node scripts/store-sync.cjs --skip-fetch   # inventory only (offline)
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const SKIP_FETCH = process.argv.includes('--skip-fetch');
const DEV = path.resolve(__dirname, '..', '..');
const MALL_DIR = path.join(DEV, 'MALL');
const FLEET_DIR = path.join(__dirname, '..', 'fleet');

const STORES = [
  // Internal (Microsoft Agency)
  { name: 'production', path: path.join(MALL_DIR, '.github-private'), pluginDir: 'plugins', quality: 'governance-reviewed' },
  { name: 'playground', path: path.join(MALL_DIR, 'playground'), pluginDir: 'plugins', quality: 'staging' },
  // Official (GitHub / Microsoft / Anthropic)
  { name: 'copilot-plugins', path: path.join(MALL_DIR, 'copilot-plugins'), pluginDir: '.', quality: 'github-official' },
  { name: 'awesome-copilot', path: path.join(MALL_DIR, 'awesome-copilot'), pluginDir: '.', quality: 'github-community' },
  { name: 'microsoft-skills', path: path.join(MALL_DIR, 'microsoft-skills'), pluginDir: 'skills', quality: 'microsoft-official' },
  { name: 'hve-core', path: path.join(MALL_DIR, 'hve-core'), pluginDir: '.', quality: 'microsoft-official' },
  { name: 'mcp-servers', path: path.join(MALL_DIR, 'mcp-servers'), pluginDir: 'src', quality: 'anthropic-official' },
  // Community
  { name: 'awesome-mcp-servers', path: path.join(MALL_DIR, 'awesome-mcp-servers'), pluginDir: '.', quality: 'community-registry' },
  { name: 'everything-claude-code', path: path.join(MALL_DIR, 'everything-claude-code'), pluginDir: '.', quality: 'community' },
  { name: 'wshobson-agents', path: path.join(MALL_DIR, 'wshobson-agents'), pluginDir: '.', quality: 'community-quality' },
  { name: 'claude-code-subagents', path: path.join(MALL_DIR, 'awesome-claude-code-subagents'), pluginDir: '.', quality: 'community' },
  { name: 'claude-skills', path: path.join(MALL_DIR, 'claude-skills'), pluginDir: '.', quality: 'community' },
  { name: 'awesome-claude-code', path: path.join(MALL_DIR, 'awesome-claude-code'), pluginDir: '.', quality: 'community-curated' },
  { name: 'karpathy-skills', path: path.join(MALL_DIR, 'andrej-karpathy-skills'), pluginDir: '.', quality: 'reference' },
  // Domain + additional
  { name: 'game-studios', path: path.join(MALL_DIR, 'game-studios'), pluginDir: '.', quality: 'domain' },
  { name: 'marketingskills', path: path.join(MALL_DIR, 'marketingskills'), pluginDir: '.', quality: 'domain' },
  { name: 'copilot-collections', path: path.join(MALL_DIR, 'copilot-collections'), pluginDir: '.', quality: 'official' },
  { name: 'copilot-kit', path: path.join(MALL_DIR, 'copilot-kit'), pluginDir: '.', quality: 'community' },
  { name: 'agents-collection', path: path.join(MALL_DIR, 'agents-collection'), pluginDir: '.', quality: 'community' },
];

const PORTFOLIO_PATH = path.join(DEV, 'AlexFleetPortfolio');
const PORTFOLIO_OWNER = 'fabioc-aloha';
const PORTFOLIO_REPO = 'AlexFleetPortfolio';
const PORTFOLIO_FILES = ['repos/repo-analysis.json', 'repos/repo-classification.json'];

// --- Fetch portfolio from GitHub API (works without local clone) ---
function fetchPortfolioFromGitHub() {
  const snapshot = {};
  for (const filePath of PORTFOLIO_FILES) {
    try {
      const url = `https://api.github.com/repos/${PORTFOLIO_OWNER}/${PORTFOLIO_REPO}/contents/${filePath}`;
      const result = execSync(
        `gh api "${url}" --jq .content`,
        { encoding: 'utf-8', timeout: 30000 }
      ).trim();
      const decoded = Buffer.from(result, 'base64').toString('utf-8');
      const fname = path.basename(filePath);
      snapshot[fname] = JSON.parse(decoded);
      console.log(`FETCH: ${fname} from GitHub API`);
    } catch (e) {
      console.log(`WARN: ${filePath} fetch from GitHub failed — ${e.message.split('\n')[0]}`);
    }
  }
  return Object.keys(snapshot).length > 0 ? snapshot : null;
}

// --- Fetch portfolio from local clone (fallback) ---
function fetchPortfolioFromLocal() {
  const portfolioRepos = path.join(PORTFOLIO_PATH, 'repos');
  if (!fs.existsSync(portfolioRepos)) return null;

  // Pull latest first
  try {
    const result = execSync('git pull --ff-only', { cwd: PORTFOLIO_PATH, encoding: 'utf-8', timeout: 30000 });
    console.log(`FETCH: AlexFleetPortfolio local — ${result.trim().split('\n').pop()}`);
  } catch (e) {
    console.log(`WARN: AlexFleetPortfolio pull failed — using cached local`);
  }

  const snapshot = {};
  for (const filePath of PORTFOLIO_FILES) {
    const src = path.join(PORTFOLIO_PATH, filePath);
    if (fs.existsSync(src)) {
      const fname = path.basename(filePath);
      snapshot[fname] = JSON.parse(fs.readFileSync(src, 'utf-8'));
    }
  }
  return Object.keys(snapshot).length > 0 ? snapshot : null;
}

// --- Fetch ---
function fetchStores() {
  for (const store of STORES) {
    if (!fs.existsSync(store.path)) {
      console.log(`SKIP: ${store.name} not found at ${store.path}`);
      continue;
    }
    try {
      const result = execSync('git pull --ff-only', { cwd: store.path, encoding: 'utf-8', timeout: 30000 });
      console.log(`FETCH: ${store.name} — ${result.trim().split('\n').pop()}`);
    } catch (e) {
      console.log(`WARN: ${store.name} fetch failed — ${e.message.split('\n')[0]}`);
    }
  }
}

// --- Inventory a plugin ---
function inventoryPlugin(pluginPath) {
  const name = path.basename(pluginPath);
  const info = { name, skills: [], agents: [], hasHooks: false, hasMcp: false, readme: '', category: '' };

  // README
  const readmePath = path.join(pluginPath, 'README.md');
  if (fs.existsSync(readmePath)) {
    const lines = fs.readFileSync(readmePath, 'utf-8').split('\n');
    // First non-empty, non-heading line as description
    for (const line of lines) {
      const t = line.trim();
      if (t && !t.startsWith('#') && !t.startsWith('!') && !t.startsWith('<') && t.length > 10) {
        info.readme = t.slice(0, 200);
        break;
      }
    }
  }

  // agency.json
  const agencyPath = path.join(pluginPath, 'agency.json');
  if (fs.existsSync(agencyPath)) {
    try {
      const agency = JSON.parse(fs.readFileSync(agencyPath, 'utf-8'));
      info.category = agency.category || '';
    } catch { }
  }

  // Skills
  const skillsDir = path.join(pluginPath, 'skills');
  if (fs.existsSync(skillsDir)) {
    for (const d of fs.readdirSync(skillsDir, { withFileTypes: true })) {
      if (d.isDirectory() && fs.existsSync(path.join(skillsDir, d.name, 'SKILL.md'))) {
        info.skills.push(d.name);
      }
    }
  }

  // Agents (in agents/ dir and root .md files)
  const agentsDir = path.join(pluginPath, 'agents');
  if (fs.existsSync(agentsDir)) {
    for (const f of fs.readdirSync(agentsDir)) {
      if (f.endsWith('.md')) info.agents.push(f.replace('.md', ''));
    }
  }
  // Root agent .md files (not README, CONTRIBUTING, etc.)
  const skipFiles = new Set(['README.md', 'CONTRIBUTING.md', 'SECURITY.md', 'CODEOWNERS', 'LICENSE', 'CHANGELOG.md']);
  for (const f of fs.readdirSync(pluginPath)) {
    if (f.endsWith('.md') && !skipFiles.has(f) && !f.startsWith('.')) {
      info.agents.push(f.replace('.md', ''));
    }
  }

  // Hooks
  info.hasHooks = fs.existsSync(path.join(pluginPath, 'hooks')) || fs.existsSync(path.join(pluginPath, 'hooks.json'));

  // MCP
  info.hasMcp = fs.existsSync(path.join(pluginPath, '.mcp.json'));

  return info;
}

// --- Inventory all stores ---
function inventoryStores() {
  const inventory = {};
  for (const store of STORES) {
    const pDir = path.join(store.path, store.pluginDir);
    if (!fs.existsSync(pDir)) { inventory[store.name] = []; continue; }

    const plugins = [];
    for (const d of fs.readdirSync(pDir, { withFileTypes: true })) {
      if (!d.isDirectory() || d.name.startsWith('.')) continue;
      // Check if it looks like a plugin (has README, skills, agents, or plugin.json)
      const dp = path.join(pDir, d.name);
      const hasPlugin = fs.existsSync(path.join(dp, 'plugin.json')) ||
        fs.existsSync(path.join(dp, 'agency.json')) ||
        fs.existsSync(path.join(dp, 'skills')) ||
        fs.existsSync(path.join(dp, 'README.md'));
      if (hasPlugin) plugins.push(inventoryPlugin(dp));
    }
    inventory[store.name] = plugins;
  }
  return inventory;
}

// --- Generate inventory report ---
function generateReport(inventory) {
  const lines = [
    '# Plugin Store Inventory',
    '',
    `Generated: ${new Date().toISOString().split('T')[0]}`,
    '',
    'This is a mechanical inventory. Semantic matching against fleet needs',
    'is done by the AI when running `/scan-stores`.',
    '',
    '## Store Summary',
    '',
    '| Store | Plugins | Quality |',
    '| --- | --- | --- |',
  ];
  let totalPlugins = 0;
  for (const store of STORES) {
    const count = (inventory[store.name] || []).length;
    totalPlugins += count;
    lines.push(`| ${store.name} | ${count} | ${store.quality} |`);
  }
  lines.push(`| **Total** | **${totalPlugins}** | |`);

  // Per-store tables with README excerpts for semantic search
  for (const store of STORES) {
    const plugins = inventory[store.name] || [];
    if (plugins.length === 0) continue;

    lines.push('', `## ${store.name} (${store.quality})`, '');
    lines.push('| Plugin | Skills | Agents | Hooks | MCP | Description |');
    lines.push('| --- | --- | --- | --- | --- | --- |');

    for (const p of plugins) {
      const desc = p.readme.replace(/\|/g, '/').slice(0, 100);
      lines.push(`| ${p.name} | ${p.skills.length} | ${p.agents.length} | ${p.hasHooks} | ${p.hasMcp} | ${desc} |`);
    }
  }

  return lines.join('\n');
}

// --- Main ---
function main() {
  if (!SKIP_FETCH) fetchStores();

  console.log('\nInventorying stores...');
  const inventory = inventoryStores();

  // Write JSON inventory (for tooling)
  const jsonPath = path.join(FLEET_DIR, 'store-inventory.json');
  fs.writeFileSync(jsonPath, JSON.stringify(inventory, null, 2));

  // Write Markdown inventory (for AI semantic search)
  const report = generateReport(inventory);
  const mdPath = path.join(FLEET_DIR, 'STORE-INVENTORY.md');
  fs.writeFileSync(mdPath, report);

  // Fetch portfolio data: GitHub API first, local clone fallback
  console.log('\nFetching portfolio data...');
  let snapshot = null;
  if (!SKIP_FETCH) {
    snapshot = fetchPortfolioFromGitHub();
    if (!snapshot) {
      console.log('GitHub API unavailable, trying local clone...');
      snapshot = fetchPortfolioFromLocal();
    }
  } else {
    snapshot = fetchPortfolioFromLocal();
  }

  if (snapshot) {
    const snapshotPath = path.join(FLEET_DIR, 'portfolio-snapshot.json');
    fs.writeFileSync(snapshotPath, JSON.stringify(snapshot, null, 2));
    const repoCount = snapshot['repo-analysis.json']?.detailed_repositories?.length
      || snapshot['repo-analysis.json']?.length || '?';
    const catCount = snapshot['repo-classification.json']?.categories?.length || '?';
    console.log(`Portfolio snapshot: ${repoCount} repos, ${catCount} categories`);
  } else {
    console.log('WARN: No portfolio data available (no API access, no local clone)');
  }

  let total = 0;
  for (const plugins of Object.values(inventory)) total += plugins.length;
  console.log(`\nWrote ${jsonPath} and ${mdPath} (${total} plugins across ${STORES.length} stores)`);
}

main();
