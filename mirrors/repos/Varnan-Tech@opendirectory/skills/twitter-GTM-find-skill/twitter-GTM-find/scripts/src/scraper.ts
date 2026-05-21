import { ApifyClient } from 'apify-client';
import dotenv from 'dotenv';
dotenv.config();

const client = new ApifyClient({
    token: process.env.APIFY_API_TOKEN,
});

export async function scrapeTwitterJobs(maxPostsPerQuery: number = 20) {
    console.log('Starting Twitter Job Scraper (Multi-Query Mode)...');

    const lastWeek = new Date();
    lastWeek.setDate(lastWeek.getDate() - 7);
    const sinceDate = lastWeek.toISOString().split('T')[0];

    const queries = [
        `("hiring" OR "looking for" OR "open role") ("DevRel" OR "Developer Advocate" OR "DevRel Intern") since:${sinceDate} -is:retweet`,
        `("hiring" OR "looking for" OR "open role") ("GTM" OR "go to market" OR "Founding GTM" OR "GTM Lead") since:${sinceDate} -is:retweet`,
        `("hiring" OR "looking for" OR "open role") ("Growth Lead" OR "Growth Hacker" OR "Head of Growth") since:${sinceDate} -is:retweet`,
        `("hiring" OR "looking for" OR "open role") ("Developer Marketing" OR "Developer Relations" OR "Community Lead") since:${sinceDate} -is:retweet`,
        `("hiring DevRel" OR "GTM Engineer" OR "hiring GTM" OR "hiring founding GTM" OR "developer advocate hiring") since:${sinceDate} -is:retweet`
    ];

    let allItems: any[] = [];

    for (const [index, query] of queries.entries()) {
        console.log(`\n--- Running Query ${index + 1}/5 ---`);
        console.log(`Executing query: ${query}`);
        const input = {
            "query": query,
            "search_type": "Latest",
            "max_posts": maxPostsPerQuery
        };
        const run = await client.actor("ghSpYIW3L1RvT57NT").call(input);
        const { items } = await client.dataset(run.defaultDatasetId).listItems();
        console.log(`Found ${items.length} tweets for this query.`);
        allItems = allItems.concat(items);
    }

    return allItems;
}
