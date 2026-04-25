# AGENTS.md

## Projekti ülevaade

See on hariduslik õppekava hoidla veebiarenduse aluste õpetamiseks algajatele. Õppekava on Microsoft Cloud Advocatesi poolt välja töötatud põhjalik 12-nädalane kursus, mis sisaldab 24 praktilist õppetundi JavaScripti, CSSi ja HTMLi kohta.

### Peamised komponendid

- **Hariduslik sisu**: 24 struktureeritud õppetundi projektipõhistes moodulites
- **Praktilised projektid**: Terrarium, Trükkimismäng, Brauserilaiendus, Kosmosemäng, Pangaäpp, Koodiredaktor ja AI vestlusassistent
- **Interaktiivsed viktoriinid**: 48 viktoriini, igaühes 3 küsimust (enne ja pärast õppetundi hindamised)
- **Mitmekeelne tugi**: 50+ keele automaatne tõlge GitHub Actions abil
- **Tehnoloogiad**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (AI projektide jaoks)

### Arhitektuur

- Hariduslik hoidla õppetundide struktuuriga
- Igas õppetunni kaustas on README, koodinäited ja lahendused
- Eraldiseisvad projektid eraldi kataloogides (quiz-app, erinevad õppetunniprojektid)
- Tõlkesüsteem GitHub Actions (co-op-translator) abil
- Dokumentatsioon esitatakse Docsify kaudu ja on saadaval PDF-formaadis

## Paigaldus käsud

See hoidla on mõeldud peamiselt haridussisu tarbimiseks. Spetsiifiliste projektidega töötamiseks:

### Peamise hoidla seadistamine

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Quiz App seadistamine (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Käivita arendusserver
npm run build      # Ehita tootmiseks
npm run lint       # Käivita ESLint
```

### Pangaprojekti API (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # Käivita API server
npm run lint       # Käivita ESLint
npm run format     # Vorminda Prettieriga
```

### Brauserilaienduse projektid

```bash
cd 5-browser-extension/solution
npm install
# Järgige brauserispetsiifilisi laienduse laadimise juhiseid
```

### Kosmosemängu projektid

```bash
cd 6-space-game/solution
npm install
# Ava index.html brauseris või kasuta Live Serverit
```

### Vestlusprojekti tagaplaan (Python)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Määra keskkonnamuutuja GITHUB_TOKEN
python api.py
```

## Arendustöövoog

### Sisuloomele

1. **Forki hoidla** oma GitHub kontole
2. **Klooni oma fork lokaalselt**
3. **Loo uus haru** oma muudatuste jaoks
4. Tee muudatusi õppe sisu või koodinäidetes
5. Testi muudatusi vastavates projektikaustades
6. Esita pull request vastavalt panustamise juhistele

### Õppijatele

1. Forki või klooni hoidla
2. Liigu õppetundide kaustades järjekorras
3. Loe iga õppetunni README faile
4. Täida eelnevad viktoriinid aadressil https://ff-quizzes.netlify.app/web/
5. Töötle läbi õppetunni koodinäited
6. Täida ülesanded ja väljakutsed
7. Tee lõppviktoriinid

### Reaalajas arendus

- **Dokumentatsioon**: käivita juurkataloogis `docsify serve` (port 3000)
- **Quiz App**: käivita `npm run dev` quiz-app kataloogis
- **Projektid**: kasuta VS Code Live Server laiendust HTML projektide jaoks
- **API projektid**: käivita vastavates API kaustades `npm start`

## Testimisjuhised

### Quiz App testimine

```bash
cd quiz-app
npm run lint       # Kontrolli koodistiili probleeme
npm run build      # Kontrolli, kas ehitus õnnestub
```

### Panga API testimine

```bash
cd 7-bank-project/api
npm run lint       # Kontrolli koodi stiiliprobleeme
node server.js     # Kontrolli, et server käivitub ilma vigadeta
```

### Üldine testimisviis

- See on hariduslik hoidla ilma põhjalike automatiseeritud testideta
- Käsitsi testimine keskendub:
  - Koodinäited töötavad ilma vigadeta
  - Dokumentatsiooni lingid töötavad korrektselt
  - Projektide ehitused õnnestuvad
  - Näited järgivad parimaid tavasid

### Enne esitamist kontroll

- Käivita kataloogides, kus on package.json, `npm run lint`
- Kontrolli markdown linkide korrasolekut
- Testi koodinäiteid brauseris või Node.js-s
- Veendu, et tõlked säilitavad õige struktuuri

## Koodi stiili juhised

### JavaScript

- Kasuta kaasaegset ES6+ süntaksit
- Järgi projektides olevaid standardseid ESLint konfiguratsioone
- Kasuta tähenduslikke muutujate ja funktsioonide nimesid selguse huvides
- Lisa kommentaare, mis selgitavad mõisteid õppijatele
- Vorminda koodi Prettieriga, kus see on seadistatud

### HTML/CSS

- Semantiline HTML5 elementide kasutus
- Reageeriv disainiprintsiip
- Selged klassinimede reeglid
- Kommentaarid, mis selgitavad CSS tehnikaid õppijatele

### Python

- Järgi PEP 8 stiilijuhiseid
- Selged ja hariduslikud koodinäited
- Kasuta tüübiviiteid, kus õppimiseks kasulik

### Markdown dokumentatsioon

- Selge pealkirjade hierarhia
- Koodiplokid koos keelespetsifikatsiooniga
- Lingid lisamaterjalidele
- Ekraanipildid ja pildid `images/` kaustades
- Piltide jaoks alternatiivtekst ligipääsetavuse tagamiseks

### Failide organiseerimine

- Õppetunnid nummerdatud järjestikku (1-getting-started-lessons, 2-js-basics jne)
- Igal projektil on `solution/` ja sageli `start/` või `your-work/` kaustad
- Pildid salvestatud õppetundide spetsiifilistesse `images/` kaustadesse
- Tõlked `translations/{language-code}/` struktuuris

## Ehitamine ja juurutamine

### Quiz App juurutamine (Azure Static Web Apps)

Quiz-app on konfigureeritud Azure Static Web Apps juurutamiseks:

```bash
cd quiz-app
npm run build      # Loob dist/ kausta
# Paigaldab GitHub Actions töövoo kaudu, kui tehakse push main harusse
```

Azure Static Web Apps konfiguratsioon:
- **Rakenduse asukoht**: `/quiz-app`
- **Väljundasukoht**: `dist`
- **Töövoog**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### Dokumentatsiooni PDF genereerimine

```bash
npm install                    # Paigalda docsify-to-pdf
npm run convert               # Genereeri PDF docsist
```

### Docsify dokumentatsioon

```bash
npm install -g docsify-cli    # Paigalda Docsify ülemaailmselt
docsify serve                 # Serveeri aadressil localhost:3000
```

### Projekti-spetsiifilised ehitused

Igal projekti kaustal võib olla oma ehitusprotsess:
- Vue projektid: `npm run build` loob tootmispaketid
- Staatilised projektid: eraldi ehitusetappi ei ole, faile serveeritakse otse

## Pull requesti juhised

### Pealkirja formaat

Kasuta selgeid ja kirjeldavaid pealkirju, mis näitavad muudatuse valdkonda:
- `[Quiz-app] Lisa uus viktoriin õppetunnile X`
- `[Lesson-3] Paranda kirjaviga terrarium projekti juures`
- `[Translation] Lisa hispaania tõlge õppetunnile 5`
- `[Docs] Uuenda paigaldusjuhiseid`

### Nõutavad kontrollid

Enne PR-i esitamist:

1. **Koodi kvaliteet**:
   - Käivita mõjutatud projektikaustades `npm run lint`
   - Paranda kõik lintimise vead ja hoiatused

2. **Ehituse kontroll**:
   - Käivita `npm run build`, kui see kehtib
   - Veendu, et ehitus ei anna vigu

3. **Linkide kontroll**:
   - Testi kõiki markdown linke
   - Kontrolli pildi viidete toimimist

4. **Sisu ülevaade**:
   - Tee õigekirja ja grammatika ülevaade
   - Veendu, et koodinäited on korrektsed ja hariduslikud
   - Kontrolli, et tõlked säilitavad algse tähenduse

### Panustamise nõuded

- Nõustu Microsoft CLA-ga (automaatselt esimese PR-i juures)
- Järgi [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/)
- Vaata [CONTRIBUTING.md](./CONTRIBUTING.md) üksikasjalike juhiste jaoks
- Viita PR kirjelduses vajadusel issue numbritele

### Ülevaatusprotsess

- PR-e vaatavad läbi hoidla hooldajad ja kogukond
- Eesmärk on haridusliku selguse tagamine
- Koodinäited peavad järgima parimaid tänaseid tavasid
- Tõlked üle vaadatakse täpsuse ja kultuurilise sobivuse osas

## Tõlkesüsteem

### Automaatne tõlge

- Kasutab GitHub Actions koos co-op-translator töövooga
- Tõlgib automaatselt 50+ keelde
- Algfailid peamistest kataloogidest
- Tõlgitud failid `translations/{language-code}/` kataloogides

### Käsitsi tõlkete parandused

1. Leia fail `translations/{language-code}/` kataloogis
2. Tee parandused, hoides struktuuri muutumatuna
3. Veendu, et koodinäited jäävad toimima
4. Testi lokaliseeritud viktoriini sisu

### Tõlke metaandmed

Tõlgitud failidel on metaandmete päis:
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

## Silumine ja probleemide lahendamine

### Levinud probleemid

**Quiz app ei käivitu**:
- Kontrolli Node.js versiooni (soovituslik v14+)
- Kustuta `node_modules` ja `package-lock.json`, käivita uuesti `npm install`
- Kontrolli portide konflikte (vaikimisi: Vite kasutab porti 5173)

**API server ei käivitu**:
- Kontrolli, et Node.js versioon on minimaalne (node >=10)
- Veendu, et port ei ole juba kasutusel
- Kontrolli, et kõik sõltuvused on paigaldatud `npm install` abil

**Brauserilaiend ei laaditu**:
- Kontrolli, et manifest.json on korrektselt vormindatud
- Vaata brauseri konsooli vigade jaoks
- Järgi brauserispetsiifilisi laienduste paigaldusjuhiseid

**Python vestlusprojekti probleemid**:
- Veendu, et OpenAI pakett on paigaldatud: `pip install openai`
- Kontrolli, et GITHUB_TOKEN keskkonnamuutuja on määratud
- Vaata GitHub Models juurde pääsemise õigusi

**Docsify ei serveeri dokumente**:
- Paigalda docsify-cli globaalset: `npm install -g docsify-cli`
- Käivita hoidla juurkataloogist
- Veendu, et `docs/_sidebar.md` fail on olemas

### Arenduskeskkonna nõuanded

- Kasuta VS Code Live Server laiendust HTML projektide jaoks
- Paigalda ESLint ja Prettier laiendused konsistentseks vormindamiseks
- Kasuta brauseri DevTools JavaScripti silumiseks
- Vue projektide jaoks installi Vue DevTools brauserilaiendus

### Tulemuslikkuse kaalutlused

- Suur hulk tõlgitud faile (50+ keelt) teeb täielikud kloonid mahukaks
- Kasuta sumbunud klooni, kui töötad ainult sisuga: `git clone --depth 1`
- Väldi tõlgete otsinguid, kui töötad ingliskeelse sisuga
- Ehitusteenused võivad esimesel käivitamisel olla aeglased (npm install, Vite build)

## Turvanõuded

### Keskkonnamuutujad

- API võtmeid ei tohi kunagi hoidlas hoida
- Kasuta `.env` faile (mida on juba `.gitignore`-s)
- Dokumenteeri vajalikud keskkonnamuutujad projektide README-des

### Python projektid

- Kasuta virtuaalkeskkonda: `python -m venv venv`
- Hoia sõltuvused värskendatud
- GitHub tokenitel peaksid olema minimaalsed õigused

### GitHub Models ligipääs

- Isiklikud ligipääsu tokenid (PAT) on vajalikud GitHub Models jaoks
- Tokenid salvestada keskkonnamuutujatena
- Tokenid ega mandaadid ei tohi kunagi hoidlasse jõuda

## Lisamärkused

### Sihtgrupp

- Täielikud algajad veebiarenduses
- Õpilased ja iseseisvad õppijad
- Õpetajad, kes kasutavad õppekava klassiruumis
- Sisu on loodud ligipääsetavaks ja samm-sammuliseks oskuste kasvatamiseks

### Haridusfilosoofia

- Projektipõhine õppimisviis
- Sageli teadmiste kontrollid (viktoriinid)
- Praktiseerivad kodeerimise harjutused
- Reaalsed näited rakendustest
- Keskendutakse alustele enne raamistikke

### Hoidla hooldus

- Aktiivne õppijate ja panustajate kogukond
- Regulaarne sõltuvuste ja sisu uuendamine
- Probleemid ja arutelud hooldajate jälgimisel
- Tõlkeuuendused automatiseeritud GitHub Actions kaudu

### Seotud ressursid

- [Microsoft Learn moodulid](https://docs.microsoft.com/learn/)
- [Student Hub ressursid](https://docs.microsoft.com/learn/student-hub/)
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) soovitatav õppijatele
- Täiendavad kursused: Generatiivne AI, Andmeteadus, ML, IoT õppekavad saadaval

### Töö spetsiifiliste projektidega

Detailseid juhiseid üksikute projektide jaoks leiad nende README failidest:
- `quiz-app/README.md` - Vue 3 viktoriini rakendus
- `7-bank-project/README.md` - Pangarakendus autentimisega
- `5-browser-extension/README.md` - Brauserilaienduse arendus
- `6-space-game/README.md` - Canvas-põhine mänguarendus
- `9-chat-project/README.md` - AI vestlusassistiendi projekt

### Monorepo struktuur

Kuigi see ei ole traditsiooniline monorepo, sisaldab see hoidla mitmeid iseseisvaid projekte:
- Iga õppetund on eraldiseisev
- Projektid ei jaga sõltuvusi
- Töötada saab üksikute projektidega mõjutamata teisi
- Klooni kogu hoidla tervikliku õppekava kogemiseks

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Vastutusest loobumine**:
See dokument on tõlgitud kasutades tehisintellekti tõlketeenust [Co-op Translator](https://github.com/Azure/co-op-translator). Kuigi me püüame täpsust, palun arvestage, et automaatsed tõlked võivad sisaldada vigu või ebatäpseid osi. Originaaldokument selle emakeeles tuleks pidada autoriteetseks allikaks. Olulise teabe puhul soovitatakse kasutada professionaalset inimtõlget. Me ei vastuta selle tõlke kasutamisest tingitud arusaamatuste ega väärarusaamade eest.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->