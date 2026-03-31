# Browser Extension Guidelines

This file provides guidance for working with the Repomix browser extension.

## Project Overview

Cross-browser extension (Chrome/Firefox/Edge) that adds Repomix integration to GitHub repository pages. Uses Manifest V3 with content scripts to inject a "Repomix" button directly into GitHub's UI.

## Directory Structure

```
browser/
├── app/                    # Extension source code
│   ├── _locales/          # Internationalization files (11 languages)
│   ├── images/            # Extension icons (16px to 128px)
│   ├── manifest.json      # Extension manifest (Manifest V3)
│   ├── scripts/           # TypeScript source files
│   │   ├── background.ts  # Service worker (background script)
│   │   └── content.ts     # Content script for GitHub integration
│   └── styles/            # CSS styles for injected elements
├── dist/                  # Built extension files (generated)
├── promo/                 # Store promotional materials
└── tests/                 # Test files
```

## Development Commands

```bash
npm run dev chrome     # Development mode for Chrome
npm run build-all      # Build for all browsers
npm run lint          # TypeScript type checking
npm run test          # Run tests
npm run generate-icons # Generate icon set from SVG
```

## Internationalization

### Supported Languages (11 total)
English, Japanese, German, French, Spanish, Portuguese (Brazilian), Indonesian, Vietnamese, Korean, Chinese (Simplified/Traditional), Hindi.

### Adding New Languages
1. Create directory in `app/_locales/[language_code]/`
2. Add `messages.json` with required keys:
   - `appName`, `appDescription`, `buttonText`
3. Add `detailed-description.txt` for store descriptions
4. Test extension loads correctly with new locale
