#!/usr/bin/env node
// Fill in latitude/longitude for venue content files that do not have them yet.
//
//   node geocode-venues.mjs --dir src/content/venues --center 40.8677,-73.3537 [--max-km 250]
//        [--force] [--dry] [--country us] [--no-census] [--state NY] [--contact you@example.org]
//
// Venue files are Markdown with YAML front matter (or plain .yml/.yaml) containing at least
// `address` and `city` (and ideally `state`, `postalCode`, `name`).
// 1) U.S. Census Bureau geocoder (free, no key, public-domain results)
// 2) OpenStreetMap Nominatim fallback (max 1 request/second, identifying User-Agent, ODbL attribution)
// Writes latitude, longitude and coordinatesSource back into each file, preserving line endings.
// Requires the `yaml` package resolvable from the current working directory.
import { readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

export const CENSUS_SOURCE = 'U.S. Census Bureau Geocoder';
export const NOMINATIM_SOURCE = 'OpenStreetMap Nominatim (© OpenStreetMap contributors, ODbL)';

export function oneLineAddress(v, defaultState = '') {
  const street = String(v.address ?? '')
    .replace(/,?\s*(suite|ste\.?|unit|apt\.?|floor|fl\.?|room|rm\.?|#)\s*[\w-]+/gi, '')
    .trim();
  return [street, v.city, [v.state ?? defaultState, v.postalCode].filter(Boolean).join(' ')].filter(Boolean).join(', ');
}

export function distanceKm(a, b) {
  const rad = (d) => (d * Math.PI) / 180;
  const dLat = rad(b.lat - a.lat);
  const dLng = rad(b.lng - a.lng);
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(rad(a.lat)) * Math.cos(rad(b.lat)) * Math.sin(dLng / 2) ** 2;
  return 2 * 6371 * Math.asin(Math.sqrt(h));
}

export function parseCensus(json) {
  const m = json?.result?.addressMatches?.[0];
  if (!m?.coordinates) return undefined;
  return { lat: Number(m.coordinates.y), lng: Number(m.coordinates.x), matched: m.matchedAddress, source: CENSUS_SOURCE };
}

export function parseNominatim(json) {
  const m = Array.isArray(json) ? json[0] : undefined;
  if (!m) return undefined;
  return { lat: Number(m.lat), lng: Number(m.lon), matched: m.display_name, source: NOMINATIM_SOURCE };
}

const round = (n) => Math.round(n * 1e6) / 1e6;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function makeGeocoder({ center, maxKm, country, useCensus, contact }) {
  const userAgent = `community-site-geocoder/1.0 (${contact || 'https://github.com/michaelsrichter/community-site-kit'})`;
  const getJson = async (url) => {
    const res = await fetch(url, { headers: { 'user-agent': userAgent, accept: 'application/json' }, signal: AbortSignal.timeout(20000) });
    if (!res.ok) throw new Error(`${res.status} from ${new URL(url).host}`);
    return res.json();
  };
  const census = async (address) => {
    const u = new URL('https://geocoding.geo.census.gov/geocoder/locations/onelineaddress');
    u.searchParams.set('address', address);
    u.searchParams.set('benchmark', 'Public_AR_Current');
    u.searchParams.set('format', 'json');
    return parseCensus(await getJson(u));
  };
  let last = 0;
  const nominatim = async (q) => {
    const wait = 1100 - (Date.now() - last);
    if (wait > 0) await sleep(wait);
    last = Date.now();
    const u = new URL('https://nominatim.openstreetmap.org/search');
    u.searchParams.set('q', q);
    u.searchParams.set('format', 'jsonv2');
    u.searchParams.set('limit', '1');
    if (country) u.searchParams.set('countrycodes', country);
    return parseNominatim(await getJson(u));
  };
  return async (address, name) => {
    const attempts = [...(useCensus ? [() => census(address)] : []), () => nominatim(address), ...(name ? [() => nominatim(`${name}, ${address}`)] : [])];
    for (const attempt of attempts) {
      try {
        const hit = await attempt();
        if (hit && Number.isFinite(hit.lat) && Number.isFinite(hit.lng)) {
          if (center && distanceKm(center, hit) > maxKm) {
            console.warn(`  ! ignored a match ${Math.round(distanceKm(center, hit))} km away: ${hit.matched}`);
            continue;
          }
          return hit;
        }
      } catch (e) {
        console.warn(`  ! ${e.message}`);
      }
    }
    return undefined;
  };
}

async function main() {
  const args = process.argv.slice(2);
  const get = (k, d) => {
    const i = args.indexOf(`--${k}`);
    return i >= 0 ? args[i + 1] : d;
  };
  const dir = get('dir', 'src/content/venues');
  const centerArg = get('center');
  const center = centerArg ? (([lat, lng]) => ({ lat: Number(lat), lng: Number(lng) }))(centerArg.split(',')) : undefined;
  const maxKm = Number(get('max-km', '250'));
  const country = get('country', 'us');
  const defaultState = get('state', '');
  const force = args.includes('--force');
  const dry = args.includes('--dry');
  const useCensus = !args.includes('--no-census') && country === 'us';
  const require = createRequire(join(process.cwd(), 'package.json'));
  const YAML = require('yaml');
  const geocode = makeGeocoder({ center, maxKm, country, useCensus, contact: get('contact') });

  let updated = 0;
  const missing = [];
  for (const file of readdirSync(dir).filter((f) => /\.(md|ya?ml)$/i.test(f)).sort()) {
    const path = join(dir, file);
    const text = readFileSync(path, 'utf8');
    const isMd = file.endsWith('.md');
    const m = isMd ? text.match(/^---\r?\n([\s\S]*?)\r?\n---(\r?\n[\s\S]*)?$/) : [null, text, ''];
    if (!m) continue;
    const doc = YAML.parseDocument(m[1]);
    const v = doc.toJS() ?? {};
    if (!force && Number.isFinite(v.latitude) && Number.isFinite(v.longitude)) continue;
    if (!v.address || !v.city) {
      missing.push(`${file} (no street address)`);
      continue;
    }
    const address = oneLineAddress(v, defaultState);
    const hit = await geocode(address, v.name);
    if (!hit) {
      missing.push(`${file} (${address})`);
      console.warn(`✗ ${file}: no match for "${address}"`);
      continue;
    }
    console.log(`✓ ${file}: ${round(hit.lat)}, ${round(hit.lng)}  ← ${hit.source}${hit.matched ? `: ${hit.matched}` : ''}`);
    if (dry) continue;
    doc.set('latitude', round(hit.lat));
    doc.set('longitude', round(hit.lng));
    doc.set('coordinatesSource', hit.source);
    const eol = text.includes('\r\n') ? '\r\n' : '\n';
    const body = doc.toString({ lineWidth: 0 }).trimEnd().replace(/\n/g, eol);
    writeFileSync(path, isMd ? `---${eol}${body}${eol}---${m[2] ?? eol}` : body + eol);
    updated++;
  }
  console.log(`\n[geocode] ${updated} venue(s) updated${dry ? ' (dry run)' : ''}.`);
  if (missing.length) console.log(`[geocode] Could not place on the map (fix the address or enter coordinates by hand):\n  ${missing.join('\n  ')}`);
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) await main();
