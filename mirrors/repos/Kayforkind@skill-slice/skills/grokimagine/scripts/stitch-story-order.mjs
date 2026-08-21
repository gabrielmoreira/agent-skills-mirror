/**
 * Stitch Agent clips into FINAL in explicit story order.
 *
 * Env:
 *   GROK_OUT     export root containing clips/
 *   GROK_ORDER   comma-separated basenames under clips/ (required)
 *                e.g. p03_abc.mp4,p04_def.mp4,...
 *   GROK_FINAL   output name (default FINAL_story_order.mp4)
 *   GROK_COPY_STORY=1 also copy ordered files to clips_story/S01_...
 */
import fs from "fs";
import path from "path";
import { spawnSync } from "child_process";

const OUT = process.env.GROK_OUT;
const ORDER = process.env.GROK_ORDER || "";
const FINAL_NAME = process.env.GROK_FINAL || "FINAL_story_order.mp4";
const COPY_STORY = process.env.GROK_COPY_STORY !== "0";

if (!OUT) {
  console.error(JSON.stringify({ ok: false, reason: "GROK_OUT required" }));
  process.exit(2);
}
const basenames = ORDER.split(/[,;\n]+/)
  .map((s) => s.trim())
  .filter(Boolean);
if (basenames.length < 2) {
  console.error(
    JSON.stringify({
      ok: false,
      reason: "GROK_ORDER needs ≥2 clip basenames under clips/",
      example: "GROK_ORDER=p03_xxx.mp4,p04_yyy.mp4,...",
    })
  );
  process.exit(2);
}

const CLIPS = path.join(OUT, "clips");
const STORY = path.join(OUT, "clips_story");
if (COPY_STORY) fs.mkdirSync(STORY, { recursive: true });

const files = [];
for (let i = 0; i < basenames.length; i++) {
  const base = basenames[i].replace(/^["']|["']$/g, "");
  const full = path.isAbsolute(base) ? base : path.join(CLIPS, base);
  if (!fs.existsSync(full)) {
    console.error(JSON.stringify({ ok: false, reason: "missing_clip", full }));
    process.exit(3);
  }
  files.push(full);
  if (COPY_STORY) {
    const dest = path.join(
      STORY,
      `S${String(i + 1).padStart(2, "0")}_${path.basename(full)}`
    );
    fs.copyFileSync(full, dest);
  }
}

const listPath = path.join(OUT, "concat_story_order.txt");
const listBody = files.map((f) => `file '${f.replace(/\\/g, "/")}'`).join("\n") + "\n";
// Explicit no-BOM write
fs.writeFileSync(listPath, listBody, { encoding: "utf8" });

const finalPath = path.join(OUT, FINAL_NAME);
const r = spawnSync(
  "ffmpeg",
  ["-y", "-f", "concat", "-safe", "0", "-i", listPath, "-c", "copy", finalPath],
  { encoding: "utf8" }
);

const ok = r.status === 0 && fs.existsSync(finalPath);
const probe = ok
  ? spawnSync(
      "ffprobe",
      [
        "-v",
        "error",
        "-show_entries",
        "format=duration,size",
        "-of",
        "default=noprint_wrappers=1",
        finalPath,
      ],
      { encoding: "utf8" }
    )
  : null;

console.log(
  JSON.stringify(
    {
      ok,
      finalPath: ok ? finalPath : null,
      bytes: ok ? fs.statSync(finalPath).size : 0,
      order: basenames,
      listPath,
      probe: probe?.stdout?.trim() || null,
      ffmpegTail: (r.stderr || r.stdout || "").slice(-600),
    },
    null,
    2
  )
);
process.exit(ok ? 0 : 4);
