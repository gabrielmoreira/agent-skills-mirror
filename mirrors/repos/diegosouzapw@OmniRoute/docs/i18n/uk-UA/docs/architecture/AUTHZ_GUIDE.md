# Authorization Guide (Українська)

🌐 **Languages:** 🇺🇸 [English](../../../../architecture/AUTHZ_GUIDE.md) · 🇪🇹 [am](../../../am/docs/architecture/AUTHZ_GUIDE.md) · 🇸🇦 [ar](../../../ar/docs/architecture/AUTHZ_GUIDE.md) · 🇦🇿 [az](../../../az/docs/architecture/AUTHZ_GUIDE.md) · 🇧🇬 [bg](../../../bg/docs/architecture/AUTHZ_GUIDE.md) · 🇧🇩 [bn](../../../bn/docs/architecture/AUTHZ_GUIDE.md) · 🇧🇦 [bs](../../../bs/docs/architecture/AUTHZ_GUIDE.md) · 🇨🇿 [cs](../../../cs/docs/architecture/AUTHZ_GUIDE.md) · 🇩🇰 [da](../../../da/docs/architecture/AUTHZ_GUIDE.md) · 🇩🇪 [de](../../../de/docs/architecture/AUTHZ_GUIDE.md) · 🇬🇷 [el](../../../el/docs/architecture/AUTHZ_GUIDE.md) · 🇪🇸 [es](../../../es/docs/architecture/AUTHZ_GUIDE.md) · 🇪🇪 [et](../../../et/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇷 [fa](../../../fa/docs/architecture/AUTHZ_GUIDE.md) · 🇫🇮 [fi](../../../fi/docs/architecture/AUTHZ_GUIDE.md) · 🇫🇷 [fr](../../../fr/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇪 [ga](../../../ga/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [gu](../../../gu/docs/architecture/AUTHZ_GUIDE.md) · 🇳🇬 [ha](../../../ha/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇱 [he](../../../he/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [hi](../../../hi/docs/architecture/AUTHZ_GUIDE.md) · 🇭🇷 [hr](../../../hr/docs/architecture/AUTHZ_GUIDE.md) · 🇭🇺 [hu](../../../hu/docs/architecture/AUTHZ_GUIDE.md) · 🇦🇲 [hy](../../../hy/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇩 [id](../../../id/docs/architecture/AUTHZ_GUIDE.md) · 🇳🇬 [ig](../../../ig/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇹 [it](../../../it/docs/architecture/AUTHZ_GUIDE.md) · 🇯🇵 [ja](../../../ja/docs/architecture/AUTHZ_GUIDE.md) · 🇬🇪 [ka](../../../ka/docs/architecture/AUTHZ_GUIDE.md) · 🇰🇭 [km](../../../km/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [kn](../../../kn/docs/architecture/AUTHZ_GUIDE.md) · 🇰🇷 [ko](../../../ko/docs/architecture/AUTHZ_GUIDE.md) · 🇱🇹 [lt](../../../lt/docs/architecture/AUTHZ_GUIDE.md) · 🇱🇻 [lv](../../../lv/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [ml](../../../ml/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [mr](../../../mr/docs/architecture/AUTHZ_GUIDE.md) · 🇲🇾 [ms](../../../ms/docs/architecture/AUTHZ_GUIDE.md) · 🇲🇹 [mt](../../../mt/docs/architecture/AUTHZ_GUIDE.md) · 🇲🇲 [my](../../../my/docs/architecture/AUTHZ_GUIDE.md) · 🇳🇵 [ne](../../../ne/docs/architecture/AUTHZ_GUIDE.md) · 🇳🇱 [nl](../../../nl/docs/architecture/AUTHZ_GUIDE.md) · 🇳🇴 [no](../../../no/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [or](../../../or/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [pa](../../../pa/docs/architecture/AUTHZ_GUIDE.md) · 🇵🇭 [phi](../../../phi/docs/architecture/AUTHZ_GUIDE.md) · 🇵🇱 [pl](../../../pl/docs/architecture/AUTHZ_GUIDE.md) · 🇵🇹 [pt](../../../pt/docs/architecture/AUTHZ_GUIDE.md) · 🇧🇷 [pt-BR](../../../pt-BR/docs/architecture/AUTHZ_GUIDE.md) · 🇷🇴 [ro](../../../ro/docs/architecture/AUTHZ_GUIDE.md) · 🇷🇺 [ru](../../../ru/docs/architecture/AUTHZ_GUIDE.md) · 🇱🇰 [si](../../../si/docs/architecture/AUTHZ_GUIDE.md) · 🇸🇰 [sk](../../../sk/docs/architecture/AUTHZ_GUIDE.md) · 🇸🇮 [sl](../../../sl/docs/architecture/AUTHZ_GUIDE.md) · 🇷🇸 [sr](../../../sr/docs/architecture/AUTHZ_GUIDE.md) · 🇸🇪 [sv](../../../sv/docs/architecture/AUTHZ_GUIDE.md) · 🇰🇪 [sw](../../../sw/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [ta](../../../ta/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [te](../../../te/docs/architecture/AUTHZ_GUIDE.md) · 🇹🇭 [th](../../../th/docs/architecture/AUTHZ_GUIDE.md) · 🇹🇷 [tr](../../../tr/docs/architecture/AUTHZ_GUIDE.md) · 🇵🇰 [ur](../../../ur/docs/architecture/AUTHZ_GUIDE.md) · 🇺🇿 [uz](../../../uz/docs/architecture/AUTHZ_GUIDE.md) · 🇻🇳 [vi](../../../vi/docs/architecture/AUTHZ_GUIDE.md) · 🇳🇬 [yo](../../../yo/docs/architecture/AUTHZ_GUIDE.md) · 🇨🇳 [zh-CN](../../../zh-CN/docs/architecture/AUTHZ_GUIDE.md) · 🇹🇼 [zh-TW](../../../zh-TW/docs/architecture/AUTHZ_GUIDE.md)

---

> **Джерело істини:** `src/server/authz/`, `src/shared/constants/publicApiRoutes.ts`, `src/lib/api/requireManagementAuth.ts`, `src/shared/utils/apiAuth.ts`
> **Останнє оновлення:** 22.09.2026 — простори імен області вказують на MCP-SERVER.md

OmniRoute має конвеєр авторизації, що враховує маршрути та захищає кожен запит API. Класифікація є **детермінованою** та **закривається при збої** — все, що не може бути класифіковано, стає `MANAGEMENT` і вимагає сесії або токена рівня управління. Ця сторінка пояснює модель для інженерів, які підтримують маршрути або розробляють нові кінцеві точки.

![Конвеєр AuthZ (3 класи маршрутів + оцінка політики)](../diagrams/exported/authz-pipeline.svg)

> Джерело: [diagrams/authz-pipeline.mmd](../diagrams/authz-pipeline.mmd)

## Два режими автентифікації

### 1. Ключ API (Bearer)

Використовується для клієнтських API, сумісних з OpenAI/Anthropic/Gemini, а також для кількох маршрутів керування, коли ключ має область дії `manage`.

```
Authorization: Bearer <api-key>
```

Перевіряється за допомогою `isValidApiKey()` / `extractApiKey()` у `src/sse/services/auth.ts` і повторно експортується через `src/shared/utils/apiAuth.ts`. Валідатор також приймає змінні середовища `OMNIROUTE_API_KEY` / `ROUTER_API_KEY` як постійні ключі наскрізної передачі (завдання #1350).

### 2. Сеанс панелі керування (файл cookie auth_token)

Для сторінок панелі керування та адміністративних операцій.

```
Cookie: auth_token=<JWT signed with JWT_SECRET>
```

Файл cookie є сеансом лише тоді, коли JWT успішно перевірено **і** він містить `authenticated: true`
(`src/shared/utils/dashboardSessionToken.ts` → `verifyDashboardSessionToken`). Кожен
споживач цього файлу cookie (захисний механізм маршруту панелі керування (`isDashboardSessionAuthenticated()`), оновлення конвеєра авторизації, встановлення з’єднання WebSocket, сервер обміну даними в реальному часі, `/api/settings/require-login`, `/api/auth/status`) використовує цей допоміжний метод.
Існують й інші JWT, підписані за допомогою `JWT_SECRET`: механізм наскрізної передачі Cursor CLI створює
для власників ключів токени з `iss "omniroute" / aud "cursor-cli"`, які ніколи не є сеансами
(#13298).

Перевіряється за допомогою `isDashboardSessionAuthenticated()` у `src/shared/utils/apiAuth.ts`. Конвеєр автоматично оновлює JWT, коли до завершення його 30-денного строку дії залишається менш ніж 7 днів.

Сеанс також може завершитися до закінчення 30 днів, оскільки кожен засіб створення токенів використовує `mintDashboardSessionToken` (час створення `iat` та ідентифікатор `jti`), а засіб перевірки перевіряє два налаштування: `sessionsValidAfter`, яке встановлюється під час зміни пароля, через що всі видані до цього сеанси перестають проходити перевірку (браузер, у якому змінено пароль, отримує новий файл cookie), і `revokedDashboardSessions`, до якого `POST /api/auth/logout` додає `jti` сеансу, з якого виконано вихід. Сеанси, створені старішим випуском, не містять жодної з цих заяв і залишаються дійсними до першої зміни пароля. Якщо налаштування неможливо прочитати, сеанс не вважається надійним.

Деякі маршрути керування приймають **будь-який** із режимів: файл cookie АБО `Bearer <key>`, якщо ключ API має область дії `manage` (або `admin`). Саме це забезпечує робочий процес «налаштування за допомогою викликів API», доданий у v3.8.

#### Необов’язковий шлюз входу OIDC (#6973)

Адміністративний вхід до панелі керування також підтримує **необов’язковий** потік OIDC (OpenID Connect)
разом зі стандартним входом за паролем — вхід за паролем ніколи не вилучається, а лише
доповнюється:

- Вимкнено, якщо `settings.oidcEnabled !== true` **або** не налаштовано хоча б одне з
  `oidcIssuer` / `oidcClientId` / `oidcClientSecret` (Налаштування → Автентифікація).
  Інакше `GET /api/auth/oidc/login` повертає `400`.
- `GET /api/auth/oidc/login` знаходить `authorization_endpoint` із
  `/.well-known/openid-configuration` постачальника
  (із резервним переходом до `<issuer>/authorize`), формує URI переспрямування з вхідного запиту
  (з урахуванням `x-forwarded-proto`) і переспрямовує до IdP із випадковим значенням `state`,
  збереженим у файлі cookie `oidc_state` з атрибутом `httpOnly`.
- `GET /api/auth/oidc/callback` перевіряє `state`, обмінює код авторизації
  та перевіряє підпис токена ID за допомогою JWKS постачальника
  (`createRemoteJWKSet` із `jose`, кешований для кожного URI JWKS) із перевірками
  `issuer`/`audience`. Список дозволених значень `oidcAllowedSubjects` є обов’язковим: він зіставляється із
  заявою `sub` токена або його заявою `email` — заява електронної пошти враховується лише
  тоді, коли `email_verified === true`, тому непідтверджена адреса електронної пошти в IdP ніколи не зможе
  пройти перевірку — а за відсутності записів зворотний виклик відхиляє кожну спробу входу
  (`not_configured`).
- У разі успіху створюється **точно такий самий** 30-денний JWT `auth_token`, який видає вхід
  за паролем (`src/app/api/auth/login/route.ts`), тому решта
  конвеєра сеансу панелі керування (автоматичне оновлення, атрибути файлу cookie) залишається незмінною —
  OIDC замінює лише спосіб створення файлу cookie, а не надані ним права.
- Кожне налаштування `oidc*` (`oidcEnabled`, `oidcDisablePasswordLogin`,
  `oidcIssuer`, `oidcClientId`, `oidcClientSecret`, `oidcAllowedSubjects`,
  `oidcRedirectPath`, `oidcScopes`) входить до `SECURITY_IMPACTING_SETTINGS_KEYS`
  (`src/shared/constants/securityImpactingSettings.ts`): `PATCH /api/settings`
  відповідає `400 PASSWORD_REQUIRED`, якщо тіло не містить пароль керування як
  `currentPassword` (`401 PASSWORD_MISMATCH`, якщо він неправильний).
  `oidcDisablePasswordLogin` забороняє _вхід_ за паролем (`POST /api/auth/login`),
  але зберігає хеш пароля, а повторна автентифікація й надалі перевіряє
  `currentPassword` відносно нього.
- `POST /api/settings/import-json` пропускає цю повторну автентифікацію, тому перед записом видаляє кожен ключ із
  `IMPORT_STRIPPED_SETTINGS_KEYS` (той самий файл): пароль і
  `currentPassword`, кожен запис `SECURITY_IMPACTING_SETTINGS_KEYS`, а також
  стан сеансу панелі керування (`sessionsValidAfter`, `revokedDashboardSessions`).
  Тому імпортування старішої резервної копії не може відновити сеанс, який уже завершила
  зміна пароля або вихід із системи.

## Класи маршрутів

`src/server/authz/types.ts` визначає три класи; будь-який маршрут, який неможливо однозначно класифікувати, за замовчуванням належить до `MANAGEMENT`.

| Клас         | Опис                                                                                                                                                                    | Необхідна автентифікація                                                    |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `PUBLIC`     | Явно безпечні маршрути — вхід, вихід, статус, ініціалізація, перевірка працездатності, початкове налаштування.                                                          | Не потрібна                                                                 |
| `CLIENT_API` | Кінцеві точки обслуговування моделей — `/api/v1/*`, `/api/v1beta/*`, а також псевдоніми `/v1/*`, `/v1beta/*`, `/chat/completions`, `/responses`, `/models`, `/codex/*`. | Bearer-ключ, коли активовано ефективний прапорець функції `REQUIRE_API_KEY` |
| `MANAGEMENT` | Сторінки панелі керування, налаштування, провайдери, ключі, адміністративні та діагностичні кінцеві точки.                                                              | Сесія панелі керування АБО Bearer зі сферою дії `manage`                    |

Деякі дії `MANAGEMENT` доступні **лише оператору**: ключа `manage` недостатньо. Експорт збережених
облікових даних (`GET /api/settings/export-json`, `GET /api/db-backups/export`,
`GET /api/db-backups/exportAll`), видача токена синхронізації (`POST /api/sync/tokens`) і створення
токена доступу CLI `admin` (`POST /api/cli/tokens`) потребують сесії панелі керування, локального
суб’єкта CLI або вимкненого входу; ключі API з будь-якою сферою дії та токени доступу `oma_`
отримують `403`. Перевірка міститься в `src/lib/api/operatorCredential.ts` (`resolveOperatorCredential()` /
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

## Конвеєр

```
Вхідний запит → src/proxy.ts
  → runAuthzPipeline() у src/server/authz/pipeline.ts
    1. Видалити довірені внутрішні заголовки (x-omniroute-auth-*, x-omniroute-route-class)
    2. Згенерувати ідентифікатор запиту, класифікувати маршрут через classifyRoute()
    3. Якщо pathname == "/" → переспрямувати на /dashboard
    4. Якщо триває завершення роботи (коректне завершення) і /api/* → 503
    5. Якщо не-GET /api/* → перевірка checkBodySize()
    6. Якщо OPTIONS → попередній CORS-запит 204
    7. Якщо options.enforce == false → пропустити із заголовками класу маршруту
    8. Інакше: POLICIES[routeClass].evaluate(ctx)
       - дозволено  → установити x-omniroute-auth-{kind,id,label,scopes} → NextResponse.next()
       - відхилено → помилка JSON із correlation_id (сторінки панелі керування → 302 /login)
```

Довірені внутрішні заголовки (визначені в `src/server/authz/headers.ts`) **видаляються з вхідних запитів** перед класифікацією — клієнти не можуть заздалегідь додати `x-omniroute-auth-*`, щоб видати себе за суб’єкта.

### Контракти політик

Кожен клас маршруту має політику в `src/server/authz/policies/`:

- **`publicPolicy`** (`policies/public.ts`) — завжди повертає `allow({ kind: "anonymous", id: "anonymous" })`.
- **`clientApiPolicy`** (`policies/clientApi.ts`) — отримує Bearer-токен і перевіряє його через `validateApiKey()`. Перехід до анонімного доступу відбувається лише тоді, коли ефективний прапорець функції `REQUIRE_API_KEY` вимкнено. Ефективне значення прапорця визначається через `isRequireApiKeyEnabled()` (`перевизначення прапорця функції в БД > process.env.REQUIRE_API_KEY > значення за замовчуванням`), тому прапорці функцій у панелі керування та змінні середовища узгоджено керують `/api/v1/*`, `/api/v1beta/*` і псевдонімами; у разі помилок засобу визначення доступ забороняється. Дозволяє запити із сесією панелі керування до клієнтських API-маршрутів (зокрема `/api/v1/models`, який використовується каталогом моделей панелі керування).
- **`managementPolicy`** (`policies/management.ts`) — приймає сесію панелі керування, внутрішні запити синхронізації моделей (зіставлені з `/api/providers/[name]/(sync-models|models)`) або повністю пропускає перевірку, якщо `isAuthRequired()` повертає false. Повертає 403 (`AUTH_001`), коли Bearer-токен наявний, але недійсний, інакше — 401. Також застосовує рівні захисту маршрутів (LOCAL_ONLY / ALWAYS_PROTECTED) перед будь-якою гілкою автентифікації — див. [Рівні захисту маршрутів](../security/ROUTE_GUARD_TIERS.md). Шляхи LOCAL_ONLY у `LOCAL_ONLY_MANAGE_SCOPE_BYPASS_PREFIXES` (наразі: `/api/mcp/`) можуть бути доступними не з loopback-адреси, якщо Bearer-ключ має сферу доступу `manage`; усі інші шляхи LOCAL_ONLY залишаються суворо доступними лише через loopback незалежно від сфери доступу.

Успішна політика повертає `AuthSubject` із `kind ∈ { client_api_key, dashboard_session, management_key, anonymous }`. Наступні обробники можуть зчитати його через `assertAuth(request, "CLIENT_API")` у `src/server/authz/assertAuth.ts` замість повторного виконання логіки автентифікації.

## Список публічних маршрутів

`src/shared/constants/publicApiRoutes.ts` є явним списком дозволених маршрутів:

Список розділено за **формою**, і цей поділ є критично важливим (GHSA-74g9-q8f6-793h): префікс зіставляється за допомогою `startsWith()`, тому він також відповідає кожному суміжному шляху, що має такі самі початкові символи.
Як префікс, `/api/usage/om-usage` робив `/api/usage/om-usage<anything>` ПУБЛІЧНИМ, а Next зіставляє це з `/api/usage/[connectionId]` — обробником без власної автентифікації.

```ts
// Справжні піддерева. Кожен запис МАЄ закінчуватися на "/" (це перевіряється модульним тестом).
PUBLIC_API_ROUTE_PREFIXES = [
  "/api/auth/oidc/",
  "/api/v1/", // класифікується як CLIENT_API у classify, а не як публічний маршрут "без автентифікації"
  "/api/oauth/",
  "/api/codex/connect/",
  "/api/telegram/",
  "/api/cursor-cli/",
];

// Окремі маршрути, що зіставляються ТОЧНО (з кінцевою скісною рискою або без неї).
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

// Окремі маршрути лише для читання, до яких також застосовується послаблення обмежень CORS для джерела.
PUBLIC_READONLY_CORS_API_ROUTES = [
  "/api/health/ping",
  "/api/monitoring/health",
  "/api/settings/require-login",
];

// Окремий маршрут лише для читання БЕЗ послаблення обмежень CORS.
PUBLIC_READONLY_API_ROUTES_EXACT = new Set(["/api/health"]);

PUBLIC_READONLY_METHODS = new Set(["GET", "HEAD", "OPTIONS"]);
```

Маршрути лише для читання є публічними **тільки** для безпечних методів. Примітка: `classifyRoute()` виключає `/api/v1/*` і `/api/v1beta/*` із резервної класифікації PUBLIC — вони завжди мають тип `CLIENT_API`, тому політика ключів Bearer усе одно застосовується.

## Додавання нового маршруту

### Шаблон 1 — Публічна кінцева точка клієнтського API (Bearer-автентифікація)

Маршрути в `/api/v1/` і `/api/v1beta/` автоматично класифікуються як `CLIENT_API`. Проміжне ПЗ забезпечує перевірку Bearer; обробникам маршрутів не потрібно виконувати її повторно, але за потреби вони можуть отримати суб’єкт.

```typescript
// src/app/api/v1/your-route/route.ts
import { NextRequest, NextResponse } from "next/server";
import { assertAuth } from "@/server/authz/assertAuth";

export async function POST(req: NextRequest) {
  const subject = assertAuth(req, "CLIENT_API");
  // subject.kind === "client_api_key" | "anonymous" | "dashboard_session"
  // ... логіка обробника
}
```

### Шаблон 2 — Кінцева точка керування (сеанс або Bearer + manage)

Використовуйте `requireManagementAuth()` із `src/lib/api/requireManagementAuth.ts`:

```typescript
import { requireManagementAuth } from "@/lib/api/requireManagementAuth";

export async function POST(request: Request) {
  const rejection = await requireManagementAuth(request);
  if (rejection) return rejection;
  // ... логіка обробника
}
```

У разі успіху `requireManagementAuth()` повертає `null`, а в разі помилки — JSON-відповідь `Response`:

- 401 `AUTH_001` "Потрібна автентифікація" — облікові дані повністю відсутні
- 403 — недійсний Bearer **або** Bearer надано, але ключ не має області дії `manage` / `admin`

`hasManageScope(scopes)` повертає true для `"manage"` або `"admin"`.

### Шаблон 3 — Додавання до публічного списку дозволених маршрутів

Вибирайте набір за формою, а не за зручністю. Один маршрут слід додавати до `PUBLIC_API_ROUTES_EXACT` (або до `PUBLIC_READONLY_CORS_API_ROUTES`, якщо він призначений лише для GET); лише справжнє піддерево слід додавати до `PUBLIC_API_ROUTE_PREFIXES`, і воно **має закінчуватися на `/`**. Додавання окремого маршруту до списку префіксів також робить публічним кожен суміжний шлях, що має такі самі початкові символи, — включно зі спорідненими маршрутами з динамічними сегментами, доданими пізніше (GHSA-74g9-q8f6-793h). Оновіть модульні тести в `tests/unit/public-api-routes.test.ts`, `tests/unit/authz/public-route-exact-match.test.ts` і `tests/unit/authz/classify.test.ts`.

## Області видимості (Scopes)

Три простори імен. Кожен перевіряльник читає лише власні рядки. Порівняння,
включно з тим, чому `manage` не проходить `scopeMatches` для `read:compression` і чому
токен доступу `read` не може `PATCH /api/keys/{id}`, знаходиться в
[Три простори імен областей видимості](../frameworks/MCP-SERVER.md#three-scope-namespaces).

Ключі API містять масив `scopes` (зберігається як JSON у `api_keys.scopes`, див. `src/lib/db/apiKeys.ts`).

### Область видимості управління

- `manage` / `admin` — `hasManageScope`. Доступ Bearer до маршрутів API управління.
- `mcp:connect`, `self:usage`, `self:account-quota` та
  `policy:bypass-provider-quota` є адитивними областями видимості з точним збігом. Вони знаходяться
  поза `MANAGEMENT_API_KEY_SCOPES`. `mcp:connect` відкриває лише
  не-зворотний виріз `/api/mcp/`.

### Області видимості інструментів MCP

Каталог та правила відповідності (ідентичний рядок або надана область видимості, що закінчується на `*`):
[Області видимості інструментів MCP](../frameworks/MCP-SERVER.md#mcp-tool-scopes).
`MCP_SCOPE_LIST` у `src/shared/constants/mcpScopes.ts` є оригінальною типізованою
підмножиною, а не повним каталогом. Примусове виконання відбувається в
`open-sse/mcp-server/scopeEnforcement.ts` після того, як `resolveCallerScopeContext()`
розв'язує області видимості з інформації про автентифікацію MCP, метаданих запиту або `OMNIROUTE_MCP_SCOPES`.
Воно залишається вимкненим, якщо `OMNIROUTE_MCP_ENFORCE_SCOPES=true`.

### Області видимості токенів доступу

`read` / `write` / `admin` на токенах `oma_live_…`, ранжовані за `scopeSatisfies`
(`src/lib/accessTokens/scopes.ts`). Цей ранг застосовується лише до облікових даних токена доступу.
Див. [Автентифікація управління](../guides/MANAGEMENT-AUTH.md).

## Перемикач обов’язкової автентифікації

`isAuthRequired()` у `src/shared/utils/apiAuth.ts` визначає, чи застосовується **будь-яка** автентифікація для запиту:

- `settings.requireLogin === false` → автентифікацію глобально вимкнено.
- Якщо пароль не налаштовано **і** змінну середовища `INITIAL_PASSWORD` не задано → режим початкового налаштування дозволяє роботу майстра адаптації та запити зі зворотного інтерфейсу, але для запитів із зовнішньої мережі все одно потрібні облікові дані.
- Будь-яка помилка БД → доступ блокується (безпека за замовчуванням).

Для перевірки ключів клієнтського API використовується `isRequireApiKeyEnabled()` із `src/shared/utils/featureFlags.ts`, а не безпосереднє читання `process.env.REQUIRE_API_KEY`. Це важливо для розгорнутих екземплярів: перемикання `REQUIRE_API_KEY` у Dashboard → Feature Flags зберігає перевизначення в БД і негайно впливає на `/v1/*`, `/v1beta/*`, `/models`, `/responses`, `/chat/completions`, `/codex/*` та інші перевірки автентифікації клієнтського API, які використовують цей допоміжний засіб. Якщо сховище прапорців функцій неможливо прочитати, автентифікація клієнтського API блокує доступ за замовчуванням і вимагає ключ.

## Несумісна зміна — v3.8.0

Кінцеві точки `/api/v1/agents/tasks/*` і `/api/resilience/model-cooldowns` **тепер вимагають автентифікації для керування** (коміт `588a0333`). Клієнти, які раніше надсилали звичайний ключ API без області `manage`, отримують `403`. Міграція: або надайте ключу область `manage` на панелі API Keys, або скористайтеся сеансом із виконаним входом на панель керування.

## Зміна поведінки — v3.8.2

`/api/mcp/*` (віддалений сервер MCP) за замовчуванням усе ще має режим LOCAL_ONLY, але тепер приймає запити не зі зворотного інтерфейсу, якщо заголовок `Authorization: Bearer <api-key>` містить область `manage`. Цей виняток явно контролюється для кожного шляху через `LOCAL_ONLY_MANAGE_SCOPE_BYPASS_PREFIXES` у `src/server/authz/routeGuard.ts`; обхід для спорідненого префікса LOCAL_ONLY `/api/cli-tools/runtime/*` навмисно неможливий, оскільки він може запускати довільні підпроцеси. Анонімні запити до `/api/mcp/*` не зі зворотного інтерфейсу й надалі отримують `403 LOCAL_ONLY` — за замовчуванням будь-який новий шлях LOCAL_ONLY залишається суворо обмеженим зворотним інтерфейсом. Див. [Рівні захисту маршрутів](../security/ROUTE_GUARD_TIERS.md#manage-scope-carve-out).

## Тестування

- Модульні тести: `tests/unit/authz/` — `classify.test.ts`, `pipeline.test.ts`, `client-api-policy.test.ts`, `management-policy.test.ts`, `public-policy.test.ts`.
- Список дозволених загальнодоступних маршрутів: `tests/unit/public-api-routes.test.ts`.
- Запуск окремого тесту: `node --import tsx/esm --test tests/unit/authz/classify.test.ts`.

## Налагодження

Конвеєр завжди додає до відповідей такі заголовки:

```
x-request-id:               <ідентифікатор кореляції, дублюється в тілах помилок>
x-omniroute-route-class:    PUBLIC | CLIENT_API | MANAGEMENT
```

Для автентифікованих запитів заголовки запиту до висхідного сервера (на стороні обробника) також містять:

```
x-omniroute-auth-kind:      client_api_key | dashboard_session | management_key | anonymous
x-omniroute-auth-id:        key_<останні-4> | "dashboard" | "anonymous"
x-omniroute-auth-label:     (необов’язково)
x-omniroute-auth-scopes:    список, розділений комами
```

Використовуйте `assertAuth(req, expectedClass)` усередині обробників — ця функція викидає виняток `AuthzAssertionError` із кодом `AUTHZ_NOT_INITIALIZED`, якщо проміжне програмне забезпечення було обійдено (це допомагає виявляти регресії конфігурації в тестах).

## Дивіться також

- [API_REFERENCE.md](../reference/API_REFERENCE.md) — маркер автентифікації для кожної кінцевої точки
- [COMPLIANCE.md](../security/COMPLIANCE.md) — журнал аудиту для подій автентифікації
- [MCP-SERVER.md](../frameworks/MCP-SERVER.md#three-scope-namespaces) — три простори імен області видимості та каталог MCP tool-scope
- Джерело: `src/server/authz/`, `src/lib/api/requireManagementAuth.ts`
