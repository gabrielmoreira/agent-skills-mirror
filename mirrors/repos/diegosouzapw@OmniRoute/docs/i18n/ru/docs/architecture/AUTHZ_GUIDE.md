# Authorization Guide (Русский)

🌐 **Languages:** 🇺🇸 [English](../../../../architecture/AUTHZ_GUIDE.md) · 🇪🇹 [am](../../../am/docs/architecture/AUTHZ_GUIDE.md) · 🇸🇦 [ar](../../../ar/docs/architecture/AUTHZ_GUIDE.md) · 🇦🇿 [az](../../../az/docs/architecture/AUTHZ_GUIDE.md) · 🇧🇬 [bg](../../../bg/docs/architecture/AUTHZ_GUIDE.md) · 🇧🇩 [bn](../../../bn/docs/architecture/AUTHZ_GUIDE.md) · 🇧🇦 [bs](../../../bs/docs/architecture/AUTHZ_GUIDE.md) · 🇨🇿 [cs](../../../cs/docs/architecture/AUTHZ_GUIDE.md) · 🇩🇰 [da](../../../da/docs/architecture/AUTHZ_GUIDE.md) · 🇩🇪 [de](../../../de/docs/architecture/AUTHZ_GUIDE.md) · 🇬🇷 [el](../../../el/docs/architecture/AUTHZ_GUIDE.md) · 🇪🇸 [es](../../../es/docs/architecture/AUTHZ_GUIDE.md) · 🇪🇪 [et](../../../et/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇷 [fa](../../../fa/docs/architecture/AUTHZ_GUIDE.md) · 🇫🇮 [fi](../../../fi/docs/architecture/AUTHZ_GUIDE.md) · 🇫🇷 [fr](../../../fr/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇪 [ga](../../../ga/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [gu](../../../gu/docs/architecture/AUTHZ_GUIDE.md) · 🇳🇬 [ha](../../../ha/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇱 [he](../../../he/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [hi](../../../hi/docs/architecture/AUTHZ_GUIDE.md) · 🇭🇷 [hr](../../../hr/docs/architecture/AUTHZ_GUIDE.md) · 🇭🇺 [hu](../../../hu/docs/architecture/AUTHZ_GUIDE.md) · 🇦🇲 [hy](../../../hy/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇩 [id](../../../id/docs/architecture/AUTHZ_GUIDE.md) · 🇳🇬 [ig](../../../ig/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇹 [it](../../../it/docs/architecture/AUTHZ_GUIDE.md) · 🇯🇵 [ja](../../../ja/docs/architecture/AUTHZ_GUIDE.md) · 🇬🇪 [ka](../../../ka/docs/architecture/AUTHZ_GUIDE.md) · 🇰🇭 [km](../../../km/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [kn](../../../kn/docs/architecture/AUTHZ_GUIDE.md) · 🇰🇷 [ko](../../../ko/docs/architecture/AUTHZ_GUIDE.md) · 🇱🇹 [lt](../../../lt/docs/architecture/AUTHZ_GUIDE.md) · 🇱🇻 [lv](../../../lv/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [ml](../../../ml/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [mr](../../../mr/docs/architecture/AUTHZ_GUIDE.md) · 🇲🇾 [ms](../../../ms/docs/architecture/AUTHZ_GUIDE.md) · 🇲🇹 [mt](../../../mt/docs/architecture/AUTHZ_GUIDE.md) · 🇲🇲 [my](../../../my/docs/architecture/AUTHZ_GUIDE.md) · 🇳🇵 [ne](../../../ne/docs/architecture/AUTHZ_GUIDE.md) · 🇳🇱 [nl](../../../nl/docs/architecture/AUTHZ_GUIDE.md) · 🇳🇴 [no](../../../no/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [or](../../../or/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [pa](../../../pa/docs/architecture/AUTHZ_GUIDE.md) · 🇵🇭 [phi](../../../phi/docs/architecture/AUTHZ_GUIDE.md) · 🇵🇱 [pl](../../../pl/docs/architecture/AUTHZ_GUIDE.md) · 🇵🇹 [pt](../../../pt/docs/architecture/AUTHZ_GUIDE.md) · 🇧🇷 [pt-BR](../../../pt-BR/docs/architecture/AUTHZ_GUIDE.md) · 🇷🇴 [ro](../../../ro/docs/architecture/AUTHZ_GUIDE.md) · 🇱🇰 [si](../../../si/docs/architecture/AUTHZ_GUIDE.md) · 🇸🇰 [sk](../../../sk/docs/architecture/AUTHZ_GUIDE.md) · 🇸🇮 [sl](../../../sl/docs/architecture/AUTHZ_GUIDE.md) · 🇷🇸 [sr](../../../sr/docs/architecture/AUTHZ_GUIDE.md) · 🇸🇪 [sv](../../../sv/docs/architecture/AUTHZ_GUIDE.md) · 🇰🇪 [sw](../../../sw/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [ta](../../../ta/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [te](../../../te/docs/architecture/AUTHZ_GUIDE.md) · 🇹🇭 [th](../../../th/docs/architecture/AUTHZ_GUIDE.md) · 🇹🇷 [tr](../../../tr/docs/architecture/AUTHZ_GUIDE.md) · 🇺🇦 [uk-UA](../../../uk-UA/docs/architecture/AUTHZ_GUIDE.md) · 🇵🇰 [ur](../../../ur/docs/architecture/AUTHZ_GUIDE.md) · 🇺🇿 [uz](../../../uz/docs/architecture/AUTHZ_GUIDE.md) · 🇻🇳 [vi](../../../vi/docs/architecture/AUTHZ_GUIDE.md) · 🇳🇬 [yo](../../../yo/docs/architecture/AUTHZ_GUIDE.md) · 🇨🇳 [zh-CN](../../../zh-CN/docs/architecture/AUTHZ_GUIDE.md) · 🇹🇼 [zh-TW](../../../zh-TW/docs/architecture/AUTHZ_GUIDE.md)

---

> **Источник истины:** `src/server/authz/`, `src/shared/constants/publicApiRoutes.ts`, `src/lib/api/requireManagementAuth.ts`, `src/shared/utils/apiAuth.ts`
> **Последнее обновление:** 2026-09-22 — пространства имен областей указывают на MCP-SERVER.md

OmniRoute имеет конвейер авторизации, учитывающий маршруты, который контролирует каждый API-запрос. Классификация **детерминирована** и **закрыта при сбое** — всё, что не может быть классифицировано, попадает в категорию `MANAGEMENT` и требует сессии или токена уровня управления. Эта страница объясняет модель для инженеров, поддерживающих маршруты или проектирующих новые конечные точки.

![Конвейер AuthZ (3 класса маршрутов + оценка политики)](../diagrams/exported/authz-pipeline.svg)

> Источник: [diagrams/authz-pipeline.mmd](../diagrams/authz-pipeline.mmd)

## Два режима аутентификации

### 1. API-ключ (Bearer)

Используется для клиентских API, совместимых с OpenAI/Anthropic/Gemini, а также для некоторых маршрутов управления, если ключ имеет область доступа `manage`.

```
Authorization: Bearer <api-key>
```

Проверяется функциями `isValidApiKey()` / `extractApiKey()` в `src/sse/services/auth.ts` и повторно экспортируется через `src/shared/utils/apiAuth.ts`. Валидатор также принимает переменные окружения `OMNIROUTE_API_KEY` / `ROUTER_API_KEY` в качестве постоянных сквозных ключей (задача #1350).

### 2. Сессия панели управления (cookie auth_token)

Для страниц панели управления и административных операций.

```
Cookie: auth_token=<JWT, подписанный с помощью JWT_SECRET>
```

Cookie считается сессионным только в том случае, если JWT успешно проходит проверку **и** содержит `authenticated: true`
(`src/shared/utils/dashboardSessionToken.ts` → `verifyDashboardSessionToken`). Каждый
потребитель cookie (защита маршрутов панели управления (`isDashboardSessionAuthenticated()`), обновление в конвейере авторизации, WebSocket-рукопожатие, сервер
данных в реальном времени, `/api/settings/require-login`, `/api/auth/status`) использует этот вспомогательный метод.
Существуют и другие JWT, подписанные с помощью `JWT_SECRET`: механизм сквозной аутентификации Cursor CLI выпускает
для владельцев ключей токены с `iss "omniroute" / aud "cursor-cli"`, и они никогда не считаются сессиями
(#13298).

Проверяется функцией `isDashboardSessionAuthenticated()` в `src/shared/utils/apiAuth.ts`. Конвейер автоматически обновляет JWT, если до конца его 30-дневного срока действия остаётся менее 7 дней.

Сессия также может завершиться до истечения 30 дней, поскольку все механизмы выпуска токенов используют `mintDashboardSessionToken` (со временем выпуска `iat` и идентификатором `jti`), а проверяющий компонент проверяет две настройки: `sessionsValidAfter`, задаваемую при смене пароля, вследствие чего все сессии, выпущенные до этого момента, перестают проходить проверку (браузер, в котором был изменён пароль, получает новый cookie), и `revokedDashboardSessions`, куда `POST /api/auth/logout` добавляет `jti` завершённой сессии. Сессии, созданные более старой версией, не содержат ни одного из этих полей и остаются действительными до первой смены пароля. Если настройки невозможно прочитать, сессия не считается доверенной.

Некоторые маршруты управления принимают **любой** из режимов: cookie ИЛИ `Bearer <key>`, если API-ключ имеет область доступа `manage` (или `admin`). Именно это обеспечивает сценарий «настройка с помощью вызовов API», добавленный в v3.8.

#### Необязательное ограничение входа через OIDC (#6973)

Вход администратора в панель управления также поддерживает **включаемый по желанию** процесс OIDC (OpenID Connect)
наряду со стандартным входом по паролю — вход по паролю никогда не удаляется, а лишь
дополняется:

- Отключено, если `settings.oidcEnabled !== true` **или** не настроено хотя бы одно из значений `oidcIssuer` /
  `oidcClientId` / `oidcClientSecret` (Настройки → Аутентификация).
  В противном случае `GET /api/auth/oidc/login` возвращает `400`.
- `GET /api/auth/oidc/login` получает `authorization_endpoint` из
  `/.well-known/openid-configuration` издателя (с резервным переходом на
  `<issuer>/authorize`), формирует URI перенаправления на основе входящего запроса
  (с учётом `x-forwarded-proto`) и перенаправляет к IdP со случайным значением `state`,
  сохранённым в cookie `oidc_state` с флагом `httpOnly`.
- `GET /api/auth/oidc/callback` проверяет `state`, обменивает код авторизации
  и проверяет подпись ID-токена через JWKS издателя
  (`createRemoteJWKSet` из `jose`, кэшируется для каждого URI JWKS) с проверками `issuer`/`audience`.
  Список разрешённых значений `oidcAllowedSubjects` обязателен: он сопоставляется
  с утверждением `sub` токена или его утверждением `email` — утверждение электронной почты учитывается
  только при `email_verified === true`, поэтому неподтверждённый адрес электронной почты у IdP никогда
  не сможет пройти проверку, — а при отсутствии записей обработчик обратного вызова отклоняет любой вход
  (`not_configured`).
- При успешном входе выпускается **точно такой же** 30-дневный JWT `auth_token`, какой выдаётся
  при входе по паролю (`src/app/api/auth/login/route.ts`), поэтому остальная часть
  конвейера сессии панели управления (автоматическое обновление, флаги cookie) остаётся неизменной —
  OIDC заменяет только способ выпуска cookie, но не предоставляемые им права.
- Каждая настройка `oidc*` (`oidcEnabled`, `oidcDisablePasswordLogin`,
  `oidcIssuer`, `oidcClientId`, `oidcClientSecret`, `oidcAllowedSubjects`,
  `oidcRedirectPath`, `oidcScopes`) входит в `SECURITY_IMPACTING_SETTINGS_KEYS`
  (`src/shared/constants/securityImpactingSettings.ts`): `PATCH /api/settings`
  возвращает `400 PASSWORD_REQUIRED`, если тело запроса не содержит пароль управления
  в поле `currentPassword` (`401 PASSWORD_MISMATCH`, если он неверен).
  `oidcDisablePasswordLogin` запрещает _вход_ по паролю (`POST /api/auth/login`),
  но сохраняет хеш пароля, и повторная аутентификация по-прежнему проверяет
  `currentPassword` по этому хешу.
- `POST /api/settings/import-json` пропускает эту повторную аутентификацию, поэтому перед записью удаляет все ключи из
  `IMPORT_STRIPPED_SETTINGS_KEYS` (тот же файл): пароль и
  `currentPassword`, каждую запись `SECURITY_IMPACTING_SETTINGS_KEYS` и
  состояние сессии панели управления (`sessionsValidAfter`, `revokedDashboardSessions`).
  Поэтому импорт старой резервной копии не может восстановить сессию, которая уже была
  завершена сменой пароля или выходом из системы.

## Классы маршрутов

`src/server/authz/types.ts` определяет три класса; любой маршрут, который невозможно классифицировать однозначно, относится к `MANAGEMENT`.

| Класс        | Описание                                                                                                                                                               | Требуемая аутентификация                                              |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `PUBLIC`     | Явно безопасные маршруты — вход, выход, статус, инициализация, проверка работоспособности, первоначальная настройка.                                                   | Не требуется                                                          |
| `CLIENT_API` | Конечные точки обслуживания моделей — `/api/v1/*`, `/api/v1beta/*`, а также псевдонимы `/v1/*`, `/v1beta/*`, `/chat/completions`, `/responses`, `/models`, `/codex/*`. | Bearer-ключ, когда включён эффективный флаг функции `REQUIRE_API_KEY` |
| `MANAGEMENT` | Страницы панели управления, настройки, провайдеры, ключи, административные и диагностические конечные точки.                                                           | Сессия панели управления ИЛИ Bearer-ключ с областью доступа `manage`  |

Некоторые действия `MANAGEMENT` доступны **только оператору**: ключа `manage` недостаточно. Для экспорта сохранённых
учётных данных (`GET /api/settings/export-json`, `GET /api/db-backups/export`,
`GET /api/db-backups/exportAll`), выпуска токена синхронизации (`POST /api/sync/tokens`) и создания
токена доступа CLI с правами `admin` (`POST /api/cli/tokens`) требуется сессия панели управления, локальный субъект CLI
либо отключённый вход; API-ключи с любой областью доступа и токены доступа `oma_` получают ответ `403`. Проверка
реализована в `src/lib/api/operatorCredential.ts` (`resolveOperatorCredential()` /
`requireOperatorCredential()`).

A few `MANAGEMENT` actions are **operator-only**: a `manage` key is not enough. Exporting stored
credentials (`GET /api/settings/export-json`, `GET /api/db-backups/export`,
`GET /api/db-backups/exportAll`), restoring a backup over the live data
(`POST /api/db-backups/import` including `dryRun=true`, `POST /api/db-backups` restore by id,
`POST /api/settings/import-json`), issuing a sync token (`POST /api/sync/tokens`) and minting an
`admin` CLI access token (`POST /api/cli/tokens`) require a dashboard session, the local CLI
subject, or login disabled; API keys of any scope and `oma_` access tokens get `403`. The check
lives in `src/lib/api/operatorCredential.ts` (`resolveOperatorCredential()` /
`requireOperatorCredential()`).

## Конвейер

```
Входящий запрос → src/proxy.ts
  → runAuthzPipeline() в src/server/authz/pipeline.ts
    1. Удалить доверенные внутренние заголовки (x-omniroute-auth-*, x-omniroute-route-class)
    2. Сгенерировать идентификатор запроса, классифицировать маршрут через classifyRoute()
    3. Если pathname == "/" → перенаправить на /dashboard
    4. Если идёт завершение работы (штатное отключение) и /api/* → 503
    5. Если запрос к /api/* использует не GET → применить проверку checkBodySize()
    6. Если OPTIONS → предварительный CORS-запрос 204
    7. Если options.enforce == false → пропустить дальше с заголовками класса маршрута
    8. Иначе: POLICIES[routeClass].evaluate(ctx)
       - разрешено → установить x-omniroute-auth-{kind,id,label,scopes} → NextResponse.next()
       - отклонено  → ошибка JSON с correlation_id (страницы панели управления → 302 /login)
```

Доверенные внутренние заголовки (определённые в `src/server/authz/headers.ts`) **удаляются из входящих запросов** перед классификацией — клиенты не могут заранее задать `x-omniroute-auth-*`, чтобы выдать себя за субъекта.

### Контракты политик

Для каждого класса маршрутов предусмотрена политика в `src/server/authz/policies/`:

- **`publicPolicy`** (`policies/public.ts`) — всегда возвращает `allow({ kind: "anonymous", id: "anonymous" })`.
- **`clientApiPolicy`** (`policies/clientApi.ts`) — извлекает Bearer и проверяет его через `validateApiKey()`. Переходит к анонимному доступу только тогда, когда эффективный флаг функции `REQUIRE_API_KEY` отключён. Эффективное значение флага определяется через `isRequireApiKeyEnabled()` (`переопределение флага функции в БД > process.env.REQUIRE_API_KEY > значение по умолчанию`), поэтому флаги функций панели управления и переменные окружения согласованно управляют `/api/v1/*`, `/api/v1beta/*` и псевдонимами; при сбоях распознавателя доступ запрещается. Разрешает запросы с сессией панели управления к маршрутам клиентского API (включая `/api/v1/models`, используемый каталогом моделей панели управления).
- **`managementPolicy`** (`policies/management.ts`) — принимает сессию панели управления и внутренние запросы синхронизации моделей (сопоставляемые с `/api/providers/[name]/(sync-models|models)`) либо полностью пропускает проверку, если `isAuthRequired()` возвращает false. Возвращает 403 (`AUTH_001`), если Bearer-токен присутствует, но недействителен, и 401 в остальных случаях. Кроме того, до выполнения любой ветви аутентификации применяет уровни защиты маршрутов (LOCAL_ONLY / ALWAYS_PROTECTED) — см. [Уровни защиты маршрутов](../security/ROUTE_GUARD_TIERS.md). К путям LOCAL_ONLY из `LOCAL_ONLY_MANAGE_SCOPE_BYPASS_PREFIXES` (на данный момент: `/api/mcp/`) можно обращаться не с loopback-адреса, если Bearer-ключ имеет область действия `manage`; для всех остальных путей LOCAL_ONLY независимо от области действия сохраняется строгое требование loopback-адреса.

При успешном выполнении политика возвращает `AuthSubject` с `kind ∈ { client_api_key, dashboard_session, management_key, anonymous }`. Нижестоящие обработчики могут получить его через `assertAuth(request, "CLIENT_API")` в `src/server/authz/assertAuth.ts` вместо повторного выполнения логики аутентификации.

## Список публичных маршрутов

`src/shared/constants/publicApiRoutes.ts` содержит явный список разрешённых маршрутов:

Список разделён по **форме маршрута**, и это разделение критически важно (GHSA-74g9-q8f6-793h): префикс сопоставляется с помощью `startsWith()`, поэтому он также совпадает со всеми соседними путями, имеющими те же начальные символы.
Если указать `/api/usage/om-usage` в качестве префикса, это сделает `/api/usage/om-usage<anything>` ПУБЛИЧНЫМ, а Next сопоставит такой путь с `/api/usage/[connectionId]` — обработчиком без собственной аутентификации.

```ts
// Настоящие поддеревья. Каждая запись ДОЛЖНА заканчиваться символом "/" (это проверяется модульным тестом).
PUBLIC_API_ROUTE_PREFIXES = [
  "/api/auth/oidc/",
  "/api/v1/", // при классификации рассматривается как CLIENT_API, а не как публичный маршрут «без аутентификации»
  "/api/oauth/",
  "/api/codex/connect/",
  "/api/telegram/",
  "/api/cursor-cli/",
];

// Отдельные маршруты, сопоставляемые ТОЧНО (с завершающей косой чертой или без неё).
PUBLIC_API_ROUTES_EXACT = new Set([
  "/api/auth/login",
  "/api/auth/logout",
  "/api/auth/status",
  "/api/init",
  "/api/sync/bundle",
  "/api/cli/connect",
  "/api/usage/om-usage",
  "/api/skills/collect/chaos",
]);

// Отдельные маршруты только для чтения, к которым также применяется послабление CORS для origin.
PUBLIC_READONLY_CORS_API_ROUTES = [
  "/api/health/ping",
  "/api/monitoring/health",
  "/api/settings/require-login",
];

// Отдельный маршрут только для чтения БЕЗ послабления CORS.
PUBLIC_READONLY_API_ROUTES_EXACT = new Set(["/api/health"]);

PUBLIC_READONLY_METHODS = new Set(["GET", "HEAD", "OPTIONS"]);
```

Маршруты только для чтения являются публичными **только** для безопасных методов. Обратите внимание: `classifyRoute()` исключает `/api/v1/*` и `/api/v1beta/*` из механизма отнесения к PUBLIC по умолчанию — они всегда классифицируются как `CLIENT_API`, поэтому к ним по-прежнему применяется политика Bearer-ключей.

## Добавление нового маршрута

### Схема 1 — Публичная конечная точка клиентского API (Bearer-аутентификация)

Маршруты в `/api/v1/` и `/api/v1beta/` автоматически классифицируются как `CLIENT_API`. Middleware обеспечивает проверку Bearer; обработчикам маршрутов не нужно выполнять её повторно, но при необходимости они могут прочитать субъект.

```typescript
// src/app/api/v1/your-route/route.ts
import { NextRequest, NextResponse } from "next/server";
import { assertAuth } from "@/server/authz/assertAuth";

export async function POST(req: NextRequest) {
  const subject = assertAuth(req, "CLIENT_API");
  // subject.kind === "client_api_key" | "anonymous" | "dashboard_session"
  // ... логика обработчика
}
```

### Схема 2 — Конечная точка управления (сессия или Bearer + manage)

Используйте `requireManagementAuth()` из `src/lib/api/requireManagementAuth.ts`:

```typescript
import { requireManagementAuth } from "@/lib/api/requireManagementAuth";

export async function POST(request: Request) {
  const rejection = await requireManagementAuth(request);
  if (rejection) return rejection;
  // ... логика обработчика
}
```

`requireManagementAuth()` возвращает `null` при успешной проверке либо JSON-ответ `Response` с ошибкой:

- 401 `AUTH_001` "Требуется аутентификация" — учётные данные полностью отсутствуют
- 403 — недействительный Bearer **или** Bearer присутствует, но у ключа нет области действия `manage` / `admin`

`hasManageScope(scopes)` возвращает true для `"manage"` или `"admin"`.

### Схема 3 — Добавление в список публичных маршрутов

Выбирайте набор по форме маршрута, а не по удобству. Отдельный маршрут следует помещать в `PUBLIC_API_ROUTES_EXACT` (или в `PUBLIC_READONLY_CORS_API_ROUTES`, если он предназначен только для GET); только настоящее поддерево следует помещать в `PUBLIC_API_ROUTE_PREFIXES`, причём оно **должно заканчиваться на `/`**. Помещение отдельного маршрута в список префиксов также делает публичными все соседние пути с теми же начальными символами, включая маршруты с динамическими сегментами, добавленные позднее (GHSA-74g9-q8f6-793h). Обновите модульные тесты в `tests/unit/public-api-routes.test.ts`, `tests/unit/authz/public-route-exact-match.test.ts` и `tests/unit/authz/classify.test.ts`.

## Области действия

Три пространства имен. Каждый проверяющий читает только свои строки. Сравнительный анализ, включая то, почему `manage` не проходит `scopeMatches` для `read:compression` и почему токен доступа `read` не может выполнить `PATCH /api/keys/{id}`, находится в
[Три пространства имен областей действия](../frameworks/MCP-SERVER.md#three-scope-namespaces).

Ключи API содержат массив `scopes` (хранится как JSON в `api_keys.scopes`, см. `src/lib/db/apiKeys.ts`).

### Область действия управления

- `manage` / `admin` — `hasManageScope`. Bearer-доступ к маршрутам API управления.
- `mcp:connect`, `self:usage`, `self:account-quota` и
  `policy:bypass-provider-quota` являются аддитивными областями действия с точным совпадением. Они находятся
  вне `MANAGEMENT_API_KEY_SCOPES`. `mcp:connect` открывает только
  не-loopback вырез `/api/mcp/`.

### Области действия инструментов MCP

Каталог и правила сопоставления (идентичная строка или предоставленная область действия, заканчивающаяся на `*`):
[Области действия инструментов MCP](../frameworks/MCP-SERVER.md#mcp-tool-scopes).
`MCP_SCOPE_LIST` в `src/shared/constants/mcpScopes.ts` является исходным типизированным
подмножеством, а не полным каталогом. Принудительное применение выполняется в
`open-sse/mcp-server/scopeEnforcement.ts` после того, как `resolveCallerScopeContext()`
разрешает области действия из информации аутентификации MCP, метаданных запроса или `OMNIROUTE_MCP_SCOPES`.
Оно остается выключенным, если только `OMNIROUTE_MCP_ENFORCE_SCOPES=true`.

### Области действия токенов доступа

`read` / `write` / `admin` для токенов `oma_live_…`, ранжированных по `scopeSatisfies`
(`src/lib/accessTokens/scopes.ts`). Этот ранг применяется только к учетным данным
токена доступа. См. [Аутентификация управления](../guides/MANAGEMENT-AUTH.md).

## Переключатель обязательной аутентификации

`isAuthRequired()` в `src/shared/utils/apiAuth.ts` определяет, требуется ли для запроса **какая-либо** аутентификация:

- `settings.requireLogin === false` → аутентификация глобально отключена.
- Пароль не настроен **и** переменная окружения `INITIAL_PASSWORD` отсутствует → режим начальной настройки разрешает доступ к мастеру адаптации и запросы с loopback-интерфейса, но для внешних сетевых запросов по-прежнему требуются учётные данные.
- Любая ошибка БД → доступ запрещается (безопасность по умолчанию).

Проверка API-ключей клиентов использует `isRequireApiKeyEnabled()` из `src/shared/utils/featureFlags.ts`, а не прямое чтение `process.env.REQUIRE_API_KEY`. Это важно для развёрнутых экземпляров: переключение `REQUIRE_API_KEY` в Dashboard → Feature Flags сохраняет переопределение в БД и немедленно влияет на `/v1/*`, `/v1beta/*`, `/models`, `/responses`, `/chat/completions`, `/codex/*` и другие проверки аутентификации клиентского API, использующие этот вспомогательный компонент. Если хранилище флагов функций недоступно для чтения, аутентификация клиентского API работает в режиме запрета по умолчанию и требует ключ.

## Критическое изменение — v3.8.0

Конечные точки `/api/v1/agents/tasks/*` и `/api/resilience/model-cooldowns` **теперь требуют аутентификацию управления** (коммит `588a0333`). Клиенты, ранее отправлявшие обычный API-ключ без области `manage`, получают `403`. Миграция: либо назначьте ключу область `manage` в панели API Keys, либо используйте аутентифицированный сеанс панели управления.

## Изменение поведения — v3.8.2

`/api/mcp/*` (удалённый сервер MCP) по-прежнему по умолчанию имеет уровень LOCAL_ONLY, но теперь принимает запросы не с loopback-интерфейса, если заголовок `Authorization: Bearer <api-key>` содержит область `manage`. Это исключение явно регулируется для каждого пути с помощью `LOCAL_ONLY_MANAGE_SCOPE_BYPASS_PREFIXES` в `src/server/authz/routeGuard.ts`; для родственного префикса LOCAL_ONLY `/api/cli-tools/runtime/*` обход намеренно НЕ разрешён, поскольку он может запускать произвольные подпроцессы. Анонимные запросы к `/api/mcp/*` не с loopback-интерфейса по-прежнему получают `403 LOCAL_ONLY` — для любого нового пути LOCAL_ONLY по умолчанию сохраняется строгий режим loopback. См. [Уровни защиты маршрутов](../security/ROUTE_GUARD_TIERS.md#manage-scope-carve-out).

## Тестирование

- Модульные тесты: `tests/unit/authz/` — `classify.test.ts`, `pipeline.test.ts`, `client-api-policy.test.ts`, `management-policy.test.ts`, `public-policy.test.ts`.
- Список разрешённых публичных маршрутов: `tests/unit/public-api-routes.test.ts`.
- Запуск отдельных тестов: `node --import tsx/esm --test tests/unit/authz/classify.test.ts`.

## Отладка

Конвейер всегда добавляет к ответам следующие заголовки:

```
x-request-id:               <идентификатор корреляции, дублируемый в телах ошибок>
x-omniroute-route-class:    PUBLIC | CLIENT_API | MANAGEMENT
```

Для аутентифицированных запросов заголовки вышестоящего запроса (на стороне обработчика) также содержат:

```
x-omniroute-auth-kind:      client_api_key | dashboard_session | management_key | anonymous
x-omniroute-auth-id:        key_<последние 4 символа> | "dashboard" | "anonymous"
x-omniroute-auth-label:     (необязательно)
x-omniroute-auth-scopes:    список, разделённый запятыми
```

Используйте `assertAuth(req, expectedClass)` внутри обработчиков — эта функция выбрасывает `AuthzAssertionError` с кодом `AUTHZ_NOT_INITIALIZED`, если промежуточное ПО было обойдено (это помогает выявлять регрессии конфигурации в тестах).

## См. также

- [API_REFERENCE.md](../reference/API_REFERENCE.md) — маркер аутентификации для каждой конечной точки
- [COMPLIANCE.md](../security/COMPLIANCE.md) — журнал аудита событий аутентификации
- [MCP-SERVER.md](../frameworks/MCP-SERVER.md#three-scope-namespaces) — три пространства имен областей видимости и каталог областей видимости инструментов MCP
- Источник: `src/server/authz/`, `src/lib/api/requireManagementAuth.ts`
