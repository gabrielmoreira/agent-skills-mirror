# AGENTS.md — Temporal dispatch allow-list (для корпоративного агента)

Этот файл — инструкция агенту, работающему в **корпоративном форке** gortex, по
сопровождению распознавания Temporal-диспатча под ваш кодовой базы. Цель: повышать точность
графа Temporal **без утечки корпоративных имён** в исходники / upstream.

> Не путать с `docs/agents.md` (это про agent-адаптеры самого gortex). Здесь — только про
> Temporal allow-list и LLM-клининг.

---

## 1. Как устроено распознавание (три слоя)

Имя активности/воркфлоу в `workflow.ExecuteActivity(ctx, <name>, …)` часто приходит не литералом.
Форк распознаёт его тремя слоями, по возрастанию доверия:

1. **Generic-эвристика (recall, скрыто).** Любой хелпер с `env` в имени —
   `cfg.ActivityFromEnv("KEY", "Default")` — распознаётся структурно: 2-й строковый аргумент
   берётся как дефолтное имя. Ребро садится на **speculative 0.4** (`temporal_env_source=heuristic`),
   скрыто из обычных запросов. Вести ничего не нужно — работает само.
2. **Allow-list (precision, видимо).** Если имя хелпера в built-in списке (`GetEnvOrDefault`,
   `GetEnvOrDefaultValue`, `EnvOr`, `GetenvDefault`, `GetEnvDefault`) **или** в вашем
   репо-локальном allow-list — ребро повышается до **inferred 0.6**, видимо по умолчанию
   (`temporal_env_source=allowlist`). `os.Getenv(...)` / `cmp.Or(...)` тоже → 0.6.
3. **LLM-клининг (опционально).** Проход `gortex analyze --kind temporal_verify` отдаёт каждое
   рёбро уровня ≤0.65 вашей LLM, заземляя в реальном коде: confirmed → повышает и делает видимым,
   rejected → гасит (скрывает), uncertain → оставляет как есть. Register-confirmed (0.9) не трогает.

**Главное:** слой 1 жадный и безвредный (скрыт), слой 2 точечно повышает, слой 3 чистит. Поэтому
**не обязательно** перечислять все хелперы — список нужен лишь чтобы **сделать конкретный хелпер
видимым по умолчанию**.

---

## 2. Как вести allow-list

Файл **git-ignored** (см. `.gitignore`: `.gortex/`), читается **только** под env-гейтом.

1. Включить гейт: `export GORTEX_ALLOW_LOCAL_TEMPORAL=1`.
2. Создать `.gortex/temporal-allowlist.yaml` в корне репозитория:

```yaml
# Имена ваших env-хелперов, по которым диспатч резолвится на дефолт.
# Сопоставление по имени функции (без пакета), регистронезависимо.
env_helpers:
  - GetActivityNameFromEnv
  - FetchActivityName
  - resolveActivity            # локальные/lowercase тоже годятся
```

3. Проверить эффект: `gortex analyze --kind temporal_orphans --path . --format json` (до/после) —
   часть `broken_dispatch` должна закрыться, env-сайты получить `temporal_env_source=allowlist`.

Что добавлять / чего нет:

- **Добавлять:** имена функций-обёрток «прочитать env и вернуть дефолт». Это generic-инфраструктура,
  не бизнес-данные.
- **НЕ добавлять:** имена активностей/воркфлоу/бизнес-логику. Они тут не нужны (распознаются
  структурно), и им не место даже в git-ignored файле.

---

## 3. Протокол анонимизации (не спалить корпоративное)

- Файл `.gortex/temporal-allowlist.yaml` **git-ignored** — не коммить его и не добавлять в PR.
- Имена env-хелперов сами по себе — generic infra (безопасны), но всё равно держим их **только** в
  локальном файле, а не в исходниках форка.
- Если делаешь фикстуры для передачи OSS-стороне — следуй
  `docs/temporal-compare/temporal-gap-synthetic-fixtures.md` (протокол: «сохраняем форму, стираем
  содержание»): repo-пути → `example.com/app`, имена активностей → `ChargeActivity`, env-ключи →
  `FOO_ACTIVITY_ENV`, тела → выкинуть.

---

## 4. LLM-клининг (precision-проход вашей моделью)

Требует настроенного `llm.provider` (например ваш `custom-provider`) в `.gortex.yaml` /
`~/.config/gortex/config.yaml`.

```bash
gortex analyze --kind temporal_verify --path . --format json
```

- Проверяет **только** низкодоверенные рёбра (speculative 0.4 + inferred 0.6) — набор маленький,
  стоимость ограничена. Register-confirmed 0.9 не трогает.
- Вердикты кэшируются в git-ignored `.gortex/temporal-verify-cache.json` по хэшу
  (модель + имя + исходник вызова + исходник кандидата) → повторный прогон детерминирован и
  бесплатен (годится для CI). Меняется код или модель — кэш промахивается и перепроверяет.
- Вывод: `checked / confirmed / rejected / uncertain / errors` (+ `details` в JSON с причинами).
- На каждом ребре остаются `temporal_llm_verdict` и `temporal_llm_reason` для аудита.

---

## 5. Что делать с тем, что всё ещё не резолвится

Для dispatch-шейпов, остающихся `broken_dispatch` и не закрытых ничем выше, —
`docs/temporal-compare/temporal-gap-synthetic-fixtures.md`: какие минимальные анонимизированные
фикстуры отдать OSS-стороне, чтобы дорезолвить либу.
