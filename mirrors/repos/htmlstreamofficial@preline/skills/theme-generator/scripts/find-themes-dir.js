#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const TRUSTED_THEME_DIRS = [
  'src/assets/css/themes',
  'src/css/themes',
  'src/styles/themes',
  'assets/css/themes',
  'styles/themes',
  'dist/assets/css/themes',
  'npm/preline/css/themes',
];

function parseArgs(argv) {
  const options = {
    all: false,
    absolute: false,
    cwd: process.cwd(),
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];

    if (arg === '--all') {
      options.all = true;
      continue;
    }

    if (arg === '--absolute') {
      options.absolute = true;
      continue;
    }

    if (arg === '--cwd') {
      const value = argv[i + 1];
      if (!value) {
        throw new Error('Missing value for --cwd');
      }

      options.cwd = path.resolve(value);
      i += 1;
      continue;
    }

    if (arg === '--help') {
      console.log(`Usage:
  node scripts/find-themes-dir.js [--all] [--absolute] [--cwd <path>]

Checks a short allowlist of trusted Preline theme directories and prints matches.
`);
      process.exit(0);
    }

    throw new Error(`Unknown argument: ${arg}`);
  }

  return options;
}

function hasBaseTheme(dir) {
  return fs.existsSync(path.join(dir, 'theme.css'));
}

function main() {
  const options = parseArgs(process.argv.slice(2));

  const matches = TRUSTED_THEME_DIRS
    .map((relativeDir) => {
      const absoluteDir = path.resolve(options.cwd, relativeDir);
      return {
        relativeDir,
        absoluteDir,
      };
    })
    .filter(({ absoluteDir }) => hasBaseTheme(absoluteDir));

  if (matches.length === 0) {
    process.exit(1);
  }

  const output = options.all ? matches : [matches[0]];

  output.forEach(({ relativeDir, absoluteDir }) => {
    console.log(options.absolute ? absoluteDir : relativeDir);
  });
}

try {
  main();
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
