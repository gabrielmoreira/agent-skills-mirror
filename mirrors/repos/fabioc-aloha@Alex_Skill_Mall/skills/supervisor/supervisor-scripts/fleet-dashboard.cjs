#!/usr/bin/env node
/**
 * fleet-dashboard.cjs
 *
 * Render a single SVG dashboard from fleet-inventory output. Aggregated view:
 * banner + KPI strip + version distribution + non-ACT activity buckets +
 * stats footer. Per-heir and per-repo inventories live in fleet/DASHBOARD.md,
 * not in the SVG. Follows the `svg-dashboard-composition` Mall skill
 * (one canvas, one panel primitive, equal-height rows, vertical-center bars,
 * footer as the final SVG row).
 *
 * Usage:
 *   node scripts/fleet-dashboard.cjs                         # write fleet/dashboard.svg
 *   node scripts/fleet-dashboard.cjs --out path/to/file.svg  # custom output path
 *   node scripts/fleet-dashboard.cjs --root <path>           # passthrough to inventory
 *   node scripts/fleet-dashboard.cjs --depth 3               # passthrough to inventory
 *   node scripts/fleet-dashboard.cjs --include-private       # passthrough
 *
 * No LLM dependencies, no Edition impact. Pure data → SVG.
 */

const fs = require('fs');
const path = require('path');
const { spawnSync, execSync } = require('child_process');

const REPO_ROOT = path.resolve(__dirname, '..');
const REPOS_CONFIG = require('./repos.config.json');

const SHARED_WIDTH = 820;
const PAD = 16; // outer canvas padding (left/right)
const GAP = 10; // vertical gap between fragments

// ---------- args ----------
const argv = process.argv.slice(2);
function argValue(name, fallback) {
    const i = argv.indexOf(name);
    return i >= 0 && argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[i + 1] : fallback;
}
function hasFlag(name) { return argv.includes(name); }

const OUT = path.resolve(REPO_ROOT, argValue('--out', path.join('fleet', 'dashboard.svg')));

const passthrough = [];
const rootArg = argValue('--root');
if (rootArg) passthrough.push('--root', rootArg);
const depthArg = argValue('--depth');
if (depthArg) passthrough.push('--depth', depthArg);
if (hasFlag('--include-private')) passthrough.push('--include-private');
// Always include non-ACT in the dashboard payload — they're part of fleet visibility
passthrough.push('--include-non-act');

// ---------- gather data ----------
function runInventory() {
    const r = spawnSync(process.execPath, [path.join(__dirname, 'fleet-inventory.cjs'), '--json', ...passthrough], { encoding: 'utf8' });
    if (r.status !== 0) {
        console.error('fleet-inventory failed:');
        console.error(r.stderr || r.stdout);
        process.exit(1);
    }
    return JSON.parse(r.stdout);
}

function runVersionProbe() {
    const r = spawnSync(process.execPath, [path.join(__dirname, 'fleet-non-act-versions.cjs'), '--json'], { encoding: 'utf8' });
    if (r.status !== 0) return { count: 0, with_version: 0, repos: [] };
    try { return JSON.parse(r.stdout); } catch { return { count: 0, with_version: 0, repos: [] }; }
}

function latestEditionVersion() {
    try {
        const editionPath = path.resolve(REPO_ROOT, REPOS_CONFIG.siblings.edition.path);
        const tag = execSync('git describe --tags --abbrev=0', { cwd: editionPath, encoding: 'utf8' }).trim();
        return tag.replace(/^v/, '');
    } catch {
        return null;
    }
}

function cmpSemver(a, b) {
    const pa = String(a).split('.').map((n) => parseInt(n, 10) || 0);
    const pb = String(b).split('.').map((n) => parseInt(n, 10) || 0);
    for (let i = 0; i < Math.max(pa.length, pb.length); i++) {
        const d = (pa[i] || 0) - (pb[i] || 0);
        if (d !== 0) return d;
    }
    return 0;
}

// ---------- SVG primitives ----------
function escapeXml(s) {
    return String(s).replace(/[<>&"']/g, (c) => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;', "'": '&apos;' }[c]));
}

/**
 * Pastel panel primitive — body + header band + hairline divider + title.
 * Matches svg-dashboard-composition rule 2.
 */
function panel({ x, y, w, h, title, color, subtitle }) {
    const r = 6;
    const headerH = 24;
    const titleColor = color.title;
    return `
  <g>
    <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" ry="${r}"
          fill="${color.fill}" stroke="${color.stroke}" stroke-width="1"/>
    <path d="M ${x},${y + r} Q ${x},${y} ${x + r},${y} L ${x + w - r},${y} Q ${x + w},${y} ${x + w},${y + r} L ${x + w},${y + headerH} L ${x},${y + headerH} Z"
          fill="${color.stroke}" fill-opacity="0.18"/>
    <line x1="${x + 1}" y1="${y + headerH}" x2="${x + w - 1}" y2="${y + headerH}" stroke="${color.stroke}" stroke-opacity="0.55" stroke-width="1"/>
    <text x="${x + 12}" y="${y + 16}" font-family="Segoe UI, sans-serif" font-size="12" font-weight="700" fill="${titleColor}">${escapeXml(title)}</text>
    ${subtitle ? `<text x="${x + w - 12}" y="${y + 16}" text-anchor="end" font-family="Segoe UI, sans-serif" font-size="11" fill="#64748b">${escapeXml(subtitle)}</text>` : ''}
  </g>`;
}

// Pastel palette (per user memory: pastel light, dark slate text)
const COLORS = {
    azure: { fill: '#dbeafe', stroke: '#93c5fd', title: '#1e3a8a' },
    fabric: { fill: '#ffedd5', stroke: '#fdba74', title: '#9a3412' },
    fresh: { fill: '#d1fae5', stroke: '#6ee7b7', title: '#065f46' },
    warn: { fill: '#fef3c7', stroke: '#fcd34d', title: '#92400e' },
    stale: { fill: '#fce7f3', stroke: '#f9a8d4', title: '#9f1239' },
    neutral: { fill: '#f3f4f6', stroke: '#d1d5db', title: '#374151' },
    indigo: { fill: '#e0e7ff', stroke: '#a5b4fc', title: '#3730a3' },
};

const TEXT_DARK = '#1f2937';
const TEXT_MUTED = '#64748b';

// ---------- fragments ----------
function bannerFragment(yOffset, heirCount, scannedAt, latestV) {
    const h = 56;
    const x = PAD, w = SHARED_WIDTH - 2 * PAD;
    const stamp = scannedAt.replace('T', ' ').replace(/\..*$/, ' UTC');
    const versionLabel = latestV ? `Edition v${latestV}` : 'Edition (no tag found)';
    return {
        height: h,
        svg: `
  <g transform="translate(0, ${yOffset})">
    <rect x="${x}" y="0" width="${w}" height="${h}" rx="8" ry="8"
          fill="#e0e7ff" stroke="#a5b4fc" stroke-width="1"/>
    <text x="${x + 16}" y="22" font-family="Segoe UI, sans-serif" font-size="16" font-weight="700" fill="${TEXT_DARK}">ACT Fleet Dashboard</text>
    <text x="${x + 16}" y="42" font-family="Segoe UI, sans-serif" font-size="11" fill="${TEXT_MUTED}">${escapeXml(stamp)} · ${heirCount} heir${heirCount === 1 ? '' : 's'} · ${escapeXml(versionLabel)}</text>
  </g>`,
    };
}

function kpiFragment(yOffset, kpis) {
    const h = 84;
    const x0 = PAD, totalW = SHARED_WIDTH - 2 * PAD;
    const cardGap = 10;
    const cardW = (totalW - cardGap * (kpis.length - 1)) / kpis.length;
    const cards = kpis.map((k, i) => {
        const cx = x0 + i * (cardW + cardGap);
        const c = COLORS[k.tone] || COLORS.neutral;
        return `
  <g>
    <rect x="${cx}" y="0" width="${cardW}" height="${h}" rx="6" ry="6"
          fill="${c.fill}" stroke="${c.stroke}" stroke-width="1"/>
    <text x="${cx + 12}" y="22" font-family="Segoe UI, sans-serif" font-size="11" font-weight="700" fill="${c.title}">${escapeXml(k.label)}</text>
    <text x="${cx + 12}" y="58" font-family="Segoe UI, sans-serif" font-size="32" font-weight="700" fill="${TEXT_DARK}">${escapeXml(String(k.value))}</text>
    ${k.note ? `<text x="${cx + 12}" y="76" font-family="Segoe UI, sans-serif" font-size="10" fill="${TEXT_MUTED}">${escapeXml(k.note)}</text>` : ''}
  </g>`;
    });
    return {
        height: h,
        svg: `<g transform="translate(0, ${yOffset})">${cards.join('')}</g>`,
    };
}

function versionBarFragment(yOffset, versionRows, latestV, totalHeirs) {
    const h = 156;
    const x = PAD, w = SHARED_WIDTH - 2 * PAD;
    const headerH = 24;
    const innerY = headerH + 12;
    const innerH = h - innerY - 12;
    const rowH = 28;
    const labelW = 90;
    const barX = x + labelW + 12;
    const barMaxW = (x + w - 16) - barX - 60; // leave 60px for count label
    const max = Math.max(1, ...versionRows.map((r) => r[1]));

    // rule 4: vertical-center if rows < slot capacity
    const totalRowsH = rowH * versionRows.length;
    const yStart = innerY + Math.max(0, (innerH - totalRowsH) / 2);

    const bars = versionRows.map(([ver, count], i) => {
        const cy = yStart + i * rowH + rowH / 2;
        const isLatest = latestV && ver === latestV;
        const c = isLatest ? COLORS.fresh : (latestV && cmpSemver(ver, latestV) < 0 ? COLORS.warn : COLORS.azure);
        const barW = (count / max) * barMaxW;
        const pct = Math.round((count / totalHeirs) * 100);
        return `
    <g>
      <text x="${x + labelW + 4}" y="${cy + 4}" text-anchor="end" font-family="Segoe UI, sans-serif" font-size="12" font-weight="600" fill="${TEXT_DARK}">v${escapeXml(ver)}${isLatest ? ' ●' : ''}</text>
      <rect x="${barX}" y="${cy - 9}" width="${barW}" height="18" rx="3" ry="3" fill="${c.fill}" stroke="${c.stroke}" stroke-width="1"/>
      <text x="${barX + barW + 8}" y="${cy + 4}" font-family="Segoe UI, sans-serif" font-size="11" fill="${TEXT_MUTED}">${count} heir${count === 1 ? '' : 's'} · ${pct}%</text>
    </g>`;
    });

    return {
        height: h,
        svg: `<g transform="translate(0, ${yOffset})">${panel({ x, y: 0, w, h, title: 'Heirs by Edition Version', color: COLORS.azure, subtitle: latestV ? `latest v${latestV}` : '' })}${bars.join('')}</g>`,
    };
}

function heirListFragment(yOffset, heirs, latestV) {
    const headerH = 24;
    const rowH = 28;
    const h = headerH + 12 + Math.max(rowH, rowH * heirs.length) + 12;
    const x = PAD, w = SHARED_WIDTH - 2 * PAD;

    if (heirs.length === 0) {
        return {
            height: h,
            svg: `<g transform="translate(0, ${yOffset})">${panel({ x, y: 0, w, h, title: 'Heirs', color: COLORS.neutral })}<text x="${x + w / 2}" y="${headerH + 28}" text-anchor="middle" font-family="Segoe UI, sans-serif" font-size="12" fill="${TEXT_MUTED}">No heirs found. See fleet/templates/act-heir.template.json.</text></g>`,
        };
    }

    // columns: heir, version, days, owner
    const colHeir = x + 14;
    const colVer = x + 360;
    const colDays = x + 470;
    const colOwner = x + 600;

    const headerRow = `
    <text x="${colHeir}" y="${headerH + 18}" font-family="Segoe UI, sans-serif" font-size="10" font-weight="700" fill="${TEXT_MUTED}">HEIR</text>
    <text x="${colVer}" y="${headerH + 18}" font-family="Segoe UI, sans-serif" font-size="10" font-weight="700" fill="${TEXT_MUTED}">VERSION</text>
    <text x="${colDays}" y="${headerH + 18}" font-family="Segoe UI, sans-serif" font-size="10" font-weight="700" fill="${TEXT_MUTED}">LAST SYNC</text>
    <text x="${colOwner}" y="${headerH + 18}" font-family="Segoe UI, sans-serif" font-size="10" font-weight="700" fill="${TEXT_MUTED}">OWNER</text>`;

    const rows = heirs.map((heir, i) => {
        const cy = headerH + 30 + i * rowH + rowH / 2 + 4;
        const stripeY = headerH + 30 + i * rowH;
        const stripe = i % 2 === 0 ? `<rect x="${x + 4}" y="${stripeY}" width="${w - 8}" height="${rowH}" rx="3" fill="#ffffff" fill-opacity="0.5"/>` : '';
        const isLatest = latestV && heir.edition_version === latestV;
        const verBadge = isLatest ? COLORS.fresh : (latestV && cmpSemver(heir.edition_version, latestV) < 0 ? COLORS.warn : COLORS.neutral);
        const days = heir.days_since_sync == null ? '?' : `${heir.days_since_sync}d`;
        const daysColor = heir.days_since_sync == null ? TEXT_MUTED : (heir.days_since_sync > 90 ? COLORS.stale.title : (heir.days_since_sync > 30 ? COLORS.warn.title : COLORS.fresh.title));
        return `
    ${stripe}
    <text x="${colHeir}" y="${cy}" font-family="Segoe UI, sans-serif" font-size="12" font-weight="600" fill="${TEXT_DARK}">${escapeXml(heir.heir_name || heir.heir_id)}</text>
    <g transform="translate(${colVer}, ${cy - 12})">
      <rect x="0" y="0" width="80" height="18" rx="3" ry="3" fill="${verBadge.fill}" stroke="${verBadge.stroke}" stroke-width="1"/>
      <text x="40" y="13" text-anchor="middle" font-family="Segoe UI, sans-serif" font-size="11" font-weight="600" fill="${verBadge.title}">v${escapeXml(heir.edition_version)}${isLatest ? ' ●' : ''}</text>
    </g>
    <text x="${colDays}" y="${cy}" font-family="Segoe UI, sans-serif" font-size="12" fill="${daysColor}">${escapeXml(days)}</text>
    <text x="${colOwner}" y="${cy}" font-family="Segoe UI, sans-serif" font-size="12" fill="${TEXT_DARK}">${escapeXml(heir.owner || '—')}</text>`;
    }).join('');

    return {
        height: h,
        svg: `<g transform="translate(0, ${yOffset})">${panel({ x, y: 0, w, h, title: 'Heirs', color: COLORS.neutral, subtitle: `${heirs.length} total` })}${headerRow}${rows}</g>`,
    };
}

function nonActPanelFragment(yOffset, repos) {
    const x = PAD, w = SHARED_WIDTH - 2 * PAD;
    const headerH = 24;

    if (repos.length === 0) {
        const h = headerH + 40;
        return {
            height: h,
            svg: `<g transform="translate(0, ${yOffset})">${panel({ x, y: 0, w, h, title: 'Non-ACT Alex Repos', color: COLORS.fabric, subtitle: '0 found' })}<text x="${x + w / 2}" y="${headerH + 24}" text-anchor="middle" font-family="Segoe UI, sans-serif" font-size="12" fill="${TEXT_MUTED}">No non-ACT Alex repos detected.</text></g>`,
        };
    }

    // Bucket by activity -- aligned with migration heuristic in DASHBOARD.md
    const buckets = [
        { label: 'Active (<7d)', verdict: 'Yes', max: 7, tone: COLORS.fresh, count: 0 },
        { label: 'Recent (7\u201330d)', verdict: 'Maybe', max: 30, tone: COLORS.azure, count: 0 },
        { label: 'Idle (30\u201390d)', verdict: 'Defer', max: 90, tone: COLORS.warn, count: 0 },
        { label: 'Stale (>90d)', verdict: 'No', max: Infinity, tone: COLORS.stale, count: 0 },
    ];
    for (const r of repos) {
        const d = r.days_since_commit == null ? Infinity : r.days_since_commit;
        for (const b of buckets) { if (d <= b.max) { b.count++; break; } }
    }

    // Aggregated panel only: stacked bar + legend. Per-repo list is in DASHBOARD.md.
    const h = headerH + 12 + 22 + 18 + 22 + 12; // header + bar + 2-row legend + padding

    const total = repos.length;
    const barX = x + 14;
    const barW = w - 28;
    const barY = headerH + 18;
    const barH = 22;
    const segs = [];
    let cursor = 0;
    for (const b of buckets) {
        if (b.count === 0) continue;
        const segW = (b.count / total) * barW;
        segs.push(`
    <rect x="${barX + cursor}" y="${barY}" width="${segW}" height="${barH}" fill="${b.tone.fill}" stroke="${b.tone.stroke}" stroke-width="1"/>
    ${segW > 24 ? `<text x="${barX + cursor + segW / 2}" y="${barY + 15}" text-anchor="middle" font-family="Segoe UI, sans-serif" font-size="11" font-weight="700" fill="${b.tone.title}">${b.count}</text>` : ''}`);
        cursor += segW;
    }

    // Legend (4 swatches in two columns) -- shows bucket label + count + migration verdict
    const legendY = barY + barH + 18;
    const legend = buckets.map((b, i) => {
        const col = i % 2;
        const row = Math.floor(i / 2);
        const lx = barX + col * (barW / 2);
        const ly = legendY + row * 22;
        return `
    <rect x="${lx}" y="${ly - 9}" width="14" height="12" rx="2" fill="${b.tone.fill}" stroke="${b.tone.stroke}" stroke-width="1"/>
    <text x="${lx + 22}" y="${ly}" font-family="Segoe UI, sans-serif" font-size="11" fill="${TEXT_DARK}">${escapeXml(b.label)}</text>
    <text x="${lx + 22}" y="${ly}" dx="110" font-family="Segoe UI, sans-serif" font-size="11" font-weight="700" fill="${b.tone.title}">${b.count}</text>
    <text x="${lx + 22}" y="${ly}" dx="140" font-family="Segoe UI, sans-serif" font-size="10" fill="${TEXT_MUTED}">migrate: ${escapeXml(b.verdict)}</text>`;
    }).join('');

    return {
        height: h,
        svg: `<g transform="translate(0, ${yOffset})">${panel({ x, y: 0, w, h, title: 'Non-ACT Alex Repos \u2014 Activity & Migration', color: COLORS.fabric, subtitle: `${repos.length} total \u00b7 see DASHBOARD.md for inventory` })}${segs.join('')}${legend}</g>`,
    };
}

function versionCoveragePanelFragment(yOffset, probe) {
    const x = PAD, w = SHARED_WIDTH - 2 * PAD;
    const headerH = 24;
    const total = probe.count || 0;
    const withV = probe.with_version || 0;
    const pct = total > 0 ? Math.round((withV / total) * 100) : 0;

    // Group by source
    const sourceMap = {};
    for (const r of probe.repos || []) {
        const key = r.source || 'none';
        sourceMap[key] = (sourceMap[key] || 0) + 1;
    }
    const sourceOrder = ['package.json', 'CHANGELOG.md', 'git-tag', 'pyproject.toml', 'VERSION', 'copilot-instructions(frontmatter)', 'copilot-instructions(currency)', 'none'];
    const toneFor = {
        'package.json': COLORS.azure,
        'CHANGELOG.md': COLORS.fresh,
        'git-tag': COLORS.indigo,
        'pyproject.toml': COLORS.fabric,
        'VERSION': COLORS.warn,
        'copilot-instructions(frontmatter)': COLORS.warn,
        'copilot-instructions(currency)': COLORS.warn,
        'none': COLORS.neutral,
    };
    const rows = sourceOrder
        .filter((k) => sourceMap[k])
        .map((k) => ({ key: k, count: sourceMap[k], tone: toneFor[k] || COLORS.neutral }));

    if (total === 0 || rows.length === 0) {
        const h = headerH + 40;
        return {
            height: h,
            svg: `<g transform="translate(0, ${yOffset})">${panel({ x, y: 0, w, h, title: 'Non-ACT Version Coverage', color: COLORS.azure, subtitle: '0 probed' })}<text x="${x + w / 2}" y="${headerH + 24}" text-anchor="middle" font-family="Segoe UI, sans-serif" font-size="12" fill="${TEXT_MUTED}">No version data.</text></g>`,
        };
    }

    // Stacked bar
    const barX = x + 14;
    const barW = w - 28;
    const barY = headerH + 18;
    const barH = 22;

    // Legend (variable rows of 2 cols)
    const legendY = barY + barH + 18;
    const legendRows = Math.ceil(rows.length / 2);
    const h = headerH + 12 + barH + 18 + legendRows * 22 + 12;

    const segs = [];
    let cursor = 0;
    for (const r of rows) {
        const segW = (r.count / total) * barW;
        segs.push(`
    <rect x="${barX + cursor}" y="${barY}" width="${segW}" height="${barH}" fill="${r.tone.fill}" stroke="${r.tone.stroke}" stroke-width="1"/>
    ${segW > 24 ? `<text x="${barX + cursor + segW / 2}" y="${barY + 15}" text-anchor="middle" font-family="Segoe UI, sans-serif" font-size="11" font-weight="700" fill="${r.tone.title}">${r.count}</text>` : ''}`);
        cursor += segW;
    }

    const legend = rows.map((r, i) => {
        const col = i % 2;
        const row = Math.floor(i / 2);
        const lx = barX + col * (barW / 2);
        const ly = legendY + row * 22;
        return `
    <rect x="${lx}" y="${ly - 9}" width="14" height="12" rx="2" fill="${r.tone.fill}" stroke="${r.tone.stroke}" stroke-width="1"/>
    <text x="${lx + 22}" y="${ly}" font-family="Segoe UI, sans-serif" font-size="11" fill="${TEXT_DARK}">${escapeXml(r.key)}</text>
    <text x="${lx + 22}" y="${ly}" dx="200" font-family="Segoe UI, sans-serif" font-size="11" font-weight="700" fill="${r.tone.title}">${r.count}</text>`;
    }).join('');

    return {
        height: h,
        svg: `<g transform="translate(0, ${yOffset})">${panel({ x, y: 0, w, h, title: 'Non-ACT Version Coverage', color: COLORS.azure, subtitle: `${withV}/${total} discoverable \u00b7 ${pct}%` })}${segs.join('')}${legend}</g>`,
    };
}

function footerFragment(yOffset, parts) {
    const h = 28;
    const cx = SHARED_WIDTH / 2;
    const baseline = h / 2 + 4;
    const spans = parts.flatMap((p, i) => [
        i > 0 ? `<tspan fill="${TEXT_MUTED}" dx="6">·</tspan>` : '',
        `<tspan font-weight="700" fill="${TEXT_DARK}" ${i > 0 ? 'dx="6"' : ''}>${escapeXml(String(p.value))}</tspan>`,
        `<tspan fill="${TEXT_MUTED}" dx="4">${escapeXml(p.label)}</tspan>`,
    ]).filter(Boolean);
    return {
        height: h,
        svg: `<g transform="translate(0, ${yOffset})"><text x="${cx}" y="${baseline}" text-anchor="middle" font-family="Segoe UI, sans-serif" font-size="12">${spans.join('')}</text></g>`,
    };
}

// ---------- compose ----------
function compose() {
    const inv = runInventory();
    const probe = runVersionProbe();
    const heirs = (inv.heirs || []).slice().sort((a, b) => {
        const dv = cmpSemver(b.edition_version, a.edition_version);
        if (dv !== 0) return dv;
        return a.heir_id.localeCompare(b.heir_id);
    });
    const nonActRepos = inv.non_act_repos || [];
    const latestV = latestEditionVersion();

    const total = heirs.length;
    const upToDate = latestV ? heirs.filter((h) => h.edition_version === latestV).length : 0;
    const lagging = latestV ? heirs.filter((h) => cmpSemver(h.edition_version, latestV) < 0).length : 0;
    const stale = heirs.filter((h) => (h.days_since_sync ?? 0) > 90).length;

    // Median heir freshness (days since sync)
    const heirAges = heirs.map((h) => h.days_since_sync).filter((d) => typeof d === 'number').sort((a, b) => a - b);
    const medianAge = heirAges.length === 0 ? null : (heirAges.length % 2 === 1 ? heirAges[(heirAges.length - 1) / 2] : Math.round((heirAges[heirAges.length / 2 - 1] + heirAges[heirAges.length / 2]) / 2));

    // Migratable counts (Active=Yes / Recent=Maybe / Idle=Defer / Stale=No)
    let migYes = 0, migMaybe = 0, migDefer = 0, migNo = 0;
    for (const r of nonActRepos) {
        const d = r.days_since_commit == null ? Infinity : r.days_since_commit;
        if (d < 7) migYes++;
        else if (d <= 30) migMaybe++;
        else if (d <= 90) migDefer++;
        else migNo++;
    }

    const kpis = [
        { label: 'ACT HEIRS', value: total, tone: 'indigo', note: medianAge == null ? '' : `median age ${medianAge}d` },
        { label: 'UP TO DATE', value: upToDate, tone: 'fresh', note: latestV ? `on v${latestV}` : 'no tag found' },
        { label: 'LAGGING', value: lagging, tone: lagging > 0 ? 'warn' : 'neutral', note: lagging > 0 ? 'need upgrade-self' : 'all current' },
        { label: 'MIGRATE: YES', value: migYes, tone: 'fabric', note: `+${migMaybe} maybe \u00b7 ${nonActRepos.length} non-ACT` },
    ];

    const versionMap = {};
    for (const h of heirs) versionMap[h.edition_version] = (versionMap[h.edition_version] || 0) + 1;
    const versionRows = Object.entries(versionMap).sort((a, b) => cmpSemver(b[0], a[0]));

    const fragments = [];
    let y = PAD;

    const banner = bannerFragment(y, total, inv.scanned_at, latestV);
    fragments.push(banner.svg); y += banner.height + GAP;

    const kpi = kpiFragment(y, kpis);
    fragments.push(kpi.svg); y += kpi.height + GAP;

    if (versionRows.length > 0) {
        const verPanel = versionBarFragment(y, versionRows, latestV, total);
        fragments.push(verPanel.svg); y += verPanel.height + GAP;
    }

    const nonActPanel = nonActPanelFragment(y, nonActRepos);
    fragments.push(nonActPanel.svg); y += nonActPanel.height + GAP;

    const verPanel = versionCoveragePanelFragment(y, probe);
    fragments.push(verPanel.svg); y += verPanel.height + GAP;

    const footer = footerFragment(y, [
        { value: total, label: total === 1 ? 'ACT heir' : 'ACT heirs' },
        { value: upToDate, label: 'up to date' },
        { value: lagging, label: 'lagging' },
        { value: stale, label: 'stale' },
        { value: nonActRepos.length, label: 'non-ACT' },
        { value: `${migYes}+${migMaybe}`, label: 'migrate now/maybe' },
        { value: probe.with_version || 0, label: 'versioned' },
        { value: inv.invalid_count || 0, label: 'invalid' },
    ]);
    fragments.push(footer.svg); y += footer.height + PAD;

    const totalH = y;
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${SHARED_WIDTH} ${Math.round(totalH)}" width="${SHARED_WIDTH}" font-family="Segoe UI, system-ui, sans-serif">
  <rect x="0" y="0" width="${SHARED_WIDTH}" height="${Math.round(totalH)}" fill="#ffffff"/>
  ${fragments.join('\n')}
</svg>`;

    return { svg, totalH, total, upToDate, lagging, stale, nonAct: nonActRepos.length };
}

// ---------- review gate (rule 5 from skill) ----------
function reviewGate(svg, expected) {
    const checks = [];
    checks.push({ name: 'svg root present', ok: /<svg [^>]*>/.test(svg) });
    checks.push({ name: 'svg root closed', ok: /<\/svg>\s*$/.test(svg) });
    checks.push({ name: 'viewBox present', ok: /viewBox="0 0 /.test(svg) });
    checks.push({ name: `total count (${expected.total}) appears`, ok: svg.includes(`>${expected.total}<`) || expected.total === 0 });
    const failed = checks.filter((c) => !c.ok);
    return { ok: failed.length === 0, checks, failed };
}

// ---------- main ----------
function main() {
    const { svg, totalH, total, upToDate, lagging, stale, nonAct } = compose();
    const review = reviewGate(svg, { total });
    if (!review.ok) {
        console.error('Review gate failed:');
        for (const f of review.failed) console.error(`  \u2717 ${f.name}`);
        process.exit(2);
    }
    fs.mkdirSync(path.dirname(OUT), { recursive: true });
    fs.writeFileSync(OUT, svg, 'utf8');
    console.log(`Wrote ${path.relative(REPO_ROOT, OUT)} (${Math.round(totalH)}px tall)`);
    console.log(`  ${total} ACT heirs \u00b7 ${upToDate} up to date \u00b7 ${lagging} lagging \u00b7 ${stale} stale \u00b7 ${nonAct} non-ACT repos`);
}

if (require.main === module) main();

module.exports = { compose, cmpSemver };
