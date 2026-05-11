#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { generateTheme } = require('./generate-theme');

function printHelp() {
  console.log(`Usage:
  node scripts/run-theme-generator.js --name <theme-name> [--hue <0-360> | --primary-color <hex>] [options] --stdout
  node scripts/run-theme-generator.js --name <theme-name> [--hue <0-360> | --primary-color <hex>] [options] --output <path>

This wrapper generates a single final Preline theme file. It should create only the new
\`<name>.css\` output and never require follow-up project file edits.

Options:
  --name <value>                 Theme name in kebab-case.
  --hue <number>                 Brand hue from 0 to 360.
  --primary-color <hex>          Hex color such as #2F6BFF.
  --style <vibrant|soft>         Brand palette style.
  --tailwind-gray <value>        Dark-mode neutral family.
  --use-custom-dark-gray         Use generated gray palette in dark mode.
  --font-sans <stack>            Optional font stack.
  --font-serif <stack>           Optional font stack.
  --font-mono <stack>            Optional font stack.
  --output <path>                Write CSS to file.
  --stdout                       Print CSS to stdout.
`);
}

function fail(message) {
  console.error(message);
  process.exit(1);
}

function requireValue(flag, value) {
  if (!value) {
    fail(`Missing value for ${flag}`);
  }

  return value;
}

function parseArgs(argv) {
  const config = {};
  let outputPath = null;
  let writeToStdout = false;

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];

    switch (arg) {
      case '--name':
        config.name = requireValue(arg, argv[i + 1]);
        i += 1;
        break;
      case '--hue':
        config.hue = Number(requireValue(arg, argv[i + 1]));
        i += 1;
        break;
      case '--primary-color':
        config.primaryColor = requireValue(arg, argv[i + 1]);
        i += 1;
        break;
      case '--style':
        config.style = requireValue(arg, argv[i + 1]);
        i += 1;
        break;
      case '--tailwind-gray':
        config.tailwindGray = requireValue(arg, argv[i + 1]);
        i += 1;
        break;
      case '--use-custom-dark-gray':
        config.useCustomDarkGray = true;
        break;
      case '--font-sans':
        config.fontSans = requireValue(arg, argv[i + 1]);
        i += 1;
        break;
      case '--font-serif':
        config.fontSerif = requireValue(arg, argv[i + 1]);
        i += 1;
        break;
      case '--font-mono':
        config.fontMono = requireValue(arg, argv[i + 1]);
        i += 1;
        break;
      case '--output':
        outputPath = requireValue(arg, argv[i + 1]);
        i += 1;
        break;
      case '--stdout':
        writeToStdout = true;
        break;
      case '--help':
        printHelp();
        process.exit(0);
      default:
        fail(`Unknown argument: ${arg}`);
    }
  }

  if (!outputPath && !writeToStdout) {
    writeToStdout = true;
  }

  if (outputPath && writeToStdout) {
    fail('Use either --output or --stdout, not both');
  }

  return {
    config,
    outputPath,
    writeToStdout,
  };
}

function writeOutput(outputPath, css) {
  const absolutePath = path.resolve(outputPath);
  fs.mkdirSync(path.dirname(absolutePath), { recursive: true });
  fs.writeFileSync(absolutePath, css, 'utf8');
  console.error(`Wrote ${absolutePath}`);

  console.error('Generated a final standalone theme file.');
}

function main() {
  const { config, outputPath, writeToStdout } = parseArgs(process.argv.slice(2));
  const css = generateTheme(config);

  if (writeToStdout) {
    process.stdout.write(css);
    return;
  }

  writeOutput(outputPath, css);
}

try {
  main();
} catch (error) {
  fail(error.message);
}
