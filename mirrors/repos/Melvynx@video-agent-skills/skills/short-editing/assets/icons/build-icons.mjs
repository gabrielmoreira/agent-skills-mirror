// House icon set = Google Noto Emoji (Apache 2.0, github.com/googlefonts/noto-emoji), the default icon library everywhere
// (the creator 2026-10-15, after a side-by-side test of Fluent 3D, Noto and Phosphor on the Editing IA Pro VSL).
// Bare color emoji on transparent, never on a tile: <name>.png and glyph/<name>.png are the same 512 px image
// (both paths kept so older specs keep working), svg/<name>.svg is the source.
// The names stay the house names, so specs that use assets/icons/<name>.png or glyph/<name>.png keep working.
// Add an icon: one line in ICONS (house name: Noto name, search https://icon-sets.iconify.design/noto/), then run:
//   cd ../../engine && npm install && node ../assets/icons/build-icons.mjs
// The SVGs come from the Iconify API in one request (it rate-limits per-icon calls) and stay in svg/; delete svg/<name>.svg to fetch it again.
import { chromium } from '../../engine/node_modules/playwright-core/index.mjs';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));

// house name: Noto name
const ICONS = {
  warning: 'warning', skull: 'skull', cross: 'cross-mark', fear: 'fearful-face', tomb: 'headstone', locked: 'locked',
  refund: 'receipt', check: 'check-mark-button', crown: 'crown', rocket: 'rocket', trophy: 'trophy',
  unlocked: 'unlocked', sunrise: 'sunrise', bolt: 'high-voltage', gift: 'wrapped-gift', play: 'clapper-board',
  money: 'euro-banknote', connected: 'electric-plug', arrowdown: 'backhand-index-pointing-down', 'arrow-down': 'backhand-index-pointing-down',
  ant: 'ant', brain: 'brain', bread: 'bread', bulb: 'light-bulb', calendar: 'spiral-calendar', camera: 'movie-camera',
  chat: 'speech-balloon', clock: 'alarm-clock', collision: 'collision', cool: 'smiling-face-with-sunglasses',
  coupon: 'admission-tickets', cursor: 'computer-mouse', elephant: 'elephant', eye: 'eyes', factory: 'factory',
  globe: 'globe-showing-europe-africa', goldfish: 'fish', hook: 'hook', hourglass: 'hourglass-not-done', laptop: 'laptop',
  megaphone: 'megaphone', mic: 'studio-microphone', mountain: 'snow-capped-mountain', palette: 'artist-palette',
  pencil: 'pencil', phone: 'mobile-phone', question: 'red-question-mark', robot: 'robot', scissors: 'scissors',
  script: 'scroll', shield: 'shield', tag: 'label', users: 'busts-in-silhouette', search: 'magnifying-glass-tilted-left',
  folder: 'open-file-folder', file: 'page-facing-up', envelope: 'envelope', heart: 'red-heart', star: 'star',
  timer: 'timer-clock', copy: 'clipboard', code: 'keyboard', ruler: 'straight-ruler', bookmark: 'bookmark',
  wrench: 'wrench', car: 'automobile', tyre: 'wheel',
  house: 'house', server: 'desktop-computer', support: 'technologist', repeat: 'counterclockwise-arrows-button', pin: 'pushpin', link: 'link',
  image: 'framed-picture', music: 'musical-notes', upload: 'outbox-tray', film: 'film-frames', waveform: 'speaker-high-volume',
  // podcast ép. 4 v3 (the creator 2026-10-16: « on utilise les émojis Google maintenant, que ce soit plus clean »): house name = Noto name
  fire: 'fire', 'money-bag': 'money-bag', 'money-with-wings': 'money-with-wings', 'chart-increasing': 'chart-increasing', 'chart-decreasing': 'chart-decreasing', 'bar-chart': 'bar-chart',
  handshake: 'handshake', 'thumbs-up': 'thumbs-up', 'thumbs-down': 'thumbs-down', 'clapping-hands': 'clapping-hands', 'raising-hands': 'raising-hands', 'flexed-biceps': 'flexed-biceps',
  'face-with-tears-of-joy': 'face-with-tears-of-joy', 'rolling-on-the-floor-laughing': 'rolling-on-the-floor-laughing', 'exploding-head': 'exploding-head', 'face-screaming-in-fear': 'face-screaming-in-fear', 'thinking-face': 'thinking-face', 'face-with-monocle': 'face-with-monocle',
  'face-with-symbols-on-mouth': 'face-with-symbols-on-mouth', 'smiling-face-with-heart-eyes': 'smiling-face-with-heart-eyes', 'star-struck': 'star-struck', 'partying-face': 'partying-face', 'pile-of-poo': 'pile-of-poo', ghost: 'ghost',
  alien: 'alien', 'clown-face': 'clown-face', 'nerd-face': 'nerd-face', 'sleeping-face': 'sleeping-face', 'yawning-face': 'yawning-face', 'face-with-rolling-eyes': 'face-with-rolling-eyes',
  'grimacing-face': 'grimacing-face', 'see-no-evil-monkey': 'see-no-evil-monkey', 'shushing-face': 'shushing-face', 'zipper-mouth-face': 'zipper-mouth-face', 'hot-face': 'hot-face', 'cold-face': 'cold-face',
  'woozy-face': 'woozy-face', 'crying-face': 'crying-face', 'loudly-crying-face': 'loudly-crying-face', 'skull-and-crossbones': 'skull-and-crossbones', bomb: 'bomb', sparkles: 'sparkles',
  'hundred-points': 'hundred-points', 'dollar-banknote': 'dollar-banknote', coin: 'coin', 'credit-card': 'credit-card', 'gem-stone': 'gem-stone', 'shopping-cart': 'shopping-cart',
  package: 'package', 'office-building': 'office-building', school: 'school', bank: 'bank', 'classical-building': 'classical-building', briefcase: 'briefcase',
  'crystal-ball': 'crystal-ball', 'magic-wand': 'magic-wand', 'game-die': 'game-die', 'slot-machine': 'slot-machine', 'puzzle-piece': 'puzzle-piece', 'teddy-bear': 'teddy-bear',
  'cat-face': 'cat-face', 'dog-face': 'dog-face', 'pig-face': 'pig-face', 'cow-face': 'cow-face', tractor: 'tractor', seedling: 'seedling',
  sun: 'sun', 'cloud-with-lightning-and-rain': 'cloud-with-lightning-and-rain', tornado: 'tornado', rainbow: 'rainbow', snowflake: 'snowflake', droplet: 'droplet',
  volcano: 'volcano', airplane: 'airplane', 'racing-car': 'racing-car', ambulance: 'ambulance', 'police-car-light': 'police-car-light', construction: 'construction',
  'stop-sign': 'stop-sign', 'no-entry': 'no-entry', prohibited: 'prohibited', gear: 'gear', hammer: 'hammer', 'hammer-and-wrench': 'hammer-and-wrench',
  toolbox: 'toolbox', magnet: 'magnet', 'test-tube': 'test-tube', microscope: 'microscope', 'satellite-antenna': 'satellite-antenna', battery: 'battery',
  'low-battery': 'low-battery', 'floppy-disk': 'floppy-disk', television: 'television', 'video-game': 'video-game', joystick: 'joystick', headphone: 'headphone',
  bell: 'bell', 'bell-with-slash': 'bell-with-slash', loudspeaker: 'loudspeaker', 'muted-speaker': 'muted-speaker', key: 'key', 'old-key': 'old-key',
  door: 'door', bed: 'bed', pill: 'pill', syringe: 'syringe', ear: 'ear', 'man-technologist': 'man-technologist',
  ninja: 'ninja', superhero: 'superhero', detective: 'detective', vampire: 'vampire', mage: 'mage', genie: 'genie',
  ring: 'ring', 'graduation-cap': 'graduation-cap', backpack: 'backpack', books: 'books', notebook: 'notebook', memo: 'memo',
  newspaper: 'newspaper', paperclip: 'paperclip', wastebasket: 'wastebasket', 'file-cabinet': 'file-cabinet', 'inbox-tray': 'inbox-tray', 'e-mail': 'e-mail',
  'incoming-envelope': 'incoming-envelope', 'ballot-box-with-ballot': 'ballot-box-with-ballot', stopwatch: 'stopwatch', 'hourglass-done': 'hourglass-done', 'balance-scale': 'balance-scale', 'sports-medal': 'sports-medal',
  '1st-place-medal': '1st-place-medal', 'flying-saucer': 'flying-saucer', 'crossed-swords': 'crossed-swords', dagger: 'dagger', axe: 'axe', chains: 'chains',
  'red-exclamation-mark': 'red-exclamation-mark', 'double-exclamation-mark': 'double-exclamation-mark', 'exclamation-question-mark': 'exclamation-question-mark', 'thought-balloon': 'thought-balloon', 'right-anger-bubble': 'right-anger-bubble', 'waving-hand': 'waving-hand',
  'ok-hand': 'ok-hand', 'pinched-fingers': 'pinched-fingers', 'victory-hand': 'victory-hand', 'crossed-fingers': 'crossed-fingers', 'index-pointing-up': 'index-pointing-up', 'backhand-index-pointing-right': 'backhand-index-pointing-right',
  'writing-hand': 'writing-hand', 'folded-hands': 'folded-hands', 'palms-up-together': 'palms-up-together', 'person-shrugging': 'person-shrugging', 'person-facepalming': 'person-facepalming', 'person-gesturing-no': 'person-gesturing-no',
  'person-running': 'person-running', 'person-lifting-weights': 'person-lifting-weights', 'speaking-head': 'speaking-head', 'bust-in-silhouette': 'bust-in-silhouette', pizza: 'pizza', hamburger: 'hamburger',
  'french-fries': 'french-fries', sushi: 'sushi', spaghetti: 'spaghetti', croissant: 'croissant', 'birthday-cake': 'birthday-cake', cookie: 'cookie',
  'hot-beverage': 'hot-beverage', 'beer-mug': 'beer-mug', 'clinking-beer-mugs': 'clinking-beer-mugs', 'bottle-with-popping-cork': 'bottle-with-popping-cork', popcorn: 'popcorn', carrot: 'carrot',
  banana: 'banana', 'red-apple': 'red-apple', lemon: 'lemon', 'hot-pepper': 'hot-pepper', 'honey-pot': 'honey-pot', soap: 'soap',
  broom: 'broom', basket: 'basket', bucket: 'bucket', 'fire-extinguisher': 'fire-extinguisher', 'shopping-bags': 'shopping-bags', balloon: 'balloon',
  'party-popper': 'party-popper', fireworks: 'fireworks', 'money-mouth-face': 'money-mouth-face', 'nauseated-face': 'nauseated-face', 'face-with-head-bandage': 'face-with-head-bandage', 'face-with-thermometer': 'face-with-thermometer',
  'face-with-medical-mask': 'face-with-medical-mask', 'cowboy-hat-face': 'cowboy-hat-face', 'disguised-face': 'disguised-face', 'smiling-face-with-horns': 'smiling-face-with-horns', 'angry-face-with-horns': 'angry-face-with-horns', 'anatomical-heart': 'anatomical-heart',
  bone: 'bone', tooth: 'tooth', 'chart-increasing-with-yen': 'chart-increasing-with-yen', goblin: 'goblin', cat: 'cat', dog: 'dog',
  mouse: 'mouse', rat: 'rat', snail: 'snail', turtle: 'turtle', snake: 'snake', dragon: 'dragon',
  unicorn: 'unicorn', monkey: 'monkey', gorilla: 'gorilla', shark: 'shark', octopus: 'octopus', butterfly: 'butterfly',
  spider: 'spider', 't-rex': 't-rex', sauropod: 'sauropod', chicken: 'chicken', 'baby-chick': 'baby-chick', egg: 'egg',
  cooking: 'cooking', moai: 'moai', 'wilted-flower': 'wilted-flower', sunflower: 'sunflower', 'four-leaf-clover': 'four-leaf-clover', cactus: 'cactus',
  'deciduous-tree': 'deciduous-tree', 'evergreen-tree': 'evergreen-tree', 'desert-island': 'desert-island', 'world-map': 'world-map', compass: 'compass', stethoscope: 'stethoscope',
  'adhesive-bandage': 'adhesive-bandage', 'drop-of-blood': 'drop-of-blood', 'broken-heart': 'broken-heart', 'heart-on-fire': 'heart-on-fire', 'sparkling-heart': 'sparkling-heart', lollipop: 'lollipop',
  'chocolate-bar': 'chocolate-bar', doughnut: 'doughnut', ice: 'ice', 'yo-yo': 'yo-yo', kite: 'kite', boomerang: 'boomerang',
  bullseye: 'bullseye', bowling: 'bowling', 'video-camera': 'video-camera', 'camera-with-flash': 'camera-with-flash', 'film-projector': 'film-projector', 'level-slider': 'level-slider',
  'control-knobs': 'control-knobs', radio: 'radio', trumpet: 'trumpet', guitar: 'guitar', drum: 'drum', saxophone: 'saxophone',
  violin: 'violin',
};

for (const d of ['svg', 'glyph']) mkdirSync(join(here, d), { recursive: true });
const svgFile = name => join(here, 'svg', name + '.svg');
const missing = Object.entries(ICONS).filter(([name, noto]) => !existsSync(svgFile(name)) || !readFileSync(svgFile(name), 'utf8').includes(`<!-- noto:${noto} -->`));
if (missing.length) {
  const res = await fetch(`https://api.iconify.design/noto.json?icons=${[...new Set(missing.map(([, n]) => n))].join(',')}`);
  if (!res.ok) throw new Error(`Iconify answered ${res.status}, try again in a few minutes`);
  const set = await res.json();
  for (const [name, noto] of missing) {
    const icon = set.icons?.[noto];
    if (!icon) throw new Error(`no Noto icon "${noto}" for ${name}`);
    const w = icon.width ?? set.width ?? 128, h = icon.height ?? set.height ?? 128;
    writeFileSync(svgFile(name), `<!-- noto:${noto} -->\n<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 ${w} ${h}">${icon.body}</svg>`);
  }
}

// installed Chrome (macOS, Windows, Linux) unless CHROME_PATH points at another Chromium
const browser = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : { channel: 'chrome' });
const page = await browser.newPage({ viewport: { width: 512, height: 512 } });
for (const name of Object.keys(ICONS)) {
  const svg = readFileSync(join(here, 'svg', name + '.svg'), 'utf8');
  await page.setContent(`<html><body style="margin:0;background:transparent"><div class="g" style="width:512px;height:512px">${svg}</div></body></html>`);
  await page.locator('.g').screenshot({ path: join(here, name + '.png'), omitBackground: true });
  writeFileSync(join(here, 'glyph', name + '.png'), readFileSync(join(here, name + '.png')));
}
await browser.close();
console.log(Object.keys(ICONS).length, 'Noto icons ->', here);
