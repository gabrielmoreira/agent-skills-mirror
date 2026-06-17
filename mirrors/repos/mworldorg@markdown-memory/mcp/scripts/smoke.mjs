// Неинтерактивный смок-тест собранного скана. Exit 1 при любом провале.
// Запуск: node scripts/smoke.mjs (после npm run build).
import assert from 'node:assert/strict';
import { scan } from '../dist/scan.js';
import { loadPatterns } from '../dist/patterns.js';

const patterns = loadPatterns();

// Все фикстуры заведомо фейковые, подобраны под реально портированные regex.
const TG_HASH = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ012345678'; // ровно 35 символов [A-Za-z0-9_-]
const TG_TOKEN = `123456789:${TG_HASH}`; // формат telegram: цифры + ':' + 35 символов
const GIT_SHA = 'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0'; // 40 hex (буквы+цифры)
const CLEAN = 'The quick brown fox jumps over the lazy dog by the river.';

let failed = 0;
function check(name, fn) {
  try {
    fn();
    console.log(`  ok   ${name}`);
  } catch (e) {
    failed++;
    console.error(`  FAIL ${name}: ${e.message}`);
  }
}

// 1. Fake telegram-токен → Класс A, telegram-token присутствует.
check('telegram token → Класс A', () => {
  const r = scan(TG_TOKEN, patterns);
  assert.equal(r.hasSecretA, true, 'ожидался hasSecretA=true');
  assert.ok(
    r.findings.some((f) => f.id === 'telegram-token' && f.class === 'A'),
    'ожидался finding telegram-token в Класс A',
  );
});

// 2. git SHA-40 → Класс B (warn), НЕ Класс A.
check('git SHA-40 → Класс B, не A', () => {
  const r = scan(GIT_SHA, patterns);
  assert.equal(r.hasSecretA, false, 'git SHA не должен попадать в Класс A');
  assert.ok(r.classBCount > 0, 'ожидался classBCount > 0');
  assert.ok(
    r.findings.every((f) => f.class === 'B'),
    'все находки по git SHA должны быть Класс B',
  );
});

// 2b. Дедуп: telegram-токен (Класс A) + git SHA-40 (Класс B) → Класс B считает ТОЛЬКО SHA.
// Хвост токена (35-символьный хэш) сам попадает под широкий Класс B, но перекрыт A-спаном → не учитывается.
check('дедуп: telegram + git SHA → classBCount=1 (только SHA)', () => {
  const r = scan(`${TG_TOKEN} ${GIT_SHA}`, patterns);
  assert.equal(r.hasSecretA, true, 'ожидался hasSecretA=true (telegram-token)');
  assert.equal(
    r.classBCount,
    1,
    `Класс B должен считать только SHA (хвост токена перекрыт A), получено ${r.classBCount}`,
  );
});

// 3. Чистый текст → findings пусто, hasSecretA false.
check('чистый текст → пусто', () => {
  const r = scan(CLEAN, patterns);
  assert.equal(r.findings.length, 0, 'findings должны быть пусты');
  assert.equal(r.hasSecretA, false, 'hasSecretA должен быть false');
  assert.equal(r.classBCount, 0, 'classBCount должен быть 0');
});

// 4. Сырое значение секрета ОТСУТСТВУЕТ в JSON-выводе функции.
check('нет утечки сырого секрета', () => {
  const out = JSON.stringify(scan(TG_TOKEN, patterns));
  assert.ok(!out.includes(TG_TOKEN), 'сырой токен не должен попадать в вывод');
  assert.ok(!out.includes(TG_HASH), 'сырой хэш не должен попадать в вывод');
});

if (failed > 0) {
  console.error(`\n✗ smoke: ${failed} провал(ов)`);
  process.exit(1);
}
console.log('\n✓ smoke: 5/5 ассертов пройдены');
