# AGENTS.md

## Muhtasari wa Mradi

Huu ni hazina ya mtaala wa elimu kwa ajili ya kufundisha misingi ya maendeleo ya wavuti kwa wanaoanza. Mtaala ni kozi kamili ya wiki 12 iliyotengenezwa na Microsoft Cloud Advocates, ikiwa na masomo 24 ya vitendo yanayohusu JavaScript, CSS, na HTML.

### Vipengele Muhimu

- **Yaliyomo ya Elimu**: Masomo 24 yaliyopangwa kwa muundo wa moduli za miradi
- **Miradi ya Vitendo**: Terrarium, Mchezo wa Kuandika, Upanuzi wa Kivinjari, Mchezo wa Anga, Programu ya Benki, Mhariri wa Msimbo, na Msaidizi wa AI wa Mazungumzo
- **Maswali Shindani Ya Kihusianisho**: Maswali 48 kila moja ikiwa na maswali 3 (majaribio kabla/baada ya somo)
- **Msaada wa Lugha Nyingi**: Tafsiri za moja kwa moja za lugha zaidi ya 50 kupitia GitHub Actions
- **Teknolojia**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (kwa miradi ya AI)

### Miundo-Mbinu

- Hazina ya elimu yenye muundo wa masomo
- Kila folda ya somo ina README, mifano ya msimbo, na suluhisho
- Miradi huru katika saraka tofauti (quiz-app, miradi mbalimbali ya masomo)
- Mfumo wa tafsiri ukitumia GitHub Actions (co-op-translator)
- Nyaraka zinatolewa kupitia Docsify na zinapatikana kama PDF

## Amri za Kuanzisha

Hazina hii ni hasa kwa kutumia yaliyomo ya elimu. Kwa kufanya kazi na miradi maalum:

### Kuanzisha Hazina Kuu

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Kuanzisha Quiz App (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Anzisha seva ya maendeleo
npm run build      # Tengeneza kwa ajili ya uzalishaji
npm run lint       # Endesha ESLint
```

### API ya Mradi wa Benki (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # Anzisha seva ya API
npm run lint       # Endesha ESLint
npm run format     # Pangilia kwa Prettier
```

### Miradi ya Upanuzi wa Kivinjari

```bash
cd 5-browser-extension/solution
npm install
# Fuata maagizo ya kupakia upanuzi maalum kwa kivinjari
```

### Miradi ya Mchezo wa Anga

```bash
cd 6-space-game/solution
npm install
# Fungua index.html katika kivinjari au tumia Live Server
```

### Mradi wa Mazungumzo (Python Backend)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Weka kigezo cha mazingira cha GITHUB_TOKEN
python api.py
```

## Mtiririko wa Maendeleo

### Kwa Wasaidizi wa Yaliyomo

1. **Fungua hazina kwa fork** kwa akaunti yako ya GitHub
2. **Nakili fork yako** mahali hapo ndani
3. **Tengeneza tawi jipya** kwa mabadiliko yako
4. Fanya mabadiliko kwenye yaliyomo ya masomo au mifano ya msimbo
5. Jaribu mabadiliko yoyote ya msimbo katika saraka za miradi husika
6. Wasilisha rufaa za kuchukua mabadiliko kuzingatia miongozo ya mchango

### Kwa Wanafunzi

1. Funga au nakili hazina
2. Elekea kwenye saraka za masomo kwa mpangilio
3. Soma faili za README kwa kila somo
4. Maliza maswali ya kabla ya somo huko https://ff-quizzes.netlify.app/web/
5. Fanyia kazi mifano ya msimbo katika folda za masomo
6. Maliza kazi za nyumbani na changamoto
7. Fanya maswali ya baada ya somo

### Maendeleo Hai

- **Nyaraka**: Endesha `docsify serve` kwenye saraka ya juu (bandari 3000)
- **Quiz App**: Endesha `npm run dev` kwenye folda ya quiz-app
- **Miradi**: Tumia upanuzi wa VS Code Live Server kwa miradi ya HTML
- **Miradi ya API**: Endesha `npm start` katika saraka husika za API

## Maelekezo ya Kupima

### Kupima Quiz App

```bash
cd quiz-app
npm run lint       # Angalia kwa matatizo ya mtindo wa msimbo
npm run build      # Thibitisha ujenzi unafanikiwa
```

### Kupima API ya Benki

```bash
cd 7-bank-project/api
npm run lint       # Angalia kwa masuala ya mtindo wa msimbo
node server.js     # Thibitisha seva inaanza bila makosa
```

### Mbinu ya Kupima kwa Ujumla

- Hii ni hazina ya elimu isiyo na majaribio ya moja kwa moja ya kina
- Kupima kwa mikono kunalenga:
  - Mifano ya msimbo inakimbia bila makosa
  - Viungo vya nyaraka vinafanya kazi kikamilifu
  - Miradi kujengwa kikamilifu bila hitilafu
  - Mifano inafuata mbinu bora

### Ukaguzi Kabla ya Kuwasilisha

- Endesha `npm run lint` katika saraka zilizo na package.json
- Hakiki viungo vya markdown vipate usahihi
- Jaribu mifano ya msimbo kwenye kivinjari au Node.js
- Hakikisha tafsiri zinahifadhi muundo sahihi

## Miongozo ya Mtindo wa Msimbo

### JavaScript

- Tumia lugha ya kisasa ya ES6+
- Fuata mipangilio ya kawaida ya ESLint iliyopo katika miradi
- Tumia majina yenye maana kwa mabadiliko na kazi kwa ajili ya ufafanuzi wa elimu
- Ongeza maelezo kuelezea dhana kwa wanafunzi
- Tengeneza kwa kutumia Prettier pale panapopangwa

### HTML/CSS

- Vipengele vya semantic vya HTML5
- Kanuni za muundo wa kujibadilisha (responsive)
- Viwango vya uandishi vya darasa wazi
- Maelezo kuelezea mbinu za CSS kwa wanafunzi

### Python

- Miongozo ya mtindo ya PEP 8
- Mifano ya msimbo wazi, ya elimu
- Vidokezo vya aina inapobidi kwa kujifunza

### Nyaraka za Markdown

- Muundo wa vichwa vya habari kwa uwazi
- Mifumo ya msimbo yenye lugha maalum
- Viungo kwenye rasilimali za ziada
- Picha na picha ndogo katika saraka za `images/`
- Maandishi ya alt ya picha kwa upatikanaji

### Mpangilio wa Faili

- Masomo yamenumberwa kwa mfuatano (1-getting-started-lessons, 2-js-basics, nk)
- Kila mradi una saraka za `solution/` na mara nyingi `start/` au `your-work/`
- Picha zimehifadhiwa katika saraka maalum za masomo `images/`
- Tafsiri ziko katika muundo wa `translations/{language-code}/`

## Ujenzi na Uenezaji

### Uenezaji wa Quiz App (Azure Static Web Apps)

Quiz-app imewekwa kwa ajili ya uenezaji wa Azure Static Web Apps:

```bash
cd quiz-app
npm run build      # Inaunda folda ya dist/
# Inaendesha kupitia mtiririko wa kazi wa GitHub Actions wakati wa kusukuma kwenye main
```

Mipangilio ya Azure Static Web Apps:
- **Eneo la app**: `/quiz-app`
- **Eneo la matokeo**: `dist`
- **Mtiririko wa kazi**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### Uzalishaji wa PDF wa Nyaraka

```bash
npm install                    # Sakinisha docsify-to-pdf
npm run convert               # Tengeneza PDF kutoka kwa docs
```

### Nyaraka za Docsify

```bash
npm install -g docsify-cli    # Sakinisha Docsify kote duniani
docsify serve                 # Tumikia kwenye localhost:3000
```

### Ujenzi wa Miradi Maalum

Kila saraka ya mradi inaweza kuwa na mchakato wake wa ujenzi:
- Miradi ya Vue: `npm run build` huunda vifurushi vya uzalishaji
- Miradi isiyohitaji ujenzi: Hakuna hatua ya ujenzi, hudumisha faili moja kwa moja

## Miongozo ya Rufaa za Kuchukua Mabadiliko (Pull Requests)

### Muundo wa Kichwa

Tumia vichwa wazi, vinavyoelezea maeneo ya mabadiliko:
- `[Quiz-app] Ongeza mtihani mpya kwa somo X`
- `[Lesson-3] Rekebisha tahajia katika mradi wa terrarium`
- `[Translation] Ongeza tafsiri ya Kihispania kwa somo 5`
- `[Docs] Sasisha maelekezo ya kuanzisha`

### Vyakati Vinavyohitajika

Kabla ya kuwasilisha PR:

1. **Ubora wa Msimbo**:
   - Endesha `npm run lint` katika saraka zilizoathirika
   - Rekebisha makosa na onyo zote za lint

2. **Uhakiki wa Ujenzi**:
   - Endesha `npm run build` inapohitajika
   - Hakikisha hakuna makosa ya ujenzi

3. **Uhakiki wa Viungo**:
   - Jaribu viungo vyote vya markdown
   - Thibitisha marejeo ya picha zinafanya kazi

4. **Ukaguzi wa Yaliyomo**:
   - Soma kwa makini kwa makosa ya tahajia na sarufi
   - Hakikisha mifano ya msimbo ni sahihi na ya kielimu
   - Hakikisha tafsiri zinahifadhi maana asilia

### Masharti ya Michango

- Kubali Microsoft CLA (ukaguzi wa moja kwa moja kwa PR ya kwanza)
- Fuata [Sheria za Maadili za Chanzo Huria za Microsoft](https://opensource.microsoft.com/codeofconduct/)
- Angalia [CONTRIBUTING.md](./CONTRIBUTING.md) kwa miongozo ya kina
- Taja nambari za masuala katika maelezo ya PR inapowezekana

### Mchakato wa Ukaguzi

- PR hurejelewa na waendelezaji na jamii
- Uwazi wa elimu unaangaziwa
- Mifano ya msimbo inapaswa kufuata mbinu bora za sasa
- Tafsiri hurejelewa kwa usahihi na utamaduni unaofaa

## Mfumo wa Tafsiri

### Tafsiri ya Moja kwa Moja (Automated)

- Inatumia GitHub Actions na mtiririko wa co-op-translator
- Inatafsiri hadi lugha zaidi ya 50 moja kwa moja
- Faili za chanzo ziko katika saraka kuu
- Faili za tafsiri ziko katika saraka za `translations/{language-code}/`

### Kuongeza Maboresho ya Tafsiri Kwa Mkono

1. Tafuta faili katika `translations/{language-code}/`
2. Fanya maboresho huku ukihifadhi muundo
3. Hakikisha mifano ya msimbo inabaki kutumika
4. Jaribu yaliyomo ya mitihani iliyotafsiriwa

### Metadata ya Tafsiri

Faili za tafsiri zina kichwa cha metadata:
```markdown
<!--
CO_OP_TRANSLATOR_METADATA:
{
  "original_hash": "...",
  "translation_date": "...",
  "source_file": "...",
  "language_code": "..."
}
-->
```

## Kurekebisha na Kutatua Matatizo

### Changamoto Zaidi Zaidi

**App ya Quiz haianzi**:
- Hakiki toleo la Node.js (inashauriwa v14+)
- Futa `node_modules` na `package-lock.json`, endesha tena `npm install`
- Angalia migongano ya bandari (kawaida: Vite hutumia bandari 5173)

**Server ya API haianzi**:
- Hakiki toleo la Node.js linakidhi (node >=10)
- Angalia kama bandari tayari inatumika
- Hakikisha utegemezi wote umetolewa kwa `npm install`

**Upanuzi wa kivinjari hauanziki**:
- Hakiki manifest.json imepandishwa vema
- Angalia console ya kivinjari kwa makosa
- Fuata maelekezo ya usanidi wa upanuzi wa kivinjari

**Matatizo ya Mradi wa Mazungumzo wa Python**:
- Hakikisha kifurushi cha OpenAI kimesakinishwa: `pip install openai`
- Hakiki kuwa mabadiliko ya mazingira ya GITHUB_TOKEN yamewekwa
- Hakiki vibali vya ufikiaji kwa GitHub Models

**Docsify haisikilizi nyaraka**:
- Sakinisha docsify-cli ulimwenguni: `npm install -g docsify-cli`
- Endesha kutoka saraka kuu ya hazina
- Hakiki `docs/_sidebar.md` ipo

### Vidokezo vya Mazingira ya Maendeleo

- Tumia VS Code na upanuzi wa Live Server kwa miradi ya HTML
- Sakinisha upanuzi za ESLint na Prettier kwa mtindo thabiti
- Tumia DevTools wa kivinjari kwa kupata na kutatua makosa ya JavaScript
- Kwa miradi ya Vue, sakinisha upanuzi wa Vue DevTools kivinjari

### Mambo ya Kujali Kuhusu Utendaji

- Idadi kubwa ya faili za tafsiri (za lugha 50+) huongeza ukubwa wa nakala kamili
- Tumia nakala ya chini (shallow) ikiwa unafanya kazi tu kwa yaliyomo: `git clone --depth 1`
- Epuka tafutiza za tafsiri wakati unafanya kazi na yaliyomo ya Kiingereza
- Mienendo ya ujenzi inaweza kuwa polepole mwanzoni (npm install, ujenzi wa Vite)

## Masuala ya Usalama

### Mabadiliko ya Mazingira

- Funguo za API hazipaswi kuwekwa moja kwa moja katika hazina
- Tumia faili za `.env` (zipo katika `.gitignore`)
- Elezea mabadiliko ya mazingira yanayohitajika katika README za miradi

### Miradi ya Python

- Tumia mazingira ya pekee: `python -m venv venv`
- Sasisha utegemezi mara kwa mara
- Tokeni za GitHub zinapaswa kuwa na vibali vidogo vinavyotakiwa tu

### Ufikiaji wa GitHub Models

- Mipangilio ya Ufikiaji wa Kibinafsi (PAT) inahitajika kwa GitHub Models
- Tokeni ziwe katika mabadiliko ya mazingira
- Kamwe usiweka tokeni au nyaraka katika hazina

## Vidokezo Zaidi

### Hadhira Lengwa

- Wananchi wapya kabisa katika maendeleo ya wavuti
- Wanafunzi na waelimishaji wa kujifunza peke yao
- Walimu wanaotumia mtaala darasani
- Yaliyomo yamebuniwa kwa kupatikana na kukuza hatua kwa hatua ujuzi

### Falsafa ya Elimu

- Mbinu ya kujifunza kwa miradi
- Ukaguzi wa mara kwa mara wa maarifa (maswali)
- Mazoezi ya kuandika msimbo kwa vitendo
- Mifano ya matumizi halisi ya dunia ya kweli
- Kuzingatia misingi kabla ya mifumo ngumu

### Matengenezo ya Hazina

- Jamii hai ya wanafunzi na wasaidizi
- Sasisho za mara kwa mara za utegemezi na yaliyomo
- Masuala na majadiliano yanatazamwa na watunzaji
- Sasisho za tafsiri zimepangwa moja kwa moja kupitia GitHub Actions

### Rasilimali Zinazohusiana

- [Moduli za Microsoft Learn](https://docs.microsoft.com/learn/)
- [Rasilimali za Kitovu cha Mwanafunzi](https://docs.microsoft.com/learn/student-hub/)
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) inashauriwa kwa wanafunzi
- Kozi zingine: AI ya kuzalisha, Sayansi ya Data, ML, na mtaala wa IoT zinapatikana

### Kufanya kazi na Miradi Mahususi

Kwa maelekezo ya kina juu ya miradi binafsi, rejea faili za README katika:
- `quiz-app/README.md` - Programu ya mtihani ya Vue 3
- `7-bank-project/README.md` - Programu ya benki yenye uthibitishaji
- `5-browser-extension/README.md` - Maendeleo ya upanuzi wa kivinjari
- `6-space-game/README.md` - Maendeleo ya mchezo wa Canvas
- `9-chat-project/README.md` - Mradi wa msaidizi wa mazungumzo wa AI

### Muundo wa Monorepo

Ingawa sio monorepo ya kawaida, hazina hii ina miradi huru mingi:
- Kila somo limejitegemea
- Miradi haishiriki utegemezi
- Fanya kazi kwenye miradi binafsi bila kuathiri mingine
- Nakili hazina nzima kwa uzoefu kamili wa mtaala

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Kinyang'anyiro**:
Hati hii imetafsiriwa kwa kutumia huduma ya tafsiri ya AI [Co-op Translator](https://github.com/Azure/co-op-translator). Wakati tunajitahidi kwa usahihi, tafadhali fahamu kwamba tafsiri za kiotomati zinaweza kuwa na makosa au upotoshaji. Hati ya asili katika lugha yake ya asili inapaswa kuchukuliwa kama chanzo cha mamlaka. Kwa taarifa muhimu, tafsiri ya mtaalamu wa binadamu inapendekezwa. Hatubeba jukumu la kutokea kwa kutoelewana au tafsiri potofu kutokana na matumizi ya tafsiri hii.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->