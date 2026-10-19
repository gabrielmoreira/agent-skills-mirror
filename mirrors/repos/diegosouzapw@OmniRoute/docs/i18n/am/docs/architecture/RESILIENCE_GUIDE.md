# Resilience Guide (አማርኛ)

🌐 **Languages:** 🇺🇸 [English](../../../../architecture/RESILIENCE_GUIDE.md) · 🇸🇦 [ar](../../../ar/docs/architecture/RESILIENCE_GUIDE.md) · 🇦🇿 [az](../../../az/docs/architecture/RESILIENCE_GUIDE.md) · 🇧🇬 [bg](../../../bg/docs/architecture/RESILIENCE_GUIDE.md) · 🇧🇩 [bn](../../../bn/docs/architecture/RESILIENCE_GUIDE.md) · 🇧🇦 [bs](../../../bs/docs/architecture/RESILIENCE_GUIDE.md) · 🇨🇿 [cs](../../../cs/docs/architecture/RESILIENCE_GUIDE.md) · 🇩🇰 [da](../../../da/docs/architecture/RESILIENCE_GUIDE.md) · 🇩🇪 [de](../../../de/docs/architecture/RESILIENCE_GUIDE.md) · 🇬🇷 [el](../../../el/docs/architecture/RESILIENCE_GUIDE.md) · 🇪🇸 [es](../../../es/docs/architecture/RESILIENCE_GUIDE.md) · 🇪🇪 [et](../../../et/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇷 [fa](../../../fa/docs/architecture/RESILIENCE_GUIDE.md) · 🇫🇮 [fi](../../../fi/docs/architecture/RESILIENCE_GUIDE.md) · 🇫🇷 [fr](../../../fr/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇪 [ga](../../../ga/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [gu](../../../gu/docs/architecture/RESILIENCE_GUIDE.md) · 🇳🇬 [ha](../../../ha/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇱 [he](../../../he/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [hi](../../../hi/docs/architecture/RESILIENCE_GUIDE.md) · 🇭🇷 [hr](../../../hr/docs/architecture/RESILIENCE_GUIDE.md) · 🇭🇺 [hu](../../../hu/docs/architecture/RESILIENCE_GUIDE.md) · 🇦🇲 [hy](../../../hy/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇩 [id](../../../id/docs/architecture/RESILIENCE_GUIDE.md) · 🇳🇬 [ig](../../../ig/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇹 [it](../../../it/docs/architecture/RESILIENCE_GUIDE.md) · 🇯🇵 [ja](../../../ja/docs/architecture/RESILIENCE_GUIDE.md) · 🇬🇪 [ka](../../../ka/docs/architecture/RESILIENCE_GUIDE.md) · 🇰🇭 [km](../../../km/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [kn](../../../kn/docs/architecture/RESILIENCE_GUIDE.md) · 🇰🇷 [ko](../../../ko/docs/architecture/RESILIENCE_GUIDE.md) · 🇱🇹 [lt](../../../lt/docs/architecture/RESILIENCE_GUIDE.md) · 🇱🇻 [lv](../../../lv/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [ml](../../../ml/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [mr](../../../mr/docs/architecture/RESILIENCE_GUIDE.md) · 🇲🇾 [ms](../../../ms/docs/architecture/RESILIENCE_GUIDE.md) · 🇲🇹 [mt](../../../mt/docs/architecture/RESILIENCE_GUIDE.md) · 🇲🇲 [my](../../../my/docs/architecture/RESILIENCE_GUIDE.md) · 🇳🇵 [ne](../../../ne/docs/architecture/RESILIENCE_GUIDE.md) · 🇳🇱 [nl](../../../nl/docs/architecture/RESILIENCE_GUIDE.md) · 🇳🇴 [no](../../../no/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [or](../../../or/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [pa](../../../pa/docs/architecture/RESILIENCE_GUIDE.md) · 🇵🇭 [phi](../../../phi/docs/architecture/RESILIENCE_GUIDE.md) · 🇵🇱 [pl](../../../pl/docs/architecture/RESILIENCE_GUIDE.md) · 🇵🇹 [pt](../../../pt/docs/architecture/RESILIENCE_GUIDE.md) · 🇧🇷 [pt-BR](../../../pt-BR/docs/architecture/RESILIENCE_GUIDE.md) · 🇷🇴 [ro](../../../ro/docs/architecture/RESILIENCE_GUIDE.md) · 🇷🇺 [ru](../../../ru/docs/architecture/RESILIENCE_GUIDE.md) · 🇱🇰 [si](../../../si/docs/architecture/RESILIENCE_GUIDE.md) · 🇸🇰 [sk](../../../sk/docs/architecture/RESILIENCE_GUIDE.md) · 🇸🇮 [sl](../../../sl/docs/architecture/RESILIENCE_GUIDE.md) · 🇷🇸 [sr](../../../sr/docs/architecture/RESILIENCE_GUIDE.md) · 🇸🇪 [sv](../../../sv/docs/architecture/RESILIENCE_GUIDE.md) · 🇰🇪 [sw](../../../sw/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [ta](../../../ta/docs/architecture/RESILIENCE_GUIDE.md) · 🇮🇳 [te](../../../te/docs/architecture/RESILIENCE_GUIDE.md) · 🇹🇭 [th](../../../th/docs/architecture/RESILIENCE_GUIDE.md) · 🇹🇷 [tr](../../../tr/docs/architecture/RESILIENCE_GUIDE.md) · 🇺🇦 [uk-UA](../../../uk-UA/docs/architecture/RESILIENCE_GUIDE.md) · 🇵🇰 [ur](../../../ur/docs/architecture/RESILIENCE_GUIDE.md) · 🇺🇿 [uz](../../../uz/docs/architecture/RESILIENCE_GUIDE.md) · 🇻🇳 [vi](../../../vi/docs/architecture/RESILIENCE_GUIDE.md) · 🇳🇬 [yo](../../../yo/docs/architecture/RESILIENCE_GUIDE.md) · 🇨🇳 [zh-CN](../../../zh-CN/docs/architecture/RESILIENCE_GUIDE.md) · 🇹🇼 [zh-TW](../../../zh-TW/docs/architecture/RESILIENCE_GUIDE.md)

---

OmniRoute ሦስት የተለያዩ ግን ተዛማጅ የመቋቋም ዘዴዎች አሉት። እያንዳንዳቸው የተለየ ወሰንና ዓላማ አላቸው። የማዞሪያ ባህሪን ሲያርሙ እነዚህን ለያይተው ይያዙ።

![ባለ 3-ንብርብር የመቋቋም ሞዴል](../diagrams/exported/resilience-3layers.svg)

> ምንጭ፦ [diagrams/resilience-3layers.mmd](../diagrams/resilience-3layers.mmd)

## 1. የአቅራቢ ሰርኪት መቋረጫ

**ወሰን፦** ሙሉው አቅራቢ (ለምሳሌ፣ `glm`፣ `openai`፣ `anthropic`)።

**ዓላማ፦** በላይኛው ዥረት/አገልግሎት ደረጃ በተደጋጋሚ ውድቀት ለሚያጋጥመው አቅራቢ ትራፊክ መላክን ማቆም።

**አተገባበር፦**

- ዋና ክፍል፦ `src/shared/utils/circuitBreaker.ts`
- ማገናኘት፦ `src/sse/handlers/chatHelpers.ts`፣ `src/sse/handlers/chat.ts`
- የሁኔታ API፦ `GET /api/monitoring/health`
- የዳግም ማስጀመሪያ API፦ `POST /api/resilience/reset`
- መጠቅለያዎች፦ `open-sse/services/accountFallback.ts`
- የውሂብ ጎታ ሰንጠረዥ፦ `domain_circuit_breakers`

**ሁኔታዎች፦**

- `CLOSED` — መደበኛ ትራፊክ ተፈቅዷል
- `DEGRADED` — ትራፊክ አሁንም ተፈቅዷል፣ ነገር ግን የጨመሩ የአቅራቢ ውድቀቶች ክትትል ይደረግባቸዋል
- `OPEN` — አቅራቢው ለጊዜው ታግዷል፤ የጥምር ማዞሪያው ይዘለዋል
- `HALF_OPEN` — የዳግም ማስጀመሪያ የጊዜ ገደቡ አልፏል፤ የመፈተሻ ጥያቄ ተፈቅዷል

**ሊዋቀሩ የሚችሉ ነባሪዎች (`open-sse/config/constants.ts`፣ በDashboard → Settings → Resilience ላይ የሚታዩ)፦**

| ክፍል     | ወደ የተዳከመ ሁኔታ የሚገባው | የሚከፈተው   | የዳግም ማስጀመሪያ የጊዜ ገደብ |
| ------- | ------------------ | -------- | ------------------- |
| OAuth   | 5 ውድቀቶች            | 8 ውድቀቶች  | 60s                 |
| API ቁልፍ | 7 ውድቀቶች            | 12 ውድቀቶች | 30s                 |
| አካባቢያዊ  | የሚሰላ               | 2 ውድቀቶች  | 15s                 |

`degradationThreshold` አንድ አቅራቢ መቼ ወደ `DEGRADED` እንደሚገባ ይቆጣጠራል፤ `failureThreshold` ደግሞ መቼ እንደሚከፈትና እንደሚዘለል ይቆጣጠራል። የአካባቢያዊ አቅራቢ መገለጫዎች እስካሁን በResilience ቅንብሮች ገጽ ላይ አይታዩም።

**የማቋረጫ ኮዶች፦** የአቅራቢ ደረጃ ሁኔታዎችን `[408, 500, 502, 503, 504]` ብቻ። በመለያ ደረጃ ለሚከሰቱ ስህተቶች (አብዛኞቹ 401/403/429 — እነዚህ በማቀዝቀዣ ጊዜ ወይም በመቆለፍ ሥር ይካተታሉ) ማቋረጫውን አያስነሱ።

**በፍላጎት ጊዜ መልሶ ማግኘት፦** `OPEN` ሲያበቃ፣ `getStatus()`፣ `canExecute()`፣ `getRetryAfterMs()` ሁኔታውን ወደ `HALF_OPEN` ያድሳሉ። የበስተጀርባ ሰዓት ቆጣሪ አያስፈልግም።

---

### በምርጫ የሚነቃ ዓለም አቀፍ የአቅራቢ ማቀዝቀዣ ጊዜ (የጊዜ መስኮት መግቢያ)

አራተኛው፣ **በምርጫ የሚነቃ** ንብርብር (`PROVIDER_COOLDOWN_ENABLED`፣ በነባሪ **የጠፋ**) ውድቀት
ያጋጠማቸውን አቅራቢዎች በጥያቄዎች መካከል የሚቆይ ማህደረ ትውስታ በ
`open-sse/services/providerCooldownTracker.ts` ውስጥ ይይዛል፤ ይህም በጥምር ዒላማ
ማግኛ ሂደት ይመከርበታል፣ ስለዚህ ተከታታይ የጥምር ጥያቄዎች በቅርቡ
ውድቀት ያጋጠመውን አቅራቢ እንደገና ማሰስ ያቆማሉ። የአቅራቢ ደረጃ ግቤቶች የ`PROVIDER_PROFILES` የጊዜ መስኮት መግቢያን ያከብራሉ፦

| መገለጫ    | የሚነሳው ከ (`providerFailureThreshold`) በኋላ | በ (`providerFailureWindowMs`) ውስጥ | ለ (`providerCooldownMs`) ይቀዘቅዛል |
| ------- | ---------------------------------------: | --------------------------------: | ------------------------------: |
| OAuth   |                                     `10` |                           `15min` |                          `5min` |
| API ቁልፍ |                                     `15` |                           `30min` |                         `10min` |

ከገደቡ በታች አቅራቢው በማቀዝቀዝ ላይ እንዳለ **አይቆጠርም**፤ ስኬታማ ምላሽ
የጊዜ መስኮቱን ያጸዳል። የግንኙነት ደረጃ ግቤቶች (`provider:connectionId`) በምትኩ
እየጨመረ የሚሄደውን `minRetryCooldownMs → maxRetryCooldownMs` የድጋሚ ሙከራ መዘግየት ይጠብቃሉ። ማሻሻያዎች፦
`OMNIROUTE_PROVIDER_BREAKER_{OAUTH,API_KEY}_{FAILURE_THRESHOLD,FAILURE_WINDOW_MS,COOLDOWN_MS}`።
የድግግሞሽ ስህተት መከላከያ፦ `tests/unit/provider-cooldown-window-gate.test.ts`።

## 2. የግንኙነት ማቀዝቀዣ ጊዜ

**ወሰን:** አንድ የአቅራቢ ግንኙነት/መለያ/ቁልፍ።

**ዓላማ:** ለተመሳሳይ አቅራቢ ያሉ ሌሎች ግንኙነቶች አገልግሎት መስጠታቸውን ሲቀጥሉ አንድ ችግር ያለበትን ቁልፍ መዝለል።

**አተገባበር:**

- እንደማይገኝ ምልክት ማድረግ፦ `src/sse/services/auth.ts::markAccountUnavailable()`
- ምርጫ፦ በተመሳሳይ ፋይል ውስጥ `getProviderCredentials*`
- የማቀዝቀዣ ጊዜ ስሌት፦ `open-sse/services/accountFallback.ts::checkFallbackError()`
- ቅንብሮች፦ `src/lib/resilience/settings.ts`

**በእያንዳንዱ ግንኙነት ያሉ መስኮች:**

- `rateLimitedUntil` — የማቀዝቀዣ ጊዜው እስከሚያበቃበት ድረስ ያለ የጊዜ ማህተም
- `testStatus: "unavailable"`
- `lastError`, `lastErrorType`, `errorCode`
- `backoffLevel` — የኤክስፖነንሻል መዘግየት ቆጣሪ

**ነባሪ የማቀዝቀዣ ጊዜዎች:**

- የOAuth መሠረት፦ 5s
- የAPI ቁልፍ መሠረት፦ 3s
- የAPI ቁልፍ 429፦ ከላይኛው አገልግሎት የሚመጡ `Retry-After`/ዳግም ማስጀመሪያ ራስጌዎችን/ሊተነተን የሚችል የዳግም ማስጀመሪያ ጽሑፍን ይመርጣል
- መዘግየት፦ `baseCooldownMs * 2 ** failureIndex`

**የተመሳሳይ ጊዜ የጥያቄ መጉረፍ መከላከያ:** በአንድ ጊዜ የሚከሰቱ ውድቀቶች የማቀዝቀዣ ጊዜውን ከመጠን በላይ እንዳያራዝሙ ወይም `backoffLevel`ን ሁለት ጊዜ እንዳይጨምሩ ይከላከላል።

**በተመሳሳይ ጊዜ ጥያቄዎች ገደብ ምክንያት የሚከሰቱ 429ዎች የመዘግየት ደረጃውን አይወጡም።** አካሉ የተመሳሳይ ጊዜ ጥያቄዎች ገደብን ("too many concurrent requests", "concurrency limit", "parallel request
limit", GLM `并发数过高`) የሚገልጽ `429` መለያው ጤናማ ነገር ግን ሥራ የበዛበት መሆኑን ያመለክታል።
`checkFallbackError()` `concurrency_limited` የሚል ምክንያት ይመልሳል፦ አሁን ወደ ቀጣዩ
ግንኙነት ይሸጋገሩ፣ ይህንን ለቋሚ `CONCURRENCY_LIMIT_COOLDOWN_MS` (1s) ወይም ከላይኛው
አገልግሎት በተሰጠው የዳግም ሙከራ ፍንጭ መሠረት ያቀዝቅዙ፣ `backoffLevel`ን ሳይቀይሩ ያቆዩ እና `skipProviderBreaker`ን ያዘጋጁ።
ግልጽ የኮታ አካል አሁንም ቅድሚያ ያገኛል፤ ስለዚህ የኮታ ጥለትንም የሚያሟላ አካል እንደ ኮታ
ውሳኔ ይቆያል። ማወቂያ፦ `src/shared/utils/classify429.ts` ውስጥ `looksLikeConcurrencyLimit()`፤
ውሳኔ፦ `open-sse/services/accountFallback/concurrencyLimit429.ts`። `classify429()` (የወረዳ ቆራጩ `FailureKind`)
አልተለወጠም፣ ለእነዚህ አካላትም አሁንም `rate_limit`ን ያነባል።

**የዥረት ይዘት መቆም መለያውን አያቀዘቅዝም።** የይዘት መቆም ተቆጣጣሪው
(`open-sse/utils/streamHandler.ts`) በተገቢው ጊዜ ምንም የሞዴል ውጤት ባልላከ ዥረት ላይ
ተስፋ ሲቆርጥ፣ `markAccountUnavailable()` ስህተቱን በግንኙነቱ ላይ ይመዘግባል፣ ነገር ግን
ምንም የማቀዝቀዣ ጊዜ አያዘጋጅም፦ መቆሙ የዚያ ጥያቄ ችግር ነው፣ ብዙውን ጊዜም እስካሁን
ውጤት የሌለው ረጅም የማመዛዘን ዙር ነው። ኦፕሬተሮች `resilienceSettings.streamStallCooldown.enabled`
(ነባሪ `false`)ን በመጠቀም ባህሪውን እንደገና ማንቃት ይችላሉ።

**የማመዛዘን ፍሬሞች የይዘት መቆም የጊዜ በጀትን እንደገና ያስጀምራሉ።** የማመዛዘን ሞዴል የመጀመሪያውን
የሚታይ ቶከን ከማውጣቱ በፊት ለደቂቃዎች ሊያስብ ይችላል፦ Claude የማሰብ ጽሑፋቸው ባዶ ሊሆን
የሚችል `thinking_delta` ፍሬሞችን በዥረት ይልካል፣ Responses API ደግሞ አንድ የማመዛዘን ንጥልን ከሌላው
በኋላ በዥረት ይልካል። `isReasoningProgressFrame()` (`open-sse/utils/streamReadiness.ts`) እነዚህን
ፍሬሞች ይለያል፣ ተቆጣጣሪውም ዙሩን ከመሰረዝ ይልቅ በእያንዳንዳቸው ላይ የጊዜ በጀቱን እንደገና ያስጀምራል።
እነሱ አሁንም የሞዴል ውጤት አይደሉም፤ ስለዚህ በማመዛዘን ብቻ የሚያበቃ ዙር አሁንም ባዶ እንደሆነ
ሪፖርት ይደረጋል፣ ማመዛዘንን አቁሞ የልብ ምት ምልክቶችን ብቻ የሚልክ ዙርም አሁንም
ተቆጣጣሪውን ያስነሳል።

ባዶ ያልሆነ ፊርማ ያላቸው የKiro ሁለትዮሽ `reasoningContentEvent` ፍሬሞች ይህንን
የማመዛዘን እንቅስቃሴ በአስፈጻሚው ውስጥ እንደ ባዶ `reasoning_content` ለውጥ ያስቀጥላሉ። ፊርማው
ወደፊት አይተላለፍም። ሜታዳታ፣ ያልተሟሉ ፍሬሞች እና ባዶ ፊርማዎች የይዘት ጊዜ በጀቱን
እንደገና አያስጀምሩም፤ ራሱን የቻለው የንቁ ዥረት ጊዜ ማብቂያ እና የደንበኛ ስረዛ አሁንም
ተግባራዊ ናቸው (`open-sse/executors/kiro/reasoning.ts`)።

**የመጨረሻ ሁኔታዎች (የማቀዝቀዣ ጊዜዎች አይደሉም):**

- `banned` — በታገደ ቁልፍ ቃል/የመለያ እገዳ ማወቂያ (ይመልከቱ [BAN_DETECTION](../security/BAN_DETECTION.md))፣ እንዲሁም ከላይኛው አገልግሎት በሚመጡ ሦስት ተከታታይ የእያንዳንዱ ጥያቄ እምቢታዎች (`request_rejected`፣ ለምሳሌ Anthropic OAuth 403 "Request not allowed" — `open-sse/services/requestRejectedStreak.ts`) ይዘጋጃል፤ አንድ እምቢታ ግንኙነቱን ለጊዜው ብቻ ያቀዘቅዛል
- `expired` (ከተወሰኑ የዳግም ሙከራዎች በኋላ ወደ መጨረሻ ሁኔታ ይሸጋገራል — ከኤክስፖነንሻል መዘግየት ጋር `EXPIRED_RETRY_MAX = 3` — ስለዚህ ጊዜያዊ የOAuth ስህተቶች መለያው በቋሚነት ከመሰናከሉ በፊት ራሳቸውን ማስተካከል ይችላሉ)
- `credits_exhausted`

እነዚህ ማረጋገጫዎቹ እስኪቀየሩ ወይም ኦፕሬተር ዳግም እስኪያስጀምራቸው ድረስ ይቆያሉ። የመጨረሻ ሁኔታዎችን በጊዜያዊ የማቀዝቀዣ ሁኔታ አይተኩ።

**ሰነፍ መልሶ ማግኛ:** `rateLimitedUntil` ካለፈ በኋላ ግንኙነቱ እንደገና ለምርጫ ብቁ ይሆናል። በተሳካ ሁኔታ ጥቅም ላይ ሲውል `clearAccountError()` ሁሉንም የስህተት መስኮች ያጸዳል።

### የClaude OAuth አጠቃቀም ገደብ፦ ዝቅተኛ ቅድሚያ ያለው መስመር + የክፍለ ጊዜ ገደብ ዳግም ማስጀመር

**ወሰን:** አንድ የClaude ምዝገባ (OAuth) ግንኙነት። ሁለቱም ባህሪያት **በእያንዳንዱ
ግንኙነት በፈቃደኝነት የሚነቁ** ናቸው (ግንኙነት አርትዕ → Claude ክፍል → በ
`providerSpecificData` ውስጥ `lowPriorityMode` / `autoLimitReset`፣ ሁለቱም በነባሪ ጠፍተዋል) እና የClaude Code
`/low-priority` እና `/limit-reset` ትዕዛዞችን ያንጸባርቃሉ (የሽቦ ውል ከClaude Code 2.1.263 የተወሰደ)።

**አተገባበር:**

- የሁኔታ ማሽን + የምላሽ ምደባ፦ `open-sse/services/claudeLowPriority.ts`
- የዳግም ማስጀመር ሁኔታ/የይገባኛል ጥያቄ ደንበኛ፦ `open-sse/services/claudeLimitReset.ts`
- የአስፈጻሚ ማያያዣ (ራስጌ ማስገባት + በተመሳሳይ መለያ ዳግም መሞከር)፦ `open-sse/executors/base.ts::execute()`
- የፈቃደኝነት ማንቃት ሁኔታ ማቆያ፦ `src/lib/providers/requestDefaults.ts::normalizeProviderSpecificData()`

**ማስነሻ:** የ5 ሰዓት አጠቃቀም ገደብ — ራስጌዎቹ
`anthropic-ratelimit-unified-status: rejected`ን እና፣ መለያው ብቁ ሲሆን፣
`anthropic-ratelimit-unified-slow-offer: treatment`ን የያዙበት `429`። ከመጀመሪያው የገደብ
429 በፊት ምንም ነገር አይላክም፤ unified ራስጌዎች የሌሉት ድንገተኛ ብዛት ያለው 429 በመደበኛው የማቀዝቀዣ መንገድ ያልፋል።

**ዝቅተኛ ቅድሚያ ያለው መስመር** (`lowPriorityMode`):

- በ wall 429 ላይ executor ቅናሹን ይቀበላል እና ወዲያውኑ **ተመሳሳዩን**
  መለያ በ `anthropic-usage-limit: slow` እንደገና ይሞክራል፤ የታወጀው
  `anthropic-ratelimit-unified-reset` (+60s የእፎይታ ጊዜ) እስኪደርስ ድረስ lane ንቁ ሆኖ ይቆያል፣ እና በዚያ የጊዜ መስኮት ውስጥ ያለ እያንዳንዱ ጥያቄ
  header-ውን ይይዛል። የተጠለፈው 429 ፈጽሞ `handleChatCore` ላይ አይደርስም፣ ስለዚህ connection-ው
  ወደ cooldown **አይገባም** እና በሌላ አይተካም።
- በኋለኞቹ ምላሾች ላይ `anthropic-ratelimit-unified-slow-status`፦ `active` / `not_needed`
  lane-ውን ያቆያሉ፤ `slot_busy` (429) ወይም `529` የserver-ውን
  `anthropic-ratelimit-unified-slow-retry-after` (ነባሪ 20s፣ ከ5–600s የተገደበ፣ ±30% jitter)
  ጠብቀው እንደገና ይሞክራሉ፣ ይህም በ `anthropic-ratelimit-unified-slow-max-wait` (ነባሪ 20 min፣
  ከ1 min–6 h የተገደበ) የተወሰነ ነው — ከዚያ ካለፈ lane-ው ያበቃል እና የ10 ደቂቃ cool-off
  እንደገና መቀበልን ያግዳል። የመጠበቂያው ጊዜ በተጨማሪም ከጥያቄው የራሱ
  upstream-start timeout (`resolveFetchStartTimeout`፣ በነባሪ 10 min) በቀረው ጊዜ ላይ የ5 s ህዳግን
  በመቀነስ ይገደባል፦ ያለዚያ ገደብ የ20 ደቂቃው ነባሪ max-wait ከጥያቄው የሕይወት ጊዜ
  ይበልጥ ነበር፣ እና sleep-ው በመጠባበቅ መሃል ይቋረጥ ነበር፣ ይህም ለስላሳው
  `max_wait` ማብቂያ + cool-off ፈንታ `TimeoutError` እንዲታይ ያደርጋል።
- `weekly_limit` / `budget_exhausted` / `off` / `ineligible`፣ የ5h-window rollover፣ ወይም
  `ineligible` + `anthropic-ratelimit-unified-overage-in-use: true` (የሚከፈልበት overage አሁን wall-ውን ስለሚሸፍን፣ በማንኛውም status ላይ እንደ
  `extra_usage` ያጠናቅቀዋል) lane-ውን ያበቃሉ፤ ከዚያም
  ምላሹ ወደ መደበኛው cooldown መንገድ ይፈሳል። `budget_exhausted` የታወጀው budget reset
  (≤ 8 days) እስኪደርስ ድረስ ይታወሳል።
- የwall ማረጋገጫው executor-ው በ400 የሚነሱ የራሱን intra-attempt retries (context
  editing፣ thinking/effort clamps፣ param auto-learn) ካከናወነ በኋላ ይሰራል፣ ስለዚህ wall 429 ከእነዚያ retries በአንዱ ላይ ብቻ ቢታይም
  ወደ cooldown መንገድ ከመድረስ ይልቅ አሁንም ይጠለፋል።
- State በእያንዳንዱ connection በin-memory ይቀመጣል (restart እንደገና ለመቀበል አንድ ተጨማሪ wall 429 ያስከፍላል)።

**የsession-limit reset** (`autoLimitReset`፣ ሁለቱም ሲበሩ ከlane-ው በፊት ይሞከራል)፦

- `GET https://api.anthropic.com/api/oauth/usage?at_wall=1&skip_spend=1` → `juniper_tide`
  block፤ `arm: "reset"` እና `available: true` ሲሆኑ፣
  `POST https://api.anthropic.com/api/organizations/{orgUUID}/reset_rate_limits` ከ
  `{ "program": "juniper_tide" }` ጋር (የorganization UUID ከ
  `providerSpecificData.organizationUUID`፣ bootstrap fallback)።
- `result: reset|not_limited` → ጥያቄው በሙሉ ፍጥነት እንደገና ይሞከራል (slow header የለም)።
  `already_used` / `not_offered` `next_available_at`-ን በማስታወሻ ይይዛሉ (ነባሪ አንድ ሳምንት)፤ ማንኛውም
  አለመሳካት ለ15 ደቂቃ ወደኋላ ያፈገፍጋል። reset-ው በሳምንት አንድ ጊዜ ሲሆን አሁንም በweekly limit ውስጥ ይቆጠራል።

የRegression guards፦ `tests/unit/claude-low-priority-mode.test.ts`፣
`tests/unit/claude-limit-reset.test.ts`፣ `tests/unit/claude-low-priority-executor.test.ts`።

### የSession affinity (#7274)

**ወሰን፦** አንድ client session (`X-Session-Id` / `x-codex-session-id` / `x-omniroute-session` header) ለ**ማንኛውም** provider ከአንድ connection ጋር ይሰካል።

**ዓላማ፦** multi-turn agent-ን (Claude Code፣ aider፣ custom agents) በተለያዩ ጥያቄዎች መካከል በተመሳሳይ account ላይ ማቆየት፣ ይህም የcross-account context መጥፋትን እና በper-account session state ባላቸው providers ላይ የሚደጋገሙ cold-start 429s-ን ይቀንሳል።

**አተገባበር፦**

- የTTL resolution፦ `src/sse/services/sessionAffinityPin.ts::resolveSessionAffinityTtlMs()`
- የPin selection/creation፦ `src/sse/services/sessionAffinityPin.ts::selectSessionAffinityConnection()`
- የHeader extraction (አጠቃላይ፣ ማንኛውም provider)፦ `src/sse/services/auth.ts::extractSessionAffinityKey()`
- የተከማቸ pin table፦ `sessionAccountAffinity` (`src/lib/db/sessionAccountAffinity.ts`)
- Setting፦ `sessionAffinityTtlMs` (አጠቃላይ TTL በms፣ `0` ያሰናክላል) — `src/lib/db/settings.ts`። ከCodex-ብቻ `codexSessionAffinityTtlMs` በmigration `124_generic_session_affinity_ttl.sql` እንደገና ተሰይሟል፣ ይህም ከዚህ በፊት የተዋቀረ ማንኛውንም Codex TTL እንደ አዲሱ ነባሪ ያስተላልፋል።

ከ#7274 በፊት፣ `resolveSessionAffinityTtlMs()` ከ`codex` በስተቀር ለሁሉም providers ወዲያውኑ `0` በመመለስ ይወጣ ነበር፣ ስለዚህ የpinning mechanism እና header extraction ቀድሞውኑ provider-agnostic ቢሆኑም TTL setting-ው (እና session headers-ዎቹ) በሌላ ቦታ ምንም ውጤት አልነበራቸውም። ማስተካከያው ያንን early-return አስወግዷል፤ TTL-ው አሁን በአጠቃላይ ከ`0` በላይ ከተቀናበረ በኋላ ለእያንዳንዱ provider በእኩል ይተገበራል።

ሦስቱ የsession-affinity headers በፍጹም ወደ upstream አይተላለፉም — executors የclient headers-ን በቀጥታ ከማሳለፍ ይልቅ የራሳቸውን upstream headers ከባዶ ይገነባሉ፣ ስለዚህ ይህ የውስጥ correlation id ብቻ ሆኖ ይቆያል።

### ልዩ የmanaged session connection leases

**ወሰን፦** አንድ ንቁ managed HTTP client/session አንድ ብቁ OmniRoute connection ይይዛል።

**ዓላማ፦** በጥያቄዎች መካከል ጥብቅ የrouting
fence ለሚያስፈልጋቸው clients ዘላቂ ልዩ የconnection ownership ማቅረብ። ይህ ለስላሳ የcontinuity preference ከሆነው session affinity የተለየ ነው፦
exclusive lease የlifecycle state-ን በSQLite ውስጥ ያቆያል፣ ዓለም አቀፍ የactive-owner እና
active-connection uniqueness-ን ያስገድዳል፣ እንዲሁም ከprovider dispatch በፊት stale generation-ን ውድቅ ያደርጋል።

ባህሪው ለእያንዳንዱ API key በምርጫ የሚነቃ ነው። managed key `lease:exclusive` scope እና
ግልጽ የሆነ ባዶ ያልሆነ `allowedConnections` list ሊኖረው ይገባል። ማንኛውም HTTP client lifecycle endpoint-ን መጠቀም ይችላል፤
የclient name፣ user-agent፣ provider፣ OAuth method፣ ወይም model አያስፈልግም። lease-ው connection እንጂ
model-ን አይይዝም፣ ስለዚህ connection-ው በመደበኛነት
ብቁ ሆኖ እስከቆየ ድረስ የmodel ለውጥ binding-ውን ያቆያል። መደበኛ የmodel፣ quota፣ health፣ cooldown፣ እና allowlist ደንቦች አሁንም
ዋና ውሳኔ ሰጪዎች ሆነው ይቆያሉ፣ እና ተመሳሳዩን generation ወደ ሌላ ነጻና ብቁ connection ሊያሸጋግሩት ይችላሉ።

የሕይወት ዑደቱ JSON ድርጊቶች `acquire`፣ `renew` እና `release` ያሉት `POST /api/v1/session-leases` ነው።
የሚተዳደሩ የኢንፈረንስ ጥያቄዎች ግልጽ ያልሆነውን `X-OmniRoute-Lease-Owner` እሴት እና ትክክለኛውን
`X-OmniRoute-Lease-Generation` ያቀርባሉ። ባለቤቱ `vlo_`ን ተከትለው 43 base64url ቁምፊዎችን ይጠቀማል፤ የእሱ
SHA-256 hash ብቻ ይከማቻል። እያንዳንዱ የመጨረሻ የመላኪያ fence የተረጋገጠውን API key ID እና
ንቁውን connection IDም ያስተሳስራል። የlease መቆጣጠሪያ headers ከlogs፣ ከተቀመጡ የጥያቄ snapshots እና
ከupstream executor headers ይወገዳሉ።

መደበኛ routing ብቁ የሆኑ managed candidates ካሉት፣ ነገር ግን እያንዳንዱ ነፃ candidate በሌላ
ንቁ lease ከተያዘ፣ OmniRoute HTTP `429`፣ lease-capacity-unavailable code፣
waiting-for-capacity state እና ከመጀመሪያው ተዛማጅ expiry የተወሰደ ገደብ ያለው `Retry-After` ይመልሳል።
መደበኛው ባዶ eligibility የlease contention አይደለም፣ እና ነባሩን የrouting error semantics ይጠብቃል።

ተዛማጅ ስልቶች እንደተለያዩ ይቆያሉ፦

- የOAuth session occupancy ለOAuth accounts በprocess ውስጥ ብቻ የሚሠራ soft distribution ነው።
- የAccount semaphores የrequest-concurrency permits ይሰጣሉ፣ እና አንድ request ሲጠናቀቅ ያበቃሉ።
- ብቸኛ managed session leases የgeneration fence ያላቸው ዘላቂ የlifecycle ownership ናቸው።

---

## 3. የሞዴል መቆለፍ

**ወሰን:** አቅራቢ + ግንኙነት + ሞዴል ጥምረት።

**ቁልፍ ወሰን በሁኔታ ኮድ:** የውድቀቱ ሁኔታ ኮድ መቆለፊያው በየትኛው ቁልፍ ላይ እንደሚጻፍ
ይወስናል (`resolveLockoutScope()` በ `open-sse/services/accountFallback/exactModelLock.ts` ውስጥ):

- `429` / `403` / `402` — የኮታ ወይም የመብት ምልክት — **የኮታ ቤተሰቡን** ይቆልፋሉ፦
  ለ codex ሙሉውን `codex` / `spark` ወሰን (በግንኙነቱ ውስጥ ያሉ ሁሉንም `gpt-5*` ሞዴሎች)፣
  ለሌሎች አቅራቢዎች `getQuotaScopedModelForProvider()`።
- `404` መሠረታዊውን ሞዴል ይቆልፋል (`getModelLockKey()` `not_found`ን ያጠባል)።
- ማንኛውም ሌላ ሁኔታ ኮድ — የ`5xx` ማጓጓዣ/አገልጋይ ውድቀቶች እና ከጥራት ማረጋገጫ
  በOmniRoute ራሱ የተፈጠረው `502` — **ትክክለኛውን**
  የአቅራቢ/ግንኙነት/ሞዴል ጥምረት ብቻ ይቆልፋል። በአንድ ሞዴል ላይ ያለ መጥፎ ዥረት
  ስለመለያው ኮታ ማስረጃ አይደለም፤ ከዚህ ደንብ በፊት በ
  `codex/gpt-5.6-luna` ላይ አንድ ባዶ ምላሽ የዚያን ግንኙነት እያንዳንዱን `gpt-5*` ሞዴል
  ከማዘዋወሪያ ለ2–30 ደቂቃ (እየጨመረ) ያስወግድ ነበር፣ ኮታው ግን አልተነካም።
- ደዋዩ በግልጽ ያስቀመጠው `scope` አማራጭ ሁልጊዜ ቅድሚያ ይኖረዋል (Antigravity `"exact"`ን ያስተላልፋል)።

**ዓላማ:** አንድ ሞዴል ብቻ በማይገኝበት ወይም በኮታ በተገደበበት ጊዜ ሙሉውን ግንኙነት ከማሰናከል መቆጠብ።

**ምሳሌዎች:**

- ለእያንዳንዱ ሞዴል ኮታ የሚያደርጉ አቅራቢዎች `429` ሲመልሱ
- የአካባቢ አቅራቢዎች ላልተገኘ አንድ ሞዴል `404` ሲመልሱ
- ለአቅራቢው የተለዩ የሁነታ/ሞዴል ፈቃድ ውድቀቶች (ለምሳሌ፣ Grok ሁነታዎች)

**አተገባበር:** `open-sse/services/accountFallback.ts` — `lockModel()`፣ `clearModelLock()`፣ `getAllModelLockouts()`።

### የሞዴል ማቀዝቀዣዎች ዳሽቦርድ (v3.8.0)

UI: ቅንብሮች → የሞዴል ማቀዝቀዣዎች (`src/app/(dashboard)/dashboard/settings/components/ModelCooldownsCard.tsx`)

ንቁ መቆለፊያዎችን ከሚከተሉት ጋር ይዘረዝራል፦ አቅራቢ፣ ግንኙነት፣ ሞዴል፣ ምክንያት፣ expiresAt። ኦፕሬተሮች ከካርዱ ላይ ሞዴልን በእጅ እንደገና ማንቃት ይችላሉ።

**REST API:**

- `GET /api/resilience/model-cooldowns` — ንቁ መቆለፊያዎችን መዘርዘር
- `DELETE /api/resilience/model-cooldowns` — በእጅ እንደገና ማንቃት። የጥያቄ አካል፦ `{provider, connection, model}`። ማረጋገጫ፦ አስተዳደር።

### የማቀዝቀዣ አስተዳዳሪ

UI: ክትትል → የማቀዝቀዣ አስተዳዳሪ (`src/app/(dashboard)/dashboard/resilience/cooldowns/`)።

እያንዳንዱን የአቅራቢ ገጽ ከመክፈት ይልቅ፣ በጊዜያዊ ምክንያት ከማዘዋወሪያ የወጣውን
እያንዳንዱን ግንኙነት የሚያሳይ አንድ ገጽ። የግንኙነት ማቀዝቀዣዎችን፣ የሞዴል መቆለፊያዎችን እና ተርሚናል
ሁኔታዎችን ይዘረዝራል፤ በእያንዳንዱ ግንኙነት፣ ለተመረጡት ወይም ለአንድ አቅራቢ ግንኙነቶች በሙሉ
ያጸዳቸዋል፤ እንዲሁም በጣም የሚስተካከሉትን የማቀዝቀዣ ደንቦች ያርታል፦ `streamStallCooldown.enabled` እና የOAuth / API-key
`connectionCooldown` መሠረታዊ ማቀዝቀዣና ከፍተኛውን የኋላ-መመለስ ደረጃዎች (በ
`PATCH /api/resilience` በኩል ይቀመጣሉ)። ተርሚናል ሁኔታዎች (`banned`፣ `expired`፣ `credits_exhausted`) ይዘረዘራሉ
ነገር ግን እዚህ ፈጽሞ አይጸዱም።

**REST API** (`src/lib/resilience/cooldownManager.ts`፣ ማረጋገጫ፦ አስተዳደር):

- `GET /api/resilience/cooldowns[?provider=]` — ሁኔታ፣ የቀረው የማቀዝቀዣ ጊዜ፣
  የኋላ-መመለስ ደረጃ፣ የመጨረሻው ስህተት ዓይነት እና የሞዴል መቆለፊያዎች ያሏቸው ግንኙነቶች (የመግቢያ ማስረጃዎች ሳይኖሩ)
- `POST /api/resilience/cooldowns` — የጥያቄ አካል `{connectionIds: string[]}` ወይም
  `{all: true, provider?}`፤ `{cleared, unchanged, skippedTerminal, lockoutsCleared}`ን ይመልሳል

### የመቆለፊያ ቅንብሮች UI + በስኬት-መቀነስ ማገገሚያ (v3.8.23)

የሞዴል መቆለፍ ሁልጊዜ ከሚሠራ በኮድ ውስጥ ቋሚ ተደርጎ ከተቀመጠ ባህሪ ወደ ሙሉ በሙሉ ሊዋቀር የሚችል፣
በፈቃድ የሚነቃ ባህሪ ተቀይሯል፤ የራሱ የቅንብሮች ካርድ እና ራሱን የሚጠግን የማገገሚያ መንገድም አለው።

**የቅንብሮች ካርድ:** ቅንብሮች → የሞዴል መቆለፍ
(`src/app/(dashboard)/dashboard/settings/components/ModelLockoutCard.tsx`)።
ይህ ከላይ ካለው ለንባብ ብቻ የሆነ `ModelCooldownsCard` (ንቁ መቆለፊያዎችን ብቻ
_ከሚዘረዝረው_) **የተለየ** ነው — አዲሱ ካርድ _መለኪያዎቹን ያዋቅራል_። ነባሪዎቹ
በ `DEFAULT_MODEL_LOCKOUT_SETTINGS`
(`src/lib/resilience/modelLockoutSettings.ts`) ውስጥ ይገኛሉ፦

| ቅንብር                    | ነባሪ                              | ትርጉም                                              |
| ----------------------- | -------------------------------- | ------------------------------------------------- |
| `enabled`               | `false`                          | ዋና መቀያየሪያ — የሞዴል መቆለፍ **በነባሪ ጠፍቷል**።              |
| `errorCodes`            | `[403, 404, 429, 502, 503, 504]` | እንደ ሞዴል-ወሰን ውድቀት የሚቆጠሩ የላይኛው ምንጭ ሁኔታ ኮዶች።         |
| `baseCooldownMs`        | `120_000` (120 ሰ)                | ለመጀመሪያው ውድቀት የመነሻ መቆለፊያ ቆይታ።                      |
| `maxCooldownMs`         | `1_800_000` (30 ደቂቃ)             | በጨመረው የማቀዝቀዣ ጊዜ ላይ ያለው ከፍተኛ ገደብ።                  |
| `maxBackoffSteps`       | `10`                             | ከፍተኛው የኤክስፖነንሻል ኋላ-መመለስ ማሳደጊያ ደረጃዎች።              |
| `useExponentialBackoff` | `true`                           | ተደጋጋሚ ውድቀቶች የማቀዝቀዣ ጊዜውን በኤክስፖነንሻል መልኩ ያሳድጉ እንደሆነ። |

ቅንብሮቹ በመደበኛው የቅንብሮች ማከማቻ በኩል ይቀመጣሉ፣ እንዲሁም በ
የጽናት ቅንብሮች ንድፈ መዋቅር ይረጋገጣሉ፤ ካርዱ `baseCooldownMs`/`maxCooldownMs`ን
(`maxCooldownMs ≥ baseCooldownMs` እንዲሆን) እና `maxBackoffSteps`ን በተፈቀደው ክልል ውስጥ ይገድባል።

**በስኬት-መቀነስ ማገገሚያ:** ማገገሚያው የሰዓት ቆጣሪው በማብቃቱ ላይ ብቻ **አይመሠረትም**። ጤናማ
ምላሽ የሞዴሉን የውድቀት ብዛት ቀስ በቀስ ይቀንሳል፤ ስለዚህ በጊዜ መስኮቱ
መካከል ያገገመ ሞዴል የጊዜ ገደቡ ከማብቃቱ በፊት መጨመሩን ያቆማል (እና ይጸዳል)። ስኬታማ
የጥምረት ዒላማ ሲኖር፣ `open-sse/services/combo.ts` `decayModelFailureCount()`ን
(`open-sse/services/accountFallback.ts`) ይጠራል፤ ይህም የተከማቸውን
`failureCount` **በግማሽ ይቀንሳል** (`Math.floor(failureCount / 2)`)፤ `0` ሲደርስ የመቆለፊያ
መዝገቡ ሙሉ በሙሉ ይሰረዛል። ተጓዳኙ `recordModelLockoutFailure()`
በማሳደጊያ ጊዜ መስኮቱ ውስጥ ውድቀቶች ሲከሰቱ ብዛቱን ይጨምራል (የማቀዝቀዣ ጊዜውንም ያሳድጋል)።
ይህ በስኬት-መቀነስ ማገገሚያ ከቀላል የጊዜ ገደብ ማብቃት በተጨማሪ ነው —
ከሁለቱ መንገዶች ማንኛውም ሞዴሉን እንደገና ሊያነቃ ይችላል።

**ሁኔታ:** መቆለፊያዎቹ **በማህደረ ትውስታ ውስጥ** ይያዛሉ (በእያንዳንዱ ሂደት `Map`ዎች፤
`ModelLockoutEntry` በ `provider:connectionId:model` የተቀየሰ፣ ትክክለኛ-ወሰን መቆለፊያዎች ደግሞ በ
`provider:connectionId:exact:model` የተቀየሱ ናቸው)፣ ወደ
DB አይቀመጡም — ዳግም ሲጀመር ይጠፋሉ። _ቅንብሮቹ_ ይቀመጣሉ፤ ንቁው
የመቆለፊያ _ሁኔታ_ ጊዜያዊ ነው።

---

## 4. የQuota-Share በአንድ ጊዜ ማስኬድ ቁጥጥር (v3.8.36)

የደንበኝነት ምዝገባ መለያዎች (GLM፣ MiniMax፣ ወዘተ) ብዙውን ጊዜ ~1–3 በአንድ ጊዜ
የሚላኩ ጥያቄዎችን ብቻ ይቀበላሉ፤ ይህን ማለፍ 429ዎችን እና የcooldown ጊዜዎችን ያስነሳል። ይህ
በተለይ በ**quota-share** (`qtSd/…`) combos ስር ከባድ ነው፤ በዚህም በርካታ API keys አንድ upstream
መለያ ይጋራሉ። ሶስት ንብርብሮች የጋራ መለያው በጥያቄዎች እንዳይጥለቀለቅ ያደርጋሉ።

### የእያንዳንዱ connection በአንድ ጊዜ ማስኬድ ገደብ (`max_concurrent`)

እያንዳንዱ provider connection የ`max_concurrent` ከፍተኛ ገደብ ሊያውጅ ይችላል
(`provider_connections.max_concurrent`፣ በconnection modal / API / DB ውስጥ የሚዋቀር)።
ገደብ እንዳይኖር ባዶ ይተዉት። ከታች ያለውን serialization
ንብርብር የሚቆጣጠረው ዋና ማስተካከያ ይህ ነው — ወደ መለያው እውነተኛ የአንድ ጊዜ ማስኬድ አቅም ያዋቅሩት (ለምሳሌ GLM ~1፣ MiniMax ~2)።

### የእያንዳንዱ model በአንድ ጊዜ ማስኬድ ገደቦች (`modelConcurrency`)

አንድ connection በ`rateLimitOverrides` map ውስጥ ለእያንዳንዱ model ትክክለኛ የአንድ ጊዜ ማስኬድ ገደቦችን
በተጨማሪ ሊያውጅ ይችላል፦

```json
{
  "rateLimitOverrides": {
    "maxConcurrent": 4,
    "modelConcurrency": { "glm-5": 1, "glm-4.7": 3 }
  }
}
```

በconnection modal (**Rate limit overrides → Per-model
concurrency caps**፣ በእያንዳንዱ መስመር አንድ `model=cap`) ውስጥ ወይም ተመሳሳይ JSON ቅርጽን በመጠቀም
`PATCH /api/providers/[id]` በኩል ያዋቅሩት። የkey ትርጉሞች፦

- **ለconnection አጠቃላይ ከሆነው ገደብ ጋር ለmodel የተወሰነው፦** `maxConcurrent` የጋራ
  የconnection አጠቃላይ ከፍተኛ ገደብ ሆኖ ይቆያል። ሁለቱም ሲተገበሩ፣ ሁለቱም gates በተመሳሳይ composite gate ውስጥ
  በአንድ ክዋኔ ይያዛሉ
  (`global → provider → account → model`)፤ በተግባር የሚሠራው ይበልጥ
  ጥብቅ የሆነው ተፈጻሚ ገደብ ነው።
- **ትክክለኛ የmodel-key ማዛመድ፦** keyው የrouting resolution ከተጠናቀቀ በኋላ ለ
  executor የሚተላለፈው የmodel string ነው — በመደበኛነት ባዶው upstream model id
  (`glm-5`) እንጂ በclient በኩል ያለ `provider/model` alias አይደለም (`zai/glm-5` ከ
  `glm-5` ጋር አይዛመድም)። Values የአዎንታዊ ኢንቲጀር በአንድ ጊዜ የሚከናወኑ ጥያቄዎች ገደቦች ናቸው።
- **አካባቢያዊ queueing፣ discovery የለም፦** ከመጠን በላይ የሆኑ ጥያቄዎች በነባሩ
  የqueue/timeout አሠራር መሠረት በአካባቢው queue ውስጥ ይጠብቃሉ (type ያላቸው `SEMAPHORE_TIMEOUT` /
  `SEMAPHORE_QUEUE_FULL` የadmission ስህተቶች)። OmniRoute የupstream policyን አያገኝም ወይም
  አይገምትም — ኦፕሬተሩ ያዋቀራቸውን ትክክለኛ ገደቦች ያስፈጽማል። የሞላ model gate providerን ፈጽሞ አያሰናክልም እንዲሁም
  ቋሚ የmodel lockout አይፈጥርም፤ የupstream 429/cooldown/fallback ባህሪ
  እንደ የስህተት የመጨረሻ መከላከያ ይቆያል።
- **የእያንዳንዱ connection፣ የእያንዳንዱ process ወሰን፦** caps ለእያንዳንዱ database connection የተለዩ ሲሆኑ
  በmemory ውስጥ ይያዛሉ፤ ስለዚህ ተመሳሳዩን upstream API key ዳግም የሚጠቀሙ ሁለት connections
  እርስ በርሳቸው አይቀናጁም።
- **ያልተዋቀረ ማለት ምንም ለውጥ የለም፦** mapን አለማካተት (ወይም የdashboard fieldን ባዶ መተው)
  ምንም model gate አይጨምርም። ምንም ዓለም አቀፍ የprovider ገደብ ሳይወሰን የሚደረግ የምሳሌ configuration፦

```text
glm-5=1
glm-4.7=3
```

### የQuota-share ጥያቄ serialization

የquota-share dispatch አዎንታዊ
`max_concurrent` ያወጀ connectionን ሲያነጣጥር፣ ወደዚያ **account** በአንድ ጊዜ የሚላኩ ጥያቄዎች በ
የእያንዳንዱ connection semaphore (key `qsconn:<connectionId>`) በኩል በተራ ይስተናገዳሉ፦ ከመጠን በላይ የሆኑ ጥያቄዎች መለያውን ከማጥለቅለቅ ይልቅ **በ
queue ውስጥ ይጠብቃሉ**። ይህ **fail-open** ነው — የሞላ
queue ወይም timeout ሊላክ የሚችልን
ጥያቄ ፈጽሞ ከመከልከል ይልቅ ያለ slot እንዲቀጥል ያደርገዋል። በ**Settings → Resilience → Quota-share per-connection
concurrency** (`resilienceSettings.quotaShareConcurrencyLimit.enabled`፣ በነባሪ ክፍት
ነው) ውስጥ ያብሩት ወይም ያጥፉት። የ`max_concurrent` cap ከሌለ ባህሪው አይቀየርም።

> የquota-share routing gate (`selectQuotaShareTarget`፣ DRR + P2C) ራሱ
> fail-open ሲሆን ገደቡ ላይ የደረሰ connectionን _ቅድሚያ ብቻ ይቀንስለታል_ — አንድ
> connection ብቻ ባለበት pool ውስጥ ጠንካራ ገደብ ማድረግ አይችልም፤ ስለዚህ ፍሰቱን በእውነት
> የሚይዘው ይህ semaphore ነው።

### Combo cooldownን ያገናዘበ retry

ለእያንዳንዱ combo strategy (ሲነቃ)፣ ለአጭር ጊዜ በሚቆይ transient cooldown 429ን
የሚያረጋግጥ ጥያቄ 429ን ከመመለስ ይልቅ cooldownው እስኪያልፍ ይጠብቃል እና እንደገና
dispatch ያደርጋል — ይህ በmulti-model combos ላይ ያሉ Gemini-class TPM/RPM windowsን (~60s retry-after)
ይሸፍናል፤ ለምሳሌ የ2-model combo ሁለቱም targets የእያንዳንዱ model
rate limit ላይ ሲደርሱ። በ**Settings → Resilience** ውስጥ ባለው `comboCooldownWait` (`enabled`፣ `maxWaitMs`፣ `maxAttempts`፣
`budgetMs`) የተገደበ ነው። በ`quota_exhausted`
(እስከ እኩለ ሌሊት locked) ወይም auth/not-found reasons ላይ ፈጽሞ አይጠብቅም።

ተመሳሳዩ gate ከdispatch በፊት ያለውን ሁኔታ (#16319) ይሸፍናል፦ ምንም ሙከራ ከመደረጉ በፊት የአንድ combo
እያንዳንዱ target የእሱ model በአጭር
transient lockout ውስጥ ስላለ ሲዘለል፣ zero-attempt path ምንም hint የሌለውን
`503 ALL_TARGETS_SKIPPED` ከመመለስ ይልቅ በተመሳሳዩ
ገደቦች ስር lockoutው እስኪያልፍ ይጠብቃል እና እንደገና dispatch ያደርጋል። መጠበቅ በማይፈቀድበት ጊዜ (ገደብ፣ ሙከራ ወይም budget
ካለቀ፣ ወይም featureው ከጠፋ)፣ terminal responseው ከመጀመሪያው
transient lock ማብቂያ `retry_after` / `reset_at`ን ይዞ ወደ
`429 rate_limit_error` ይሻሻላል፤ quota፣ auth እና not-found locks ምንም hint የሌለውን 503 ይዘው ይቆያሉ።

```text
#16319 · comboCooldownWait · pre-dispatch (attempts = 0)
all targets skipped + transient model lockout:
  enabled ∧ 0 < waitMs ≤ maxWaitMs ∧ attempt < maxAttempts ∧ budgetLeftMs ≥ waitMs
    → wait → re-dispatch
  wait = false → HTTP 429 rate_limit_error
  retry_after / reset_at ← earliest transient lock expiry
quota_exhausted / auth_error / not_found / not_found_local:
  no transient hint → HTTP 503 ALL_TARGETS_SKIPPED
```

---

## 5. የጥያቄ ወረፋ መግቢያ ቁጥጥር (v3.8.49 · issue #6593)

**ወሰን**፦ የአካባቢው፣ ለእያንዳንዱ provider+connection የተለየ የፍጥነት-ገደብ ወረፋ (`open-sse/services/rateLimitManager.ts`፣
በBottleneck የሚደገፍ)፤ ከላይ ካሉት ሦስት ዘዴዎች አንድ ደረጃ በታች።

**`maxWaitMs` የወረፋ ጥበቃን ይገድባል፤ `executionMaxWaitMs` ደግሞ አፈጻጸምን ይገድባል።**
ሁለቱ ሆን ተብለው የተለያዩ ናቸው፣ አንዳቸውም ለሌላው ግብዓት አይሆንም።

`resilienceSettings.requestQueue.maxWaitMs` **የወረፋ-ጥበቃ በጀት** ነው፦
የprovider ቦታ እስኪገኝ መጠበቅን እና ከዚያ QUEUED ሁኔታ ውስጥ መቆየትን ያካትታል፤ ሥራው
ከQUEUED ወጥቶ መፈጸም በጀመረበት ቅጽበት የጊዜ ቆጣሪው ይሰረዛል
(`rateLimitManager.ts`፣ `wrappedFn`)። ይህን ጊዜ ያለፈ ጥያቄ
ወደ upstream ፈጽሞ አይደርስም። ነባሪው 30000ms ሲሆን፣
በ`src/lib/resilience/settings.ts` ውስጥ ባለው `DEFAULT_REQUEST_QUEUE_MAX_WAIT_MS`
ይቀርባል እና በ`tests/unit/ratelimit-admission-control-6593.test.ts`
ተወስኖ ተቀምጧል፤ ስለዚህ በእሱ ላይ የሚደረግ ለውጥ ይህ አንቀጽ ሳይታወቅ ጊዜ ያለፈበት ሆኖ እንዲቀር ከማድረግ ይልቅ
ያንን ሙከራ ያሳክታል።

`resilienceSettings.requestQueue.executionMaxWaitMs` Bottleneck
እንደ ሥራ `expiration` የሚቀበለው ሲሆን፣ የጊዜ ቆጣሪው መላክ ከተከናወነ በኋላ ብቻ ይጀምራል። የራሳቸው
upstream timeout ለሌላቸው executors የመጨረሻ መከላከያ ነው፤ የexecutor የራሱ fetch-start timeout ከዚህ የሚረዝም ከሆነም
ወደዚያ ጊዜ ይጨመራል፣ ስለዚህ ጤናማ እና በሂደት ላይ ያለ ምላሽን ሊያቋርጥ አይችልም። ነባሪው 600000ms (10 ደቂቃ) ነው።

የወረፋውን በጀት ወደ `expiration` ማስገባት ቀደም ሲል non-incremental
gatewaysን በሥራ መካከል ይገድል የነበረው ነው — የመጀመሪያዎቹ ባይቶች ከመምጣታቸው በፊት ለደቂቃዎች መሥራታቸው ትክክለኛ ነው —
እናም expiration እንደ `code:
"RATE_LIMIT_EXECUTION_TIMEOUT"` (HTTP 504) የሚቀርበው፣ የወረፋው በጀት ደግሞ
የqueue-timeout codeን የሚይዘው በዚህ ምክንያት ነው። አንዳቸውንም በ`RATE_LIMIT_MAX_WAIT_MS` /
`RATE_LIMIT_EXECUTION_MAX_WAIT_MS` (env) ወይም በdashboard
(**Settings → Resilience**) በኩል ይቀይሩ። ሁለቱም መደበኛ ሲደረጉ በ1ms–24h መካከል ይገደባሉ።

**ለሁለቱም የቅድሚያ ቅደም ተከተል፦** env var የሚያቀርበው _ነባሪውን_ ብቻ ነው።
በ`resilienceSettings.requestQueue` ውስጥ በቋሚነት የተቀመጠ እሴት (dashboard / API patch፣
በ`key_value` ውስጥ የተከማቸ) ከእሱ ቅድሚያ ያገኛል፤ እና ለእያንዳንዱ connection የተወሰነ
`rateLimitOverrides.maxWaitMs` / `.executionMaxWaitMs` ከዚያም ቅድሚያ ያገኛል። ስለዚህ
አስቀድሞ በቋሚነት የተቀመጠ እሴት ባለው deployment ላይ env varን ማቀናበር
ምንም ነገር አይቀይርም — በምትኩ በቋሚነት የተቀመጠውን ቅንብር ያጽዱ ወይም ያዘምኑ።

በወረፋ ውስጥ የመቆያ ጊዜ በ`maxWaitMs` ይገደባል፤ ከታች ያለው `maxQueueDepth` ደግሞ
በአንድ ጊዜ ስንት ጠሪዎች በወረፋ ሊቆዩ እንደሚችሉ ይገድባል።

**`maxQueueDepth` — በምርጫ የሚነቃ የመግቢያ ገደብ (አዲስ)።** `resilienceSettings.requestQueue.maxQueueDepth`
ለአንድ provider+connection በአንድ ጊዜ ስንት ጥያቄዎች በወረፋ ሊቆዩ (ገና ሳይላኩ) እንደሚችሉ
ይገድባል። ወረፋው አስቀድሞ `maxQueueDepth`
ጥያቄዎችን ይዞ ሲገኝ፣ አዲስ ጥያቄ እስከ `limiter.schedule()` ከመድረሱ **በፊት**
typed `code: "RATE_LIMIT_QUEUE_FULL"` error በመስጠት ወዲያውኑ ውድቅ ይደረጋል —
ስለዚህ ውድቅ ማድረጉ አነስተኛ ወጪ ያለው ሲሆን፣ ለዚያ ጥያቄ ማንኛውም downstream
prompt-compression / translation ሥራ ከመከናወኑ በፊት ይፈጸማል። ነባሪው `0` =
የተሰናከለ ሲሆን፣ ነባሩን ገደብ-የለሽ የወረፋ ባህሪ ይጠብቃል፤ በ0–100000 መካከል ይገደባል።
በ`RATE_LIMIT_MAX_QUEUE_DEPTH` (env) ወይም
`resilienceSettings.requestQueue.maxQueueDepth` (dashboard/API patch) በኩል ይቀይሩ።

የመግቢያ ፍተሻው ራሱ pure function ነው
(`open-sse/services/rateLimitManager/admission.ts::checkQueueAdmission`)፣ ስለዚህ
እውነተኛ Bottleneck limiter ሳያስፈልግ በunit test መፈተሽ ይቻላል።

> #6593ን የከፈተው RFC የ`bypassCompressionOnRateLimit`
> flagንም አቅርቦ ነበር። የዚህ repo `open-sse/services/compression/` pipeline
> በወጪው LLM ጥያቄ ላይ የሚከናወን prompt/context compression ነው (`chatCore.ts`፣
> በ`resolveCompressionSettings`/`selectCompressionStrategy` block አካባቢ)፤
> በተፈጠሩ 429 bodies ላይ የሚከናወን HTTP response compression አይደለም — ለቀጥተኛ bypass flag
> የሚዛመድ code path የለም። ያ የprompt-compression ደረጃም
> በአሁኑ ጊዜ በጥያቄ pipeline ውስጥ ከ`withRateLimit()` _በፊት_ ይሠራል፤ ስለዚህ
> queue-full በሚል ውድቅ ሲደረግ እሱን ለመዝለል ቅደም ተከተሉን መቀየር፣ ከዚህ issue ወሰን የተለየና ትልቅ
> ለውጥ ነው፤ ሆን ተብሎ **እዚህ አልተተገበረም**፣ እና የCPU ቁጠባው ጥቅም
> የቅደም ተከተል መቀየሩን ስጋት የሚያዋጣ ከሆነ እንደ follow-up ተትቷል።

---

## 6. የዝግተኛ ዥረት የውጤት መጠን ተቆጣጣሪ (#9709)

አማራጭ የሆነው `resilienceSettings.streamRecovery.throughputWatchdog` ጥበቃ፣
አሁንም chunks እየላከ ነገር ግን ከተዋቀረው ጠቃሚ የውጤት መጠን በታች የረዳት ውጤት
እያመነጨ ያለ upstream ይለያል። ይህ ሆን ተብሎ ከidle timeout የተለየ ነው፦
heartbeats እና metadata የትኛውንም timer ዳግም አያስጀምሩም፣ እንደ እድገትም
አይቆጠሩም። የውጤት ጥራት ምንም ይሁን ምን ፍጹም የደህንነት ጣሪያ ሆኖ
ከሚቆየው hard attempt deadline (#9153) ጋርም የተለየ ነው።

watchdog ማቋረጥ ከመቻሉ በፊት የማሟሟቂያ ጊዜ እና ከዚያ በኋላ ሙሉ rolling window
ያስፈልገዋል። ከChat Completions እና Responses API የውጤት ክስተቶች የሚመጡ
የጽሑፍ deltas ይቆጥራል (ጥንቃቄ የተደረገበት የUTF-8 byte ግምታዊ መለኪያ)፣
usage-only እና ባዶ ክስተቶችን ችላ ይላል፣ እንዲሁም tool-call ወይም reasoning
ክስተቶች በሂደት ላይ ሳሉ ግምገማውን ያቆማል። በነባሪነት ተሰናክሏል እና
በ`STREAM_THROUGHPUT_WATCHDOG_ENABLED=true` ማንቃት ይቻላል፤ window፣
warm-up፣ ዝቅተኛው rate እና ሊለካ የሚችለው ዝቅተኛ ውጤት በመደበኛው
resilience-settings normalization layer ገደብ ውስጥ ይቀመጣሉ።

ሲነቃ፣ የwatchdog ማቋረጥ ተግባራዊ የሚሆነው ንቁ በሆነው upstream attempt ላይ
ብቻ ነው። ማንኛውም client-visible bytes ከመላካቸው በፊት፣ ነባሩ
same-account early-recovery path attemptን እንደገና ሊከፍት ይችላል። commit ከተደረገ
በኋላ ዥረቱ ያለጥንቃቄ በድጋሚ አይጫወትም፤ suffixን ማገናኘት የሚችለው ነባሩ
ደህንነቱ የተጠበቀ mid-stream continuation contract ብቻ ነው። Finalization
አንድ ጊዜ ብቻ የሚከናወን ሆኖ ይቀጥላል፣ ስለዚህ usage accounting እና semaphore
release አይደጋገሙም።

---

## 7. የUpstream ሁኔታ ዳግም መግለጫ (በስህተት የተገለጹ የኮታ ስህተቶች)

**ወሰን፦** ጊዜያዊ የኮታ መሟጠጥን በተሳሳተ HTTP status የሚዘግብ አንድ upstream gateway።

**ዓላማ፦** downstream ተጠቃሚዎች (fallback engine፣ combo aggregation፣ ለclient የሚታየው response) የውድቀቱን እውነተኛ እንደገና ሊሞከር የሚችል ባህሪ እንዲያዩ፣ ከclassification በፊት አሳሳች statusን ማረም።

አንዳንድ gateways ጊዜያዊ የኮታ መሟጠጥን እንደገና ሊሞከር በማይችል HTTP
status ያመለክታሉ። `agentrouter.org` ከመደበኛው `429` ይልቅ `403` (አንዳንድ ጊዜ
`400`) ከቻይንኛ body (`用户额度不足` / `额度不足`) ጋር ይመልሳል። እንደ Claude
Code ያሉ clients `403`ን እንደ ቋሚ ውድቀት በመቁጠር sessionን ያቋርጣሉ፣ እና
እርማት ከሌለ fallback engine እንደ የኮታ ክስተት ሳይሆን እንደ `AUTH_ERROR`
ይመድበዋል።

**አተገባበር፦**

- Registry + matcher፦ `open-sse/config/upstreamStatusRestatement.ts` — ለእያንዳንዱ
  provider የሚዘጋጅ የሕጎች ዝርዝር (`{id, fromStatuses, toStatus, textMarkers,
excludeMarkers, defaultRetryAfterMs}`)፣ በ`applyStatusRestatement()` በኩል የሚዛመድ።
- የጥሪ ቦታ፦ በ`open-sse/handlers/chatCore.ts` ውስጥ ያለው `providerFailure:` block
  (በመስመር 3654 አካባቢ)፣ `parseUpstreamError()` የerror HTTP status ያለውን upstream
  response (`!providerResponse.ok`) ከተነተነ ወዲያውኑ እና ማንኛውም
  classification ከመካሄዱ በፊት፣ ይህም እያንዳንዱ downstream ተጠቃሚ የታረመውን
  status እንዲያይ ያደርጋል። በ`200` SSE stream ውስጥ የተካተቱ ስህተቶች የተለየ፣
  በኋላ የሚከናወን stream-parsing pathን ይከተላሉ እና በአሁኑ ጊዜ በዚህ hook
  **አይሸፈኑም** — ይህ የታወቀ ገደብ ነው፣ ነገር ግን እንደ error HTTP status
  ለሚታየው የagentrouter misstatus እስካሁን አላስፈለገም።
- እንደገና የመሞከር ብቁነት፦ `429` በ`RETRY_AFTER_ELIGIBLE_STATUSES`
  (`open-sse/services/combo/unavailableRetryGate.ts`) ውስጥ ስላለ፣ እንደገና የተገለጸ
  error እንደ የማይሰራ `403` ከመታየት ይልቅ እውነተኛ የretry window ይይዛል።
- ሰው ሠራሹ `60s` `defaultRetryAfterMs` (`upstreamStatusRestatement.ts`)
  እንደገና የተገለጸው response ለ**client** የሚነግረው ብቻ ነው፤ ይህ ራሱ
  የconnectionው ውስጣዊ cooldown/lockout ጊዜ አይደለም — ያንን የሚወስነው
  እንደገና የተገለጸውን error በተግባር የሚያስተናግደው የተለየ mechanism ነው
  (የConnection Cooldown እየጨመረ የሚሄድ backoff፣ §2፣ ለAPI-key providers
  መሠረታዊ `3s`፤ ወይም እንደ agentrouter ላሉ per-model-quota providers የModel
  Lockout፣ §3)። router ለclient ከሚያሳውቀው የ60s window ቀደም ብሎ በውስጥ
  እንደገና ለመሞከር ብቁ ሊሆን ይችላል — ይህ ሆን ተብሎ የተቀመጠ headroom ነው
  እንጂ bug አይደለም።

ቋሚ ስህተቶች (የagentrouter `无权访问模型` — ይህን ሞዴል የመድረስ ፈቃድ የለም)
በፍጹም እንደገና አይገለጹም፦ `textMarkers` ቢዛመዱም `excludeMarkers` ሕጉን
ውድቅ ያደርገዋል፣ ስለዚህ error የመጀመሪያ statusን ይዞ ይቆያል እና ምንም ነገር
ለዘላለም እንደገና አይሞክረውም። የሚዛመደው provider classification rule
(`agentrouter-model-access-denied` በ`open-sse/config/providerErrorRules.ts` ውስጥ፦
`reason: "auth_error"`፣ `scope: "model"`፣ የታወጀ `6h` base cooldown)
በ`checkFallbackError` (`open-sse/services/accountFallback.ts`) የሚፈተሸው
ከአጠቃላይ apikey-category `FORBIDDEN` early-return _በፊት_ ሲሆን፣
በ`honorsRuleLockScope(provider)` የተገደበ ነው (#10334 — በአሁኑ ጊዜ
በ`providerErrorRules.ts` ውስጥ ባለው `HONORS_RULE_LOCK_SCOPE_PROVIDERS` allowlist
አማካኝነት ለagentrouter ብቻ የተወሰነ)። ሕጉ ያወጀው የ6h cooldown
እንደ `fallbackResult.baseCooldownMs` ሙሉ በሙሉ ይተላለፋል፣ ነገር ግን አሁንም
ቀድሞ የነበረውን per-model-quota lockout path (`lockModelIfPerModelQuota()` /
`recordModelLockoutFailure()`፣ ከcooldown source በስተቀር በ#10334 ያልተለወጠ)
ይጠቀማል፦ እንደ ማንኛውም ሌላ model lockout ወደ operatorው
`mlSettings.maxCooldownMs` (ነባሪ `1_800_000ms` / 30min) ዝቅ ተደርጎ ይገደባል፣
እና _የሚቀመጠው lockout reason_ የሕጉ `"auth_error"` ሳይሆን ቀድሞ የነበረው
hardcoded `"forbidden"` ሆኖ ይቆያል — ከጫፍ እስከ ጫፍ የሚከበረው የcooldown
ቆይታ ብቻ ነው፣ reason string አይደለም። connectionው ራሱ ንቁ ሆኖ ይቆያል፤
በተመሳሳይ connection ላይ ያሉ sibling models አይጎዱም።

በድጋሚ የተገለጹ የኮታ ስህተቶች (`额度不足`) በምርት አካባቢ የአቅራቢ ደንብ ላይ ይደርሳሉ
(`agentrouter-user-quota-exhausted`: `reason: "quota_exhausted"`, `scope:
"connection"`፣ የራሱ የሆነ የተገለጸ የማቀዝቀዣ ጊዜ የለውም — የማከማቻ ንብርብሩ
ተመጣጣኝ የbackoff ነባሪ ቅንብር ተግባራዊ ይሆናል)። ከ#10334 ጀምሮ፣ በ
`ProviderErrorRuleMatch` ላይ ያለው `scope` ከጫፍ እስከ ጫፍ ጥቅም ላይ ይውላል፣ ነገር ግን **በ**
`HONORS_RULE_LOCK_SCOPE_PROVIDERS` ፈቃድ ዝርዝር ውስጥ ላሉ አቅራቢዎች ብቻ ነው
(`providerErrorRules.ts` — በአሁኑ ጊዜ `"agentrouter"` ብቻ፣ በ
`honorsRuleLockScope()` የተገደበ)። ለሌሎች አቅራቢዎች በሙሉ
`scope` ልክ ከ#10334 በፊት እንደነበረው መረጃ ሰጪ ብቻ ሆኖ ይቀራል።
`checkFallbackError` የተዛመደውን ደንብ ወሰን እንደ
`fallbackResult.ruleScope` ያቀርባል፤ `isAgentrouterConnectionQuotaScope()`
(`src/sse/services/auth.ts`) አንድ `ruleScope` በእውነት በግንኙነት ደረጃ
ተፈጻሚ እና ራሱን የሚያገግም ምልክት እንደሆነ ማክበር ደህንነቱ የተጠበቀ
መሆኑን የሚያረጋግጥ የጋራ guard ነው (`scope` `"connection"`፣ reason
`quota_exhausted`፣ ፈጽሞ `permanent` ያልሆነ፣ ፈጽሞ `creditsExhausted`
ያልሆነ — ወደፊት አንድ ደንብ `scope` `"connection"`ን ከቋሚ የመለያ ሁኔታ
ጋር እንዳያጣምር መከላከያ ነው)። ሁለት ተጠቃሚዎች ይጠሩታል፦

- **ማከማቻ** (`markAccountUnavailable()`, `src/sse/services/auth.ts`)፦
  ወደ passthrough-provider **በእያንዳንዱ ሞዴል** የመቆለፊያ
  ቅርንጫፍ ከመውደቅ ይልቅ (agentrouter `passthroughModels: true` ነው → `hasPerModelQuota()`
  `true` ይመልሳል)፣ **ጊዜያዊ የግንኙነት ማቀዝቀዣ ጊዜ** ተግባራዊ ያደርጋል —
  `testStatus: "unavailable"` + `rateLimitedUntil`፣ ፈጽሞ የመጨረሻ ሁኔታ
  (`credits_exhausted`/`banned`/`expired`) አይደለም — ስለዚህ ግንኙነቱ
  በእጅ የማረጋገጫ መረጃ ዳግም እንዲቀናበር ሳያስፈልገው የማቀዝቀዣው ጊዜ
  ሲያበቃ በራሱ ያገግማል። `disableCooling: true` ላላቸው ግንኙነቶች
  ይዘለላል (#2997)፦ ያ የመርጦ መውጣት በምትኩ ወደ በእያንዳንዱ ሞዴል
  መቆለፊያ ይወርዳል (በሰነድ የተገለጸ የጥቅምና ጉዳት ሚዛን ነው —
  ከቅርንጫፉ በላይ ያለውን የኮድ አስተያየት ይመልከቱ)።
- **በተመሳሳይ ጥያቄ ውስጥ የcombo ማስተላለፊያ** (`applyComboTargetExhaustion()`,
  `open-sse/services/combo/targetExhaustion.ts`)፦ ያው guard ግንኙነቱን
  `${provider}:${connectionId}` ቁልፍ ተጠቅሞ በማህደረ ትውስታ ውስጥ ባለው
  `exhaustedConnections` set ላይ ምልክት ያደርግበታል። ይህ የሚዘለው ቀሪ
  የተመሳሳይ-ጥያቄ ዒላማ፣ _ዒላማው ራሱ ያንኑ `connectionId` በራሱ_
  የዒላማ ነገር ላይ አስቀድሞ የያዘ ከሆነ ብቻ ነው (`getExhaustedTargetSkipReason()`,
  `open-sse/services/combo/comboPredicates.ts`፣ ከ`exhaustedConnections`
  lookup በፊት `if (provider &&
connectionId)`) — የተለመደ የሞዴል-ዝርዝር combo፣ ወንድም ዒላማዎቹ የራሳቸው የተሰካ
  `connectionId` የሌላቸውበት እና አንዱ ከምላሹ
  `X-OmniRoute-Selected-Connection-Id` header በእያንዳንዱ dispatch ወቅት ብቻ
  የሚወሰንበት፣ ያንን የቁልፍ መዛመድ ፈጽሞ አያገኝም። ለዚያ የተለመደ
  ሁኔታ፣ አንድ ቀሪ leg አሁን ያለቀበትን መለያ እንዳይጠቀም የሚያደርገው
  እውነተኛ ጥበቃ ይህ Set **አይደለም** — ከላይ ያለው የማከማቻ ንብርብር
  (የግንኙነቱ `rateLimitedUntil` አሁን ወደፊት ላይ ነው) ከዚሁ guard ጋር
  ተጣምሮ ለውድቀቱ `transientRateLimitedProviders`ን መጨቆኑ ነው
  ("ባለሁለት-ደረጃ ንድፍ" እና በ`targetExhaustion.ts` ውስጥ ባለው
  `isAgentrouterConnectionQuotaScope` ቅርንጫፍ ላይ ያለውን የኮድ አስተያየት
  ይመልከቱ)፦ ያ Set ምልክት ሳይደረግበት ሲቀር፣ የ`combo.ts`
  `allowRateLimitedConnection` የግዳጅ-ፍቀድ (`open-sse/services/combo.ts:1005-1013`,
  `:2734-2738`) ለቀሪዎቹ የአቅራቢው legs **አይ**ነሳም፣ ስለዚህ የማረጋገጫ
  መረጃ ምርጫው `rateLimitedUntil` filter (`src/sse/services/auth.ts:1238`)
  በተለመደው ሁኔታ ይከበራል፣ እና ቀሪው leg የተለየ፣ አሁንም ብቁ የሆነ
  agentrouter ግንኙነት ይመርጣል ወይም ምንም የማረጋገጫ መረጃ ሳይገኝ
  ይወድቃል — ይህ ቅርንጫፍ አሁን ወደ አቀዘቀዘው ግንኙነት በግድ
  ተመልሶ አይገባም።

### ባለሁለት-ደረጃ ንድፍ፦ የሁኔታ ዳግም መግለጫ፣ ከዚያም ምደባ

የሁኔታ ዳግም መግለጫ (`upstreamStatusRestatement.ts`) እና የአቅራቢ
ምደባ ደንቦች (`open-sse/config/providerErrorRules.ts`,
`providerRuleRegistry`) ሁለቱም በአቅራቢ id እና በጽሑፍ ምልክቶች ቁልፍ
የሚያደርጉ የተለያዩ registries ናቸው፣ ነገር ግን በተለያዩ ቦታዎች
ይሰራሉ እና የተለያዩ ዓላማዎችን ያገለግላሉ፦ restatement በ`chatCore.ts`
ውስጥ ቀደም ብሎ የHTTP ሁኔታውን እንደገና ይጽፋል፤ የምደባ ደንቦች
ደግሞ በ`checkFallbackError()` ውስጥ የfallback `reason`ን እና የመቆለፊያ
`scope`ን (`model` / `provider` / `connection`) ይመርጣሉ
(`open-sse/services/accountFallback.ts`)።

የምደባ ደንቦች ሙሉ የስህተት **ጽሑፍ**ን (እንደ `额度不足` ያሉ
የbody ምልክቶችን ለማዛመድ የሚያስፈልገው) የሚያዩት በ
`providerErrorRules.ts` ውስጥ ባለው `FULL_TEXT_RULE_PROVIDERS`
ፈቃድ ዝርዝር ውስጥ ላሉ አቅራቢዎች ብቻ ነው — በአሁኑ ጊዜ
`"agentrouter"` ብቻ። ለሁሉም ሌሎች **አብሮገነብ ካታሎግ** አቅራቢዎች፣
`checkFallbackError` ለ`getProviderErrorRuleMatch` የሚያስተላልፈው
የተዋቀረውን ስህተት (`{code, type}`) ብቻ ነው፣ ይህም በ
header/status/code ላይ ለተመሰረቱ ደንቦች በቂ ቢሆንም የbody-ጽሑፍ
ምልክቶችን ማየት አይችልም። `resolveRuleMatchBody()` helper ይህን ምርጫ
ያከናውናል፦ በፈቃድ ዝርዝሩ ውስጥ ላሉ አቅራቢዎች ሙሉ የስህተት
ጽሑፍ፣ ካልሆነ የተዋቀረው ስህተት። አንድ **አብሮገነብ** አቅራቢን ወደ
`FULL_TEXT_RULE_PROVIDERS` ማከል ግልጽ የበእያንዳንዱ-አቅራቢ opt-in
ነው — ይህ የሚኖረው በዝርዝሩ ላይ ላልሆነ እያንዳንዱ አቅራቢ
ነባሪው መንገድ ባይት-በ-ባይት ሳይቀየር እንዲቆይ ነው።

የአንድ ደንብ `scope` (`model` / `provider` / `connection`) ከ
`FULL_TEXT_RULE_PROVIDERS` የተለየ opt-in ነው፦ `checkFallbackError`
ይህን እንደ `fallbackResult.ruleScope` ብቻ ያቀርበዋል፣ እና downstream
ተጠቃሚዎች በዚሁ ፋይል ውስጥ ባለው
`HONORS_RULE_LOCK_SCOPE_PROVIDERS` ፈቃድ ዝርዝር ውስጥ ላሉ አቅራቢዎች
ብቻ፣ ከመረጃ ሰጪ መለያ የተለየ ነገር እንደሆነ ያከብሩታል (`በ
honorsRuleLockScope()` የተገደበ — በአሁኑ ጊዜ `"agentrouter"` ብቻ)።
አንድ አቅራቢ በዚያ ፈቃድ ዝርዝር ላይ ከገባ በኋላ የ
`scope: "connection"` መዛመድ በትክክል ምን እንደሚያደርግ ለማየት
ከላይ ያለውን "በድጋሚ የተገለጹ የኮታ ስህተቶች" ይመልከቱ።

**#11104 — በኦፕሬተር የታወጁ ደንቦች ሁለቱንም የፍቃድ ዝርዝሮች ያልፋሉ።** አንድ ኦፕሬተር
ይህን ፋይል ሳያርትዕ በሩጫ ጊዜ በ`settings.providerErrorRules`
(`open-sse/config/providerErrorRules.ts::setOperatorProviderErrorRules`)
አማካኝነት ለእያንዳንዱ አቅራቢ ደንብ ማወጅ ይችላል። የኦፕሬተር ደንብን በ
`FULL_TEXT_RULE_PROVIDERS`/`HONORS_RULE_LOCK_SCOPE_PROVIDERS` — አብሮ የተሰሩ
የካታሎግ ደንቦችን **ነባሪ** ባህሪ ለመጠበቅ በታሰቡ የፍቃድ ዝርዝሮች —
ጀርባ መገደብ፣ ደንቡን ማወጅ ራሱ የኦፕሬተሩ ግልጽ የመርጦ መግባት
ውሳኔ ስለሆነ፣ ቀድሞውኑ በዚያ ከተዘረዘሩት በስተቀር ለሁሉም
አቅራቢዎች የቅንብሮቹን ስልት የማይሰራ ያደርገዋል። `resolveRuleMatchBody()`
እና `honorsRuleLockScope()` ሁለቱም መጀመሪያ
`hasOperatorRuleForProvider()`ን ይፈትሻሉ፦ የኦፕሬተር ደንብ ያለው
አቅራቢ፣ በሁለቱ የፍቃድ ዝርዝሮች ውስጥ ቢኖርም ባይኖርም፣
ጥሬውን የስህተት ጽሑፍ ያገኛል እና ያወጀው `scope` ይከበርለታል።

**የሚታወቅ ክፍተት — `providerRuleRegistry` ለHTTP 400 ፈጽሞ አይመከርም።**
የ`checkFallbackError` `BAD_REQUEST` ቅርንጫፍ ሁኔታ 400ን ሙሉ በሙሉ
በራሱ የስርዓተ-ጥለት ድርድሮች (`MODEL_ACCESS_DENIED_PATTERNS`,
`CONTEXT_OVERFLOW_PATTERNS`፣ ወዘተ በ`accountFallback.ts`) ይመድባል፣ እና
ከእሱ በላይ ያለው የ`configuredRule`/`getProviderErrorRuleMatch` ቅርንጫፍ
ከመድረሱ በፊት ይመለሳል። `status: 400` ያለው አብሮ የተሰራ የካታሎግ
ደንብ (ወይም የኦፕሬተር ደንብ) በአገባብ ትክክለኛ ቢሆንም ፈጽሞ
አይተገበርም። በአሁኑ ጊዜ 400ን የሚያነጣጥር ነባር ደንብ የለም፣
ስለዚህ በምርት አካባቢ ምንም ነገር አልተጎዳም — ነገር ግን ወደፊት
የሚጨመር የ400 ደንብ በመጀመሪያ ይህ ቅርንጫፍ እንዲሻሻል ይፈልጋል፤
ይህም ደንብ ከመጨመር የሚበልጥ ለውጥ ነው (ቀድሞውኑ በስርዓተ-ጥለት
ድርድር ባህሪ ላይ ለሚመረኮዝ እያንዳንዱ አቅራቢ 400ን እንደገና
ይመድባል)፣ እና ለአንድ አቅራቢ ብቻ የደንብ ጭማሪ ከተወሰነው ወሰን
ውጭ ነው።

### ኮታን በተሳሳተ መንገድ የሚገልጽ አዲስ መግቢያ በር ማከል

1. በ`statusRestatementRegistry`
   (`open-sse/config/upstreamStatusRestatement.ts`) ውስጥ አንድ የደንብ ድርድር
   ይመዝግቡ። `textMarkers`ን ለአቅራቢው የተለየ አድርገው ያቆዩ፤
   ከ`CREDITS_EXHAUSTED_SIGNALS` (`open-sse/services/accountFallback.ts`) ጋር
   የሚጋጩ አጠቃላይ የእንግሊዝኛ ሐረጎችን ፈጽሞ ዳግም አይጠቀሙ።
2. ትክክለኛውን የመቆለፊያ ወሰን (`connection` ለመለያው በሙሉ የሚመለከት
   ኮታ፣ `model` ደግሞ ለእያንዳንዱ ሞዴል ስህተቶች) ለመምረጥ፣ እንደ
   አማራጭ በ`open-sse/config/providerErrorRules.ts`
   (`providerRuleRegistry`) ውስጥ የምደባ ደንቦችን ይመዝግቡ። ይህ ደረጃ
   ሙሉውን የስህተት ጽሑፍ (የይዘት ምልክቶች) ለሚፈልጉ ደንቦች በምርት
   አካባቢ ተግባራዊ የሚሆነው ለተወሰኑ አቅራቢዎች ብቻ ነው፦ የአቅራቢውን
   id በዚያው ፋይል ወደ `FULL_TEXT_RULE_PROVIDERS` ያክሉ — ካልሆነ
   `checkFallbackError` ለደንቡ የሚያስተላልፈው የተዋቀረውን
   `{code, type}` ስህተት ብቻ ስለሆነ፣ የይዘት-ጽሑፍ ደንብ ከቀጥታ
   ትራፊክ ጋር ፈጽሞ አይዛመድም። በ`status`/`headers` ላይ ብቻ የሚዛመዱ
   ደንቦች (እንደ Opencode ወይም Minimax) ይህን መርጦ መግባት
   አያስፈልጋቸውም። በተናጠል፣ ደንቡ `scope: "connection"` ካወጀ እና
   የታሰበው እውነተኛ የግንኙነት-አቀፍ ማቀዝቀዣ ከተመሳሳይ ጥያቄ
   የጥምር መዝለል ጋር ከሆነ (የመረጃ መለያ ብቻ ካልሆነ)፣ የአቅራቢውን
   id በዚያው ፋይል ውስጥ ወደ `HONORS_RULE_LOCK_SCOPE_PROVIDERS` ያክሉ —
   ይህ በ`markAccountUnavailable()` (`src/sse/services/auth.ts`) እና
   `applyComboTargetExhaustion()`
   (`open-sse/services/combo/targetExhaustion.ts`) ውስጥ እንደ
   `isAgentrouterConnectionQuotaScope()` ያለ ፍጆታን የሚገድበው ነው፤
   ያለዚህ `scope` አሁንም በ`fallbackResult.ruleScope` በኩል ይተላለፋል፣
   ነገር ግን ምንም ነገር በእሱ መሠረት አይሰራም።
3. `tests/unit/upstream-status-restatement.test.ts` እና
   `tests/unit/agentrouter-error-rules.test.ts`ን የሚያንጸባርቁ የክፍል
   ሙከራዎችን ያክሉ (የnot-permanent / not-creditsExhausted መከላከያዎችን
   ጨምሮ፣ እና — አቅራቢው የፍቃድ ዝርዝሩን ከፈለገ — `resolveRuleMatchBody()`
   ሙሉውን ጽሑፍ ለዚያ አቅራቢ ብቻ እንደሚመልስ የሚያረጋግጥ ሙከራ)።

በ`chatCore.ts`፣ `classifyError` ወይም combo ላይ ምንም ለውጥ አያስፈልግም።

#### በወጪ ትራፊክ ባልዲ የተከፋፈለ መቆለፊያ (#10880)

በ`EGRESS_BUCKETED_LOCK_PROVIDERS` (የopencode ቤተሰብ) ውስጥ ያሉ
አቅራቢዎች በIP የተከፋፈለ የላይኛው ስርዓት ተደርገው ይወሰዳሉ
(የopencode ነጻ ደረጃ በIP የተከፋፈለ እንጂ በመለያ የተከፋፈለ
አይደለም — #9611ን ይመልከቱ)፦ `quota_exhausted` **ወይም**
`rate_limit_exceeded` ተብሎ የተመደበ ሁኔታ-429፣ ማዞሪያው ሊሞክራቸው
ከመቻሉ በፊት፣ የመጨረሻ የታወቀ የወጪ ትራፊክ IP አድራሻቸው
ከከሸፈው ግንኙነት ጋር የሚዛመድ እያንዳንዱን በፍቃድ ዝርዝር
የተካተተ የቤተሰቡ ግንኙነት ያቀዘቅዛል
— ይህም N-1 መክሸፋቸው አይቀሬ የሆኑ የላይኛው ስርዓት ጥሪዎችን
ይከላከላል (ከ#10460/#10525 ጋር ተመሳሳይ ቅርጽ)።
`rate_limit_exceeded` ሆን ተብሎ ተካቷል፦ በ`markAccountUnavailable`
መንገድ ላይ ለopencode የተለዩት ደንቦች ፈጽሞ አይዛመዱም (ምንም
headers/body ወደ `checkFallbackError` አይተላለፍም፣ opencode በ
`FULL_TEXT_RULE_PROVIDERS` ውስጥ የለም)፣ ስለዚህ bodyው የደንበኝነት
ምዝገባ ኮታ ጽሑፍን ("monthly usage limit reached") የያዘ 429፣
የ`status_429` ደንብ ከመድረሱ በፊት በኮታ-ጽሑፍ ምትክ
(`buildSubscriptionQuotaFallback`, `accountFallback.ts`; 1h ማቀዝቀዣ)
እንደ `quota_exhausted` ይመደባል — ከኮታ-ጽሑፍ ነጻ የሆነ 429
(ተራ የፍጥነት ገደብ) ግን በ`status_429` ደንብ አማካኝነት እንደ
`rate_limit_exceeded` ይመደባል፣ እና አሁንም የIP ቤተሰቡን ያቀዘቅዛል።
በፍቃድ ዝርዝሩ ለተካተተ አቅራቢ፣ በIP የተከፋፈለ የፍጥነት ገደብ
ከተሟጠጠ ኮታ ጋር ተመሳሳይ ምልክት ነው። ግልጽ ገደቦች፦

- **በተቻለ መጠን**: መቆለፊያው የግንኙነቱን የመጨረሻ የታወቀ `egress_ip`
  ከ`proxy_logs` ይፈታል (የ24h መስኮት፣ የተመሳሰለ፣ ያለ መሸጎጫ)። ቀዝቃዛ መሸጎጫ (የወጪ
  IP ፈጽሞ ካልተፈተሸ) ወይም ረድፍ ከሌለ → ያልተሳካው ግንኙነት አሁንም በቅርንጫፉ
  ይቀዘቅዛል (እንደ አሁኑ ይመዘገባል)፣ የሚቆለፍ ተመሳሳይ ግንኙነት ብቻ አይኖርም።
- **ፈጽሞ ቋሚ አይደለም**: የማቀዝቀዣ ጊዜው የሚታደስ የኮታ መስኮት ነው
  (`testStatus: "unavailable"`)፤ ቋሚ ሁኔታ ከIP-ደረጃ ምልክት ፈጽሞ አይወሰድም።
  `disableCooling` ያላቸው ግንኙነቶች ቅርንጫፉን ሙሉ በሙሉ ያልፋሉ።
- **ለተፈቀደለት ቤተሰብ የመቆለፊያ ጥራጥሬነት ይለወጣል**: ይህ የወሰን
  ለውጥ እንጂ የተመሳሳይ ግንኙነት ማመቻቸት ብቻ አይደለም። opencode የ
  `passthroughModels` አቅራቢ ነው፣ ስለዚህ ከዚህ ቅርንጫፍ በፊት 429 በእያንዳንዱ-MODEL
  ደረጃ መቆለፍን ያስከትል ነበር፤ አሁን ግን የግንኙነት ማቀዝቀዣን ያስከትላል —
  ምንም ተመሳሳይ ግንኙነት ሳይኖረው አንድ ግንኙነት ብቻ ለሚያስኬድ ኦፕሬተርም ጭምር።
  የopencode ደንብ ሰንጠረዥ ትክክለኛ እንደሆነ አስቀድሞ የሚገልጸው ጥራጥሬነት ይህ ነው
  (`scope: "connection"`፣ `providerErrorRules.ts`)፤ opencode በ
  `HONORS_RULE_LOCK_SCOPE_PROVIDERS` ውስጥ ስለሌለ እስካሁን ፈጽሞ አልተከበረም።
  ቅርንጫፉ በግንኙነት-ወሰን ያለውን የagentrouter ቅርንጫፍ በመኮረጅ ያልተሳካውን
  የግንኙነት ማቀዝቀዣ + `backoffLevel` ራሱ ይጽፋል፣ ከዚያም ይመለሳል —
  በእያንዳንዱ-ሞዴል ያለው እገዳና ከታች ያለው አጠቃላይ መንገድ ፈጽሞ አይደረስባቸውም።
- **Combo ተካትቷል**: እንደ agentrouter ቅርንጫፍ፣ ወሰኑ አንድ combo ጠሪ
  በ429 ላይ የሚተገብረውን የ`persistUnavailableState`/`isCombo` ደረጃ ቅናሽ ሆን ብሎ
  ችላ ይላል። በእያንዳንዱ-ሞዴል የሚደረግ መቆለፍ የዚህ ወሰን ደካማ ቅርጽ አይደለም፤
  የተሳሳተ አሃድ ነው፤ ስለተሟጠጠው IP ምንም አይናገርም፣ ስለዚህ የcombo
  ማዞሪያው በእያንዳንዱ ተመሳሳይ ግንኙነት አንድ መሳካቱ የማይቀር ጥሪን ማባከኑን ይቀጥላል።
- **የተመሳሳይ ግንኙነት ደህንነት**: አስቀድሞ ቋሚ ሁኔታ ላይ ያለ ተመሳሳይ ግንኙነት
  (banned/credits_exhausted) ወይም አስቀድሞ ረዘም ያለ የማቀዝቀዣ ጊዜ ያለው
  ፈጽሞ አይተካም።
- **የተወሰነ የፍቃድ ዝርዝር**: `EGRESS_BUCKETED_LOCK_PROVIDERS`ን ማስፋት
  ግልጽ የባለቤት ውሳኔ ነው፤ አጠቃላይ ሽቦ ማገናኘት የለም (pattern #10334/#10419)።
  የተመሳሳይ ግንኙነት መጠይቁ ያንኑ የፍቃድ ዝርዝር እንደ SQL
  ቃል-በቃል ከመድገም ይልቅ ያስራል፣ ስለዚህ ማስፋቱ የአንድ-መስመር ለውጥ ሆኖ ይቆያል።
- **የወጪ IP ማዞር፣ በሁለቱም አቅጣጫዎች**: የፍለጋ መስኮቱ (24h) ከወጪ-IP
  መሸጎጫ TTL (5 min) እጅግ የሰፋ ነው፣ ስለዚህ "የመጨረሻ የታወቀ IP" ታሪክ እንጂ
  የአሁን ሁኔታ አይደለም። የአንድ ግንኙነት proxy በመስኮቱ ውስጥ ከተዘዋወረ
  መቆለፊያው በእውነት የሚጋራ IPን **ሊያመልጠው** ይችላል (የተመዘገበው IP አዲሱ፣
  ያልተሟጠጠው ነው) — በተመሳሳይም ሁኔታ ከተሟጠጠው IP ርቆ የተዘዋወረን
  **ተመሳሳይ ግንኙነት ሊያቀዘቅዝ** ይችላል። ሁለተኛው ሁኔታ ያንን ተመሳሳይ ግንኙነት
  አንድ የማቀዝቀዣ መስኮት ያስከፍለዋል፤ ሁለቱም በታሪክ ላይ የተመሠረተ ፍለጋ
  የሚያስከትላቸው ተቀባይነት ያላቸው የበተቻለ መጠን ገደቦች ናቸው።
- **ወጪ**: ሁለት የተገደቡ የ`proxy_logs` ቅኝቶች (በ
  `idx_pl_timestamp` በኩል በመስኮቱ የተጣሩ)፣ በ429 ድግግሞሽ ጊዜ ብቻ። አዲስ
  index የለም (migration 134 YAGNI)። መካከለኛ መጠን ባለው የእውነተኛ-ትራፊክ DB
  ቅጂ ላይ ተለክቷል፤ ከፍተኛ-የውሂብ-ፍሰት instance በተመሳሳይ መስኮት ውስጥ
  በተመጣጣኝ ሁኔታ ተጨማሪ ረድፎችን ይይዛል።

---

## ሌሎች የጽናት ባህሪያት

- **19 የማዘዋወሪያ ስልቶች** (ቅድሚያ፣ ክብደት ያለው፣ ተራ-በተራ፣ የዐውድ ማስተላለፊያ፣ መጀመሪያ-ሙላ፣ p2c፣ የዘፈቀደ፣ በትንሹ-ጥቅም-ላይ-የዋለ፣ ወጪ-የተመቻቸ፣ ዳግም-ማስጀመርን-የሚያውቅ፣ የዳግም-ማስጀመሪያ-ጊዜ-መስኮት፣ ትርፍ-አቅም፣ ጥብቅ-የዘፈቀደ፣ ራስ-ሰር፣ lkgp፣ ዐውድ-የተመቻቸ፣ መሸጎጫ-የተመቻቸ፣ ውህደት፣ ቧንቧ-መስመር) — [AUTO-COMBO.md](../routing/AUTO-COMBO.md)ን ይመልከቱ።
- **ዳግም ማስጀመርን የሚያውቅ ማዘዋወር** (v3.8.0) — ግንኙነቶችን በኮታ ዳግም ማስጀመሪያ ጊዜ መሠረት ቅድሚያ ይሰጣል።
- **የበስተጀርባ ሁነታ ማውረድ** — Responses API `background: true` ከማስጠንቀቂያ ጋር ወደ የተመሳሰለ ሁነታ ዝቅ ይደረጋል።
- **ተለዋዋጭ የመሣሪያ ገደብ ማወቂያ** — የመሣሪያ ብዛት ገደቦች ሲደረሱ አቅራቢዎችን ወደ ኋላ ያፈገፍጋል።
- **የድንገተኛ ጊዜ አማራጭ** — በ`OMNIROUTE_EMERGENCY_FALLBACK` ይቆጣጠራል፤ ኦፕሬተሮች ዳግም ሳያስጀምሩ ከባህሪ ጥቆማዎች ገጽ ሊተኩት ይችላሉ።

---

## ማረም

- ክብደት ያለው combo `503 all_targets_cooling_down` ምላሽ ከሰጠ (`Retry-After` ተቀናብሯል፣ `diagnostics.excluded` ደግሞ እያንዳንዱን ዒላማ ከ`model_lockout` / `circuit_open` / `provider_cooldown` / `unavailable` ጋር ይዘረዝራል) → pool-ው ተዋቅሯል እና ተገናኝቷል፤ እያንዳንዱ ዒላማ በresilience timer ምክንያት ብቻ ተገልሏል። የ`[COMBO] Weighted selection: every target excluded before dispatch — …` ማስጠንቀቂያ ምክንያቶቹን እና የቀሩትን ሰከንዶች ይጠቅሳል። ከተመሳሳዩ combo የሚመጣ `404 no_executable_targets` ማለት ምንም resilience timer አልተሳተፈም ማለት ነው (የሚሰራ ምንም ነገር የለም፣ ወይም ሁሉም መለያዎች የavailability probe-ውን አላለፉም)። ይህም በ`targetResolution.ts` ውስጥ ከተሰበሰቡት ማግለሎች በ`open-sse/services/combo/pinRecovery.ts` ውስጥ ተገንብቷል።
- የአንድ provider ሁሉም keys ከታለፉ → የcircuit breaker ሁኔታን እና የእያንዳንዱ connection `rateLimitedUntil`/`testStatus`ን ሁለቱንም ያረጋግጡ።
- ከreset window በኋላ provider በቋሚነት ከተገለለ → ኮዱ `getStatus()`/`canExecute()`ን ከመጠቀም ይልቅ ጥሬ `state`ን እያነበበ ነው።
- አንድ key ከወደቀ፣ ሌሎቹ መስራት አለባቸው → ከcircuit breaker ይልቅ connection cooldownን ይምረጡ።
- አንድ model ብቻ ከወደቀ → ከconnection cooldown ይልቅ model lockoutን ይምረጡ።
- State ራሱን መልሶ ማገገም ሲገባው ካላገገመ → የወደፊት timestamp መኖሩን እና ጊዜው ያለፈበትን state የሚያድስ read path መኖሩን ያረጋግጡ። ቋሚ statuses በእጅ ለውጦችን ይፈልጋሉ።

---

## TLS የጣት አሻራ መለየት እና ስውርነት

ለአቅራቢ የተወሰነ ስውርነት (JA3/JA4፣ CCH፣ ማደበዝ) በተናጠል ተመዝግቧል — `docs/security/STEALTH_GUIDE.md`ን ይመልከቱ (git፤ ወደ `/docs` አልተቀናበረም)።

---

## የጽናት ሙከራ (ደረጃ 8 · ክፍል C)

ከጽናት አመክንዮ የአሃድ ሙከራዎች በተጨማሪ፣ ሦስት ሙከራዎች በእውነተኛ
የጭንቀት/ውድቀት ሁኔታዎች የአሂድ ጊዜውን ይፈትሻሉ (ሁሉም ውህደት/የምሽት ናቸው — PRsን የሚያግድ የለም)፦

| ሙከራ            | ምን                                                                                                                                               | ማስኬጃ                                  |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------- |
| ትርምስ           | አስመሳይ የላይኛው ዥረት ኖድ እውነተኛ መዘግየት/ዳግም ማስጀመር/የጊዜ ማብቂያ/503ን ያስገባል፤ የወረዳ ቆራጩ መከፈቱን/መመለሱን እና `checkFallbackError` 503ን እንደ ሊመለስ የሚችል አማራጭ መመደቡን ያረጋግጣል። | `RUN_CHAOS_INT=1 npm run test:chaos`  |
| የሂፕ-እድገት       | በ`--expose-gc` ስር ለእያንዳንዱ `createSSEStream` ~500 ዥረቶች፤ ሂፑ ከጣሪያው በላይ ካደገ ይወድቃል (የOOM መከላከያ #3069)።                                                | `npm run test:heap`                   |
| k6 የረጅም ጊዜ ጭነት | በ`/api/monitoring/health` ላይ ዘላቂ ጭነት፤ የp95/ስህተት ገደቦች።                                                                                            | `k6 run tests/load/k6-soak.js` (በምሽት) |

በ`.github/workflows/nightly-resilience.yml` (cron + dispatch) ይቀናበራል። በነባሪው
`test:integration` ውስጥ፣ የትርምስ እና የሂፕ ሙከራዎች ራሳቸውን ይዘላሉ (`RUN_CHAOS_INT`/`--expose-gc` ከሌለ)።

---

## ተጨማሪ ይመልከቱ

- [የሥነ ሕንፃ መመሪያ](./ARCHITECTURE.md) — የስርዓት ሥነ ሕንፃ እና ውስጣዊ አሠራሮች
- [የተጠቃሚ መመሪያ](../guides/USER_GUIDE.md) — አቅራቢዎች፣ ጥምረቶች፣ የCLI ውህደት
- [ራስ-ሰር ጥምረት ሞተር](../routing/AUTO-COMBO.md) — ባለ16-ምክንያት ውጤት አሰጣጥ፣ የሁነታ ጥቅሎች
