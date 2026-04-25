# AGENTS.md

## Projektübersicht

Dies ist ein Bildungs-Curriculum-Repository zum Erlernen der Grundlagen der Webentwicklung für Einsteiger. Das Curriculum ist ein umfassender 12-Wochen-Kurs, der von Microsoft Cloud Advocates entwickelt wurde und 24 praxisorientierte Lektionen zu JavaScript, CSS und HTML enthält.

### Hauptkomponenten

- **Bildungsinhalte**: 24 strukturierte Lektionen, organisiert in projektbasierten Modulen
- **Praktische Projekte**: Terrarium, Tipp-Spiel, Browser-Erweiterung, Weltraumspiel, Banking-App, Code-Editor und KI-Chat-Assistent
- **Interaktive Quizze**: 48 Quizze mit jeweils 3 Fragen (Vor-/Nach-Lektion Bewertungen)
- **Mehrsprachige Unterstützung**: Automatisierte Übersetzungen für über 50 Sprachen via GitHub Actions
- **Technologien**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (für KI-Projekte)

### Architektur

- Bildungs-Repository mit lektionenbasierter Struktur
- Jeder Lektionenordner enthält README, Codebeispiele und Lösungen
- Eigenständige Projekte in separaten Verzeichnissen (quiz-app, verschiedene Lektionenprojekte)
- Übersetzungssystem unter Verwendung von GitHub Actions (co-op-translator)
- Dokumentation bereitgestellt über Docsify und als PDF verfügbar

## Setup-Befehle

Dieses Repository dient hauptsächlich dem Konsum von Bildungsinhalten. Für die Arbeit mit spezifischen Projekten:

### Haupt-Repository-Setup

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Quiz-App Setup (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Entwicklungsserver starten
npm run build      # Für die Produktion erstellen
npm run lint       # ESLint ausführen
```

### Bank-Projekt API (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # API-Server starten
npm run lint       # ESLint ausführen
npm run format     # Mit Prettier formatieren
```

### Browser-Erweiterungsprojekte

```bash
cd 5-browser-extension/solution
npm install
# Folgen Sie den browserspezifischen Anweisungen zum Laden der Erweiterung
```

### Weltraumspiel-Projekte

```bash
cd 6-space-game/solution
npm install
# Öffne index.html im Browser oder verwende Live Server
```

### Chat-Projekt (Python Backend)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Setze die Umgebungsvariable GITHUB_TOKEN
python api.py
```

## Entwicklungs-Workflow

### Für Inhaltsanbieter

1. **Forke das Repository** in dein GitHub-Konto
2. **Klon deinen Fork** lokal
3. **Erstelle einen neuen Branch** für deine Änderungen
4. Ändere Inhalte der Lektionen oder Codebeispiele
5. Teste Codeänderungen in den entsprechenden Projektverzeichnissen
6. Reiche Pull Requests gemäß den Beitragsrichtlinien ein

### Für Lernende

1. Forke oder klone das Repository
2. Navigiere nacheinander zu Lektionen-Verzeichnissen
3. Lies README-Dateien jeder Lektion
4. Absolviere Pre-Lesson-Quizze unter https://ff-quizzes.netlify.app/web/
5. Arbeite die Codebeispiele in den Lektionenordnern durch
6. Bearbeite Aufgaben und Herausforderungen
7. Mache Post-Lesson-Quizze

### Live-Entwicklung

- **Dokumentation**: Führe `docsify serve` im Root-Verzeichnis aus (Port 3000)
- **Quiz-App**: Führe `npm run dev` im Verzeichnis quiz-app aus
- **Projekte**: Nutze VS Code Live Server Erweiterung für HTML-Projekte
- **API-Projekte**: Führe `npm start` in den jeweiligen API-Verzeichnissen aus

## Testanweisungen

### Quiz-App-Tests

```bash
cd quiz-app
npm run lint       # Überprüfen Sie auf Code-Stil-Probleme
npm run build      # Überprüfen Sie, ob der Build erfolgreich ist
```

### Bank API-Tests

```bash
cd 7-bank-project/api
npm run lint       # Überprüfen Sie auf Probleme mit dem Code-Stil
node server.js     # Überprüfen Sie, ob der Server ohne Fehler startet
```

### Allgemeiner Testansatz

- Dies ist ein Bildungs-Repository ohne umfassende automatisierte Tests
- Manuelles Testen konzentriert sich auf:
  - Codebeispiele laufen fehlerfrei
  - Links in der Dokumentation funktionieren korrekt
  - Projekte bauen fehlerfrei
  - Beispiele folgen Best Practices

### Vorab-Checks vor Pull Requests

- Führe `npm run lint` in Verzeichnissen mit package.json aus
- Überprüfe ob Markdown-Links gültig sind
- Teste Codebeispiele im Browser oder Node.js
- Prüfe, dass Übersetzungen die richtige Struktur behalten

## Code Style Richtlinien

### JavaScript

- Verwende moderne ES6+ Syntax
- Folge den standardmäßigen ESLint-Konfigurationen der Projekte
- Verwende aussagekräftige Variablen- und Funktionsnamen für Bildungszwecke
- Füge erklärende Kommentare für Lernende hinzu
- Formatiere mit Prettier, wenn konfiguriert

### HTML/CSS

- Semantische HTML5-Elemente
- Responsive Design Prinzipien
- Klare Klassennamen-Konventionen
- Kommentare, die CSS-Techniken für Lernende erklären

### Python

- PEP 8 Stilrichtlinien
- Klare, bildungsorientierte Codebeispiele
- Type Hints wo hilfreich zum Lernen

### Markdown-Dokumentation

- Klare Überschriftenhierarchie
- Codeblöcke mit Sprachangabe
- Links zu weiterführenden Ressourcen
- Screenshots und Bilder in `images/` Verzeichnissen
- Alt-Text für Bilder für Barrierefreiheit

### Dateiorganisation

- Lektionen nummeriert (1-getting-started-lessons, 2-js-basics, etc.)
- Jedes Projekt hat `solution/` und oft `start/` oder `your-work/` Verzeichnisse
- Bilder in lektionenspezifischen `images/` Ordnern
- Übersetzungen in `translations/{language-code}/` Struktur

## Build und Deployment

### Quiz-App Deployment (Azure Static Web Apps)

Die quiz-app ist für Azure Static Web Apps Deployment konfiguriert:

```bash
cd quiz-app
npm run build      # Erstellt den Ordner dist/
# Führt Bereitstellung über GitHub Actions Workflow bei Push auf main durch
```

Azure Static Web Apps Konfiguration:
- **App Location**: `/quiz-app`
- **Output Location**: `dist`
- **Workflow**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### Generierung der PDF-Dokumentation

```bash
npm install                    # Installiere docsify-to-pdf
npm run convert               # Erzeuge PDF aus Docs
```

### Docsify Dokumentation

```bash
npm install -g docsify-cli    # Installiere Docsify global
docsify serve                 # Auf localhost:3000 bereitstellen
```

### Projektspezifische Builds

Jedes Projektverzeichnis kann einen eigenen Build-Prozess besitzen:
- Vue-Projekte: `npm run build` erstellt Produktions-Bundles
- Statische Projekte: Kein Build-Schritt, Dateien werden direkt ausgeliefert

## Pull Request Richtlinien

### Titel-Format

Verwende klare, beschreibende Titel, die den Änderungsbereich angeben:
- `[Quiz-app] Neues Quiz für Lektion X hinzufügen`
- `[Lesson-3] Rechtschreibfehler im Terrarium-Projekt korrigieren`
- `[Translation] Spanische Übersetzung für Lektion 5 hinzufügen`
- `[Docs] Setup-Anweisungen aktualisieren`

### Erforderliche Checks

Vor dem Einreichen eines PR:

1. **Codequalität**:
   - Führe `npm run lint` in betroffenen Projektverzeichnissen aus
   - Behebe alle Linting-Fehler und Warnungen

2. **Build-Verifikation**:
   - Führe `npm run build` falls zutreffend aus
   - Stelle sicher, dass keine Build-Fehler auftreten

3. **Link-Validierung**:
   - Teste alle Markdown-Links
   - Überprüfe Bildreferenzen

4. **Inhaltsüberprüfung**:
   - Lektorat auf Rechtschreibung und Grammatik
   - Stelle sicher, dass Codebeispiele korrekt und didaktisch sind
   - Prüfe, dass Übersetzungen den Originalinhalt richtig wiedergeben

### Beitragspflichten

- D Zustimmung zur Microsoft CLA (automatische Prüfung beim ersten PR)
- Folge dem [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/)
- Siehe [CONTRIBUTING.md](./CONTRIBUTING.md) für detaillierte Richtlinien
- Verweise Issue-Nummern im PR-Beschreibung, falls zutreffend

### Review-Prozess

- PRs werden von Maintainer:innen und Community geprüft
- Bildnerische Klarheit hat Priorität
- Codebeispiele sollen aktuellen Best Practices folgen
- Übersetzungen werden auf Genauigkeit und kulturelle Angemessenheit geprüft

## Übersetzungssystem

### Automatische Übersetzung

- Nutzt GitHub Actions mit co-op-translator Workflow
- Übersetzt automatisch in über 50 Sprachen
- Quelldateien in Hauptverzeichnissen
- Übersetzte Dateien in `translations/{language-code}/`

### Manuelle Verbesserungen der Übersetzung hinzufügen

1. Finde Datei in `translations/{language-code}/`
2. Nimm Verbesserungen vor, Struktur soll erhalten bleiben
3. Sicherstellen, dass Codebeispiele funktionsfähig bleiben
4. Teste ggf. Quiz-Inhalte in Lokalisation

### Übersetzungs-Metadaten

Übersetzte Dateien enthalten Meta-Daten-Header:
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

## Debugging und Fehlerbehebung

### Häufige Probleme

**Quiz-App startet nicht**:
- Prüfe Node.js-Version (v14+ empfohlen)
- Lösche `node_modules` und `package-lock.json`, führe `npm install` erneut aus
- Prüfe Port-Konflikte (standardmäßig Vite Port 5173)

**API-Server startet nicht**:
- Stelle sicher, dass Node.js Version >=10 ist
- Prüfe, ob Port bereits belegt ist
- Stelle sicher, dass alle Abhängigkeiten mit `npm install` installiert sind

**Browser-Erweiterung lädt nicht**:
- Prüfe, ob manifest.json korrekt formatiert ist
- Schau in die Browser-Konsole auf Fehler
- Folge browserspezifischen Installationsanweisungen

**Probleme mit Python Chat-Projekt**:
- Stelle sicher, dass OpenAI-Paket installiert ist: `pip install openai`
- Prüfe, ob Umgebungsvariable GITHUB_TOKEN gesetzt ist
- Prüfe GitHub Models-Zugriffsrechte

**Docsify liefert keine Dokumentation aus**:
- Installiere docsify-cli global: `npm install -g docsify-cli`
- Starte im Root-Verzeichnis des Repos
- Stelle sicher, dass `docs/_sidebar.md` existiert

### Tipps zur Entwicklungsumgebung

- Verwende VS Code mit Live Server-Erweiterung für HTML-Projekte
- Installiere ESLint und Prettier Erweiterungen für konsistente Formatierung
- Nutze Browser DevTools zum Debuggen von JavaScript
- Für Vue-Projekte: Installiere Vue DevTools Browser Erweiterung

### Performance-Überlegungen

- Große Anzahl übersetzter Dateien (50+ Sprachen) führt zu großen Vollklonen
- Verwende flachen Klon wenn nur Inhalt bearbeitet wird: `git clone --depth 1`
- Schließe Übersetzungen von Suchvorgängen aus, wenn du an englischen Inhalten arbeitest
- Build-Prozesse können beim ersten Lauf langsam sein (npm install, Vite Build)

## Sicherheitsüberlegungen

### Umgebungsvariablen

- API-Schlüssel dürfen niemals im Repository hinterlegt werden
- Verwende `.env`-Dateien (schon in `.gitignore` enthalten)
- Dokumentiere benötigte Umgebungsvariablen in Projekt-READMEs

### Python-Projekte

- Nutze virtuelle Umgebungen: `python -m venv venv`
- Halte Abhängigkeiten aktuell
- GitHub-Tokens sollten minimale erforderliche Berechtigungen haben

### GitHub Models Zugriff

- Personal Access Tokens (PAT) sind für GitHub Models erforderlich
- Tokens sollten als Umgebungsvariablen gespeichert werden
- Tokens oder Zugangsdaten niemals committen

## Zusätzliche Hinweise

### Zielgruppe

- Absolute Anfänger in der Webentwicklung
- Studierende und autodidaktische Lernende
- Lehrkräfte, die das Curriculum im Unterricht verwenden
- Inhalte sind auf Barrierefreiheit und schrittweise Kompetenzentwicklung ausgelegt

### Pädagogische Philosophie

- Projektbasiertes Lernen
- Regelmäßige Wissensüberprüfungen (Quizze)
- Praxisorientierte Coding-Übungen
- Beispiele aus der realen Welt
- Fokus auf Grundlagen vor Frameworks

### Repository-Wartung

- Aktive Community aus Lernenden und Beitragenden
- Regelmäßige Updates von Abhängigkeiten und Inhalten
- Probleme und Diskussionen werden von Maintainer:innen überwacht
- Übersetzungsupdates automatisiert via GitHub Actions

### Verwandte Ressourcen

- [Microsoft Learn Module](https://docs.microsoft.com/learn/)
- [Student Hub Ressourcen](https://docs.microsoft.com/learn/student-hub/)
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) empfohlen für Lernende
- Zusätzliche Kurse: Generative KI, Data Science, ML, IoT Curricula verfügbar

### Arbeit mit spezifischen Projekten

Für detaillierte Anweisungen zu einzelnen Projekten siehe README-Dateien in:
- `quiz-app/README.md` - Vue 3 Quiz-Anwendung
- `7-bank-project/README.md` - Banking-Anwendung mit Authentifizierung
- `5-browser-extension/README.md` - Browser-Erweiterungsentwicklung
- `6-space-game/README.md` - Canvas-basiertes Spiel
- `9-chat-project/README.md` - KI-Chat-Assistent Projekt

### Monorepo-Struktur

Obgleich kein klassisches Monorepo, enthält dieses Repository mehrere unabhängige Projekte:
- Jede Lektion ist autark
- Projekte teilen keine Abhängigkeiten
- Arbeit an einzelnen Projekten ohne Einfluss auf andere
- Gesamtes Repo klonen für das komplette Curriculum-Erlebnis

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Haftungsausschluss**:  
Dieses Dokument wurde mit dem KI-Übersetzungsdienst [Co-op Translator](https://github.com/Azure/co-op-translator) übersetzt. Obwohl wir Genauigkeit anstreben, beachten Sie bitte, dass automatisierte Übersetzungen Fehler oder Ungenauigkeiten enthalten können. Das Originaldokument in seiner Ursprungssprache gilt als maßgebliche Quelle. Für kritische Informationen wird eine professionelle menschliche Übersetzung empfohlen. Wir übernehmen keine Haftung für Missverständnisse oder Fehlinterpretationen, die durch die Verwendung dieser Übersetzung entstehen.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->