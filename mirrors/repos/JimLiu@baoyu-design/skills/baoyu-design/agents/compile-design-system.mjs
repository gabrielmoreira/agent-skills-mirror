#!/usr/bin/env node
// compile-design-system.mjs — the WRITE step of the portable design-system
// pipeline. It reimplements the web product's "automated compiler": it reads a
// design-system folder, transpiles every component .jsx/.tsx with the vendored
// @babel/standalone (JSX/TSX → React.createElement, classic runtime), and emits
// the three artifacts the runtime cards load:
//
//   _ds_bundle.js            — one IIFE that defines window.<Namespace>.<Component>
//   _ds_manifest.json        — namespace, components, cards, starting points, tokens, fonts
//   _adherence.oxlintrc.json — lint config (raw hex/px + per-component prop whitelists)
//
// Usage: node compile-design-system.mjs <projectDir>
//
// Only THIS script writes; the parser (ds-core.mjs) and checker
// (check-design-system.mjs) write nothing.

import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { createRequire } from 'node:module';
import { buildModel } from './lib/ds-core.mjs';

const require = createRequire(import.meta.url);
const here = path.dirname(new URL(import.meta.url).pathname);

// --- load vendored Babel (UMD → CJS) ------------------------------------------
let Babel;
try {
  Babel = require('./vendor/babel.min.js');
  if (!Babel || typeof Babel.transform !== 'function') {
    throw new Error('vendored Babel did not expose transform()');
  }
} catch (e) {
  process.stderr.write(
    `compile-design-system: could not load agents/vendor/babel.min.js — ${(e && e.message) || e}\n` +
    'Fetch it once with: curl -L https://unpkg.com/@babel/standalone@7.29.0/babel.min.js -o agents/vendor/babel.min.js\n',
  );
  process.exit(1);
}

// --- Babel plugin: strip ESM, keep React/window globals -----------------------
// The reference sources read deps from globals (`const React = window.React`,
// `const { Icon } = window.<NS>`) and use no ESM imports. Defensively we also
// strip react/react-dom imports and rewrite relative imports to read from
// __ds_scope, so an authored component that *does* use imports still bundles.
function makeStripPlugin({ types: t }) {
  return {
    visitor: {
      ExportNamedDeclaration(p) {
        if (p.node.declaration) p.replaceWith(p.node.declaration);
        else p.remove();
      },
      ExportDefaultDeclaration(p) {
        const d = p.node.declaration;
        if (t.isFunctionDeclaration(d) || t.isClassDeclaration(d)) {
          if (d.id) p.replaceWith(d);
          else p.remove();
        } else {
          p.remove();
        }
      },
      ExportAllDeclaration(p) { p.remove(); },
      ImportDeclaration(p) {
        const src = p.node.source.value;
        if (src === 'react' || src === 'react-dom' || src === 'react-dom/client') {
          p.remove();
          return;
        }
        if (src.startsWith('.') || src.startsWith('/')) {
          // relative sibling import → pull the names out of __ds_scope
          const names = [];
          for (const s of p.node.specifiers) {
            if (t.isImportDefaultSpecifier(s) || t.isImportNamespaceSpecifier(s)) {
              names.push(t.objectProperty(t.identifier(s.local.name), t.identifier(s.local.name), false, true));
            } else if (t.isImportSpecifier(s)) {
              const imported = s.imported.name || s.imported.value;
              names.push(t.objectProperty(t.identifier(imported), t.identifier(s.local.name), false, imported === s.local.name));
            }
          }
          if (names.length) {
            p.replaceWith(
              t.variableDeclaration('const', [
                t.variableDeclarator(t.objectPattern(names), t.identifier('__ds_scope')),
              ]),
            );
          } else {
            p.remove();
          }
        }
        // bare external imports (e.g. a CDN lib) are left as-is for the author to resolve
      },
    },
  };
}

function transpile(code, file) {
  const isTsx = /\.tsx$/.test(file);
  const isTs = /\.tsx?$/.test(file);
  const presets = [['react', { runtime: 'classic' }]];
  if (isTs) presets.push(['typescript', { isTSX: isTsx, allExtensions: true }]);
  const out = Babel.transform(code, {
    filename: file,
    presets,
    plugins: [makeStripPlugin],
    sourceType: 'module',
    compact: false,
    comments: true,
    retainLines: false,
  });
  return out.code;
}

// --- bundle assembly ----------------------------------------------------------
function sourceHash(code) {
  return crypto.createHash('sha256').update(code).digest('hex').slice(0, 12);
}

function buildBundle(model) {
  const { root, namespace, components, unexposedExports, allSources } = model;
  const sourceHashes = {};
  const blocks = [];
  const exposed = new Set(components.map((c) => c.name));

  for (const s of allSources) {
    const abs = path.join(root, s.path);
    let raw = '';
    try { raw = fs.readFileSync(abs, 'utf8'); } catch { /* skip */ }
    sourceHashes[s.path] = sourceHash(raw);
    let body;
    try {
      body = transpile(raw, s.path);
    } catch (e) {
      // a file that fails to transpile becomes a runtime error entry, matching
      // the bundle's per-file try/catch contract
      body = `throw new Error(${JSON.stringify('transpile failed: ' + ((e && e.message) || e))});`;
    }
    const assign = s.exports.length
      ? `\nObject.assign(__ds_scope, { ${s.exports.join(', ')} });`
      : '';
    blocks.push(
      `// ${s.path}\n` +
      `try { (() => {\n${body}${assign}\n})(); } catch (e) { ` +
      `__ds_ns.__errors.push({ path: ${JSON.stringify(s.path)}, error: String((e && e.message) || e) }); }`,
    );
  }

  const meta = {
    format: 3,
    namespace,
    components: components.map((c) => ({ name: c.name, sourcePath: c.sourcePath })),
    sourceHashes,
    inlinedExternals: [],
    unexposedExports: unexposedExports.map((u) => ({ name: u.name, sourcePath: u.sourcePath })),
  };

  const tail = components.map((c) => `__ds_ns.${c.name} = __ds_scope.${c.name};`).join('\n\n');

  return (
    `/* @ds-bundle: ${JSON.stringify(meta)} */\n\n` +
    `(() => {\n\n` +
    `const __ds_ns = (window.${namespace} = window.${namespace} || {});\n\n` +
    `const __ds_scope = {};\n\n` +
    `(__ds_ns.__errors = __ds_ns.__errors || []);\n\n` +
    blocks.join('\n\n') +
    `\n\n` +
    (tail ? tail + '\n\n' : '') +
    `})();\n`
  );
}

// --- manifest -----------------------------------------------------------------
function buildManifest(model) {
  return {
    namespace: model.namespace,
    components: model.components,
    startingPoints: model.startingPoints,
    cards: model.cards,
    globalCssPaths: model.globalCssPaths,
    tokens: model.tokens,
    themes: model.themes,
    fonts: model.fonts,
    brandFonts: model.brandFonts,
    source: model.source,
  };
}

// --- adherence lint config ----------------------------------------------------
// The web compiler derives one JSX prop-whitelist per component .d.ts file from
// the FIRST exported interface in that file — its name minus a trailing "Props"
// is the JSX element, its properties are the allowed props — then orders the
// components alphabetically. For collection components (Dropdown/RadioGroup/
// TabList) the first interface is the item shape (DropdownOption/RadioOption/
// TabItem), so the rule targets the item element, not the container; for a file
// with several interfaces (Card → CardProps, CardHeaderProps) only the first is
// used. This is advisory lint config.
const ALWAYS_PROPS = ['key', 'ref', 'className', 'style', 'children'];

function parseFirstInterface(dtsSrc) {
  const re = /(?:export\s+)?interface\s+([A-Za-z][A-Za-z0-9]*)\b[^{]*\{/;
  const m = re.exec(dtsSrc);
  if (!m) return null;
  // capture balanced-ish body (interfaces here are flat, no nested braces)
  let i = m.index + m[0].length;
  let depth = 1;
  let body = '';
  while (i < dtsSrc.length && depth > 0) {
    const ch = dtsSrc[i];
    if (ch === '{') depth++;
    else if (ch === '}') { depth--; if (depth === 0) break; }
    body += ch;
    i++;
  }
  const props = [];
  // split single-line interfaces (`{ value: string; label: ... }`) onto rows so
  // the line-anchored prop regex matches every member, while keeping function
  // types like `onChange?: (value: string) => void` from yielding a bogus prop.
  const norm = body.replace(/;/g, ';\n');
  const propRe = /(?:^|\n)\s*([A-Za-z][A-Za-z0-9]*)\??\s*:\s*([^;]+);/g;
  let pm;
  while ((pm = propRe.exec(norm))) {
    const name = pm[1];
    const type = pm[2].trim();
    const union = [...type.matchAll(/'([^']+)'/g)].map((u) => u[1]);
    const isPureUnion = /^(\s*'[^']+'\s*\|?\s*)+$/.test(type);
    props.push({ name, values: isPureUnion && union.length ? union : null });
  }
  return { name: m[1].replace(/Props$/, ''), props };
}

function buildAdherence(model) {
  const root = model.root;
  // import-restriction groups: each directory that holds source files
  const dirs = [...new Set(model.allSources.map((s) => path.posix.dirname(s.path)))]
    .filter((d) => d && d !== '.')
    .sort()
    .map((d) => `${d}/**`);

  const syntax = [
    {
      selector: 'Literal[value=/#[0-9a-fA-F]{3,8}\\b/]',
      message: 'Raw hex color — use a design-system color token via var().',
    },
    {
      selector: 'Literal[value=/\\b\\d+px\\b/]',
      message: 'Raw px value — use a design-system spacing token via var().',
    },
  ];

  const dtsCache = new Map();
  const readDts = (p) => {
    if (dtsCache.has(p)) return dtsCache.get(p);
    let s = '';
    try { s = fs.readFileSync(path.join(root, p), 'utf8'); } catch { /* */ }
    dtsCache.set(p, s);
    return s;
  };

  // one adherence component per module .d.ts: the file's first exported interface
  const components = [];
  const seenDts = new Set();
  for (const s of model.allSources) {
    if (!s.isModule || seenDts.has(s.dtsPath)) continue;
    seenDts.add(s.dtsPath);
    const iface = parseFirstInterface(readDts(s.dtsPath));
    if (iface) components.push(iface);
  }
  components.sort((a, b) => (a.name < b.name ? -1 : a.name > b.name ? 1 : 0));

  for (const { name, props } of components) {
    const allowed = [...props.map((p) => p.name), ...ALWAYS_PROPS];
    const allowedRe = `^(?:${allowed.join('|')})$`;
    syntax.push({
      selector: `JSXOpeningElement[name.name='${name}'] > JSXAttribute > JSXIdentifier[name!=/${allowedRe}/]`,
      message: `<${name}> doesn't accept that prop. Declared props: ${props.map((p) => p.name).join(', ')}.`,
    });
    for (const p of props) {
      if (!p.values) continue;
      const valRe = `^(?:${p.values.join('|')})$`;
      syntax.push({
        selector: `JSXOpeningElement[name.name='${name}'] > JSXAttribute[name.name='${p.name}'] > Literal[value!=/${valRe}/]`,
        message: `<${name}> ${p.name} must be one of ${p.values.map((v) => `'${v}'`).join(' | ')}.`,
      });
    }
  }

  const tokensSorted = model.tokens.map((t) => t.name).sort();
  const tokenKinds = {};
  for (const t of model.tokens) tokenKinds[t.name] = t.kind;
  const componentsMap = {};
  for (const { name } of components) componentsMap[name] = { replaces: [] };

  return {
    plugins: ['react', 'import'],
    rules: {
      'react/forbid-elements': ['warn', { forbid: [] }],
      'no-restricted-imports': ['warn', {
        patterns: [{
          group: dirs,
          message: "Import design-system components from 'index.js', not component internals.",
        }],
      }],
      'no-restricted-syntax': ['warn', ...syntax],
    },
    overrides: [{ files: ['**/index.js'], rules: { 'no-restricted-imports': 'off' } }],
    'x-omelette': {
      components: componentsMap,
      tokens: tokensSorted,
      tokenKinds,
      fontFamilies: model.fonts.map((f) => f.family),
    },
  };
}

// --- main ---------------------------------------------------------------------
const projectDir = process.argv[2];
if (!projectDir) {
  process.stderr.write('Usage: node compile-design-system.mjs <projectDir>\n');
  process.exit(64);
}

let model;
try {
  model = buildModel(projectDir);
} catch (e) {
  process.stderr.write(`compile-design-system: ${(e && e.message) || e}\n`);
  process.exit(1);
}

const bundle = buildBundle(model);
const manifest = buildManifest(model);
const adherence = buildAdherence(model);

const w = (name, content) => {
  fs.writeFileSync(path.join(model.root, name), content);
  return name;
};

w('_ds_bundle.js', bundle);
w('_ds_manifest.json', JSON.stringify(manifest, null, 2));
w('_adherence.oxlintrc.json', JSON.stringify(adherence, null, 2));

const hist = model.tokenHist;
const histStr = Object.keys(hist).sort().map((k) => `${k} ${hist[k]}`).join(', ');
process.stdout.write(
  `Compiled ${model.namespace}: ${model.components.length} components, ` +
  `${model.cards.length} cards, ${model.startingPoints.length} starting points, ` +
  `${model.tokens.length} tokens (${histStr}).\n` +
  'Wrote _ds_bundle.js, _ds_manifest.json, _adherence.oxlintrc.json.\n' +
  (model.unclassified.length
    ? `Note: ${model.unclassified.length} tokens unclassified by value — add /* @kind */ comments.\n`
    : ''),
);
