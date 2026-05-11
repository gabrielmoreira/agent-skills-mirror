/**
 * Preline Theme Generator
 *
 * Core library for generating a complete theme CSS file from config.
 *
 * Use `run-theme-generator.js` for CLI execution. Import this file when you
 * need the generator programmatically:
 *
 *   const { generateTheme } = require('./generate-theme.js');
 *   const css = generateTheme(config);
 */

// ============================================
// COLOR CONVERSION UTILITIES
// ============================================

/**
 * Convert OKLCH to sRGB
 * Based on CSS Color Level 4 spec
 */
function oklchToRgb(l, c, h) {
  // Convert to OKLab first
  const hRad = (h * Math.PI) / 180;
  const a = c * Math.cos(hRad);
  const b = c * Math.sin(hRad);

  // OKLab to linear sRGB via LMS
  const L = l + 0.3963377774 * a + 0.2158037573 * b;
  const M = l - 0.1055613458 * a - 0.0638541728 * b;
  const S = l - 0.0894841775 * a - 1.2914855480 * b;

  const l_ = L * L * L;
  const m_ = M * M * M;
  const s_ = S * S * S;

  let rLinear = 4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_;
  let gLinear = -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_;
  let bLinear = -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_;

  // Linear to sRGB gamma
  const gammaCorrect = (x) => {
    if (x >= 0.0031308) {
      return 1.055 * Math.pow(x, 1 / 2.4) - 0.055;
    }
    return 12.92 * x;
  };

  let r = Math.round(Math.max(0, Math.min(1, gammaCorrect(rLinear))) * 255);
  let g = Math.round(Math.max(0, Math.min(1, gammaCorrect(gLinear))) * 255);
  let bVal = Math.round(Math.max(0, Math.min(1, gammaCorrect(bLinear))) * 255);

  return { r, g, b: bVal };
}

/**
 * Convert OKLCH to hex color
 * @param {number} l - Lightness (0-100 as percentage, will be converted to 0-1)
 * @param {number} c - Chroma (0-0.4 typically)
 * @param {number} h - Hue (0-360)
 * @returns {string} Hex color string (e.g., "#2563eb")
 */
function oklchToHex(l, c, h) {
  // Convert percentage to 0-1 if needed
  const lightness = l > 1 ? l / 100 : l;

  const { r, g, b } = oklchToRgb(lightness, c, h);

  const toHex = (n) => {
    const hex = Math.max(0, Math.min(255, n)).toString(16);
    return hex.length === 1 ? '0' + hex : hex;
  };

  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}

/**
 * Convert sRGB channel value to linear space
 * @param {number} channel - 0-255
 * @returns {number}
 */
function srgbChannelToLinear(channel) {
  const normalized = channel / 255;

  if (normalized <= 0.04045) {
    return normalized / 12.92;
  }

  return Math.pow((normalized + 0.055) / 1.055, 2.4);
}

/**
 * Relative luminance per WCAG
 * @param {{r: number, g: number, b: number}} rgb
 * @returns {number}
 */
function getRelativeLuminance(rgb) {
  const r = srgbChannelToLinear(rgb.r);
  const g = srgbChannelToLinear(rgb.g);
  const b = srgbChannelToLinear(rgb.b);

  return (0.2126 * r) + (0.7152 * g) + (0.0722 * b);
}

/**
 * WCAG contrast ratio between two colors
 * @param {{r: number, g: number, b: number}} colorA
 * @param {{r: number, g: number, b: number}} colorB
 * @returns {number}
 */
function getContrastRatio(colorA, colorB) {
  const luminanceA = getRelativeLuminance(colorA);
  const luminanceB = getRelativeLuminance(colorB);
  const lighter = Math.max(luminanceA, luminanceB);
  const darker = Math.min(luminanceA, luminanceB);

  return (lighter + 0.05) / (darker + 0.05);
}

/**
 * Convert hex color to hue (0-360)
 * @param {string} hex - Hex color (e.g., "#2F6BFF" or "2F6BFF")
 * @returns {number} Hue in degrees (0-360)
 */
function hexToHue(hex) {
  // Remove # if present
  hex = hex.replace(/^#/, '');

  const r = parseInt(hex.substring(0, 2), 16) / 255;
  const g = parseInt(hex.substring(2, 4), 16) / 255;
  const b = parseInt(hex.substring(4, 6), 16) / 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const delta = max - min;

  let h = 0;
  if (delta !== 0) {
    if (max === r) {
      h = ((g - b) / delta) % 6;
    } else if (max === g) {
      h = (b - r) / delta + 2;
    } else {
      h = (r - g) / delta + 4;
    }
    h = Math.round(h * 60);
    if (h < 0) h += 360;
  }

  return h;
}

// ============================================
// VALIDATION
// ============================================

/**
 * Validate config and return error messages if invalid
 * @param {Object} config
 * @returns {string[]} Array of error messages (empty if valid)
 */
function validateConfig(config) {
  const errors = [];

  // Required: name
  if (!config.name || typeof config.name !== 'string') {
    errors.push('Missing required field: "name" (string, kebab-case theme name)');
  } else if (!/^[a-z][a-z0-9-]*$/.test(config.name)) {
    errors.push(`Invalid name "${config.name}": must be kebab-case (lowercase letters, numbers, hyphens, starting with letter)`);
  }

  // Required: hue OR primaryColor
  const hasHue = typeof config.hue === 'number';
  const hasPrimaryColor = typeof config.primaryColor === 'string';

  if (!hasHue && !hasPrimaryColor) {
    errors.push('Missing required field: "hue" (number 0-360) or "primaryColor" (hex string like "#2F6BFF")');
  }

  if (hasHue && (config.hue < 0 || config.hue > 360)) {
    errors.push(`Invalid hue ${config.hue}: must be between 0 and 360`);
  }

  if (hasPrimaryColor && !/^#?[0-9A-Fa-f]{6}$/.test(config.primaryColor)) {
    errors.push(`Invalid primaryColor "${config.primaryColor}": must be 6-digit hex (e.g., "#2F6BFF")`);
  }

  // Optional: style
  if (config.style && !['vibrant', 'soft'].includes(config.style)) {
    errors.push(`Invalid style "${config.style}": must be "vibrant" or "soft"`);
  }

  // Optional: tailwindGray
  const validGrays = ['neutral', 'stone', 'zinc', 'slate', 'gray'];
  if (config.tailwindGray && !validGrays.includes(config.tailwindGray)) {
    errors.push(`Invalid tailwindGray "${config.tailwindGray}": must be one of ${validGrays.join(', ')}`);
  }

  return errors;
}

// ============================================
// PALETTE GENERATION
// ============================================

/**
 * Calculate lightness for a shade using a formula-based approach
 * @param {number} shade - Shade number (50-950)
 * @returns {number} Lightness percentage
 */
function calculateLightness(shade) {
  // Use a polynomial curve that matches Tailwind's visual rhythm
  // 50 = ~97%, 500 = ~60%, 950 = ~20%
  const shadeNormalized = shade / 1000;
  const lightness = 97 - (shadeNormalized * 85) + (Math.pow(shadeNormalized, 2) * 10);
  return Math.round(Math.max(15, Math.min(98, lightness)) * 10) / 10;
}

/**
 * Generate brand color palette (vibrant or soft)
 */
function generateBrandPalette(name, hue, style = 'vibrant') {
  const shades = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950];

  // Chroma values - vibrant vs soft
  const chromaVibrant = {
    50: 0.08, 100: 0.10, 200: 0.12, 300: 0.14, 400: 0.16,
    500: 0.14, 600: 0.12, 700: 0.10, 800: 0.08, 900: 0.06, 950: 0.05
  };

  const chromaSoft = {
    50: 0.012, 100: 0.020, 200: 0.035, 300: 0.055, 400: 0.075,
    500: 0.085, 600: 0.080, 700: 0.070, 800: 0.055, 900: 0.040, 950: 0.030
  };

  const chroma = style === 'soft' ? chromaSoft : chromaVibrant;

  return shades.map(shade => {
    const l = calculateLightness(shade);
    const c = chroma[shade];
    return `  --color-${name}-${shade}: oklch(${l}% ${c} ${hue});`;
  }).join('\n');
}

/**
 * Generate gray palette with bell curve chroma
 * Low at extremes (for clean light/dark backgrounds), peak at midtones
 */
function generateGrayPalette(name, hue) {
  const shades = [
    { shade: 50, l: 98, c: 0.002 },
    { shade: 100, l: 95.5, c: 0.004 },
    { shade: 200, l: 89.7, c: 0.008 },
    { shade: 300, l: 82.7, c: 0.012 },
    { shade: 400, l: 73, c: 0.018 },
    { shade: 500, l: 62.5, c: 0.020 },  // Peak chroma
    { shade: 600, l: 52.8, c: 0.016 },
    { shade: 700, l: 41.4, c: 0.012 },
    { shade: 800, l: 26.9, c: 0.006 },  // Darker - matches Tailwind neutral-800
    { shade: 900, l: 20.5, c: 0.004 },  // Darker - matches Tailwind neutral-900
    { shade: 950, l: 14.1, c: 0.002 },  // Darker - matches Tailwind neutral-950
  ];

  return shades.map(({ shade, l, c }) =>
    `  --color-${name}-gray-${shade}: oklch(${l}% ${c} ${hue});`
  ).join('\n');
}

function getBrandShadeOklch(style, hue, shade) {
  const chromaByStyle = {
    vibrant: {
      50: 0.08, 100: 0.10, 200: 0.12, 300: 0.14, 400: 0.16,
      500: 0.14, 600: 0.12, 700: 0.10, 800: 0.08, 900: 0.06, 950: 0.05
    },
    soft: {
      50: 0.012, 100: 0.020, 200: 0.035, 300: 0.055, 400: 0.075,
      500: 0.085, 600: 0.080, 700: 0.070, 800: 0.055, 900: 0.040, 950: 0.030
    }
  };

  return {
    l: calculateLightness(shade),
    c: chromaByStyle[style][shade],
    h: hue,
  };
}

function getThemeGrayShadeOklch(hue, shade) {
  const grayScale = {
    50: { l: 98, c: 0.002 },
    100: { l: 95.5, c: 0.004 },
    200: { l: 89.7, c: 0.008 },
    300: { l: 82.7, c: 0.012 },
    400: { l: 73, c: 0.018 },
    500: { l: 62.5, c: 0.020 },
    600: { l: 52.8, c: 0.016 },
    700: { l: 41.4, c: 0.012 },
    800: { l: 26.9, c: 0.006 },
    900: { l: 20.5, c: 0.004 },
    950: { l: 14.1, c: 0.002 },
  };

  return {
    ...grayScale[shade],
    h: hue,
  };
}

function oklchColorToRgb(color) {
  return oklchToRgb(color.l / 100, color.c, color.h);
}

function getWorstContrast(candidate, backgrounds) {
  return Math.min(...backgrounds.map((background) => getContrastRatio(candidate, background)));
}

function pickContrastingForegroundValue(candidates, backgrounds) {
  const evaluated = candidates.map((candidate) => ({
    value: candidate.value,
    worstContrast: getWorstContrast(candidate.rgb, backgrounds),
  }));

  evaluated.sort((left, right) => right.worstContrast - left.worstContrast);

  return evaluated[0].value;
}

// ============================================
// CHART & MAP TOKEN GENERATION
// ============================================

function buildChartSeriesTokens(series) {
  return series.map((item, index) => {
    const num = index + 1;
    return `
  --chart-${num}: ${item.base};
  --chart-colors-chart-${num}: ${item.base};
  --chart-colors-chart-${num}-inverse: ${item.inverse};
  --chart-colors-chart-${num}-hex: ${item.base};
  --chart-colors-chart-${num}-hex-inverse: ${item.inverse};`;
  }).join('');
}

function generateChartTokensLight(name) {
  const g = `--color-${name}-gray`;
  const series = [
    { base: 'var(--color-primary-50)', inverse: 'var(--color-primary-100)' },
    { base: 'var(--color-primary-200)', inverse: 'var(--color-primary-300)' },
    { base: 'var(--color-primary-400)', inverse: 'var(--color-primary-500)' },
    { base: 'var(--color-primary-700)', inverse: 'var(--color-primary-500)' },
    { base: 'var(--color-primary-900)', inverse: 'var(--color-primary-700)' },
    { base: 'var(--color-sky-600)', inverse: 'var(--color-sky-400)' },
    { base: 'var(--color-emerald-600)', inverse: 'var(--color-emerald-400)' },
    { base: 'var(--color-violet-600)', inverse: 'var(--color-violet-400)' },
    { base: 'var(--color-rose-500)', inverse: 'var(--color-rose-300)' },
    { base: `var(${g}-300)`, inverse: `var(${g}-500)` },
  ];

  return `
  /* ============================================ */
  /* CHARTS (Apexcharts)                          */
  /* ============================================ */
  
  --chart-colors-background: var(--background-plain);
  --chart-colors-background-inverse: var(--inverse);
  --chart-colors-chart-inverse: var(--background-1);
  --chart-colors-foreground: var(--foreground);
  --chart-colors-foreground-inverse: var(--foreground-inverse);
  
  --chart-primary: var(--color-primary-600);
  --chart-colors-primary: var(--color-primary-600);
  --chart-colors-primary-inverse: var(--color-primary-300);
  --chart-colors-primary-hex: var(--color-primary-600);
  --chart-colors-primary-hex-inverse: var(--color-primary-300);` +
    buildChartSeriesTokens(series) +
    `
  
  --chart-colors-candlestick-upward: var(--color-green-500);
  --chart-colors-candlestick-upward-inverse: var(--color-green-400);
  --chart-colors-candlestick-downward: var(--color-red-500);
  --chart-colors-candlestick-downward-inverse: var(--color-red-400);
  
  --chart-colors-labels: var(${g}-600);
  --chart-colors-labels-inverse: var(${g}-400);
  --chart-colors-xaxis-labels: var(${g}-500);
  --chart-colors-xaxis-labels-inverse: var(${g}-400);
  --chart-colors-yaxis-labels: var(${g}-500);
  --chart-colors-yaxis-labels-inverse: var(${g}-400);
  
  --chart-colors-grid-border: var(--border);
  --chart-colors-grid-border-inverse: var(${g}-700);
  --chart-colors-bar-ranges: var(--surface-1);
  --chart-colors-bar-ranges-inverse: var(${g}-700);`;
}

function generateChartTokensDark(name, grayVar, darkModePrimaryProfile) {
  const primaryShade = darkModePrimaryProfile.primaryShade;
  const interactionShade = darkModePrimaryProfile.interactionShade;
  const companionShade = primaryShade >= 500 ? 300 : 200;
  const series = [
    { base: 'var(--color-primary-200)', inverse: 'var(--color-primary-300)' },
    { base: 'var(--color-primary-300)', inverse: 'var(--color-primary-400)' },
    { base: 'var(--color-primary-400)', inverse: `var(--color-primary-${primaryShade})` },
    { base: `var(--color-primary-${primaryShade})`, inverse: `var(--color-primary-${interactionShade})` },
    { base: `var(--color-primary-${companionShade})`, inverse: `var(--color-primary-${primaryShade})` },
    { base: 'var(--color-sky-400)', inverse: 'var(--color-sky-300)' },
    { base: 'var(--color-emerald-400)', inverse: 'var(--color-emerald-300)' },
    { base: 'var(--color-violet-400)', inverse: 'var(--color-violet-300)' },
    { base: 'var(--color-rose-400)', inverse: 'var(--color-rose-300)' },
    { base: `var(${grayVar}-300)`, inverse: `var(${grayVar}-500)` },
  ];

  return `
  /* CHARTS - dark mode adjustments */
  --chart-colors-background: var(--background);
  --chart-colors-background-inverse: var(${grayVar}-100);
  --chart-colors-chart-inverse: var(--background-1);
  --chart-colors-foreground: var(${grayVar}-300);
  --chart-colors-foreground-inverse: var(--color-white);

  --chart-primary: var(--color-primary-${primaryShade});
  --chart-colors-primary: var(--color-primary-${primaryShade});
  --chart-colors-primary-inverse: var(--color-primary-${companionShade});
  --chart-colors-primary-hex: var(--color-primary-${primaryShade});
  --chart-colors-primary-hex-inverse: var(--color-primary-${companionShade});` +
    buildChartSeriesTokens(series) +
    `

  --chart-colors-labels: var(${grayVar}-400);
  --chart-colors-xaxis-labels: var(${grayVar}-400);
  --chart-colors-yaxis-labels: var(${grayVar}-400);
  --chart-colors-grid-border: var(--border);
  --chart-colors-bar-ranges: var(--surface);`;
}

function generateMapTokens(name) {
  const g = `--color-${name}-gray`;

  return `
  /* ============================================ */
  /* MAPS (jsvectormap)                           */
  /* ============================================ */
  
  --map-colors-primary: var(--color-primary-500);
  --map-colors-primary-inverse: var(--color-primary-300);
  --map-colors-default: var(--surface-1);
  --map-colors-default-inverse: var(${g}-700);
  --map-colors-highlight: var(--color-primary-300);
  --map-colors-highlight-inverse: var(--color-primary-500);
  --map-colors-border: var(--border-line-3);
  --map-colors-border-inverse: var(${g}-600);`;
}

// ============================================
// HELPER FUNCTIONS
// ============================================

function getPrimaryForegroundForLightMode(name, hue, style) {
  const backgrounds = [600, 700]
    .map((shade) => getBrandShadeOklch(style, hue, shade))
    .map(oklchColorToRgb);
  const darkText = oklchColorToRgb(getThemeGrayShadeOklch(hue, 900));

  return pickContrastingForegroundValue([
    { value: 'var(--color-white)', rgb: { r: 255, g: 255, b: 255 } },
    { value: `var(--color-${name}-gray-900)`, rgb: darkText },
  ], backgrounds);
}

function getDarkModePrimaryProfile(name, hue, style, grayVar) {
  const white = { r: 255, g: 255, b: 255 };
  const darkText = oklchColorToRgb(getThemeGrayShadeOklch(hue, 900));
  const minimumUiContrast = 3;
  const profiles = [
    {
      key: 'white',
      foregroundValue: 'var(--color-white)',
      switchValue: 'var(--color-white)',
      primaryShade: 500,
      interactionShade: 600,
      checkedShade: 500,
      backgrounds: [500, 600].map((shade) => oklchColorToRgb(getBrandShadeOklch(style, hue, shade))),
      foregroundRgb: white,
    },
    {
      key: 'dark',
      foregroundValue: `var(${grayVar}-900)`,
      switchValue: `var(${grayVar}-800)`,
      primaryShade: 400,
      interactionShade: 500,
      checkedShade: 400,
      backgrounds: [400, 500].map((shade) => oklchColorToRgb(getBrandShadeOklch(style, hue, shade))),
      foregroundRgb: darkText,
    },
  ].map((profile) => ({
    ...profile,
    worstContrast: getWorstContrast(profile.foregroundRgb, profile.backgrounds),
  }));

  const preferredWhiteProfile = profiles.find((profile) =>
    profile.key === 'white' && profile.worstContrast >= minimumUiContrast
  );

  if (preferredWhiteProfile) {
    return preferredWhiteProfile;
  }

  const acceptableProfiles = profiles.filter((profile) => profile.worstContrast >= minimumUiContrast);
  if (acceptableProfiles.length > 0) {
    acceptableProfiles.sort((left, right) => right.worstContrast - left.worstContrast);
    return acceptableProfiles[0];
  }

  profiles.sort((left, right) => right.worstContrast - left.worstContrast);
  return profiles[0];
}

// ============================================
// THEME SECTION GENERATORS
// ============================================

function generateLightModeTokens(name, hue, style) {
  const g = `--color-${name}-gray`;
  const primaryForeground = getPrimaryForegroundForLightMode(name, hue, style);

  return `
  /* ============================================ */
  /* GLOBAL SURFACES + TEXT                       */
  /* ============================================ */
  
  --background: var(--color-white);
  --background-1: var(${g}-50);
  --background-2: var(${g}-100);
  --background-plain: var(--color-white);
  --foreground: var(${g}-800);
  --foreground-inverse: var(--color-white);
  
  --inverse: var(--color-primary-950);
  
  /* ============================================ */
  /* BORDERS (Full Scale)                         */
  /* ============================================ */
  
  --border: var(${g}-200);
  --border-line-inverse: var(--color-white);
  --border-line-1: var(${g}-100);
  --border-line-2: var(${g}-200);
  --border-line-3: var(${g}-300);
  --border-line-4: var(${g}-400);
  --border-line-5: var(${g}-500);
  --border-line-6: var(${g}-600);
  --border-line-7: var(${g}-700);
  --border-line-8: var(${g}-800);
  
  /* ============================================ */
  /* PRIMARY RAMP (Full 11-shade scale)           */
  /* ============================================ */
  
  --primary-50: var(--color-${name}-50);
  --primary-100: var(--color-${name}-100);
  --primary-200: var(--color-${name}-200);
  --primary-300: var(--color-${name}-300);
  --primary-400: var(--color-${name}-400);
  --primary-500: var(--color-${name}-500);
  --primary-600: var(--color-${name}-600);
  --primary-700: var(--color-${name}-700);
  --primary-800: var(--color-${name}-800);
  --primary-900: var(--color-${name}-900);
  --primary-950: var(--color-${name}-950);
  
  /* PRIMARY STATES */
  --primary: var(--color-primary-600);
  --primary-line: transparent;
  --primary-foreground: ${primaryForeground};
  --primary-hover: var(--color-primary-700);
  --primary-focus: var(--color-primary-700);
  --primary-active: var(--color-primary-700);
  --primary-checked: var(--color-primary-600);
  
  /* ============================================ */
  /* SECONDARY                                    */
  /* ============================================ */
  
  --secondary: var(${g}-900);
  --secondary-line: transparent;
  --secondary-foreground: var(--color-white);
  --secondary-hover: var(${g}-800);
  --secondary-focus: var(${g}-800);
  --secondary-active: var(${g}-800);
  
  /* ============================================ */
  /* LAYER                                        */
  /* ============================================ */
  
  --layer: var(--background-plain);
  --layer-line: var(--border);
  --layer-foreground: var(--foreground);
  --layer-hover: var(--background-1);
  --layer-focus: var(--background-1);
  --layer-active: var(--background-1);
  
  /* ============================================ */
  /* SURFACE                                      */
  /* ============================================ */
  
  --surface: var(${g}-100);
  --surface-1: var(${g}-200);
  --surface-2: var(${g}-300);
  --surface-3: var(${g}-400);
  --surface-4: var(${g}-500);
  --surface-5: var(${g}-600);
  --surface-line: transparent;
  --surface-foreground: var(${g}-800);
  --surface-hover: var(${g}-200);
  --surface-focus: var(${g}-200);
  --surface-active: var(${g}-200);
  
  /* ============================================ */
  /* MUTED                                        */
  /* ============================================ */
  
  --muted: var(${g}-50);
  --muted-foreground: var(${g}-500);
  --muted-foreground-1: var(${g}-600);
  --muted-foreground-2: var(${g}-700);
  --muted-hover: var(${g}-100);
  --muted-focus: var(${g}-100);
  --muted-active: var(${g}-100);
  
  /* ============================================ */
  /* DESTRUCTIVE                                  */
  /* ============================================ */
  
  --destructive: var(--color-red-500);
  --destructive-foreground: var(--color-white);
  --destructive-hover: var(--color-red-600);
  --destructive-focus: var(--color-red-600);
  
  /* ============================================ */
  /* NAVBAR                                       */
  /* ============================================ */
  
  --navbar: var(--background-plain);
  --navbar-line: var(--border);
  --navbar-divider: var(--border);
  --navbar-nav-foreground: var(--foreground);
  --navbar-nav-hover: var(--muted-hover);
  --navbar-nav-focus: var(--muted-hover);
  --navbar-nav-active: var(--muted-hover);
  --navbar-nav-list-divider: var(--border);
  --navbar-inverse: var(--inverse);
  
  --navbar-1: var(--background-1);
  --navbar-1-line: var(--border);
  --navbar-1-divider: var(--border);
  --navbar-1-nav-foreground: var(--foreground);
  --navbar-1-nav-hover: var(--surface-1);
  --navbar-1-nav-focus: var(--surface-1);
  --navbar-1-nav-active: var(--surface-1);
  --navbar-1-nav-list-divider: var(--border);
  
  --navbar-2: var(--background-2);
  --navbar-2-line: transparent;
  --navbar-2-divider: var(--border-line-3);
  --navbar-2-nav-foreground: var(--foreground);
  --navbar-2-nav-hover: var(--surface-1);
  --navbar-2-nav-focus: var(--surface-1);
  --navbar-2-nav-active: var(--surface-1);
  --navbar-2-nav-list-divider: var(--border);
  
  /* ============================================ */
  /* SIDEBAR                                      */
  /* ============================================ */
  
  --sidebar: var(--background-plain);
  --sidebar-line: var(--border);
  --sidebar-divider: var(--border);
  --sidebar-nav-foreground: var(--foreground);
  --sidebar-nav-hover: var(--muted-hover);
  --sidebar-nav-focus: var(--muted-hover);
  --sidebar-nav-active: var(--muted-hover);
  --sidebar-nav-list-divider: var(--border);
  --sidebar-inverse: var(--inverse);
  
  --sidebar-1: var(--background-1);
  --sidebar-1-line: var(--border);
  --sidebar-1-divider: var(--border);
  --sidebar-1-nav-foreground: var(--foreground);
  --sidebar-1-nav-hover: var(--surface-1);
  --sidebar-1-nav-focus: var(--surface-1);
  --sidebar-1-nav-active: var(--surface-1);
  --sidebar-1-nav-list-divider: var(--border);
  
  --sidebar-2: var(--background-2);
  --sidebar-2-line: transparent;
  --sidebar-2-divider: var(--border);
  --sidebar-2-nav-foreground: var(--foreground);
  --sidebar-2-nav-hover: var(--surface-1);
  --sidebar-2-nav-focus: var(--surface-1);
  --sidebar-2-nav-active: var(--surface-1);
  --sidebar-2-nav-list-divider: var(--border);
  
  /* ============================================ */
  /* CARD                                         */
  /* ============================================ */
  
  --card: var(--background-plain);
  --card-line: var(--border);
  --card-divider: var(--border);
  --card-header: var(--background-2);
  --card-footer: var(--background-2);
  --card-inverse: var(--inverse);
  
  /* ============================================ */
  /* DROPDOWN                                     */
  /* ============================================ */
  
  --dropdown: var(--background-plain);
  --dropdown-1: var(--background-plain);
  --dropdown-line: transparent;
  --dropdown-divider: var(--border);
  --dropdown-header: var(--background-2);
  --dropdown-footer: var(--background-2);
  --dropdown-item-foreground: var(--foreground);
  --dropdown-item-hover: var(--muted-hover);
  --dropdown-item-focus: var(--muted-hover);
  --dropdown-item-active: var(--muted-hover);
  --dropdown-inverse: var(--inverse);
  
  /* ============================================ */
  /* SELECT                                       */
  /* ============================================ */
  
  --select: var(--background-plain);
  --select-1: var(--background-plain);
  --select-line: transparent;
  --select-item-foreground: var(--foreground);
  --select-item-hover: var(--muted-hover);
  --select-item-focus: var(--muted-hover);
  --select-item-active: var(--muted-hover);
  --select-inverse: var(--inverse);
  
  /* ============================================ */
  /* OVERLAY                                      */
  /* ============================================ */
  
  --overlay: var(--background-plain);
  --overlay-line: transparent;
  --overlay-divider: var(--border);
  --overlay-header: var(--background-2);
  --overlay-footer: var(--background-2);
  --overlay-inverse: var(--inverse);
  
  /* ============================================ */
  /* POPOVER                                      */
  /* ============================================ */
  
  --popover: var(--background-plain);
  --popover-line: var(--border-line-1);
  
  /* ============================================ */
  /* TOOLTIP                                      */
  /* ============================================ */
  
  --tooltip: var(--inverse);
  --tooltip-foreground: var(--foreground-inverse);
  --tooltip-line: transparent;
  
  /* ============================================ */
  /* TABLE                                        */
  /* ============================================ */
  
  --table-line: var(--border);
  
  /* ============================================ */
  /* SWITCH                                       */
  /* ============================================ */
  
  --switch: var(--background-plain);
  
  /* ============================================ */
  /* FOOTER                                       */
  /* ============================================ */
  
  --footer: var(--background-plain);
  --footer-line: var(--border);
  --footer-inverse: var(--inverse);
  
  /* ============================================ */
  /* SCROLLBAR                                    */
  /* ============================================ */
  
  --scrollbar-track: var(--background-1);
  --scrollbar-thumb: var(--surface-2);
  --scrollbar-track-inverse: transparent;
  --scrollbar-thumb-inverse: var(--foreground-inverse);` +
    generateChartTokensLight(name) +
    generateMapTokens(name);
}

function generateDarkModeTokens(name, tailwindGray, useCustomGray = false, hue = 0, style = 'vibrant') {
  const g = useCustomGray ? `--color-${name}-gray` : `--color-${tailwindGray}`;
  const darkModePrimaryProfile = getDarkModePrimaryProfile(name, hue, style, g);
  const switchColor = darkModePrimaryProfile.switchValue;
  const primaryForeground = darkModePrimaryProfile.foregroundValue;

  return `
  /* ============================================ */
  /* DARK MODE - ${useCustomGray ? 'Custom Gray' : 'Tailwind ' + tailwindGray} */
  /* ============================================ */
  
  /* BACKGROUNDS */
  --background: var(${g}-800);
  --background-1: var(${g}-900);
  --background-2: var(${g}-950);
  --background-plain: var(${g}-800);
  
  /* TEXT */
  --foreground: var(${g}-200);
  --foreground-inverse: var(--color-white);
  
  --inverse: var(${g}-950);
  
  /* BORDERS */
  --border: var(${g}-700);
  --border-line-inverse: var(${g}-200);
  --border-line-1: var(${g}-800);
  --border-line-2: var(${g}-700);
  --border-line-3: var(${g}-600);
  --border-line-4: var(${g}-500);
  --border-line-5: var(${g}-400);
  --border-line-6: var(${g}-300);
  --border-line-7: var(${g}-200);
  --border-line-8: var(${g}-100);
  
  /* PRIMARY STATES */
  --primary: var(--color-primary-${darkModePrimaryProfile.primaryShade});
  --primary-line: transparent;
  --primary-foreground: ${primaryForeground};
  --primary-hover: var(--color-primary-${darkModePrimaryProfile.interactionShade});
  --primary-focus: var(--color-primary-${darkModePrimaryProfile.interactionShade});
  --primary-active: var(--color-primary-${darkModePrimaryProfile.interactionShade});
  --primary-checked: var(--color-primary-${darkModePrimaryProfile.checkedShade});
  
  /* SECONDARY */
  --secondary: var(--color-white);
  --secondary-line: transparent;
  --secondary-foreground: var(${g}-800);
  --secondary-hover: var(${g}-100);
  --secondary-focus: var(${g}-100);
  --secondary-active: var(${g}-100);
  
  /* LAYER */
  --layer: var(--background);
  --layer-line: var(--border);
  --layer-foreground: var(--color-white);
  --layer-hover: var(${g}-700);
  --layer-focus: var(${g}-700);
  --layer-active: var(${g}-700);
  
  /* SURFACE */
  --surface: var(${g}-700);
  --surface-1: var(${g}-600);
  --surface-2: var(${g}-500);
  --surface-3: var(${g}-600);
  --surface-4: var(${g}-500);
  --surface-5: var(${g}-400);
  --surface-line: transparent;
  --surface-foreground: var(${g}-200);
  --surface-hover: var(${g}-600);
  --surface-focus: var(${g}-600);
  --surface-active: var(${g}-600);
  
  /* MUTED */
  --muted: var(${g}-800);
  --muted-foreground: var(${g}-500);
  --muted-foreground-1: var(${g}-400);
  --muted-foreground-2: var(${g}-300);
  --muted-hover: var(${g}-700);
  --muted-focus: var(${g}-700);
  --muted-active: var(${g}-700);
  
  /* DESTRUCTIVE */
  --destructive: var(--color-red-500);
  --destructive-foreground: var(--color-white);
  --destructive-hover: var(--color-red-600);
  --destructive-focus: var(--color-red-600);
  
  /* NAVBAR */
  --navbar: var(--background);
  --navbar-line: var(--border);
  --navbar-divider: var(--border);
  --navbar-nav-foreground: var(--foreground);
  --navbar-nav-hover: var(--muted-hover);
  --navbar-nav-focus: var(--muted-hover);
  --navbar-nav-active: var(--muted-hover);
  --navbar-nav-list-divider: var(--border);
  --navbar-inverse: var(--inverse);
  
  --navbar-1: var(--background-1);
  --navbar-1-line: var(--border);
  --navbar-1-divider: var(--border);
  --navbar-1-nav-foreground: var(--foreground);
  --navbar-1-nav-hover: var(--surface);
  --navbar-1-nav-focus: var(--surface);
  --navbar-1-nav-active: var(--surface);
  --navbar-1-nav-list-divider: var(--border);
  
  --navbar-2: var(--background-2);
  --navbar-2-line: transparent;
  --navbar-2-divider: var(--border);
  --navbar-2-nav-foreground: var(--foreground);
  --navbar-2-nav-hover: var(--surface);
  --navbar-2-nav-focus: var(--surface);
  --navbar-2-nav-active: var(--surface);
  --navbar-2-nav-list-divider: var(--border);
  
  /* SIDEBAR */
  --sidebar: var(--background);
  --sidebar-line: var(--border);
  --sidebar-divider: var(--border);
  --sidebar-nav-foreground: var(--foreground);
  --sidebar-nav-hover: var(--muted-hover);
  --sidebar-nav-focus: var(--muted-hover);
  --sidebar-nav-active: var(--muted-hover);
  --sidebar-nav-list-divider: var(--border);
  --sidebar-inverse: var(--inverse);
  
  --sidebar-1: var(--background-1);
  --sidebar-1-line: var(--border);
  --sidebar-1-divider: var(--border);
  --sidebar-1-nav-foreground: var(--foreground);
  --sidebar-1-nav-hover: var(--surface);
  --sidebar-1-nav-focus: var(--surface);
  --sidebar-1-nav-active: var(--surface);
  --sidebar-1-nav-list-divider: var(--border);
  
  --sidebar-2: var(--background-2);
  --sidebar-2-line: transparent;
  --sidebar-2-divider: var(--border);
  --sidebar-2-nav-foreground: var(--foreground);
  --sidebar-2-nav-hover: var(--surface);
  --sidebar-2-nav-focus: var(--surface);
  --sidebar-2-nav-active: var(--surface);
  --sidebar-2-nav-list-divider: var(--border);
  
  /* CARD */
  --card: var(--background);
  --card-line: var(--border);
  --card-divider: var(--border);
  --card-header: var(--surface);
  --card-footer: var(--surface);
  --card-inverse: var(--inverse);
  
  /* DROPDOWN */
  --dropdown: var(--background-1);
  --dropdown-1: var(--background-2);
  --dropdown-line: transparent;
  --dropdown-divider: var(--border);
  --dropdown-header: var(--surface);
  --dropdown-footer: var(--surface);
  --dropdown-item-foreground: var(--foreground);
  --dropdown-item-hover: var(--muted-hover);
  --dropdown-item-focus: var(--muted-hover);
  --dropdown-item-active: var(--muted-hover);
  --dropdown-inverse: var(--inverse);
  
  /* SELECT */
  --select: var(--background-1);
  --select-1: var(--background-2);
  --select-line: transparent;
  --select-item-foreground: var(--foreground);
  --select-item-hover: var(--muted-hover);
  --select-item-focus: var(--muted-hover);
  --select-item-active: var(--muted-hover);
  --select-inverse: var(--inverse);
  
  /* OVERLAY */
  --overlay: var(--background);
  --overlay-line: transparent;
  --overlay-divider: var(--border);
  --overlay-header: var(--surface);
  --overlay-footer: var(--surface);
  --overlay-inverse: var(--inverse);
  
  /* POPOVER */
  --popover: var(--background-1);
  --popover-line: var(--border);
  
  /* TOOLTIP */
  --tooltip: var(--color-white);
  --tooltip-foreground: var(${g}-800);
  --tooltip-line: transparent;
  
  /* TABLE */
  --table-line: var(--border);
  
  /* SWITCH */
  --switch: ${switchColor};
  
  /* FOOTER */
  --footer: var(--background);
  --footer-line: var(--border);
  --footer-inverse: var(--inverse);
  
  /* SCROLLBAR */
  --scrollbar-track: var(--surface);
  --scrollbar-thumb: var(--surface-3);
  --scrollbar-track-inverse: var(--surface-4);
  --scrollbar-thumb-inverse: var(--surface-2);` +
    generateChartTokensDark(name, g, darkModePrimaryProfile) +
    `
  
  /* MAPS - dark mode adjustments */
  --map-colors-default: var(--surface);
  --map-colors-default-inverse: var(--surface-2);
  --map-colors-border: var(--border-line-3);
  --map-colors-border-inverse: var(--border-line-4);`;
}

// ============================================
// FONT SUPPORT
// ============================================

function generateFontTokens(config) {
  const fonts = [];

  if (config.fontSans) {
    fonts.push(`  /* Typography */`);
    fonts.push(`  --font-sans: ${config.fontSans};`);
  }
  if (config.fontSerif) {
    fonts.push(`  --font-serif: ${config.fontSerif};`);
  }
  if (config.fontMono) {
    fonts.push(`  --font-mono: ${config.fontMono};`);
  }

  if (fonts.length > 0) {
    return '\n' + fonts.join('\n') + '\n';
  }
  return '';
}

// ============================================
// MAIN GENERATOR
// ============================================

/**
 * Generate a complete theme CSS file from config
 * 
 * @param {Object} config - Theme configuration
 * @param {string} config.name - Theme name (kebab-case)
 * @param {number} [config.hue] - Brand color hue (0-360) - required if no primaryColor
 * @param {string} [config.primaryColor] - Brand color as hex (e.g., "#2F6BFF") - converts to hue
 * @param {string} [config.style='vibrant'] - 'vibrant' or 'soft'
 * @param {boolean} [config.useCustomDarkGray=false] - Use custom gray for dark mode
 * @param {string} [config.tailwindGray='neutral'] - Tailwind gray for dark mode
 * @param {string} [config.fontSans] - Optional custom sans-serif font stack
 * @param {string} [config.fontSerif] - Optional custom serif font stack
 * @param {string} [config.fontMono] - Optional custom monospace font stack
 * @returns {string} Complete CSS theme file
 */
function generateTheme(config) {
  // Validate config
  const errors = validateConfig(config);
  if (errors.length > 0) {
    throw new Error('Invalid config:\n  - ' + errors.join('\n  - '));
  }

  // Resolve hue from primaryColor if provided
  let hue = config.hue;
  if (config.primaryColor && typeof hue !== 'number') {
    hue = hexToHue(config.primaryColor);
  }

  const {
    name,
    style = 'vibrant',
    useCustomDarkGray = false,
    tailwindGray = 'neutral',
  } = config;

  const themeName = `theme-${name}`;
  const displayName = name.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');

  // Choose Tailwind gray based on warmth if not specified
  const darkGray = tailwindGray || (hue > 30 && hue < 200 ? 'stone' : 'neutral');

  const brandPalette = generateBrandPalette(name, hue, style);
  const grayPalette = generateGrayPalette(name, hue);
  const fontTokens = generateFontTokens(config);
  const lightTokens = generateLightModeTokens(name, hue, style);
  const darkTokens = generateDarkModeTokens(name, darkGray, useCustomDarkGray, hue, style);

  return `/* ------------------------------ */
/* ---------- ${displayName} ----------- */
/* ------------------------------ */

@theme ${themeName} inline {
  /* Brand palette (${style}) */
${brandPalette}

  /* Gray palette */
${grayPalette}

}

:root[data-theme="${themeName}"],
[data-theme="${themeName}"] {
${fontTokens}${lightTokens}
}

[data-theme="${themeName}"].dark {
${darkTokens}
}
`;
}

module.exports = {
  generateTheme,
  generateBrandPalette,
  generateGrayPalette,
  oklchToHex,
  hexToHue,
  validateConfig
};
