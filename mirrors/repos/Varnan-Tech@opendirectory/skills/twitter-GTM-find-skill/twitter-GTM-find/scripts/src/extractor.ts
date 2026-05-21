import { GoogleGenerativeAI, SchemaType } from '@google/generative-ai';
import dotenv from 'dotenv';
dotenv.config();

const apiKey = process.env.GEMINI_API_KEY || '';
const genAI = new GoogleGenerativeAI(apiKey);

export interface JobExtract {
    isJobPost: boolean;
    role: string | null;
    company: string | null;
    tweetUrl: string | null;
    authorProfileUrl: string | null;
}

export async function extractJobDetails(tweetText: string, authorName: string, authorBio: string, tweetUrl: string, authorProfileUrl: string): Promise<JobExtract> {
    if (!apiKey) {
        return {
            isJobPost: tweetText.toLowerCase().includes('hiring') || tweetText.toLowerCase().includes('role'),
            role: "Mocked GTM Role",
            company: "Mocked Company Inc.",
            tweetUrl,
            authorProfileUrl
        };
    }

    const prompt = `
You are an AI assistant designed to extract ONLY TECH AND STARTUP job postings from Twitter data.

Your goal is to parse the tweet and the author's profile bio to identify:
1. Is this a genuine job posting looking to hire someone?
2. What is the specific role being hired for?
3. What is the name or domain of the company hiring?

STRICT FILTERING RULES:
- ONLY mark "isJobPost" as TRUE if the company is a software startup, tech company, developer-first tool, SaaS, or similar.
- REJECT and mark "isJobPost" as FALSE if the role is for traditional industries (e.g. Automotive, Real Estate, Clinics, generic Recruitment Agencies, HR Trainees, Payroll clerks, etc.).
- REJECT if the author is just praising someone who used to be a "Founding GTM" or similar. It MUST be an active request to hire someone.
- Ignore people looking for jobs themselves (e.g., "I am looking for a DevRel role").

If they don't explicitly name the company in the tweet, infer it from their bio (e.g., "Founder @ CompanyX").

Data:
Tweet Text: "${tweetText}"
Author Name: "${authorName}"
Author Bio: "${authorBio}"
`;

    try {
        const model = genAI.getGenerativeModel({ 
            model: "gemini-flash-latest",
            generationConfig: {
                responseMimeType: "application/json",
                responseSchema: {
                    type: SchemaType.OBJECT,
                    properties: {
                        isJobPost: { type: SchemaType.BOOLEAN },
                        role: { type: SchemaType.STRING, nullable: true },
                        company: { type: SchemaType.STRING, nullable: true }
                    },
                    required: ["isJobPost"]
                }
            }
        });

        const result = await model.generateContent(prompt);
        const content = result.response.text();

        if (!content) throw new Error("No response from LLM");

        const parsed: JobExtract = JSON.parse(content);
        parsed.tweetUrl = tweetUrl;
        parsed.authorProfileUrl = authorProfileUrl;
        return parsed;
    } catch (error) {
        console.error("Error extracting job details:", error);
        return { isJobPost: false, role: null, company: null, tweetUrl, authorProfileUrl };
    }
}
