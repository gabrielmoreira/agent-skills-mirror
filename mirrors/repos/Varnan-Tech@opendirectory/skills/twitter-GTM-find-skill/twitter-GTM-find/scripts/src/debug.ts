// Write a quick script to debug the exact apify item output
import { ApifyClient } from 'apify-client';
import dotenv from 'dotenv';
dotenv.config();

const client = new ApifyClient({
    token: process.env.APIFY_API_TOKEN,
});

async function debug() {
    const input = {
        "query": '("DevRel hiring" OR "GTM hiring" OR "hiring DevRel" OR "hiring GTM" OR "founding GTM" OR "developer advocate hiring") since:2026-03-10 -is:retweet',
        "search_type": "Latest",
        "max_posts": 3
    };

    console.log('Running debug query...');
    const run = await client.actor("ghSpYIW3L1RvT57NT").call(input);
    const { items } = await client.dataset(run.defaultDatasetId).listItems();
    console.log(JSON.stringify(items[0], null, 2));
}

debug().catch(console.error);
