# AGENTS.md

## Pregled projekta

To je učni učni načrt za poučevanje osnov spletnega razvoja za začetnike. Učni načrt je obsežen 12-tedenski tečaj, ki so ga razvili Microsoft Cloud Advocates, in vsebuje 24 praktičnih lekcij o JavaScriptu, CSS in HTML.

### Ključne sestavine

- **Izobraževalna vsebina**: 24 strukturiranih lekcij, organiziranih v modulih na osnovi projektov
- **Praktični projekti**: Terarij, Tipkovniška igra, Razširitev brskalnika, Vesoljska igra, Bančna aplikacija, Urejevalnik kode in AI klepetalni pomočnik
- **Interaktivni kvizi**: 48 kvizov s 3 vprašanji vsak (pred in po lekciji)
- **Podpora za več jezikov**: Avtomatizirani prevodi za več kot 50 jezikov preko GitHub Actions
- **Tehnologije**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (za AI projekte)

### Arhitektura

- Učni skladišče z strukturo na osnovi lekcij
- Vsaka mapa lekcije vsebuje README, primere kode in rešitve
- Samostojni projekti v ločenih imenikih (quiz-app, različni lekcijski projekti)
- Sistem za prevajanje z uporabo GitHub Actions (co-op-translator)
- Dokumentacija, postrežena preko Docsify in dostopna kot PDF

## Ukazi za nastavitev

To skladišče je primarno namenjeno za uživanje izobraževalne vsebine. Za delo z določenimi projekti:

### Nastavitev glavnega skladišča

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Nastavitev Quiz App (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Zaženi razvojni strežnik
npm run build      # Zgradi za produkcijo
npm run lint       # Zaženi ESLint
```

### API projekta Banka (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # Zaženi API strežnik
npm run lint       # Zaženi ESLint
npm run format     # Oblikuj s Prettierjem
```

### Projekti razširitev brskalnika

```bash
cd 5-browser-extension/solution
npm install
# Upoštevajte navodila za nalaganje razširitev, specifična za brskalnik
```

### Projekti vesoljske igre

```bash
cd 6-space-game/solution
npm install
# Odprite index.html v brskalniku ali uporabite Live Server
```

### Projekt klepeta (Python Backend)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Nastavite okoljsko spremenljivko GITHUB_TOKEN
python api.py
```

## Razvojni potek dela

### Za prispevatele vsebine

1. **Razvezi skladišče (fork)** v svoj GitHub račun
2. **Kloniraj svoj fork** lokalno
3. **Ustvari nov podal (branch)** za svoje spremembe
4. Naredi spremembe v vsebini lekcij ali primerih kode
5. Testiraj spremembe kode v ustreznih mapah projektov
6. Pošlji pull requeste v skladu z navodili za prispevanje

### Za učence

1. Razvezi ali kloniraj skladišče
2. Pomakni se zaporedno skozi mape lekcij
3. Preberi README datoteke za vsako lekcijo
4. Reši predlečnične kvize na https://ff-quizzes.netlify.app/web/
5. Delaj skozi primere kode v mapah lekcij
6. Dokončaj naloge in izzive
7. Reši postlečnične kvize

### Živ razvoj

- **Dokumentacija**: Zaženi `docsify serve` v korenu projekta (port 3000)
- **Quiz App**: Zaženi `npm run dev` v mapi quiz-app
- **Projekti**: Uporabi razširitev VS Code Live Server za HTML projekte
- **API projekti**: Zaženi `npm start` v ustreznih API mapah

## Navodila za testiranje

### Testiranje Quiz App

```bash
cd quiz-app
npm run lint       # Preveri težave s slogom kode
npm run build      # Preveri, ali je gradnja uspešna
```

### Testiranje Bank API

```bash
cd 7-bank-project/api
npm run lint       # Preveri težave s slogom kode
node server.js     # Preveri, ali strežnik zažene brez napak
```

### Splošni pristop k testiranju

- To je učni repozitorij brez celovitega avtomatskega testiranja
- Ročno testiranje se osredotoča na:
  - Primeri kode tečejo brez napak
  - Povezave v dokumentaciji delujejo pravilno
  - Projekti se uspešno zgradijo
  - Primeri sledijo najboljšim praksam

### Preverjanje pred oddajo

- Zaženi `npm run lint` v mapah z datoteko package.json
- Preveri veljavnost povezav v markdownu
- Testiraj primere kode v brskalniku ali Node.js
- Preveri, da prevodi ohranjajo pravilno strukturo

## Smernice za stil kode

### JavaScript

- Uporaba sodobne sintakse ES6+
- Sledenje standardnim ESLint konfiguracijam, podanim v projektih
- Uporaba pomenljivih imen spremenljivk in funkcij za lažje razumevanje
- Dodajanje komentarjev za pojasnitev konceptov za učence
- Formatiranje z uporabo Prettier kjer je konfigurirano

### HTML/CSS

- Semantični elementi HTML5
- Principi odzivnega oblikovanja
- Jasne konvencije poimenovanja razredov
- Komentarji, ki pojasnjujejo CSS tehnike za učence

### Python

- Slediti smernicam sloga PEP 8
- Jasni, izobraževalni primeri kode
- Tipiziranje (type hints) kjer je koristno za učenje

### Dokumentacija v Markdownu

- Jasna hierarhija naslovov
- Bloki kode z navedbo jezika
- Povezave do dodatnih virov
- Posnetki zaslona in slike v mapah `images/`
- Alt besedilo za slike zaradi dostopnosti

### Organizacija datotek

- Lekcije označene zaporedno (1-getting-started-lessons, 2-js-basics itd.)
- Vsak projekt ima mape `solution/` in pogosto `start/` ali `your-work/`
- Slike so shranjene v lekcijsko specifičnih mapah `images/`
- Prevodi v strukturi `translations/{jezikovna-koda}/`

## Sestavljanje in nameščanje

### Namestitev Quiz App (Azure Static Web Apps)

quiz-app je konfiguriran za nameščanje v Azure Static Web Apps:

```bash
cd quiz-app
npm run build      # Ustvari mapo dist/
# Izvede namestitev prek GitHub Actions poteka ob potisku na main
```

Konfiguracija Azure Static Web Apps:
- **Lokacija aplikacije**: `/quiz-app`
- **Izhodna lokacija**: `dist`
- **Delovni tok**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### Generiranje PDF dokumentacije

```bash
npm install                    # Namestite docsify-to-pdf
npm run convert               # Ustvari PDF iz docs
```

### Dokumentacija Docsify

```bash
npm install -g docsify-cli    # Namestite Docsify globalno
docsify serve                 # Strežnik na localhost:3000
```

### Gradnje specifične za projekte

Vsaka mapa projekta lahko ima lasten postopek gradnje:
- Vue projekti: `npm run build` ustvari produkcijske pakete
- Statični projekti: brez koraka gradnje, postreže se datoteke neposredno

## Smernice za pull requeste

### Oblika naslova

Uporabi jasne, opisne naslove, ki označujejo področje spremembe:
- `[Quiz-app] Dodaj nov kviz za lekcijo X`
- `[Lesson-3] Popravi tipkarsko napako v projektu terarij`
- `[Translation] Dodaj španski prevod za lekcijo 5`
- `[Docs] Posodobi navodila za nastavitev`

### Zahtevani pregledi

Pred oddajo PR:

1. **Kakovost kode**:
   - Zaženi `npm run lint` v prizadetih projektnih mapah
   - Odpravi vse napake in opozorila linterja

2. **Preverjanje gradnje**:
   - Zaženi `npm run build` če je potrebno
   - Prepričaj se, da ni napak pri gradnji

3. **Preverjanje povezav**:
   - Testiraj vse markdown povezave
   - Preveri delovanje referenc slik

4. **Pregled vsebine**:
   - Preveri pravopis in slovnico
   - Zagotovi, da so primeri kode pravilni in poučni
   - Preveri, da prevodi ohranjajo originalni pomen

### Zahteve za prispevanje

- Strinjanje z Microsoft CLA (avtomatizirana kontrola ob prvem PR)
- Sledenje [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/)
- Glej [CONTRIBUTING.md](./CONTRIBUTING.md) za podrobna navodila
- Navedi številke issue-ov v opisu PR, če je primerno

### Pregledni postopek

- PR-je pregledajo vzdrževalci in skupnost
- Prioriteta je izobraževalna jasnost
- Primeri kode sledijo najboljšim trenutnim praksam
- Prevodi se pregledajo za natančnost in kulturno ustreznost

## Sistem prevajanja

### Avtomatizirani prevod

- Uporablja GitHub Actions z delovnim tokom co-op-translator
- Samodejno prevaja v več kot 50 jezikov
- Izvorne datoteke so v glavnih direktorijih
- Prevedene datoteke v `translations/{jezikovna-koda}/`

### Dodajanje ročnih izboljšav prevodov

1. Najdi datoteko v `translations/{jezikovna-koda}/`
2. Naredi izboljšave, ob ohranitvi strukture
3. Poskrbi, da primeri kode ostanejo funkcionalni
4. Testiraj lokalizirano vsebino kvizov

### Metapodatki prevodov

Prevedene datoteke vključujejo meta glavo:
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

## Razhroščevanje in odpravljanje težav

### Pogoste težave

**Quiz app ne zažene**:
- Preveri verzijo Node.js (priporočena v14+)
- Izbriši `node_modules` in `package-lock.json`, ponovno zaženi `npm install`
- Preveri morebitne konflikte vrat (privzeto: Vite uporablja port 5173)

**API strežnik se ne zažene**:
- Preveri verzijo Node.js (node >=10)
- Preveri, če je port že v uporabi
- Poskrbi, da so vse odvisnosti nameščene z `npm install`

**Razširitev brskalnika se ne naloži**:
- Preveri, da je manifest.json pravilno oblikovan
- Preveri konzolo brskalnika za napake
- Sledi navodilom za namestitev specifičnim za brskalnik

**Težave s projektom klepeta v Pythonu**:
- Namesti paket OpenAI: `pip install openai`
- Preveri, da je okoljska spremenljivka GITHUB_TOKEN nastavljena
- Preveri dovoljenja za dostop do GitHub modelov

**Docsify ne postreže dokumentacije**:
- Namesti docsify-cli globalno: `npm install -g docsify-cli`
- Zaženi v korenski mapi skladišča
- Preveri obstoj `docs/_sidebar.md`

### Nasveti za razvojno okolje

- Uporabljaj VS Code z razširitvijo Live Server za HTML projekte
- Namesti razširitve ESLint in Prettier za skladno oblikovanje
- Uporabljaj DevTools brskalnika za razhroščevanje JavaScript-a
- Za Vue projekte namesti Vue DevTools brskalniško razširitev

### Upoštevanje zmogljivosti

- Veliko število prevedenih datotek (več kot 50 jezikov) pomeni velike polne klone
- Uporabi plitki klon, če delaš le na vsebini: `git clone --depth 1`
- Izključi prevode iz iskanj, ko delaš na angleški vsebini
- Procesi gradnje so lahko počasnejši ob prvem zagonu (npm install, Vite build)

## Varnostni vidiki

### Okoljske spremenljivke

- Ključi API ne smejo biti nikoli vključeni v repozitorij
- Uporabljaj `.env` datoteke (že vključene v `.gitignore`)
- Dokumentiraj potrebne okoljske spremenljivke v README-jih projektov

### Python projekti

- Uporabljaj virtualna okolja: `python -m venv venv`
- Posodabljaj odvisnosti
- GitHub tokeni naj imajo minimalne potrebne pravice

### Dostop do GitHub modelov

- Za GitHub modele so potrebni osebni dostopni tokeni (PAT)
- Tokeni morajo biti shranjeni kot okoljske spremenljivke
- Tokenov ali poverilnic nikoli ne vključi v repozitorij

## Dodatne opombe

### Ciljna publika

- Popolni začetniki v spletni razvoj
- Študenti in samouki
- Učitelji, ki uporabljajo učni načrt v razredih
- Vsebina je zasnovana za dostopnost in postopno gradnjo veščin

### Izobraževalna filozofija

- Pristop učenja na osnovi projektov
- Pogoste preveritve znanja (kvizi)
- Praktične vaje programiranja
- Primeri uporabe iz realnega sveta
- Osredotočenost na osnove pred ogrodji

### Vzdrževanje skladišča

- Aktivna skupnost učencev in prispevajočih
- Redne posodobitve odvisnosti in vsebine
- Vzdrževalci nadzorujejo težave in razprave
- Prevodi se posodabljajo avtomatsko preko GitHub Actions

### Sorodni viri

- [Moduli Microsoft Learn](https://docs.microsoft.com/learn/)
- [Viri Student Hub](https://docs.microsoft.com/learn/student-hub/)
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) priporočeno za učence
- Dodatni tečaji: Generativna AI, Data Science, ML, IoT učni načrti na voljo

### Delo z določenimi projekti

Za podrobna navodila o posameznih projektih glej README datoteke v:
- `quiz-app/README.md` - Vue 3 aplikacija kviza
- `7-bank-project/README.md` - Bančna aplikacija z avtentikacijo
- `5-browser-extension/README.md` - Razvoj razširitve brskalnika
- `6-space-game/README.md` - Razvoj igre na platnu (Canvas)
- `9-chat-project/README.md` - Projekt AI klepetalnega pomočnika

### Struktura monorepo

Čeprav ni tradicionalni monorepo, to skladišče vsebuje več samostojnih projektov:
- Vsaka lekcija je samostojna
- Projekti ne delijo odvisnosti
- Delo na posameznih projektih brez vpliva na druge
- Kloniraj celotno skladišče za celotno učni izkušnjo

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Omejitev odgovornosti**:  
Ta dokument je bil preveden z uporabo storitve za prevajanje z umetno inteligenco [Co-op Translator](https://github.com/Azure/co-op-translator). Čeprav si prizadevamo za točnost, vas opozarjamo, da avtomatizirani prevodi lahko vsebujejo napake ali netočnosti. Izvirni dokument v njegovem izvirnem jeziku je treba obravnavati kot avtoritativni vir. Za ključne informacije priporočamo strokovni človeški prevod. Nismo odgovorni za morebitna nesporazume ali nepravilne interpretacije, ki izhajajo iz uporabe tega prevoda.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->