# AGENTS.md

## Prosjektoversikt

Dette er et utdanningspensum-repositorium for å lære grunnleggende webutvikling til nybegynnere. Pensumet er et omfattende 12-ukers kurs utviklet av Microsoft Cloud Advocates, med 24 praktiske leksjoner som dekker JavaScript, CSS og HTML.

### Nøkkelkomponenter

- **Utdanningsinnhold**: 24 strukturerte leksjoner organisert i prosjektbaserte moduler  
- **Praktiske Prosjekter**: Terrarium, Typingspill, Nettleserutvidelse, Romspill, Bankapp, Kodeditor og AI Chat-assistent  
- **Interaktive Quizzer**: 48 quizzer med 3 spørsmål hver (før- og etter-leksjon vurderinger)  
- **Flerspråklig Støtte**: Automatiske oversettelser til 50+ språk via GitHub Actions  
- **Teknologier**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (for AI-prosjekter)  

### Arkitektur

- Utdanningsrepo med leksjonsbasert struktur  
- Hver leksjonsmappe inneholder README, kodeeksempler og løsninger  
- Selvstendige prosjekter i separate kataloger (quiz-app, ulike leksjonsprosjekter)  
- Oversettelsessystem med GitHub Actions (co-op-translator)  
- Dokumentasjon levert via Docsify og tilgjengelig som PDF  

## Oppsettkommandoer

Dette repositoriet er hovedsakelig for konsum av utdanningsinnhold. For arbeid med spesifikke prosjekter:

### Hovedrepo-setup

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Quiz App Setup (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Start utviklingsserver
npm run build      # Bygg for produksjon
npm run lint       # Kjør ESLint
```

### Bank Prosjekt API (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # Start API-server
npm run lint       # Kjør ESLint
npm run format     # Formater med Prettier
```

### Nettleserutvidelsesprosjekter

```bash
cd 5-browser-extension/solution
npm install
# Følg nettleserspesifikke instruksjoner for lasting av utvidelser
```

### Romspillprosjekter

```bash
cd 6-space-game/solution
npm install
# Åpne index.html i nettleser eller bruk Live Server
```

### Chatprosjekt (Python Backend)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Sett GITHUB_TOKEN-miljøvariabelen
python api.py
```

## Utviklingsarbeidsflyt

### For Innholdsbidragsytere

1. **Fork repositoriet** til din GitHub-konto  
2. **Klon din fork** lokalt  
3. **Opprett en ny gren** for dine endringer  
4. Gjør endringer i leksjonsinnhold eller kodeeksempler  
5. Test eventuelle kodeendringer i relevante prosjektmapper  
6. Send inn pull requests i samsvar med bidragsretningslinjer  

### For Lærende

1. Fork eller klon repositoriet  
2. Naviger gjennom leksjonskatalogene sekvensielt  
3. Les README-filer for hver leksjon  
4. Fullfør før-leksjonsquizzer på https://ff-quizzes.netlify.app/web/  
5. Arbeid gjennom kodeeksempler i leksjonsmapper  
6. Fullfør oppgaver og utfordringer  
7. Ta etter-leksjonsquizzer  

### Live utvikling

- **Dokumentasjon**: Kjør `docsify serve` i rotkatalog (port 3000)  
- **Quiz App**: Kjør `npm run dev` i quiz-app katalogen  
- **Prosjekter**: Bruk VS Code Live Server extension for HTML-prosjekter  
- **API Prosjekter**: Kjør `npm start` i respektive API-kataloger  

## Testinstruksjoner

### Quiz App Testing

```bash
cd quiz-app
npm run lint       # Sjekk for problemer med kodestil
npm run build      # Verifiser at byggingen lykkes
```

### Bank API Testing

```bash
cd 7-bank-project/api
npm run lint       # Sjekk for problemer med kodestil
node server.js     # Bekreft at serveren starter uten feil
```

### Generell Testtilnærming

- Dette er et utdanningsrepo uten omfattende automatiske tester  
- Manuell testing fokuserer på:  
  - Kodeeksempler kjører uten feil  
  - Lenker i dokumentasjon fungerer korrekt  
  - Prosjektbygg fullføres suksessfullt  
  - Eksempler følger beste praksis  

### Forhåndssjekker før innsending

- Kjør `npm run lint` i kataloger med package.json  
- Verifiser at markdown-lenker er gyldige  
- Test kodeeksempler i nettleser eller Node.js  
- Sjekk at oversettelser beholder riktig struktur  

## Kode-stilretningslinjer

### JavaScript

- Bruk moderne ES6+ syntaks  
- Følg standard ESLint-konfigurasjoner gitt i prosjektene  
- Bruk meningsfulle variabel- og funksjonsnavn for pedagogisk klarhet  
- Legg til kommentarer som forklarer konsepter for lærende  
- Formater med Prettier der konfigurert  

### HTML/CSS

- Semantiske HTML5-elementer  
- Responsive designprinsipper  
- Klare klasse-navnekonvensjoner  
- Kommentarer som forklarer CSS-teknikker for lærende  

### Python

- PEP 8 stilretningslinjer  
- Klare, pedagogiske kodeeksempler  
- Typehint der nyttig for læring  

### Markdown Dokumentasjon

- Klar overskriftsstruktur  
- Kodeblokker med språkspesifikasjon  
- Lenker til tilleggsmateriale  
- Skjermbilder og bilder i `images/` kataloger  
- Alt-tekst for bilder for tilgjengelighet  

### Filorganisering

- Leksjoner nummerert sekvensielt (1-getting-started-lessons, 2-js-basics, osv.)  
- Hvert prosjekt har `solution/` og ofte `start/` eller `your-work/` kataloger  
- Bilder lagres i leksjonsspesifikke `images/` mapper  
- Oversettelser i `translations/{language-code}/` struktur  

## Bygging og Distribusjon

### Quiz App distribusjon (Azure Static Web Apps)

quiz-app er konfigurert for Azure Static Web Apps-distribusjon:

```bash
cd quiz-app
npm run build      # Oppretter dist/-mappen
# Distribuerer via GitHub Actions-arbeidsflyt ved push til main
```

Azure Static Web Apps-konfigurasjon:  
- **App-lokasjon**: `/quiz-app`  
- **Output-lokasjon**: `dist`  
- **Workflow**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`  

### Dokumentasjons PDF-generering

```bash
npm install                    # Installer docsify-to-pdf
npm run convert               # Generer PDF fra docs
```

### Docsify Dokumentasjon

```bash
npm install -g docsify-cli    # Installer Docsify globalt
docsify serve                 # Server på localhost:3000
```

### Prosjektspesifikke bygg

Hver prosjektmappe kan ha egen byggprosess:  
- Vue-prosjekter: `npm run build` lager produksjonspakker  
- Statisk prosjekter: Ingen byggesteg, tjen filer direkte  

## Retningslinjer for Pull Requests

### Tittelformat

Bruk klare, beskrivende titler som angir endringsområdet:  
- `[Quiz-app] Legg til ny quiz for leksjon X`  
- `[Lesson-3] Rett skrivefeil i terrarium-prosjektet`  
- `[Translation] Legg til spansk oversettelse for leksjon 5`  
- `[Docs] Oppdater oppsettinstruksjoner`  

### Påkrevde Sjekker

Før innsending av PR:  

1. **Kodekvalitet**:  
   - Kjør `npm run lint` i berørte prosjektmapper  
   - Rett alle lintfeil og advarsler  

2. **Byggverifisering**:  
   - Kjør `npm run build` om aktuelt  
   - Sørg for ingen byggefeil  

3. **Lenkevalidering**:  
   - Test alle markdown-lenker  
   - Verifiser bildehenvisninger fungerer  

4. **Innholdsrevisjon**:  
   - Korrekturles for rettskrivning og grammatikk  
   - Sørg for at kodeeksempler er korrekte og pedagogiske  
   - Kontroller at oversettelser beholder opprinnelig mening  

### Bidragskrav

- Aksepter Microsoft CLA (automatisk sjekk ved første PR)  
- Følg [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/)  
- Se [CONTRIBUTING.md](./CONTRIBUTING.md) for detaljerte retningslinjer  
- Referer til issues i PR-beskrivelse om aktuelt  

### Gjennomgangsprosess

- PR-er gjennomgås av vedlikeholdere og community  
- Pedagogisk klarhet prioriteres  
- Kodeeksempler skal følge gjeldende beste praksis  
- Oversettelser vurderes for nøyaktighet og kulturell hensiktsmessighet  

## Oversettelsessystem

### Automatisk Oversettelse

- Bruker GitHub Actions med co-op-translator workflow  
- Oversetter til 50+ språk automatisk  
- Kildefiler i hovedkataloger  
- Oversatte filer i `translations/{language-code}/` kataloger  

### Legge til Manuelle Oversettelsesforbedringer

1. Finn fil i `translations/{language-code}/`  
2. Gjør forbedringer mens du bevarer struktur  
3. Sørg for at kodeeksempler fortsatt fungerer  
4. Test eventuelt lokalt quiz-innhold  

### Oversettelsesmetadata

Oversatte filer inkluderer metadataheader:  
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
  
## Feilsøking og Problemløsning

### Vanlige Problemer

**Quiz-app starter ikke**:  
- Sjekk Node.js-versjon (v14+ anbefalt)  
- Slett `node_modules` og `package-lock.json`, kjør `npm install` på nytt  
- Sjekk for portkonflikter (standard: Vite bruker port 5173)  

**API-server starter ikke**:  
- Bekreft Node.js-versjon møter minimumskrav (node >=10)  
- Sjekk om port allerede er i bruk  
- Sørg for at alle avhengigheter er installert med `npm install`  

**Nettleserutvidelse lastes ikke**:  
- Verifiser at manifest.json er riktig formatert  
- Sjekk nettleserkonsollen for feil  
- Følg nettleserspesifikke installasjonsinstrukser for utvidelser  

**Python chat-prosjekt problemer**:  
- Sørg for at OpenAI-pakken er installert: `pip install openai`  
- Bekreft at GITHUB_TOKEN miljøvariabel er satt  
- Sjekk GitHub Models adgangstillatelser  

**Docsify server ikke dokumentasjon**:  
- Installer docsify-cli globalt: `npm install -g docsify-cli`  
- Kjør fra repos rotkatalog  
- Sjekk at `docs/_sidebar.md` eksisterer  

### Tips for Utviklingsmiljø

- Bruk VS Code med Live Server extension for HTML-prosjekter  
- Installer ESLint og Prettier extensions for konsistent formatering  
- Bruk nettleserens DevTools for JavaScript-feilsøking  
- For Vue-prosjekter, installer Vue DevTools nettleser-utvidelse  

### Ytelsesbetraktninger

- Mange oversatte filer (50+ språk) gjør full kloning stor  
- Bruk shallow clone hvis du kun jobber med innhold: `git clone --depth 1`  
- Ekskluder oversettelser i søk når du jobber med engelsk innhold  
- Byggeprosesser kan være treg ved første kjøring (npm install, Vite build)  

## Sikkerhetsbetraktninger

### Miljøvariabler

- API-nøkler må aldri legges i repositoriet  
- Bruk `.env` filer (allerede i `.gitignore`)  
- Dokumenter nødvendige miljøvariabler i prosjekt-READMEer  

### Python Prosjekter

- Bruk virtuelle miljøer: `python -m venv venv`  
- Hold avhengigheter oppdatert  
- GitHub-tokens bør ha minimale nødvendige rettigheter  

### GitHub Models-adgang

- Personlige tilgangstokener (PAT) kreves for GitHub Models  
- Tokens skal lagres som miljøvariabler  
- Aldri legg tokens eller credentials i repositoriet  

## Tilleggsnotater

### Målgruppe

- Helt komplette nybegynnere til webutvikling  
- Studenter og selvstudenter  
- Lærere som bruker pensum i klasserom  
- Innhold designet for tilgjengelighet og gradvis ferdighetsbygging  

### Pedagogisk Filosofi

- Prosjektbasert læringsmetode  
- Hyppige kunnskapssjekker (quizzer)  
- Praktiske kodingøvelser  
- Virkelighetsnære eksempler  
- Fokus på grunnprinsipper før rammeverk  

### Repositorieveiledning

- Aktiv community av lærende og bidragsytere  
- Regelmessige oppdateringer av avhengigheter og innhold  
- Issues og diskusjoner overvåkes av vedlikeholdere  
- Oversettelsesoppdateringer automatisert via GitHub Actions  

### Relaterte Ressurser

- [Microsoft Learn moduler](https://docs.microsoft.com/learn/)  
- [Student Hub-ressurser](https://docs.microsoft.com/learn/student-hub/)  
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) anbefalt for lærende  
- Flere kurs: Generative AI, Data Science, ML, IoT pensum tilgjengelig  

### Arbeid med Spesifikke Prosjekter

For detaljerte instrukser om enkeltprosjekter, se README-filene i:  
- `quiz-app/README.md` - Vue 3 quiz-applikasjon  
- `7-bank-project/README.md` - Bankapplikasjon med autentisering  
- `5-browser-extension/README.md` - Nettleserutvidelsesutvikling  
- `6-space-game/README.md` - Canvas-basert spillutvikling  
- `9-chat-project/README.md` - AI chat-assistent prosjekt  

### Monorepo-struktur

Selv om det ikke er et tradisjonelt monorepo, inneholder dette repositoriet flere uavhengige prosjekter:  
- Hver leksjon er selvstendig  
- Prosjekter deler ikke avhengigheter  
- Arbeid med individuelle prosjekter uten å påvirke andre  
- Klon hele repo for full pensumopplevelse  

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Ansvarsfraskrivelse**:  
Dette dokumentet er oversatt ved hjelp av AI-oversettelsestjenesten [Co-op Translator](https://github.com/Azure/co-op-translator). Selv om vi streber etter nøyaktighet, vennligst vær oppmerksom på at automatiserte oversettelser kan inneholde feil eller unøyaktigheter. Det opprinnelige dokumentet på originalspråket skal anses som den autoritative kilden. For kritisk informasjon anbefales profesjonell menneskelig oversettelse. Vi er ikke ansvarlige for misforståelser eller feiltolkninger som følge av bruken av denne oversettelsen.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->