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

// Спаны [start, end) всех совпадений паттерна. matchAll на глобальном regex stateless
// (работает с копией, не трогает lastIndex оригинала) — сырое значение наружу не уходит.
function spansOf(text: string, regex: RegExp): Array<[number, number]> {
  const spans: Array<[number, number]> = [];
  for (const m of text.matchAll(regex)) {
    const start = m.index ?? 0;
    spans.push([start, start + m[0].length]);
  }
  return spans;
}

export function scan(text: string, patterns: CompiledPattern[]): ScanResult {
  // Спаны совпадений Класса A — ими дедупим Класс B: B-совпадение,
  // чей спан перекрыт A-совпадением, в Класс B не считаем (двойной учёт одного фрагмента).
  const aSpans: Array<[number, number]> = [];
  for (const p of patterns) {
    if (p.class === 'A') aSpans.push(...spansOf(text, p.regex));
  }

  const findings: Finding[] = [];
  let classBCount = 0;

  for (const p of patterns) {
    const spans = spansOf(text, p.regex);
    if (spans.length === 0) continue;

    if (p.class === 'A') {
      findings.push({ id: p.id, class: 'A', count: spans.length });
      continue;
    }

    // Класс B: оставляем только совпадения, не пересекающиеся ни с одним A-спаном.
    const count = spans.filter(
      ([bStart, bEnd]) => !aSpans.some(([aStart, aEnd]) => bStart < aEnd && aStart < bEnd),
    ).length;
    if (count === 0) continue;

    findings.push({ id: p.id, class: 'B', count });
    classBCount += count;
  }

  return {
    hasSecretA: findings.some((f) => f.class === 'A'),
    findings,
    classBCount,
  };
}
