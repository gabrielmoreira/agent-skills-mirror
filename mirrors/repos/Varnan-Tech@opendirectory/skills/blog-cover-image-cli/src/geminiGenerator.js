import { GoogleGenAI } from '@google/genai';
import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function getExampleImages() {
  const examplesDir = path.join(__dirname, '..', 'examples');
  const imageParts = [];
  try {
    const files = await readdir(examplesDir);
    for (const file of files) {
      if (file.match(/\.(png|jpe?g)$/i)) {
        const filePath = path.join(examplesDir, file);
        const buffer = await readFile(filePath);
        const ext = path.extname(file).toLowerCase();
        const mimeType = ext === '.png' ? 'image/png' : 'image/jpeg';
        imageParts.push({
          inlineData: {
            data: buffer.toString('base64'),
            mimeType
          }
        });
      }
    }
  } catch (err) {
    console.warn('Warning: Could not load example images from ./examples directory.', err.message);
  }
  return imageParts;
}

/**
 * Generates a blog cover image using Gemini 3.1 Flash Image Preview.
 * 
 * @param {string} title - The title text to include in the image.
 * @param {Object|null} logoData - Optional logo data { data: base64String, mimeType: 'image/png' }.
 * @param {string} [apiKey] - Optional API key.
 * @param {string} [criticalFeedback] - Optional feedback from a previous failed attempt.
 * @returns {Promise<{ base64Image: string, textOutput: string }>} - The base64 encoded image data and any text output.
 */
export async function generateCoverImage(title, logoData, apiKey, criticalFeedback) {
  const ai = new GoogleGenAI({ apiKey: apiKey || process.env.GEMINI_API_KEY });
  const exampleImages = await getExampleImages();

  let textPrompt = `
You are an expert technical marketing designer creating a high-converting, minimalist 16:9 blog cover image. Strictly match the visual aesthetic of the provided example images.

CANVAS & TYPOGRAPHY:
- Use a pure solid white background.
- Render the text in a heavy, bold, black sans-serif font.
- Perfectly center-align the text block in the middle of the canvas, leaving generous negative space (padding) around the edges. 
- Break the text naturally into 1 to 3 balanced lines (ABSOLUTE MAXIMUM 3 LINES).

THE EXACT TEXT TO RENDER: 
"${title}"

LOGO INTEGRATION RULES:
Carefully analyze the provided reference logo(s) and integrate them into the text flow using these exact rules:
1. IF the logo is a 'Wordmark' (it contains the brand's name text): Use it inline to completely replace that specific word in the text string.
2. IF the logo is a 'Logomark' (a standalone icon or character): Place it immediately adjacent to the typed brand name in the text.
3. TYPOGRAPHIC REPLACEMENT: If an icon is geometrically similar to a letter in the brand name (like the letter 'O'), creatively substitute the letter with the icon.

AESTHETIC TOUCHES:
Keep the composition radically uncluttered. DO NOT add random, unrelated third-party logos or generic floating UI icons unless explicitly requested in the title. The composition MUST be incredibly clean. If you add a UI element, it must make perfect contextual sense. The primary focus must remain on the bold text and the specific requested logo.
`;

  if (criticalFeedback) {
    textPrompt += `\nCRITICAL FEEDBACK FROM PREVIOUS ATTEMPT: ${criticalFeedback}. You MUST fix these errors in this new generation or you will be penalized.\n`;
  }

  const parts = [];

  // 1. Examples
  if (exampleImages.length > 0) {
    parts.push({ text: 'Here are some reference examples for the desired style and layout:' });
    parts.push(...exampleImages);
  }

  // 2. Instructions + Title
  parts.push({ text: textPrompt });

  // 3. Logo
  if (logoData) {
    parts.push({ text: 'Here is the reference logo to include in the image:' });
    parts.push({
      inlineData: {
        data: logoData.data,
        mimeType: logoData.mimeType
      }
    });
  }

  const contents = [{ role: 'user', parts }];

  const response = await ai.models.generateContent({
    model: 'gemini-3.1-flash-image-preview',
    contents,
    config: {
      responseModalities: ['TEXT', 'IMAGE'],
      imageConfig: {
        aspectRatio: '16:9',
        numberOfImages: 1
      },
      tools: [{ googleSearch: {} }]
    }
  });

  let base64Image = null;
  let textOutput = '';

  for (const part of response.candidates[0].content.parts) {
    if (part.text) {
      textOutput += part.text + '\n';
    } else if (part.inlineData) {
      base64Image = part.inlineData.data;
    }
  }
  
  if (!base64Image) {
    throw new Error('No image was generated in the response. Text returned: ' + textOutput);
  }

  return { base64Image, textOutput };
}
