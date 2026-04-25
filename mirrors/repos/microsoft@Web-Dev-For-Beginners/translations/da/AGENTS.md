# AGENTS.md

## Projektoversigt

Dette er et uddannelsesforløbsdepot til undervisning i grundlæggende webudvikling for begyndere. Forløbet er et omfattende 12-ugers kursus udviklet af Microsoft Cloud Advocates og indeholder 24 praktiske lektioner om JavaScript, CSS og HTML.

### Centrale elementer

- **Uddannelsesindhold**: 24 strukturerede lektioner organiseret i projektbaserede moduler
- **Praktiske projekter**: Terrarium, Typing Game, Browser Extension, Space Game, Banking App, Code Editor og AI Chat Assistant
- **Interaktive quizzer**: 48 quizzer med 3 spørgsmål hver (før/efter lektion vurderinger)
- **Flersproget support**: Automatiske oversættelser til 50+ sprog via GitHub Actions
- **Teknologier**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (til AI projekter)

### Arkitektur

- Uddannelsesdepot med lektionbaseret struktur
- Hver lektionsmappe indeholder README, kodeeksempler og løsninger
- Selvstændige projekter i separate mapper (quiz-app, forskellige lektionsprojekter)
- Oversættelsessystem ved brug af GitHub Actions (co-op-translator)
- Dokumentation serveres via Docsify og er tilgængelig som PDF

## Opsætningskommandoer

Dette depot er primært til forbrug af uddannelsesindhold. For arbejde med specifikke projekter:

### Hoveddepot opsætning

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Quiz App opsætning (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Start udviklingsserver
npm run build      # Byg til produktion
npm run lint       # Kør ESLint
```

### Bank Projekt API (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # Start API-server
npm run lint       # Kør ESLint
npm run format     # Formater med Prettier
```

### Browser Extension projekter

```bash
cd 5-browser-extension/solution
npm install
# Følg browser-specifikke instruktioner til indlæsning af udvidelser
```

### Space Game projekter

```bash
cd 6-space-game/solution
npm install
# Åbn index.html i browseren eller brug Live Server
```

### Chat projekt (Python Backend)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Indstil miljøvariablen GITHUB_TOKEN
python api.py
```

## Udviklingsarbejdsgang

### For indholdsleverandører

1. **Fork depotet** til din GitHub konto
2. **Klon dit fork** lokalt
3. **Opret en ny gren** til dine ændringer
4. Foretag ændringer i lektionens indhold eller kodeeksempler
5. Test eventuelle kodeændringer i relevante projektmapper
6. Indsend pull requests i henhold til bidragsretningslinjer

### For lærende

1. Fork eller klon depotet
2. Naviger sekventielt gennem lektionsmapperne
3. Læs README-filer for hver lektion
4. Gennemfør før-lektions quizzer på https://ff-quizzes.netlify.app/web/
5. Arbejd gennem kodeeksemplerne i lektionsmapperne
6. Udfør opgaver og udfordringer
7. Tag efter-lektions quizzer

### Live udvikling

- **Dokumentation**: Kør `docsify serve` i rodmappen (port 3000)
- **Quiz App**: Kør `npm run dev` i quiz-app mappen
- **Projekter**: Brug VS Code Live Server-udvidelsen til HTML-projekter
- **API projekter**: Kør `npm start` i de respektive API mapper

## Testinstruktioner

### Quiz App test

```bash
cd quiz-app
npm run lint       # Tjek for kode stilproblemer
npm run build      # Bekræft at byggeriet lykkes
```

### Bank API test

```bash
cd 7-bank-project/api
npm run lint       # Tjek for kode stil problemer
node server.js     # Bekræft at serveren starter uden fejl
```

### Generel testtilgang

- Dette er et uddannelsesdepot uden omfattende automatiserede tests
- Manuel test fokuserer på:
  - At kodeeksempler kører uden fejl
  - At links i dokumentationen fungerer korrekt
  - At projektbygninger fuldføres succesfuldt
  - At eksempler følger bedste praksis

### Forud for indsendelse

- Kør `npm run lint` i mapper med package.json
- Verificer at markdown-links er gyldige
- Test kodeeksempler i browser eller Node.js
- Kontroller at oversættelser bevarer korrekt struktur

## Kode stil retningslinjer

### JavaScript

- Brug moderne ES6+ syntaks
- Følg standard ESLint konfigurationer i projekterne
- Brug meningsfulde variabel- og funktionsnavne for pædagogisk klarhed
- Tilføj kommentarer der forklarer koncepter for lærende
- Formater med Prettier hvor det er konfigureret

### HTML/CSS

- Semantiske HTML5 elementer
- Responsive designprincipper
- Klare konventioner for klassenavne
- Kommentarer der forklarer CSS-teknikker til lærende

### Python

- PEP 8 stilretningslinjer
- Klare, pædagogiske kodeeksempler
- Type hints hvor det er hjælpsomt for læring

### Markdown dokumentation

- Klar overskriftsstruktur
- Kodeblokke med sprogangivelse
- Links til yderligere ressourcer
- Skærmbilleder og billeder i `images/` mapper
- Alt-tekst til billeder for tilgængelighed

### Filorganisation

- Lektioner nummereret sekventielt (1-getting-started-lessons, 2-js-basics osv.)
- Hvert projekt har `solution/` og ofte `start/` eller `your-work/` mapper
- Billeder gemt i lektion-specifikke `images/` mapper
- Oversættelser i `translations/{language-code}/` struktur

## Byg og udrulning

### Quiz App udrulning (Azure Static Web Apps)

quiz-app er konfigureret til Azure Static Web Apps udrulning:

```bash
cd quiz-app
npm run build      # Opretter dist/ mappe
# Udruller via GitHub Actions workflow ved push til main
```

Azure Static Web Apps konfiguration:
- **App placering**: `/quiz-app`
- **Output placering**: `dist`
- **Workflow**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### Generering af PDF dokumentation

```bash
npm install                    # Installer docsify-to-pdf
npm run convert               # Generer PDF fra docs
```

### Docsify dokumentation

```bash
npm install -g docsify-cli    # Installer Docsify globalt
docsify serve                 # Kør på localhost:3000
```

### Projekt-specifikke builds

Hver projektmappe kan have sin egen build-proces:
- Vue projekter: `npm run build` skaber produktionsbundles
- Statiske projekter: Ingen build-step, server filer direkte

## Pull Request retningslinjer

### Titel format

Brug klare, beskrivende titler der angiver ændringsområde:
- `[Quiz-app] Tilføj ny quiz til lektion X`
- `[Lesson-3] Ret stavefejl i terrarium projekt`
- `[Translation] Tilføj spansk oversættelse til lektion 5`
- `[Docs] Opdater opsætningsinstruktioner`

### Krævede kontroller

Før indsendelse af PR:

1. **Kodekvalitet**:
   - Kør `npm run lint` i berørte projektmapper
   - Ret alle linting fejl og advarsler

2. **Build verifikation**:
   - Kør `npm run build` hvis relevant
   - Sørg for ingen build fejl

3. **Link validering**:
   - Test alle markdown-links
   - Bekræft billedreferencer fungerer

4. **Indholdsrevision**:
   - Læs korrektur for stave- og grammatikfejl
   - Sørg for kodeeksempler er korrekte og pædagogiske
   - Verificer at oversættelser bevarer original betydning

### Bidragskrav

- Accepter Microsoft CLA (automatisk ved første PR)
- Følg [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/)
- Se [CONTRIBUTING.md](./CONTRIBUTING.md) for detaljerede retningslinjer
- Henvis til issues i PR-beskrivelsen hvis relevant

### Review proces

- PR’s gennemgås af vedligeholdere og community
- Prioritér pædagogisk klarhed
- Kodeeksempler skal følge gældende bedste praksis
- Oversættelser vurderes for nøjagtighed og kulturel relevans

## Oversættelsessystem

### Automatisk oversættelse

- Bruger GitHub Actions med co-op-translator workflow
- Oversætter til 50+ sprog automatisk
- Kildefiler i hovedmapper
- Oversatte filer i `translations/{language-code}/` mapper

### Tilføjelse af manuelle oversættelsesforbedringer

1. Find fil i `translations/{language-code}/`
2. Foretag forbedringer mens strukturen bevares
3. Sørg for kodeeksempler fortsat fungerer
4. Test eventuelt lokaliseret quiz-indhold

### Oversættelsesmetadata

Oversatte filer inkluderer metadata-header:
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

## Fejlfinding og problemløsning

### Almindelige problemer

**Quiz app starter ikke**:
- Tjek Node.js version (v14+ anbefales)
- Slet `node_modules` og `package-lock.json`, kør `npm install` igen
- Tjek for port-konflikter (standard: Vite bruger port 5173)

**API server starter ikke**:
- Tjek at Node.js version er minimum (node >=10)
- Se om port allerede er i brug
- Sørg for alle afhængigheder installeret med `npm install`

**Browser extension indlæses ikke**:
- Tjek at manifest.json er korrekt formatteret
- Se efter fejl i browserens konsol
- Følg browser-specifikke instruktioner til installation af extension

**Problemer med Python chat projekt**:
- Sørg for OpenAI pakken er installeret: `pip install openai`
- Tjek at miljøvariablen GITHUB_TOKEN er sat
- Tjek adgangstilladelser til GitHub Models

**Docsify serverer ikke dokumentation**:
- Installer docsify-cli globalt: `npm install -g docsify-cli`
- Kør fra depotets rodfolder
- Sørg for at `docs/_sidebar.md` findes

### Tips til udviklingsmiljø

- Brug VS Code med Live Server extension til HTML projekter
- Installer ESLint og Prettier extensions for ensartet formatering
- Brug browser DevTools til JavaScript-debugging
- For Vue projekter, installer Vue DevTools browser extension

### Ydeevnehensyn

- Stort antal oversatte filer (50+ sprog) betyder store fulde kloner
- Brug shallow clone hvis du kun arbejder med indhold: `git clone --depth 1`
- Ekskluder oversættelser fra søgninger ved arbejde med engelsk indhold
- Build-processer kan være langsomme ved første kørsel (npm install, Vite build)

## Sikkerhedshensyn

### Miljøvariabler

- API nøgler må aldrig committes til depotet
- Brug `.env` filer (er allerede i `.gitignore`)
- Dokumenter krævede miljøvariabler i projekternes README-filer

### Python projekter

- Brug virtuelle miljøer: `python -m venv venv`
- Hold afhængigheder opdaterede
- GitHub tokens skal have minimale nødvendige tilladelser

### GitHub Models adgang

- Personlige Access Tokens (PAT) kræves til GitHub Models
- Tokens skal opbevares som miljøvariabler
- Aldrig commit tokens eller legitimationsoplysninger

## Yderligere noter

### Målgruppe

- Komplette begyndere i webudvikling
- Studerende og selvstuderende
- Lærere der bruger forløbet i klasserum
- Indholdet er designet til tilgængelighed og gradvis kompetenceopbygning

### Uddannelsesfilosofi

- Projektbaseret læringstilgang
- Hyppige videnschecks (quizzer)
- Praktiske kodningsøvelser
- Eksempler på virkelige anvendelser
- Fokus på fundament før frameworks

### Depotvedligeholdelse

- Aktivt fællesskab af lærende og bidragsydere
- Regelmæssige opdateringer af afhængigheder og indhold
- Issues og diskussioner overvåges af vedligeholdere
- Oversættelsesopdateringer automatiseres via GitHub Actions

### Relaterede ressourcer

- [Microsoft Learn moduler](https://docs.microsoft.com/learn/)
- [Student Hub ressourcer](https://docs.microsoft.com/learn/student-hub/)
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) anbefalet til lærende
- Yderligere kurser: Generativ AI, Data Science, ML, IoT forløb tilgængelige

### Arbejde med specifikke projekter

For detaljerede instruktioner om individuelle projekter, se README-filerne i:
- `quiz-app/README.md` - Vue 3 quiz applikation
- `7-bank-project/README.md` - Banking applikation med autentificering
- `5-browser-extension/README.md` - Udvikling af browser extension
- `6-space-game/README.md` - Canvas-baseret spiludvikling
- `9-chat-project/README.md` - AI chat assistent projekt

### Monorepo struktur

Selvom det ikke er et traditionelt monorepo, indeholder dette depot flere uafhængige projekter:
- Hver lektion er selvstændig
- Projekter deler ikke afhængigheder
- Arbejd på individuelle projekter uden at påvirke andre
- Klon hele depotet for hele kursusoplevelsen

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Ansvarsfraskrivelse**:  
Dette dokument er blevet oversat ved hjælp af AI-oversættelsestjenesten [Co-op Translator](https://github.com/Azure/co-op-translator). Selvom vi bestræber os på nøjagtighed, skal du være opmærksom på, at automatiserede oversættelser kan indeholde fejl eller unøjagtigheder. Det originale dokument på dets oprindelige sprog bør betragtes som den autoritative kilde. For kritisk information anbefales professionel menneskelig oversættelse. Vi påtager os intet ansvar for misforståelser eller fejltolkninger, der måtte opstå som følge af brugen af denne oversættelse.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->