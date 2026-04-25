# AGENTS.md

## Projektöversikt

Detta är ett utbildningscurriculum för att lära ut grunderna i webbutveckling till nybörjare. Curriculumet är en omfattande 12-veckorskurs utvecklad av Microsoft Cloud Advocates, med 24 praktiska lektioner som täcker JavaScript, CSS och HTML.

### Viktiga komponenter

- **Utbildningsinnehåll**: 24 strukturerade lektioner organiserade i projektbaserade moduler
- **Praktiska projekt**: Terrarium, Skrivspel, Webbläsartillägg, Rymdspel, Bankapp, Kodredigerare och AI-chattassistent
- **Interaktiva quiz**: 48 quiz med 3 frågor vardera (före- och efter-lektionsbedömningar)
- **Flerspråkigt stöd**: Automatiska översättningar till 50+ språk via GitHub Actions
- **Teknologier**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (för AI-projekt)

### Arkitektur

- Utbildningsrepository med lektionsbaserad struktur
- Varje lektionsmapp innehåller README, kodexempel och lösningar
- Självständiga projekt i separata kataloger (quiz-app, olika lektionsprojekt)
- Översättningssystem som använder GitHub Actions (co-op-translator)
- Dokumentation tillgänglig via Docsify och som PDF

## Installationskommandon

Detta repository är främst för konsumtion av utbildningsinnehåll. För arbete med specifika projekt:

### Huvudrepositoryinstallation

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Quiz App Installation (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Starta utvecklingsserver
npm run build      # Bygg för produktion
npm run lint       # Kör ESLint
```

### Bankprojekt API (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # Starta API-server
npm run lint       # Kör ESLint
npm run format     # Formatera med Prettier
```

### Webbläsartilläggsprojekt

```bash
cd 5-browser-extension/solution
npm install
# Följ webbläsarspecifika instruktioner för att ladda tillägg
```

### Rymdspelsprojekt

```bash
cd 6-space-game/solution
npm install
# Öppna index.html i webbläsaren eller använd Live Server
```

### Chattprojekt (Python Backend)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Sätt miljövariabeln GITHUB_TOKEN
python api.py
```

## Utvecklingsarbetsflöde

### För innehållsbidragare

1. **Forka repositoryt** till ditt GitHub-konto
2. **Klona din fork** lokalt
3. **Skapa en ny branch** för dina ändringar
4. Gör ändringar av lektioninnehåll eller kodexempel
5. Testa kodändringar i relevanta projektmappar
6. Skicka pull requests enligt riktlinjerna för bidrag

### För elever

1. Forka eller klona repositoryt
2. Navigera sekventiellt till lektionsmappar
3. Läs README-filer för varje lektion
4. Genomför quiz före lektioner på https://ff-quizzes.netlify.app/web/
5. Arbeta igenom kodexempel i lektionsmappar
6. Slutför uppgifter och utmaningar
7. Gör quiz efter lektioner

### Live-utveckling

- **Dokumentation**: Kör `docsify serve` i rotmappen (port 3000)
- **Quiz App**: Kör `npm run dev` i quiz-app-katalogen
- **Projekt**: Använd VS Code Live Server-tillägg för HTML-projekt
- **API-projekt**: Kör `npm start` i respektive API-katalog

## Testinstruktioner

### Quiz App-testning

```bash
cd quiz-app
npm run lint       # Kontrollera kodstilproblem
npm run build      # Verifiera att kompilering lyckas
```

### Bank API-testning

```bash
cd 7-bank-project/api
npm run lint       # Kontrollera kodstilproblem
node server.js     # Verifiera att servern startar utan fel
```

### Allmän testmetod

- Detta är ett utbildningsrepository utan omfattande automatiserade tester
- Manuell testning fokuserar på:
  - Kodexempel körs utan fel
  - Länkar i dokumentation fungerar korrekt
  - Projekt bygger klart utan problem
  - Exempel följer bästa praxis

### Kontroll före inskickning

- Kör `npm run lint` i kataloger med package.json
- Verifiera att markdown-länkar är giltiga
- Testa kodexempel i webbläsare eller Node.js
- Kontrollera att översättningar behåller korrekt struktur

## Kodstilriktlinjer

### JavaScript

- Använd modern ES6+ syntax
- Följ standard ESLint-konfigurationer i projekten
- Använd meningsfulla variabel- och funktionsnamn för tydlighet i utbildningen
- Lägg till kommentarer som förklarar koncept för elever
- Formatera med Prettier där det är konfigurerat

### HTML/CSS

- Semantiska HTML5-element
- Responsiva designprinciper
- Klara och tydliga klassnamn
- Kommentarer som förklarar CSS-tekniker för elever

### Python

- Följ PEP 8-stilriktlinjer
- Tydliga, pedagogiska kodexempel
- Typanvisningar där det är hjälpsamt för lärande

### Markdown-dokumentation

- Tydlig rubrikhierarki
- Kodblock med språkangivelse
- Länkar till ytterligare resurser
- Skärmdumpar och bilder i `images/`-mappar
- Alt-text för bilder för tillgänglighet

### Filorganisation

- Lektioner numrerade sekventiellt (1-getting-started-lessons, 2-js-basics, etc.)
- Varje projekt har `solution/` och ofta `start/` eller `your-work/`-mappar
- Bilder lagras i lektion-specifika `images/`-mappar
- Översättningar i `translations/{language-code}/`-struktur

## Bygg och distribution

### Distribution av Quiz App (Azure Static Web Apps)

quiz-app är konfigurerad för deployment via Azure Static Web Apps:

```bash
cd quiz-app
npm run build      # Skapar dist/-mappen
# Distribuerar via GitHub Actions arbetsflöde vid push till main
```

Azure Static Web Apps-konfiguration:
- **App-lokalisation**: `/quiz-app`
- **Output-lokalisation**: `dist`
- **Arbetsflöde**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### PDF-generering av dokumentation

```bash
npm install                    # Installera docsify-to-pdf
npm run convert               # Generera PDF från docs
```

### Docsify-dokumentation

```bash
npm install -g docsify-cli    # Installera Docsify globalt
docsify serve                 # Servera på localhost:3000
```

### Projekt-specifika byggprocesser

Varje projektkatalog kan ha sin egen byggprocess:
- Vue-projekt: `npm run build` skapar produktionspaket
- Statiska projekt: Ingen byggsteg, servera filer direkt

## Pull Request-riktlinjer

### Titelformat

Använd tydliga, beskrivande titlar som anger ändringsområde:
- `[Quiz-app] Lägg till nytt quiz för lektion X`
- `[Lesson-3] Åtgärda stavfel i terrariumprojekt`
- `[Translation] Lägg till spansk översättning för lektion 5`
- `[Docs] Uppdatera installationsinstruktioner`

### Obligatoriska kontroller

Innan PR skickas:

1. **Kodkvalitet**:
   - Kör `npm run lint` i berörda projektmappar
   - Åtgärda alla lintfel och varningar

2. **Byggverifiering**:
   - Kör `npm run build` om tillämpligt
   - Säkerställ att inga byggfel uppstår

3. **Länkvalidering**:
   - Testa alla markdown-länkar
   - Verifiera bildreferenser fungerar

4. **Innehållsgranskning**:
   - Korrekturläs för stavning och grammatik
   - Säkerställ kodexempel är korrekta och pedagogiska
   - Kontrollera att översättningar bevarar ursprungligt budskap

### Bidragskrav

- Acceptera Microsoft CLA (automatisk kontroll vid första PR)
- Följ [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/)
- Se [CONTRIBUTING.md](./CONTRIBUTING.md) för detaljerade riktlinjer
- Referera ärendenummer i PR-beskrivning om tillämpligt

### Granskningsprocess

- PR granskas av underhållare och community
- Pedagogisk tydlighet prioriteras
- Kodexempel ska följa aktuella bästa praxis
- Översättningar granskas för korrekthet och kulturell anpassning

## Översättningssystem

### Automatisk översättning

- Använder GitHub Actions med co-op-translator arbetsflöde
- Översätter automatiskt till 50+ språk
- Källfiler i huvudkataloger
- Översatta filer i `translations/{language-code}/`-mappar

### Lägga till manuella förbättringar

1. Lokalisera fil i `translations/{language-code}/`
2. Gör förbättringar med bibehållen struktur
3. Säkerställ att kodexempel fortsätter att fungera
4. Testa lokaliserat quiz-innehåll

### Metadata för översättningar

Översatta filer inkluderar metadata-header:
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

## Felsökning och problemlösning

### Vanliga problem

**Quiz app startar inte**:
- Kontrollera Node.js-version (v14+ rekommenderas)
- Ta bort `node_modules` och `package-lock.json`, kör `npm install` igen
- Kontrollera portkonflikter (standard: Vite använder port 5173)

**API-server startar inte**:
- Verifiera att Node.js-version uppfyller minimikrav (node >=10)
- Kontrollera om port redan används
- Se till att alla beroenden är installerade med `npm install`

**Webbläsartillägg laddas inte**:
- Verifiera att manifest.json är korrekt formaterad
- Kontrollera webbläsarkonsol för fel
- Följ webbläsarspecifika installationsinstruktioner för tillägg

**Problem med Python-chattprojekt**:
- Säkerställ att OpenAI-paket är installerat: `pip install openai`
- Kontrollera att miljövariabeln GITHUB_TOKEN är satt
- Kontrollera tillgång till GitHub Models

**Docsify serverar inte dokumentation**:
- Installera docsify-cli globalt: `npm install -g docsify-cli`
- Kör från repositories rotkatalog
- Kontrollera att `docs/_sidebar.md` finns

### Tips för utvecklingsmiljö

- Använd VS Code med Live Server-tillägg för HTML-projekt
- Installera ESLint och Prettier-tillägg för konsekvent formatering
- Använd webbläsarens utvecklarverktyg för att felsöka JavaScript
- För Vue-projekt, installera Vue DevTools webbläsartillägg

### Prestandaöverväganden

- Stort antal översatta filer (50+ språk) gör att fulla kloner blir stora
- Använd shallow clone vid arbete enbart med innehåll: `git clone --depth 1`
- Exkludera översättningar från sökningar vid arbete med engelskt innehåll
- Byggprocesser kan vara långsamma vid första körning (npm install, Vite build)

## Säkerhetsöverväganden

### Miljövariabler

- API-nycklar ska aldrig committas till repositoryt
- Använd `.env`-filer (är redan med i `.gitignore`)
- Dokumentera nödvändiga miljövariabler i projekts README-filer

### Python-projekt

- Använd virtuella miljöer: `python -m venv venv`
- Håll beroenden uppdaterade
- GitHub-token bör ha minimala tillåtna behörigheter

### GitHub Models access

- Personliga Access Tokens (PAT) krävs för GitHub Models
- Tokens bör lagras som miljövariabler
- Aldrig commit tokens eller inloggningsuppgifter

## Ytterligare anteckningar

### Målgrupp

- Kompletta nybörjare i webbutveckling
- Studenter och självstudenter
- Lärare som använder curriculum i klassrum
- Innehåll designat för tillgänglighet och gradvis kompetensuppbyggnad

### Pedagogisk filosofi

- Projektbaserat lärande
- Frekventa kunskapskontroller (quiz)
- Praktiska kodningsövningar
- Exempel från verkliga applikationer
- Fokus på grunder innan ramverk

### Repositoryunderhåll

- Aktiv community av elever och bidragsgivare
- Regelbundna uppdateringar av beroenden och innehåll
- Ärenden och diskussioner övervakas av underhållare
- Översättningsuppdateringar automatiserade via GitHub Actions

### Relaterade resurser

- [Microsoft Learn-moduler](https://docs.microsoft.com/learn/)
- [Student Hub-resurser](https://docs.microsoft.com/learn/student-hub/)
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) rekommenderas för elever
- Ytterligare kurser: Generativ AI, Data Science, ML, IoT curriculum tillgängliga

### Arbeta med specifika projekt

För detaljerade instruktioner om individuella projekt, se README-filer i:
- `quiz-app/README.md` - Vue 3 quizapplikation
- `7-bank-project/README.md` - Bankapplikation med autentisering
- `5-browser-extension/README.md` - Webbläsartilläggsutveckling
- `6-space-game/README.md` - Canvas-baserat spel
- `9-chat-project/README.md` - AI-chattassistentprojekt

### Monorepo-struktur

Även om det inte är ett traditionellt monorepo innehåller detta repository flera oberoende projekt:
- Varje lektion är självständig
- Projekt delar inte beroenden
- Arbeta med individuella projekt utan påverkan på andra
- Klona hela repositoryt för hela curriculum-upplevelsen

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Ansvarsfriskrivning**:
Detta dokument har översatts med hjälp av AI-översättningstjänsten [Co-op Translator](https://github.com/Azure/co-op-translator). Även om vi strävar efter noggrannhet, var vänlig notera att automatiska översättningar kan innehålla fel eller felaktigheter. Det ursprungliga dokumentet på dess modersmål bör betraktas som den auktoritativa källan. För kritisk information rekommenderas professionell mänsklig översättning. Vi ansvarar inte för några missförstånd eller feltolkningar som uppstår från användningen av denna översättning.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->