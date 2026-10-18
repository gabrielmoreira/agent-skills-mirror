# Authorization Guide (Oʻzbekcha)

🌐 **Languages:** 🇺🇸 [English](../../../../architecture/AUTHZ_GUIDE.md) · 🇪🇹 [am](../../../am/docs/architecture/AUTHZ_GUIDE.md) · 🇸🇦 [ar](../../../ar/docs/architecture/AUTHZ_GUIDE.md) · 🇦🇿 [az](../../../az/docs/architecture/AUTHZ_GUIDE.md) · 🇧🇬 [bg](../../../bg/docs/architecture/AUTHZ_GUIDE.md) · 🇧🇩 [bn](../../../bn/docs/architecture/AUTHZ_GUIDE.md) · 🇧🇦 [bs](../../../bs/docs/architecture/AUTHZ_GUIDE.md) · 🇨🇿 [cs](../../../cs/docs/architecture/AUTHZ_GUIDE.md) · 🇩🇰 [da](../../../da/docs/architecture/AUTHZ_GUIDE.md) · 🇩🇪 [de](../../../de/docs/architecture/AUTHZ_GUIDE.md) · 🇬🇷 [el](../../../el/docs/architecture/AUTHZ_GUIDE.md) · 🇪🇸 [es](../../../es/docs/architecture/AUTHZ_GUIDE.md) · 🇪🇪 [et](../../../et/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇷 [fa](../../../fa/docs/architecture/AUTHZ_GUIDE.md) · 🇫🇮 [fi](../../../fi/docs/architecture/AUTHZ_GUIDE.md) · 🇫🇷 [fr](../../../fr/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇪 [ga](../../../ga/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [gu](../../../gu/docs/architecture/AUTHZ_GUIDE.md) · 🇳🇬 [ha](../../../ha/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇱 [he](../../../he/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [hi](../../../hi/docs/architecture/AUTHZ_GUIDE.md) · 🇭🇷 [hr](../../../hr/docs/architecture/AUTHZ_GUIDE.md) · 🇭🇺 [hu](../../../hu/docs/architecture/AUTHZ_GUIDE.md) · 🇦🇲 [hy](../../../hy/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇩 [id](../../../id/docs/architecture/AUTHZ_GUIDE.md) · 🇳🇬 [ig](../../../ig/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇹 [it](../../../it/docs/architecture/AUTHZ_GUIDE.md) · 🇯🇵 [ja](../../../ja/docs/architecture/AUTHZ_GUIDE.md) · 🇬🇪 [ka](../../../ka/docs/architecture/AUTHZ_GUIDE.md) · 🇰🇭 [km](../../../km/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [kn](../../../kn/docs/architecture/AUTHZ_GUIDE.md) · 🇰🇷 [ko](../../../ko/docs/architecture/AUTHZ_GUIDE.md) · 🇱🇹 [lt](../../../lt/docs/architecture/AUTHZ_GUIDE.md) · 🇱🇻 [lv](../../../lv/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [ml](../../../ml/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [mr](../../../mr/docs/architecture/AUTHZ_GUIDE.md) · 🇲🇾 [ms](../../../ms/docs/architecture/AUTHZ_GUIDE.md) · 🇲🇹 [mt](../../../mt/docs/architecture/AUTHZ_GUIDE.md) · 🇲🇲 [my](../../../my/docs/architecture/AUTHZ_GUIDE.md) · 🇳🇵 [ne](../../../ne/docs/architecture/AUTHZ_GUIDE.md) · 🇳🇱 [nl](../../../nl/docs/architecture/AUTHZ_GUIDE.md) · 🇳🇴 [no](../../../no/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [or](../../../or/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [pa](../../../pa/docs/architecture/AUTHZ_GUIDE.md) · 🇵🇭 [phi](../../../phi/docs/architecture/AUTHZ_GUIDE.md) · 🇵🇱 [pl](../../../pl/docs/architecture/AUTHZ_GUIDE.md) · 🇵🇹 [pt](../../../pt/docs/architecture/AUTHZ_GUIDE.md) · 🇧🇷 [pt-BR](../../../pt-BR/docs/architecture/AUTHZ_GUIDE.md) · 🇷🇴 [ro](../../../ro/docs/architecture/AUTHZ_GUIDE.md) · 🇷🇺 [ru](../../../ru/docs/architecture/AUTHZ_GUIDE.md) · 🇱🇰 [si](../../../si/docs/architecture/AUTHZ_GUIDE.md) · 🇸🇰 [sk](../../../sk/docs/architecture/AUTHZ_GUIDE.md) · 🇸🇮 [sl](../../../sl/docs/architecture/AUTHZ_GUIDE.md) · 🇷🇸 [sr](../../../sr/docs/architecture/AUTHZ_GUIDE.md) · 🇸🇪 [sv](../../../sv/docs/architecture/AUTHZ_GUIDE.md) · 🇰🇪 [sw](../../../sw/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [ta](../../../ta/docs/architecture/AUTHZ_GUIDE.md) · 🇮🇳 [te](../../../te/docs/architecture/AUTHZ_GUIDE.md) · 🇹🇭 [th](../../../th/docs/architecture/AUTHZ_GUIDE.md) · 🇹🇷 [tr](../../../tr/docs/architecture/AUTHZ_GUIDE.md) · 🇺🇦 [uk-UA](../../../uk-UA/docs/architecture/AUTHZ_GUIDE.md) · 🇵🇰 [ur](../../../ur/docs/architecture/AUTHZ_GUIDE.md) · 🇻🇳 [vi](../../../vi/docs/architecture/AUTHZ_GUIDE.md) · 🇳🇬 [yo](../../../yo/docs/architecture/AUTHZ_GUIDE.md) · 🇨🇳 [zh-CN](../../../zh-CN/docs/architecture/AUTHZ_GUIDE.md) · 🇹🇼 [zh-TW](../../../zh-TW/docs/architecture/AUTHZ_GUIDE.md)

---

> **Haqiqat manbai:** `src/server/authz/`, `src/shared/constants/publicApiRoutes.ts`, `src/lib/api/requireManagementAuth.ts`, `src/shared/utils/apiAuth.ts`
> **Oxirgi yangilangan sana:** 2026-09-22 — koʻlam nomfazo (scope namespaces) MCP-SERVER.md ga ishora qiladi

OmniRoute har bir API soʻrovini boshqaradigan marshrutni biluvchi avtorizatsiya quvuriga ega. Tasniflash **deterministik** va **fail-closed** (xato boʻlsa yopiladi) — tasniflanmaydigan har qanday narsa `MANAGEMENT` sifatida yakunlanadi va sessiya yoki boshqaruv darajasidagi token talab qiladi. Ushbu sahifa marshrutlarni saqlovchi yoki yangi yakuniy nuqtalarni loyihalashtiruvchi muhandislar uchun modelni tushuntiradi.

![AuthZ quvuri (3 ta marshrut sinfi + siyosatni baholash)](../diagrams/exported/authz-pipeline.svg)

> Manba: [diagrams/authz-pipeline.mmd](../diagrams/authz-pipeline.mmd)

## Ikki autentifikatsiya rejimi

### 1. API kaliti (Bearer)

OpenAI/Anthropic/Gemini bilan mos mijoz APIʼlari va kalit `manage` doirasiga ega boʻlganda ayrim boshqaruv yoʻnalishlari uchun ishlatiladi.

```
Authorization: Bearer <api-key>
```

`src/sse/services/auth.ts` ichidagi `isValidApiKey()` / `extractApiKey()` tomonidan tekshiriladi va `src/shared/utils/apiAuth.ts` orqali qayta eksport qilinadi. Tekshiruvchi, shuningdek, `OMNIROUTE_API_KEY` / `ROUTER_API_KEY` muhit oʻzgaruvchilarini doimiy tranzit kalitlar sifatida qabul qiladi (muammo #1350).

### 2. Boshqaruv paneli sessiyasi (auth_token cookie fayli)

Boshqaruv paneli sahifalari va administrator amallari uchun.

```
Cookie: auth_token=<JWT_SECRET bilan imzolangan JWT>
```

Cookie fayli faqat JWT tekshiruvdan oʻtsa **va** `authenticated: true` qiymatiga ega boʻlsa sessiya hisoblanadi
(`src/shared/utils/dashboardSessionToken.ts` → `verifyDashboardSessionToken`). Cookie faylining har bir
isteʼmolchisi (boshqaruv paneli yoʻnalishi himoyasi (`isDashboardSessionAuthenticated()`), avtorizatsiya konveyerini yangilash, WebSocket ulanishini oʻrnatish, jonli
server, `/api/settings/require-login`, `/api/auth/status`) shu yordamchi orqali ishlaydi.
`JWT_SECRET` bilan imzolangan boshqa JWTʼlar ham mavjud — Cursor CLI tranzit mexanizmi kalit egalariga
`iss "omniroute" / aud "cursor-cli"` tokenlarini yaratadi — va ular hech qachon sessiya hisoblanmaydi
(#13298).

`src/shared/utils/apiAuth.ts` ichidagi `isDashboardSessionAuthenticated()` tomonidan tekshiriladi. JWTʼning 30 kunlik amal qilish muddatidan 7 kundan kam vaqt qolganida konveyer uni avtomatik ravishda yangilaydi.

Sessiya 30 kunlik muddati tugashidan oldin ham yakunlanishi mumkin, chunki har bir token yaratuvchi `mintDashboardSessionToken` orqali ishlaydi (yaratilish vaqti `iat` va identifikator `jti`) hamda tekshiruvchi ikkita sozlamani tekshiradi: parol oʻzgartirilganda oʻrnatiladigan `sessionsValidAfter`, buning natijasida undan oldin berilgan barcha sessiyalar tekshiruvdan oʻtmaydi (parolni oʻzgartirgan brauzer yangi cookie faylini oladi), va `POST /api/auth/logout` tizimdan chiqarilgan sessiyaning `jti` qiymatini qoʻshadigan `revokedDashboardSessions`. Eski reliz tomonidan yaratilgan sessiyalarda bu daʼvolarning hech biri boʻlmaydi va ular birinchi parol oʻzgarishigacha amal qiladi. Agar sozlamalarni oʻqib boʻlmasa, sessiyaga ishonilmaydi.

Ayrim boshqaruv yoʻnalishlari **ikkala** rejimni ham qabul qiladi: cookie fayli YOKI API kaliti `manage` (yoki `admin`) doirasiga ega boʻlganda `Bearer <key>`. Aynan shu v3.8 versiyasida qoʻshilgan «API chaqiruvlari orqali sozlash mumkin» ish jarayonini taʼminlaydi.

#### Ixtiyoriy OIDC kirish darvozasi (#6973)

Boshqaruv panelidagi administrator kirishi standart parol orqali kirish bilan birga **ixtiyoriy ravishda yoqiladigan** OIDC (OpenID Connect) oqimini ham
qoʻllab-quvvatlaydi — parol orqali kirish hech qachon olib tashlanmaydi, faqat
toʻldiriladi:

- `settings.oidcEnabled === true` boʻlmasa **va** `oidcIssuer` /
  `oidcClientId` / `oidcClientSecret` qiymatlarining barchasi sozlanmagan boʻlsa, oʻchirilgan boʻladi (Settings → Auth).
  Aks holda `GET /api/auth/oidc/login` `400` qaytaradi.
- `GET /api/auth/oidc/login` emitentning
  `/.well-known/openid-configuration` manzilidan `authorization_endpoint` qiymatini aniqlaydi (`<issuer>/authorize`
  manziliga zaxira oʻtish mavjud), kiruvchi soʻrov asosida qayta yoʻnaltirish URIʼsini tuzadi
  (`x-forwarded-proto` hisobga olinadi) va `httpOnly` turidagi `oidc_state` cookie faylida saqlangan tasodifiy `state`
  bilan IdPʼga qayta yoʻnaltiradi.
- `GET /api/auth/oidc/callback` `state` qiymatini tekshiradi, avtorizatsiya
  kodini almashtiradi va ID token imzosini emitentning JWKSʼi orqali
  (`jose` paketining `createRemoteJWKSet` funksiyasi, har bir JWKS URI uchun keshlanadi), `issuer`/`audience`
  tekshiruvlari bilan tasdiqlaydi. `oidcAllowedSubjects` ruxsat roʻyxati majburiy: u
  tokenning `sub` daʼvosiga yoki `email` daʼvosiga mos keladi — email daʼvosi faqat
  `email_verified === true` boʻlganda hisobga olinadi, shuning uchun IdPʼdagi tasdiqlanmagan email hech qachon
  kirish darvozasidan oʻta olmaydi — va roʻyxatda hech qanday yozuv boʻlmasa, qayta chaqiruv barcha kirish urinishlarini rad etadi
  (`not_configured`).
- Muvaffaqiyatli yakunlanganda u parol orqali kirish beradigan **aynan oʻsha** 30 kunlik `auth_token` JWTʼni yaratadi
  (`src/app/api/auth/login/route.ts`), shu sababli boshqaruv paneli sessiyasi
  konveyerining qolgan qismi (avtomatik yangilash, cookie fayli bayroqlari) oʻzgarmaydi —
  OIDC faqat cookie fayli qanday yaratilishini almashtiradi, u taqdim etadigan huquqlarni emas.
- Har bir `oidc*` sozlamasi (`oidcEnabled`, `oidcDisablePasswordLogin`,
  `oidcIssuer`, `oidcClientId`, `oidcClientSecret`, `oidcAllowedSubjects`,
  `oidcRedirectPath`, `oidcScopes`) `SECURITY_IMPACTING_SETTINGS_KEYS`
  (`src/shared/constants/securityImpactingSettings.ts`) ichida joylashgan: soʻrov tanasida boshqaruv
  paroli `currentPassword` sifatida berilmasa, `PATCH /api/settings`
  `400 PASSWORD_REQUIRED` javobini qaytaradi (notoʻgʻri boʻlsa, `401 PASSWORD_MISMATCH`).
  `oidcDisablePasswordLogin` parol orqali _kirishni_ (`POST /api/auth/login`) rad etadi,
  ammo saqlangan parol xeshini qoldiradi va qayta autentifikatsiya hali ham
  `currentPassword` qiymatini unga nisbatan tekshiradi.
- `POST /api/settings/import-json` bu qayta autentifikatsiyani oʻtkazib yuboradi, shuning uchun yozishdan oldin
  `IMPORT_STRIPPED_SETTINGS_KEYS` ichidagi har bir kalitni (oʻsha fayl) olib tashlaydi: parol va
  `currentPassword`, har bir `SECURITY_IMPACTING_SETTINGS_KEYS` yozuvi hamda
  boshqaruv paneli sessiyasi holati (`sessionsValidAfter`, `revokedDashboardSessions`).
  Shu sababli eski zaxira nusxasini import qilish parol
  oʻzgarishi yoki tizimdan chiqish allaqachon yakunlagan sessiyani qayta tiklay olmaydi.

## Marshrut klasslari

`src/server/authz/types.ts` uchta klassni belgilaydi; deterministik tarzda tasniflab bo‘lmaydigan har qanday marshrut `MANAGEMENT` klassiga tushadi.

| Klass        | Tavsif                                                                                                                                                                         | Autentifikatsiya talabi                                                               |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------- |
| `PUBLIC`     | Xavfsizligi aniq belgilangan marshrutlar — tizimga kirish, chiqish, holat, ishga tushirish, tizim salomatligi, dastlabki sozlash.                                              | Talab qilinmaydi                                                                      |
| `CLIENT_API` | Modelga xizmat ko‘rsatish endpointlari — `/api/v1/*`, `/api/v1beta/*`, shuningdek `/v1/*`, `/v1beta/*`, `/chat/completions`, `/responses`, `/models`, `/codex/*` taxalluslari. | Amaldagi `REQUIRE_API_KEY` funksiya bayrog‘i yoqilganida Bearer kaliti talab qilinadi |
| `MANAGEMENT` | Boshqaruv paneli sahifalari, sozlamalar, provayderlar, kalitlar, administrator va diagnostika endpointlari.                                                                    | Boshqaruv paneli sessiyasi YOKI `manage` doirasiga ega Bearer                         |

Ayrim `MANAGEMENT` amallari **faqat operatorlar uchun**: `manage` kalitining o‘zi yetarli emas. Saqlangan
hisob ma’lumotlarini eksport qilish (`GET /api/settings/export-json`, `GET /api/db-backups/export`,
`GET /api/db-backups/exportAll`), sinxronlash tokenini chiqarish (`POST /api/sync/tokens`) va
`admin` CLI kirish tokenini yaratish (`POST /api/cli/tokens`) uchun boshqaruv paneli sessiyasi, lokal CLI
subyekti yoki kirish o‘chirib qo‘yilgan bo‘lishi talab etiladi; istalgan doiradagi API kalitlari va `oma_`
kirish tokenlari `403` javobini oladi. Tekshiruv `src/lib/api/operatorCredential.ts` faylida
(`resolveOperatorCredential()` / `requireOperatorCredential()`) joylashgan.

A few `MANAGEMENT` actions are **operator-only**: a `manage` key is not enough. Exporting stored
credentials (`GET /api/settings/export-json`, `GET /api/db-backups/export`,
`GET /api/db-backups/exportAll`), restoring a backup over the live data
(`POST /api/db-backups/import` including `dryRun=true`, `POST /api/db-backups` restore by id,
`POST /api/settings/import-json`), issuing a sync token (`POST /api/sync/tokens`) and minting an
`admin` CLI access token (`POST /api/cli/tokens`) require a dashboard session, the local CLI
subject, or login disabled; API keys of any scope and `oma_` access tokens get `403`. The check
lives in `src/lib/api/operatorCredential.ts` (`resolveOperatorCredential()` /
`requireOperatorCredential()`).

## Konveyer

```
Kiruvchi so‘rov → src/proxy.ts
  → src/server/authz/pipeline.ts ichidagi runAuthzPipeline()
    1. Ishonchli ichki sarlavhalarni olib tashlash (x-omniroute-auth-*, x-omniroute-route-class)
    2. So‘rov identifikatorini yaratish, marshrutni classifyRoute() orqali tasniflash
    3. Agar pathname == "/" bo‘lsa → /dashboard manziliga yo‘naltirish
    4. Agar tizim yakunlanayotgan bo‘lsa (to‘g‘ri yakunlash) va /api/* bo‘lsa → 503
    5. Agar GET bo‘lmagan /api/* bo‘lsa → checkBodySize() himoyasini tekshirish
    6. Agar OPTIONS bo‘lsa → CORS preflight 204
    7. Agar options.enforce == false bo‘lsa → marshrut sinfi sarlavhalari bilan o‘tkazib yuborish
    8. Aks holda: POLICIES[routeClass].evaluate(ctx)
       - allow  → x-omniroute-auth-{kind,id,label,scopes} ni belgilash → NextResponse.next()
       - reject → correlation_id bilan JSON xatosi (boshqaruv paneli sahifalari → 302 /login)
```

Ishonchli ichki sarlavhalar (`src/server/authz/headers.ts` ichida belgilangan) tasniflashdan oldin **kiruvchi so‘rovlardan olib tashlanadi** — mijozlar boshqa subyekt nomidan ish ko‘rish uchun `x-omniroute-auth-*` sarlavhalarini oldindan kirita olmaydi.

### Siyosat shartnomalari

Har bir marshrut sinfi `src/server/authz/policies/` ichida o‘z siyosatiga ega:

- **`publicPolicy`** (`policies/public.ts`) — har doim `allow({ kind: "anonymous", id: "anonymous" })` qaytaradi.
- **`clientApiPolicy`** (`policies/clientApi.ts`) — Bearer qiymatini ajratib oladi va `validateApiKey()` orqali tekshiradi. Faqat amaldagi `REQUIRE_API_KEY` funksiya bayrog‘i o‘chirilganida anonim kirishga o‘tadi. Amaldagi bayroq `isRequireApiKeyEnabled()` orqali aniqlanadi (`DB funksiya bayrog‘i ustuvor qiymati > process.env.REQUIRE_API_KEY > standart qiymat`), shu sababli boshqaruv panelidagi funksiya bayroqlari va muhit o‘zgaruvchilari `/api/v1/*`, `/api/v1beta/*` hamda taxalluslarni izchil boshqaradi; aniqlashdagi xatoliklar kirishni yopadi. Mijoz API marshrutlarida, jumladan boshqaruv panelining modellar katalogi foydalanadigan `/api/v1/models` marshrutida, boshqaruv paneli sessiyasiga ega so‘rovlarga ruxsat beradi.
- **`managementPolicy`** (`policies/management.ts`) — boshqaruv paneli sessiyasini, ichki model sinxronlash so‘rovlarini (`/api/providers/[name]/(sync-models|models)` bilan moslashtiriladi) qabul qiladi yoki `isAuthRequired()` false qaytarsa, tekshiruvni butunlay o‘tkazib yuboradi. Bearer tokeni mavjud, ammo yaroqsiz bo‘lsa 403 (`AUTH_001`), aks holda 401 qaytaradi. Shuningdek, autentifikatsiyaning har qanday tarmog‘idan oldin marshrut himoyasi darajalarini (LOCAL_ONLY / ALWAYS_PROTECTED) qo‘llaydi — [Marshrut himoyasi darajalari](../security/ROUTE_GUARD_TIERS.md) bo‘limiga qarang. `LOCAL_ONLY_MANAGE_SCOPE_BYPASS_PREFIXES` ichidagi LOCAL_ONLY yo‘llariga (hozirda: `/api/mcp/`) Bearer kaliti `manage` doirasiga ega bo‘lsa, loopback bo‘lmagan manzildan kirish mumkin; boshqa barcha LOCAL_ONLY yo‘llari doiradan qat’i nazar faqat loopback orqali kirish talabini qat’iy saqlaydi.

Muvaffaqiyatli siyosat `kind ∈ { client_api_key, dashboard_session, management_key, anonymous }` qiymatiga ega `AuthSubject` qaytaradi. Quyi oqimdagi ishlov beruvchilar autentifikatsiya mantiqini qayta ishga tushirish o‘rniga uni `src/server/authz/assertAuth.ts` ichidagi `assertAuth(request, "CLIENT_API")` orqali o‘qishi mumkin.

## Ommaviy marshrutlar roʻyxati

`src/shared/constants/publicApiRoutes.ts` — aniq ruxsat etilganlar roʻyxati:

Roʻyxat **shakliga** koʻra ajratilgan va bu ajratish xavfsizlik uchun muhim (GHSA-74g9-q8f6-793h): prefiks `startsWith()` orqali moslashtiriladi, shuning uchun u boshlangʻich belgilari bir xil boʻlgan barcha yondosh yoʻllarga ham mos keladi.
`/api/usage/om-usage` prefiks sifatida `/api/usage/om-usage<anything>` yoʻlini OMMAVIY deb belgilagan va Next buni `/api/usage/[connectionId]` ga yoʻnaltiradi — bu oʻz autentifikatsiyasiga ega boʻlmagan ishlov beruvchi.

```ts
// Haqiqiy quyi daraxtlar. Har bir yozuv "/" bilan tugashi SHART (bu birlik testi orqali tekshiriladi).
PUBLIC_API_ROUTE_PREFIXES = [
  "/api/auth/oidc/",
  "/api/v1/", // classify ichida CLIENT_API sifatida koʻriladi, "autentifikatsiyasiz ommaviy" sifatida emas
  "/api/oauth/",
  "/api/codex/connect/",
  "/api/telegram/",
  "/api/cursor-cli/",
];

// Oxiridagi qiya chiziq bilan yoki usiz, AYNAN moslashtiriladigan alohida marshrutlar.
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

// CORS origin cheklovi yumshatilishi ham qoʻllanadigan faqat oʻqish uchun alohida marshrutlar.
PUBLIC_READONLY_CORS_API_ROUTES = [
  "/api/health/ping",
  "/api/monitoring/health",
  "/api/settings/require-login",
];

// CORS cheklovi yumshatilishi qoʻllanmaydigan faqat oʻqish uchun alohida marshrut.
PUBLIC_READONLY_API_ROUTES_EXACT = new Set(["/api/health"]);

PUBLIC_READONLY_METHODS = new Set(["GET", "HEAD", "OPTIONS"]);
```

Faqat oʻqish uchun marshrutlar faqat xavfsiz metodlar uchun ommaviydir. Eslatma: `classifyRoute()` `/api/v1/*` va `/api/v1beta/*` yoʻllarini PUBLIC standart holatidan chiqarib tashlaydi — Bearer kaliti siyosati baribir qoʻllanishi uchun ular har doim `CLIENT_API` boʻladi.

## Yangi marshrut qoʻshish

### 1-andoza — Ommaviy mijoz API endpointi (Bearer autentifikatsiyasi)

`/api/v1/` va `/api/v1beta/` ostidagi marshrutlar avtomatik ravishda `CLIENT_API` sifatida tasniflanadi. Oraliq dastur Bearer tekshiruvini majburiy qiladi; marshrut ishlov beruvchilari uni qayta bajarishi shart emas, ammo zarur boʻlsa subyektni oʻqishi mumkin.

```typescript
// src/app/api/v1/your-route/route.ts
import { NextRequest, NextResponse } from "next/server";
import { assertAuth } from "@/server/authz/assertAuth";

export async function POST(req: NextRequest) {
  const subject = assertAuth(req, "CLIENT_API");
  // subject.kind === "client_api_key" | "anonymous" | "dashboard_session"
  // ... ishlov beruvchi mantiqi
}
```

### 2-andoza — Boshqaruv endpointi (sessiya yoki Bearer + manage)

`src/lib/api/requireManagementAuth.ts` ichidagi `requireManagementAuth()` dan foydalaning:

```typescript
import { requireManagementAuth } from "@/lib/api/requireManagementAuth";

export async function POST(request: Request) {
  const rejection = await requireManagementAuth(request);
  if (rejection) return rejection;
  // ... ishlov beruvchi mantiqi
}
```

`requireManagementAuth()` muvaffaqiyatli boʻlsa `null`, aks holda JSON xatosi boʻlgan `Response` qaytaradi:

- 401 `AUTH_001` "Autentifikatsiya talab qilinadi" — umuman hisob maʼlumotlari yoʻq
- 403 — Bearer yaroqsiz **yoki** Bearer mavjud, ammo kalitda `manage` / `admin` doirasi yoʻq

`hasManageScope(scopes)` `"manage"` yoki `"admin"` uchun true qaytaradi.

### 3-andoza — Ommaviy ruxsat etilganlar roʻyxatiga qoʻshish

Toʻplamni qulaylikka qarab emas, shakliga qarab tanlang. Bitta marshrut `PUBLIC_API_ROUTES_EXACT` ga (yoki faqat GET uchun `PUBLIC_READONLY_CORS_API_ROUTES` ga) qoʻshiladi; faqat haqiqiy quyi daraxt `PUBLIC_API_ROUTE_PREFIXES` ga qoʻshiladi va u **`/` bilan tugashi shart**. Bitta marshrutni prefikslar roʻyxatiga kiritish uning boshlangʻich belgilariga ega barcha yondosh yoʻllarni, jumladan keyinchalik qoʻshilgan dinamik segmentli qardosh yoʻllarni ham ommaviy qiladi (GHSA-74g9-q8f6-793h). `tests/unit/public-api-routes.test.ts`, `tests/unit/authz/public-route-exact-match.test.ts` va `tests/unit/authz/classify.test.ts` fayllaridagi birlik testlarini yangilang.

## Doiralar

Uchta nom maydoni. Har bir tekshiruvchi faqat o'zining satrlarini o'qiydi. Yonma-yon taqqoslash, jumladan, nima uchun `manage` `read:compression` uchun `scopeMatches`ni bajara olmasligi va nima uchun `read` kirish tokeni `PATCH /api/keys/{id}`ni bajara olmasligi [Uchta nom maydoni](../frameworks/MCP-SERVER.md#three-scope-namespaces)da keltirilgan.

API kalitlari `scopes` massivini o'z ichiga oladi (`api_keys.scopes`da JSON sifatida saqlanadi, qarang `src/lib/db/apiKeys.ts`).

### Boshqaruv doirasi

- `manage` / `admin` — `hasManageScope`. Boshqaruv API marshrutlariga tashuvchi orqali kirish.
- `mcp:connect`, `self:usage`, `self:account-quota` va `policy:bypass-provider-quota` qo'shimcha aniq mos keladigan doiralardir. Ular `MANAGEMENT_API_KEY_SCOPES`dan tashqarida joylashgan. `mcp:connect` faqat `/api/mcp/` non-loopback ajratmasini ochadi.

### MCP asbob doiralari

Katalog va mos kelish qoidalari (bir xil satr yoki `*` bilan tugaydigan berilgan doira): [MCP asbob doiralari](../frameworks/MCP-SERVER.md#mcp-tool-scopes). `src/shared/constants/mcpScopes.ts`dagi `MCP_SCOPE_LIST` to'liq katalog emas, balki asl terilgan kichik to'plamdir. Ijro etish `open-sse/mcp-server/scopeEnforcement.ts`da `resolveCallerScopeContext()` MCP autentifikatsiya ma'lumotlari, so'rov metama'lumotlari yoki `OMNIROUTE_MCP_SCOPES`dan doiralarni hal qilgandan so'ng amalga oshiriladi. U `OMNIROUTE_MCP_ENFORCE_SCOPES=true` bo'lmaguncha o'chirilgan holatda qoladi.

### Kirish tokeni doiralari

`oma_live_…` tokenlarida `read` / `write` / `admin`, `scopeSatisfies` (`src/lib/accessTokens/scopes.ts`) bo'yicha tartiblangan. Bu daraja faqat kirish tokeni hisob ma'lumotlariga tegishli. Qarang [Boshqaruv autentifikatsiyasi](../guides/MANAGEMENT-AUTH.md).

## Autentifikatsiya talabi almashtirgichi

`src/shared/utils/apiAuth.ts` ichidagi `isAuthRequired()` soʻrov uchun **har qanday** autentifikatsiya majburiy yoki majburiy emasligini belgilaydi:

- `settings.requireLogin === false` → autentifikatsiya global miqyosda oʻchiriladi.
- Parol sozlanmagan **va** `INITIAL_PASSWORD` muhit oʻzgaruvchisi mavjud emas → boshlangʻich sozlash rejimi dastlabki sozlash ustasi va loopback soʻrovlariga ruxsat beradi, ammo tarmoqqa ochiq soʻrovlar uchun baribir hisob maʼlumotlari talab qilinadi.
- Har qanday DB xatosi → yopiq holatda rad etiladi (standart holatda xavfsiz).

Mijoz API kalitini majburiy tekshirish `process.env.REQUIRE_API_KEY` qiymatini bevosita oʻqishdan emas, `src/shared/utils/featureFlags.ts` ichidagi `isRequireApiKeyEnabled()` funksiyasidan foydalanadi. Bu joylashtirilgan instansiyalar uchun muhim: Dashboard → Feature Flags boʻlimida `REQUIRE_API_KEY` qiymatini almashtirish DB bekor qilish qiymatini saqlaydi va `/v1/*`, `/v1beta/*`, `/models`, `/responses`, `/chat/completions`, `/codex/*` hamda ushbu yordamchi funksiyadan foydalanadigan boshqa mijoz API autentifikatsiya tekshiruvlariga darhol taʼsir qiladi. Agar xususiyat bayroqlari omborini oʻqib boʻlmasa, mijoz API autentifikatsiyasi yopiq holatda rad etiladi va kalit talab qiladi.

## Moslikni buzuvchi oʻzgarish — v3.8.0

`/api/v1/agents/tasks/*` va `/api/resilience/model-cooldowns` endpointlari **endi boshqaruv autentifikatsiyasini talab qiladi** (`588a0333` kommiti). Avval `manage` qamrovisiz oddiy API kalitini yuborgan mijozlar `403` javobini oladi. Migratsiya: API Keys boshqaruv panelida kalitga `manage` qamrovini bering yoki tizimga kirilgan boshqaruv paneli seansidan foydalaning.

## Xatti-harakat oʻzgarishi — v3.8.2

`/api/mcp/*` (masofaviy MCP serveri) hali ham standart holatda LOCAL_ONLY, ammo `Authorization: Bearer <api-key>` sarlavhasida `manage` qamrovi mavjud boʻlsa, endi loopback boʻlmagan soʻrovlarni ham qabul qiladi. Ushbu istisno `src/server/authz/routeGuard.ts` ichidagi `LOCAL_ONLY_MANAGE_SCOPE_BYPASS_PREFIXES` orqali har bir yoʻl uchun alohida boshqariladi; yonma-yon joylashgan `/api/cli-tools/runtime/*` LOCAL_ONLY prefiksini ataylab chetlab oʻtib boʻlmaydi, chunki u ixtiyoriy quyi jarayonlarni ishga tushirishi mumkin. Loopback boʻlmagan manzildan `/api/mcp/*` ga yuborilgan anonim soʻrovlar `403 LOCAL_ONLY` javobini qaytarishda davom etadi — har qanday yangi LOCAL_ONLY yoʻli uchun standart holat qatʼiy loopback boʻlib qoladi. [Yoʻnalish himoyachisi darajalari](../security/ROUTE_GUARD_TIERS.md#manage-scope-carve-out) boʻlimiga qarang.

## Sinov

- Birlik sinovlari: `tests/unit/authz/` — `classify.test.ts`, `pipeline.test.ts`, `client-api-policy.test.ts`, `management-policy.test.ts`, `public-policy.test.ts`.
- Ommaviy ruxsat berilganlar roʻyxati: `tests/unit/public-api-routes.test.ts`.
- Yoʻnaltirilgan ishga tushirish: `node --import tsx/esm --test tests/unit/authz/classify.test.ts`.

## Nosozliklarni tuzatish

Konveyer javoblarga har doim quyidagi sarlavhalarni qoʻshadi:

```
x-request-id:               <korrelyatsiya identifikatori, xato javoblari tanasida qaytariladi>
x-omniroute-route-class:    PUBLIC | CLIENT_API | MANAGEMENT
```

Autentifikatsiya qilingan soʻrovlar uchun yuqori oqimdagi (ishlov beruvchi tomonidagi) soʻrov sarlavhalari quyidagilarni ham oʻz ichiga oladi:

```
x-omniroute-auth-kind:      client_api_key | dashboard_session | management_key | anonymous
x-omniroute-auth-id:        key_<oxirgi-4> | "dashboard" | "anonymous"
x-omniroute-auth-label:     (ixtiyoriy)
x-omniroute-auth-scopes:    vergul bilan ajratilgan roʻyxat
```

Ishlov beruvchilar ichida `assertAuth(req, expectedClass)` dan foydalaning — agar oraliq dasturiy taʼminot chetlab oʻtilgan boʻlsa, u `AUTHZ_NOT_INITIALIZED` kodli `AuthzAssertionError` xatosini chiqaradi (testlarda konfiguratsiya regressiyalarini aniqlash uchun foydali).

## Yana qarang

- [API_REFERENCE.md](../reference/API_REFERENCE.md) — har bir yakuniy nuqta uchun avtorizatsiya belgisi
- [COMPLIANCE.md](../security/COMPLIANCE.md) — avtorizatsiya hodisalari uchun audit jurnali
- [MCP-SERVER.md](../frameworks/MCP-SERVER.md#three-scope-namespaces) — uchta qamrov nomfazo va MCP asbob-qamrov katalogi
- Manba: `src/server/authz/`, `src/lib/api/requireManagementAuth.ts`
