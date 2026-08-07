#!/usr/bin/env node
// 自测：覆盖 novel-characters.mjs 里所有确定性逻辑。
// 不调用任何模型，不花额度，跑一次 < 1 秒。
//   node scripts/selftest.mjs

import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { CHUNK_SIZE, MAX_CHUNKS, chunkText, mergeRoster, renderHtml, renderMarkdown, slug, validateCast } from './novel-characters.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const examples = join(here, '..', 'examples');
const SOURCE = readFileSync(join(examples, '渡口.txt'), 'utf8');
const CAST = JSON.parse(readFileSync(join(examples, '渡口-cast.json'), 'utf8')).characters;

let passed = 0;
function ok(condition, label) {
  assert.ok(condition, label);
  passed += 1;
}
function eq(actual, expected, label) {
  assert.equal(actual, expected, `${label} — 期望 ${expected}，实际 ${actual}`);
  passed += 1;
}

/* ---------------- chunkText ---------------- */

eq(chunkText('').length, 0, '空文本不产生块');
eq(chunkText('   \n  ').length, 0, '纯空白不产生块');
eq(chunkText(SOURCE).length, 1, '短故事只有一块');

const long = SOURCE.repeat(40);
const chunks = chunkText(long);
ok(chunks.length > 1, '长文本会切成多块');
ok(chunks.every((c) => c.length <= CHUNK_SIZE), `没有块超过 CHUNK_SIZE(${CHUNK_SIZE})`);
ok(long.includes(chunks[0].slice(0, 200)), '块内容来自原文');
// 相邻块必须重叠，否则卡在切口上的角色会两边都漏
ok(chunks[1].includes(chunks[0].slice(-100).slice(0, 40)), '相邻块有重叠');
// 覆盖率：把所有块拼起来（去重叠后）应该盖住绝大部分原文
const covered = chunks.reduce((sum, c) => sum + c.length, 0);
ok(covered >= long.length, '所有块加起来覆盖全文（含重叠）');

const huge = SOURCE.repeat(500);
ok(chunkText(huge).length <= MAX_CHUNKS, `超长文本被 MAX_CHUNKS(${MAX_CHUNKS}) 截断而不是无限切`);

/* ---------------- mergeRoster ---------------- */

// 跨块用不同称呼发现同一个人，必须收敛成一条
const merged = mergeRoster([
  [{ name: '陆行远', aliases: ['陆'], note: '瘦，颧骨高。', quotes: ['他的脸很瘦，颧骨很高'] }],
  [{ name: '陆', aliases: [], note: '眉骨有疤。', quotes: ['右边眉骨上有一道两寸长的旧疤。', '他的脸很瘦，颧骨很高'] }],
  [{ name: '沈知微', aliases: ['姑娘'], note: '两条辫子。', quotes: [] }],
]);
eq(merged.length, 2, '别名跨块归并');
const lu = merged.find((c) => c.name === '陆行远');
ok(lu, '保留出现次数最多的规范名');
eq(lu.notes.length, 2, 'notes 累加');
ok(lu.aliases.includes('陆'), '别名被记录');
eq(lu.quotes.length, 2, 'quotes 合并且去重');

// 先看到别名、后看到本名，也要能合并
const reverse = mergeRoster([
  [{ name: '姑娘', aliases: [], note: 'a', quotes: [] }],
  [{ name: '沈知微', aliases: ['姑娘'], note: 'b', quotes: [] }],
]);
eq(reverse.length, 1, '别名先出现也能归并');
eq(reverse[0].notes.length, 2, '归并后两条 note 都在');

eq(
  mergeRoster([[{ name: 'Ishmael', aliases: [], note: 'a', quotes: [] }], [{ name: 'ishmael', aliases: [], note: 'b', quotes: [] }]]).length,
  1,
  '拉丁名大小写不敏感',
);

// 出现的块数越多排越前 —— 这是戏份权重的唯一依据
const ranked = mergeRoster([
  [{ name: '甲', aliases: [], note: '1', quotes: [] }, { name: '乙', aliases: [], note: '1', quotes: [] }],
  [{ name: '乙', aliases: [], note: '2', quotes: [] }],
  [{ name: '乙', aliases: [], note: '3', quotes: [] }],
]);
eq(ranked[0].name, '乙', '按出现块数降序排列');

// 脏数据不能让整个流程崩掉
eq(mergeRoster([[]]).length, 0, '空批次不报错');
eq(mergeRoster([[{ name: '甲' }]]).length, 1, '缺 aliases/notes/quotes 字段也能处理');
eq(mergeRoster([[{ note: '没名字' }]]).length, 0, '没有 name 的条目被丢弃');

/* ---------------- slug ---------------- */

eq(slug('胡二爷'), '胡二爷', '中文名原样保留');
eq(slug('a/b:c*d'), 'a-b-c-d', '路径危险字符被替换');
eq(slug('  x  '), 'x', '两端空白被去掉');
eq(slug(''), 'character', '空名有兜底');

/* ---------------- validateCast ---------------- */

eq(validateCast(CAST, SOURCE).length, 0, '自带样例通过全部校验');
ok(validateCast([], SOURCE).length > 0, '空 cast 报错');

const clone = () => JSON.parse(JSON.stringify(CAST));
const hits = (cast, keyword) => validateCast(cast, SOURCE).filter((p) => p.includes(keyword)).length;

// 这四类是模型真实犯过的错，每一类都必须抓住
let bad = clone();
bad[0].persona.evidence[0] = 'She was nineteen years old.';
ok(hits(bad, '逐字片段') > 0, '抓住意译的引文');

bad = clone();
bad[0].image.prompt = `${bad[0].name}, ${bad[0].image.prompt}`;
ok(hits(bad, '人名') > 0, '抓住出图提示词里的人名');

bad = clone();
bad[0].image.promptZh = `${bad[0].aliases[0]}的设定图`;
ok(hits(bad, '人名') > 0, '抓住中文出图提示词里的别名');

bad = clone();
bad[0].voice.timbre = 'warm husky alto';
ok(hits(bad, '应为中文') > 0, '抓住该中文却写成英文的字段');

bad = clone();
bad[0].image.turnaround = '中文三视图描述';
ok(hits(bad, '应为英文') > 0, '抓住该英文却含中文的字段');

bad = clone();
bad[0].importance = 'sidekick';
ok(hits(bad, 'importance') > 0, '抓住 importance 枚举越界');

bad = clone();
delete bad[0].image.turnaround;
ok(hits(bad, 'turnaround') > 0, '抓住缺失的三视图提示词');

bad = clone();
delete bad[0].persona;
ok(hits(bad, 'persona') > 0, '抓住缺失的 persona');

// 没有原文时应该跳过逐字校验而不是全判失败
eq(validateCast(CAST, null).length, 0, '不给原文时跳过引文校验');

/* ---------------- render ---------------- */

const md = renderMarkdown(CAST, '渡口');
ok(md.includes('# 渡口 — 角色表'), 'Markdown 有标题');
for (const c of CAST) ok(md.includes(`## ${c.name}`), `Markdown 包含 ${c.name}`);
ok(md.includes('三视图 prompt'), 'Markdown 含三视图提示词');

const html = renderHtml(CAST, '渡口');
ok(html.startsWith('<!doctype html>'), 'HTML 是完整文档');
eq((html.match(/class="entry"/g) || []).length, CAST.length, `HTML 有 ${CAST.length} 个条目`);
// 每人 8 个复制按钮：标签 + 4 段出图 + 2 段音色 + 整份 JSON
eq((html.match(/class="copy"/g) || []).length, CAST.length * 8, '每段提示词都有复制按钮');
ok(html.includes('<nav aria-label="角色索引"'), '有角色索引');
eq((html.match(/class="ix-name"/g) || []).length, CAST.length, '索引列出全部角色');
ok(html.includes('<blockquote>'), '原文依据用 blockquote');
// 四种写法都要认：半角/全角 × 推断/inferred
for (const marker of ['（推断）', '(inferred)', '（inferred）', '(推断)']) {
  const t = clone();
  t[0].persona.appearance = '身形单薄' + marker + '。';
  ok(renderHtml(t, 'x').includes('class="inf"'), `推断标记 ${marker} 被高亮`);
}
ok(html.includes('prefers-reduced-motion'), '尊重减少动效');
ok(html.includes('@media print'), '可打印');
// 自包含：不能有任何外部请求
ok(!/<script\s+src=/.test(html), 'HTML 不引用外部脚本');
ok(!/<link\s/.test(html), 'HTML 不引用外部样式');
// 反向验证：上面两条正则本身要真的能抓到东西，否则是永远为真的假测试
ok(/<script\s+src=/.test('<script src="x.js">'), '外部脚本检测正则有效');
ok(/<link\s/.test('<link rel="stylesheet">'), '外部样式检测正则有效');
ok(!/@import|url\(https?:/.test(html), 'CSS 不拉外部资源');

// 没有三视图时要有占位而不是空白
ok(renderHtml(CAST, 'x').includes('plate-empty'), '缺图时显示占位');
const withShot = clone();
withShot[0].turnaroundImage = 'images/x.png';
ok(renderHtml(withShot, 'x').includes('<img src="images/x.png"'), '有图时嵌入');

// XSS：角色数据是模型生成的，不能直接拼进 HTML
const evil = clone();
evil[0].name = '<img src=x onerror=alert(1)>';
const evilHtml = renderHtml(evil, 'x');
ok(!evilHtml.includes('<img src=x onerror'), '角色字段里的 HTML 被转义');

// 故事摘要
const DOC = JSON.parse(readFileSync(join(examples, '渡口-cast.json'), 'utf8'));
ok(DOC.summary && DOC.summary.trim(), '样例带故事摘要');
ok(renderHtml(CAST, '渡口', DOC.summary).includes('class="synopsis"'), 'HTML 顶部渲染摘要');
ok(!renderHtml(CAST, '渡口', '').includes('class="synopsis"'), '没有摘要时不留空壳');
ok(renderMarkdown(CAST, '渡口', DOC.summary).includes('## 故事摘要'), 'Markdown 也带摘要');
ok(renderHtml(CAST, '渡口', '<b>x</b>').includes('&lt;b&gt;'), '摘要里的 HTML 被转义');

// 一排最多三个角色：靠 minmax 下限卡住，两个值必须一起改
const css = renderHtml(CAST, 'x');
ok(css.includes('max-width:1800px'), '页面上限 1800px');
ok(/\.cast\{[^}]*minmax\(460px/.test(css), '角色墙用 minmax(460px) 卡三列');
ok(/\.cast\{[^}]*minmax\(460px/.test('.cast{grid-template-columns:repeat(auto-fit,minmax(460px,1fr))}'), '上面这条正则本身有效');
// 1800 上限、40 内边距、28 间距下，三列装得下、四列装不下
const inner = 1800 - 40 * 2;
ok(3 * 460 + 2 * 28 <= inner, '三列能排下');
ok(4 * 460 + 3 * 28 > inner, '四列排不下——这是「一排最多三个」的机制');
ok(css.includes('.groups{display:block}'), '卡内三组竖排而不是再分栏');

console.log(`✓ ${passed} 项自测全部通过`);
