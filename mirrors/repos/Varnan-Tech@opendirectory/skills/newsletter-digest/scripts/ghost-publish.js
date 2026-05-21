#!/usr/bin/env node
/**
 * ghost-publish.js
 * Publishes the newsletter digest to Ghost CMS via Admin API.
 *
 * Usage:
 *   node ghost-publish.js --title "Weekly Digest: Apr 7-14" --status draft
 *   node ghost-publish.js --title "Weekly Digest: Apr 7-14" --status published
 *
 * Reads digest content from: /tmp/newsletter-digest-output.json
 * Required env vars: GHOST_URL, GHOST_ADMIN_KEY
 *
 * GHOST_ADMIN_KEY format: "key_id:secret" (from Ghost Admin > Settings > Integrations)
 */

import jwt from 'jsonwebtoken';
import { readFileSync } from 'fs';

const OUTPUT_PATH = '/tmp/newsletter-digest-output.json';

function generateToken(adminKey) {
  const [id, secret] = adminKey.split(':');
  if (!id || !secret) {
    throw new Error('GHOST_ADMIN_KEY must be in format "key_id:secret"');
  }
  // Ghost requires the secret as binary (hex-decoded), signed with HS256
  return jwt.sign({}, Buffer.from(secret, 'hex'), {
    keyid: id,
    algorithm: 'HS256',
    expiresIn: '5m',
    audience: '/admin/',
  });
}

async function main() {
  const args = process.argv.slice(2);
  const titleArg = args.find(a => a.startsWith('--title='));
  const statusArg = args.find(a => a.startsWith('--status='));

  const title = titleArg ? titleArg.split('=').slice(1).join('=') : null;
  const status = statusArg ? statusArg.split('=')[1] : 'draft';

  if (!title) {
    console.error('ERROR: --title is required');
    process.exit(1);
  }

  if (!['draft', 'published'].includes(status)) {
    console.error('ERROR: --status must be "draft" or "published"');
    process.exit(1);
  }

  const ghostUrl = process.env.GHOST_URL;
  const adminKey = process.env.GHOST_ADMIN_KEY;

  if (!ghostUrl) {
    console.error('ERROR: GHOST_URL is not set');
    process.exit(1);
  }
  if (!adminKey) {
    console.error('ERROR: GHOST_ADMIN_KEY is not set');
    process.exit(1);
  }

  // Read digest content
  let digestOutput;
  try {
    digestOutput = JSON.parse(readFileSync(OUTPUT_PATH, 'utf8'));
  } catch (err) {
    console.error(`ERROR: Could not read digest output at ${OUTPUT_PATH}`);
    console.error('The agent must write the digest to this file before running ghost-publish.js');
    process.exit(1);
  }

  const html = digestOutput.html;
  if (!html) {
    console.error('ERROR: digest output JSON does not contain an "html" field');
    process.exit(1);
  }

  // Generate JWT token
  let token;
  try {
    token = generateToken(adminKey);
  } catch (err) {
    console.error(`ERROR: Failed to generate Ghost JWT: ${err.message}`);
    process.exit(1);
  }

  // Build Ghost API URL (strip trailing slash)
  const baseUrl = ghostUrl.replace(/\/$/, '');
  const apiUrl = `${baseUrl}/ghost/api/admin/posts/?source=html`;

  const payload = {
    posts: [
      {
        title,
        html,
        status,
      },
    ],
  };

  // POST to Ghost Admin API
  let response;
  try {
    const res = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Ghost ${token}`,
      },
      body: JSON.stringify(payload),
    });

    response = await res.json();

    if (!res.ok) {
      console.error('Ghost API error:', JSON.stringify(response, null, 2));
      process.exit(1);
    }
  } catch (err) {
    console.error(`ERROR: Network request to Ghost failed: ${err.message}`);
    process.exit(1);
  }

  const post = response.posts?.[0];
  if (!post) {
    console.error('ERROR: Ghost did not return a post object');
    console.error(JSON.stringify(response, null, 2));
    process.exit(1);
  }

  console.log(`\nPost created successfully.`);
  console.log(`  Status:   ${post.status}`);
  console.log(`  Title:    ${post.title}`);
  console.log(`  Slug:     ${post.slug}`);
  console.log(`  Admin URL: ${baseUrl}/ghost/#/editor/post/${post.id}`);
  if (post.status === 'published') {
    console.log(`  Public URL: ${post.url}`);
  }
}

main().catch(err => {
  console.error('Unexpected error:', err);
  process.exit(1);
});
