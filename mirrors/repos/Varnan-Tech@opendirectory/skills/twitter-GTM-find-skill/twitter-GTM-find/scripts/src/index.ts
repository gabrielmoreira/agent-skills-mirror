import { scrapeTwitterJobs } from './scraper';
import { extractJobDetails, JobExtract } from './extractor';
import { evaluateICP, IcpResult } from './icp-filter';
import fs from 'fs';

async function main() {
    const maxPosts = parseInt(process.env.MAX_POSTS || '20', 10);
    
    const rawTweets = await scrapeTwitterJobs(maxPosts);
    const radarData: JobExtract[] = [];

    console.log(`\nProcessing ${rawTweets.length} tweets to extract job details...`);
    const seenJobs = new Set<string>();
    const seenTweetIds = new Set<string>();

    const extractedResults = await Promise.all(rawTweets.map(async (item: any) => {
        const itemAny = item;
        const tweetId = itemAny.tweet_id || itemAny.id_str || itemAny.id || "";
        
        const tweetText = itemAny.full_text || itemAny.text || String(itemAny);
        let authorName = "Unknown";
        let authorBio = "Unknown";
        
        if (itemAny.user_info) {
            authorName = itemAny.user_info.name || itemAny.user_info.screen_name || "Unknown";
            authorBio = itemAny.user_info.description || "Unknown";
        } else if (itemAny.author) {
            authorName = itemAny.author.name || itemAny.author.userName || "Unknown";
            authorBio = itemAny.author.description || "Unknown";
        } else if (itemAny.user) {
            authorName = itemAny.user.name || itemAny.user.screen_name || "Unknown";
            authorBio = itemAny.user.description || "Unknown";
        }

        const authorHandle = itemAny.screen_name || itemAny.user_info?.screen_name || itemAny.author?.userName || itemAny.user?.screen_name || "";
        const tweetUrl = tweetId && authorHandle ? `https://twitter.com/${authorHandle}/status/${tweetId}` : itemAny.url || "";
        const authorProfileUrl = authorHandle ? `https://twitter.com/${authorHandle}` : "";

        return {
            tweetId,
            extracted: await extractJobDetails(tweetText, authorName, String(authorBio), tweetUrl, authorProfileUrl)
        };
    }));

    for (const result of extractedResults) {
        if (result.tweetId && seenTweetIds.has(result.tweetId)) continue;
        if (result.tweetId) seenTweetIds.add(result.tweetId);

        const { extracted } = result;
        if (extracted.isJobPost && extracted.company && extracted.role) {
            const dedupKey = extracted.company.toLowerCase().replace(/[^a-z0-9]/g, '');
            if (seenJobs.has(dedupKey)) {
                console.log(`⚠️ Skipped Duplicate Company: [Role]: ${extracted.role} | [Company]: ${extracted.company}`);
                continue;
            }
            seenJobs.add(dedupKey);

            radarData.push(extracted);
            console.log(`✅ Added to Radar: [Role]: ${extracted.role} | [Company]: ${extracted.company}`);
        } else {
            console.log(`❌ Skipped: Not a valid job post or missing info.`);
        }
    }

    fs.writeFileSync('radar-jobs.json', JSON.stringify(radarData, null, 2));
    console.log(`\n🎉 Step 1 Complete: Found ${radarData.length} valid jobs.`);
    
    console.log(`\n🔍 Step 2: Evaluating ${radarData.length} companies against OpenClaw ICP...`);
    
    const icpData: IcpResult[] = [];
    
    const BATCH_SIZE = 5;
    for (let i = 0; i < radarData.length; i += BATCH_SIZE) {
        const batch = radarData.slice(i, i + BATCH_SIZE);
        console.log(`Researching batch ${i/BATCH_SIZE + 1} (${batch.length} companies)...`);
        
        const evaluations = await Promise.all(batch.map(job => evaluateICP(job)));
        
        for (const evaluation of evaluations) {
            if (evaluation.isICP) {
                console.log(`   🟢 PASSED ICP: ${evaluation.company} - ${evaluation.icpReasoning}`);
                icpData.push(evaluation);
            } else {
                console.log(`   🔴 FAILED ICP: ${evaluation.company} - ${evaluation.icpReasoning}`);
            }
        }
        
        fs.writeFileSync('openclaw-icp-jobs.json', JSON.stringify(icpData, null, 2));
    }

    console.log(`\n🎉 Pipeline Complete! Exported ${icpData.length} highly-targeted ICP companies to openclaw-icp-jobs.json.`);
}

main().catch(console.error);
