# AGENTS.md

## Prezentare generală a proiectului

Acesta este un depozit curricular educațional pentru predarea elementelor fundamentale ale dezvoltării web începătorilor. Curriculumul este un curs cuprinzător de 12 săptămâni, dezvoltat de Microsoft Cloud Advocates, care include 24 de lecții practice acoperind JavaScript, CSS și HTML.

### Componente cheie

- **Conținut educațional**: 24 de lecții structurate organizate în module bazate pe proiecte
- **Proiecte practice**: Terrarium, Joc de tastare, Extensie pentru browser, Joc spațial, Aplicație bancară, Editor de cod și Asistent chat AI
- **Chestionare interactive**: 48 de chestionare cu câte 3 întrebări fiecare (evaluări pre/post-lecție)
- **Suport multi-limbă**: Traduceri automate pentru peste 50 de limbi prin GitHub Actions
- **Tehnologii**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (pentru proiectele AI)

### Arhitectură

- Depozit educațional cu structură bazată pe lecții
- Fiecare folder de lecție conține README, exemple de cod și soluții
- Proiecte autonome în directoare separate (quiz-app, diverse proiecte din lecții)
- Sistem de traducere folosind GitHub Actions (co-op-translator)
- Documentația este servită prin Docsify și disponibilă ca PDF

## Comenzi de configurare

Acest depozit este destinat în principal consumului de conținut educațional. Pentru a lucra cu proiecte specifice:

### Configurare depozit principal

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Configurare Quiz App (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Pornește serverul de dezvoltare
npm run build      # Compilează pentru producție
npm run lint       # Rulează ESLint
```

### API Proiect Bancar (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # Pornește serverul API
npm run lint       # Rulează ESLint
npm run format     # Formatează cu Prettier
```

### Proiecte Extensie de Browser

```bash
cd 5-browser-extension/solution
npm install
# Urmați instrucțiunile specifice browserului pentru încărcarea extensiilor
```

### Proiecte Joc Spațial

```bash
cd 6-space-game/solution
npm install
# Deschide index.html în browser sau folosește Live Server
```

### Proiect Chat (backend Python)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Setează variabila de mediu GITHUB_TOKEN
python api.py
```

## Flux de dezvoltare

### Pentru contribuitori de conținut

1. **Furcați depozitul** în contul vostru GitHub
2. **Clonați furca local**
3. **Creați un nou branch** pentru modificările voastre
4. Faceți modificări la conținutul lecțiilor sau la exemplele de cod
5. Testați orice modificare de cod în directoarele relevante ale proiectului
6. Trimiteți pull request-uri respectând ghidul de contribuție

### Pentru cursanți

1. Fork sau clonează depozitul
2. Navigați secvențial prin directoarele lecțiilor
3. Citiți fișierele README pentru fiecare lecție
4. Completați chestionarele pre-lecție la https://ff-quizzes.netlify.app/web/
5. Parcurgeți exemplele de cod din folderele lecțiilor
6. Finalizați temele și provocările
7. Susțineți chestionarele post-lecție

### Dezvoltare Live

- **Documentație**: Rulați `docsify serve` din rădăcină (port 3000)
- **Quiz App**: Rulați `npm run dev` în directorul quiz-app
- **Proiecte**: Folosiți extensia VS Code Live Server pentru proiectele HTML
- **Proiecte API**: Rulați `npm start` în directoarele API relevante

## Instrucțiuni de testare

### Testare Quiz App

```bash
cd quiz-app
npm run lint       # Verifică problemele de stil ale codului
npm run build      # Verifică dacă compilarea reușește
```

### Testare Bank API

```bash
cd 7-bank-project/api
npm run lint       # Verifica problemele de stil de cod
node server.js     # Verifică dacă serverul pornește fără erori
```

### Abordare generală a testării

- Acesta este un depozit educațional fără teste automate complete
- Testarea manuală se concentrează pe:
  - Exemplele de cod să ruleze fără erori
  - Linkurile din documentație să funcționeze corect
  - Construirea proiectelor să fie finalizată cu succes
  - Exemplele să respecte cele mai bune practici

### Verificări înainte de trimitere

- Rulați `npm run lint` în directoarele cu package.json
- Verificați dacă linkurile markdown sunt valide
- Testați exemplele de cod în browser sau în Node.js
- Asigurați-vă că traducerile păstrează structura corectă

## Ghid de stil pentru cod

### JavaScript

- Folosiți sintaxa modernă ES6+
- Respectați configurațiile standard ESLint oferite în proiecte
- Utilizați nume de variabile și funcții semnificative pentru claritate educațională
- Adăugați comentarii explicative pentru cursanți
- Formatați folosind Prettier acolo unde este configurat

### HTML/CSS

- Elemente semantice HTML5
- Principii de design responsive
- Convenții clare de denumire a claselor
- Comentarii care explică tehnicile CSS pentru cursanți

### Python

- Respectați ghidurile de stil PEP 8
- Exemple de cod clare și educaționale
- Indicații de tip unde sunt utile pentru învățare

### Documentație Markdown

- Ierarhie clară a titlurilor
- Blocuri de cod cu specificație de limbaj
- Linkuri către resurse suplimentare
- Capturi de ecran și imagini în directoarele `images/`
- Text alternativ pentru imagini pentru accesibilitate

### Organizarea fișierelor

- Lecțiile numerotate secvențial (1-getting-started-lessons, 2-js-basics etc.)
- Fiecare proiect are directoare `solution/` și adesea `start/` sau `your-work/`
- Imaginile sunt stocate în foldere specifice lecțiilor `images/`
- Traducerile în structura `translations/{language-code}/`

## Build și implementare

### Implementarea Quiz App (Azure Static Web Apps)

quiz-app este configurat pentru implementarea pe Azure Static Web Apps:

```bash
cd quiz-app
npm run build      # Creează folderul dist/
# Face deploy prin workflow-ul GitHub Actions la push în main
```

Configurare Azure Static Web Apps:
- **Locația aplicației**: `/quiz-app`
- **Locația de output**: `dist`
- **Workflow**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### Generarea PDF documentație

```bash
npm install                    # Instalează docsify-to-pdf
npm run convert               # Generează PDF din docs
```

### Documentație Docsify

```bash
npm install -g docsify-cli    # Instalează Docsify la nivel global
docsify serve                 # Servește pe localhost:3000
```

### Build-uri specifice proiectelor

Fiecare director de proiect poate avea propriul proces de build:
- Proiecte Vue: `npm run build` creează pachete de producție
- Proiecte statice: Fără pas de build, se servesc fișierele direct

## Ghid pentru pull request-uri

### Formatul titlului

Folosiți titluri clare și descriptive care indică zona de modificare:
- `[Quiz-app] Adaugă chestionar nou pentru lecția X`
- `[Lesson-3] Corectează greșeală de scriere în proiectul terrarium`
- `[Translation] Adaugă traducere în spaniolă pentru lecția 5`
- `[Docs] Actualizează instrucțiuni de configurare`

### Verificări obligatorii

Înainte de a trimite un PR:

1. **Calitatea codului**:
   - Rulați `npm run lint` în directoarele proiectului afectat
   - Remediați toate erorile și avertismentele lint

2. **Verificarea build-ului**:
   - Rulați `npm run build` dacă este cazul
   - Asigurați-vă că nu apar erori în build

3. **Validarea linkurilor**:
   - Testați toate linkurile markdown
   - Verificați că referințele imaginilor funcționează

4. **Revizuirea conținutului**:
   - Corectați ortografia și gramatica
   - Asigurați-vă că exemplele de cod sunt corecte și educaționale
   - Verificați dacă traducerile păstrează sensul original

### Cerințe pentru contribuții

- Acceptați CLA Microsoft (verificare automată la primul PR)
- Respectați [Codul de conduită Microsoft Open Source](https://opensource.microsoft.com/codeofconduct/)
- Consultați [CONTRIBUTING.md](./CONTRIBUTING.md) pentru detalii
- Referiți numerele issue-urilor în descrierea PR-ului, dacă este cazul

### Procesul de revizuire

- PR-urile sunt revizuite de mentori și comunitate
- Prioritate pentru claritatea educațională
- Exemplele de cod trebuie să urmeze cele mai bune practici actuale
- Traducerile sunt verificate pentru acuratețe și adaptare culturală

## Sistem de traducere

### Traducere automată

- Folosește GitHub Actions cu workflow co-op-translator
- Traduce automat în peste 50 de limbi
- Fișiere sursă în directoarele principale
- Fișiere traduse în directoarele `translations/{language-code}/`

### Adăugarea îmbunătățirilor manuale

1. Găsiți fișierul în `translations/{language-code}/`
2. Faceți îmbunătățiri păstrând structura
3. Asigurați-vă că exemplele de cod rămân funcționale
4. Testați eventualele conținuturi locale din chestionare

### Metadate traducere

Fișierele traduse includ antet cu metadate:
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

## Depanare și rezolvarea problemelor

### Probleme comune

**Quiz app nu pornește**:
- Verificați versiunea Node.js (recomandat v14+)
- Ștergeți `node_modules` și `package-lock.json`, rulați iar `npm install`
- Verificați conflictele de port (implict: Vite folosește portul 5173)

**Serverul API nu pornește**:
- Asigurați-vă că versiunea Node.js este minim node >=10
- Verificați dacă portul este ocupat
- Verificați că toate dependențele sunt instalate cu `npm install`

**Extensia de browser nu se încarcă**:
- Verificați formatul corect al manifest.json
- Consultați consola browserului pentru erori
- Urmați instrucțiunile specifice browserului pentru instalarea extensiei

**Probleme proiect chat Python**:
- Asigurați-vă că pachetul OpenAI este instalat: `pip install openai`
- Verificați dacă variabila de mediu GITHUB_TOKEN este setată
- Verificați permisiunile de acces la GitHub Models

**Docsify nu servește documentația**:
- Instalați global docsify-cli: `npm install -g docsify-cli`
- Rulați din directorul rădăcină al depozitului
- Verificați existența fișierului `docs/_sidebar.md`

### Sfaturi pentru mediul de dezvoltare

- Folosiți VS Code cu extensia Live Server pentru proiectele HTML
- Instalați extensiile ESLint și Prettier pentru formatare consistentă
- Folosiți DevTools ale browserului pentru depanarea JavaScript
- Pentru proiecte Vue, instalați extensia Vue DevTools în browser

### Considerații de performanță

- Numărul mare de fișiere traduse (50+ limbi) face clonările totale mari
- Folosiți clonarea superficială dacă lucrați doar pe conținut: `git clone --depth 1`
- Excludeți traducerile din căutări când lucrați pe conținut în engleză
- Procesele de build pot fi lente la prima rulare (npm install, build Vite)

## Considerații de securitate

### Variabile de mediu

- Cheile API nu trebuie niciodată comise în depozit
- Folosiți fișiere `.env` (deja în `.gitignore`)
- Documentați variabilele de mediu necesare în README-urile proiectelor

### Proiecte Python

- Folosiți medii virtuale: `python -m venv venv`
- Mențineți dependențele actualizate
- Token-urile GitHub trebuie să aibă permisiuni minime necesare

### Acces GitHub Models

- Sunt necesare token-uri personale de acces (PAT) pentru GitHub Models
- Token-urile trebuie păstrate ca variabile de mediu
- Nu comiteți niciodată token-uri sau credențiale

## Note suplimentare

### Public țintă

- Începători compleți în dezvoltare web
- Studenți și autodidacți
- Profesori care folosesc curriculumul în săli de clasă
- Conținut gândit pentru accesibilitate și dezvoltare graduală a competențelor

### Filosofie educațională

- Abordare bazată pe proiecte
- Verificări frecvente ale cunoștințelor (chestionare)
- Exerciții practice de codare
- Exemple aplicate din lumea reală
- Accent pe elementele fundamentale înaintea framework-urilor

### Mentenanță depozit

- Comunitate activă de cursanți și contribuitori
- Actualizări regulate ale dependențelor și conținutului
- Probleme și discuții monitorizate de mentori
- Actualizări automate ale traducerilor prin GitHub Actions

### Resurse conexe

- [Module Microsoft Learn](https://docs.microsoft.com/learn/)
- [Resurse Student Hub](https://docs.microsoft.com/learn/student-hub/)
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) recomandat pentru cursanți
- Cursuri suplimentare: AI Generativ, Știința datelor, ML, curricula IoT disponibile

### Lucrul cu proiecte specifice

Pentru instrucțiuni detaliate despre proiectele individuale, consultați fișierele README din:
- `quiz-app/README.md` - aplicație quiz Vue 3
- `7-bank-project/README.md` - aplicație bancară cu autentificare
- `5-browser-extension/README.md` - dezvoltarea extensiilor pentru browser
- `6-space-game/README.md` - dezvoltarea jocurilor canvas
- `9-chat-project/README.md` - proiect asistent chat AI

### Structura monorepo

Deși nu este un monorepo tradițional, acest depozit conține mai multe proiecte independente:
- Fiecare lecție este autonomă
- Proiectele nu împart dependențe
- Lucrați pe proiectele individuale fără a afecta altele
- Clonați întregul repo pentru experiența completă a curriculumului

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Declinare a responsabilității**:
Acest document a fost tradus folosind serviciul de traducere AI [Co-op Translator](https://github.com/Azure/co-op-translator). Deși ne străduim pentru acuratețe, vă rugăm să rețineți că traducerile automate pot conține erori sau inexactități. Documentul original în limba sa nativă trebuie considerat sursa autoritară. Pentru informații critice, se recomandă traducerea profesională realizată de o persoană. Nu ne asumăm responsabilitatea pentru eventuale neînțelegeri sau interpretări greșite rezultate din utilizarea acestei traduceri.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->