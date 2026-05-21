import { GoogleGenerativeAI, SchemaType } from '@google/generative-ai';
import { JobExtract } from './extractor';
import dotenv from 'dotenv';
dotenv.config();

const apiKey = process.env.GEMINI_API_KEY || '';
const genAI = new GoogleGenerativeAI(apiKey);

export interface IcpResult extends JobExtract {
    isICP: boolean;
    icpReasoning: string;
    companyUrl: string | null;
    estimatedFunding: string | null;
}

export async function evaluateICP(job: JobExtract): Promise<IcpResult> {
    if (!apiKey) {
        return { ...job, isICP: false, icpReasoning: "No API Key", companyUrl: null, estimatedFunding: null };
    }

    const model = genAI.getGenerativeModel({
        model: "gemini-flash-latest",
        tools: [
            { googleSearch: {} } as any
        ],
        generationConfig: {
            responseMimeType: "application/json",
            responseSchema: {
                type: SchemaType.OBJECT,
                properties: {
                    isICP: { type: SchemaType.BOOLEAN },
                    icpReasoning: { type: SchemaType.STRING },
                    companyUrl: { type: SchemaType.STRING, nullable: true },
                    estimatedFunding: { type: SchemaType.STRING, nullable: true }
                },
                required: ["isICP", "icpReasoning"]
            }
        }
    });

    const prompt = `
You are an M&A/Sales researcher validating a company against a strict ICP (Ideal Customer Profile) checklist.
Your goal is to use Google Search to research the company and determine if they are an exact match for our ICP.

COMPANY TO RESEARCH: "${job.company}"
(Role hiring for: "${job.role}")

### ICP CHECKLIST:
1. Developer-First Product
- WHAT QUALIFIES: API platforms, infrastructure tools, SDKs, dev utilities, AI agents/automation for technical workflows, DevOps, CI/CD, monitoring, analytics, Code editors, Data infrastructure, LLM deployment platforms.
- AUTO-SKIP (NOT ICP): Consumer apps, B2C SaaS, HR tools, pure Fintech/healthcare, traditional physical industries, recruiting agencies.

2. Funding Evidence
- MINIMUM REQUIREMENT: $100K+ raised (verifiable via Crunchbase, YC, press, founder posts).
- PREFERRED: $500K-$5M seed/Series A in last 18 months. YC, a16z, Sequoia backed.
- SKIP IF (NOT ICP): Pure bootstrap, absolutely no funding evidence found.

### INSTRUCTIONS:
1. Use Google Search to find the official website for "${job.company}".
2. Use Google Search to find funding data (search "${job.company} funding Crunchbase Y Combinator").
3. Evaluate them strictly against the 2 checklist items above.
4. If they are a dev-first/infrastructure/AI tool AND have funding, "isICP" must be TRUE.
5. If they fail EITHER criteria (e.g. consumer app, OR zero funding found), "isICP" must be FALSE.
6. Provide a concise 1-2 sentence "icpReasoning" explaining exactly what the company does and how much funding you found.

Output valid JSON exactly matching the schema.
`;

    try {
        const result = await model.generateContent(prompt);
        const content = result.response.text();
        
        if (!content) throw new Error("No response from LLM");
        
        const parsed = JSON.parse(content);
        return {
            ...job,
            isICP: parsed.isICP,
            icpReasoning: parsed.icpReasoning,
            companyUrl: parsed.companyUrl || null,
            estimatedFunding: parsed.estimatedFunding || null
        };
    } catch (error) {
        console.error(`Error evaluating ICP for ${job.company}:`, error);
        return { ...job, isICP: false, icpReasoning: "Error during evaluation", companyUrl: null, estimatedFunding: null };
    }
}
