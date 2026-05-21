#!/usr/bin/env node
/**
 * monitor-hn.js
 * Monitors Hacker News for keywords via the Algolia search API.
 * Deduplicates via SQLite. Sends Slack alerts for new matching posts.
 *
 * Usage:
 *   node monitor-hn.js                  # Normal run
 *   node monitor-hn.js --dry-run        # Preview matches, no Slack alerts
 *   node monitor-hn.js --days=7         # Look back 7 days on first run
 *   node monitor-hn.js --reset          # Clear cache and start fresh
 *
 * Required env vars:
 *   HN_KEYWORDS     Comma-separated keywords (e.g. "claude code,LLM agents,deno")
 *   SLACK_WEBHOOK   Slack Incoming Webhook URL
 *
 * Optional env vars:
 *   HN_MIN_POINTS        Minimum points to alert (default: 0 = all posts)
 *   HN_INCLUDE_COMMENTS  Include comments in search (default: false)
 *   HN_DB_PATH           SQLite DB file path (default: ./hn-intel.db)
 */

import Database from 'better-sqlite3';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Parse CLI args
const args = process.argv.slice(2);
const DRY_RUN = args.includes('--dry-run');
const RESET = args.includes('--reset');
const daysArg = args.find(a => a.startsWith('--days='));
const FIRST_RUN_DAYS = daysArg ? parseInt(daysArg.split('=')[1], 10) : 1;

// Config from environment
const RAW_KEYWORDS = process.env.HN_KEYWORDS || '';
const SLACK_WEBHOOK = process.env.SLACK_WEBHOOK || '';
const MIN_POINTS = parseInt(process.env.HN_MIN_POINTS || '0', 10);
const INCLUDE_COMMENTS = process.env.HN_INCLUDE_COMMENTS === 'true';
const DB_PATH = process.env.HN_DB_PATH || join(__dirname, '..', 'hn-intel.db');

// Validate required config
if (!RAW_KEYWORDS.trim()) {
  console.error('ERROR: HN_KEYWORDS is not set.');
  console.error('Set it to a comma-separated list: HN_KEYWORDS="claude code,LLM agents"');
  process.exit(1);
}

if (!SLACK_WEBHOOK && !DRY_RUN) {
  console.error('ERROR: SLACK_WEBHOOK is not set.');
  console.error('Create one at: https://api.slack.com/apps');
  console.error('Or run with --dry-run to preview without sending alerts.');
  process.exit(1);
}

const keywords = RAW_KEYWORDS.split(',').map(k => k.trim()).filter(Boolean);

// Initialize SQLite
const db = new Database(DB_PATH);

if (RESET) {
  db.exec('DROP TABLE IF EXISTS seen_posts');
  db.exec('DROP TABLE IF EXISTS poll_log');
  console.log('Cache cleared.');
}

db.exec(`
  CREATE TABLE IF NOT EXISTS seen_posts (
    objectID   TEXT PRIMARY KEY,
    title      TEXT,
    url        TEXT,
    points     INTEGER,
    author     TEXT,
    keyword    TEXT,
    created_at_i INTEGER,
    alerted_at INTEGER
  );
  CREATE TABLE IF NOT EXISTS poll_log (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    polled_at    INTEGER,
    posts_found  INTEGER,
    posts_alerted INTEGER
  );
`);

// Prepared statements
const insertPost = db.prepare(`
  INSERT OR IGNORE INTO seen_posts (objectID, title, url, points, author, keyword, created_at_i, alerted_at)
  VALUES (@objectID, @title, @url, @points, @author, @keyword, @created_at_i, @alerted_at)
`);
const hasPost = db.prepare('SELECT 1 FROM seen_posts WHERE objectID = ?');
const insertLog = db.prepare(`
  INSERT INTO poll_log (polled_at, posts_found, posts_alerted)
  VALUES (@polled_at, @posts_found, @posts_alerted)
`);

// Get the timestamp of the last seen post (for incremental polling)
function getLastSeenTimestamp() {
  const row = db.prepare('SELECT MAX(created_at_i) as ts FROM seen_posts').get();
  if (row && row.ts) return row.ts;
  // First run: use FIRST_RUN_DAYS lookback
  return Math.floor(Date.now() / 1000) - FIRST_RUN_DAYS * 86400;
}

// Fetch posts from HN Algolia API
async function fetchPosts(keyword, sinceTimestamp) {
  const tags = INCLUDE_COMMENTS ? 'story,comment' : 'story';
  const url =
    `https://hn.algolia.com/api/v1/search_by_date` +
    `?query=${encodeURIComponent(keyword)}` +
    `&tags=${tags}` +
    `&numericFilters=created_at_i>${sinceTimestamp}` +
    `&hitsPerPage=50`;

  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`HN API returned ${res.status} for keyword "${keyword}"`);
  }
  const data = await res.json();
  return data.hits || [];
}

// Send a Slack alert for a single post
async function sendSlackAlert(post, keyword) {
  const storyUrl = post.url || `https://news.ycombinator.com/item?id=${post.objectID}`;
  const hnUrl = `https://news.ycombinator.com/item?id=${post.objectID}`;

  const payload = {
    blocks: [
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: `*<${storyUrl}|${post.title}>*\n:arrow_up: ${post.points ?? 0} points  :speech_balloon: ${post.num_comments ?? 0} comments  :bust_in_silhouette: ${post.author}`,
        },
      },
      {
        type: 'context',
        elements: [
          {
            type: 'mrkdwn',
            text: `Keyword: \`${keyword}\`  |  <${hnUrl}|HN discussion>`,
          },
        ],
      },
    ],
  };

  const res = await fetch(SLACK_WEBHOOK, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Slack webhook returned ${res.status}: ${body}`);
  }
}

// Sleep helper for rate limiting between keyword queries
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
  console.log(`HN Intel Monitor`);
  console.log(`  Keywords: ${keywords.join(', ')}`);
  console.log(`  Min points: ${MIN_POINTS}`);
  console.log(`  Include comments: ${INCLUDE_COMMENTS}`);
  console.log(`  Mode: ${DRY_RUN ? 'DRY RUN (no alerts)' : 'LIVE'}`);
  console.log('');

  const sinceTimestamp = getLastSeenTimestamp();
  const sinceDate = new Date(sinceTimestamp * 1000).toISOString();
  console.log(`Fetching posts since: ${sinceDate}`);
  console.log('');

  let totalFound = 0;
  let totalAlerted = 0;
  let totalErrors = 0;

  for (let i = 0; i < keywords.length; i++) {
    const keyword = keywords[i];

    // Rate limit: 1 second between keyword queries
    if (i > 0) await sleep(1000);

    let hits;
    try {
      hits = await fetchPosts(keyword, sinceTimestamp);
    } catch (err) {
      console.error(`  ERROR fetching "${keyword}": ${err.message}`);
      totalErrors++;
      continue;
    }

    const filtered = hits.filter(hit => (hit.points ?? 0) >= MIN_POINTS);
    const newPosts = filtered.filter(hit => !hasPost.get(hit.objectID));

    console.log(`"${keyword}": ${hits.length} hits, ${filtered.length} above min points, ${newPosts.length} new`);

    for (const post of newPosts) {
      totalFound++;

      const storyUrl = post.url || `https://news.ycombinator.com/item?id=${post.objectID}`;
      console.log(`  [NEW] ${post.title}`);
      console.log(`        ${storyUrl}`);
      console.log(`        Points: ${post.points ?? 0}  Comments: ${post.num_comments ?? 0}  Author: ${post.author}`);

      if (!DRY_RUN) {
        try {
          await sendSlackAlert(post, keyword);
          totalAlerted++;
          console.log(`        Slack alert sent.`);
        } catch (err) {
          console.error(`        ERROR sending Slack alert: ${err.message}`);
          totalErrors++;
        }
      } else {
        console.log(`        [DRY RUN] Would send Slack alert.`);
        totalAlerted++;
      }

      // Insert into cache regardless of Slack success (avoid double-alerting on retry)
      insertPost.run({
        objectID: post.objectID,
        title: post.title || '',
        url: post.url || '',
        points: post.points ?? 0,
        author: post.author || '',
        keyword,
        created_at_i: post.created_at_i,
        alerted_at: Math.floor(Date.now() / 1000),
      });
    }
  }

  // Log this run
  insertLog.run({
    polled_at: Math.floor(Date.now() / 1000),
    posts_found: totalFound,
    posts_alerted: totalAlerted,
  });

  console.log('');
  console.log('Run complete.');
  console.log(`  Keywords checked: ${keywords.length}`);
  console.log(`  New posts found: ${totalFound}`);
  console.log(`  Alerts sent: ${totalAlerted}${DRY_RUN ? ' (dry run)' : ''}`);
  if (totalErrors > 0) console.log(`  Errors: ${totalErrors}`);
}

main().catch(err => {
  console.error('Unexpected error:', err);
  process.exit(1);
});
