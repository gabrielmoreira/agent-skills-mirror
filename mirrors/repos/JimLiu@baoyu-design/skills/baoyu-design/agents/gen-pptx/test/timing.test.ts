import { test } from "node:test";
import assert from "node:assert/strict";
import { buildTimingXml, type TimingAnim } from "../src/render/timing.ts";
import type { AnimationDef } from "../src/types.ts";

const def = (over: Partial<AnimationDef>): AnimationDef => ({
  effect: "fade-in",
  trigger: "after",
  delayMs: 0,
  durationMs: 500,
  order: 0,
  index: 0,
  ...over,
});

const anim = (spids: number[], over: Partial<AnimationDef>): TimingAnim => ({ def: def(over), spids });

test("buildTimingXml: skeleton (tmRoot, mainSeq, seq conditions, bldLst)", () => {
  const xml = buildTimingXml([anim([2], {})], 1920, 1080);
  assert.match(xml, /^<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">/);
  assert.match(xml, /<p:cTn id="2" dur="indefinite" nodeType="mainSeq">/);
  assert.match(xml, /<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt\/><\/p:tgtEl><\/p:cond><\/p:prevCondLst>/);
  assert.match(xml, /<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt\/><\/p:tgtEl><\/p:cond><\/p:nextCondLst>/);
  assert.match(xml, /<p:bldLst><p:bldP spid="2" grpId="0" animBg="1"\/><\/p:bldLst><\/p:timing>$/);
});

test("buildTimingXml: auto lead-in group opens at delay 0, click group at indefinite", () => {
  const auto = buildTimingXml([anim([2], { trigger: "after" })], 1920, 1080);
  const groupCond = auto.match(/mainSeq"><p:childTnLst><p:par><p:cTn id="\d+" fill="hold"><p:stCondLst><p:cond delay="([^"]+)"/);
  assert.equal(groupCond?.[1], "0");

  const click = buildTimingXml([anim([2], { trigger: "click" })], 1920, 1080);
  const clickCond = click.match(/mainSeq"><p:childTnLst><p:par><p:cTn id="\d+" fill="hold"><p:stCondLst><p:cond delay="([^"]+)"/);
  assert.equal(clickCond?.[1], "indefinite");
  assert.match(click, /nodeType="clickEffect"/);
});

test("buildTimingXml: after chains behind group end, with co-starts", () => {
  const xml = buildTimingXml(
    [
      anim([2], { index: 0, durationMs: 500 }),
      anim([3], { index: 1, trigger: "after", delayMs: 250, durationMs: 400 }),
      anim([4], { index: 2, trigger: "with", delayMs: 0 }),
    ],
    1920,
    1080,
  );
  // Inner-par start offsets: first 0, second 500+250=750, third with → 750.
  const starts = [...xml.matchAll(/<p:par><p:cTn id="\d+" fill="hold"><p:stCondLst><p:cond delay="(\d+)"\/><\/p:stCondLst><p:childTnLst><p:par><p:cTn id="\d+" presetID/g)].map(
    (m) => m[1],
  );
  assert.deepEqual(starts, ["0", "750", "750"]);
  assert.match(xml, /nodeType="afterEffect"/);
  assert.match(xml, /nodeType="withEffect"/);
});

test("buildTimingXml: data-anim-order overrides document order", () => {
  const xml = buildTimingXml(
    [
      anim([2], { index: 0, order: 5, effect: "fade-in" }),
      anim([3], { index: 1, order: 1, effect: "wipe-in", dir: "left" }),
    ],
    1920,
    1080,
  );
  const wipePos = xml.indexOf('filter="wipe(right)"');
  const fadePos = xml.indexOf('filter="fade"');
  assert.ok(wipePos >= 0 && fadePos >= 0 && wipePos < fadePos, "order 1 (wipe) must precede order 5 (fade)");
});

test("buildTimingXml: effect fragments", () => {
  const w = 1280;
  const h = 720;
  // fade-in: set visible + animEffect in/fade
  const fadeIn = buildTimingXml([anim([2], {})], w, h);
  assert.match(fadeIn, /<p:to><p:strVal val="visible"\/><\/p:to>/);
  assert.match(fadeIn, /<p:animEffect transition="in" filter="fade">/);
  assert.match(fadeIn, /presetID="10" presetClass="entr"/);

  // fade-out: out transition + hidden at D-1
  const fadeOut = buildTimingXml([anim([2], { effect: "fade-out", durationMs: 600 })], w, h);
  assert.match(fadeOut, /<p:animEffect transition="out" filter="fade">/);
  assert.match(fadeOut, /<p:cond delay="599"\/>.*<p:strVal val="hidden"\/>/);
  assert.match(fadeOut, /presetClass="exit"/);

  // appear/disappear: set only, dur 1
  const appear = buildTimingXml([anim([2], { effect: "appear", durationMs: 1 })], w, h);
  assert.match(appear, /presetID="1" presetClass="entr"/);
  assert.ok(!/animEffect/.test(appear));

  // fly-in from left: subtype 8, offscreen x start, both axes animated
  const fly = buildTimingXml([anim([2], { effect: "fly-in", dir: "left" })], w, h);
  assert.match(fly, /presetID="2" presetClass="entr" presetSubtype="8"/);
  assert.match(fly, /<p:strVal val="0-#ppt_w\/2"\/>/);
  assert.match(fly, /<p:attrName>ppt_y<\/p:attrName>/);
  assert.match(fly, /<p:strVal val="#ppt_x"\/>/);

  // wipe-in from bottom → wipe(up), subtype 4
  const wipe = buildTimingXml([anim([2], { effect: "wipe-in", dir: "bottom" })], w, h);
  assert.match(wipe, /presetID="22".*filter="wipe\(up\)"/);
  assert.match(wipe, /presetSubtype="4"/);

  // zoom-in: fade + scale 10% → 100%
  const zoom = buildTimingXml([anim([2], { effect: "zoom-in" })], w, h);
  assert.match(zoom, /presetID="23"/);
  assert.match(zoom, /<p:from x="10000" y="10000"\/><p:to x="100000" y="100000"\/>/);

  // spin 360° → by=21600000 on attribute r
  const spin = buildTimingXml([anim([2], { effect: "spin", rotateDeg: 360, durationMs: 2000 })], w, h);
  assert.match(spin, /<p:animRot by="21600000">/);
  assert.match(spin, /<p:attrName>r<\/p:attrName>/);
  assert.match(spin, /presetID="8" presetClass="emph"/);

  // grow ×1.5 → by=150000
  const grow = buildTimingXml([anim([2], { effect: "grow", scale: 1.5 })], w, h);
  assert.match(grow, /<p:by x="150000" y="150000"\/>/);

  // path: animMotion with fraction path + both position attributes
  const path = buildTimingXml(
    [anim([2], { effect: "path", pathSegs: [{ c: "L", p: [128, -72] }], durationMs: 2000 })],
    w,
    h,
  );
  assert.match(path, /<p:animMotion origin="layout" path="M 0 0 L 0\.10000 -0\.10000 E" pathEditMode="relative"/);
  assert.match(path, /<p:attrName>ppt_x<\/p:attrName><p:attrName>ppt_y<\/p:attrName>/);
  assert.match(path, /presetClass="path"/);
});

test("buildTimingXml: multi-shape element animates all shapes together", () => {
  const xml = buildTimingXml([anim([5, 6, 7], { trigger: "click" })], 1920, 1080);
  assert.equal([...xml.matchAll(/<p:spTgt spid="5"\/>/g)].length >= 1, true);
  const nodeTypes = [...xml.matchAll(/nodeType="(clickEffect|withEffect|afterEffect)"/g)].map((m) => m[1]);
  assert.deepEqual(nodeTypes, ["clickEffect", "withEffect", "withEffect"]);
  // one bldP per distinct spid
  assert.equal([...xml.matchAll(/<p:bldP /g)].length, 3);
});

test("buildTimingXml: every cTn id is unique", () => {
  const xml = buildTimingXml(
    [
      anim([2, 3], { index: 0, trigger: "click", effect: "fly-in", dir: "top" }),
      anim([4], { index: 1, trigger: "with", effect: "spin", rotateDeg: -720 }),
      anim([5], { index: 2, trigger: "after", effect: "zoom-out" }),
      anim([6], { index: 3, trigger: "click", effect: "path", pathSegs: [{ c: "C", p: [1, 2, 3, 4, 5, 6] }] }),
    ],
    1920,
    1080,
  );
  const ids = [...xml.matchAll(/<p:cTn id="(\d+)"/g)].map((m) => m[1]);
  assert.equal(new Set(ids).size, ids.length, `duplicate cTn ids in: ${ids.join(",")}`);
});

test("buildTimingXml: empty and all-hidden input produce no timing", () => {
  assert.equal(buildTimingXml([], 1920, 1080), "");
  assert.equal(buildTimingXml([anim([], {})], 1920, 1080), "");
});

test("buildTimingXml: new-effect fragments", () => {
  const w = 1280;
  const h = 720;
  const one = (over: Partial<AnimationDef>) => buildTimingXml([anim([2], over)], w, h);

  // wipe-out: entrance token reversed by transition="out", subtype from dir,
  // hidden lands at D-1.
  const wipeOut = one({ effect: "wipe-out", dir: "bottom", durationMs: 600 });
  assert.match(wipeOut, /presetID="22" presetClass="exit" presetSubtype="4"/);
  assert.match(wipeOut, /<p:animEffect transition="out" filter="wipe\(up\)">/);
  assert.match(wipeOut, /<p:cond delay="599"\/>.*<p:strVal val="hidden"\/>/);

  // float: fade + 0.1-slide-height ppt_y drift; Float Up = 42, Float Down = 47.
  const floatUp = one({ effect: "float-in", dir: "bottom", durationMs: 1000 });
  assert.match(floatUp, /presetID="42" presetClass="entr"/);
  assert.match(floatUp, /<p:animEffect transition="in" filter="fade">/);
  assert.match(floatUp, /<p:strVal val="#ppt_y\+\.1"\/>/);
  assert.match(floatUp, /<p:strVal val="#ppt_y"\/>/);
  assert.ok(!/ppt_x<\/p:attrName>/.test(floatUp), "float animates y only");
  const floatDown = one({ effect: "float-in", dir: "top" });
  assert.match(floatDown, /presetID="47" presetClass="entr"/);
  assert.match(floatDown, /<p:strVal val="#ppt_y-\.1"\/>/);
  const floatOut = one({ effect: "float-out", dir: "top", durationMs: 1000 });
  assert.match(floatOut, /presetID="47" presetClass="exit"/);
  assert.match(floatOut, /<p:animEffect transition="out" filter="fade">/);
  assert.match(floatOut, /<p:cond delay="999"\/>.*<p:strVal val="hidden"\/>/);

  // split: long-form barn filters and the verified subtype table.
  const splitInV = one({ effect: "split-in", dir: "vertical" });
  assert.match(splitInV, /presetID="16" presetClass="entr" presetSubtype="21"/);
  assert.match(splitInV, /filter="barn\(inVertical\)"/);
  const splitInH = one({ effect: "split-in", dir: "horizontal" });
  assert.match(splitInH, /presetSubtype="26"/);
  assert.match(splitInH, /filter="barn\(inHorizontal\)"/);
  const splitOutV = one({ effect: "split-out", dir: "vertical" });
  assert.match(splitOutV, /presetID="16" presetClass="exit" presetSubtype="37"/);
  assert.match(splitOutV, /transition="out" filter="barn\(outVertical\)"/);
  const splitOutH = one({ effect: "split-out", dir: "horizontal" });
  assert.match(splitOutH, /presetSubtype="42"/);
  assert.match(splitOutH, /filter="barn\(outHorizontal\)"/);

  // bounce: damped-hop motion path + early fade in / late fade out.
  const bounceIn = one({ effect: "bounce-in", durationMs: 2000 });
  assert.match(bounceIn, /presetID="26" presetClass="entr"/);
  assert.match(bounceIn, /path="M -0\.25 -0\.33333 C /);
  assert.match(bounceIn, /<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="\d+" dur="640"\/>/);
  const bounceOut = one({ effect: "bounce-out", durationMs: 2000 });
  assert.match(bounceOut, /presetID="26" presetClass="exit"/);
  assert.match(bounceOut, /path="M 0 0 C 0\.0025 -0\.0164 /);
  // late fade: dur 400 starting at 1600
  assert.match(bounceOut, /transition="out" filter="fade"><p:cBhvr><p:cTn id="\d+" dur="400"><p:stCondLst><p:cond delay="1600"\/>/);

  // wheel: one spoke, subtype 1.
  const wheelIn = one({ effect: "wheel-in" });
  assert.match(wheelIn, /presetID="21" presetClass="entr" presetSubtype="1"/);
  assert.match(wheelIn, /filter="wheel\(1\)"/);
  const wheelOut = one({ effect: "wheel-out", durationMs: 2000 });
  assert.match(wheelOut, /presetClass="exit"/);
  assert.match(wheelOut, /transition="out" filter="wheel\(1\)"/);
  assert.match(wheelOut, /<p:cond delay="1999"\/>.*hidden/);

  // random-bars: axis filter + subtype (horizontal 10, vertical 5).
  const rbH = one({ effect: "random-bars-in", dir: "horizontal" });
  assert.match(rbH, /presetID="14" presetClass="entr" presetSubtype="10"/);
  assert.match(rbH, /filter="randombar\(horizontal\)"/);
  const rbV = one({ effect: "random-bars-out", dir: "vertical" });
  assert.match(rbV, /presetID="14" presetClass="exit" presetSubtype="5"/);
  assert.match(rbV, /transition="out" filter="randombar\(vertical\)"/);

  // pulse: tmFilter fade dip + auto-reversed half-duration scale to 105%.
  const pulse = one({ effect: "pulse", scale: 1.05, durationMs: 500 });
  assert.match(pulse, /presetID="26" presetClass="emph"/);
  assert.match(pulse, /<p:cBhvr tmFilter="0,0; \.2,\.5; \.8,\.5; 1,0">/);
  assert.match(pulse, /<p:cTn id="\d+" dur="250" fill="hold" autoRev="1"\/>/);
  assert.match(pulse, /<p:by x="105000" y="105000"\/>/);

  // teeter: five rocks summing to zero, chained by per-behavior delays.
  const teeter = one({ effect: "teeter", rotateDeg: 5, durationMs: 1000 });
  assert.match(teeter, /presetID="32" presetClass="emph"/);
  const rots = [...teeter.matchAll(/<p:animRot by="(-?\d+)">/g)].map((m) => Number(m[1]));
  assert.deepEqual(rots, [300000, -600000, 600000, -600000, 300000]);
  assert.equal(rots.reduce((a, b) => a + b, 0), 0);
  const rockDelays = [...teeter.matchAll(/<p:animRot[^>]*><p:cBhvr><p:cTn id="\d+" dur="\d+" fill="hold"><p:stCondLst><p:cond delay="(\d+)"\/>/g)].map(
    (m) => m[1],
  );
  assert.deepEqual(rockDelays, ["200", "400", "600", "800"]);
});

test("buildTimingXml: repeat and auto-reverse land on the effect cTn", () => {
  const xml = buildTimingXml(
    [anim([2], { effect: "spin", rotateDeg: 360, durationMs: 500, repeat: 3, autoReverse: true })],
    1920,
    1080,
  );
  assert.match(xml, /presetID="8" presetClass="emph" presetSubtype="0" repeatCount="3000" autoRev="1" fill="hold"/);
});

test("buildTimingXml: after-chain waits out the effective duration", () => {
  const xml = buildTimingXml(
    [
      anim([2], { index: 0, effect: "spin", rotateDeg: 360, durationMs: 500, repeat: 3 }),
      anim([3], { index: 1, trigger: "after" }),
    ],
    1920,
    1080,
  );
  const starts = [...xml.matchAll(/<p:par><p:cTn id="\d+" fill="hold"><p:stCondLst><p:cond delay="(\d+)"\/><\/p:stCondLst><p:childTnLst><p:par><p:cTn id="\d+" presetID/g)].map(
    (m) => m[1],
  );
  assert.deepEqual(starts, ["0", "1500"]);

  // Auto-reverse doubles the wait too: 500 × 2 = 1000.
  const rev = buildTimingXml(
    [
      anim([2], { index: 0, effect: "grow", scale: 1.5, durationMs: 500, autoReverse: true }),
      anim([3], { index: 1, trigger: "after" }),
    ],
    1920,
    1080,
  );
  const revStarts = [...rev.matchAll(/<p:cond delay="(\d+)"\/><\/p:stCondLst><p:childTnLst><p:par><p:cTn id="\d+" presetID/g)].map((m) => m[1]);
  assert.deepEqual(revStarts, ["0", "1000"]);
});

// Every effect once (plus repeat/multi-shape variants): ids stay unique and
// the assembled XML is tag-balanced — the two things that trip PowerPoint's
// repair dialog.
test("buildTimingXml: all-effects sweep — unique ids, balanced tags", () => {
  const all: TimingAnim[] = (
    [
      { effect: "appear" },
      { effect: "disappear" },
      { effect: "fade-in" },
      { effect: "fade-out" },
      { effect: "fly-in", dir: "left" },
      { effect: "fly-out", dir: "right" },
      { effect: "wipe-in", dir: "top" },
      { effect: "wipe-out", dir: "bottom" },
      { effect: "float-in", dir: "bottom" },
      { effect: "float-out", dir: "top" },
      { effect: "split-in", dir: "vertical" },
      { effect: "split-out", dir: "horizontal" },
      { effect: "bounce-in" },
      { effect: "bounce-out" },
      { effect: "zoom-in" },
      { effect: "zoom-out" },
      { effect: "wheel-in" },
      { effect: "wheel-out" },
      { effect: "random-bars-in", dir: "horizontal" },
      { effect: "random-bars-out", dir: "vertical" },
      { effect: "spin", rotateDeg: -720, repeat: 2 },
      { effect: "grow", scale: 2 },
      { effect: "shrink", scale: 0.5, autoReverse: true },
      { effect: "pulse", scale: 1.05 },
      { effect: "teeter", rotateDeg: 5, repeat: 3, autoReverse: true },
      { effect: "path", pathSegs: [{ c: "C", p: [1, 2, 3, 4, 5, 6] }] },
    ] as Partial<AnimationDef>[]
  ).map((over, i) =>
    anim(i % 5 === 0 ? [i * 2 + 2, i * 2 + 3] : [i * 2 + 2], {
      index: i,
      trigger: i % 3 === 0 ? "click" : i % 3 === 1 ? "with" : "after",
      ...over,
    }),
  );
  const xml = buildTimingXml(all, 1920, 1080);

  const ids = [...xml.matchAll(/<p:cTn id="(\d+)"/g)].map((m) => m[1]);
  assert.equal(new Set(ids).size, ids.length, "duplicate cTn ids");

  // Tag-balance sweep. The tag regex only matches properly-quoted attributes,
  // so stripping every match and asserting no angle bracket survives also
  // catches malformed/unquoted tags.
  const TAG = /<(\/?)([a-zA-Z:]+)((?:\s+[a-zA-Z:_-]+="[^"]*")*)\s*(\/?)>/g;
  const stack: string[] = [];
  for (const m of xml.matchAll(TAG)) {
    const [, close, name, , selfClose] = m;
    if (selfClose) continue;
    if (close) assert.equal(stack.pop(), name, `mismatched </${name}>`);
    else stack.push(name);
  }
  assert.deepEqual(stack, [], "unclosed tags");
  const residue = xml.replace(TAG, "");
  assert.ok(!/[<>]/.test(residue), `malformed tag near: ${residue.match(/.{0,40}[<>].{0,40}/)?.[0]}`);
});
