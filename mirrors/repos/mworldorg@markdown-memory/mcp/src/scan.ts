// Чистая функция скана. НИКОГДА не возвращает сырое значение совпавшего секрета —
// только id паттерна, его класс (A/B) и количество совпадений.

export interface CompiledPattern {
  id: string;
  class: 'A' | 'B';
  regex: RegExp;
}

export interface Finding {
  id: string;
  class: 'A' | 'B';
  count: number;
}

export interface ScanResult {
  hasSecretA: boolean;
  findings: Finding[];
  classBCount: number;
}

export function scan(text: string, patterns: CompiledPattern[]): ScanResult {
  const findings: Finding[] = [];
  let classBCount = 0;

  for (const p of patterns) {
    // String.match с глобальным флагом stateless: вернёт все совпадения, без утечки lastIndex.
    const matches = text.match(p.regex);
    const count = matches ? matches.length : 0;
    if (count === 0) continue;

    findings.push({ id: p.id, class: p.class, count });
    if (p.class === 'B') classBCount += count;
  }

  return {
    hasSecretA: findings.some((f) => f.class === 'A'),
    findings,
    classBCount,
  };
}
