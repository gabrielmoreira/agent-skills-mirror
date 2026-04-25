# AGENTS.md

## Pregled projekta

Ovo je repozitorij nastavnog programa za podučavanje osnova web razvoja početnicima. Nastavni plan i program je sveobuhvatan tečaj u trajanju od 12 tjedana koji su razvili Microsoft Cloud Advocates, a sadrži 24 praktične lekcije koje pokrivaju JavaScript, CSS i HTML.

### Ključne komponente

- **Nastavni sadržaj**: 24 strukturirane lekcije organizirane u module temeljene na projektima
- **Praktični projekti**: Terrarij, Igra tipkanja, Proširenje za preglednik, Svemirska igra, Bankarska aplikacija, Code Editor i AI Chat asistent
- **Interaktivni kvizovi**: 48 kvizova sa po 3 pitanja svaki (procjena prije i nakon lekcije)
- **Višestruka podrška jezika**: Automatski prijevodi na 50+ jezika putem GitHub Actions
- **Tehnologije**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (za AI projekte)

### Arhitektura

- Edukativni repozitorij sa strukturom baziranom na lekcijama
- Svaka mapa lekcije sadrži README, primjere koda i rješenja
- Samostalni projekti u posebnim direktorijima (quiz-app, razni projektni lekcijski direktoriji)
- Sustav prevođenja pomoću GitHub Actions (co-op-translator)
- Dokumentacija poslužena putem Docsify i dostupna kao PDF

## Komande za postavljanje

Ovaj repozitorij je primarno namijenjen za konzumaciju edukativnog sadržaja. Za rad s određenim projektima:

### Postavljanje glavnog repozitorija

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Postavljanje Quiz aplikacije (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Pokreni razvojni poslužitelj
npm run build      # Izgradi za produkciju
npm run lint       # Pokreni ESLint
```

### Bankarski projekt API (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # Pokreni API poslužitelj
npm run lint       # Pokreni ESLint
npm run format     # Formatiraj s Prettierom
```

### Projekti proširenja za preglednik

```bash
cd 5-browser-extension/solution
npm install
# Slijedite upute za učitavanje ekstenzija specifičnih za preglednik
```

### Projekti svemirske igre

```bash
cd 6-space-game/solution
npm install
# Otvorite index.html u pregledniku ili koristite Live Server
```

### Chat projekt (Python Backend)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Postavi varijablu okoline GITHUB_TOKEN
python api.py
```

## Razvojni tijek rada

### Za suradnike na sadržaju

1. **Forkajte repozitorij** na svoj GitHub račun
2. **Klonirajte svoj fork** lokalno
3. **Napravite novu granu** za svoje promjene
4. Izvršite promjene u sadržaju lekcija ili primjerima koda
5. Testirajte sve izmjene koda u odgovarajućim projektnim direktorijima
6. Pošaljite pull requestove u skladu s uputama za doprinose

### Za učenike

1. Forkajte ili klonirajte repozitorij
2. Navigirajte kroz direktorije lekcija redom
3. Čitajte README datoteke za svaku lekciju
4. Završite kvizove prije lekcija na https://ff-quizzes.netlify.app/web/
5. Riješite primjere koda u mapama lekcija
6. Završite zadatke i izazove
7. Polažite kvizove nakon lekcija

### Živi razvoj

- **Dokumentacija**: Pokrenite `docsify serve` u rootu (port 3000)
- **Quiz aplikacija**: Pokrenite `npm run dev` u direktoriju quiz-app
- **Projekti**: Koristite VS Code Live Server ekstenziju za HTML projekte
- **API projekti**: Pokrenite `npm start` u odgovarajućim API direktorijima

## Upute za testiranje

### Testiranje Quiz aplikacije

```bash
cd quiz-app
npm run lint       # Provjeri probleme sa stilom koda
npm run build      # Provjeri uspješnost izgradnje
```

### Testiranje Bank API-ja

```bash
cd 7-bank-project/api
npm run lint       # Provjeri probleme sa stilom koda
node server.js     # Provjeri da li se poslužitelj pokreće bez grešaka
```

### Opći pristup testiranju

- Ovo je edukativni repozitorij bez sveobuhvatnih automatskih testova
- Ručno testiranje fokusira se na:
  - Primjere koda koji se izvršavaju bez pogrešaka
  - Ispravno funkcioniranje linkova u dokumentaciji
  - Uspješnu gradnju projekata
  - Slijedjenje najboljih praksi u primjerima

### Provjere prije slanja

- Pokrenite `npm run lint` u direktorijima s package.json
- Provjerite valjanost markdown linkova
- Testirajte primjere koda u pregledniku ili Node.js
- Provjerite da prijevodi održavaju pravilnu strukturu

## Smjernice za stil kodiranja

### JavaScript

- Koristite modernu ES6+ sintaksu
- Slijedite standardne ESLint konfiguracije iz projekata
- Koristite smisleno imenovanje varijabli i funkcija radi jasnoće za učenike
- Dodajte komentare koji objašnjavaju koncepte
- Formatirajte kod koristeći Prettier gdje je konfigurirano

### HTML/CSS

- Semantički HTML5 elementi
- Principi responzivnog dizajna
- Jasne konvencije imenovanja klasa
- Komentari koji objašnjavaju CSS tehnike za učenike

### Python

- Pridržavajte se PEP 8 smjernica
- Jasni, edukativni primjeri koda
- Tipizacije tamo gdje pomažu učenju

### Markdown dokumentacija

- Jasna hijerarhija naslova
- Code blokovi s označenim jezikom
- Linkovi na dodatne resurse
- Screenshoti i slike u mapama `images/`
- Alt tekst za slike radi pristupačnosti

### Organizacija datoteka

- Lekcije numerirane sekvencijalno (1-getting-started-lessons, 2-js-basics, itd.)
- Svaki projekt ima direktorije `solution/` i često `start/` ili `your-work/`
- Slike se nalaze u lekcijski specifičnim mapama `images/`
- Prijevodi u strukturi `translations/{language-code}/`

## Gradnja i implementacija

### Postavljanje Quiz aplikacije (Azure Static Web Apps)

Quiz aplikacija je konfigurirana za implementaciju na Azure Static Web Apps:

```bash
cd quiz-app
npm run build      # Stvara mapu dist/
# Implementira putem GitHub Actions workflow-a pri pushanju na main
```

Konfiguracija Azure Static Web Apps:
- **Lokacija aplikacije**: `/quiz-app`
- **Lokacija izlaza**: `dist`
- **Workflow**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### Generiranje PDF dokumentacije

```bash
npm install                    # Instalirajte docsify-to-pdf
npm run convert               # Generirajte PDF iz docsa
```

### Dokumentacija Docsify

```bash
npm install -g docsify-cli    # Instalirajte Docsify globalno
docsify serve                 # Poslužite na localhost:3000
```

### Gradnje specifične za projekte

Svaki projektni direktorij može imati vlastiti proces gradnje:
- Vue projekti: `npm run build` kreira produkcijske bundleove
- Statički projekti: bez koraka gradnje, direktna usluga datoteka

## Smjernice za pull requestove

### Format naslova

Koristite jasne, opisne naslove koji označavaju područje promjene:
- `[Quiz-app] Dodaj novi kviz za lekciju X`
- `[Lesson-3] Ispravi tipfelere u terrarium projektu`
- `[Translation] Dodaj španjolski prijevod za lekciju 5`
- `[Docs] Ažuriraj upute za postavljanje`

### Potrebne provjere

Prije slanja PR-a:

1. **Kvaliteta koda**:
   - Pokrenite `npm run lint` u pogođenim projektnim direktorijima
   - Ispravite sve lint greške i upozorenja

2. **Verifikacija gradnje**:
   - Pokrenite `npm run build` ako je primjenjivo
   - Osigurajte da nema grešaka u gradnji

3. **Provjera linkova**:
   - Testirajte sve markdown linkove
   - Provjerite ispravnost referenci na slike

4. **Pregled sadržaja**:
   - Provjerite pravopis i gramatiku
   - Osigurajte da su primjeri koda točni i edukativni
   - Provjerite da prijevodi čuvaju izvorno značenje

### Zahtjevi za doprinos

- Prihvatite Microsoft CLA (automatska provjera pri prvom PR-u)
- Slijedite [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/)
- Pogledajte [CONTRIBUTING.md](./CONTRIBUTING.md) za detaljne upute
- U opisu PR-a navedite brojeve povezanih issuea ako ih ima

### Proces pregleda

- PR-ove pregledavaju održavatelji i zajednica
- Prioritet je jasnoća edukativnog sadržaja
- Primjeri koda trebaju slijediti trenutne najbolje prakse
- Prijevodi se pregledavaju radi točnosti i kulturne prikladnosti

## Sustav prevođenja

### Automatizirani prijevod

- Koristi GitHub Actions s co-op-translator workflowom
- Automatski prevodi na 50+ jezika
- Izvorne datoteke u glavnim direktorijima
- Prevedene datoteke u direktorijima `translations/{language-code}/`

### Dodavanje ručnih poboljšanja prijevoda

1. Pronađite datoteku u `translations/{language-code}/`
2. Napravite poboljšanja pazeći na očuvanje strukture
3. Osigurajte ispravnost funkcionalnosti primjera koda
4. Testirajte eventualni lokalizirani sadržaj kvizova

### Metapodaci prijevoda

Prevedene datoteke sadrže metapodatkovni header:
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

## Otklanjanje pogrešaka i rješavanje problema

### Česti problemi

**Quiz aplikacija ne želi startati**:
- Provjerite verziju Node.js (preporučeno v14+)
- Izbrišite `node_modules` i `package-lock.json`, pokrenite `npm install` ponovno
- Provjerite sukobe portova (default: Vite koristi port 5173)

**API server se ne pokreće**:
- Provjerite zadovoljava li Node.js minimalnu verziju (node >=10)
- Provjerite je li port zauzet
- Osigurajte da su sve ovisnosti instalirane s `npm install`

**Proširenje za preglednik se ne učitava**:
- Provjerite ispravnost manifest.json formata
- Provjerite konzolu preglednika za greške
- Slijedite upute za instalaciju proširenja specifične za preglednik

**Problemi s Python chat projektom**:
- Provjerite je li instaliran paket OpenAI: `pip install openai`
- Provjerite je li GITHUB_TOKEN varijabla okruženja postavljena
- Provjerite dozvole pristupa za GitHub Models

**Docsify ne poslužuje dokumente**:
- Instalirajte docsify-cli globalno: `npm install -g docsify-cli`
- Pokrenite iz root direktorija repozitorija
- Provjerite postoji li `docs/_sidebar.md`

### Savjeti za razvojno okruženje

- Koristite VS Code s Live Server ekstenzijom za HTML projekte
- Instalirajte ESLint i Prettier ekstenzije za dosljedno formatiranje
- Koristite DevTools u pregledniku za debug JavaScripta
- Za Vue projekte instalirajte Vue DevTools ekstenziju za preglednik

### Razmatranja performansi

- Veliki broj prevedenih datoteka (50+ jezika) uzrokuje velike klonove
- Koristite shallow clone ako radite samo na sadržaju: `git clone --depth 1`
- Isključite prijevode iz pretraživanja kad radite na sadržaju na engleskom
- Procesi gradnje mogu biti spori pri prvom pokretanju (npm install, Vite build)

## Sigurnosna razmatranja

### Varijable okruženja

- API ključevi se nikad ne bi smjeli komitirati u repozitorij
- Koristite `.env` datoteke (već navedene u `.gitignore`)
- Dokumentirajte potrebne varijable okruženja u README-ima projekata

### Python projekti

- Koristite virtualna okruženja: `python -m venv venv`
- Održavajte ovisnosti ažurnima
- GitHub tokeni trebaju imati minimalne potrebne dozvole

### Pristup GitHub Models

- Potrebni su Personal Access Tokens (PAT) za GitHub modele
- Tokeni trebaju biti pohranjeni kao varijable okruženja
- Nikad nemojte komitirati tokene ili vjerodajnice

## Dodatne napomene

### Ciljana publika

- Potpuni početnici u web razvoju
- Studenti i samostalni učenici
- Nastavnici koji koriste nastavne planove u učionicama
- Sadržaj je osmišljen za pristupačnost i postupno stjecanje vještina

### Pedagoška filozofija

- Pristup učenja baziran na projektima
- Česte provjere znanja (kvizovi)
- Praktične vježbe kodiranja
- Primjeri iz stvarnog svijeta
- Fokus na temelje prije okvira

### Održavanje repozitorija

- Aktivna zajednica učenika i suradnika
- Redovne nadogradnje ovisnosti i sadržaja
- Problemi i diskusije praćeni od strane održavatelja
- Automatska ažuriranja prijevoda putem GitHub Actions

### Povezani resursi

- [Microsoft Learn moduli](https://docs.microsoft.com/learn/)
- [Student Hub resursi](https://docs.microsoft.com/learn/student-hub/)
- Preporučen GitHub Copilot za učenike: [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot)
- Dodatni tečajevi: Generativni AI, Data Science, ML, IoT kurikulumi dostupni

### Rad s određenim projektima

Za detaljne upute o pojedinačnim projektima, pogledajte README datoteke u:
- `quiz-app/README.md` - Vue 3 aplikacija kviza
- `7-bank-project/README.md` - Bankarska aplikacija s autentikacijom
- `5-browser-extension/README.md` - Razvoj proširenja za preglednik
- `6-space-game/README.md` - Razvoj igre bazirane na canvasu
- `9-chat-project/README.md` - Projekt AI chat asistenta

### Struktura Monorepo repozitorija

Iako nije tradicionalni monorepo, repozitorij sadrži više nezavisnih projekata:
- Svaka lekcija je samostalna
- Projekti ne dijele ovisnosti
- Rad na pojedinačnim projektima bez utjecaja na druge
- Klonirajte cijeli repozitorij za potpuno iskustvo nastavnog programa

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Odricanje od odgovornosti**:
Ovaj dokument je preveden pomoću AI usluge za prijevod [Co-op Translator](https://github.com/Azure/co-op-translator). Iako težimo točnosti, molimo imajte na umu da automatski prijevodi mogu sadržavati pogreške ili netočnosti. Izvorni dokument na njegovom izvornom jeziku treba smatrati autoritativnim izvorom. Za važne informacije preporučuje se profesionalni ljudski prijevod. Ne snosimo odgovornost za bilo kakve nesporazume ili kriva tumačenja koja proizlaze iz korištenja ovog prijevoda.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->