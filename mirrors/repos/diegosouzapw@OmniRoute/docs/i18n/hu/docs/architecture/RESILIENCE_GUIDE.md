# Resilience Guide (Magyar)

🌐 **Languages:** 🇺🇸 [English](../../../../architecture/RESILIENCE_GUIDE.md) · 🇪🇹 [am](../../../am/docs/architecture/RESILIENCE_GUIDE.md) · 🇸🇦 [ar](../../../ar/docs/architecture/RESILIENCE_GUIDE.md) · 🇦🇿 [az](../../../az/docs/architecture/RESILIENCE_GUIDE.md) · 🇧🇬 [bg](../../../bg/docs/architecture/RESILIENCE_GUIDE.md) · 🇧🇩 [bn](../../../bn/docs/architecture/RESILIENCE_GUIDE.md) · 🇨🇿 [cs](../../../cs/docs/architecture/RESILIENCE_GUIDE.md) · 🇩🇰 [da](../../../da/docs/architecture/RESILIENCE_GUIDE.md) · 🇩🇪 [de](../../../de/docs/architecture/RESILIENCE_GUIDE.md) · 🇬🇷 [el](../../../el/docs/architecture/RESILIENCE_GUIDE.md) · 🇪🇸 [es](../../../es/docs/architecture/RESILIENCE_GUIDE.md) · 🇪🇪 [et](../../../et/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇷 [fa](../../../fa/docs/architecture/RESILIENCE_GUIDE.md) · 🇫🇮 [fi](../../../fi/docs/architecture/RESILIENCE_GUIDE.md) · 🇫🇷 [fr](../../../fr/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇪 [ga](../../../ga/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [gu](../../../gu/docs/architecture/RESILIENCE_GUIDE.md) · 🇳🇬 [ha](../../../ha/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇱 [he](../../../he/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [hi](../../../hi/docs/architecture/RESILIENCE_GUIDE.md) · 🇭🇷 [hr](../../../hr/docs/architecture/RESILIENCE_GUIDE.md) · 🇦🇲 [hy](../../../hy/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇩 [id](../../../id/docs/architecture/RESILIENCE_GUIDE.md) · 🇳🇬 [ig](../../../ig/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇹 [it](../../../it/docs/architecture/RESILIENCE_GUIDE.md) · 🇯🇵 [ja](../../../ja/docs/architecture/RESILIENCE_GUIDE.md) · 🇬🇪 [ka](../../../ka/docs/architecture/RESILIENCE_GUIDE.md) · 🇰🇭 [km](../../../km/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [kn](../../../kn/docs/architecture/RESILIENCE_GUIDE.md) · 🇰🇷 [ko](../../../ko/docs/architecture/RESILIENCE_GUIDE.md) · 🇱🇹 [lt](../../../lt/docs/architecture/RESILIENCE_GUIDE.md) · 🇱🇻 [lv](../../../lv/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [ml](../../../ml/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [mr](../../../mr/docs/architecture/RESILIENCE_GUIDE.md) · 🇲🇾 [ms](../../../ms/docs/architecture/RESILIENCE_GUIDE.md) · 🇲🇹 [mt](../../../mt/docs/architecture/RESILIENCE_GUIDE.md) · 🇲🇲 [my](../../../my/docs/architecture/RESILIENCE_GUIDE.md) · 🇳🇵 [ne](../../../ne/docs/architecture/RESILIENCE_GUIDE.md) · 🇳🇱 [nl](../../../nl/docs/architecture/RESILIENCE_GUIDE.md) · 🇳🇴 [no](../../../no/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [or](../../../or/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [pa](../../../pa/docs/architecture/RESILIENCE_GUIDE.md) · 🇵🇭 [phi](../../../phi/docs/architecture/RESILIENCE_GUIDE.md) · 🇵🇱 [pl](../../../pl/docs/architecture/RESILIENCE_GUIDE.md) · 🇵🇹 [pt](../../../pt/docs/architecture/RESILIENCE_GUIDE.md) · 🇧🇷 [pt-BR](../../../pt-BR/docs/architecture/RESILIENCE_GUIDE.md) · 🇷🇴 [ro](../../../ro/docs/architecture/RESILIENCE_GUIDE.md) · 🇷🇺 [ru](../../../ru/docs/architecture/RESILIENCE_GUIDE.md) · 🇱🇰 [si](../../../si/docs/architecture/RESILIENCE_GUIDE.md) · 🇸🇰 [sk](../../../sk/docs/architecture/RESILIENCE_GUIDE.md) · 🇸🇮 [sl](../../../sl/docs/architecture/RESILIENCE_GUIDE.md) · 🇷🇸 [sr](../../../sr/docs/architecture/RESILIENCE_GUIDE.md) · 🇸🇪 [sv](../../../sv/docs/architecture/RESILIENCE_GUIDE.md) · 🇰🇪 [sw](../../../sw/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [ta](../../../ta/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [te](../../../te/docs/architecture/RESILIENCE_GUIDE.md) · 🇹🇭 [th](../../../th/docs/architecture/RESILIENCE_GUIDE.md) · 🇹🇷 [tr](../../../tr/docs/architecture/RESILIENCE_GUIDE.md) · 🇺🇦 [uk-UA](../../../uk-UA/docs/architecture/RESILIENCE_GUIDE.md) · 🇵🇰 [ur](../../../ur/docs/architecture/RESILIENCE_GUIDE.md) · 🇺🇿 [uz](../../../uz/docs/architecture/RESILIENCE_GUIDE.md) · 🇻🇳 [vi](../../../vi/docs/architecture/RESILIENCE_GUIDE.md) · 🇳🇬 [yo](../../../yo/docs/architecture/RESILIENCE_GUIDE.md) · 🇨🇳 [zh-CN](../../../zh-CN/docs/architecture/RESILIENCE_GUIDE.md) · 🇹🇼 [zh-TW](../../../zh-TW/docs/architecture/RESILIENCE_GUIDE.md)

---

Az OmniRoute három különálló, de egymással összefüggő rezilienciamechanizmussal rendelkezik. Mindegyik eltérő hatókörrel és céllal bír. Az útválasztási viselkedés hibakeresésekor kezelje őket különállóként.

![Háromrétegű rezilienciamodell](../diagrams/exported/resilience-3layers.svg)

> Forrás: [diagrams/resilience-3layers.mmd](../diagrams/resilience-3layers.mmd)

## 1. Szolgáltatói áramkör-megszakító

**Hatókör:** a teljes szolgáltató (például `glm`, `openai`, `anthropic`).

**Cél:** ne küldjön több forgalmat olyan szolgáltatónak, amelynél az upstream/szolgáltatási szinten ismétlődő hibák jelentkeznek.

**Megvalósítás:**

- Alaposztály: `src/shared/utils/circuitBreaker.ts`
- Bekötés: `src/sse/handlers/chatHelpers.ts`, `src/sse/handlers/chat.ts`
- Állapot API: `GET /api/monitoring/health`
- Visszaállítási API: `POST /api/resilience/reset`
- Burkolók: `open-sse/services/accountFallback.ts`
- Adatbázistábla: `domain_circuit_breakers`

**Állapotok:**

- `CLOSED` — a normál forgalom engedélyezett
- `DEGRADED` — a forgalom továbbra is engedélyezett, de a szolgáltatói hibák megnövekedett számát nyomon követi a rendszer
- `OPEN` — a szolgáltató ideiglenesen blokkolva van; a kombinált útválasztás kihagyja
- `HALF_OPEN` — a visszaállítási időkorlát letelt; egy tesztkérés engedélyezett

**Konfigurálható alapértékek (`open-sse/config/constants.ts`, elérhetők a Vezérlőpult → Beállítások → Reziliencia menüpontban):**

| Osztály   | Csökkentett mód ennyi után | Megnyitás ennyi után | Visszaállítási időkorlát |
| --------- | -------------------------- | -------------------- | ------------------------ |
| OAuth     | 5 hiba                     | 8 hiba               | 60s                      |
| API-kulcs | 7 hiba                     | 12 hiba              | 30s                      |
| Helyi     | származtatott              | 2 hiba               | 15s                      |

A `degradationThreshold` szabályozza, hogy egy szolgáltató mikor lépjen `DEGRADED` állapotba; a `failureThreshold` pedig azt, hogy mikor nyíljon meg és mikor hagyja ki a rendszer. A helyi szolgáltatói profilok egyelőre nem érhetők el a Reziliencia beállítási oldalán.

**Aktiváló kódok:** kizárólag a szolgáltatói szintű `[408, 500, 502, 503, 504]` állapotok. NE aktiválja fiókszintű hibák esetén (a legtöbb 401/403/429 — ezek a várakoztatáshoz vagy a kizáráshoz tartoznak).

**Lusta helyreállítás:** amikor az `OPEN` lejár, a `getStatus()`, a `canExecute()` és a `getRetryAfterMs()` `HALF_OPEN` állapotra frissíti az állapotot. Nincs szükség háttérben futó időzítőre.

---

### Opcionális globális szolgáltatói várakoztatás (időablak-kapu)

Egy negyedik, **opcionális** réteg (`PROVIDER_COOLDOWN_ENABLED`, alapértelmezetten **kikapcsolva**) a kérések között is megőrzi a hibás szolgáltatókra vonatkozó információkat az
`open-sse/services/providerCooldownTracker.ts` fájlban, amelyet a kombinált célpontok
feloldása használ, így az egymást követő kombinált kérések nem próbálják újra végig ugyanazt a nemrég
meghibásodott szolgáltatót. A szolgáltatói szintű bejegyzések figyelembe veszik a `PROVIDER_PROFILES` időablak-kapuját:

| Profil    | aktiválás ennyi után (`providerFailureThreshold`) | ezen belül (`providerFailureWindowMs`) | várakoztatás időtartama (`providerCooldownMs`) |
| --------- | ------------------------------------------------: | -------------------------------------: | ---------------------------------------------: |
| OAuth     |                                              `10` |                                `15min` |                                         `5min` |
| API-kulcs |                                              `15` |                                `30min` |                                        `10min` |

A küszöbérték alatt a szolgáltató **nem** tekintendő várakoztatott állapotúnak; egy sikeres
művelet törli az időablakot. A kapcsolatszintű bejegyzések (`provider:connectionId`) továbbra is az
exponenciális `minRetryCooldownMs → maxRetryCooldownMs` visszalépési stratégiát használják. Felülírások:
`OMNIROUTE_PROVIDER_BREAKER_{OAUTH,API_KEY}_{FAILURE_THRESHOLD,FAILURE_WINDOW_MS,COOLDOWN_MS}`.
Regresszióvédelmi teszt: `tests/unit/provider-cooldown-window-gate.test.ts`.

## 2. Kapcsolati várakozási idő

**Hatókör:** egyetlen szolgáltatói kapcsolat/fiók/kulcs.

**Cél:** egy hibás kulcs kihagyása, miközben ugyanazon szolgáltató többi kapcsolata továbbra is kiszolgálja a kéréseket.

**Megvalósítás:**

- Elérhetetlenként való megjelölés: `src/sse/services/auth.ts::markAccountUnavailable()`
- Kiválasztás: `getProviderCredentials*` ugyanabban a fájlban
- Várakozási idő kiszámítása: `open-sse/services/accountFallback.ts::checkFallbackError()`
- Beállítások: `src/lib/resilience/settings.ts`

**Kapcsolatonkénti mezők:**

- `rateLimitedUntil` — időbélyeg, ameddig a várakozási idő tart
- `testStatus: "unavailable"`
- `lastError`, `lastErrorType`, `errorCode`
- `backoffLevel` — exponenciális visszalépési számláló

**Alapértelmezett várakozási idők:**

- OAuth-alapérték: 5 s
- API-kulcs-alapérték: 3 s
- API-kulcs 429: előnyben részesíti a felsőbb szintű szolgáltató `Retry-After`/visszaállítási fejléceit vagy az értelmezhető visszaállítási szöveget
- Visszalépés: `baseCooldownMs * 2 ** failureIndex`

**Túlterhelési roham elleni védelem:** megakadályozza, hogy az egyidejű hibák túlzottan meghosszabbítsák a várakozási időt, vagy kétszer növeljék a `backoffLevel` értékét.

**Végállapotok (NEM várakozási idők):**

- `banned` — tiltott kulcsszó/fióktiltás észlelésekor kerül beállításra (lásd: [BAN_DETECTION](../security/BAN_DETECTION.md)), valamint három egymást követő, kérésenkénti felsőbb szintű elutasítás után (`request_rejected`, például Anthropic OAuth 403 „Request not allowed” — `open-sse/services/requestRejectedStreak.ts`); egyetlen elutasítás csak várakozási állapotba helyezi a kapcsolatot
- `expired` (korlátozott számú újrapróbálkozás után válik végállapottá — `EXPIRED_RETRY_MAX = 3` exponenciális visszalépéssel —, így az átmeneti OAuth-hibák maguktól helyreállhatnak, mielőtt a fiók véglegesen deaktiválódna)
- `credits_exhausted`

Ezek mindaddig megmaradnak, amíg a hitelesítő adatok meg nem változnak, vagy egy üzemeltető vissza nem állítja őket. A végállapotokat nem szabad átmeneti várakozási állapottal felülírni.

**Lusta helyreállítás:** amikor a `rateLimitedUntil` időpontja elmúlt, a kapcsolat ismét kiválaszthatóvá válik. Sikeres használatkor a `clearAccountError()` törli az összes hibamezőt.

### Munkamenet-affinitás (#7274)

**Hatókör:** egy ügyfél-munkamenet (`X-Session-Id` / `x-codex-session-id` / `x-omniroute-session` fejléc), amely egy kapcsolathoz van rögzítve, **bármely** szolgáltató esetén.

**Cél:** egy többfordulós ügynök (Claude Code, aider, egyéni ügynökök) ugyanazon a fiókon tartása a kérések között, csökkentve a fiókok közötti kontextusvesztést és az ismétlődő hidegindítási 429-es hibákat azoknál a szolgáltatóknál, amelyek fiókonkénti munkamenet-állapotot használnak.

**Megvalósítás:**

- TTL feloldása: `src/sse/services/sessionAffinityPin.ts::resolveSessionAffinityTtlMs()`
- Rögzítés kiválasztása/létrehozása: `src/sse/services/sessionAffinityPin.ts::selectSessionAffinityConnection()`
- Fejléc kinyerése (általános, bármely szolgáltató): `src/sse/services/auth.ts::extractSessionAffinityKey()`
- Tartós rögzítési tábla: `sessionAccountAffinity` (`src/lib/db/sessionAccountAffinity.ts`)
- Beállítás: `sessionAffinityTtlMs` (globális TTL ezredmásodpercben, a `0` letiltja) — `src/lib/db/settings.ts`. A kizárólag Codexhez tartozó `codexSessionAffinityTtlMs` névről a `124_generic_session_affinity_ttl.sql` migráció nevezte át, amely minden korábban konfigurált Codex TTL-t átvisz új alapértelmezett értékként.

A #7274 előtt a `resolveSessionAffinityTtlMs()` minden, nem `codex` szolgáltató esetén azonnal `0` értékkel tért vissza, ezért a TTL-beállításnak (és a munkamenet-fejléceknek) máshol nem volt hatása, noha a rögzítési mechanizmus és a fejléckinyerés már szolgáltatófüggetlen volt. A javítás eltávolította ezt a korai visszatérést; a TTL mostantól egységesen alkalmazandó minden szolgáltatóra, ha globális értékét `0` fölé állítják.

A három munkamenet-affinitási fejlécet a rendszer soha nem továbbítja a felsőbb szintű szolgáltatónak — a végrehajtók saját felsőbb szintű fejléceiket az alapoktól építik fel, ahelyett, hogy továbbítanák az ügyfél fejléceit, így ez kizárólag belső korrelációs azonosító marad.

### Kizárólagos felügyelt munkamenet-kapcsolati bérletek

**Hatókör:** egy aktív felügyelt HTTP-ügyfél/munkamenet egyetlen alkalmas OmniRoute-kapcsolatot birtokol.

**Cél:** tartós, kizárólagos kapcsolattulajdont biztosítani azoknak az ügyfeleknek, amelyeknek szigorú útválasztási
korlátra van szükségük a kérések között. Ez eltér a munkamenet-affinitástól, amely egy enyhe folytonossági preferencia:
a kizárólagos bérlet életciklus-állapotot őriz az SQLite-ban, kikényszeríti az aktív tulajdonos és az
aktív kapcsolat globális egyediségét, valamint a szolgáltatói továbbítás előtt elutasítja az elavult generációt.

A funkció API-kulcsonként külön engedélyezhető. Egy felügyelt kulcsnak rendelkeznie kell a `lease:exclusive` hatókörrel és egy
explicit, nem üres `allowedConnections` listával. Bármely HTTP-ügyfél használhatja az életciklus-végpontot; nincs szükség
ügyfélnévre, felhasználói ügynökre, szolgáltatóra, OAuth-módszerre vagy modellre. A bérlet egy kapcsolatot birtokol,
nem pedig egy modellt, ezért a modellváltás megtartja a kötést, amíg a kapcsolat a szokásos feltételek szerint
alkalmas marad. A normál modell-, kvóta-, állapot-, várakozásiidő- és engedélyezésilista-szabályok továbbra is mérvadók, és
ugyanazt a generációt egy másik szabad, alkalmas kapcsolatra válthatják át.

Az életciklus a `POST /api/v1/session-leases` végponton keresztül kezelhető az `acquire`, `renew` és `release` JSON-műveletekkel.
A felügyelt következtetési kérések az átlátszatlan `X-OmniRoute-Lease-Owner` értéket és a pontos
`X-OmniRoute-Lease-Generation` értéket adják meg. A tulajdonos azonosítója `vlo_` előtagból és azt követő 43 base64url-karakterből áll; csak
az SHA-256 kivonata kerül tárolásra. Minden végső továbbítási korlát azonosítja a hitelesített API-kulcs azonosítóját és
az aktív kapcsolat azonosítóját is. A bérletvezérlő fejlécek eltávolításra kerülnek a naplókból, a megőrzött kérési pillanatképekből és
a felsőbb szintű végrehajtók fejléceiből.

Ha a szokásos útválasztás rendelkezik alkalmas felügyelt jelöltekkel, de minden szabad jelöltet egy
idegen aktív bérlet foglal el, az OmniRoute HTTP `429` választ, bérleti kapacitás hiányát jelző kódot,
kapacitásra várakozó állapotot, valamint a legkorábbi releváns lejáratból származtatott, korlátozott `Retry-After` értéket ad vissza.
Az alkalmassági halmaz szokásos üressége nem bérleti ütközés, és megtartja a meglévő útválasztási hibaszemantikát.

A kapcsolódó mechanizmusok továbbra is elkülönülnek:

- Az OAuth-munkamenetek foglaltsága folyamaton belüli, enyhe elosztást biztosít az OAuth-fiókok számára.
- A fiókszemaforok kérés-egyidejűségi engedélyeket adnak, amelyek a kérés befejezésekor megszűnnek.
- A kizárólagos felügyelt munkamenet-bérletek tartós életciklus-tulajdont biztosítanak generációs korláttal.

---

## 3. Modellzárolás

**Hatókör:** szolgáltató + kapcsolat + modell hármasa.

**A kulcs hatóköre állapotkód szerint:** a hibát jelző állapotkód határozza meg, hogy a zárolás melyik kulcsba kerül
(`resolveLockoutScope()` az `open-sse/services/accountFallback/exactModelLock.ts` fájlban):

- `429` / `403` / `402` — kvótára vagy jogosultságra utaló jelzés — zárolja a **kvótacsaládot**:
  codex esetén a kapcsolat teljes `codex` / `spark` hatókörét (a kapcsolat minden
  `gpt-5*` modelljét), más szolgáltatóknál pedig a `getQuotaScopedModelForProvider()` által meghatározott hatókört.
- A `404` az alapmodellt zárolja (a `getModelLockKey()` leszűkíti a `not_found` esetet).
- Minden más állapotkód — az `5xx` átviteli-/szerverhibák, valamint az OmniRoute
  minőségellenőrzése által előállított `502` — kizárólag a **pontos**
  szolgáltató/kapcsolat/modell hármast zárolja. Egy modell hibás adatfolyama nem bizonyíték
  a fiók kvótahelyzetére; e szabály előtt egyetlen üres válasz a
  `codex/gpt-5.6-luna` modellen 2–30 percre (fokozatosan növekvő időtartammal) eltávolította
  az adott kapcsolat összes `gpt-5*` modelljét az útválasztásból,
  miközben a kvótája érintetlen maradt.
- A hívó explicit `scope` beállítása mindig elsőbbséget élvez (az Antigravity az `"exact"` értéket adja át).

**Cél:** elkerülni egy teljes kapcsolat letiltását, amikor csak egyetlen modell nem érhető el, vagy annak kvótája korlátozott.

**Példák:**

- Modellenkénti kvótát alkalmazó szolgáltatók, amelyek 429-et adnak vissza
- Helyi szolgáltatók, amelyek 404-et adnak vissza egyetlen hiányzó modell esetén
- Szolgáltatóspecifikus mód-/modelljogosultsági hibák (pl. Grok módok)

**Megvalósítás:** `open-sse/services/accountFallback.ts` — `lockModel()`, `clearModelLock()`, `getAllModelLockouts()`.

### Modell-lehűlési irányítópult (v3.8.0)

Felhasználói felület: Beállítások → Modell-lehűlések (`src/app/(dashboard)/dashboard/settings/components/ModelCooldownsCard.tsx`)

Az aktív zárolásokat a következő adatokkal sorolja fel: szolgáltató, kapcsolat, modell, ok, expiresAt. Az üzemeltetők a kártyáról manuálisan újra engedélyezhetnek egy modellt.

**REST API:**

- `GET /api/resilience/model-cooldowns` — aktív zárolások listázása
- `DELETE /api/resilience/model-cooldowns` — manuális újraengedélyezés. Törzs: `{provider, connection, model}`. Hitelesítés: felügyeleti.

### Zárolási beállítások felhasználói felülete + siker-alapú lecsengéses helyreállítás (v3.8.23)

A modellzárolás a mindig bekapcsolt, beégetett működésből teljesen konfigurálható,
külön bekapcsolható funkcióvá vált, saját beállításkártyával és öngyógyító helyreállítási útvonallal.

**Beállításkártya:** Beállítások → Modellzárolás
(`src/app/(dashboard)/dashboard/settings/components/ModelLockoutCard.tsx`).
Ez **különbözik** a fenti, csak olvasható `ModelCooldownsCard` kártyától (amely csak
_felsorolja_ az aktív zárolásokat) — az új kártya _a paramétereket konfigurálja_. Az alapértelmezett értékek a
`DEFAULT_MODEL_LOCKOUT_SETTINGS` konstansban találhatók
(`src/lib/resilience/modelLockoutSettings.ts`):

| Beállítás               | Alapértelmezett                  | Jelentés                                                                  |
| ----------------------- | -------------------------------- | ------------------------------------------------------------------------- |
| `enabled`               | `false`                          | Főkapcsoló — a modellzárolás **alapértelmezés szerint ki van kapcsolva**. |
| `errorCodes`            | `[403, 404, 429, 502, 503, 504]` | Modellhatókörű hibának számító upstream állapotkódok.                     |
| `baseCooldownMs`        | `120_000` (120 mp)               | Az első hiba kezdeti zárolási időtartama.                                 |
| `maxCooldownMs`         | `1_800_000` (30 perc)            | A fokozatosan növelt lehűlési idő felső korlátja.                         |
| `maxBackoffSteps`       | `10`                             | Az exponenciális visszalépés növelési lépéseinek maximális száma.         |
| `useExponentialBackoff` | `true`                           | Ismétlődő hibák esetén exponenciálisan növekedjen-e a lehűlési idő.       |

A beállítások a szokásos beállítástáron keresztül maradnak fenn, és az ellenálló képességi
beállítások sémája alapján lesznek ellenőrizve; a kártya korlátozza a `baseCooldownMs`/`maxCooldownMs`
értékeket (`maxCooldownMs ≥ baseCooldownMs`), valamint a `maxBackoffSteps` értékét.

**Siker-alapú lecsengéses helyreállítás:** a helyreállítás **nem** kizárólag az időzítő lejáratán alapul. Egy megfelelő
válasz fokozatosan csökkenti a modell hibaszámát, így az időablak közben helyreállt modell
növekvő büntetése megszűnik (és a zárolása törlődik), még mielőtt az időzítője lejárna. Sikeres
kombinált cél esetén az `open-sse/services/combo.ts` meghívja a `decayModelFailureCount()`
függvényt (`open-sse/services/accountFallback.ts`), amely **megfelezi** a tárolt
`failureCount` értékét (`Math.floor(failureCount / 2)`); amikor az eléri a `0` értéket, a zárolási
bejegyzés teljes egészében törlődik. A párja, a `recordModelLockoutFailure()`,
a növelési időablakon belüli hibák esetén növeli a számlálót (és meghosszabbítja a lehűlési időt).
Ez a siker-alapú lecsengés az egyszerű időzítőlejáraton felül működik —
bármelyik útvonal újra engedélyezheti a modellt.

**Állapot:** a zárolások **memóriában** vannak tárolva (folyamatonkénti `Map` példányokban,
`ModelLockoutEntry` bejegyzésekkel, amelyek kulcsa `provider:connectionId:model`, míg a pontos hatókörű zárolásoké
`provider:connectionId:exact:model`), és nem kerülnek mentésre
az adatbázisba — újraindításkor elvesznek. A _beállítások_ megmaradnak; az aktív
zárolási _állapot_ átmeneti.

---

## 4. Kvótamegosztási párhuzamosság-szabályozás (v3.8.36)

Az előfizetéses fiókok (GLM, MiniMax stb.) gyakran csak ~1–3 párhuzamos
kérést fogadnak el; ennek túllépése 429-es válaszokat és várakozási időszakokat vált ki. Ez különösen súlyos a
**kvótamegosztási** (`qtSd/…`) kombinációknál, ahol több API-kulcs osztozik egyetlen felsőbb szintű
fiókon. Három réteg akadályozza meg a megosztott fiók túlterhelését.

### Kapcsolatonkénti párhuzamossági korlát (`max_concurrent`)

Minden szolgáltatói kapcsolat megadhat egy `max_concurrent` felső korlátot
(`provider_connections.max_concurrent`, amely a kapcsolat párbeszédablakában / API-n / adatbázisban állítható be).
Korlátlan működéshez hagyja üresen. Ez az egyetlen beállítás vezérli az alábbi szerializálási
réteget — állítsa a fiók tényleges párhuzamossági értékére (pl. GLM ~1, MiniMax ~2).

### Kvótamegosztási kérések szerializálása

Amikor egy kvótamegosztási továbbítás olyan kapcsolatot céloz meg, amely pozitív
`max_concurrent` értéket ad meg, az adott **fiókhoz** tartozó párhuzamos kérések egy
kapcsolatonkénti szemaforon keresztül szerializálódnak (`qsconn:<connectionId>` kulcs): a többletkérések **a
sorban várakoznak**, ahelyett, hogy túlterhelnék a fiókot. A működés **fail-open** jellegű — telített
sor vagy időtúllépés esetén a kérés foglalás nélkül folytatódik, ahelyett, hogy egy továbbítható
kérést valaha is elutasítana. A funkció a **Beállítások → Hibatűrés → Kvótamegosztás kapcsolatonkénti
párhuzamossága** alatt kapcsolható (`resilienceSettings.quotaShareConcurrencyLimit.enabled`, alapértelmezetten
bekapcsolva). `max_concurrent` korlát nélkül a működés változatlan marad.

> Maga a kvótamegosztási útválasztási kapu (`selectQuotaShareTarget`, DRR + P2C) is
> fail-open módon működik, és csak _alacsonyabb prioritásúvá teszi_ a korlátját elérő kapcsolatot — egyetlen
> kapcsolatból álló készlet esetén nem képes szigorú korlátozást alkalmazni, így valójában ez a szemafor
> tartja kordában a túlterhelést.

### A kombinációk várakozási időszakát figyelembe vevő újrapróbálkozás

Minden kombinációs stratégia esetén (ha engedélyezve van) az a kérés, amely egy RÖVID,
átmeneti várakozási időszak miatt 429-es választ eredményezne, kivárja ezt az időszakot, majd
újra továbbításra kerül a 429-es válasz visszaadása helyett — ez lefedi a Gemini-osztályú TPM/RPM-ablakokat
(~60 másodperces retry-after) a többmodelles kombinációknál, például amikor egy kétmodellű kombináció
mindkét célpontja eléri a modellenkénti sebességkorlátot. A működést a `comboCooldownWait`
(`enabled`, `maxWaitMs`, `maxAttempts`, `budgetMs`) korlátozza a **Beállítások → Hibatűrés**
alatt. Soha nem várakozik `quota_exhausted` (éjfélig zárolva), illetve hitelesítési vagy
nem található okok esetén.

---

## 5. A kérési sor beléptetés-szabályozása (v3.8.49 · #6593-as probléma)

**Hatókör**: a helyi, szolgáltatónkénti+kapcsolatonkénti sebességkorlátozási sor (`open-sse/services/rateLimitManager.ts`,
amelyet a Bottleneck támogat), egy réteggel a fenti három mechanizmus alatt.

**A `maxWaitMs` a végrehajtási lejárat korábbi, megőrzött neve.**
A `resilienceSettings.requestQueue.maxWaitMs` a Bottleneck számára egy feladat
`expiration` értékeként kerül átadásra, amelynek időzítője csak a továbbítás után indul el. Ezért ez
a korlátozó által kezelt végrehajtást korlátozza, nem pedig a helyi sorban töltött időt. A lejárat
megbízható helyi `code: "RATE_LIMIT_EXECUTION_TIMEOUT"` hibaként jelenik meg (HTTP 504);
a soridőtúllépés korábbi kódneve csak a megbízható belső
visszamenőleges kompatibilitás érdekében elfogadott. Az alapértelmezett érték 15000ms; felülírható a
`RATE_LIMIT_MAX_WAIT_MS` (környezeti változó) használatával vagy az irányítópulton (**Beállítások → Hibatűrés**,
1–30000ms értékű felhasználóifelület-korlát). A sorban tartózkodásnak nincs időbeli határideje; a sorban álló
kérők számának korlátozásához használja az alábbi `maxQueueDepth` beállítást.

**`maxQueueDepth` — opcionálisan bekapcsolható beléptetési korlát (új).** A `resilienceSettings.requestQueue.maxQueueDepth`
korlátozza, hogy egy szolgáltató+kapcsolat esetén egyszerre hány kérés várakozhat a sorban
(még nem továbbított állapotban). Ha a sor már `maxQueueDepth` számú kérést tartalmaz,
az új kérés azonnal elutasításra kerül egy típusos
`code: "RATE_LIMIT_QUEUE_FULL"` hibával, **mielőtt** valaha is elérné a `limiter.schedule()`
hívást — így az elutasítás kis költségű, és az adott kéréshez kapcsolódó bármely későbbi
prompttömörítési / fordítási munka előtt megtörténik. Az alapértelmezett `0` =
letiltva, ami megőrzi a meglévő, korlátlan sor működését; a megengedett tartomány 0–100000.
Felülírható a `RATE_LIMIT_MAX_QUEUE_DEPTH` (környezeti változó) vagy a
`resilienceSettings.requestQueue.maxQueueDepth` használatával (irányítópult/API-módosítás).

Maga a beléptetési ellenőrzés egy tiszta függvény
(`open-sse/services/rateLimitManager/admission.ts::checkQueueAdmission`), így
valódi Bottleneck-korlátozó nélkül is egységtesztelhető.

> A #6593-at megnyitó RFC egy `bypassCompressionOnRateLimit`
> jelzőt is javasolt. Ennek a tárolónak az `open-sse/services/compression/` adatfolyama
> a kimenő LLM-kérés prompt-/kontextustömörítését végzi (`chatCore.ts`,
> a `resolveCompressionSettings`/`selectCompressionStrategy` blokk körül),
> nem pedig a létrehozott 429-es válaszok HTTP-választömörítését — nincs
> megfelelő kódútvonal egy szó szerinti megkerülési jelzőhöz. Ez a prompttömörítési lépés
> jelenleg szintén a `withRateLimit()` _előtt_ fut a kérési adatfolyamban, ezért
> az átrendezés, amely kihagyná ezt egy megtelt sor miatti elutasítás esetén, különálló és nagyobb
> változtatás, mint ami e probléma hatókörébe tartozik; itt szándékosan **nem** lett megvalósítva,
> és későbbi feladatként marad meg arra az esetre, ha a CPU-megtakarítás megérné az
> átrendezés kockázatát.

---

## 6. Lassú adatfolyam átviteli sebességének felügyelete (#9709)

Az opcionális `resilienceSettings.streamRecovery.throughputWatchdog` védelmi mechanizmus észleli az olyan upstream szolgáltatót, amely továbbra is küld adatrészleteket, de az asszisztensi kimenetet a konfigurált hasznos kimeneti sebességnél lassabban állítja elő. Ez szándékosan különbözik az inaktivitási időkorláttól: a szívverések és a metaadatok egyik időzítőt sem állítják vissza, és nem számítanak előrehaladásnak. Szintén különbözik a próbálkozás rögzített határidejétől (#9153), amely a kimenet minőségétől függetlenül abszolút biztonsági felső korlát marad.

A felügyeleti mechanizmus csak egy bemelegedési időszakot és egy teljes gördülő időablakot követően szakíthatja meg a folyamatot. Számolja a Chat Completions és a Responses API kimeneti eseményeiből származó szövegváltozásokat (az UTF-8-bájtmennyiség konzervatív közelítéseként), figyelmen kívül hagyja a csak használati adatokat tartalmazó és az üres eseményeket, valamint felfüggeszti a kiértékelést, amíg eszközhívási vagy következtetési események vannak folyamatban. Alapértelmezés szerint le van tiltva, és a `STREAM_THROUGHPUT_WATCHDOG_ENABLED=true` beállítással engedélyezhető; az időablakot, a bemelegedést, a minimális sebességet és a minimális mérhető kimenetet a szokásos rugalmassági beállítások normalizálási rétege korlátozza.

Ha engedélyezve van, a felügyeleti mechanizmus megszakítása csak az aktív upstream-próbálkozásra vonatkozik. Mielőtt bármilyen, az ügyfél számára látható bájt elküldésre kerülne, a meglévő, azonos fiókon belüli korai helyreállítási útvonal újraindíthatja a próbálkozást. A véglegesítés után az adatfolyamot a rendszer soha nem játssza vissza vakon; csak a meglévő, biztonságos, adatfolyam közbeni folytatási szerződés illeszthet hozzá egy utótagot. A lezárás továbbra is csak egyszer történik meg, így a használat elszámolása és a szemafor felszabadítása nem ismétlődik meg.

---

## 7. Upstream állapot újramegadása (hibásan megadott kvótahibák)

**Hatókör:** egy upstream átjáró, amely az ideiglenes kvótakimerülést helytelen HTTP-állapotkóddal jelenti.

**Cél:** egy félrevezető állapot kijavítása a besorolás ELŐTT, hogy a downstream fogyasztók (a tartalékmechanizmus, a kombinált összesítés és az ügyfélnek küldött válasz) a hiba valódi, újrapróbálható jellegét lássák.

Egyes átjárók az IDEIGLENES kvótakimerülést nem újrapróbálható HTTP-állapotkóddal jelzik. Az `agentrouter.org` `403`-at (néha `400`-at) ad vissza kínai nyelvű törzzsel (`用户额度不足` / `额度不足`) a szabványos `429` helyett. Az olyan ügyfelek, mint a Claude Code, a `403`-at állandó hibaként kezelik, és megszakítják a munkamenetet; javítás nélkül pedig a tartalékmechanizmus kvótaesemény helyett `AUTH_ERROR` értékkel sorolná be.

**Megvalósítás:**

- Nyilvántartás + egyeztető: `open-sse/config/upstreamStatusRestatement.ts` — szolgáltatónkénti szabálylista (`{id, fromStatuses, toStatus, textMarkers,
excludeMarkers, defaultRetryAfterMs}`), amelyet az `applyStatusRestatement()` használ az egyeztetéshez.
- Hívási hely: a `providerFailure:` blokk az `open-sse/handlers/chatCore.ts` fájlban (körülbelül a 3654. sornál), közvetlenül azután, hogy a `parseUpstreamError()` feldolgozza a hibás HTTP-állapotú upstream-választ (`!providerResponse.ok`), és még bármilyen besorolás végrehajtása előtt, így minden downstream fogyasztó a javított állapotot látja. A `200` állapotú SSE-adatfolyamba ágyazott hibák egy különálló, későbbi adatfolyam-feldolgozási útvonalat követnek, ezért ez a kapcsolódási pont jelenleg **nem** kezeli őket — ez ismert korlátozás, amelyre az agentrouter hibás állapotjelzése esetében egyelőre nincs szükség (mivel az hibás HTTP-állapotként jelenik meg).
- Újrapróbálhatóság: a `429` szerepel a `RETRY_AFTER_ELIGIBLE_STATUSES` listában (`open-sse/services/combo/unavailableRetryGate.ts`), így az újramegadott hiba valódi újrapróbálási időablakot kap, ahelyett, hogy használhatatlan `403`-ként jelenne meg.
- A szintetikus `60s` értékű `defaultRetryAfterMs` (`upstreamStatusRestatement.ts`) csak azt határozza meg, amit az újramegadott válasz közöl az **ügyféllel**; önmagában nem ez a kapcsolat belső lehűlési/letiltási időtartama — azt külön szabályozza az újramegadott hibát ténylegesen kezelő mechanizmus (a Connection Cooldown növekvő visszalépési ideje, §2, API-kulcsos szolgáltatók esetén `3s` alapértékkel; vagy a Model Lockout, §3, a modellenkénti kvótát alkalmazó szolgáltatók, például az agentrouter esetében). Az útválasztó belsőleg hamarabb válhat jogosulttá az újrapróbálkozásra, mint az ügyfélnek jelzett 60 másodperces időablak — ez szándékos tartalék, nem hiba.

Az állandó hibák (az agentrouter `无权访问模型` üzenete — nincs hozzáférés ehhez a modellhez) SOHA nem kapnak újramegadott állapotot: az `excludeMarkers` akkor is megakadályozza a szabály alkalmazását, ha a `textMarkers` egyezést talál, így a hiba megtartja eredeti állapotát, és semmi sem próbálkozik vele a végtelenségig. A megfelelő szolgáltatói besorolási szabályt (`agentrouter-model-access-denied` az `open-sse/config/providerErrorRules.ts` fájlban: `reason: "auth_error"`, `scope: "model"`, deklarált `6h` alap-lehűlési idővel) a `checkFallbackError` (`open-sse/services/accountFallback.ts`) az általános, apikey-kategóriájú `FORBIDDEN` korai visszatérés _előtt_ vizsgálja meg, a `honorsRuleLockScope(provider)` feltételéhez kötve (#10334 — jelenleg kizárólag az agentrouter esetén, a `providerErrorRules.ts` fájlban található `HONORS_RULE_LOCK_SCOPE_PROVIDERS` engedélyezési listán keresztül). A szabály deklarált 6 órás lehűlési ideje `fallbackResult.baseCooldownMs` értékként halad tovább, de továbbra is a már meglévő, modellenkénti kvótához tartozó letiltási útvonalba kerül (`lockModelIfPerModelQuota()` / `recordModelLockoutFailure()`, amelyet a #10334 a lehűlési idő forrásán kívül nem módosított): ezt az operátor `mlSettings.maxCooldownMs` beállítása (alapértelmezés szerint `1_800_000ms` / 30 perc) felső korlátként csökkenti, akárcsak minden más modellletiltás esetén, és a _tárolt letiltási ok_ továbbra is a már meglévő, beégetett `"forbidden"` marad, nem pedig a szabály `"auth_error"` értéke — a teljes folyamatban csak a lehűlés időtartama érvényesül, az okot tartalmazó karakterlánc nem. Maga a kapcsolat aktív marad; az ugyanazon a kapcsolaton elérhető többi modellt ez nem érinti.

Az újrafogalmazott kvótahibák (`额度不足`) éles környezetben illeszkednek egy szolgáltatói szabályra
(`agentrouter-user-quota-exhausted`: `reason: "quota_exhausted"`, `scope:
"connection"`, nincs saját deklarált várakozási ideje — a perzisztenciaréteg
skálázott visszalépési alapértelmezése érvényesül). A #10334 óta a
`ProviderErrorRuleMatch` `scope` értékét a rendszer a teljes folyamaton keresztül
felhasználja, de **csak** a `HONORS_RULE_LOCK_SCOPE_PROVIDERS` engedélyezési
listán szereplő szolgáltatóknál (`providerErrorRules.ts` — jelenleg csak az
`"agentrouter"`, az `honorsRuleLockScope()` által korlátozva). Minden más
szolgáltató esetében a `scope` továbbra is csak tájékoztató jellegű, pontosan
úgy, mint a #10334 előtt. A `checkFallbackError` a megtalált szabály hatókörét
`fallbackResult.ruleScope` értékként teszi elérhetővé; az
`isAgentrouterConnectionQuotaScope()`
(`src/sse/services/auth.ts`) az a közös védőellenőrzés, amely megerősíti, hogy
egy `ruleScope` valóban biztonságosan kezelhető kapcsolatszintű, önmagától
helyreálló jelzésként (`scope` értéke `"connection"`, az ok
`quota_exhausted`, soha nem `permanent`, és soha nem `creditsExhausted` — ez
védelmet nyújt egy olyan jövőbeli szabállyal szemben, amely a
`"connection"` hatókört állandó fiókállapottal párosítaná). Két fogyasztó
hívja meg:

- **Perzisztencia** (`markAccountUnavailable()`, `src/sse/services/auth.ts`):
  ahelyett, hogy a közvetítő szolgáltató **modellenkénti** kizárási ágába
  kerülne (az agentrouter esetében `passthroughModels: true` →
  a `hasPerModelQuota()` értéke `true`), egy **ideiglenes kapcsolati
  várakozási időt** alkalmaz — `testStatus: "unavailable"` +
  `rateLimitedUntil`, végleges állapot (`credits_exhausted`/`banned`/`expired`)
  nélkül —, így a kapcsolat a várakozási idő lejárta után magától helyreáll,
  és nincs szükség a hitelesítő adatok kézi visszaállítására. A
  `disableCooling: true` beállítású kapcsolatoknál kihagyja ezt (#2997): ez a
  letiltás ehelyett a modellenkénti kizáráshoz jut tovább (ez dokumentált
  kompromisszum — lásd az ág feletti megjegyzést a kódban).
- **Azonos kérésen belüli kombinált útválasztás**
  (`applyComboTargetExhaustion()`,
  `open-sse/services/combo/targetExhaustion.ts`): ugyanez a védőellenőrzés
  felveszi a kapcsolatot a memóriabeli `exhaustedConnections` halmazba, a
  `${provider}:${connectionId}` kulccsal. Ez csak olyan hátralévő,
  AZONOS KÉRÉSHEZ TARTOZÓ célpontot hagy ki, amely _saját célobjektumában már
  maga is pontosan ugyanezt a `connectionId` értéket tartalmazza_
  (`getExhaustedTargetSkipReason()`,
  `open-sse/services/combo/comboPredicates.ts`, `if (provider &&
connectionId)` az `exhaustedConnections` lekérdezése előtt) — egy egyszerű
  modelllistás kombináció, amelyben a testvércélpontok nem rendelkeznek saját,
  rögzített `connectionId` értékkel, és az csak elküldésenként kerül
  feloldásra a válasz `X-OmniRoute-Selected-Connection-Id` fejlécéből, soha
  nem illeszkedik erre a kulcsra. Ebben a gyakori esetben a valódi védelmet
  egy hátralévő ág éppen kimerült fiókkal való újbóli próbálkozása ellen NEM
  ez a halmaz biztosítja, hanem a fenti perzisztenciaréteg (a kapcsolat
  `rateLimitedUntil` értéke most már a jövőbe mutat), valamint az, hogy
  ugyanez a védőellenőrzés elnyomja a hibához tartozó
  `transientRateLimitedProviders` értéket (lásd a „Kétlépcsős kialakítás”
  részt és a `targetExhaustion.ts` fájlban az
  `isAgentrouterConnectionQuotaScope` ág kódmegjegyzését): mivel ez a halmaz
  jelöletlen marad, a `combo.ts` `allowRateLimitedConnection` kényszerített
  engedélyezése (`open-sse/services/combo.ts:1005-1013`, `:2734-2738`) NEM
  aktiválódik a szolgáltató hátralévő ágaihoz, így a hitelesítő adatok
  kiválasztása a szokásos módon figyelembe veszi a `rateLimitedUntil` szűrőt
  (`src/sse/services/auth.ts:1238`), és egy hátralévő ág vagy másik, még
  használható agentrouter-kapcsolatot választ, vagy elérhető hitelesítő
  adatok hiányában hibával leáll — nem kényszeríti vissza magát arra a
  kapcsolatra, amelyet ez az ág éppen várakozó állapotba helyezett.

### Kétlépcsős kialakítás: állapot-újrafogalmazás, majd besorolás

Az állapot-újrafogalmazás (`upstreamStatusRestatement.ts`) és a szolgáltatói
besorolási szabályok (`open-sse/config/providerErrorRules.ts`,
`providerRuleRegistry`) különálló regiszterek, amelyek egyaránt a szolgáltató
azonosítója és szöveges jelölők alapján működnek, de eltérő helyeken futnak,
és eltérő célokat szolgálnak: az újrafogalmazás a `chatCore.ts` fájlban
korán átírja a HTTP-állapotot; a besorolási szabályok pedig a
`checkFallbackError()` belsejében választják ki a tartalék útvonal `reason`
értékét és zárolási `scope` értékét (`model` / `provider` / `connection`)
(`open-sse/services/accountFallback.ts`).

A besorolási szabályok csak a `providerErrorRules.ts` fájl
`FULL_TEXT_RULE_PROVIDERS` engedélyezési listáján szereplő szolgáltatóknál
látják a teljes hibaszöveget (amely szükséges az olyan törzsjelölők
illesztéséhez, mint az `额度不足`) — jelenleg csak az `"agentrouter"` esetében.
Minden más **beépített katalógusbeli** szolgáltatónál a `checkFallbackError`
csak a strukturált hibát (`{code, type}`) adja át a
`getProviderErrorRuleMatch` számára, ami elegendő a fejléc-, állapot- vagy
kódalapú szabályokhoz, de nem látja a választörzs szöveges jelölőit. Ezt a
kiválasztást a `resolveRuleMatchBody()` segédfüggvény végzi: az engedélyezett
szolgáltatóknál a teljes hibaszöveget, egyébként a strukturált hibát
használja. Egy **beépített** szolgáltató hozzáadása a
`FULL_TEXT_RULE_PROVIDERS` listához kifejezett, szolgáltatónkénti
engedélyezést jelent — ennek célja, hogy a listán nem szereplő összes
szolgáltató alapértelmezett feldolgozási útvonala bájtról bájtra változatlan
maradjon.

Egy szabály `scope` értékének (`model` / `provider` / `connection`)
engedélyezése elkülönül a `FULL_TEXT_RULE_PROVIDERS` engedélyezésétől: a
`checkFallbackError` csak `fallbackResult.ruleScope` értékként teszi
elérhetővé, és az alsóbb szintű fogyasztók csak az ugyanebben a fájlban lévő
`HONORS_RULE_LOCK_SCOPE_PROVIDERS` engedélyezési listán szereplő
szolgáltatóknál kezelik többként egyszerű tájékoztató címkénél (az
`honorsRuleLockScope()` által korlátozva — jelenleg csak az `"agentrouter"`).
Azt, hogy egy `scope: "connection"` egyezés ténylegesen mit tesz, miután egy
szolgáltató felkerült erre az engedélyezési listára, lásd fent, az
„Újrafogalmazott kvótahibák” részben.

**#11104 — az operátor által deklarált szabályok mindkét engedélyezési listát megkerülik.** Egy operátor futásidőben
deklarálhat szolgáltatónkénti szabályt a `settings.providerErrorRules`
(`open-sse/config/providerErrorRules.ts::setOperatorProviderErrorRules`)
segítségével, ennek a fájlnak a szerkesztése nélkül. Ha egy operátori szabályt a
`FULL_TEXT_RULE_PROVIDERS`/`HONORS_RULE_LOCK_SCOPE_PROVIDERS` mögé zárnánk — ezek az engedélyezési listák
a beépített katalógusszabályok **alapértelmezett** viselkedését hivatottak védeni —,
akkor a beállítási mechanizmus minden szolgáltatónál hatástalanná válna, kivéve azokat,
amelyek már szerepelnek ezekben a listákban, hiszen a szabály deklarálása már önmagában
az operátor kifejezett engedélyezése. A `resolveRuleMatchBody()` és a
`honorsRuleLockScope()` is először a `hasOperatorRuleForProvider()` függvényt ellenőrzi:
az operátori szabállyal rendelkező szolgáltató megkapja a nyers hibaszöveget, és a deklarált
`scope` értéke érvényesül, függetlenül attól, hogy szerepel-e bármelyik engedélyezési listában.

**Ismert hiányosság — HTTP 400 esetén a `providerRuleRegistry` soha nem kerül lekérdezésre.**
A `checkFallbackError` `BAD_REQUEST` ága a 400-as állapotot teljes egészében
a saját minta-tömbjein (`MODEL_ACCESS_DENIED_PATTERNS`,
`CONTEXT_OVERFLOW_PATTERNS` stb. az `accountFallback.ts` fájlban) keresztül
osztályozza, és még azelőtt visszatér, hogy elérné a felette lévő
`configuredRule`/`getProviderErrorRuleMatch` ágat.
A `status: 400` értékkel rendelkező beépített katalógusszabály (vagy operátori szabály)
szintaktikailag érvényes, de soha nem fog aktiválódni. Jelenleg egyetlen meglévő szabály
sem célozza a 400-as állapotot, így ez semmit sem érint éles környezetben — egy jövőbeli
400-as szabályhoz azonban előbb ezt az ágat kell módosítani, ami nagyobb változtatás,
mint egy szabály hozzáadása (újraosztályozza a 400-as állapotot minden olyan szolgáltatónál,
amely már a minta-tömbök viselkedésére támaszkodik), ezért kívül esik egyetlen szolgáltatóhoz
tartozó szabály hozzáadásának hatókörén.

### Hibás kvótaállapotot közlő új átjáró hozzáadása

1. Regisztráljon egy szabálytömböt a `statusRestatementRegistry` fájlban
   (`open-sse/config/upstreamStatusRestatement.ts`). A `textMarkers` értékei
   legyenek szolgáltatóspecifikusak; soha ne használjon újra olyan általános angol kifejezéseket,
   amelyek ütköznek a `CREDITS_EXHAUSTED_SIGNALS` elemeivel
   (`open-sse/services/accountFallback.ts`).
2. Opcionálisan regisztráljon osztályozási szabályokat az
   `open-sse/config/providerErrorRules.ts` fájlban (`providerRuleRegistry`) a
   megfelelő zárolási hatókör kiválasztásához (`connection` a teljes fiókra érvényes
   kvóta, `model` a modellenkénti hibák esetén). Ez a lépés éles környezetben csak
   azoknál a szolgáltatóknál lép hatályba, amelyek szabályainak szükségük van a teljes
   hibaszövegre (törzsjelölőkre): adja hozzá a szolgáltató azonosítóját az ugyanebben
   a fájlban található `FULL_TEXT_RULE_PROVIDERS` listához — ellenkező esetben a
   `checkFallbackError` csak a strukturált `{code, type}` hibát adja át a szabálynak,
   így egy törzsszövegre illeszkedő szabály soha nem fog megfelelni az élő forgalomban.
   A kizárólag `status`/`headers` alapján illeszkedő szabályokhoz (például az Opencode
   vagy a Minimax szabályaihoz) nincs szükség erre a külön engedélyezésre. Ettől függetlenül,
   ha a szabály `scope: "connection"` értéket deklarál, és a cél tényleges, a teljes
   kapcsolatra kiterjedő várakoztatás, valamint ugyanazon kérés kombinációjának kihagyása
   (nem csupán tájékoztató címke), adja hozzá a szolgáltató azonosítóját az ugyanebben
   a fájlban található `HONORS_RULE_LOCK_SCOPE_PROVIDERS` listához — ez engedélyezi az
   `isAgentrouterConnectionQuotaScope()` jellegű feldolgozást a
   `markAccountUnavailable()` (`src/sse/services/auth.ts`) és az
   `applyComboTargetExhaustion()`
   (`open-sse/services/combo/targetExhaustion.ts`) függvényben; enélkül a `scope`
   továbbra is bekerül a `fallbackResult.ruleScope` értékébe, de semmi sem reagál rá.
3. Adjon hozzá a `tests/unit/upstream-status-restatement.test.ts` és a
   `tests/unit/agentrouter-error-rules.test.ts` mintáját követő egységteszteket
   (beleértve a nem végleges / nem `creditsExhausted` védőellenőrzéseket, valamint —
   ha a szolgáltatónak szüksége van az engedélyezési listára — egy tesztet, amely igazolja,
   hogy a `resolveRuleMatchBody()` csak ennél a szolgáltatónál adja vissza a teljes szöveget).

A `chatCore.ts`, a `classifyError` és a kombinációs logika módosítása nem szükséges.

#### Kimenő forgalom szerint csoportosított zárolás (#10880)

Az `EGRESS_BUCKETED_LOCK_PROVIDERS` listában szereplő szolgáltatókat (az opencode családot)
IP-csoportosított upstreamként kezeljük (az opencode ingyenes csomagja IP, nem pedig
fiók szerint van csoportosítva — lásd #9611): egy `quota_exhausted`
**vagy** `rate_limit_exceeded` besorolású 429-es állapot várakoztatja az engedélyezési
listán szereplő szolgáltatócsalád minden olyan kapcsolatát, amelynek utoljára ismert
kimenő IP-címe megegyezik a hibázó kapcsolatéval, még mielőtt a rotáció megpróbálhatná őket
— ezzel elkerülve N-1 garantáltan sikertelen upstream hívást (ugyanaz a minta, mint
#10460/#10525 esetén). A `rate_limit_exceeded` szándékosan szerepel benne: a
`markAccountUnavailable` útvonalon az opencode-specifikus szabályok soha nem illeszkednek
(a `checkFallbackError` nem kap fejlécet/törzset, az opencode pedig nem szerepel a
`FULL_TEXT_RULE_PROVIDERS` listában), ezért egy olyan 429-es válasz, amelynek törzse
tartalmazza az előfizetési kvótára vonatkozó szöveget ("monthly usage limit
reached"), a kvótaszöveges tartaléklogika
(`buildSubscriptionQuotaFallback`, `accountFallback.ts`; 1 órás várakoztatás) révén
`quota_exhausted` besorolást kap, még mielőtt a `status_429` szabály egyáltalán
elérhető lenne — míg a kvótára utaló szöveg nélküli 429-es válasz (egyszerű
sebességkorlátozás) a `status_429` szabály révén `rate_limit_exceeded` besorolást kap,
és továbbra is várakoztatja az IP-családot. Az engedélyezési listán szereplő
szolgáltatóknál az IP szerint csoportosított sebességkorlát ugyanazt jelzi, mint a
kimerült kvóta. Valós korlátok:

- **Legjobb tudás szerinti**: a zárolás a kapcsolat legutóbb ismert `egress_ip`
  értékét határozza meg a `proxy_logs` alapján (24 órás időablak, szinkron,
  gyorsítótár nélkül). Üres gyorsítótár (a kimenő IP még sosem volt ellenőrizve)
  vagy hiányzó sor esetén → a hibát okozó kapcsolatot az ág továbbra is
  várakoztatja (a jelenlegi módon rögzítve), csak a testvérkapcsolat nem lesz
  zárolva.
- **Soha nem végleges**: a várakoztatás egy megújuló kvótaablak
  (`testStatus: "unavailable"`); IP-szintű jelből soha nem következik végleges
  állapot. A `disableCooling` beállítású kapcsolatok teljesen kihagyják ezt az
  ágat.
- **A zárolás granularitása megváltozik az engedélyezési listán szereplő
  családnál**: ez hatókörváltozás, nem csupán a testvérkapcsolatokra vonatkozó
  optimalizálás. Az opencode egy `passthroughModels` szolgáltató, ezért ezen ág
  előtt egy 429-es válasz modellenkénti zárolást eredményezett; mostantól
  kapcsolat-várakoztatást eredményez — akkor is, ha egy operátor egyetlen,
  testvér nélküli kapcsolatot futtat. Az opencode szabálytáblája már eddig is
  ezt a granularitást nyilvánította helyesnek (`scope: "connection"`,
  `providerErrorRules.ts`), de ezt mindeddig nem vettük figyelembe, mert az
  opencode nem szerepel a `HONORS_RULE_LOCK_SCOPE_PROVIDERS` listában. Az ág
  maga írja be a hibát okozó kapcsolat várakoztatását és `backoffLevel`
  értékét, a kapcsolat-hatókörű agentrouter ágat követve, majd visszatér — az
  alatta lévő modellenkénti blokkolás és az általános útvonal soha nem fut le.
- **A combo is ide tartozik**: az agentrouter ághoz hasonlóan a hatókör
  szándékosan figyelmen kívül hagyja a `persistUnavailableState`/`isCombo`
  visszaminősítést, amelyet egy combo hívó alkalmaz a 429-es válaszra. A
  modellenkénti zárolás nem ennek a hatókörnek egy gyengébb formája, hanem
  rossz egységet használ: semmit sem mond a kimerült IP-ről, így a combo
  rotáció testvérkapcsolatonként továbbra is elhasználna egy garantáltan
  sikertelen hívást.
- **Testvérkapcsolatok biztonsága**: a már végleges állapotú
  (banned/credits_exhausted), illetve már hosszabb várakoztatás alatt álló
  testvérkapcsolatok állapota soha nem lesz felülírva.
- **Kizárólagos engedélyezési lista**: az `EGRESS_BUCKETED_LOCK_PROVIDERS`
  bővítése kifejezett tulajdonosi döntés; nincs általános bekötés
  (#10334/#10419 minta). A testvérkapcsolatokat lekérdező lekérdezés ugyanezt
  az engedélyezési listát köti be ahelyett, hogy SQL-literálként megismételné,
  így a bővítése továbbra is egysoros módosítás marad.
- **Kimenő IP rotációja mindkét irányban**: a keresési időablak (24 óra) jóval
  szélesebb a kimenő IP gyorsítótárának TTL-értékénél (5 perc), így a „legutóbb
  ismert IP” előzmény, nem pedig aktuális állapot. Ha egy kapcsolat proxyja az
  időablakon belül rotálódott, a zárolás **kihagyhat** egy valóban megosztott
  IP-t (a rögzített IP az új, még nem kimerült IP) — és ezzel szimmetrikusan
  **várakoztathat egy olyan testvérkapcsolatot, amely azóta elrotálódott** a
  kimerült IP-ről. A második eset a testvérkapcsolatnak egyetlen várakoztatási
  ablakba kerül; mindkettő elfogadott, legjobb tudás szerinti korlátja az
  előzményalapú keresésnek.
- **Költség**: a `proxy_logs` két korlátozott bejárása (az időablak szerinti
  szűrést az `idx_pl_timestamp` végzi), kizárólag 429-es válaszok
  gyakoriságával. Nincs új index (134-es migráció, YAGNI). Közepes méretű,
  valós forgalmi adatbázis másolatán mérve; egy nagy áteresztőképességű példány
  arányosan több sort tartalmaz ugyanabban az időablakban.

---

## Egyéb ellenálló képességi funkciók

- **19 útválasztási stratégia** (prioritásos, súlyozott, körforgásos, kontextustovábbító, először feltöltő, p2c, véletlenszerű, legkevésbé használt, költségoptimalizált, visszaállítás-tudatos, visszaállítási ablakos, tartalékkapacitás-alapú, szigorúan véletlenszerű, automatikus, lkgp, kontextusoptimalizált, gyorsítótár-optimalizált, fúziós, folyamatlánc) — lásd: [AUTO-COMBO.md](../routing/AUTO-COMBO.md).
- **Visszaállítás-tudatos útválasztás** (v3.8.0) — a kvóta visszaállítási ideje alapján rangsorolja a kapcsolatokat.
- **Háttérmód visszaminősítése** — a Responses API `background: true` beállítása figyelmeztetés mellett szinkron módra vált.
- **Dinamikus eszközkorlát-észlelés** — visszalépteti a szolgáltatókat az eszközszám-korlát elérésekor.
- **Vészhelyzeti tartalékmegoldás** — az `OMNIROUTE_EMERGENCY_FALLBACK` szabályozza; az üzemeltetők újraindítás nélkül felülbírálhatják a Funkciójelzők oldalon.

---

## Hibakeresés

- A súlyozott kombináció `503 all_targets_cooling_down` választ ad (a `Retry-After` be van állítva, a `diagnostics.excluded` pedig minden célpontot felsorol `model_lockout` / `circuit_open` / `provider_cooldown` / `unavailable` állapottal) → a készlet konfigurálva és csatlakoztatva van, csupán minden célpontot kizár egy rezilienciát biztosító időzítő; a `[COMBO] Weighted selection: every target excluded before dispatch — …` figyelmeztetés megnevezi az okokat és a hátralévő másodperceket. Az ugyanettől a kombinációtól érkező `404 no_executable_targets` azt jelenti, hogy nem volt érintett rezilienciát biztosító időzítő (nincs mit futtatni, vagy minden fiók sikertelen volt az elérhetőségi ellenőrzésen). Az `open-sse/services/combo/pinRecovery.ts` fájlban valósul meg, a `targetResolution.ts` fájlban összegyűjtött kizárások alapján.
- Egy szolgáltató összes kulcsa ki lett hagyva → ellenőrizze a megszakító állapotát ÉS minden kapcsolat `rateLimitedUntil`/`testStatus` értékét.
- A szolgáltató a visszaállítási időablak után is véglegesen ki van zárva → a kód a nyers `state` értéket olvassa a `getStatus()`/`canExecute()` helyett.
- Egy kulcs meghibásodik, a többinek működnie kellene → részesítse előnyben a kapcsolat lehűlési idejét a megszakítóval szemben.
- Csak egy modell hibásodik meg → részesítse előnyben a modell zárolását a kapcsolat lehűlési idejével szemben.
- Az állapotnak magától helyre kellene állnia, de nem teszi → ellenőrizze, van-e jövőbeli időbélyeg, valamint olyan olvasási útvonal, amely frissíti a lejárt állapotot. Az állandó állapotok kézi módosítást igényelnek.

---

## TLS-ujjlenyomat-készítés és rejtőzködés

A szolgáltatóspecifikus rejtőzködés (JA3/JA4, CCH, elhomályosítás) külön dokumentációban található — lásd: `docs/security/STEALTH_GUIDE.md` (git; nincs beépítve a `/docs` könyvtárba).

---

## Ellenálló képességi tesztelés (8. fázis · C blokk)

Az ellenálló képességi logika egységtesztjein túl három teszt vizsgálja a futtatási környezetet
valós terhelési/hibahelyzetekben (mind integrációs/éjszakai — egyik sem blokkolja a PR-eket):

| Teszt             | Mit vizsgál                                                                                                                                                                                                                                            | Futtatás                                  |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------- |
| Káosz             | A szimulált felsőbb rétegbeli csomópont valós késleltetést/visszaállítást/időtúllépést/503-as hibát idéz elő; ellenőrzi, hogy a megszakító kinyit/helyreáll, és a `checkFallbackError` a 503-as hibát helyreállítható tartalékeseményként osztályozza. | `RUN_CHAOS_INT=1 npm run test:chaos`      |
| Heap-növekedés    | Körülbelül 500 adatfolyam `createSSEStream` példányonként a `--expose-gc` alatt; sikertelen, ha a heap mérete a felső korlát fölé nő (OOM-védelem #3069).                                                                                              | `npm run test:heap`                       |
| k6 tartósterhelés | Tartós terhelés az `/api/monitoring/health` végponton; p95-/hibaküszöbértékek.                                                                                                                                                                         | `k6 run tests/load/k6-soak.js` (éjszakai) |

A `.github/workflows/nightly-resilience.yml` vezérli (cron + kézi indítás). Az alapértelmezett
`test:integration` futtatásban a káosz- és heap-teszt kihagyja önmagát (a `RUN_CHAOS_INT`/`--expose-gc` nélkül).

---

## Lásd még

- [Architektúra-útmutató](./ARCHITECTURE.md) — Rendszerarchitektúra és belső működés
- [Felhasználói útmutató](../guides/USER_GUIDE.md) — Szolgáltatók, kombinációk, CLI-integráció
- [Automatikus kombinációs motor](../routing/AUTO-COMBO.md) — 16 tényezős pontozás, módcsomagok
