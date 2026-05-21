#!/usr/bin/env node
/**
 * fetch-feeds.js
 * Fetches RSS/Atom feeds, filters by date window, deduplicates, and saves to JSON.
 *
 * Usage:
 *   node fetch-feeds.js              # Default: last 7 days
 *   node fetch-feeds.js --days=14    # Extend window to 14 days
 *
 * Output: /tmp/newsletter-digest-articles.json
 */

import Parser from 'rss-parser';
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Parse CLI args
const args = process.argv.slice(2);
const daysArg = args.find(a => a.startsWith('--days='));
const DAYS = daysArg ? parseInt(daysArg.split('=')[1], 10) : 7;
const OUTPUT_PATH = '/tmp/newsletter-digest-articles.json';
const FEEDS_PATH = join(__dirname, '..', 'feeds.json');

async function main() {
  // Load feeds config
  let feeds;
  try {
    feeds = JSON.parse(readFileSync(FEEDS_PATH, 'utf8'));
  } catch (err) {
    console.error(`ERROR: Could not read feeds.json at ${FEEDS_PATH}`);
    console.error('Create feeds.json with this format:');
    console.error('[{"url": "https://example.com/feed", "name": "Source Name"}]');
    process.exit(1);
  }

  if (!Array.isArray(feeds) || feeds.length === 0) {
    console.error('ERROR: feeds.json is empty or not an array.');
    process.exit(1);
  }

  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - DAYS);

  const parser = new Parser({
    timeout: 10000,
    headers: { 'User-Agent': 'newsletter-digest-skill/1.0' },
    customFields: {
      item: ['summary', 'description', 'content:encoded', 'media:content'],
    },
  });

  const allArticles = [];
  const seenUrls = new Set();
  const feedsSummary = [];

  for (const feed of feeds) {
    if (!feed.url || !feed.name) {
      console.warn(`WARN: Skipping malformed feed entry: ${JSON.stringify(feed)}`);
      continue;
    }

    let parsed;
    try {
      console.log(`Fetching: ${feed.name} (${feed.url})`);
      parsed = await parser.parseURL(feed.url);
    } catch (err) {
      console.warn(`WARN: Failed to fetch ${feed.name}: ${err.message}`);
      feedsSummary.push({ name: feed.name, count: 0, error: err.message });
      continue;
    }

    let feedCount = 0;
    for (const item of parsed.items) {
      const pubDate = item.pubDate || item.isoDate;
      if (!pubDate) continue;

      const publishedAt = new Date(pubDate);
      if (isNaN(publishedAt.getTime())) continue;
      if (publishedAt < cutoffDate) continue;

      const url = item.link || item.guid;
      if (!url || seenUrls.has(url)) continue;
      seenUrls.add(url);

      // Extract the best available summary
      const content =
        item['content:encoded'] ||
        item.content ||
        item.summary ||
        item.description ||
        '';

      // Strip HTML tags for plain text excerpt
      const plainText = content.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
      const excerpt = plainText.slice(0, 400) + (plainText.length > 400 ? '...' : '');

      allArticles.push({
        title: item.title || 'Untitled',
        url,
        source: feed.name,
        publishedAt: publishedAt.toISOString(),
        author: item.author || item.creator || '',
        excerpt,
      });
      feedCount++;
    }

    feedsSummary.push({ name: feed.name, count: feedCount });
    console.log(`  Found ${feedCount} articles in the last ${DAYS} days`);
  }

  // Sort newest first
  allArticles.sort((a, b) => new Date(b.publishedAt) - new Date(a.publishedAt));

  const output = {
    fetchedAt: new Date().toISOString(),
    daysWindow: DAYS,
    dateRange: {
      from: cutoffDate.toISOString(),
      to: new Date().toISOString(),
    },
    articles: allArticles,
    feedsSummary,
  };

  writeFileSync(OUTPUT_PATH, JSON.stringify(output, null, 2));

  console.log(`\nDone. ${allArticles.length} articles saved to ${OUTPUT_PATH}`);
  feedsSummary.forEach(f => {
    const status = f.error ? `ERROR: ${f.error}` : `${f.count} articles`;
    console.log(`  ${f.name}: ${status}`);
  });
}

main().catch(err => {
  console.error('Unexpected error:', err);
  process.exit(1);
});
