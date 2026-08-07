#!/usr/bin/env node
// novel-characters — deterministic helpers for the novel-characters skill.
// Zero dependencies on purpose: the skill must work in any directory
// without an npm install. Node 18+ (stdlib only).

import { existsSync, mkdirSync, readdirSync, readFileSync, realpathSync, writeFileSync } from 'node:fs';
import { basename, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

/* ------------------------------------------------------------------ */
/* chunk                                                               */
/* ------------------------------------------------------------------ */

export const CHUNK_SIZE = 14_000;
export const CHUNK_OVERLAP = 600;
export const MAX_CHUNKS = 24;

/**
 * Split source text on paragraph boundaries into overlapping chunks.
 * Overlap keeps a character introduced at a chunk seam visible to both sides.
 */
export function chunkText(text) {
  const clean = text.replace(/\r\n/g, '\n').trim();
  if (!clean) return [];
  if (clean.length <= CHUNK_SIZE) return [clean];

  const chunks = [];
  let cursor = 0;

  while (cursor < clean.length && chunks.length < MAX_CHUNKS) {
    let end = Math.min(cursor + CHUNK_SIZE, clean.length);

    if (end < clean.length) {
      // Prefer a paragraph break, then a sentence end, inside the last 20%.
      const windowStart = cursor + Math.floor(CHUNK_SIZE * 0.8);
      const window = clean.slice(windowStart, end);
      const para = window.lastIndexOf('\n\n');
      const sentence = Math.max(
        window.lastIndexOf('。'),
        window.lastIndexOf('！'),
        window.lastIndexOf('？'),
        window.lastIndexOf('. '),
      );
      const offset = para >= 0 ? para : sentence;
      if (offset >= 0) end = windowStart + offset + 1;
    }

    chunks.push(clean.slice(cursor, end).trim());
    if (end >= clean.length) break;
    cursor = Math.max(end - CHUNK_OVERLAP, cursor + 1);
  }

  return chunks;
}

/* ------------------------------------------------------------------ */
/* merge                                                               */
/* ------------------------------------------------------------------ */

/**
 * Merge per-chunk rosters into one cast, keyed by name AND alias so that
 * 陆行远 / 陆 / 姑娘 collapse onto the same person regardless of which
 * chunk saw which form first.
 */
export function mergeRoster(batches) {
  const byKey = new Map();
  const keyOf = (s) => String(s).trim().toLowerCase();

  for (const batch of batches) {
    for (const entry of batch ?? []) {
      if (!entry?.name) continue;
      const aliases = Array.isArray(entry.aliases) ? entry.aliases : [];
      const candidates = [entry.name, ...aliases].map(keyOf).filter(Boolean);
      const existingKey = candidates.find((c) => byKey.has(c));
      const target = existingKey
        ? byKey.get(existingKey)
        : { name: String(entry.name).trim(), aliases: [], notes: [], quotes: [] };

      for (const alias of [entry.name, ...aliases]) {
        const trimmed = String(alias).trim();
        if (trimmed && trimmed !== target.name && !target.aliases.includes(trimmed)) {
          target.aliases.push(trimmed);
        }
      }
      if (entry.note && String(entry.note).trim()) target.notes.push(String(entry.note).trim());
      for (const quote of entry.quotes ?? []) {
        const trimmed = String(quote).trim();
        if (trimmed && !target.quotes.includes(trimmed)) target.quotes.push(trimmed);
      }

      for (const c of candidates) byKey.set(c, target);
    }
  }

  // Collapse the alias-keyed index back to one entry per character.
  const unique = new Map();
  for (const value of byKey.values()) unique.set(keyOf(value.name), value);
  // More chunks mentioning a character == more screen time.
  return [...unique.values()].sort((a, b) => b.notes.length - a.notes.length);
}

/* ------------------------------------------------------------------ */
/* slug                                                                */
/* ------------------------------------------------------------------ */

/** Filesystem-safe stem for a character name, CJK preserved. */
export function slug(name) {
  const cleaned = String(name)
    .trim()
    .replace(/[\s/\\:*?"<>|]+/g, '-')
    .replace(/^-+|-+$/g, '');
  return cleaned || 'character';
}

/* ------------------------------------------------------------------ */
/* validate                                                            */
/* ------------------------------------------------------------------ */

const IMPORTANCE = ['protagonist', 'major', 'supporting', 'minor'];
const CJK = /[㐀-鿿぀-ヿ가-힯]/;

const PERSONA_STRINGS = ['gender', 'ageRange', 'identity', 'appearance', 'temperament', 'motivation', 'arc'];
const IMAGE_STRINGS = ['style', 'prompt', 'promptZh', 'negativePrompt'];
const VOICE_STRINGS = ['timbre', 'pitch', 'pace', 'accent', 'emotion', 'prompt', 'promptZh', 'referenceHint'];
/** These must read as Chinese — the model drifts to English without a check. */
const VOICE_MUST_BE_ZH = ['timbre', 'pitch', 'pace', 'accent', 'emotion', 'referenceHint'];
/** These go to image models, which choke on CJK and bias on names. */
const IMAGE_MUST_BE_EN = ['prompt', 'negativePrompt', 'turnaround'];

const normalise = (s) => String(s).replace(/\s+/g, '');

export function validateCast(characters, sourceText) {
  const problems = [];
  const flatSource = sourceText === null ? null : normalise(sourceText);
  const at = (name, msg) => problems.push(`[${name}] ${msg}`);

  if (!Array.isArray(characters) || characters.length === 0) {
    return ['cast 为空或不是数组'];
  }

  for (const c of characters) {
    const name = c?.name ?? '(无名)';

    // --- structure ---
    if (typeof c?.name !== 'string' || !c.name.trim()) at(name, '缺少 name');
    if (!Array.isArray(c?.aliases)) at(name, 'aliases 必须是数组');
    if (!IMPORTANCE.includes(c?.importance)) {
      at(name, `importance 必须是 ${IMPORTANCE.join('/')}，实际是 ${JSON.stringify(c?.importance)}`);
    }
    if (typeof c?.oneLiner !== 'string' || !c.oneLiner.trim()) at(name, '缺少 oneLiner');

    const persona = c?.persona;
    if (!persona || typeof persona !== 'object') {
      at(name, '缺少 persona');
    } else {
      for (const f of PERSONA_STRINGS) {
        if (typeof persona[f] !== 'string' || !persona[f].trim()) at(name, `persona.${f} 缺失或为空`);
      }
      if (!Array.isArray(persona.personality)) at(name, 'persona.personality 必须是数组');
      if (!Array.isArray(persona.relationships)) at(name, 'persona.relationships 必须是数组');
      if (!Array.isArray(persona.evidence)) at(name, 'persona.evidence 必须是数组');
    }

    const image = c?.image;
    if (!image || typeof image !== 'object') {
      at(name, '缺少 image');
    } else {
      for (const f of IMAGE_STRINGS) {
        if (typeof image[f] !== 'string' || !image[f].trim()) at(name, `image.${f} 缺失或为空`);
      }
      if (typeof image.turnaround !== 'string' || !image.turnaround.trim()) {
        at(name, 'image.turnaround 缺失或为空（三视图提示词）');
      }
      if (!Array.isArray(image.tags)) at(name, 'image.tags 必须是数组');
    }

    const voice = c?.voice;
    if (!voice || typeof voice !== 'object') {
      at(name, '缺少 voice');
    } else {
      for (const f of VOICE_STRINGS) {
        if (typeof voice[f] !== 'string' || !voice[f].trim()) at(name, `voice.${f} 缺失或为空`);
      }
    }

    // --- evidence must be verbatim ---
    if (flatSource && Array.isArray(persona?.evidence)) {
      for (const quote of persona.evidence) {
        if (typeof quote !== 'string') {
          at(name, 'persona.evidence 里有非字符串');
        } else if (!flatSource.includes(normalise(quote))) {
          at(name, `引文不是原文逐字片段：${quote}`);
        }
      }
    }

    // --- no name leakage into image prompts ---
    if (image) {
      const names = [c?.name, ...(Array.isArray(c?.aliases) ? c.aliases : [])].filter(
        (n) => typeof n === 'string' && n.trim(),
      );
      for (const field of ['prompt', 'promptZh', 'turnaround']) {
        const value = image[field];
        if (typeof value !== 'string') continue;
        for (const n of names) {
          if (value.includes(n)) at(name, `image.${field} 里出现了人名「${n}」`);
        }
      }
    }

    // --- language split ---
    if (voice) {
      for (const f of VOICE_MUST_BE_ZH) {
        const v = voice[f];
        if (typeof v === 'string' && v.trim() && !CJK.test(v)) {
          at(name, `voice.${f} 应为中文，实际是「${v}」`);
        }
      }
    }
    if (image) {
      for (const f of IMAGE_MUST_BE_EN) {
        const v = image[f];
        if (typeof v === 'string' && CJK.test(v)) {
          at(name, `image.${f} 应为英文，但含中日韩字符`);
        }
      }
      if (Array.isArray(image.tags)) {
        for (const t of image.tags) {
          if (typeof t === 'string' && CJK.test(t)) at(name, `image.tags 应为英文，但「${t}」含中日韩字符`);
        }
      }
    }
  }

  return problems;
}

/* ------------------------------------------------------------------ */
/* render — markdown                                                   */
/* ------------------------------------------------------------------ */

const IMPORTANCE_LABEL = {
  protagonist: '主角',
  major: '主要角色',
  supporting: '配角',
  minor: '龙套',
};

export function renderMarkdown(characters, source, summary = '') {
  const out = [
    `# ${source} — 角色表`,
    '',
    `共 ${characters.length} 位角色：${characters.map((c) => c.name).join('、')}`,
    '',
  ];
  if (summary) out.push('## 故事摘要', '', summary, '');

  for (const c of characters) {
    const { persona, image, voice } = c;
    out.push('---', '');
    out.push(`## ${c.name}${c.aliases.length ? `（${c.aliases.join('、')}）` : ''}`, '');
    out.push(`> ${IMPORTANCE_LABEL[c.importance] ?? c.importance} · ${c.oneLiner}`, '');

    if (c.turnaroundImage) out.push(`![${c.name} 三视图](${c.turnaroundImage})`, '');

    out.push('### 人物画像', '');
    out.push(`- **性别**：${persona.gender}`);
    out.push(`- **年龄**：${persona.ageRange}`);
    out.push(`- **身份**：${persona.identity}`);
    if (persona.personality.length) out.push(`- **性格**：${persona.personality.join(' / ')}`);
    out.push('');
    out.push(`**外貌**　${persona.appearance}`, '');
    out.push(`**性情**　${persona.temperament}`, '');
    out.push(`**动机**　${persona.motivation}`, '');
    out.push(`**人物弧光**　${persona.arc}`, '');

    if (persona.relationships.length) {
      out.push('**关系**', '');
      for (const r of persona.relationships) out.push(`- ${r.name} — ${r.relation}`);
      out.push('');
    }
    if (persona.evidence.length) {
      out.push('**原文依据**', '');
      for (const q of persona.evidence) out.push(`> ${q}`, '');
    }

    out.push('### 卡通形象提示词', '');
    out.push(`**风格**　${image.style}`, '');
    if (image.tags.length) out.push(`**标签**　\`${image.tags.join('`, `')}\``, '');
    out.push('```text', image.prompt, '```', '');
    out.push(`中文：${image.promptZh}`, '');
    out.push('**Negative prompt**', '', '```text', image.negativePrompt, '```', '');
    out.push('**三视图 prompt**', '', '```text', image.turnaround, '```', '');

    out.push('### 音色提示词', '');
    out.push(`- **音色**：${voice.timbre}`);
    out.push(`- **音高**：${voice.pitch}`);
    out.push(`- **语速**：${voice.pace}`);
    out.push(`- **口音**：${voice.accent}`);
    out.push(`- **情绪**：${voice.emotion}`);
    out.push(`- **类比**：${voice.referenceHint}`, '');
    out.push('```text', voice.prompt, '```', '');
    out.push(`中文：${voice.promptZh}`, '');
  }

  return out.join('\n');
}

/* ------------------------------------------------------------------ */
/* render — html                                                       */
/* ------------------------------------------------------------------ */
/*
 * 设计约定见 references/report-style.md。三条不能破的：
 *   1. 双字域：宋体=书本原文，黑体=模型分析，等宽=喂给机器的提示词
 *   2. 不藏内容——没有页签、没有折叠，整页可以 Cmd+F
 *   3. 「（推断）」自动高亮，让读者一眼分清有据和补全
 */

const esc = (s) =>
  String(s ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');

/**
 * 把推断标记包起来——这是本报告的签名细节，不是装饰。
 * 半角/全角括号 × 推断/inferred 四种写法都要认：提示词虽然规定了写法，
 * 但模型实际会四种都产出，渲染器不能挑食。
 */
const INFERRED = /（\s*(?:推断|inferred)[^）]*）|\(\s*(?:推断|inferred)[^)]*\)/gi;
const marked = (s) => esc(s).replace(INFERRED, (m) => `<span class="inf">${m}</span>`);

const IMPORTANCE_ORDER = ['protagonist', 'major', 'supporting', 'minor'];

/** 一段提示词 + 它自己的复制按钮。 */
const promptBlock = (label, value, cls = 'mono') =>
  !value
    ? ''
    : `<div class="pb">
<div class="pb-h"><span class="pb-l">${esc(label)}</span><button class="copy" data-copy="${esc(value)}">复制</button></div>
<p class="${cls}">${esc(value)}</p>
</div>`;

const row = (label, value) =>
  !value ? '' : `<div class="row"><dt>${esc(label)}</dt><dd>${marked(value)}</dd></div>`;

const para = (label, body) =>
  !body ? '' : `<div class="para"><h4>${esc(label)}</h4><p>${marked(body)}</p></div>`;

function renderEntry(c, index) {
  const { persona, image, voice } = c;
  const rank = String(index + 1).padStart(2, '0');
  const id = `p-${slug(c.name)}`;

  const shot = c.turnaroundImage
    ? `<a class="plate" href="${esc(c.turnaroundImage)}" target="_blank" rel="noopener">
         <img src="${esc(c.turnaroundImage)}" alt="${esc(c.name)}的三视图设定" loading="lazy">
         <span class="plate-c">正视 · 侧视 · 背视</span>
       </a>`
    : `<div class="plate plate-empty"><span>尚未出图<br><em>用下方三视图提示词生成</em></span></div>`;

  return `<article class="entry" id="${id}">
  <header class="entry-h">
    <span class="rank">${rank}</span>
    <h2 class="name">${esc(c.name)}</h2>
    <span class="tag tag-${esc(c.importance)}">${esc(IMPORTANCE_LABEL[c.importance] ?? c.importance)}</span>
    ${c.aliases.length ? `<span class="aka">又称 ${esc(c.aliases.join(' · '))}</span>` : ''}
  </header>
  <p class="oneliner">${marked(c.oneLiner)}</p>

  ${shot}

  <div class="groups">
    <section class="group">
      <h3 class="group-h">画像</h3>
      <dl class="rows">
        ${row('性别', persona.gender)}${row('年龄', persona.ageRange)}${row('身份', persona.identity)}
      </dl>
      ${persona.personality.length ? `<ul class="traits">${persona.personality.map((t) => `<li>${esc(t)}</li>`).join('')}</ul>` : ''}
      ${para('外貌', persona.appearance)}
      ${para('性情', persona.temperament)}
      ${para('动机', persona.motivation)}
      ${para('人物弧光', persona.arc)}
      ${
        persona.relationships.length
          ? `<div class="para"><h4>关系</h4><dl class="rows">${persona.relationships
              .map((r) => `<div class="row"><dt>${esc(r.name)}</dt><dd>${marked(r.relation)}</dd></div>`)
              .join('')}</dl></div>`
          : ''
      }
      ${
        persona.evidence.length
          ? `<div class="source">
               <h4>原文依据</h4>
               ${persona.evidence.map((q) => `<blockquote>${esc(q)}</blockquote>`).join('')}
             </div>`
          : ''
      }
    </section>

    <section class="group">
      <h3 class="group-h">形象</h3>
      ${row('画风', image.style)}
      ${
        image.tags.length
          ? `<div class="tagrow"><ul class="tags">${image.tags.map((t) => `<li>${esc(t)}</li>`).join('')}</ul><button class="copy" data-copy="${esc(image.tags.join(', '))}">复制标签</button></div>`
          : ''
      }
      ${promptBlock('出图提示词 EN', image.prompt)}
      ${promptBlock('出图提示词 中文', image.promptZh, 'zh')}
      ${promptBlock('反向提示词', image.negativePrompt)}
      ${promptBlock('三视图提示词 EN', image.turnaround)}
    </section>

    <section class="group">
      <h3 class="group-h">声音</h3>
      <dl class="rows">
        ${row('音色', voice.timbre)}${row('音高', voice.pitch)}${row('语速', voice.pace)}
        ${row('口音', voice.accent)}${row('情绪', voice.emotion)}${row('类比', voice.referenceHint)}
      </dl>
      ${promptBlock('音色提示词 EN', voice.prompt)}
      ${promptBlock('音色提示词 中文', voice.promptZh, 'zh')}
      <div class="entry-f">
        <button class="copy" data-copy="${esc(JSON.stringify(c, null, 2))}">复制整份角色 JSON</button>
      </div>
    </section>
  </div>
</article>`;
}

export function renderHtml(characters, source, summary = '') {
  const shot = characters.filter((c) => c.turnaroundImage).length;
  const ordered = [...characters].sort(
    (a, b) => IMPORTANCE_ORDER.indexOf(a.importance) - IMPORTANCE_ORDER.indexOf(b.importance),
  );

  const index = ordered
    .map(
      (c, i) => `<li style="--i:${i}">
        <a href="#p-${slug(c.name)}">
          <span class="ix-n">${String(i + 1).padStart(2, '0')}</span>
          <span class="ix-name">${esc(c.name)}</span>
          <span class="ix-rule"></span>
          <span class="ix-tag">${esc(IMPORTANCE_LABEL[c.importance] ?? c.importance)}</span>
        </a></li>`,
    )
    .join('');

  return `<!doctype html>
<html lang="zh-CN"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(source)} · 角色设定集</title>
<style>
/* 冷灰印张 + 铁锈红印记。红色只用在与原文有关的地方。 */
:root{
  --paper:#e9eae5; --panel:#e1e3dd; --ink:#191d21; --ink-2:#5b636a; --ink-3:#8c9298;
  --rule:#cdd0c9; --seal:#8a3324; --seal-soft:#8a332412;
  --serif:"Songti SC","STSong","Source Han Serif SC","Noto Serif CJK SC",Georgia,serif;
  --sans:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",system-ui,-apple-system,sans-serif;
  --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
}
@media(prefers-color-scheme:dark){
  :root{
    --paper:#14171a; --panel:#1c2024; --ink:#e6e8e4; --ink-2:#9aa1a7; --ink-3:#6d757c;
    --rule:#2c3237; --seal:#c96a4f; --seal-soft:#c96a4f16;
  }
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.75 var(--sans);
  -webkit-font-smoothing:antialiased}
.wrap{max-width:1800px;margin:0 auto;padding:clamp(32px,5vw,64px) clamp(20px,3vw,40px) 96px}

/* ---- 头 ---- */
.masthead{border-bottom:2px solid var(--ink);padding-bottom:20px;margin-bottom:8px}
.eyebrow{font:500 11px/1 var(--sans);letter-spacing:.28em;text-transform:uppercase;color:var(--ink-3);margin:0 0 14px}
.title{font:400 clamp(34px,6vw,58px)/1.1 var(--serif);margin:0;letter-spacing:.02em}
.title em{font-style:normal;color:var(--ink-3)}
.meta{margin:14px 0 0;font-size:13px;color:var(--ink-2)}
.meta b{font-weight:500;color:var(--ink)}

/* ---- 目录：戏份排序，序号是排名不是装饰 ---- */
.index{margin:0;padding:0;list-style:none}
.index li{border-bottom:1px solid var(--rule);animation:rise .5s both;animation-delay:calc(var(--i)*45ms)}
.index a{display:flex;align-items:baseline;gap:14px;padding:11px 2px;text-decoration:none;color:inherit}
.index a:hover .ix-name{color:var(--seal)}
.ix-n{font:500 11px/1 var(--mono);color:var(--ink-3);width:20px;flex:none}
.ix-name{font:400 21px/1.2 var(--serif);letter-spacing:.03em;transition:color .15s}
.ix-rule{flex:1;border-bottom:1px dotted var(--rule);transform:translateY(-4px)}
.ix-tag{font-size:12px;color:var(--ink-2);flex:none}
@keyframes rise{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}

/* ---- 摘要 + 目录并排，把 1800px 的宽度用起来 ---- */
.brief{display:grid;gap:40px;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);
  align-items:start;margin-top:28px}
@media(max-width:1100px){.brief{grid-template-columns:1fr;gap:24px}}

/* 摘要说的是故事本身，用叙事字域 */
.synopsis{padding:22px 26px;background:var(--panel);border:1px solid var(--rule);
  border-radius:2px;border-left:2px solid var(--ink)}
.synopsis h2{font:500 11px/1 var(--sans);letter-spacing:.28em;color:var(--ink-3);margin:0 0 10px}
.synopsis p{margin:0;font:400 clamp(15px,1.1vw,16.5px)/1.95 var(--serif)}

/* ---- 角色墙：一排最多三个 ----
   minmax 下限 460px 配 1800px 上限，天然卡在三列：
   3×460+2×28=1436 装得下，4×460+3×28=1924 装不下。 */
.cast{display:grid;gap:28px;grid-template-columns:repeat(auto-fit,minmax(460px,1fr));
  align-items:start;margin-top:40px}

/* ---- 条目 ---- */
.entry{border:1px solid var(--rule);border-radius:2px;background:var(--panel);
  padding:24px;scroll-margin-top:24px}
.entry-h{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
.rank{font:500 12px/1 var(--mono);color:var(--ink-3)}
.name{font:400 clamp(28px,4vw,38px)/1.15 var(--serif);margin:0;letter-spacing:.04em}
.tag{font-size:12px;padding:2px 9px;border:1px solid var(--rule);border-radius:2px;color:var(--ink-2)}
.tag-protagonist{border-color:var(--seal);color:var(--seal)}
.aka{font-size:13px;color:var(--ink-3)}
.oneliner{font:400 clamp(16px,2vw,18px)/1.7 var(--serif);color:var(--ink-2);margin:12px 0 28px;max-width:62ch}

/* ---- 三视图 ---- */
/* 三视图是白底的印张，深色模式下也保持白底——它是一张纸，不是 UI 面板 */
.plate{display:block;position:relative;background:#fff;border:1px solid var(--rule);
  border-radius:2px;overflow:hidden;margin-bottom:36px}
.plate-empty{background:var(--panel)}
.plate img{display:block;width:100%;height:auto}
.plate-c{position:absolute;left:0;bottom:0;background:var(--paper);border-top:1px solid var(--rule);
  border-right:1px solid var(--rule);padding:5px 12px;font:500 11px/1 var(--sans);
  letter-spacing:.18em;color:var(--ink-2)}
.plate-empty{display:grid;place-items:center;min-height:180px;text-align:center;color:var(--ink-3);font-size:13px}
.plate-empty em{font-style:normal;font-size:12px;color:var(--ink-3);opacity:.75}

/* ---- 卡内三组竖排：画像 → 形象 → 声音 ---- */
.groups{display:block}
.group{margin-top:30px}
.group:first-child{margin-top:0}
.group-h{font:500 11px/1 var(--sans);letter-spacing:.28em;text-transform:uppercase;color:var(--ink-3);
  margin:0 0 16px;padding-bottom:8px;border-bottom:1px solid var(--rule)}
.rows{margin:0 0 16px}
.row{display:flex;gap:14px;padding:3px 0;font-size:14px}
.row dt{color:var(--ink-3);flex:none;min-width:46px}
.row dd{margin:0}
.traits{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 18px;padding:0;list-style:none}
.traits li{border:1px solid var(--rule);border-radius:2px;padding:2px 9px;font-size:13px}
.para{margin-bottom:18px}
.para h4,.source h4{font:500 11px/1 var(--sans);letter-spacing:.2em;color:var(--ink-3);margin:0 0 6px}
.para p{margin:0;font-size:14px;line-height:1.8}

/* ---- 签名：推断标记 ---- */
.inf{color:var(--ink-3);font-size:.88em;background:var(--seal-soft);padding:0 3px;border-radius:2px}

/* ---- 原文：宋体，铁锈红边栏。这里是书自己在说话 ---- */
.source{border-left:2px solid var(--seal);padding-left:16px;margin-top:22px}
.source blockquote{margin:0 0 10px;font:400 15px/1.85 var(--serif);color:var(--ink)}
.source blockquote:last-child{margin-bottom:0}
.source blockquote::before{content:"「";color:var(--seal)}
.source blockquote::after{content:"」";color:var(--seal)}

/* ---- 提示词：等宽，机器的输入 ---- */
.tagrow{display:flex;justify-content:space-between;align-items:flex-start;gap:10px;margin-bottom:18px}
.tags{display:flex;flex-wrap:wrap;gap:6px;margin:0;padding:0;list-style:none}
.tags li{font:400 12px/1.5 var(--mono);color:var(--ink-2);border:1px solid var(--rule);
  border-radius:2px;padding:1px 7px}
.pb{border:1px solid var(--rule);border-radius:2px;background:var(--paper);margin-bottom:14px}
.pb-h{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:7px 11px;
  border-bottom:1px solid var(--rule)}
.pb-l{font:500 10px/1 var(--sans);letter-spacing:.2em;text-transform:uppercase;color:var(--ink-3)}
.pb p{margin:0;padding:11px;white-space:pre-wrap;word-break:break-word}
.pb .mono{font:400 12.5px/1.7 var(--mono)}
.pb .zh{font:400 14px/1.8 var(--sans)}

.copy{flex:none;font:500 11px/1 var(--sans);color:var(--ink-2);background:transparent;
  border:1px solid var(--rule);border-radius:2px;padding:4px 10px;cursor:pointer;transition:.15s}
.copy:hover{border-color:var(--seal);color:var(--seal)}
.copy:focus-visible{outline:2px solid var(--seal);outline-offset:2px}
.copy[data-done]{border-color:var(--seal);color:var(--seal)}
.entry-f{margin-top:20px;padding-top:16px;border-top:1px solid var(--rule)}
.entry-f .copy{width:100%;padding:9px}

.colophon{margin-top:72px;padding-top:20px;border-top:2px solid var(--ink);
  font-size:12px;color:var(--ink-3);display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}

@media(max-width:640px){
  .cast{gap:20px;grid-template-columns:1fr}
  .entry{padding:18px}
  .index a{gap:10px}
  .ix-name{font-size:18px}
}
@media(prefers-reduced-motion:reduce){
  *{animation:none!important;transition:none!important}
  html{scroll-behavior:auto}
}
@media print{
  .copy,.index{display:none}
  .entry{page-break-inside:avoid;border-top:1px solid #000}
  body{background:#fff}
}
</style></head><body>
<div class="wrap">

<header class="masthead">
  <p class="eyebrow">角色设定集</p>
  <h1 class="title">${esc(source)}<em> · 角色</em></h1>
  <p class="meta"><b>${characters.length}</b> 位角色${shot ? ` · <b>${shot}</b> 张三视图` : ''} · 按戏份排序</p>
</header>

<div class="brief">
${summary ? `<section class="synopsis"><h2>故事摘要</h2><p>${marked(summary)}</p></section>` : ''}
<nav aria-label="角色索引"><ol class="index">${index}</ol></nav>
</div>

<div class="cast">
${ordered.map(renderEntry).join('\n')}
</div>

<footer class="colophon">
  <span>画像与提示词由模型依据原文生成，<span class="inf">（推断）</span>标记处为原文未明说、为可用性补全的内容。</span>
  <span>novel-characters</span>
</footer>

</div>
<script>
document.addEventListener('click', async (e) => {
  const btn = e.target.closest('.copy');
  if (!btn) return;
  try {
    await navigator.clipboard.writeText(btn.dataset.copy);
    const label = btn.textContent;
    btn.textContent = '已复制';
    btn.dataset.done = '1';
    setTimeout(() => { btn.textContent = label; delete btn.dataset.done; }, 1600);
  } catch {
    btn.textContent = '复制失败';
    setTimeout(() => { btn.textContent = '复制'; }, 1600);
  }
});
</script>
</body></html>`;
}

/* ------------------------------------------------------------------ */
/* CLI                                                                 */
/* ------------------------------------------------------------------ */

const USAGE = `novel-characters.mjs — novel-characters skill 的确定性工具

  chunk <book.txt> <workdir>       段落感知重叠切块，写 chunk-NN.txt，打印块数
  merge <workdir>                  归并 roster-*.json，打印 cast JSON
  validate <cast.json> <book.txt>  校验；有违规逐条打印并 exit 1
  render <cast.json> [--html|--md] 渲染报告到 stdout（默认 --md）
  slug <name>                      角色名转安全文件名

render 选项：
  --source <name>   报告标题用的书名（默认取 cast.json 的 source 或文件名）
  --images <dir>    图片目录名，默认 images；会去找 <dir>/<slug>-turnaround.png`;

function readJson(path) {
  return JSON.parse(readFileSync(resolve(path), 'utf8'));
}

/** cast.json 可以是 {source, summary, characters}，也可以是裸数组（旧格式）。 */
function loadCast(path) {
  const raw = readJson(path);
  const characters = Array.isArray(raw) ? raw : raw.characters;
  if (!Array.isArray(characters)) throw new Error(`${path} 里没有 characters 数组`);
  return {
    characters,
    source: Array.isArray(raw) ? null : raw.source,
    summary: Array.isArray(raw) ? '' : (raw.summary ?? ''),
  };
}

function main(argv) {
  const [cmd, ...rest] = argv;

  if (!cmd || cmd === '-h' || cmd === '--help') {
    console.log(USAGE);
    process.exit(cmd ? 0 : 1);
  }

  if (cmd === 'chunk') {
    const [book, workdir] = rest;
    if (!book || !workdir) throw new Error('用法：chunk <book.txt> <workdir>');
    const text = readFileSync(resolve(book), 'utf8');
    const chunks = chunkText(text);
    mkdirSync(resolve(workdir), { recursive: true });
    chunks.forEach((c, i) => {
      writeFileSync(join(resolve(workdir), `chunk-${String(i).padStart(2, '0')}.txt`), c, 'utf8');
    });
    const truncated = chunks.length >= MAX_CHUNKS && text.length > CHUNK_SIZE * MAX_CHUNKS;
    console.log(
      JSON.stringify(
        { chunks: chunks.length, chars: text.length, workdir: resolve(workdir), truncated },
        null,
        2,
      ),
    );
    if (truncated) console.error(`⚠️ 文本超过 ${MAX_CHUNKS} 块上限，尾部未扫描`);
    return;
  }

  if (cmd === 'merge') {
    const [workdir] = rest;
    if (!workdir) throw new Error('用法：merge <workdir>');
    const dir = resolve(workdir);
    const files = readdirSync(dir).filter((f) => /^roster-.*\.json$/.test(f)).sort();
    if (!files.length) throw new Error(`${dir} 里没有 roster-*.json`);
    const batches = files.map((f) => {
      const raw = readJson(join(dir, f));
      return Array.isArray(raw) ? raw : (raw.characters ?? []);
    });
    console.log(JSON.stringify(mergeRoster(batches), null, 2));
    return;
  }

  if (cmd === 'validate') {
    const [castPath, bookPath] = rest;
    if (!castPath) throw new Error('用法：validate <cast.json> <book.txt>');
    const { characters, summary } = loadCast(castPath);
    const source = bookPath ? readFileSync(resolve(bookPath), 'utf8') : null;
    if (!bookPath) console.error('⚠️ 没给原文，跳过逐字引文校验');
    const problems = validateCast(characters, source);
    // 顶层的故事摘要——报告要用，缺了就没法在顶部交代背景
    if (typeof summary !== 'string' || !summary.trim()) {
      problems.unshift('顶层缺少 summary（故事摘要），报告顶部会空着');
    }
    if (problems.length) {
      console.error(`✗ ${problems.length} 处违规：\n`);
      for (const p of problems) console.error('  ' + p);
      process.exit(1);
    }
    console.log(`✓ ${characters.length} 个角色全部通过校验`);
    return;
  }

  if (cmd === 'render') {
    const [castPath] = rest;
    if (!castPath) throw new Error('用法：render <cast.json> [--html|--md]');
    const html = rest.includes('--html');
    const imagesDir = rest.includes('--images') ? rest[rest.indexOf('--images') + 1] : 'images';
    const sourceFlag = rest.includes('--source') ? rest[rest.indexOf('--source') + 1] : null;

    const { characters, source, summary } = loadCast(castPath);
    const title = sourceFlag ?? source ?? basename(castPath).replace(/\.[^.]+$/, '');

    // Attach turnaround images when the files actually exist next to the report.
    const outDir = resolve(castPath, '..');
    for (const c of characters) {
      const rel = `${imagesDir}/${slug(c.name)}-turnaround.png`;
      if (existsSync(join(outDir, rel))) c.turnaroundImage = rel;
    }

    process.stdout.write(
      (html ? renderHtml(characters, title, summary) : renderMarkdown(characters, title, summary)) +
        '\n',
    );
    return;
  }

  if (cmd === 'slug') {
    if (!rest[0]) throw new Error('用法：slug <name>');
    console.log(slug(rest[0]));
    return;
  }

  throw new Error(`未知命令 ${cmd}\n\n${USAGE}`);
}

// 只有直接运行才跑 CLI —— selftest.mjs 需要 import 这些函数。
// 两边都取 realpath：软链安装时 argv[1] 是链接路径，而 import.meta.url
// 已被 Node 解析成真实路径，不归一化就永远不相等。
function isMainModule() {
  if (!process.argv[1]) return false;
  try {
    return realpathSync(process.argv[1]) === realpathSync(fileURLToPath(import.meta.url));
  } catch {
    return false;
  }
}

if (isMainModule()) {
  try {
    main(process.argv.slice(2));
  } catch (error) {
    console.error(error instanceof Error ? error.message : error);
    process.exit(1);
  }
}
