# AGENTS.md

## Panoramica del Progetto

Questo è un repository didattico per insegnare le basi dello sviluppo web ai principianti. Il curriculum è un corso completo di 12 settimane sviluppato dai Microsoft Cloud Advocates, con 24 lezioni pratiche che coprono JavaScript, CSS e HTML.

### Componenti Chiave

- **Contenuti Educativi**: 24 lezioni strutturate organizzate in moduli basati su progetti
- **Progetti Pratici**: Terrario, Gioco di Digitazione, Estensione Browser, Gioco Spaziale, App Bancaria, Editor di Codice e Assistente Chat AI
- **Quiz Interattivi**: 48 quiz con 3 domande ciascuno (valutazioni pre/post lezione)
- **Supporto Multilingue**: Traduzioni automatiche per oltre 50 lingue tramite GitHub Actions
- **Tecnologie**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (per progetti AI)

### Architettura

- Repository educativo con struttura basata sulle lezioni
- Ogni cartella lezione contiene README, esempi di codice e soluzioni
- Progetti indipendenti in directory separate (quiz-app, vari progetti delle lezioni)
- Sistema di traduzione usando GitHub Actions (co-op-translator)
- Documentazione servita tramite Docsify e disponibile in PDF

## Comandi di Setup

Questo repository è principalmente per il consumo di contenuti educativi. Per lavorare con progetti specifici:

### Setup Principale del Repository

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Setup Quiz App (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Avvia il server di sviluppo
npm run build      # Compila per la produzione
npm run lint       # Esegui ESLint
```

### API Progetto Bancario (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # Avvia il server API
npm run lint       # Esegui ESLint
npm run format     # Format con Prettier
```

### Progetti Estensioni Browser

```bash
cd 5-browser-extension/solution
npm install
# Seguire le istruzioni specifiche del browser per il caricamento delle estensioni
```

### Progetti Gioco Spaziale

```bash
cd 6-space-game/solution
npm install
# Apri index.html nel browser o usa Live Server
```

### Progetto Chat (Backend Python)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Imposta la variabile d'ambiente GITHUB_TOKEN
python api.py
```

## Flusso di Lavoro Sviluppo

### Per i Contributori di Contenuti

1. **Fai il fork del repository** sul tuo account GitHub
2. **Clona il tuo fork** localmente
3. **Crea un nuovo branch** per le tue modifiche
4. Apporta modifiche ai contenuti della lezione o agli esempi di codice
5. Testa ogni modifica al codice nelle directory dei progetti rilevanti
6. Invia pull request seguendo le linee guida di contributo

### Per gli Studenti

1. Fai fork o clona il repository
2. Naviga sequenzialmente nelle directory delle lezioni
3. Leggi i file README per ogni lezione
4. Completa i quiz pre-lezione su https://ff-quizzes.netlify.app/web/
5. Lavora sugli esempi di codice nelle cartelle delle lezioni
6. Completa compiti e sfide
7. Sostieni i quiz post-lezione

### Sviluppo Live

- **Documentazione**: Esegui `docsify serve` nella root (porta 3000)
- **Quiz App**: Esegui `npm run dev` nella directory quiz-app
- **Progetti**: Usa l’estensione VS Code Live Server per progetti HTML
- **Progetti API**: Esegui `npm start` nelle rispettive directory API

## Istruzioni per i Test

### Test Quiz App

```bash
cd quiz-app
npm run lint       # Controlla problemi di stile del codice
npm run build      # Verifica che la compilazione abbia successo
```

### Test API Bancaria

```bash
cd 7-bank-project/api
npm run lint       # Controlla problemi di stile del codice
node server.js     # Verifica che il server si avvii senza errori
```

### Approccio Generale ai Test

- Questo è un repository educativo senza test automatizzati completi
- Il testing manuale si concentra su:
  - Gli esempi di codice funzionano senza errori
  - I link nella documentazione sono funzionanti
  - Le build dei progetti completano con successo
  - Gli esempi rispettano le best practice

### Controlli Pre-Invio

- Esegui `npm run lint` nelle directory con package.json
- Verifica che i link markdown siano validi
- Testa gli esempi di codice in browser o Node.js
- Controlla che le traduzioni mantengano la struttura corretta

## Linee Guida per lo Stile del Codice

### JavaScript

- Usa sintassi moderna ES6+
- Segui le configurazioni ESLint standard fornite nei progetti
- Usa nomi significativi per variabili e funzioni per chiarezza didattica
- Aggiungi commenti che spiegano i concetti per gli studenti
- Formattta usando Prettier dove configurato

### HTML/CSS

- Elementi semantici HTML5
- Principi di design responsivo
- Convenzioni chiare per la nomenclatura delle classi
- Commenti che spiegano le tecniche CSS per gli studenti

### Python

- Linee guida di stile PEP 8
- Esempi di codice chiari e didattici
- Suggerimenti di tipo dove utili per l’apprendimento

### Documentazione Markdown

- Gerarchia chiara delle intestazioni
- Blocchi di codice con specifica linguaggio
- Link a risorse aggiuntive
- Screenshot e immagini nelle cartelle `images/`
- Testo alternativo per le immagini per accessibilità

### Organizzazione dei File

- Lezioni numerate sequenzialmente (1-getting-started-lessons, 2-js-basics, ecc.)
- Ogni progetto ha directory `solution/` e spesso `start/` o `your-work/`
- Immagini archiviate nelle cartelle `images/` specifiche della lezione
- Traduzioni in struttura `translations/{language-code}/`

## Build e Deployment

### Deployment Quiz App (Azure Static Web Apps)

La quiz-app è configurata per il deployment su Azure Static Web Apps:

```bash
cd quiz-app
npm run build      # Crea la cartella dist/
# Esegue il deploy tramite workflow di GitHub Actions al push su main
```

Configurazione Azure Static Web Apps:
- **Posizione app**: `/quiz-app`
- **Cartella output**: `dist`
- **Workflow**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### Generazione PDF Documentazione

```bash
npm install                    # Installa docsify-to-pdf
npm run convert               # Genera PDF da docs
```

### Documentazione Docsify

```bash
npm install -g docsify-cli    # Installa Docsify globalmente
docsify serve                 # Servi su localhost:3000
```

### Build Specifici per Progetto

Ogni directory progetto può avere un proprio processo di build:
- Progetti Vue: `npm run build` crea bundle di produzione
- Progetti statici: nessun passaggio di build, servire i file direttamente

## Linee Guida per le Pull Request

### Formato del Titolo

Usa titoli chiari e descrittivi che indicano l’area di modifica:
- `[Quiz-app] Aggiunta nuovo quiz per la lezione X`
- `[Lesson-3] Correzione errore di battitura nel progetto terrario`
- `[Translation] Aggiunta traduzione spagnola per la lezione 5`
- `[Docs] Aggiornate istruzioni di setup`

### Controlli Richiesti

Prima di inviare una PR:

1. **Qualità del Codice**:
   - Esegui `npm run lint` nelle directory dei progetti interessati
   - Correggi tutti errori e avvisi di lint

2. **Verifica Build**:
   - Esegui `npm run build` se applicabile
   - Assicurati che non ci siano errori di build

3. **Validazione Link**:
   - Testa tutti i link markdown
   - Verifica riferimenti alle immagini

4. **Revisione Contenuti**:
   - Controllo ortografia e grammatica
   - Assicurati che gli esempi di codice siano corretti e didattici
   - Verifica che le traduzioni mantengano il significato originale

### Requisiti di Contributo

- Accetta la Microsoft CLA (verifica automatica alla prima PR)
- Segui il [Codice di Condotta Open Source Microsoft](https://opensource.microsoft.com/codeofconduct/)
- Consulta [CONTRIBUTING.md](./CONTRIBUTING.md) per dettagli
- Riferisci numeri di issue nella descrizione PR se appropriato

### Processo di Revisione

- Le PR sono revisionate da maintainer e community
- Si dà priorità alla chiarezza didattica
- Gli esempi di codice devono seguire le migliori pratiche correnti
- Le traduzioni sono riviste per accuratezza e adeguatezza culturale

## Sistema di Traduzione

### Traduzione Automatica

- Usa GitHub Actions con workflow co-op-translator
- Traduce automaticamente in oltre 50 lingue
- File sorgente nelle directory principali
- File tradotti in directory `translations/{language-code}/`

### Aggiungere Miglioramenti Manuali

1. Trova il file in `translations/{language-code}/`
2. Apporta miglioramenti preservando la struttura
3. Assicurati che gli esempi di codice rimangano funzionanti
4. Testa ogni contenuto quiz localizzato

### Metadata Traduzione

I file tradotti includono header di metadata:
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

## Debug e Risoluzione Problemi

### Problemi Comuni

**Quiz app non si avvia**:
- Controlla versione Node.js (consigliata v14+)
- Cancella `node_modules` e `package-lock.json`, esegui di nuovo `npm install`
- Controlla conflitti di porta (default: Vite usa porta 5173)

**Server API non si avvia**:
- Verifica che versione Node.js sia almeno (node >=10)
- Controlla se la porta è già in uso
- Assicurati che tutte le dipendenze siano installate con `npm install`

**Estensione browser non si carica**:
- Verifica che manifest.json sia ben formato
- Controlla la console del browser per errori
- Segui le istruzioni specifiche di installazione per il browser

**Problemi con progetto chat Python**:
- Assicurati che il pacchetto OpenAI sia installato: `pip install openai`
- Verifica che la variabile ambiente GITHUB_TOKEN sia impostata
- Controlla i permessi di accesso ai Modelli GitHub

**Docsify non serve la documentazione**:
- Installa docsify-cli globalmente: `npm install -g docsify-cli`
- Avvia dalla root del repository
- Verifica che `docs/_sidebar.md` esista

### Consigli Ambiente di Sviluppo

- Usa VS Code con estensione Live Server per progetti HTML
- Installa estensioni ESLint e Prettier per formattazione coerente
- Usa gli strumenti DevTools del browser per il debug JavaScript
- Per progetti Vue, installa l’estensione Vue DevTools per browser

### Considerazioni sulle Prestazioni

- Gran numero di file tradotti (oltre 50 lingue) rende il clone completo pesante
- Usa clone shallow se lavori solo sui contenuti: `git clone --depth 1`
- Escludi le traduzioni dalle ricerche quando lavori solo su contenuti in inglese
- I processi di build possono essere lenti alla prima esecuzione (npm install, build Vite)

## Considerazioni di Sicurezza

### Variabili d’Ambiente

- Le chiavi API non devono mai essere committate nel repository
- Usa file `.env` (già in `.gitignore`)
- Documenta variabili d’ambiente richieste nei README dei progetti

### Progetti Python

- Usa ambienti virtuali: `python -m venv venv`
- Mantieni aggiornate le dipendenze
- I token GitHub devono avere permessi minimi necessari

### Accesso Modelli GitHub

- Sono richiesti Personal Access Tokens (PAT) per i Modelli GitHub
- I token devono essere conservati come variabili ambiente
- Mai committare token o credenziali

## Note Aggiuntive

### Pubblico Target

- Principianti completi nello sviluppo web
- Studenti e autodidatti
- Insegnanti che usano il curriculum in aula
- Contenuti progettati per accessibilità e sviluppo graduale delle competenze

### Filosofia Educativa

- Approccio basato su progetti
- Verifiche di apprendimento frequenti (quiz)
- Esercizi pratici di coding
- Esempi di applicazioni reali
- Focus sulle basi prima dei framework

### Manutenzione del Repository

- Comunità attiva di studenti e contributori
- Aggiornamenti regolari di dipendenze e contenuti
- Issue e discussioni monitorate dai maintainer
- Aggiornamenti alle traduzioni automatici via GitHub Actions

### Risorse Correlate

- [Moduli Microsoft Learn](https://docs.microsoft.com/learn/)
- [Risorse Student Hub](https://docs.microsoft.com/learn/student-hub/)
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) consigliato per gli studenti
- Corsi aggiuntivi: curricula di IA generativa, Data Science, ML, IoT disponibili

### Lavorare con Progetti Specifici

Per istruzioni dettagliate sui singoli progetti, consulta i file README in:
- `quiz-app/README.md` - Applicazione quiz Vue 3
- `7-bank-project/README.md` - Applicazione bancaria con autenticazione
- `5-browser-extension/README.md` - Sviluppo estensione browser
- `6-space-game/README.md` - Sviluppo gioco basato su Canvas
- `9-chat-project/README.md` - Progetto assistente chat AI

### Struttura Monorepo

Sebbene non sia un monorepo tradizionale, questo repository contiene più progetti indipendenti:
- Ogni lezione è autonoma
- I progetti non condividono dipendenze
- Lavora sui singoli progetti senza influenzarne altri
- Clona l’intero repo per l’esperienza completa del curriculum

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Disclaimer**:  
Questo documento è stato tradotto utilizzando il servizio di traduzione AI [Co-op Translator](https://github.com/Azure/co-op-translator). Pur impegnandoci per l'accuratezza, si prega di notare che le traduzioni automatiche possono contenere errori o imprecisioni. Il documento originale nella sua lingua madre deve essere considerato la fonte autorevole. Per informazioni critiche, si consiglia una traduzione professionale effettuata da un umano. Non siamo responsabili per eventuali incomprensioni o interpretazioni errate derivanti dall'uso di questa traduzione.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->