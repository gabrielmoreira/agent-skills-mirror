import { GoogleGenAI } from '@google/genai';

export async function validateImage(base64Image, title, hasLogo, apiKey) {
  const ai = new GoogleGenAI({ apiKey });

  const prompt = `
Analyze this blog cover image and verify if it meets the following CRITICAL requirements:
1. TEXT ACCURACY: Does the image contain the exact text: "${title}"? It must be legible and spelled correctly.
2. LOGO PRESENCE: ${hasLogo ? 'The image MUST contain the requested company logo.' : 'No specific logo was required.'}
3. IMAGE INTEGRITY: Is the image clear and not obviously corrupted or garbled?
4. UNWANTED ELEMENTS: Are there any redundant, misplaced, or entirely irrelevant third-party icons or UI elements that don't fit the strict title context? (If yes, the image is INVALID).

RELAXED RULES (DO NOT FAIL FOR THESE):
- Colored text is ALLOWED and ENCOURAGED if it matches the brand.
- Brand-colored logos are ALLOWED.
- Minimalist, subtle UI elements are allowed ONLY if they perfectly match the specific requested context.
- The background does NOT have to be pure white; subtle gradients or brand colors are acceptable.

Return a JSON object with:
- "isValid": boolean (true only if CRITICAL requirements are met)
- "issues": string (empty if isValid is true, otherwise describe what is wrong)
`;

  const contents = [
    {
      role: 'user',
      parts: [
        { text: prompt },
        {
          inlineData: {
            data: base64Image,
            mimeType: 'image/png',
          },
        },
      ],
    },
  ];

  const response = await ai.models.generateContent({
    model: 'gemini-3.1-pro-preview',
    contents,
    config: {
      responseMimeType: 'application/json',
    },
  });

  const text = response.candidates[0].content.parts[0].text;
  
  try {
    return JSON.parse(text);
  } catch (error) {
    throw new Error(`Failed to parse validation response: ${text}`);
  }
}
