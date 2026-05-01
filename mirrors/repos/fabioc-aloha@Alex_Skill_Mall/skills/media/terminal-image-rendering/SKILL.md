---
type: skill
lifecycle: stable
inheritance: inheritable
name: "terminal-image-rendering"
description: Render images inline in VS Code's integrated terminal using the Kitty graphics protocol
tier: extended
applyTo: '**/*terminal*,**/*image*,**/*rendering*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Terminal Image Rendering


> Images in the terminal — no file explorer needed.

VS Code 1.110+ supports the **Kitty graphics protocol** for rendering images directly in the integrated terminal. Enable with `terminal.integrated.enableImages: true`.

## Quick Start

```bash
# Verify the setting is enabled
# Settings → terminal.integrated.enableImages → true

# Display an image using imgcat (if installed)
imgcat assets/banner.png

# Or use a Node.js script with kitty escape sequences
node -e "const fs=require('fs');const b=fs.readFileSync('assets/banner.png').toString('base64');process.stdout.write('\x1b_Gf=100,a=T;'+b+'\x1b\\\\')"
```

## Supported Methods

| Method | Platform | Notes |
| ------ | -------- | ----- |
| **imgcat** | macOS (iTerm2 protocol) | `brew install imgcat` or use VS Code's built-in support |
| **Kitty escape sequences** | All platforms | Native protocol, works in VS Code 1.110+ |
| **chafa** | Linux/macOS | `brew install chafa` — converts images to terminal graphics |
| **Node.js inline** | All platforms | Read file, base64 encode, write Kitty escape sequence |

## Use Cases for the AI assistant

### Preview Generated Banners

After running banner generation scripts, preview results without leaving the terminal:

```bash
node scripts/generate-readme-banners.js
# Then preview the output:
imgcat assets/banner-main.png
```

### Display Architecture Diagrams

Render diagram visualizations inline during development:

```bash
node scripts/generate-diagram-visualizations.js
imgcat diagram-visualization/cognitive-architecture.png
```

### Visual QA for Brand Assets

Quick-check brand assets without opening files:

```bash
# Check all banner variants
for f in assets/banner-*.png; do echo "=== $f ==="; imgcat "$f"; done
```

### Avatar State Preview

View the AI assistant's cognitive state avatars during development:

```bash
imgcat assets/states/meditation.png
imgcat assets/states/debugging.png
```

## Node.js Helper

For cross-platform terminal image display without external tools:

```javascript
const fs = require('fs');
const path = require('path');

function displayInTerminal(imagePath) {
  const data = fs.readFileSync(imagePath);
  const base64 = data.toString('base64');
  // Kitty graphics protocol: transmit and display
  process.stdout.write(`\x1b_Gf=100,a=T;${base64}\x1b\\`);
  process.stdout.write('\n');
}

// Usage: node display.js assets/banner.png
const file = process.argv[2];
if (file && fs.existsSync(file)) {
  displayInTerminal(file);
} else {
  console.error('Usage: node display.js <image-path>');
}
```

## Settings

| Setting | Value | Purpose |
| ------- | ----- | ------- |
| `terminal.integrated.enableImages` | `true` | Enable Kitty graphics protocol |
| `terminal.integrated.gpuAcceleration` | `on` | Better rendering performance |

## Limitations

- **File size**: Large images (>10MB) may be slow to render
- **Format**: PNG, JPEG, GIF supported; SVG must be converted first
- **Terminal width**: Images scale to terminal width — wide terminals show more detail
- **SSH remotes**: May not work over SSH unless the remote terminal supports Kitty protocol
