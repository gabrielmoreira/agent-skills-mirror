#!/usr/bin/env npx tsx
/**
 * TPB API Tool v2 — Search torrents & get magnet links
 *
 * Uses the public apibay.org JSON API. No scraping, no auth.
 *
 * v2 improvements:
 *   - --json flag on all commands for agent-parseable output
 *   - `season` command: auto-groups episodes, picks best per-episode, outputs all magnets
 *   - `open` command: launches magnet in default torrent client
 *   - `smart` command: auto-detects content type, applies quality preferences
 *   - Retry with exponential backoff on 429
 *   - Quality scoring & preference system
 *   - Search result enrichment (parsed resolution, codec, source, episode info)
 */

// ─── Config ──────────────────────────────────────────────────────────────────

const API_BASE = "https://apibay.org";

const TRACKERS = [
  "udp://tracker.opentrackr.org:1337",
  "udp://open.stealth.si:80/announce",
  "udp://tracker.torrent.eu.org:451/announce",
  "udp://tracker.bittor.pw:1337/announce",
  "udp://public.popcorn-tracker.org:6969/announce",
  "udp://tracker.dler.org:6969/announce",
  "udp://exodus.desync.com:6969",
  "udp://open.demonii.com:1337/announce",
  "udp://glotorrents.pw:6969/announce",
  "udp://tracker.coppersurfer.tk:6969",
  "udp://torrent.gresille.org:80/announce",
  "udp://p4p.arenabg.com:1337",
  "udp://tracker.internetwarriors.net:1337",
];

// ─── Category mapping ────────────────────────────────────────────────────────

const CATEGORY_MAP: Record<string, string> = {
  all: "0", audio: "100", video: "200", apps: "300", applications: "300",
  games: "400", porn: "500", other: "600",
  music: "101", audiobooks: "102", "sound-clips": "103", flac: "104",
  movies: "201", "movies-dvdr": "202", "music-videos": "203", "movie-clips": "204",
  "tv-shows": "205", tv: "205", "hd-movies": "207", "hd-tv": "208",
  "3d": "209", "cam-ts": "210", "uhd-movies": "211", "4k-movies": "211",
  "uhd-tv": "212", "4k-tv": "212",
  windows: "301", mac: "302", unix: "303", android: "306", ios: "305",
  "pc-games": "401", "mac-games": "402", psx: "403", xbox: "404",
  wii: "405", "android-games": "408",
  ebooks: "601", "e-books": "601", comics: "602", pictures: "603",
};

const CATEGORY_NAMES: Record<number, string> = {
  100: "Audio", 101: "Audio > Music", 102: "Audio > Audiobooks",
  103: "Audio > Sound clips", 104: "Audio > FLAC", 199: "Audio > Other",
  200: "Video", 201: "Video > Movies", 202: "Video > Movies DVDR",
  203: "Video > Music Videos", 204: "Video > Movie Clips", 205: "Video > TV Shows",
  206: "Video > Handheld", 207: "Video > HD Movies", 208: "Video > HD TV Shows",
  209: "Video > 3D", 210: "Video > CAM/TS", 211: "Video > UHD/4K Movies",
  212: "Video > UHD/4K TV Shows", 299: "Video > Other",
  300: "Applications", 301: "Apps > Windows", 302: "Apps > Mac",
  303: "Apps > UNIX", 304: "Apps > Handheld", 305: "Apps > iOS",
  306: "Apps > Android", 399: "Apps > Other",
  400: "Games", 401: "Games > PC", 402: "Games > Mac", 403: "Games > PSx",
  404: "Games > XBOX360", 405: "Games > Wii", 406: "Games > Handheld",
  407: "Games > iOS", 408: "Games > Android", 499: "Games > Other",
  500: "Porn", 501: "Porn > Movies", 505: "Porn > HD Movies",
  507: "Porn > UHD/4K", 599: "Porn > Other",
  600: "Other", 601: "Other > E-books", 602: "Other > Comics",
  603: "Other > Pictures", 604: "Other > Covers", 605: "Other > Physibles",
  699: "Other > Other",
};

// ─── Types ───────────────────────────────────────────────────────────────────

interface TorrentResult {
  id: string; name: string; info_hash: string; leechers: string;
  seeders: string; num_files: string; size: string; username: string;
  added: string; status: string; category: string; imdb: string;
  total_found?: string;
}

interface TorrentDetail extends TorrentResult {
  descr: string; language: string | null; textlanguage: number;
}

interface TorrentFile {
  name: [string]; size: [number];
}

// Enriched torrent with parsed metadata
interface EnrichedTorrent extends TorrentResult {
  magnet: string;
  parsed: {
    resolution: string | null;   // "2160p", "1080p", "720p", "480p"
    codec: string | null;        // "x265", "x264", "hevc", "av1"
    source: string | null;       // "bluray", "web-dl", "webrip", "hdtv", "cam", "ts"
    hdr: boolean;
    remux: boolean;
    season: number | null;
    episode: number | null;
    seasonPack: boolean;         // "S01" with no episode = full season
    qualityScore: number;        // 0-100 composite score
    trustScore: number;          // 0-100 based on status + seeders
  };
  size_bytes: number;
  size_human: string;
  category_name: string;
  date: string;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function formatSize(bytes: number): string {
  if (bytes >= 1099511627776) return (bytes / 1099511627776).toFixed(2) + " TiB";
  if (bytes >= 1073741824) return (bytes / 1073741824).toFixed(2) + " GiB";
  if (bytes >= 1048576) return (bytes / 1048576).toFixed(2) + " MiB";
  if (bytes >= 1024) return (bytes / 1024).toFixed(2) + " KiB";
  return bytes + " B";
}

function formatDate(unixTs: number): string {
  if (unixTs === 0) return "N/A";
  return new Date(unixTs * 1000).toISOString().split("T")[0];
}

function buildMagnetLink(infoHash: string, name: string): string {
  const dn = encodeURIComponent(name);
  const trackers = TRACKERS.map((t) => "&tr=" + encodeURIComponent(t)).join("");
  return `magnet:?xt=urn:btih:${infoHash}&dn=${dn}${trackers}`;
}

function getCategoryName(cat: number): string {
  return CATEGORY_NAMES[cat] || `Unknown (${cat})`;
}

function resolveCategoryCode(input: string): string {
  const lower = input.toLowerCase().trim();
  if (CATEGORY_MAP[lower]) return CATEGORY_MAP[lower];
  if (/^\d+$/.test(lower)) return lower;
  console.error(`Unknown category: "${input}". Valid: ${Object.keys(CATEGORY_MAP).join(", ")}`);
  process.exit(1);
}

function statusBadge(status: string): string {
  switch (status) {
    case "vip": return "🟢VIP";
    case "trusted": return "🟡TRU";
    case "helper": return "🔵HLP";
    case "moderator": case "supermod": case "admin": return "⭐MOD";
    default: return "   ";
  }
}

function isNoResults(results: TorrentResult[]): boolean {
  return results.length === 1 && results[0].id === "0" &&
    results[0].info_hash === "0000000000000000000000000000000000000000";
}

// ─── Torrent Name Parser ─────────────────────────────────────────────────────

function parseTorrentName(name: string): EnrichedTorrent["parsed"] {
  const n = name.toLowerCase();

  // Resolution
  let resolution: string | null = null;
  if (/2160p|4k|uhd/i.test(name)) resolution = "2160p";
  else if (/1080p/i.test(name)) resolution = "1080p";
  else if (/720p/i.test(name)) resolution = "720p";
  else if (/480p|sd/i.test(name)) resolution = "480p";

  // Codec
  let codec: string | null = null;
  if (/x265|h\.?265|hevc/i.test(name)) codec = "x265";
  else if (/x264|h\.?264|avc/i.test(name)) codec = "x264";
  else if (/av1/i.test(name)) codec = "av1";
  else if (/xvid|divx/i.test(name)) codec = "xvid";

  // Source
  let source: string | null = null;
  if (/remux/i.test(name)) source = "remux";
  else if (/blu-?ray/i.test(name)) source = "bluray";
  else if (/web-?dl/i.test(name)) source = "web-dl";
  else if (/webrip/i.test(name)) source = "webrip";
  else if (/\bweb\b/i.test(name)) source = "web";
  else if (/hdtv/i.test(name)) source = "hdtv";
  else if (/dvdrip/i.test(name)) source = "dvdrip";
  else if (/\bcam\b/i.test(name)) source = "cam";
  else if (/\bts\b|telesync/i.test(name)) source = "ts";
  else if (/\bhdrip\b/i.test(name)) source = "hdrip";

  const hdr = /\bhdr\b|hdr10|dolby.?vision|\bdv\b/i.test(name);
  const remux = /remux/i.test(name);

  // Season/Episode
  const seMatch = name.match(/S(\d{1,2})E(\d{1,3})/i);
  const seasonOnlyMatch = name.match(/S(\d{1,2})(?!E)/i);
  let season: number | null = null;
  let episode: number | null = null;
  let seasonPack = false;

  if (seMatch) {
    season = parseInt(seMatch[1]);
    episode = parseInt(seMatch[2]);
  } else if (seasonOnlyMatch) {
    season = parseInt(seasonOnlyMatch[1]);
    seasonPack = true;
  } else {
    // Try "Season 1" or "season.1" patterns
    const seasonWordMatch = name.match(/season[\s._-]*(\d{1,2})/i);
    if (seasonWordMatch) {
      season = parseInt(seasonWordMatch[1]);
      seasonPack = true;
    }
  }

  // Quality scoring
  const resScore: Record<string, number> = { "2160p": 40, "1080p": 30, "720p": 15, "480p": 5 };
  const srcScore: Record<string, number> = {
    remux: 30, bluray: 25, "web-dl": 20, web: 18, webrip: 15,
    hdtv: 10, hdrip: 8, dvdrip: 5, ts: 2, cam: 1,
  };
  const codecScore: Record<string, number> = { x265: 15, av1: 15, x264: 10, xvid: 3 };

  let qualityScore = 0;
  if (resolution) qualityScore += resScore[resolution] || 0;
  if (source) qualityScore += srcScore[source] || 0;
  if (codec) qualityScore += codecScore[codec] || 0;
  if (hdr) qualityScore += 10;
  if (remux) qualityScore += 5;

  // Trust score is computed in enrichTorrent (needs seeders + status)
  return { resolution, codec, source, hdr, remux, season, episode, seasonPack, qualityScore, trustScore: 0 };
}

function enrichTorrent(t: TorrentResult): EnrichedTorrent {
  const parsed = parseTorrentName(t.name);

  // Trust score: status + seeders
  const statusScores: Record<string, number> = {
    vip: 40, trusted: 30, helper: 20, moderator: 50, supermod: 50, admin: 50,
  };
  const seeders = parseInt(String(t.seeders));
  let trustScore = statusScores[t.status] || 0;
  if (seeders >= 100) trustScore += 40;
  else if (seeders >= 50) trustScore += 30;
  else if (seeders >= 20) trustScore += 20;
  else if (seeders >= 5) trustScore += 10;
  else if (seeders >= 1) trustScore += 5;
  parsed.trustScore = Math.min(trustScore, 100);

  const sizeBytes = parseInt(String(t.size));

  return {
    ...t,
    magnet: buildMagnetLink(t.info_hash, t.name),
    parsed,
    size_bytes: sizeBytes,
    size_human: formatSize(sizeBytes),
    category_name: getCategoryName(parseInt(String(t.category))),
    date: formatDate(parseInt(String(t.added))),
  };
}

// ─── API Functions with Retry ────────────────────────────────────────────────

async function fetchWithRetry(url: string, maxRetries = 3): Promise<Response> {
  let lastError: Error | null = null;
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const res = await fetch(url);
      if (res.status === 429) {
        const waitMs = Math.min(1000 * Math.pow(2, attempt + 1), 30000); // 2s, 4s, 8s, max 30s
        console.error(`  ⏳ Rate limited (429). Retrying in ${waitMs / 1000}s... (${attempt + 1}/${maxRetries})`);
        await new Promise((r) => setTimeout(r, waitMs));
        continue;
      }
      if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`);
      return res;
    } catch (e: any) {
      lastError = e;
      if (attempt < maxRetries && e.message?.includes("429")) continue;
      if (attempt < maxRetries && e.code === "ECONNRESET") {
        await new Promise((r) => setTimeout(r, 2000));
        continue;
      }
      throw e;
    }
  }
  throw lastError || new Error("Max retries exceeded");
}

async function apiSearch(query: string, category: string = "0"): Promise<TorrentResult[]> {
  const url = `${API_BASE}/q.php?q=${encodeURIComponent(query)}&cat=${category}`;
  const res = await fetchWithRetry(url);
  const data: TorrentResult[] = await res.json();
  if (isNoResults(data)) return [];
  return data;
}

async function apiDetail(id: string): Promise<TorrentDetail> {
  const url = `${API_BASE}/t.php?id=${encodeURIComponent(id)}`;
  const res = await fetchWithRetry(url);
  return res.json();
}

async function apiFiles(id: string): Promise<TorrentFile[]> {
  const url = `${API_BASE}/f.php?id=${encodeURIComponent(id)}`;
  const res = await fetchWithRetry(url);
  return res.json();
}

async function apiTop100(category: string = "all"): Promise<TorrentResult[]> {
  const slug = category === "all" ? "all" : category;
  const url = `${API_BASE}/precompiled/data_top100_${slug}.json`;
  const res = await fetchWithRetry(url);
  return res.json();
}

async function apiRecent(page: number = 0): Promise<TorrentResult[]> {
  const suffix = page === 0 ? "" : `_${page}`;
  const url = `${API_BASE}/precompiled/data_top100_recent${suffix}.json`;
  const res = await fetchWithRetry(url);
  return res.json();
}

// ─── Smart Search Logic ──────────────────────────────────────────────────────

function filterByQuality(results: EnrichedTorrent[], prefer?: string): EnrichedTorrent[] {
  if (!prefer) return results;
  const prefs = prefer.toLowerCase().split(",").map((p) => p.trim());

  return results.filter((t) => {
    for (const pref of prefs) {
      if (pref === "vip" && t.status !== "vip") return false;
      if (pref === "trusted" && !["vip", "trusted"].includes(t.status)) return false;
      if (["2160p", "1080p", "720p", "480p"].includes(pref) && t.parsed.resolution !== pref) return false;
      if (["x265", "x264", "hevc", "av1"].includes(pref) && t.parsed.codec !== pref) return false;
      if (["bluray", "web-dl", "webrip", "web", "remux"].includes(pref) && t.parsed.source !== pref) return false;
      if (pref === "hdr" && !t.parsed.hdr) return false;
    }
    return true;
  });
}

function rankResults(results: EnrichedTorrent[]): EnrichedTorrent[] {
  return [...results].sort((a, b) => {
    // Combined score: quality (0-100) + trust (0-100), weighted
    const scoreA = a.parsed.qualityScore * 0.4 + a.parsed.trustScore * 0.6;
    const scoreB = b.parsed.qualityScore * 0.4 + b.parsed.trustScore * 0.6;
    return scoreB - scoreA;
  });
}

// ─── Season Logic ────────────────────────────────────────────────────────────

interface SeasonResult {
  show: string;
  season: number;
  episodes: Map<number, EnrichedTorrent>;  // episode number → best torrent
  seasonPacks: EnrichedTorrent[];
  missing: number[];
  totalSize: number;
  magnets: string[];
}

function buildSeasonResult(
  results: EnrichedTorrent[],
  targetSeason: number,
  preferQuality?: string,
): SeasonResult {
  // Filter to target season
  let seasonResults = results.filter((t) =>
    t.parsed.season === targetSeason && (t.parsed.episode !== null || t.parsed.seasonPack)
  );

  // Apply quality filter if specified
  if (preferQuality) {
    const filtered = filterByQuality(seasonResults, preferQuality);
    if (filtered.length > 0) seasonResults = filtered;
  }

  // Separate packs from individual episodes
  const packs = seasonResults.filter((t) => t.parsed.seasonPack);
  const episodes = seasonResults.filter((t) => t.parsed.episode !== null);

  // Pick best torrent per episode (highest combined quality+trust score)
  const episodeMap = new Map<number, EnrichedTorrent>();
  for (const t of episodes) {
    const ep = t.parsed.episode!;
    const existing = episodeMap.get(ep);
    if (!existing) {
      episodeMap.set(ep, t);
    } else {
      const scoreNew = t.parsed.qualityScore * 0.4 + t.parsed.trustScore * 0.6;
      const scoreOld = existing.parsed.qualityScore * 0.4 + existing.parsed.trustScore * 0.6;
      if (scoreNew > scoreOld) episodeMap.set(ep, t);
    }
  }

  // Determine expected episode range
  const epNumbers = [...episodeMap.keys()].sort((a, b) => a - b);
  const maxEp = epNumbers.length > 0 ? epNumbers[epNumbers.length - 1] : 0;
  const missing: number[] = [];
  for (let i = 1; i <= maxEp; i++) {
    if (!episodeMap.has(i)) missing.push(i);
  }

  // Build ordered magnets
  const orderedEps = [...episodeMap.entries()].sort(([a], [b]) => a - b);
  const magnets = orderedEps.map(([, t]) => t.magnet);

  const totalSize = orderedEps.reduce((sum, [, t]) => sum + t.size_bytes, 0);

  // Infer show name from first result (strip S##E## and release info)
  const firstResult = orderedEps[0]?.[1] || packs[0];
  const show = firstResult
    ? firstResult.name.replace(/[.\s_-]*S\d{1,2}E?\d{0,3}.*/i, "").replace(/\./g, " ").trim()
    : "Unknown";

  return { show, season: targetSeason, episodes: episodeMap, seasonPacks: packs, missing, totalSize, magnets };
}

// ─── Display Functions ───────────────────────────────────────────────────────

function printResults(results: TorrentResult[], limit?: number, jsonMode = false) {
  const enriched = results.map(enrichTorrent);
  const sorted = [...enriched].sort((a, b) => parseInt(String(b.seeders)) - parseInt(String(a.seeders)));
  const display = limit ? sorted.slice(0, limit) : sorted;

  if (display.length === 0) {
    if (jsonMode) console.log(JSON.stringify([]));
    else console.log("No results found.");
    return;
  }

  if (jsonMode) {
    console.log(JSON.stringify(display, null, 2));
    return;
  }

  console.log(`\n  Found ${results.length} results (showing ${display.length}):\n`);
  console.log(
    "  " + "#".padEnd(4) + "SE".padStart(6) + "LE".padStart(6) + "  " +
    "Size".padEnd(12) + "Status".padEnd(8) + "Q".padStart(3) + "  " +
    "Res".padEnd(6) + "Category".padEnd(22) + "Name"
  );
  console.log("  " + "─".repeat(130));

  display.forEach((t, i) => {
    const res = t.parsed.resolution || "  -";
    const line =
      `  ${String(i + 1).padEnd(4)}` +
      `${String(t.seeders).padStart(6)}` +
      `${String(t.leechers).padStart(6)}` +
      `  ${t.size_human.padEnd(12)}` +
      `${statusBadge(t.status).padEnd(8)}` +
      `${String(t.parsed.qualityScore).padStart(3)}  ` +
      `${res.padEnd(6)}` +
      `${t.category_name.padEnd(22)}` +
      `${t.name}`;
    console.log(line);
    console.log(`       ID: ${t.id}  |  User: ${t.username}  |  Date: ${t.date}`);
  });
  console.log();
}

function printDetail(detail: TorrentDetail, jsonMode = false) {
  const enriched = enrichTorrent(detail);
  if (jsonMode) {
    console.log(JSON.stringify(enriched, null, 2));
    return;
  }
  console.log(`\n  ── Torrent Detail ──────────────────────────────────────\n`);
  console.log(`  Name:       ${detail.name}`);
  console.log(`  ID:         ${detail.id}`);
  console.log(`  Hash:       ${detail.info_hash}`);
  console.log(`  Category:   ${enriched.category_name}`);
  console.log(`  Size:       ${enriched.size_human}`);
  console.log(`  Files:      ${detail.num_files}`);
  console.log(`  Seeders:    ${detail.seeders}`);
  console.log(`  Leechers:   ${detail.leechers}`);
  console.log(`  Uploaded:   ${enriched.date}`);
  console.log(`  User:       ${detail.username} ${statusBadge(detail.status)}`);
  console.log(`  Quality:    ${enriched.parsed.qualityScore}/100  Trust: ${enriched.parsed.trustScore}/100`);
  if (enriched.parsed.resolution) console.log(`  Resolution: ${enriched.parsed.resolution}`);
  if (enriched.parsed.codec) console.log(`  Codec:      ${enriched.parsed.codec}`);
  if (enriched.parsed.source) console.log(`  Source:     ${enriched.parsed.source}`);
  if (detail.imdb) console.log(`  IMDB:       https://www.imdb.com/title/${detail.imdb}/`);
  console.log(`\n  Description:`);
  console.log(`  ${(detail.descr || "None").replace(/\r?\n/g, "\n  ")}`);
  console.log(`\n  Magnet Link:`);
  console.log(`  ${enriched.magnet}`);
  console.log();
}

function printFiles(files: TorrentFile[], id: string, jsonMode = false) {
  if (jsonMode) {
    const data = files.map((f) => ({ name: f.name[0], size: f.size[0], size_human: formatSize(f.size[0]) }));
    console.log(JSON.stringify(data, null, 2));
    return;
  }
  console.log(`\n  ── File List (torrent ${id}) ──\n`);
  files.forEach((f, i) => {
    console.log(`  ${String(i + 1).padEnd(4)} ${formatSize(f.size[0]).padEnd(12)} ${f.name[0]}`);
  });
  console.log();
}

function printSeason(sr: SeasonResult, jsonMode = false) {
  if (jsonMode) {
    const episodes = [...sr.episodes.entries()]
      .sort(([a], [b]) => a - b)
      .map(([ep, t]) => ({
        episode: ep,
        name: t.name,
        magnet: t.magnet,
        seeders: parseInt(String(t.seeders)),
        size_human: t.size_human,
        size_bytes: t.size_bytes,
        quality_score: t.parsed.qualityScore,
        trust_score: t.parsed.trustScore,
        resolution: t.parsed.resolution,
        codec: t.parsed.codec,
        source: t.parsed.source,
        username: t.username,
        status: t.status,
      }));
    console.log(JSON.stringify({
      show: sr.show,
      season: sr.season,
      episode_count: sr.episodes.size,
      missing_episodes: sr.missing,
      total_size: formatSize(sr.totalSize),
      total_size_bytes: sr.totalSize,
      season_packs: sr.seasonPacks.map((p) => ({
        name: p.name, magnet: p.magnet, seeders: parseInt(String(p.seeders)),
        size_human: p.size_human, quality_score: p.parsed.qualityScore,
      })),
      episodes,
    }, null, 2));
    return;
  }

  console.log(`\n  ── ${sr.show} — Season ${sr.season} ──────────────────────────────────\n`);

  if (sr.seasonPacks.length > 0) {
    console.log(`  📦 Season Packs Available:`);
    for (const p of sr.seasonPacks) {
      console.log(`     ${p.name}`);
      console.log(`     SE:${p.seeders} | ${p.size_human} | Q:${p.parsed.qualityScore} | ${statusBadge(p.status)} ${p.username}`);
    }
    console.log();
  }

  console.log(`  📺 Individual Episodes (${sr.episodes.size} found):\n`);
  console.log("  " + "EP".padEnd(5) + "SE".padStart(5) + "  " + "Size".padEnd(12) + "Q".padStart(3) + "  " + "Status".padEnd(8) + "Name");
  console.log("  " + "─".repeat(110));

  const orderedEps = [...sr.episodes.entries()].sort(([a], [b]) => a - b);
  for (const [ep, t] of orderedEps) {
    console.log(
      `  E${String(ep).padStart(2, "0").padEnd(3)}` +
      `${String(t.seeders).padStart(5)}  ` +
      `${t.size_human.padEnd(12)}` +
      `${String(t.parsed.qualityScore).padStart(3)}  ` +
      `${statusBadge(t.status).padEnd(8)}` +
      `${t.name}`
    );
  }

  if (sr.missing.length > 0) {
    console.log(`\n  ⚠️  Missing episodes: ${sr.missing.map((e) => `E${String(e).padStart(2, "0")}`).join(", ")}`);
  }

  console.log(`\n  Total: ${formatSize(sr.totalSize)} across ${sr.episodes.size} episodes`);
  console.log(`\n  ── Magnet Links (copy all) ──\n`);
  for (const [ep, t] of orderedEps) {
    console.log(`  # E${String(ep).padStart(2, "0")} — ${t.name}`);
    console.log(`  ${t.magnet}\n`);
  }
}

// ─── CLI ─────────────────────────────────────────────────────────────────────

function printUsage() {
  console.log(`
  TPB API Tool v2 — Search torrents & get magnet links

  Usage:
    tpb search <query> [options]       Search torrents
    tpb season <query> --s <n> [opts]  Get all episodes for a TV season
    tpb grab <query> [options]         Search + instant magnet (1 API call)
    tpb smart <query> [options]        Auto-detect type, apply quality prefs
    tpb detail <id>                    Full torrent info
    tpb files <id>                     List files in torrent
    tpb magnet <id>                    Print magnet link only
    tpb open <id|query> [options]      Launch magnet in torrent client
    tpb top100 [options]               Top 100 most seeded
    tpb recent [options]               Recently uploaded

  Options:
    --cat <category>      Filter by category (video, audio, apps, etc.)
    --limit <n>           Max results to show
    --prefer <filters>    Quality preferences: "1080p,x265,vip"
    --json                Output raw JSON (for agent/script use)
    --s <n>               Season number (for season command)
    --n <count>           Number of results (for grab command)

  Categories:
    all, audio, video, apps, games, other, ebooks
    movies, tv, hd-movies, hd-tv, 4k-movies, 4k-tv
    music, audiobooks, flac, windows, mac, android, ios

  Quality Filters (--prefer):
    Resolution: 2160p, 1080p, 720p
    Codec:      x265, x264, av1
    Source:     bluray, web-dl, webrip, remux
    Trust:      vip, trusted
    Other:      hdr

  Examples:
    tpb search "ubuntu 24.04"
    tpb search "interstellar" --cat video --prefer "1080p,x265"
    tpb season "1670" --s 1                          # all S01 episodes
    tpb season "breaking bad" --s 3 --prefer "1080p,vip"
    tpb smart "dark knight rises"                    # auto-detect movie
    tpb grab "ubuntu" --cat apps                     # instant magnet
    tpb open "dark knight" --cat video               # search + open in client
    tpb top100 --cat video --limit 10 --json         # agent-friendly output
`);
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === "--help" || args[0] === "-h") {
    printUsage();
    process.exit(0);
  }

  const command = args[0];

  // Parse flags (supports --flag value and --flag with no value for booleans)
  const flags: Record<string, string> = {};
  const positional: string[] = [];
  for (let i = 1; i < args.length; i++) {
    if (args[i] === "--json") {
      flags.json = "true";
    } else if (args[i].startsWith("--") && i + 1 < args.length && !args[i + 1].startsWith("--")) {
      flags[args[i].slice(2)] = args[i + 1];
      i++;
    } else if (args[i].startsWith("--")) {
      flags[args[i].slice(2)] = "true";
    } else {
      positional.push(args[i]);
    }
  }

  const jsonMode = flags.json === "true";

  try {
    switch (command) {
      case "search":
      case "s": {
        const query = positional[0];
        if (!query) { console.error('Error: search requires a query.'); process.exit(1); }
        const cat = flags.cat ? resolveCategoryCode(flags.cat) : "0";
        const limit = flags.limit ? parseInt(flags.limit) : undefined;
        let results = await apiSearch(query, cat);
        if (flags.prefer) {
          const enriched = results.map(enrichTorrent);
          const filtered = filterByQuality(enriched, flags.prefer);
          if (filtered.length > 0) {
            // Output filtered results but we need TorrentResult[] for printResults
            // Actually just use enriched path
            const ranked = rankResults(filtered);
            const display = limit ? ranked.slice(0, limit) : ranked;
            if (jsonMode) { console.log(JSON.stringify(display, null, 2)); }
            else { printResults(display.map((e) => e as TorrentResult), limit, false); }
            break;
          }
          // If filter yields nothing, fall through to unfiltered
          if (!jsonMode) console.log("  ⚠️  No results match preferences, showing all:");
        }
        printResults(results, limit, jsonMode);
        break;
      }

      case "season":
      case "ss": {
        const query = positional[0];
        if (!query) { console.error('Error: season requires a show name.'); process.exit(1); }
        const seasonNum = flags.s ? parseInt(flags.s) : 1;
        const cat = flags.cat ? resolveCategoryCode(flags.cat) : "200"; // default to video
        const results = await apiSearch(query, cat);
        const enriched = results.map(enrichTorrent);
        const sr = buildSeasonResult(enriched, seasonNum, flags.prefer);

        if (sr.episodes.size === 0 && sr.seasonPacks.length === 0) {
          if (jsonMode) console.log(JSON.stringify({ error: "No episodes found", show: query, season: seasonNum }));
          else console.log(`\n  No episodes found for "${query}" Season ${seasonNum}.\n  Try a different search query or check --s number.`);
          break;
        }
        printSeason(sr, jsonMode);
        break;
      }

      case "smart": {
        const query = positional[0];
        if (!query) { console.error('Error: smart requires a query.'); process.exit(1); }

        // Auto-detect: search in video first
        let results = await apiSearch(query, "200");
        if (results.length === 0) {
          // Fallback to all categories
          results = await apiSearch(query, "0");
        }
        if (results.length === 0) {
          if (jsonMode) console.log(JSON.stringify({ error: "No results found" }));
          else console.log("No results found.");
          break;
        }

        const enriched = results.map(enrichTorrent);

        // Detect if it's a TV show (multiple episodes from same show)
        const hasEpisodes = enriched.filter((t) => t.parsed.episode !== null);
        const seasons = new Set(hasEpisodes.map((t) => t.parsed.season));

        if (hasEpisodes.length > enriched.length * 0.3 && seasons.size <= 5) {
          // It's a TV show — group by season
          if (!jsonMode) console.log(`  🔍 Detected TV show with ${seasons.size} season(s): ${[...seasons].sort((a, b) => a! - b!).map((s) => `S${String(s).padStart(2, "0")}`).join(", ")}`);

          if (seasons.size === 1) {
            const sr = buildSeasonResult(enriched, [...seasons][0]!, flags.prefer);
            printSeason(sr, jsonMode);
          } else {
            // Multiple seasons — show summary
            const summaries = [...seasons].sort((a, b) => a! - b!).map((s) => {
              const sr = buildSeasonResult(enriched, s!, flags.prefer);
              return { season: s, episodeCount: sr.episodes.size, totalSize: formatSize(sr.totalSize) };
            });
            if (jsonMode) {
              console.log(JSON.stringify({ type: "tv_show", seasons: summaries }));
            } else {
              console.log(`\n  Available seasons:`);
              for (const s of summaries) {
                console.log(`    Season ${s.season}: ${s.episodeCount} episodes (${s.totalSize})`);
              }
              console.log(`\n  Use: tpb season "${query}" --s <n> to get a specific season.`);
            }
          }
        } else {
          // It's a movie or general content — rank and show best
          let ranked = rankResults(enriched);
          if (flags.prefer) {
            const filtered = filterByQuality(ranked, flags.prefer);
            if (filtered.length > 0) ranked = filtered;
          }

          // Filter out CAM/TS for movies unless nothing else available
          const goodQuality = ranked.filter((t) => !["cam", "ts"].includes(t.parsed.source || ""));
          if (goodQuality.length > 0) ranked = goodQuality;

          const limit = flags.limit ? parseInt(flags.limit) : 10;
          const display = ranked.slice(0, limit);

          if (jsonMode) {
            console.log(JSON.stringify(display, null, 2));
          } else {
            console.log(`\n  🔍 Detected movie/content — ranked by quality + trust:\n`);
            console.log("  " + "#".padEnd(4) + "Score".padStart(5) + "  " + "SE".padStart(5) + "  " +
              "Size".padEnd(12) + "Res".padEnd(7) + "Source".padEnd(10) + "Status".padEnd(8) + "Name");
            console.log("  " + "─".repeat(120));
            display.forEach((t, i) => {
              const score = Math.round(t.parsed.qualityScore * 0.4 + t.parsed.trustScore * 0.6);
              console.log(
                `  ${String(i + 1).padEnd(4)}` +
                `${String(score).padStart(5)}  ` +
                `${String(t.seeders).padStart(5)}  ` +
                `${t.size_human.padEnd(12)}` +
                `${(t.parsed.resolution || "-").padEnd(7)}` +
                `${(t.parsed.source || "-").padEnd(10)}` +
                `${statusBadge(t.status).padEnd(8)}` +
                `${t.name}`
              );
            });
            if (display.length > 0) {
              console.log(`\n  🏆 Recommended: #1 — ${display[0].name}`);
              console.log(`  ${display[0].magnet}\n`);
            }
          }
        }
        break;
      }

      case "detail":
      case "d":
      case "info": {
        const id = positional[0];
        if (!id) { console.error("Error: detail requires a torrent ID."); process.exit(1); }
        const detail = await apiDetail(id);
        printDetail(detail, jsonMode);
        break;
      }

      case "files":
      case "f": {
        const id = positional[0];
        if (!id) { console.error("Error: files requires a torrent ID."); process.exit(1); }
        const files = await apiFiles(id);
        printFiles(files, id, jsonMode);
        break;
      }

      case "magnet":
      case "m": {
        const id = positional[0];
        if (!id) { console.error("Error: magnet requires a torrent ID."); process.exit(1); }
        const detail = await apiDetail(id);
        const magnet = buildMagnetLink(detail.info_hash, detail.name);
        if (jsonMode) console.log(JSON.stringify({ id, name: detail.name, magnet }));
        else console.log(magnet);
        break;
      }

      case "open":
      case "o": {
        // Two modes: open by ID (numeric) or open by search query
        const input = positional[0];
        if (!input) { console.error("Error: open requires a torrent ID or search query."); process.exit(1); }

        let magnet: string;
        let name: string;

        if (/^\d+$/.test(input)) {
          // It's an ID
          const detail = await apiDetail(input);
          magnet = buildMagnetLink(detail.info_hash, detail.name);
          name = detail.name;
        } else {
          // It's a search query — grab top result
          const cat = flags.cat ? resolveCategoryCode(flags.cat) : "0";
          const results = await apiSearch(input, cat);
          if (results.length === 0) { console.error("No results found."); process.exit(1); }
          const enriched = results.map(enrichTorrent);
          let ranked = rankResults(enriched);
          if (flags.prefer) {
            const filtered = filterByQuality(ranked, flags.prefer);
            if (filtered.length > 0) ranked = filtered;
          }
          const best = ranked[0];
          magnet = best.magnet;
          name = best.name;
        }

        console.log(`  Opening: ${name}`);
        const { execSync } = await import("child_process");
        const platform = process.platform;
        try {
          if (platform === "darwin") {
            execSync(`open "${magnet}"`);
          } else if (platform === "linux") {
            execSync(`xdg-open "${magnet}"`);
          } else if (platform === "win32") {
            execSync(`start "" "${magnet}"`);
          } else {
            console.log(`  Platform "${platform}" not supported for open. Magnet link:`);
            console.log(`  ${magnet}`);
          }
          console.log("  ✅ Magnet link sent to torrent client.");
        } catch {
          console.log("  ⚠️  Could not open magnet link. Make sure a torrent client is installed.");
          console.log(`  ${magnet}`);
        }
        break;
      }

      case "grab":
      case "g": {
        const query = positional[0];
        if (!query) { console.error('Error: grab requires a query.'); process.exit(1); }
        const cat = flags.cat ? resolveCategoryCode(flags.cat) : "0";
        const n = flags.n ? parseInt(flags.n) : 1;
        const results = await apiSearch(query, cat);
        if (results.length === 0) { console.error("No results found."); process.exit(1); }
        let enriched = results.map(enrichTorrent);
        let ranked = rankResults(enriched);
        if (flags.prefer) {
          const filtered = filterByQuality(ranked, flags.prefer);
          if (filtered.length > 0) ranked = filtered;
        }
        const picks = ranked.slice(0, n);
        if (jsonMode) {
          console.log(JSON.stringify(picks.map((p) => ({
            name: p.name, magnet: p.magnet, seeders: parseInt(String(p.seeders)),
            size_human: p.size_human, quality_score: p.parsed.qualityScore,
            trust_score: p.parsed.trustScore, username: p.username, status: p.status,
          })), null, 2));
        } else {
          for (const pick of picks) {
            console.log(`# ${pick.name}`);
            console.log(`# SE:${pick.seeders} LE:${pick.leechers} ${pick.size_human} Q:${pick.parsed.qualityScore} T:${pick.parsed.trustScore} ${pick.username}(${pick.status})`);
            console.log(pick.magnet);
            console.log();
          }
        }
        break;
      }

      case "top100":
      case "top": {
        const catInput = flags.cat ? resolveCategoryCode(flags.cat) : "all";
        const limit = flags.limit ? parseInt(flags.limit) : undefined;
        const results = await apiTop100(catInput);
        printResults(results, limit, jsonMode);
        break;
      }

      case "recent":
      case "new": {
        const page = flags.page ? parseInt(flags.page) : 0;
        const limit = flags.limit ? parseInt(flags.limit) : undefined;
        const results = await apiRecent(page);
        printResults(results, limit, jsonMode);
        break;
      }

      default:
        console.error(`Unknown command: "${command}"`);
        printUsage();
        process.exit(1);
    }
  } catch (err: any) {
    if (jsonMode) console.log(JSON.stringify({ error: err.message }));
    else console.error(`Error: ${err.message}`);
    process.exit(1);
  }
}

main();

// ─── Exports ─────────────────────────────────────────────────────────────────

export {
  apiSearch, apiDetail, apiFiles, apiTop100, apiRecent,
  buildMagnetLink, enrichTorrent, parseTorrentName,
  filterByQuality, rankResults, buildSeasonResult,
  formatSize, formatDate, getCategoryName,
  TRACKERS, CATEGORY_MAP,
  type TorrentResult, type TorrentDetail, type TorrentFile, type EnrichedTorrent, type SeasonResult,
};
