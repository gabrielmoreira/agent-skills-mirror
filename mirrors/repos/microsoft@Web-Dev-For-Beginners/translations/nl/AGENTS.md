# AGENTS.md

## Projectoverzicht

Dit is een educatieve curriculumrepository voor het onderwijzen van de basisprincipes van webontwikkeling aan beginners. Het curriculum is een uitgebreide cursus van 12 weken, ontwikkeld door Microsoft Cloud Advocates, met 24 praktische lessen over JavaScript, CSS en HTML.

### Belangrijkste Componenten

- **Educatieve Inhoud**: 24 gestructureerde lessen georganiseerd in projectgebaseerde modules
- **Praktische Projecten**: Terrarium, Typwedstrijd, Browserextensie, Ruimtegame, Bankapp, Code-editor en AI Chatassistent
- **Interactieve Quizzen**: 48 quizzen met elk 3 vragen (voor-/nabesprekingen)
- **Meertalige Ondersteuning**: Geautomatiseerde vertalingen voor meer dan 50 talen via GitHub Actions
- **Technologieën**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (voor AI-projecten)

### Architectuur

- Educatieve repository met op lessen gebaseerde structuur
- Elke lesmap bevat README, codevoorbeelden en oplossingen
- Losstaande projecten in aparte mappen (quiz-app, diverse lesprojecten)
- Vertalingssysteem via GitHub Actions (co-op-translator)
- Documentatie verzorgd via Docsify en beschikbaar als PDF

## Setup Commando's

Deze repository is hoofdzakelijk bedoeld voor het consumeren van educatieve inhoud. Voor het werken met specifieke projecten:

### Hoofdrepository Setup

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Quiz App Setup (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Start ontwikkelserver
npm run build      # Bouw voor productie
npm run lint       # Voer ESLint uit
```

### Bank Project API (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # Start API-server
npm run lint       # Voer ESLint uit
npm run format     # Opmaak met Prettier
```

### Browserextensie Projecten

```bash
cd 5-browser-extension/solution
npm install
# Volg browser-specifieke instructies voor het laden van extensies
```

### Ruimtegame Projecten

```bash
cd 6-space-game/solution
npm install
# Open index.html in de browser of gebruik Live Server
```

### Chat Project (Python Backend)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Stel de omgevingsvariabele GITHUB_TOKEN in
python api.py
```

## Ontwikkelworkflow

### Voor Inhoudbijdragers

1. **Fork de repository** naar je GitHub-account
2. **Clone je fork** lokaal
3. **Maak een nieuwe branch** voor je wijzigingen
4. Breng wijzigingen aan in lesinhoud of codevoorbeelden
5. Test eventuele codewijzigingen in relevante projectmappen
6. Dien pull requests in volgens de bijdrage-richtlijnen

### Voor Leerlingen

1. Fork of clone de repository
2. Navigeer sequentieel door lesmappen
3. Lees README-bestanden voor elke les
4. Maak pre-les quizzen via https://ff-quizzes.netlify.app/web/
5. Doorloop codevoorbeelden in lesmappen
6. Maak opdrachten en uitdagingen
7. Maak post-les quizzen

### Live Ontwikkeling

- **Documentatie**: Run `docsify serve` in root (poort 3000)
- **Quiz App**: Run `npm run dev` in quiz-app map
- **Projecten**: Gebruik VS Code Live Server extensie voor HTML-projecten
- **API Projecten**: Run `npm start` in respectievelijke API mappen

## Testinstructies

### Quiz App Testen

```bash
cd quiz-app
npm run lint       # Controleer op codeerstijlfouten
npm run build      # Verifieer dat de build slaagt
```

### Bank API Testen

```bash
cd 7-bank-project/api
npm run lint       # Controleer op problemen met de code-stijl
node server.js     # Controleer of de server zonder fouten start
```

### Algemene Testaanpak

- Dit is een educatieve repository zonder uitgebreide geautomatiseerde tests
- Handmatig testen richt zich op:
  - Codevoorbeelden draaien zonder fouten
  - Links in documentatie werken correct
  - Projectbuilds worden succesvol afgerond
  - Voorbeelden volgen best practices

### Pre-submissie Controles

- Run `npm run lint` in mappen met package.json
- Controleer of markdown links geldig zijn
- Test codevoorbeelden in browser of Node.js
- Controleer dat vertalingen juiste structuur behouden

## Code Stijlgids

### JavaScript

- Gebruik moderne ES6+ syntax
- Volg standaard ESLint configuraties die in projecten zijn opgenomen
- Gebruik betekenisvolle variabele- en functienamen om educatief inzicht te bieden
- Voeg commentaar toe ter uitleg van concepten voor leerlingen
- Formatteer met Prettier waar geconfigureerd

### HTML/CSS

- Semantische HTML5 elementen
- Responsive design principes
- Duidelijke class naamgevingsconventies
- Commentaar met uitleg over CSS-technieken voor leerlingen

### Python

- PEP 8 stijlrichtlijnen
- Duidelijke, educatieve codevoorbeelden
- Type hints waar nuttig voor het leren

### Markdown Documentatie

- Duidelijke kopjeshiërarchie
- Codeblokken met taal specificatie
- Links naar aanvullende bronnen
- Screenshots en afbeeldingen in `images/` mappen
- Alt-tekst voor afbeeldingen voor toegankelijkheid

### Bestandsorganisatie

- Lessen genummerd in volgorde (1-getting-started-lessons, 2-js-basics, etc.)
- Elk project heeft `solution/` en vaak `start/` of `your-work/` mappen
- Afbeeldingen opgeslagen in les-specifieke `images/` mappen
- Vertalingen in `translations/{language-code}/` structuur

## Build en Deployment

### Quiz App Deployment (Azure Static Web Apps)

De quiz-app is geconfigureerd voor Azure Static Web Apps deployment:

```bash
cd quiz-app
npm run build      # Maakt de dist/ map aan
# Zet uit via GitHub Actions workflow bij push naar main
```

Azure Static Web Apps configuratie:
- **App-locatie**: `/quiz-app`
- **Output-locatie**: `dist`
- **Workflow**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### Documentatie PDF Generatie

```bash
npm install                    # Installeer docsify-to-pdf
npm run convert               # Genereer PDF van docs
```

### Docsify Documentatie

```bash
npm install -g docsify-cli    # Installeer Docsify globaal
docsify serve                 # Serveer op localhost:3000
```

### Project-specifieke Builds

Elke projectmap kan een eigen buildproces hebben:
- Vue-projecten: `npm run build` maakt productiebundels
- Statische projecten: Geen build-stap, bestanden direct serveren

## Pull Request Richtlijnen

### Titel Formaat

Gebruik duidelijke, beschrijvende titels die het wijzigingsgebied aangeven:
- `[Quiz-app] Nieuwe quiz toegevoegd voor les X`
- `[Lesson-3] Typfout opgelost in terrarium-project`
- `[Translation] Spaanse vertaling toegevoegd voor les 5`
- `[Docs] Setup instructies bijgewerkt`

### Vereiste Controles

Voor het indienen van een PR:

1. **Codekwaliteit**:
   - Run `npm run lint` in de betrokken projectmappen
   - Los alle lintfouten en waarschuwingen op

2. **Buildverificatie**:
   - Run `npm run build` indien van toepassing
   - Zorg dat er geen buildfouten zijn

3. **Link Validatie**:
   - Test alle markdown links
   - Controleer of afbeeldingsreferenties werken

4. **Inhoud Review**:
   - Controleer spelling en grammatica
   - Zorg dat codevoorbeelden correct en educatief zijn
   - Controleer dat vertalingen oorspronkelijke betekenis behouden

### Bijdragereisen

- Akkoord gaan met Microsoft CLA (geautomatiseerde check bij eerste PR)
- Volg de [Microsoft Open Source Gedragscode](https://opensource.microsoft.com/codeofconduct/)
- Zie [CONTRIBUTING.md](./CONTRIBUTING.md) voor gedetailleerde richtlijnen
- Verwijs naar issue nummers in PR-omschrijving indien van toepassing

### Reviewproces

- PR's worden beoordeeld door maintainers en community
- Educatieve helderheid krijgt prioriteit
- Codevoorbeelden volgen huidige best practices
- Vertalingen worden beoordeeld op nauwkeurigheid en culturele relevantie

## Vertalingssysteem

### Geautomatiseerde Vertaling

- Maakt gebruik van GitHub Actions met co-op-translator workflow
- Vertalingen in meer dan 50 talen automatisch
- Bronbestanden in hoofdmappen
- Vertaalde bestanden in `translations/{language-code}/` mappen

### Manuele Vertaalverbeteringen Toevoegen

1. Zoek bestand in `translations/{language-code}/`
2. Breng verbeteringen aan en behoud de structuur
3. Zorg dat codevoorbeelden functioneel blijven
4. Test alle gelokaliseerde quizinhoud

### Vertaalmetadata

Vertaalde bestanden bevatten metadata-header:
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

## Debugging en Probleemoplossing

### Veelvoorkomende Problemen

**Quiz-app start niet**:
- Controleer Node.js versie (v14+ aanbevolen)
- Verwijder `node_modules` en `package-lock.json`, run `npm install` opnieuw
- Controleer op poortconflicten (standaard: Vite gebruikt poort 5173)

**API-server start niet**:
- Controleer Node.js versie (node >=10 vereist)
- Controleer of poort al in gebruik is
- Zorg dat alle dependencies geïnstalleerd zijn met `npm install`

**Browserextensie laadt niet**:
- Controleer of manifest.json correct is geformatteerd
- Check browserconsole op fouten
- Volg browser-specifieke installatie-instructies voor extensies

**Problemen met Python chat project**:
- Zorg dat OpenAI package is geïnstalleerd: `pip install openai`
- Controleer of GITHUB_TOKEN omgevingsvariabele is ingesteld
- Controleer toegangsrechten voor GitHub Models

**Docsify serveert geen documentatie**:
- Installeer docsify-cli globaal: `npm install -g docsify-cli`
- Run vanuit root van repository
- Controleer dat `docs/_sidebar.md` bestaat

### Tips Ontwikkelomgeving

- Gebruik VS Code met Live Server extensie voor HTML-projecten
- Installeer ESLint en Prettier extensies voor consistente formattering
- Gebruik browser DevTools voor debugging van JavaScript
- Voor Vue-projecten: installeer Vue DevTools browser extensie

### Prestatie-overwegingen

- Groot aantal vertaalde bestanden (50+ talen) betekent grote klonen
- Gebruik shallow clone als je alleen aan inhoud werkt: `git clone --depth 1`
- Sluit vertalingen uit bij zoekopdrachten tijdens Engels werken
- Buildprocessen kunnen traag zijn bij eerste run (npm install, Vite build)

## Beveiligingsoverwegingen

### Omgevingsvariabelen

- API-sleutels nooit aan repository toevoegen
- Gebruik `.env` bestanden (staan al in `.gitignore`)
- Documenteer benodigde omgevingsvariabelen in project-READMEs

### Python Projecten

- Gebruik virtuele omgevingen: `python -m venv venv`
- Houd dependencies up-to-date
- GitHub tokens met minimale benodigde rechten

### GitHub Models Toegang

- Persoonlijke Toegangstokens (PAT) vereist voor GitHub Models
- Tokens opslaan als omgevingsvariabelen
- Nooit tokens of inloggegevens committen

## Aanvullende Notities

### Doelgroep

- Volledig beginners in webontwikkeling
- Studenten en zelflerenden
- Docenten die het curriculum in klassen gebruiken
- Inhoud ontworpen voor toegankelijkheid en geleidelijke vaardigheidsopbouw

### Educatieve Filosofie

- Projectgebaseerde leerbenadering
- Regelmatige kennischecks (quizzen)
- Praktische code-oefeningen
- Voorbeelden van toepassingen uit de echte wereld
- Focus op basisprincipes voor frameworks

### Repository Onderhoud

- Actieve gemeenschap van leerlingen en bijdragers
- Regelmatige updates van dependencies en inhoud
- Issues en discussies worden door maintainers gemonitord
- Vertaalupdates geautomatiseerd via GitHub Actions

### Gerelateerde Bronnen

- [Microsoft Learn modules](https://docs.microsoft.com/learn/)
- [Student Hub bronnen](https://docs.microsoft.com/learn/student-hub/)
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) aanbevolen voor leerlingen
- Extra cursussen: Generative AI, Data Science, ML, IoT curricula beschikbaar

### Werken met Specifieke Projecten

Voor gedetailleerde instructies over individuele projecten, zie de README-bestanden in:
- `quiz-app/README.md` - Vue 3 quizapplicatie
- `7-bank-project/README.md` - Banking app met authenticatie
- `5-browser-extension/README.md` - Browserextensie ontwikkeling
- `6-space-game/README.md` - Canvas-gebaseerde gameontwikkeling
- `9-chat-project/README.md` - AI chatassistent project

### Monorepo Structuur

Hoewel het geen traditionele monorepo is, bevat deze repository meerdere onafhankelijke projecten:
- Elke les is zelfstandig
- Projecten delen geen dependencies
- Werk aan individuele projecten zonder anderen te beïnvloeden
- Clone de gehele repo voor de volledige curriculumervaring

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Disclaimer**:  
Dit document is vertaald met behulp van de AI-vertalingsservice [Co-op Translator](https://github.com/Azure/co-op-translator). Hoewel we streven naar nauwkeurigheid, dient u er rekening mee te houden dat automatische vertalingen fouten of onnauwkeurigheden kunnen bevatten. Het oorspronkelijke document in de oorspronkelijke taal moet als de gezaghebbende bron worden beschouwd. Voor kritieke informatie wordt een professionele menselijke vertaling aanbevolen. Wij zijn niet aansprakelijk voor eventuele misverstanden of verkeerde interpretaties die voortvloeien uit het gebruik van deze vertaling.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->