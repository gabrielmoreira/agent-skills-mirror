# Resilience Guide (ગુજરાતી)

🌐 **Languages:** 🇺🇸 [English](../../../../architecture/RESILIENCE_GUIDE.md) · 🇪🇹 [am](../../../am/docs/architecture/RESILIENCE_GUIDE.md) · 🇸🇦 [ar](../../../ar/docs/architecture/RESILIENCE_GUIDE.md) · 🇦🇿 [az](../../../az/docs/architecture/RESILIENCE_GUIDE.md) · 🇧🇬 [bg](../../../bg/docs/architecture/RESILIENCE_GUIDE.md) · 🇧🇩 [bn](../../../bn/docs/architecture/RESILIENCE_GUIDE.md) · 🇨🇿 [cs](../../../cs/docs/architecture/RESILIENCE_GUIDE.md) · 🇩🇰 [da](../../../da/docs/architecture/RESILIENCE_GUIDE.md) · 🇩🇪 [de](../../../de/docs/architecture/RESILIENCE_GUIDE.md) · 🇬🇷 [el](../../../el/docs/architecture/RESILIENCE_GUIDE.md) · 🇪🇸 [es](../../../es/docs/architecture/RESILIENCE_GUIDE.md) · 🇪🇪 [et](../../../et/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇷 [fa](../../../fa/docs/architecture/RESILIENCE_GUIDE.md) · 🇫🇮 [fi](../../../fi/docs/architecture/RESILIENCE_GUIDE.md) · 🇫🇷 [fr](../../../fr/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇪 [ga](../../../ga/docs/architecture/RESILIENCE_GUIDE.md) · 🇳🇬 [ha](../../../ha/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇱 [he](../../../he/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [hi](../../../hi/docs/architecture/RESILIENCE_GUIDE.md) · 🇭🇷 [hr](../../../hr/docs/architecture/RESILIENCE_GUIDE.md) · 🇭🇺 [hu](../../../hu/docs/architecture/RESILIENCE_GUIDE.md) · 🇦🇲 [hy](../../../hy/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇩 [id](../../../id/docs/architecture/RESILIENCE_GUIDE.md) · 🇳🇬 [ig](../../../ig/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇹 [it](../../../it/docs/architecture/RESILIENCE_GUIDE.md) · 🇯🇵 [ja](../../../ja/docs/architecture/RESILIENCE_GUIDE.md) · 🇬🇪 [ka](../../../ka/docs/architecture/RESILIENCE_GUIDE.md) · 🇰🇭 [km](../../../km/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [kn](../../../kn/docs/architecture/RESILIENCE_GUIDE.md) · 🇰🇷 [ko](../../../ko/docs/architecture/RESILIENCE_GUIDE.md) · 🇱🇹 [lt](../../../lt/docs/architecture/RESILIENCE_GUIDE.md) · 🇱🇻 [lv](../../../lv/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [ml](../../../ml/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [mr](../../../mr/docs/architecture/RESILIENCE_GUIDE.md) · 🇲🇾 [ms](../../../ms/docs/architecture/RESILIENCE_GUIDE.md) · 🇲🇹 [mt](../../../mt/docs/architecture/RESILIENCE_GUIDE.md) · 🇲🇲 [my](../../../my/docs/architecture/RESILIENCE_GUIDE.md) · 🇳🇵 [ne](../../../ne/docs/architecture/RESILIENCE_GUIDE.md) · 🇳🇱 [nl](../../../nl/docs/architecture/RESILIENCE_GUIDE.md) · 🇳🇴 [no](../../../no/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [or](../../../or/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [pa](../../../pa/docs/architecture/RESILIENCE_GUIDE.md) · 🇵🇭 [phi](../../../phi/docs/architecture/RESILIENCE_GUIDE.md) · 🇵🇱 [pl](../../../pl/docs/architecture/RESILIENCE_GUIDE.md) · 🇵🇹 [pt](../../../pt/docs/architecture/RESILIENCE_GUIDE.md) · 🇧🇷 [pt-BR](../../../pt-BR/docs/architecture/RESILIENCE_GUIDE.md) · 🇷🇴 [ro](../../../ro/docs/architecture/RESILIENCE_GUIDE.md) · 🇷🇺 [ru](../../../ru/docs/architecture/RESILIENCE_GUIDE.md) · 🇱🇰 [si](../../../si/docs/architecture/RESILIENCE_GUIDE.md) · 🇸🇰 [sk](../../../sk/docs/architecture/RESILIENCE_GUIDE.md) · 🇸🇮 [sl](../../../sl/docs/architecture/RESILIENCE_GUIDE.md) · 🇷🇸 [sr](../../../sr/docs/architecture/RESILIENCE_GUIDE.md) · 🇸🇪 [sv](../../../sv/docs/architecture/RESILIENCE_GUIDE.md) · 🇰🇪 [sw](../../../sw/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [ta](../../../ta/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [te](../../../te/docs/architecture/RESILIENCE_GUIDE.md) · 🇹🇭 [th](../../../th/docs/architecture/RESILIENCE_GUIDE.md) · 🇹🇷 [tr](../../../tr/docs/architecture/RESILIENCE_GUIDE.md) · 🇺🇦 [uk-UA](../../../uk-UA/docs/architecture/RESILIENCE_GUIDE.md) · 🇵🇰 [ur](../../../ur/docs/architecture/RESILIENCE_GUIDE.md) · 🇺🇿 [uz](../../../uz/docs/architecture/RESILIENCE_GUIDE.md) · 🇻🇳 [vi](../../../vi/docs/architecture/RESILIENCE_GUIDE.md) · 🇳🇬 [yo](../../../yo/docs/architecture/RESILIENCE_GUIDE.md) · 🇨🇳 [zh-CN](../../../zh-CN/docs/architecture/RESILIENCE_GUIDE.md) · 🇹🇼 [zh-TW](../../../zh-TW/docs/architecture/RESILIENCE_GUIDE.md)

---

OmniRoute પાસે ત્રણ અલગ પરંતુ પરસ્પર સંબંધિત સ્થિતિસ્થાપકતા મિકેનિઝમ છે. દરેકનો વ્યાપ અને હેતુ અલગ છે. રૂટિંગ વર્તણૂક ડિબગ કરતી વખતે તેમને અલગ રાખો.

![3-સ્તરીય સ્થિતિસ્થાપકતા મોડેલ](../diagrams/exported/resilience-3layers.svg)

> સ્રોત: [diagrams/resilience-3layers.mmd](../diagrams/resilience-3layers.mmd)

## 1. પ્રદાતા સર્કિટ બ્રેકર

**વ્યાપ:** સમગ્ર પ્રદાતા (દા.ત., `glm`, `openai`, `anthropic`).

**હેતુ:** અપસ્ટ્રીમ/સેવા સ્તરે વારંવાર નિષ્ફળ થતા પ્રદાતાને ટ્રાફિક મોકલવાનું બંધ કરવું.

**અમલીકરણ:**

- મુખ્ય ક્લાસ: `src/shared/utils/circuitBreaker.ts`
- વાયરિંગ: `src/sse/handlers/chatHelpers.ts`, `src/sse/handlers/chat.ts`
- સ્થિતિ API: `GET /api/monitoring/health`
- રીસેટ API: `POST /api/resilience/reset`
- રૅપર્સ: `open-sse/services/accountFallback.ts`
- DB કોષ્ટક: `domain_circuit_breakers`

**સ્થિતિઓ:**

- `CLOSED` — સામાન્ય ટ્રાફિકને મંજૂરી છે
- `DEGRADED` — ટ્રાફિકને હજી પણ મંજૂરી છે, પરંતુ પ્રદાતાની વધેલી નિષ્ફળતાઓ ટ્રૅક કરવામાં આવે છે
- `OPEN` — પ્રદાતા અસ્થાયી રૂપે અવરોધિત છે; કોમ્બો રૂટિંગ તેને છોડી દે છે
- `HALF_OPEN` — રીસેટ સમયસમાપ્તિ પૂર્ણ થઈ છે; તપાસ વિનંતીને મંજૂરી છે

**રૂપરેખાંકિત કરી શકાય તેવા ડિફૉલ્ટ (`open-sse/config/constants.ts`, Dashboard → Settings → Resilienceમાં ઉપલબ્ધ):**

| ક્લાસ   | આ સમયે ડિગ્રેડ થાય | આ સમયે ખૂલે  | રીસેટ સમયસમાપ્તિ |
| ------- | ------------------ | ------------ | ---------------- |
| OAuth   | 5 નિષ્ફળતાઓ        | 8 નિષ્ફળતાઓ  | 60s              |
| API-કી  | 7 નિષ્ફળતાઓ        | 12 નિષ્ફળતાઓ | 30s              |
| સ્થાનિક | વ્યુત્પન્ન         | 2 નિષ્ફળતાઓ  | 15s              |

`degradationThreshold` એ નિયંત્રિત કરે છે કે પ્રદાતા ક્યારે `DEGRADED` સ્થિતિમાં પ્રવેશે છે; `failureThreshold` એ નિયંત્રિત કરે છે કે તે ક્યારે ખુલે છે અને તેને છોડી દેવામાં આવે છે. સ્થાનિક પ્રદાતા પ્રોફાઇલ્સ હજુ સુધી Resilience સેટિંગ્સ પૃષ્ઠ પર ઉપલબ્ધ નથી.

**ટ્રિપ કોડ્સ:** માત્ર પ્રદાતા-સ્તરની સ્થિતિઓ `[408, 500, 502, 503, 504]`. એકાઉન્ટ-સ્તરની ભૂલો માટે ટ્રિપ કરશો નહીં (મોટાભાગની 401/403/429 — તે કૂલડાઉન અથવા લૉકઆઉટ હેઠળ આવે છે).

**આળસુ પુનઃપ્રાપ્તિ:** જ્યારે `OPEN`ની મુદત પૂરી થાય છે, ત્યારે `getStatus()`, `canExecute()`, `getRetryAfterMs()` સ્થિતિને `HALF_OPEN`માં રિફ્રેશ કરે છે. કોઈ બૅકગ્રાઉન્ડ ટાઇમરની જરૂર નથી.

---

### વૈકલ્પિક વૈશ્વિક પ્રદાતા કૂલડાઉન (વિન્ડો ગેટ)

ચોથું, **વૈકલ્પિક** સ્તર (`PROVIDER_COOLDOWN_ENABLED`, ડિફૉલ્ટ રૂપે **બંધ**) નિષ્ફળ થતા પ્રદાતાઓની
ક્રોસ-રિક્વેસ્ટ મેમરી
`open-sse/services/providerCooldownTracker.ts`માં રાખે છે, જેનો કોમ્બો લક્ષ્ય
રિઝોલ્યુશન દ્વારા ઉપયોગ થાય છે જેથી સળંગ કોમ્બો વિનંતીઓ હમણાં જ
નિષ્ફળ થયેલા પ્રદાતાને ફરીથી તપાસવાનું બંધ કરે. પ્રદાતા-સ્તરની એન્ટ્રીઓ `PROVIDER_PROFILES` વિન્ડો ગેટનું પાલન કરે છે:

| પ્રોફાઇલ | આ પછી ટ્રિપ થાય (`providerFailureThreshold`) | આ સમયગાળાની અંદર (`providerFailureWindowMs`) | આટલા સમય માટે કૂલ થાય (`providerCooldownMs`) |
| -------- | -------------------------------------------: | -------------------------------------------: | -------------------------------------------: |
| OAuth    |                                         `10` |                                      `15min` |                                       `5min` |
| API કી   |                                         `15` |                                      `30min` |                                      `10min` |

થ્રેશોલ્ડથી નીચે પ્રદાતાને **કૂલિંગ સ્થિતિમાં** ગણવામાં આવતો નથી; સફળતા
વિન્ડોને સાફ કરે છે. કનેક્શન-સ્તરની એન્ટ્રીઓ (`provider:connectionId`) તેના બદલે
ઘાતાંકીય `minRetryCooldownMs → maxRetryCooldownMs` બૅકઑફ જાળવે છે. ઓવરરાઇડ્સ:
`OMNIROUTE_PROVIDER_BREAKER_{OAUTH,API_KEY}_{FAILURE_THRESHOLD,FAILURE_WINDOW_MS,COOLDOWN_MS}`.
રીગ્રેશન ગાર્ડ: `tests/unit/provider-cooldown-window-gate.test.ts`.

## 2. કનેક્શન કૂલડાઉન

**વ્યાપ:** એક પ્રદાતા કનેક્શન/એકાઉન્ટ/કી.

**હેતુ:** સમાન પ્રદાતાનાં અન્ય કનેક્શનો સેવા આપવાનું ચાલુ રાખે ત્યારે એક ખામીયુક્ત કીને અવગણવી.

**અમલીકરણ:**

- અનુપલબ્ધ તરીકે ચિહ્નિત કરવું: `src/sse/services/auth.ts::markAccountUnavailable()`
- પસંદગી: સમાન ફાઇલમાં `getProviderCredentials*`
- કૂલડાઉનની ગણતરી: `open-sse/services/accountFallback.ts::checkFallbackError()`
- સેટિંગ્સ: `src/lib/resilience/settings.ts`

**પ્રત્યેક કનેક્શન માટેનાં ફીલ્ડ્સ:**

- `rateLimitedUntil` — કૂલડાઉન સમાપ્ત થાય ત્યાં સુધીનો ટાઇમસ્ટૅમ્પ
- `testStatus: "unavailable"`
- `lastError`, `lastErrorType`, `errorCode`
- `backoffLevel` — એક્સ્પોનેન્શિયલ બૅકઑફ કાઉન્ટર

**ડિફૉલ્ટ કૂલડાઉન:**

- OAuth આધાર: 5s
- API-key આધાર: 3s
- API-key 429: અપસ્ટ્રીમ `Retry-After`/રીસેટ હેડર્સ/પાર્સ કરી શકાય તેવા રીસેટ ટેક્સ્ટને પ્રાધાન્ય આપે છે
- બૅકઑફ: `baseCooldownMs * 2 ** failureIndex`

**થન્ડરિંગ-હર્ડ વિરોધી સુરક્ષા:** સમકાલીન નિષ્ફળતાઓને કારણે કૂલડાઉન વધુ પડતું લંબાવાતું અથવા `backoffLevel` બે વાર વધતું અટકાવે છે.

**ટર્મિનલ સ્થિતિઓ (કૂલડાઉન નથી):**

- `banned` — પ્રતિબંધિત-કીવર્ડ / એકાઉન્ટ-પ્રતિબંધ શોધ દ્વારા સેટ થાય છે ([BAN_DETECTION](../security/BAN_DETECTION.md) જુઓ), તેમજ અપસ્ટ્રીમ દ્વારા પ્રતિ-વિનંતી સતત ત્રણ વાર ઇનકાર (`request_rejected`, દા.ત. Anthropic OAuth 403 "વિનંતીને મંજૂરી નથી" — `open-sse/services/requestRejectedStreak.ts`) કરવામાં આવે ત્યારે સેટ થાય છે; એક જ ઇનકાર માત્ર કનેક્શનને કૂલડાઉનમાં મૂકે છે
- `expired` (મર્યાદિત પુનઃપ્રયાસો પછી ટર્મિનલ સ્થિતિમાં પરિવર્તિત થાય છે — એક્સ્પોનેન્શિયલ બૅકઑફ સાથે `EXPIRED_RETRY_MAX = 3` — જેથી ક્ષણિક OAuth ભૂલો એકાઉન્ટ કાયમી રીતે નિષ્ક્રિય થાય તે પહેલાં આપમેળે સુધરી શકે)
- `credits_exhausted`

ક્રેડેન્શિયલ્સ બદલાય અથવા ઑપરેટર તેમને રીસેટ કરે ત્યાં સુધી આ સ્થિતિઓ જળવાઈ રહે છે. ક્ષણિક કૂલડાઉન સ્થિતિ વડે ટર્મિનલ સ્થિતિઓને ઓવરરાઇટ કરશો નહીં.

**લેઝી પુનઃપ્રાપ્તિ:** જ્યારે `rateLimitedUntil` વીતી જાય છે, ત્યારે કનેક્શન ફરીથી પાત્ર બને છે. સફળ ઉપયોગ પર, `clearAccountError()` તમામ ભૂલ ફીલ્ડ્સ સાફ કરે છે.

### સેશન અફિનિટી (#7274)

**વ્યાપ:** એક ક્લાયન્ટ સેશન (`X-Session-Id` / `x-codex-session-id` / `x-omniroute-session` હેડર), **કોઈપણ** પ્રદાતા માટે એક કનેક્શન સાથે પિન કરેલું.

**હેતુ:** મલ્ટિ-ટર્ન એજન્ટને (Claude Code, aider, કસ્ટમ એજન્ટ્સ) વિનંતીઓમાં સમાન એકાઉન્ટ પર જાળવી રાખવું, જેથી એકાઉન્ટ્સ વચ્ચેનો કૉન્ટેક્સ્ટ લૉસ અને પ્રતિ-એકાઉન્ટ સેશન સ્ટેટ ધરાવતા પ્રદાતાઓ પર વારંવાર થતા કોલ્ડ-સ્ટાર્ટ 429 ઘટે.

**અમલીકરણ:**

- TTL રિઝોલ્યુશન: `src/sse/services/sessionAffinityPin.ts::resolveSessionAffinityTtlMs()`
- પિનની પસંદગી/બનાવટ: `src/sse/services/sessionAffinityPin.ts::selectSessionAffinityConnection()`
- હેડર એક્સ્ટ્રેક્શન (સામાન્ય, કોઈપણ પ્રદાતા): `src/sse/services/auth.ts::extractSessionAffinityKey()`
- કાયમી સંગ્રહિત પિન ટેબલ: `sessionAccountAffinity` (`src/lib/db/sessionAccountAffinity.ts`)
- સેટિંગ: `sessionAffinityTtlMs` (msમાં ગ્લોબલ TTL, `0` તેને નિષ્ક્રિય કરે છે) — `src/lib/db/settings.ts`. માઇગ્રેશન `124_generic_session_affinity_ttl.sql` દ્વારા તેનું નામ માત્ર Codex માટેના `codexSessionAffinityTtlMs` પરથી બદલવામાં આવ્યું છે, જે અગાઉ કૉન્ફિગર કરાયેલ કોઈપણ Codex TTLને નવા ડિફૉલ્ટ તરીકે આગળ લઈ જાય છે.

#7274 પહેલાં, `resolveSessionAffinityTtlMs()` `codex` સિવાયના દરેક પ્રદાતા માટે તરત જ `0` પર અટકી જતું હતું, તેથી પિનિંગ મિકૅનિઝમ અને હેડર એક્સ્ટ્રેક્શન પહેલેથી જ પ્રદાતા-અજ્ઞેય હોવા છતાં TTL સેટિંગ (અને સેશન હેડર્સ) અન્ય ક્યાંય અસર કરતા નહોતા. સુધારામાં તે વહેલું રિટર્ન દૂર કરવામાં આવ્યું; હવે TTLને ગ્લોબલી `0`થી વધુ સેટ કર્યા પછી તે દરેક પ્રદાતા પર એકસરખું લાગુ પડે છે.

ત્રણેય સેશન-અફિનિટી હેડર્સ ક્યારેય અપસ્ટ્રીમ ફૉર્વર્ડ કરવામાં આવતા નથી — એક્ઝિક્યુટર્સ ક્લાયન્ટ હેડર્સને પસાર કરવાને બદલે શરૂઆતથી પોતાના અપસ્ટ્રીમ હેડર્સ બનાવે છે, તેથી આ ફક્ત આંતરિક કોરિલેશન ID તરીકે જ રહે છે.

### એક્સક્લૂસિવ મેનેજ્ડ સેશન કનેક્શન લીઝ

**વ્યાપ:** એક સક્રિય મેનેજ્ડ HTTP ક્લાયન્ટ/સેશન એક પાત્ર OmniRoute કનેક્શનની માલિકી ધરાવે છે.

**હેતુ:** વિનંતીઓમાં કડક રાઉટિંગ
ફેન્સની જરૂર હોય તેવા ક્લાયન્ટ્સ માટે ટકાઉ એક્સક્લૂસિવ કનેક્શન માલિકી પ્રદાન કરવી. આ સેશન અફિનિટીથી અલગ છે, જે સૉફ્ટ સાતત્ય પ્રાધાન્ય છે:
એક્સક્લૂસિવ લીઝ SQLiteમાં લાઇફસાઇકલ સ્ટેટ જાળવી રાખે છે, ગ્લોબલ સક્રિય-માલિક અને
સક્રિય-કનેક્શન વિશિષ્ટતા લાગુ કરે છે અને પ્રદાતા ડિસ્પૅચ પહેલાં જૂની જનરેશનને નકારે છે.

આ સુવિધા દરેક API કી દીઠ ઑપ્ટ-ઇન છે. મેનેજ્ડ કી પાસે `lease:exclusive` સ્કોપ અને
સ્પષ્ટપણે બિન-ખાલી `allowedConnections` સૂચિ હોવી જરૂરી છે. કોઈપણ HTTP ક્લાયન્ટ લાઇફસાઇકલ એન્ડપૉઇન્ટનો ઉપયોગ કરી શકે છે; કોઈ
ક્લાયન્ટ નામ, યુઝર-એજન્ટ, પ્રદાતા, OAuth પદ્ધતિ અથવા મૉડલ જરૂરી નથી. લીઝ કનેક્શનની માલિકી ધરાવે છે,
મૉડલની નહીં, તેથી કનેક્શન સામાન્ય રીતે
પાત્ર રહે ત્યાં સુધી મૉડલ બદલાવ બાઇન્ડિંગ જાળવી રાખે છે. સામાન્ય મૉડલ, ક્વોટા, હેલ્થ, કૂલડાઉન અને અલાઉલિસ્ટ નિયમો અધિકૃત રહે છે અને
સમાન જનરેશનને અન્ય મુક્ત પાત્ર કનેક્શન પર પરિવર્તિત કરી શકે છે.

લાઇફસાઇકલ JSON ઍક્શન્સ `acquire`, `renew` અને `release` સાથે `POST /api/v1/session-leases` છે.
મેનેજ્ડ ઇન્ફરન્સ વિનંતીઓ અસ્પષ્ટ `X-OmniRoute-Lease-Owner` મૂલ્ય અને ચોક્કસ
`X-OmniRoute-Lease-Generation` રજૂ કરે છે. માલિક `vlo_` પછી 43 base64url અક્ષરોનો ઉપયોગ કરે છે; ફક્ત
તેનો SHA-256 હૅશ સંગ્રહિત થાય છે. દરેક અંતિમ ડિસ્પૅચ ફેન્સ પ્રમાણિત API કી ID અને
સક્રિય કનેક્શન IDને પણ બાઇન્ડ કરે છે. લીઝ કન્ટ્રોલ હેડર્સ લૉગ્સ, જાળવી રાખેલા રિક્વેસ્ટ સ્નૅપશૉટ્સ અને
અપસ્ટ્રીમ એક્ઝિક્યુટર હેડર્સમાંથી દૂર કરવામાં આવે છે.

જો સામાન્ય રાઉટિંગ પાસે પાત્ર મેનેજ્ડ ઉમેદવારો હોય, પરંતુ દરેક મુક્ત ઉમેદવાર વિદેશી સક્રિય લીઝના કબજામાં હોય, તો
OmniRoute HTTP `429`, lease-capacity-unavailable કોડ,
waiting-for-capacity સ્થિતિ અને સૌથી વહેલી સંબંધિત સમાપ્તિ પરથી મેળવેલું મર્યાદિત `Retry-After` પરત કરે છે.
સામાન્ય ખાલી પાત્રતા લીઝ વિવાદ નથી અને તેના હાલના રાઉટિંગ ભૂલના અર્થશાસ્ત્રને જાળવી રાખે છે.

સંબંધિત મિકૅનિઝમ્સ અલગ રહે છે:

- OAuth સેશન ઑક્યુપન્સી OAuth એકાઉન્ટ્સ માટે પ્રોસેસ-લોકલ સૉફ્ટ વિતરણ છે.
- એકાઉન્ટ સેમાફોર્સ વિનંતી-સમકાલીનતા પરમિટ આપે છે અને વિનંતી પૂર્ણ થાય ત્યારે સમાપ્ત થાય છે.
- એક્સક્લૂસિવ મેનેજ્ડ સેશન લીઝ એ જનરેશન ફેન્સ સાથેની ટકાઉ લાઇફસાઇકલ માલિકી છે.

---

## 3. મોડલ લૉકઆઉટ

**વ્યાપ:** provider + connection + model ત્રિપુટી.

**સ્થિતિ અનુસાર કીનો વ્યાપ:** નિષ્ફળ સ્થિતિ નક્કી કરે છે કે લૉકઆઉટ કઈ કી પર લખવામાં આવે
(`open-sse/services/accountFallback/exactModelLock.ts` માં `resolveLockoutScope()`):

- `429` / `403` / `402` — quota અથવા entitlement સંકેત — **quota family**ને લૉક કરે છે:
  codex માટે સંપૂર્ણ `codex` / `spark` વ્યાપ (connectionના દરેક `gpt-5*` model),
  અન્ય providers માટે `getQuotaScopedModelForProvider()`.
- `404` મૂળ modelને લૉક કરે છે (`getModelLockKey()` `not_found`ને સંકુચિત કરે છે).
- અન્ય કોઈપણ સ્થિતિ — `5xx` transport/server નિષ્ફળતાઓ અને ગુણવત્તા માન્યતામાંથી
  OmniRoute દ્વારા જ બનાવાયેલ `502` — માત્ર **ચોક્કસ**
  provider/connection/model ત્રિપુટીને લૉક કરે છે. એક model પરનો ખરાબ stream
  accountના quota વિશે પુરાવો નથી; આ નિયમ પહેલાં
  `codex/gpt-5.6-luna` પરના એક ખાલી responseને કારણે તે connectionના દરેક
  `gpt-5*` modelને 2–30 મિનિટ માટે routingમાંથી દૂર કરવામાં આવતા હતા
  (ક્રમશઃ વધતા સમય સાથે), જ્યારે તેનો quota અસ્પર્શિત રહેતો હતો.
- callerનો સ્પષ્ટ `scope` વિકલ્પ હંમેશાં પ્રાધાન્ય મેળવે છે (Antigravity `"exact"` પસાર કરે છે).

**હેતુ:** જ્યારે માત્ર એક model અનુપલબ્ધ હોય અથવા quota દ્વારા મર્યાદિત હોય ત્યારે આખા connectionને અક્ષમ કરવાનું ટાળવું.

**ઉદાહરણો:**

- દરેક model માટે quota ધરાવતા providers દ્વારા પરત કરાયેલ 429
- એક ગુમ થયેલા model માટે local providers દ્વારા પરત કરાયેલ 404
- Provider-વિશિષ્ટ mode/model પરવાનગી નિષ્ફળતાઓ (દા.ત., Grok modes)

**અમલીકરણ:** `open-sse/services/accountFallback.ts` — `lockModel()`, `clearModelLock()`, `getAllModelLockouts()`.

### મોડલ કૂલડાઉન ડૅશબોર્ડ (v3.8.0)

UI: Settings → Model Cooldowns (`src/app/(dashboard)/dashboard/settings/components/ModelCooldownsCard.tsx`)

સક્રિય lockoutsને provider, connection, model, reason, expiresAt સાથે સૂચિબદ્ધ કરે છે. Operators cardમાંથી modelને મેન્યુઅલી ફરી સક્ષમ કરી શકે છે.

**REST API:**

- `GET /api/resilience/model-cooldowns` — સક્રિય lockoutsની સૂચિ મેળવો
- `DELETE /api/resilience/model-cooldowns` — મેન્યુઅલી ફરી સક્ષમ કરો. Body: `{provider, connection, model}`. Auth: management.

### લૉકઆઉટ સેટિંગ્સ UI + સફળતા-ક્ષય પુનઃપ્રાપ્તિ (v3.8.23)

Model lockout હંમેશાં ચાલુ રહેતી hardcoded વર્તણૂકમાંથી તેના પોતાના settings card અને
સ્વયં-સુધારક recovery path સાથેની સંપૂર્ણપણે રૂપરેખાંકિત કરી શકાય તેવી,
opt-in સુવિધામાં ફેરવાયું.

**Settings card:** Settings → Model Lockout
(`src/app/(dashboard)/dashboard/settings/components/ModelLockoutCard.tsx`).
આ ઉપરના ફક્ત વાંચી શકાય તેવા `ModelCooldownsCard`થી **અલગ** છે (જે માત્ર
સક્રિય lockoutsને _સૂચિબદ્ધ_ કરે છે) — નવું card _parametersને ગોઠવે છે_. Defaults
`DEFAULT_MODEL_LOCKOUT_SETTINGS`
(`src/lib/resilience/modelLockoutSettings.ts`)માં છે:

| સેટિંગ                  | ડિફૉલ્ટ                          | અર્થ                                                                |
| ----------------------- | -------------------------------- | ------------------------------------------------------------------- |
| `enabled`               | `false`                          | મુખ્ય toggle — model lockout **ડિફૉલ્ટ રૂપે બંધ** છે.               |
| `errorCodes`            | `[403, 404, 429, 502, 503, 504]` | Model-વ્યાપી નિષ્ફળતા તરીકે ગણાતી upstream સ્થિતિઓ.                 |
| `baseCooldownMs`        | `120_000` (120 s)                | પ્રથમ નિષ્ફળતા માટે પ્રારંભિક lockout અવધિ.                         |
| `maxCooldownMs`         | `1_800_000` (30 min)             | વધારવામાં આવેલા cooldownની મહત્તમ મર્યાદા.                          |
| `maxBackoffSteps`       | `10`                             | Exponential-backoff વધારાના મહત્તમ પગલાં.                           |
| `useExponentialBackoff` | `true`                           | પુનરાવર્તિત નિષ્ફળતાઓ cooldownને exponential રીતે વધારે છે કે નહીં. |

Settings સામાન્ય settings store દ્વારા જળવાઈ રહે છે અને resilience settings schema દ્વારા
validate થાય છે; card `baseCooldownMs`/`maxCooldownMs`
(`maxCooldownMs ≥ baseCooldownMs` સાથે) અને `maxBackoffSteps`ને મર્યાદામાં રાખે છે.

**સફળતા-ક્ષય પુનઃપ્રાપ્તિ:** recovery ફક્ત timer સમાપ્ત થવા પર આધારિત **નથી**. સ્વસ્થ
response modelની failure countને પાછી ઘટાડે છે, જેથી windowની વચ્ચે recover થયેલું model
તેનો timer સમાપ્ત થાય તે પહેલાં વધવાનું અટકાવે છે (અને clear થાય છે). સફળ
combo target પર `open-sse/services/combo.ts`, `decayModelFailureCount()`
(`open-sse/services/accountFallback.ts`)ને call કરે છે, જે સંગ્રહિત
`failureCount`ને **અડધો** કરે છે (`Math.floor(failureCount / 2)`); તે `0` પર પહોંચે ત્યારે lockout
entry સંપૂર્ણપણે delete થાય છે. તેનો સમકક્ષ `recordModelLockoutFailure()`,
escalation windowની અંદર નિષ્ફળતા આવે ત્યારે count વધારે છે (અને cooldownને વધારતો જાય છે).
આ success-decay સામાન્ય timer expiry ઉપરાંત છે —
કોઈપણ path modelને ફરી સક્ષમ કરી શકે છે.

**સ્થિતિ:** lockouts **in-memory** રાખવામાં આવે છે (દરેક process માટેનાં
`ModelLockoutEntry`ના `Map`s, જે `provider:connectionId:model` દ્વારા keyed છે; exact-scope locks
`provider:connectionId:exact:model` દ્વારા keyed છે), DBમાં
persist થતા નથી — restart વખતે તે ગુમ થઈ જાય છે. _Settings_ persist થાય છે; સક્રિય
lockout _સ્થિતિ_ અસ્થાયી છે.

---

## 4. ક્વોટા-શેર સમકાલીનતા નિયંત્રણ (v3.8.36)

સબ્સ્ક્રિપ્શન એકાઉન્ટ્સ (GLM, MiniMax વગેરે) ઘણીવાર માત્ર ~1–3 સમકાલીન
વિનંતીઓ સ્વીકારે છે; તેનાથી વધુ વિનંતીઓ 429 અને કૂલડાઉન ટ્રિગર કરે છે. આ સમસ્યા
**ક્વોટા-શેર** (`qtSd/…`) કોમ્બોમાં વધુ ગંભીર હોય છે, જ્યાં અનેક API કી એક જ અપસ્ટ્રીમ
એકાઉન્ટ શેર કરે છે. ત્રણ સ્તરો શેર કરેલા એકાઉન્ટને વિનંતીઓથી ભરાઈ જતું અટકાવે છે.

### પ્રતિ-કનેક્શન સમકાલીનતા મર્યાદા (`max_concurrent`)

દરેક પ્રોવાઇડર કનેક્શન `max_concurrent`ની મહત્તમ મર્યાદા જાહેર કરી શકે છે
(`provider_connections.max_concurrent`, જે કનેક્શન મોડલ / API / DBમાં સેટ થાય છે).
કોઈ મર્યાદા ન રાખવા માટે તેને ખાલી છોડો. નીચેના સીરિયલાઇઝેશન સ્તરને નિયંત્રિત
કરતું આ એકમાત્ર સેટિંગ છે — તેને એકાઉન્ટની વાસ્તવિક સમકાલીનતા મુજબ સેટ કરો
(દા.ત. GLM ~1, MiniMax ~2).

### ક્વોટા-શેર વિનંતી સીરિયલાઇઝેશન

જ્યારે ક્વોટા-શેર ડિસ્પેચ સકારાત્મક `max_concurrent` જાહેર કરતા કનેક્શનને લક્ષ્ય
બનાવે છે, ત્યારે તે **એકાઉન્ટ** માટેની સમકાલીન વિનંતીઓને પ્રતિ-કનેક્શન સેમાફોર
(કી `qsconn:<connectionId>`) મારફતે ક્રમબદ્ધ કરવામાં આવે છે: વધારાની વિનંતીઓ
એકાઉન્ટને ભરવાને બદલે **કતારમાં રાહ જુએ છે**. તે **fail-open** છે — સંતૃપ્ત
કતાર અથવા સમયસમાપ્તિની સ્થિતિમાં ડિસ્પેચ કરી શકાય તેવી વિનંતીને નકારવાને બદલે
સ્લોટ વિના પ્રક્રિયા આગળ વધે છે. તેને **સેટિંગ્સ → સ્થિતિસ્થાપકતા → ક્વોટા-શેર
પ્રતિ-કનેક્શન સમકાલીનતા** (`resilienceSettings.quotaShareConcurrencyLimit.enabled`,
ડિફૉલ્ટ રૂપે ચાલુ)માં ટૉગલ કરો. `max_concurrent` મર્યાદા વિના વર્તન યથાવત્ રહે છે.

> ક્વોટા-શેર રાઉટિંગ ગેટ (`selectQuotaShareTarget`, DRR + P2C) પોતે પણ
> fail-open છે અને મર્યાદા પર પહોંચી ગયેલા કનેક્શનને માત્ર _ઓછી પ્રાથમિકતા આપે છે_
> — એકલ-કનેક્શન પૂલમાં તે કડક મર્યાદા લાગુ કરી શકતું નથી, તેથી વિનંતીઓના પૂરને
> વાસ્તવમાં નિયંત્રિત કરતું સાધન આ સેમાફોર છે.

### કોમ્બો કૂલડાઉન-અવેર પુનઃપ્રયાસ

દરેક કોમ્બો વ્યૂહરચના માટે (સક્ષમ હોય ત્યારે), એવી વિનંતી જે ટૂંકા સમયના અસ્થાયી
કૂલડાઉન માટે 429ને નિશ્ચિત બનાવી દેતી હોય, તે 429 પરત આપવાને બદલે કૂલડાઉન
પૂરો થવાની રાહ જુએ છે અને ફરી ડિસ્પેચ થાય છે — આ મલ્ટિ-મોડલ કોમ્બો પરની
Gemini-શ્રેણીની TPM/RPM વિન્ડો (~60s retry-after)ને આવરી લે છે, દા.ત. 2-મોડલ
કોમ્બોના બંને લક્ષ્યો પ્રતિ-મોડલ દર મર્યાદા પર પહોંચે ત્યારે. આ
**સેટિંગ્સ → સ્થિતિસ્થાપકતા**માંના `comboCooldownWait` (`enabled`, `maxWaitMs`,
`maxAttempts`, `budgetMs`) દ્વારા મર્યાદિત છે. તે `quota_exhausted`
(મધરાત સુધી લૉક) અથવા પ્રમાણીકરણ/ન મળવાનાં કારણો માટે ક્યારેય રાહ જોતું નથી.

---

## 5. વિનંતી કતાર પ્રવેશ નિયંત્રણ (v3.8.49 · issue #6593)

**વ્યાપ**: સ્થાનિક પ્રતિ-પ્રોવાઇડર+કનેક્શન દર-મર્યાદા કતાર (`open-sse/services/rateLimitManager.ts`,
Bottleneck દ્વારા સમર્થિત), જે ઉપરના ત્રણ મિકેનિઝમથી એક સ્તર નીચે છે.

**`maxWaitMs` એ એક્ઝિક્યુશન સમાપ્તિ માટેનું લેગસી સ્થાયી નામ છે.**
`resilienceSettings.requestQueue.maxWaitMs`ને Bottleneckમાં જોબ
`expiration` તરીકે પસાર કરવામાં આવે છે, જેનો ટાઇમર ડિસ્પેચ થયા પછી જ શરૂ થાય છે.
તેથી તે સ્થાનિક કતારમાં વિતાવેલા સમયને નહીં, પરંતુ લિમિટર દ્વારા સંચાલિત
એક્ઝિક્યુશનને મર્યાદિત કરે છે. સમાપ્તિને વિશ્વસનીય સ્થાનિક
`code: "RATE_LIMIT_EXECUTION_TIMEOUT"` (HTTP 504) તરીકે દર્શાવવામાં આવે છે;
પાછળની સુસંગતતા માટે અગાઉનું કતાર-સમયસમાપ્તિ કોડ નામ માત્ર વિશ્વસનીય આંતરિક
ઉપયોગ માટે સ્વીકારવામાં આવે છે. ડિફૉલ્ટ 15000ms છે; તેને
`RATE_LIMIT_MAX_WAIT_MS` (env) અથવા ડૅશબોર્ડ (**સેટિંગ્સ → સ્થિતિસ્થાપકતા**,
1–30000ms UI મહત્તમ મર્યાદા) મારફતે ઓવરરાઇડ કરો. કતારમાં રહેવા માટે કોઈ
સમયમર્યાદા નથી; કતારમાં રહેલા કૉલર્સને મર્યાદિત કરવા નીચેનું
`maxQueueDepth` વાપરો.

**`maxQueueDepth` — ઑપ્ટ-ઇન પ્રવેશ મર્યાદા (નવી).** `resilienceSettings.requestQueue.maxQueueDepth`
એક સમયે એક પ્રોવાઇડર+કનેક્શન માટે કેટલી વિનંતીઓ કતારમાં (હજુ ડિસ્પેચ ન થયેલી)
રહી શકે તે મર્યાદિત કરે છે. જ્યારે કતારમાં પહેલેથી જ `maxQueueDepth` વિનંતીઓ
હોય, ત્યારે નવી વિનંતીને ટાઇપ કરેલી `code: "RATE_LIMIT_QUEUE_FULL"` ભૂલ સાથે
`limiter.schedule()` સુધી પહોંચે તે **પહેલાં જ** તરત નકારી દેવામાં આવે છે —
એટલે નકારવાની પ્રક્રિયા સસ્તી છે અને તે વિનંતી માટેના કોઈપણ ડાઉનસ્ટ્રીમ
પ્રોમ્પ્ટ-કમ્પ્રેશન / અનુવાદ કાર્ય પહેલાં થાય છે. ડિફૉલ્ટ `0` = અક્ષમ,
જે હાલના અમર્યાદિત-કતાર વર્તનને જાળવે છે; મર્યાદિત શ્રેણી 0–100000 છે.
તેને `RATE_LIMIT_MAX_QUEUE_DEPTH` (env) અથવા
`resilienceSettings.requestQueue.maxQueueDepth` (ડૅશબોર્ડ/API પેચ) મારફતે
ઓવરરાઇડ કરો.

પ્રવેશ તપાસ પોતે એક શુદ્ધ ફંક્શન છે
(`open-sse/services/rateLimitManager/admission.ts::checkQueueAdmission`), તેથી
વાસ્તવિક Bottleneck લિમિટર વિના તેનું યુનિટ-ટેસ્ટિંગ કરી શકાય છે.

> #6593 શરૂ કરનાર RFCએ `bypassCompressionOnRateLimit`
> ફ્લૅગનો પણ પ્રસ્તાવ કર્યો હતો. આ રેપોની `open-sse/services/compression/`
> પાઇપલાઇન આઉટબાઉન્ડ LLM વિનંતી (`chatCore.ts`,
> `resolveCompressionSettings`/`selectCompressionStrategy` બ્લૉકની આસપાસ)
> પરનું પ્રોમ્પ્ટ/કૉન્ટેક્સ્ટ કમ્પ્રેશન છે, કૃત્રિમ રીતે બનાવેલા 429 બોડી પરનું
> HTTP પ્રતિસાદ કમ્પ્રેશન નહીં — તેથી સીધા બાયપાસ ફ્લૅગને અનુરૂપ કોઈ કોડ પાથ
> નથી. પ્રોમ્પ્ટ-કમ્પ્રેશનનું એ પગલું પણ હાલમાં વિનંતી પાઇપલાઇનમાં
> `withRateLimit()` _પહેલાં_ ચાલે છે, તેથી કતાર-પૂર્ણ હોવાને કારણે વિનંતી નકારાય
> ત્યારે તેને છોડવા માટે ક્રમ બદલવો એ આ issueના વ્યાપ કરતાં અલગ અને વધુ મોટો
> ફેરફાર છે; અહીં ઇરાદાપૂર્વક તેનો અમલ **કરવામાં આવ્યો નથી** અને જો CPU બચતનો
> લાભ ક્રમ બદલવાના જોખમને યોગ્ય ઠેરવે તો તેને અનુવર્તી કાર્ય તરીકે બાકી રાખવામાં
> આવ્યો છે.

---

## 6. ધીમા-સ્ટ્રીમ થ્રૂપુટ વૉચડૉગ (#9709)

વૈકલ્પિક `resilienceSettings.streamRecovery.throughputWatchdog` ગાર્ડ એવા
અપસ્ટ્રીમને શોધે છે જે હજી પણ ચંક્સ મોકલી રહ્યું હોય, પરંતુ ગોઠવેલા ઉપયોગી-આઉટપુટ
દર કરતાં ઓછું આસિસ્ટન્ટ આઉટપુટ ઉત્પન્ન કરતું હોય. તેને ઇરાદાપૂર્વક આઇડલ ટાઇમઆઉટથી
અલગ રાખવામાં આવ્યું છે: હાર્ટબીટ્સ અને મેટાડેટા કોઈ પણ ટાઇમરને રીસેટ કરતા નથી અને
પ્રગતિ તરીકે ગણાતા નથી. તે હાર્ડ અટેમ્પ ડેડલાઇન (#9153)થી પણ અલગ છે, જે આઉટપુટની
ગુણવત્તાને ધ્યાનમાં લીધા વિના સંપૂર્ણ સલામતી મર્યાદા તરીકે યથાવત્ રહે છે.

વૉચડૉગ અટકાવી શકે તે પહેલાં તેને વૉર્મ-અપ અવધિ અને ત્યારબાદ સંપૂર્ણ રોલિંગ વિન્ડોની
જરૂર પડે છે. તે Chat Completions અને Responses APIના આઉટપુટ ઇવેન્ટ્સમાંથી ટેક્સ્ટ
ડેલ્ટાની ગણતરી કરે છે (UTF-8 બાઇટ્સનો સાવચેત પ્રૉક્સી), માત્ર ઉપયોગ-સંબંધિત અને ખાલી
ઇવેન્ટ્સને અવગણે છે, અને ટૂલ-કૉલ અથવા રીઝનિંગ ઇવેન્ટ્સ ચાલુ હોય ત્યારે મૂલ્યાંકન
સ્થગિત કરે છે. તે ડિફૉલ્ટ રૂપે અક્ષમ હોય છે અને
`STREAM_THROUGHPUT_WATCHDOG_ENABLED=true` વડે સક્ષમ કરી શકાય છે; વિન્ડો, વૉર્મ-અપ,
ન્યૂનતમ દર અને ન્યૂનતમ માપી શકાય તેવું આઉટપુટ સામાન્ય રેઝિલિયન્સ-સેટિંગ્સ
નોર્મલાઇઝેશન સ્તર દ્વારા મર્યાદિત કરવામાં આવે છે.

સક્ષમ હોય ત્યારે, વૉચડૉગ દ્વારા કરાયેલ અટકાવ માત્ર સક્રિય અપસ્ટ્રીમ અટેમ્પ પર લાગુ
થાય છે. ક્લાયન્ટને દેખાતા કોઈ પણ બાઇટ્સ મોકલવામાં આવે તે પહેલાં, હાલનો સમાન-એકાઉન્ટ
અર્લી-રિકવરી પાથ અટેમ્પને ફરી ખોલી શકે છે. કમિટ થયા પછી, સ્ટ્રીમને ક્યારેય વિચાર્યા
વિના ફરી ચલાવવામાં આવતી નથી; માત્ર હાલનો સુરક્ષિત મિડ-સ્ટ્રીમ કન્ટિન્યુએશન કોન્ટ્રાક્ટ
સફિક્સને જોડી શકે છે. ફાઇનલાઇઝેશન એક જ વાર થાય છે, તેથી ઉપયોગની ગણતરી અને સેમાફોર
રિલીઝની નકલ થતી નથી.

---

## 7. અપસ્ટ્રીમ સ્ટેટસનું પુનઃકથન (ખોટી રીતે દર્શાવેલી ક્વોટા ભૂલો)

**વ્યાપ:** એક અપસ્ટ્રીમ ગેટવે જે અસ્થાયી ક્વોટા સમાપ્તિને ખોટા HTTP સ્ટેટસ સાથે દર્શાવે છે.

**હેતુ:** વર્ગીકરણ પહેલાં ગેરમાર્ગે દોરતા સ્ટેટસને સુધારવો, જેથી ડાઉનસ્ટ્રીમ ગ્રાહકો (ફૉલબૅક એન્જિન, કોમ્બો એગ્રીગેશન, ક્લાયન્ટ-ફેસિંગ પ્રતિસાદ) નિષ્ફળતાનું વાસ્તવિક રીતે ફરી પ્રયાસ કરી શકાય તેવું સ્વરૂપ જોઈ શકે.

કેટલાક ગેટવે અસ્થાયી ક્વોટા સમાપ્તિને ફરી પ્રયાસ ન કરી શકાય તેવા HTTP
સ્ટેટસથી દર્શાવે છે. `agentrouter.org` પ્રમાણભૂત `429`ને બદલે ચાઇનીઝ બૉડી
(`用户额度不足` / `额度不足`) સાથે `403` (ક્યારેક `400`) પરત કરે છે. Claude
Code જેવા ક્લાયન્ટ્સ `403`ને કાયમી માનીને સેશન અટકાવી દે છે, અને સુધારા વિના
ફૉલબૅક એન્જિન તેને ક્વોટા ઇવેન્ટને બદલે `AUTH_ERROR` તરીકે વર્ગીકૃત કરશે.

**અમલીકરણ:**

- રજિસ્ટ્રી + મૅચર: `open-sse/config/upstreamStatusRestatement.ts` — નિયમોની
  પ્રતિ-પ્રોવાઇડર સૂચિ (`{id, fromStatuses, toStatus, textMarkers,
excludeMarkers, defaultRetryAfterMs}`), જે `applyStatusRestatement()` દ્વારા મૅચ થાય છે.
- કૉલ સાઇટ: `open-sse/handlers/chatCore.ts`માં `providerFailure:` બ્લૉક
  (લાઇન 3654ની આસપાસ), `parseUpstreamError()` ભૂલવાળા HTTP સ્ટેટસ
  (`!providerResponse.ok`) સાથે અપસ્ટ્રીમ પ્રતિસાદ પાર્સ કરે તેના તરત પછી અને કોઈ પણ
  વર્ગીકરણ ચાલે તે પહેલાં, જેથી દરેક ડાઉનસ્ટ્રીમ ગ્રાહક સુધારેલો સ્ટેટસ જોઈ શકે.
  `200` SSE સ્ટ્રીમમાં એમ્બેડ કરેલી ભૂલો એક અલગ, ત્યારપછીના સ્ટ્રીમ-પાર્સિંગ
  પાથને અનુસરે છે અને આજે આ હૂક હેઠળ **આવરી લેવાતી નથી** — આ એક જાણીતી
  મર્યાદા છે, જેની agentrouterની ખોટી સ્ટેટસ સમસ્યા માટે હજી જરૂર નથી (કારણ કે
  તે ભૂલવાળા HTTP સ્ટેટસ તરીકે સામે આવે છે).
- ફરી પ્રયાસ માટેની પાત્રતા: `429`, `RETRY_AFTER_ELIGIBLE_STATUSES`
  (`open-sse/services/combo/unavailableRetryGate.ts`)માં છે, તેથી પુનઃકથિત ભૂલ
  નિષ્ક્રિય `403` તરીકે સામે આવવાને બદલે વાસ્તવિક પુનઃપ્રયાસ વિન્ડો ધરાવે છે.
- કૃત્રિમ `60s` `defaultRetryAfterMs` (`upstreamStatusRestatement.ts`)
  ફક્ત એટલું જ છે જે પુનઃકથિત પ્રતિસાદ **ક્લાયન્ટ**ને જણાવે છે; તે પોતે
  કનેક્શનની આંતરિક કૂલડાઉન/લૉકઆઉટ અવધિ નથી — તેનું સંચાલન પુનઃકથિત ભૂલને
  ખરેખર હેન્ડલ કરતી મિકેનિઝમ દ્વારા અલગથી થાય છે (Connection Cooldownનું
  વધતું બૅકઑફ, §2, API-key પ્રોવાઇડર્સ માટે મૂળ `3s`; અથવા agentrouter જેવા
  પ્રતિ-મૉડલ-ક્વોટા પ્રોવાઇડર્સ માટે Model Lockout, §3). રાઉટર ક્લાયન્ટને
  જણાવેલી 60s વિન્ડો કરતાં વહેલો આંતરિક પુનઃપ્રયાસ માટે પાત્ર બની શકે છે —
  આ ઇરાદાપૂર્વકનું વધારાનું માર્જિન છે, બગ નહીં.

કાયમી ભૂલો (agentrouterનું `无权访问模型` — આ મૉડલને ઍક્સેસ કરવાની પરવાનગી નથી)
ક્યારેય પુનઃકથિત થતી નથી: `textMarkers` મૅચ થાય ત્યારે પણ `excludeMarkers`
નિયમને વીટો કરે છે, તેથી ભૂલ પોતાનો મૂળ સ્ટેટસ જાળવે છે અને કંઈ પણ તેનો
અનંતકાળ સુધી ફરી પ્રયાસ કરતું નથી. સંબંધિત પ્રોવાઇડર વર્ગીકરણ નિયમ
(`open-sse/config/providerErrorRules.ts`માં `agentrouter-model-access-denied`:
`reason: "auth_error"`, `scope: "model"`, જાહેર કરાયેલ `6h` મૂળ કૂલડાઉન)ને
`checkFallbackError` (`open-sse/services/accountFallback.ts`) દ્વારા સામાન્ય
apikey-કૅટેગરી `FORBIDDEN` અર્લી-રિટર્ન _પહેલાં_ તપાસવામાં આવે છે, જે
`honorsRuleLockScope(provider)` પર ગેટેડ છે (#10334 — હાલમાં
`providerErrorRules.ts`માં `HONORS_RULE_LOCK_SCOPE_PROVIDERS` અલાઉલિસ્ટ દ્વારા
ફક્ત agentrouter માટે). નિયમનું જાહેર કરાયેલ 6h કૂલડાઉન
`fallbackResult.baseCooldownMs` તરીકે આગળ વહે છે, પરંતુ તે હજી પણ પહેલેથી
હયાત પ્રતિ-મૉડલ-ક્વોટા લૉકઆઉટ પાથ (`lockModelIfPerModelQuota()` /
`recordModelLockoutFailure()`, કૂલડાઉન સ્ત્રોત સિવાય #10334થી અપરિવર્તિત)માં
જાય છે: અન્ય દરેક મૉડલ લૉકઆઉટની જેમ તેને ઑપરેટરના
`mlSettings.maxCooldownMs` (ડિફૉલ્ટ `1_800_000ms` / 30min) સુધી ઘટાડવામાં
આવે છે, અને _સંગ્રહિત લૉકઆઉટ કારણ_ નિયમના `"auth_error"`ને બદલે પહેલેથી
હાર્ડકોડ કરાયેલ `"forbidden"` જ રહે છે — ફક્ત કૂલડાઉન અવધિને છેડેથી છેડા સુધી
માન આપવામાં આવે છે, કારણ સ્ટ્રિંગને નહીં. કનેક્શન પોતે સક્રિય રહે છે;
સમાન કનેક્શન પરના અન્ય મૉડલ્સ અપ્રભાવિત રહે છે.

ફરીથી નિર્ધારિત ક્વોટા ભૂલો (`额度不足`) પ્રોડક્શનમાં પ્રોવાઇડર નિયમ સુધી પહોંચે છે
(`agentrouter-user-quota-exhausted`: `reason: "quota_exhausted"`, `scope:
"connection"`, તેનો પોતાનો કોઈ જાહેર કરાયેલ કૂલડાઉન નથી — પર્સિસ્ટન્સ લેયરનું
સ્કેલ કરાયેલ બૅકઑફ ડિફૉલ્ટ લાગુ થાય છે). #10334થી, `ProviderErrorRuleMatch` પરનો
`scope` એન્ડ-ટુ-એન્ડ ઉપયોગમાં લેવાય છે, પરંતુ **ફક્ત**
`HONORS_RULE_LOCK_SCOPE_PROVIDERS` અલાઉલિસ્ટમાં રહેલા પ્રોવાઇડર્સ માટે
(`providerErrorRules.ts` — હાલમાં ફક્ત `"agentrouter"`, `honorsRuleLockScope()`
દ્વારા ગેટ કરાયેલ). અન્ય દરેક પ્રોવાઇડર માટે `scope`, #10334 પહેલાંની જેમ જ,
માત્ર માહિતીપ્રદ રહે છે. `checkFallbackError` મેળ ખાતા નિયમનો સ્કોપ
`fallbackResult.ruleScope` તરીકે પ્રદર્શિત કરે છે;
`isAgentrouterConnectionQuotaScope()`
(`src/sse/services/auth.ts`) એ શેર કરાયેલ ગાર્ડ છે જે ખાતરી કરે છે કે
`ruleScope` ને કનેક્શન-વ્યાપી, સ્વયં-પુનઃપ્રાપ્ત થતા સંકેત તરીકે માન આપવું ખરેખર
સુરક્ષિત છે (સ્કોપ `"connection"`, કારણ `quota_exhausted`, ક્યારેય `permanent`
નહીં, ક્યારેય `creditsExhausted` નહીં — ભવિષ્યનો કોઈ નિયમ સ્કોપ
`"connection"` ને કાયમી એકાઉન્ટ સ્થિતિ સાથે જોડે તે સામેનું રક્ષણ). બે ઉપભોક્તાઓ
તેને કૉલ કરે છે:

- **પર્સિસ્ટન્સ** (`markAccountUnavailable()`, `src/sse/services/auth.ts`):
  પાસથ્રૂ-પ્રોવાઇડરની **પ્રતિ-મોડલ** લૉકઆઉટ બ્રાન્ચમાં જવાને બદલે
  (agentrouter માટે `passthroughModels: true` છે → `hasPerModelQuota()`
  `true` પરત કરે છે), તે **અસ્થાયી કનેક્શન કૂલડાઉન** લાગુ કરે છે —
  `testStatus: "unavailable"` + `rateLimitedUntil`, ક્યારેય ટર્મિનલ સ્થિતિ
  (`credits_exhausted`/`banned`/`expired`) નહીં — જેથી કૂલડાઉન પૂર્ણ થયા પછી
  કનેક્શન મેન્યુઅલ ક્રેડેન્શિયલ રીસેટની જરૂર વિના સ્વયં પુનઃપ્રાપ્ત થાય.
  `disableCooling: true` ધરાવતા કનેક્શન્સ માટે આ છોડવામાં આવે છે (#2997):
  તે ઑપ્ટ-આઉટ તેના બદલે પ્રતિ-મોડલ લૉકઆઉટ તરફ આગળ વધે છે (દસ્તાવેજીકૃત
  સમાધાન — બ્રાન્ચની ઉપરની કોડ ટિપ્પણી જુઓ).
- **એજ-વિનંતી કોમ્બો રાઉટિંગ** (`applyComboTargetExhaustion()`,
  `open-sse/services/combo/targetExhaustion.ts`): એ જ ગાર્ડ કનેક્શનને
  ઇન-મેમરી `exhaustedConnections` સેટમાં ચિહ્નિત કરે છે, જે
  `${provider}:${connectionId}` દ્વારા કી કરાયેલ છે. આ ફક્ત બાકી રહેલા એવા
  SAME-REQUEST લક્ષ્યને છોડે છે જે _પોતાના લક્ષ્ય ઑબ્જેક્ટ પર તે જ ચોક્કસ
  `connectionId` પહેલેથી ધરાવે છે_ (`getExhaustedTargetSkipReason()`,
  `open-sse/services/combo/comboPredicates.ts`, `if (provider &&
connectionId)` ને `exhaustedConnections` લુકઅપ પહેલાં) — સામાન્ય
  મોડલ-લિસ્ટ કોમ્બોમાં, જ્યાં સમકક્ષ લક્ષ્યો પોતાનો કોઈ પિન કરાયેલ `connectionId`
  ધરાવતા નથી અને પ્રતિ-ડિસ્પૅચ માત્ર પ્રતિસાદના
  `X-OmniRoute-Selected-Connection-Id` હેડરમાંથી એક ઉકેલવામાં આવે છે, ત્યાં
  તે કી ક્યારેય મેળ ખાતી નથી. તે સામાન્ય કિસ્સામાં, બાકી રહેલો લેગ હમણાં જ
  નિઃશેષ થયેલા એકાઉન્ટનો ફરીથી ઉપયોગ ન કરે તે માટેનું વાસ્તવિક રક્ષણ આ Set
  **નથી** — તે ઉપરનું પર્સિસ્ટન્સ લેયર (કનેક્શનનું `rateLimitedUntil` હવે
  ભવિષ્યમાં છે) અને આ જ ગાર્ડ દ્વારા નિષ્ફળતા માટે
  `transientRateLimitedProviders` ને દબાવવાનું સંયોજન છે ("બે-તબક્કાની ડિઝાઇન"
  અને `targetExhaustion.ts` માં `isAgentrouterConnectionQuotaScope` બ્રાન્ચ
  પરની કોડ ટિપ્પણી જુઓ): તે Set ને અચિહ્નિત રાખવાથી, `combo.ts` નું
  `allowRateLimitedConnection` ફોર્સ-અલાઉ
  (`open-sse/services/combo.ts:1005-1013`, `:2734-2738`) પ્રોવાઇડરના બાકી
  લેગ્સ માટે સક્રિય **થતું નથી**, તેથી ક્રેડેન્શિયલ પસંદગીના
  `rateLimitedUntil` ફિલ્ટર (`src/sse/services/auth.ts:1238`) નું સામાન્ય રીતે
  પાલન થાય છે અને બાકી રહેલો લેગ કાં તો અલગ, હજુ પણ પાત્ર agentrouter
  કનેક્શન પસંદ કરે છે અથવા કોઈ ક્રેડેન્શિયલ ઉપલબ્ધ ન હોવાથી નિષ્ફળ જાય છે —
  આ બ્રાન્ચે હમણાં જ કૂલડાઉનમાં મૂકેલા કનેક્શન પર તે બળજબરીથી પાછો જતો નથી.

### બે-તબક્કાની ડિઝાઇન: સ્થિતિનું પુનઃનિર્ધારણ, પછી વર્ગીકરણ

સ્થિતિનું પુનઃનિર્ધારણ (`upstreamStatusRestatement.ts`) અને પ્રોવાઇડર
વર્ગીકરણ નિયમો (`open-sse/config/providerErrorRules.ts`,
`providerRuleRegistry`) અલગ રજિસ્ટ્રીઓ છે, જે બંને પ્રોવાઇડર id અને ટેક્સ્ટ
માર્કર્સને કી તરીકે ઉપયોગ કરે છે, પરંતુ તેઓ અલગ સ્થળોએ ચાલે છે અને અલગ
હેતુઓ પૂરા કરે છે: પુનઃનિર્ધારણ `chatCore.ts` માં HTTP સ્થિતિ વહેલી તકે ફરીથી
લખે છે; વર્ગીકરણ નિયમો `checkFallbackError()` ની અંદર ફૉલબૅક `reason` અને
લૉક `scope` (`model` / `provider` / `connection`) પસંદ કરે છે
(`open-sse/services/accountFallback.ts`).

વર્ગીકરણ નિયમો સંપૂર્ણ ભૂલ **ટેક્સ્ટ** (જેમ કે `额度不足` જેવા બૉડી માર્કર્સને
મેળવવા માટે જરૂરી) ફક્ત `providerErrorRules.ts` માંના
`FULL_TEXT_RULE_PROVIDERS` અલાઉલિસ્ટમાં સૂચિબદ્ધ પ્રોવાઇડર્સ માટે જ જુએ છે —
હાલમાં ફક્ત `"agentrouter"`. અન્ય દરેક **બિલ્ટ-ઇન કૅટલૉગ** પ્રોવાઇડર માટે,
`checkFallbackError`, `getProviderErrorRuleMatch` ને ફક્ત સ્ટ્રક્ચર્ડ ભૂલ
(`{code, type}`) આપે છે, જે હેડર/સ્થિતિ/કોડ-આધારિત નિયમો માટે પૂરતી છે પરંતુ
બૉડી-ટેક્સ્ટ માર્કર્સ જોઈ શકતી નથી. હેલ્પર `resolveRuleMatchBody()` આ પસંદગી
કરે છે: અલાઉલિસ્ટમાં રહેલા પ્રોવાઇડર્સ માટે સંપૂર્ણ ભૂલ ટેક્સ્ટ, અન્યથા
સ્ટ્રક્ચર્ડ ભૂલ. કોઈ **બિલ્ટ-ઇન** પ્રોવાઇડરને `FULL_TEXT_RULE_PROVIDERS` માં
ઉમેરવું એ સ્પષ્ટ પ્રતિ-પ્રોવાઇડર ઑપ્ટ-ઇન છે — તે એટલા માટે છે કે સૂચિમાં ન
હોય તેવા દરેક પ્રોવાઇડર માટેનો ડિફૉલ્ટ પાથ બાઇટ-ફૉર-બાઇટ અપરિવર્તિત રહે.

નિયમનો `scope` (`model` / `provider` / `connection`) એ
`FULL_TEXT_RULE_PROVIDERS` થી અલગ ઑપ્ટ-ઇન છે: `checkFallbackError` તેને ફક્ત
`fallbackResult.ruleScope` તરીકે પ્રદર્શિત કરે છે, અને ડાઉનસ્ટ્રીમ ઉપભોક્તાઓ
તે જ ફાઇલના `HONORS_RULE_LOCK_SCOPE_PROVIDERS` અલાઉલિસ્ટમાં રહેલા પ્રોવાઇડર્સ
માટે જ તેને માહિતીપ્રદ લેબલ કરતાં વધુ કંઈક તરીકે માને છે (`gated via
honorsRuleLockScope()` — હાલમાં ફક્ત `"agentrouter"`). કોઈ પ્રોવાઇડર તે
અલાઉલિસ્ટમાં આવે પછી `scope: "connection"` મેળ વાસ્તવમાં શું કરે છે તે માટે
ઉપરનું "ફરીથી નિર્ધારિત ક્વોટા ભૂલો" જુઓ.

**#11104 — ઑપરેટર દ્વારા જાહેર કરાયેલા નિયમો બંને allowlistને બાયપાસ કરે છે.** ઑપરેટર
આ ફાઇલમાં ફેરફાર કર્યા વિના `settings.providerErrorRules`
(`open-sse/config/providerErrorRules.ts::setOperatorProviderErrorRules`)
મારફતે runtime પર provider-દીઠ નિયમ જાહેર કરી શકે છે. ઑપરેટર નિયમને
`FULL_TEXT_RULE_PROVIDERS`/`HONORS_RULE_LOCK_SCOPE_PROVIDERS` પાછળ gate કરવાથી — આ allowlist
બિલ્ટ-ઇન catalog નિયમોના **ડિફૉલ્ટ** વર્તનને સુરક્ષિત રાખવા માટે છે —
પહેલેથી ત્યાં સૂચિબદ્ધ provider સિવાય દરેક provider માટે settings વ્યવસ્થા
નિષ્ક્રિય બની જશે, કારણ કે નિયમ જાહેર કરવો એ પોતે જ ઑપરેટરનું સ્પષ્ટ
opt-in છે. `resolveRuleMatchBody()` અને `honorsRuleLockScope()` બંને પહેલાં
`hasOperatorRuleForProvider()` તપાસે છે: ઑપરેટર નિયમ ધરાવતા providerને
કાચો error text મળે છે અને તેના દ્વારા જાહેર કરાયેલા `scope`નું પાલન થાય છે,
ભલે તે કોઈ એક અથવા બંને allowlistમાં દેખાતો ન હોય.

**જાણીતી ખામી — HTTP 400 માટે `providerRuleRegistry`નો ક્યારેય ઉપયોગ થતો નથી.**
`checkFallbackError`ની `BAD_REQUEST` branch status 400ને સંપૂર્ણપણે
તેના પોતાના pattern array (`MODEL_ACCESS_DENIED_PATTERNS`,
`CONTEXT_OVERFLOW_PATTERNS`, વગેરે `accountFallback.ts`માં) દ્વારા વર્ગીકૃત કરે છે અને
તેની ઉપરની `configuredRule`/`getProviderErrorRuleMatch` branch સુધી પહોંચતાં પહેલાં
પરત ફરે છે. `status: 400` ધરાવતો બિલ્ટ-ઇન catalog નિયમ (અથવા ઑપરેટર નિયમ)
વાક્યરચનાની દૃષ્ટિએ માન્ય છે, પરંતુ તે ક્યારેય અમલમાં આવશે નહીં. આજે કોઈ વર્તમાન નિયમ 400ને લક્ષ્ય બનાવતો નથી,
તેથી productionમાં કંઈ અસરગ્રસ્ત નથી — પરંતુ ભવિષ્યના 400 નિયમ માટે પહેલાં આ
branchમાં ફેરફાર કરવો પડશે, જે માત્ર એક નિયમ ઉમેરવા કરતાં મોટો ફેરફાર છે (તે
pattern-array વર્તન પર પહેલેથી નિર્ભર દરેક provider માટે 400નું
પુનઃવર્ગીકરણ કરે છે) અને એક provider માટે નિયમ ઉમેરવાના કાર્યક્ષેત્રની બહાર છે.

### ક્વોટા વિશે ખોટી માહિતી આપતો નવો gateway ઉમેરવો

1. `statusRestatementRegistry`
   (`open-sse/config/upstreamStatusRestatement.ts`)માં એક rule array register કરો. `textMarkers`
   provider-વિશિષ્ટ રાખો; `CREDITS_EXHAUSTED_SIGNALS`
   (`open-sse/services/accountFallback.ts`) સાથે ટકરાતા સામાન્ય અંગ્રેજી શબ્દસમૂહોનો ક્યારેય પુનઃઉપયોગ કરશો નહીં.
2. યોગ્ય lock scope પસંદ કરવા માટે વૈકલ્પિક રીતે
   `open-sse/config/providerErrorRules.ts` (`providerRuleRegistry`)માં classification rules
   register કરો (`connection` account-વ્યાપી quota માટે, `model`
   model-દીઠ errors માટે). આ પગલું productionમાં માત્ર એવા
   providers માટે અસરકારક બને છે, જેમના rulesને સંપૂર્ણ error text (body markers)ની જરૂર હોય: એ જ
   ફાઇલમાં provider idને `FULL_TEXT_RULE_PROVIDERS`માં ઉમેરો — નહિતર
   `checkFallbackError` નિયમને માત્ર structured
   `{code, type}` error આપે છે અને body-text નિયમ live traffic સાથે ક્યારેય મેળ નહીં ખાય.
   માત્ર `status`/`headers` પર મેળ ખાતા rules (જેમ કે Opencode અથવા
   Minimaxના)ને આ opt-inની જરૂર નથી. અલગથી, જો નિયમ
   `scope: "connection"` જાહેર કરે અને હેતુ વાસ્તવિક connection-વ્યાપી cooldown
   તેમજ same-request combo skip હોય (માત્ર માહિતીપ્રદ label નહીં), તો એ જ
   ફાઇલમાં provider idને `HONORS_RULE_LOCK_SCOPE_PROVIDERS`માં ઉમેરો — આ
   `markAccountUnavailable()` (`src/sse/services/auth.ts`) અને
   `applyComboTargetExhaustion()`
   (`open-sse/services/combo/targetExhaustion.ts`)માં
   `isAgentrouterConnectionQuotaScope()`-શૈલીના consumptionને gate કરે છે; તેના વિના `scope`
   હજુ પણ `fallbackResult.ruleScope`માંથી પસાર થાય છે, પરંતુ તેના આધારે કોઈ કાર્યવાહી થતી નથી.
3. `tests/unit/upstream-status-restatement.test.ts`
   અને `tests/unit/agentrouter-error-rules.test.ts`ને અનુરૂપ unit tests ઉમેરો (જેમાં
   not-permanent / not-creditsExhausted guards સામેલ હોય અને — જો providerને
   allowlistની જરૂર હોય — માત્ર તે provider માટે જ `resolveRuleMatchBody()` સંપૂર્ણ
   text પરત કરે છે એવું નિશ્ચિત કરતો test પણ સામેલ હોય).

`chatCore.ts`, `classifyError` અથવા comboમાં કોઈ ફેરફાર જરૂરી નથી.

#### Egress-bucketed lock (#10880)

`EGRESS_BUCKETED_LOCK_PROVIDERS`માં રહેલા providers (opencode family)ને
IP-bucketed upstream તરીકે ગણવામાં આવે છે (opencode free tier IP-bucketed છે,
account-bucketed નહીં — #9611 જુઓ): `quota_exhausted`
**અથવા** `rate_limit_exceeded` તરીકે વર્ગીકૃત થયેલું status-429, rotation તેમને અજમાવી શકે તે પહેલાં,
નિષ્ફળ થયેલા connectionના છેલ્લે જાણીતા egress IP સાથે મેળ ખાતા દરેક allowlisted-family connectionને
cooldownમાં મૂકે છે
— જેથી N-1 નિશ્ચિતપણે નિષ્ફળ થનારા upstream calls ટાળી શકાય (#10460/#10525 જેવી જ રચના).
`rate_limit_exceeded`ને ઇરાદાપૂર્વક સામેલ કરવામાં આવ્યું છે: `markAccountUnavailable`
path પર opencode-વિશિષ્ટ rules ક્યારેય match થતા નથી (કોઈ headers/body
`checkFallbackError`ને આપવામાં આવતા નથી, opencode `FULL_TEXT_RULE_PROVIDERS`માં નથી), તેથી એવો 429
જેના bodyમાં subscription-quota text ("monthly usage limit
reached") હોય તેને `status_429` rule સુધી પહોંચે તે પહેલાં
quota-text fallback
(`buildSubscriptionQuotaFallback`, `accountFallback.ts`; 1h cooldown) દ્વારા `quota_exhausted`
તરીકે વર્ગીકૃત કરવામાં આવે છે — જ્યારે quota-text વિનાનો 429 (સાદું
rate limiting) `status_429` rule મારફતે `rate_limit_exceeded` તરીકે વર્ગીકૃત થાય છે
અને તેમ છતાં IP familyને cooldownમાં મૂકે છે. allowlisted provider માટે IP-bucketed
rate limit એ exhausted quota જેવો જ signal છે. વાસ્તવિક મર્યાદાઓ:

- **શ્રેષ્ઠ પ્રયાસ**: લૉક `proxy_logs`માંથી કનેક્શનનું છેલ્લે જાણીતું `egress_ip`
  શોધે છે (24h વિન્ડો, સિંક્રોનસ, કોઈ કૅશ નહીં). કોલ્ડ કૅશ (egress
  IP ક્યારેય પ્રોબ ન થયો હોય) અથવા કોઈ પંક્તિ ન હોય → નિષ્ફળ કનેક્શનને હજી પણ
  બ્રાન્ચ દ્વારા કૂલડાઉન કરવામાં આવે છે (આજની જેમ રેકોર્ડ કરવામાં આવે છે), ફક્ત કોઈ સિબ્લિંગ લૉક થતું નથી.
- **ક્યારેય ટર્મિનલ નહીં**: કૂલડાઉન એક નવીનીકૃત થતી ક્વોટા વિન્ડો છે
  (`testStatus: "unavailable"`); IP-સ્તરના સિગ્નલમાંથી ક્યારેય કાયમી સ્થિતિ
  નક્કી કરવામાં આવતી નથી. `disableCooling` કનેક્શનો બ્રાન્ચને સંપૂર્ણપણે અવગણે છે.
- **અલાઉલિસ્ટ કરેલા ફૅમિલી માટે લૉકની ગ્રેન્યુલારિટી બદલાય છે**: આ સ્કોપમાં
  ફેરફાર છે, માત્ર સિબ્લિંગ ઑપ્ટિમાઇઝેશન નહીં. opencode એ `passthroughModels`
  પ્રોવાઇડર છે, તેથી આ બ્રાન્ચ પહેલાં 429 પ્રતિ-MODEL લૉકઆઉટ સર્જતું હતું; હવે તે
  કનેક્શન કૂલડાઉન સર્જે છે — જેમાં કોઈપણ સિબ્લિંગ વિના એકમાત્ર
  કનેક્શન ચલાવતા ઑપરેટરનો પણ સમાવેશ થાય છે. આ એ ગ્રેન્યુલારિટી છે જેને opencode નિયમ
  કોષ્ટક પહેલેથી જ યોગ્ય જાહેર કરે છે (`scope: "connection"`,
  `providerErrorRules.ts`), પરંતુ અત્યાર સુધી તેનું ક્યારેય પાલન થયું નથી કારણ કે opencode
  `HONORS_RULE_LOCK_SCOPE_PROVIDERS`માં નથી. બ્રાન્ચ નિષ્ફળ
  કનેક્શનનું કૂલડાઉન + `backoffLevel` જાતે લખે છે, કનેક્શન-સ્કોપવાળી
  agentrouter બ્રાન્ચને પ્રતિબિંબિત કરે છે, અને પરત ફરે છે — પ્રતિ-મોડેલ બ્લૉક અને
  નીચેનો સામાન્ય પાથ ક્યારેય પહોંચતા નથી.
- **કોમ્બો સામેલ છે**: agentrouter બ્રાન્ચની જેમ, સ્કોપ જાણીજોઈને
  `persistUnavailableState`/`isCombo` ડાઉનગ્રેડને અવગણે છે, જે કોમ્બો કૉલર
  429 પર લાગુ કરે છે. પ્રતિ-મોડેલ લૉકઆઉટ આ સ્કોપનું નબળું સ્વરૂપ નથી, તે
  ખોટું એકમ છે: તે સમાપ્ત થયેલા IP વિશે કશું કહેતું નથી, તેથી કોમ્બો
  રોટેશન દરેક સિબ્લિંગ દીઠ ખાતરીપૂર્વક નિષ્ફળ થતો એક કૉલ વેડફવાનું ચાલુ રાખશે.
- **સિબ્લિંગ સલામતી**: પહેલેથી ટર્મિનલ (banned/credits_exhausted) થયેલ
  અથવા પહેલેથી વધુ લાંબા કૂલડાઉનમાં રહેલ સિબ્લિંગને ક્યારેય ઓવરરાઇટ કરવામાં આવતું નથી.
- **એક્સક્લૂસિવ અલાઉલિસ્ટ**: `EGRESS_BUCKETED_LOCK_PROVIDERS`ને વિસ્તૃત કરવું એ
  સ્પષ્ટ ઑનર નિર્ણય છે; કોઈ સામાન્ય વાયરિંગ નહીં (પૅટર્ન #10334/#10419).
  સિબ્લિંગ ક્વેરી એ જ અલાઉલિસ્ટને SQL
  લિટરલ તરીકે પુનરાવર્તિત કરવાને બદલે બાઇન્ડ કરે છે, તેથી તેને વિસ્તૃત કરવું એક-લાઇનનો ફેરફાર રહે છે.
- **Egress IP રોટેશન, બંને દિશામાં**: લુકઅપ વિન્ડો (24h), egress-IP કૅશ TTL
  (5 min) કરતાં ઘણી વિશાળ છે, તેથી "છેલ્લે જાણીતો IP" ઇતિહાસ છે,
  વર્તમાન સ્થિતિ નહીં. જો કોઈ કનેક્શનનો પ્રૉક્સી આ વિન્ડોમાં રોટેટ થયો હોય, તો
  લૉક ખરેખર શેર થયેલો IP **ચૂકી** શકે છે (રેકોર્ડ થયેલો IP નવો,
  સમાપ્ત ન થયેલો હોય છે) — અને સમાન રીતે તે એવા સિબ્લિંગને **કૂલ કરી શકે છે જે ત્યારથી
  રોટેટ થઈને** સમાપ્ત થયેલા IPથી દૂર થઈ ગયું હોય. બીજા કિસ્સામાં તે સિબ્લિંગને એક
  કૂલડાઉન વિન્ડોનો ખર્ચ થાય છે; બંનેને ઇતિહાસ-આધારિત
  લુકઅપની સ્વીકારેલી શ્રેષ્ઠ-પ્રયાસ મર્યાદાઓ માનવામાં આવે છે.
- **ખર્ચ**: `proxy_logs`ના બે મર્યાદિત સ્કૅન (વિન્ડો-ફિલ્ટરિંગ
  `idx_pl_timestamp` મારફતે), માત્ર 429ની આવર્તન પર. કોઈ નવો ઇન્ડેક્સ નહીં (માઇગ્રેશન 134
  YAGNI). મધ્યમ કદની વાસ્તવિક-ટ્રાફિક DB કૉપી પર માપવામાં આવ્યું છે;
  ઉચ્ચ-થ્રૂપુટ ઇન્સ્ટન્સ સમાન વિન્ડોમાં પ્રમાણસર વધુ પંક્તિઓ રાખે છે.

---

## અન્ય સ્થિતિસ્થાપકતા સુવિધાઓ

- **19 રાઉટિંગ વ્યૂહરચનાઓ** (પ્રાથમિકતા, વેઇટેડ, રાઉન્ડ-રોબિન, કોન્ટેક્સ્ટ-રિલે, ફિલ-ફર્સ્ટ, p2c, રેન્ડમ, સૌથી ઓછું વપરાયેલ, ખર્ચ-ઑપ્ટિમાઇઝ્ડ, રીસેટ-અવેર, રીસેટ-વિન્ડો, હેડરૂમ, સ્ટ્રિક્ટ-રેન્ડમ, ઑટો, lkgp, કોન્ટેક્સ્ટ-ઑપ્ટિમાઇઝ્ડ, કૅશ-ઑપ્ટિમાઇઝ્ડ, ફ્યુઝન, પાઇપલાઇન) — [AUTO-COMBO.md](../routing/AUTO-COMBO.md) જુઓ.
- **રીસેટ-અવેર રાઉટિંગ** (v3.8.0) — ક્વોટા રીસેટ સમયના આધારે કનેક્શન્સને પ્રાથમિકતા આપે છે.
- **બૅકગ્રાઉન્ડ મોડ ડિગ્રેડેશન** — Responses API `background: true` ને ચેતવણી સાથે સિંક મોડમાં ડિગ્રેડ કરવામાં આવે છે.
- **ડાયનેમિક ટૂલ મર્યાદા શોધ** — ટૂલની સંખ્યા મર્યાદા સુધી પહોંચે ત્યારે પ્રોવાઇડર્સથી પાછળ હટે છે.
- **ઇમરજન્સી ફૉલબૅક** — `OMNIROUTE_EMERGENCY_FALLBACK` દ્વારા નિયંત્રિત; ઑપરેટર્સ તેને રીસ્ટાર્ટ કર્યા વિના Feature Flags પેજ પરથી ઓવરરાઇડ કરી શકે છે.

---

## ડિબગિંગ

- વેઇટેડ કોમ્બો `503 all_targets_cooling_down` જવાબ આપે છે (`Retry-After` સેટ હોય છે, `diagnostics.excluded` દરેક ટાર્ગેટને `model_lockout` / `circuit_open` / `provider_cooldown` / `unavailable` સાથે સૂચિબદ્ધ કરે છે) → પૂલ કૉન્ફિગર અને કનેક્ટ થયેલો છે, પરંતુ દરેક ટાર્ગેટ રેઝિલિયન્સ ટાઇમર દ્વારા બાકાત રાખવામાં આવ્યો છે; `[COMBO] Weighted selection: every target excluded before dispatch — …` ચેતવણી કારણો અને બાકી રહેલી સેકન્ડ દર્શાવે છે. એ જ કોમ્બોમાંથી મળતો `404 no_executable_targets` દર્શાવે છે કે કોઈ રેઝિલિયન્સ ટાઇમર સામેલ નહોતો (ચલાવવા માટે કંઈ નથી અથવા દરેક એકાઉન્ટ અવેલેબિલિટી પ્રોબમાં નિષ્ફળ ગયું). આ `targetResolution.ts` માં એકત્રિત કરાયેલા એક્સક્લુઝન્સમાંથી `open-sse/services/combo/pinRecovery.ts` માં બનાવવામાં આવે છે.
- કોઈ પ્રોવાઇડરની બધી કીઓ સ્કિપ થાય → સર્કિટ બ્રેકરની સ્થિતિ અને દરેક કનેક્શનના `rateLimitedUntil`/`testStatus`, બંને તપાસો.
- રીસેટ વિન્ડો પછી પણ પ્રોવાઇડર કાયમી રીતે બાકાત રહે → કોડ `getStatus()`/`canExecute()` ને બદલે સીધું `state` વાંચી રહ્યો છે.
- એક કી નિષ્ફળ જાય, પરંતુ બાકીની કાર્ય કરવી જોઈએ → સર્કિટ બ્રેકર કરતાં કનેક્શન કૂલડાઉનને પ્રાથમિકતા આપો.
- માત્ર એક મોડેલ નિષ્ફળ જાય → કનેક્શન કૂલડાઉન કરતાં મોડેલ લૉકઆઉટને પ્રાથમિકતા આપો.
- સ્થિતિ આપમેળે પુનઃપ્રાપ્ત થવી જોઈએ, પરંતુ થતી નથી → ભવિષ્યના ટાઇમસ્ટૅમ્પ અને સમાપ્ત થયેલી સ્થિતિને રિફ્રેશ કરતા રીડ પાથ માટે તપાસો. કાયમી સ્ટેટસ માટે મેન્યુઅલ ફેરફારો જરૂરી છે.

---

## TLS ફિંગરપ્રિન્ટિંગ અને સ્ટેલ્થ

પ્રોવાઇડર-વિશિષ્ટ સ્ટેલ્થ (JA3/JA4, CCH, ઑબ્ફસ્કેશન) અલગથી દસ્તાવેજીકૃત છે — `docs/security/STEALTH_GUIDE.md` જુઓ (git; `/docs` માં કમ્પાઇલ કરેલ નથી).

---

## સ્થિતિસ્થાપકતા પરીક્ષણ (તબક્કો 8 · બ્લૉક C)

સ્થિતિસ્થાપકતા લૉજિક માટેના યુનિટ ટેસ્ટ્સ ઉપરાંત, ત્રણ ટેસ્ટ્સ વાસ્તવિક તણાવ/નિષ્ફળતા પરિસ્થિતિઓ હેઠળ રનટાઇમનું પરીક્ષણ કરે છે (બધા ઇન્ટિગ્રેશન/નાઇટલી — કોઈપણ PRs ને બ્લૉક કરતા નથી):

| ટેસ્ટ     | શું                                                                                                                                                                                         | ચલાવવું                                 |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| કેઓસ      | ફેક-અપસ્ટ્રીમ નોડ વાસ્તવિક લેટન્સી/રીસેટ/ટાઇમઆઉટ/503 ઇન્જેક્ટ કરે છે; ચકાસે છે કે સર્કિટ બ્રેકર ખૂલે/પુનઃપ્રાપ્ત થાય અને `checkFallbackError` 503 ને પુનઃપ્રાપ્ય ફૉલબૅક તરીકે વર્ગીકૃત કરે. | `RUN_CHAOS_INT=1 npm run test:chaos`    |
| હીપ-ગ્રોથ | `--expose-gc` હેઠળ પ્રત્યેક `createSSEStream` દીઠ ~500 સ્ટ્રીમ્સ; જો હીપ નિર્ધારિત મર્યાદાથી વધુ વધે તો નિષ્ફળ થાય છે (OOM ગાર્ડ #3069).                                                    | `npm run test:heap`                     |
| k6 સોક    | `/api/monitoring/health` સામે સતત લોડ; p95/ભૂલ થ્રેશોલ્ડ્સ.                                                                                                                                 | `k6 run tests/load/k6-soak.js` (નાઇટલી) |

`.github/workflows/nightly-resilience.yml` (cron + dispatch) દ્વારા સંચાલિત. ડિફૉલ્ટ
`test:integration` માં, કેઓસ અને હીપ પોતાને સ્કિપ કરે છે (`RUN_CHAOS_INT`/`--expose-gc` વિના).

---

## આ પણ જુઓ

- [આર્કિટેક્ચર માર્ગદર્શિકા](./ARCHITECTURE.md) — સિસ્ટમ આર્કિટેક્ચર અને આંતરિક રચના
- [વપરાશકર્તા માર્ગદર્શિકા](../guides/USER_GUIDE.md) — પ્રદાતાઓ, કોમ્બોઝ, CLI એકીકરણ
- [ઑટો-કોમ્બો એન્જિન](../routing/AUTO-COMBO.md) — 16-પરિબળ સ્કોરિંગ, મોડ પૅક્સ
