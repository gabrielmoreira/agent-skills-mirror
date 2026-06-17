# mm-mcp — локальный MCP-сервер mm-системы

Локальный **stdio** MCP-сервер (TypeScript, [`@modelcontextprotocol/sdk`](https://github.com/modelcontextprotocol/typescript-sdk) `1.29.0`). Отдаёт два инструмента — `mm_secret_scan` и `mm_health` — доступных локальным агентам: **Claude Code**, **Claude Desktop**, **Antigravity** и любому MCP-клиенту, умеющему запускать stdio-сервер.

Имя сервера в доках и примерах регистрации — **`mm-mcp`** (совпадает с `new McpServer({ name: 'mm-mcp' })` в `src/index.ts` и `name` в `package.json`).

> Зависимости (из `package.json`): `@modelcontextprotocol/sdk` `1.29.0`, `gray-matter` `^4.0.3`, `zod` `^4`. Node `>=18`.

---

## Инструменты

### `mm_secret_scan` — детерминированный скан текста на секреты

Прогоняет переданный текст по канону паттернов из [`config/secret-patterns.json`](../config/secret-patterns.json) — **единый источник истины** для всех путей скана mm.

| | |
|---|---|
| **Вход** | `{ text: string }` |
| **Выход** (`structuredContent`) | `{ hasSecretA: boolean, findings: [{ id, class, count }], classBCount: number }` |

- **Сырое значение секрета НЕ возвращается** — только `id` паттерна, его класс (`A`/`B`) и количество совпадений.
- **Класс A** — высокоточные секреты (низкий FP → считается реальным секретом). **Класс B** — широкие / warn-only (git SHA, UUID, base64 — высокий FP, только предупреждение). Подробнее о классах и списке паттернов — в [`docs/SECRET-PATTERNS.md`](../docs/SECRET-PATTERNS.md) (паттерны и regex здесь не дублируются — канон в json).
- Текстовый `content` — краткая сводка (`🔒 секретов не найдено` либо перечисление классов и счётчиков).

**Интеграция:** этот инструмент — приоритетный путь скана для mm-скиллов; когда он недоступен в сессии, скиллы применяют те же паттерны из того же json напрямую (fallback). Политика реакции на находки зависит от скилла и **здесь не дублируется** — для `mm-save-session` это «средний путь» (hard-stop → показать → маскировка только по явному подтверждению → ре-скан → push), описанный в [`skills/mm-save-session/SKILL.md`](../skills/mm-save-session/SKILL.md), Шаг 5.7. Сводная таблица политик по скиллам — в [`docs/SECRET-PATTERNS.md`](../docs/SECRET-PATTERNS.md).

### `mm_health` — read-only проверки здоровья mm-системы

Детерминированный движок проверок. **Ничего не чинит и не пишет** — возвращает только факты. Суждение и авто-фиксы — в скилле `mm-doctor`.

| | |
|---|---|
| **Вход** | `{ projectRoot?: string }` |
| **Выход** (`structuredContent`) | `{ checks: [{ id, status, detail }], summary: { ok, warn, fail, na } }` |

Группы проверок:

- **config** — загрузка `mm-config`, overlay `mm-config.local.json`, наличие ключевых путей.
- **junctions** — проводка `~/.claude/skills/<name>` → каталоги `skills/mm*` и `vendor/*` репозитория.
- **vault-git** — резолв vault и его git-состояние (репо/origin). *Требует `projectRoot`.*
- **passport/gsd** — наличие и консистентность `passport.md` (frontmatter, `gsd_version` ↔ `.planning/`/`.gsd/`). *Требует `projectRoot`.*

Без `projectRoot` группы **config** и **junctions** работают всегда; **vault-git** и **passport/gsd** помечаются статусом `na`.

Статусы: `ok` · `warn` · `fail` · `na`. `summary` — счётчики по каждому статусу.

---

## Сборка

```bash
cd mcp
npm install
npm run build
```

`npm run build` (= `tsc`) компилирует `src/` → `dist/`. Точка входа — `dist/index.js`.

---

## Регистрация в Claude Code

Локальный stdio-сервер регистрируется по абсолютному пути к собранному `dist/index.js`:

```bash
claude mcp add --transport stdio mm-mcp -- node "<абсолютный путь к репо>/mcp/dist/index.js"
```

Пример (этот репозиторий на Windows):

```bash
claude mcp add --transport stdio mm-mcp -- node "C:/Users/louise/Desktop/louise-skills/mcp/dist/index.js"
```

Заметки:

- **stdio-инструменты подхватываются только в НОВОЙ сессии** — после регистрации перезапусти Claude Code (или начни новый чат).
- Проверка регистрации: `claude mcp get mm-mcp`.
- Инструменты появятся под именами `mcp__mm-mcp__mm_secret_scan` и `mcp__mm-mcp__mm_health` (префикс зависит от клиента).

---

## Scope

- **Phase 1 — только локальный stdio.** Сервер запускается локальным агентом и читает локальные файлы репозитория (`config/secret-patterns.json`, `mm-config`, junction-ссылки, `passport.md`, vault).
- **Удалённый / HTTP / VPS — отложено.** Удалённый сервер не имеет доступа к локальным файлам пользователя, поэтому из веб-интерфейса claude.ai этот сервер **недоступен** — только из локальных агентов (Claude Code / Desktop / Antigravity).

---

## Тесты

```bash
npm run smoke         # smoke-тест mm_secret_scan (scripts/smoke.mjs)
npm run health-smoke  # smoke-тест mm_health    (scripts/health-smoke.mjs)
```

Дополнительно — интерактивная отладка через MCP Inspector: `npm run inspect`.
