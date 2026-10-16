#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const { loadSourceRules } = require("./source-rules");

const root = path.resolve(process.cwd());
const sourceRoot = path.join(root, "01-原始素材区");
const stateRoot = path.join(root, "03-处理状态");

const rawIndexPath = path.join(stateRoot, "原始素材索引.csv");
const pendingPath = path.join(stateRoot, "待处理清单.csv");
const processedPath = path.join(stateRoot, "已处理清单.csv");

const catalog = loadSourceRules(root);

function walkFiles(dir) {
  const results = [];
  if (!fs.existsSync(dir)) return results;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) results.push(...walkFiles(full));
    else if (entry.isFile() && /\.(md|txt|html|csv|json|jsonl)$/i.test(entry.name)) results.push(full);
  }
  return results;
}

function csvEscape(value) {
  return `"${String(value).replaceAll("\"", "\"\"")}"`;
}

function readProcessedPaths() {
  const processed = new Set();
  if (!fs.existsSync(processedPath)) return processed;
  const lines = fs.readFileSync(processedPath, "utf8").split("\n").slice(1);
  for (const line of lines) {
    if (!line.trim()) continue;
    const match = line.match(/^"((?:[^"]|"")*)"/);
    if (!match) continue;
    processed.add(match[1].replaceAll("\"\"", "\""));
  }
  return processed;
}

const processed = readProcessedPaths();
const rawRows = [["path", "category"]];
const pendingRows = [["path", "status", "source_type", "notes"]];

for (const rule of catalog) {
  const files = rule.dirs
    .flatMap((rel) => walkFiles(path.join(sourceRoot, rel)))
    .map((file) => path.relative(sourceRoot, file).replaceAll(path.sep, "/"))
    .sort((a, b) => a.localeCompare(b, "zh-Hans-CN"));

  for (const rel of files) {
    rawRows.push([rel, rule.category]);
    if (!processed.has(rel)) pendingRows.push([rel, "待处理", rule.sourceType, ""]);
  }
}

fs.writeFileSync(rawIndexPath, rawRows.map((row) => row.map(csvEscape).join(",")).join("\n") + "\n");
fs.writeFileSync(pendingPath, pendingRows.map((row) => row.map(csvEscape).join(",")).join("\n") + "\n");

console.log(JSON.stringify({
  rawIndexPath,
  pendingPath,
  rawCount: rawRows.length - 1,
  pendingCount: pendingRows.length - 1,
}, null, 2));
