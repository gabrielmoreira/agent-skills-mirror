#!/usr/bin/env node
// Print a saved report's HTML as readable text, main body first, so reports
// can be compared without opening the app. Usage: node report-text.mjs <file>...
import { readFile } from "node:fs/promises";

const decode = (s) =>
  s
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;|&rsquo;|&lsquo;/g, "'")
    .replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(Number(n)));

for (const file of process.argv.slice(2)) {
  let s = await readFile(file, "utf8");
  s = s.replace(/<style[\s\S]*?<\/style>/g, "");
  s = s.replace(/<h[1-3][^>]*>/g, "\n## ");
  s = s.replace(/<(li|tr|p|summary)[^>]*>/g, "\n- ");
  s = s.replace(/<(td|th)[^>]*>/g, " | ");
  s = s.replace(/<details/g, "\n[DETAILS]<details");
  s = decode(s.replace(/<[^>]+>/g, "")).replace(/\n\s*\n+/g, "\n");
  const main = s.split("[DETAILS]")[0];
  const words = (t) => t.split(/\s+/).filter(Boolean).length;
  console.log(
    `${"=".repeat(30)} ${file} | total words ${words(s)} | main-body words ${words(main)}`,
  );
  console.log(s);
}
