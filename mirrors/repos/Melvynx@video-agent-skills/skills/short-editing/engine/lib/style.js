// Creator style: the look and pace every short of one creator shares (colors, font, paper grain, captions, pace,
// music, mix). Written by the studio-setup skill to a LOCAL <project>/.short-editing/styles/<name>/style.json; `short.mjs init` snapshots it
// into <project>/source/style.json, so changing the profile later never restyles a finished short.
// Layer order: engine defaults < style < spec. A spec value always wins. A project without source/style.json
// renders exactly as before (legacy shorts are never touched).
// Pure module: used by short.mjs (node), audio.mjs and the browser runtime.

const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
const rgb = h => { h = String(h).replace('#', ''); if (h.length === 3) h = h.replace(/./g, '$&$&'); return [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16)); };
const hexOf = a => '#' + a.map(v => Math.round(clamp(v, 0, 255)).toString(16).padStart(2, '0')).join('').toUpperCase();
const lum = h => { const [r, g, b] = rgb(h).map(v => v / 255); return .2126 * r + .7152 * g + .0722 * b; };
export const mixHex = (a, b, p) => { const x = rgb(a), y = rgb(b); return hexOf(x.map((v, i) => v + (y[i] - v) * p)); };
export const isHex = h => /^#?([0-9a-f]{3}|[0-9a-f]{6})$/i.test(String(h || ''));
// relative luminance (WCAG), to check that ink reads on the paper and white reads on the accent
export const luminance = h => { const [r, g, b] = rgb(h).map(v => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; }); return .2126 * r + .7152 * g + .0722 * b; };
export const contrast = (a, b) => { const x = luminance(a), y = luminance(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); };

// style.colors = {paper, ink, accent} (any other kit.js C key can be pinned too: sheet, ink2, ink3, line, dim, accent2,
// tint). The rest is derived so the whole kit (sheets, hairlines, grays, the accent's dark and tint) stays coherent.
// Derived from the defaults it gives back the original palette within a few levels.
export function palette(c = {}) {
  const paper = c.paper || '#F1EEE6', ink = c.ink || '#14161B', accent = c.accent || '#258EFF';
  const sheet = c.sheet || mixHex(paper, '#FFFFFF', .78);
  return {
    paper, sheet, ink, blue: accent,
    ink2: c.ink2 || mixHex(ink, paper, .3),
    ink3: c.ink3 || mixHex(ink, paper, .62),
    line: c.line || mixHex(paper, ink, .065),
    dim: c.dim || mixHex(paper, ink, .11),
    blue2: c.accent2 || mixHex(accent, '#000000', .16),
    tint: c.tint || mixHex(sheet, accent, .11),
    // text on an accent fill: ink on a light accent (yellow), white on a dark one (blue)
    onBlue: c.onAccent || (lum(accent) > .55 ? ink : '#FFFFFF'),
    // second fill color for labels (k: 'label', bg: 'pop'), e.g. the podcast violet; defaults to ink
    pop: c.pop || ink,
  };
}

// The caption looks (same order as the capStyles scene, which cycles the first 20). 'sticker' is the default per-word paper
// sticker; 'clean' is the white sentence-case pill of the clean look (sized by captions.size directly, 40-44).
// 'rise' and 'hard' follow the spoken word (runtime.js): the word being said sits on an accent block.
//   rise: white words with a soft shadow (ink on the paper), the block blurs in, sharp in ~.15 s, then fades out in place (DM Sans 900)
//   hard: ink words with a paper outline, the block is a flat rect with a hard ink shadow (Bricolage Grotesque 800)
// 'stack' (nico-slowdown, runtime.js stackCaption) switches with the layout. Full camera or paper alone: the chunk builds
// word by word into a centered stack, small bold words flowing on a line, the key word (captions.emph, else the longest
// content word) alone on its own line, huge, uppercase, condensed (Archivo 900). Split: one word at a time, regular
// weight, accent text on a tight white label straddling the camera's top edge.
// 'band' (justyn-ai, runtime.js bandCaption): the whole line on one flat block (captions.bg, default ink), words in
// captions.font, white (captions.color), emphasised words in captions.hi (default the tint). No motion: hard in, hard out.
// captions.bg 'none' (aiwithremy): no block, the words sit on the video with a soft shadow (captions.shadow false = none).
// 'dim' (speedy-devv, runtime.js dimCaption, appended last so numeric indexes stay put): the phrase builds word by word,
// spoken words in captions.color (grey, captions.dimWeight 500), the word being said in captions.hi (white) at
// captions.weight, an emphasised word keeps a dark pill (captions.pill, default #2B2B2B) once said; each word blurs in.
export const CAPTION_STYLES = ['sticker', 'pill', 'box', 'caps', 'karaoke', 'underline', 'serif', 'chip', 'highlight', 'outline',
  'punch', 'light', 'split', 'tiles', 'tilted', 'typing', 'accent', 'stacked', 'brackets', 'bar', 'clean', 'rise', 'hard', 'stack', 'band', 'dim'];
// default family and weight per word-block look (captions.font / captions.weight override them)
export const CAPTION_FONTS = { rise: ['DM Sans', 900], hard: ['Bricolage Grotesque', 800] };
export const captionStyleIndex = s => {
  if (s == null || s === '') return 0;
  if (typeof s === 'number') return clamp(Math.round(s) - 1, 0, CAPTION_STYLES.length - 1);   // 1-based, like the "Style 07 / 20" counter
  const i = CAPTION_STYLES.indexOf(String(s).toLowerCase()); return i < 0 ? 0 : i;
};

// subscribe button words when the profile only gives a name (any other language: write cta.button / done in the profile)
const CTA = { fr: { sub: 'Plus de vidéos', button: "S'abonner", done: 'Abonné' }, en: { sub: 'More videos', button: 'Subscribe', done: 'Subscribed' },
  es: { sub: 'Más vídeos', button: 'Suscribirse', done: 'Suscrito' }, pt: { sub: 'Mais vídeos', button: 'Inscrever-se', done: 'Inscrito' },
  de: { sub: 'Mehr Videos', button: 'Abonnieren', done: 'Abonniert' }, it: { sub: 'Altri video', button: 'Iscriviti', done: 'Iscritto' } };
export const ctaDefaults = lang => CTA[String(lang || 'fr').slice(0, 2).toLowerCase()] || CTA.en;

// Long-form sound (format youtube): the shorts profile's sfx never applies. Only paper slides, tweet shutters and the
// quiet marker, at most one hit every 20 s (about 3 per minute), SFX bus at -36 LUFS. A spec.sfx / spec.mix key still
// wins. YouTube comments on the Mistral video (2026-10-08): "j'en peux plus des tings", "les clochettes c'est fini",
// "ding dong, flush, slide": it had 17 hits per minute with bells and blips.
export const LONG_SFX = { appear: 'slide', accents: 0, marker: .4, swish: 0, only: ['slide', 'shutter', 'marker'], minGap: 20 };

// style -> spec defaults. Only keys the spec leaves out are filled; objects merge one level deep (spec keys win).
export function withStyle(spec, st) {
  if (!spec || !st) return spec;
  const o = { ...spec }, under = (k, v) => { if (v && typeof v === 'object') o[k] = { ...v, ...(spec[k] || {}) }; };
  if (spec.speed == null && st.pace?.speed != null) o.speed = st.pace.speed;
  under('tighten', st.pace?.tighten);
  under('captions', st.captions);
  under('music', st.music);
  under('mix', st.mix);
  under('zoom', st.zoom);   // zoom.drift: the slow push per shot (runtime.js)
  if (spec.format === 'youtube') { o.sfx = { ...LONG_SFX, ...(spec.sfx || {}) }; o.mix = { ...(st.mix || {}), sfx: -36, ...(spec.mix || {}) }; }
  else under('sfx', st.sfx);
  under('layout', st.layout);   // layout.card: the fixed camera card of the clean look (runtime.js)
  under('header', st.header);   // header: brand top left + tagline top right, drawn on every frame of a card layout
  under('display', st.display);   // display: the big-text look (kit.js D): counters and big numbers family, flat or embossed
  if (spec.grade == null && st.grade != null) o.grade = st.grade;
  if (spec.cuts == null && st.cuts != null) o.cuts = st.cuts;   // cuts: 'hard' = boards, cutouts and B-roll in and out in one frame (runtime.js)   // camera colour grade, baked at prepare (short.mjs)
  // creator: {name, lang, cta: {sub, button, done}} fills the CTA card text a cta scene leaves out
  const cr = st.creator, cta = cr && Object.fromEntries(Object.entries({ name: cr.name, ...ctaDefaults(cr.lang), ...(cr.cta || {}) }).filter(([, v]) => v != null && v !== ''));
  if (cta && Array.isArray(spec.scenes)) o.scenes = spec.scenes.map(s => s?.type === 'cta' ? { ...cta, ...s } : s);
  return o;
}

// style -> kit.setTheme() input (browser)
export const themeOf = st => ({
  colors: st?.colors ? palette(st.colors) : null,
  font: st?.font?.family || null,
  grain: st?.paper?.grain ?? null,
  tooth: st?.paper?.tooth ?? null,
  toothCell: st?.paper?.toothCell ?? null,
  waves: st?.paper?.waves ?? null,
  mottle: st?.paper?.mottle ?? null,
  depth: st?.paper?.depth ?? null,
  logos: st?.paper?.logos ?? null,
  bg: st?.paper?.bg ?? null,
  dots: st?.paper?.dots ?? null,
  shadow: st?.paper?.shadow ?? null,
});
