# AGENTS.md

## Prehľad projektu

Toto je vzdelávací repozitár pre výučbu základov webového vývoja pre začiatočníkov. Kurz je komplexný 12-týždňový program vyvinutý Microsoft Cloud Advocates, obsahujúci 24 praktických lekcií pokrývajúcich JavaScript, CSS a HTML.

### Kľúčové komponenty

- **Vzdelávací obsah**: 24 štruktúrovaných lekcií usporiadaných do modulov založených na projektoch
- **Praktické projekty**: Terrárium, Hra na písanie, Rozšírenie prehliadača, Vesmírna hra, Banková aplikácia, Code Editor a AI Chat Asistent
- **Interaktívne kvízy**: 48 kvízov s 3 otázkami v každom (pred/po lekcii)
- **Podpora viacerých jazykov**: Automatizované preklady do 50+ jazykov cez GitHub Actions
- **Technológie**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (pre AI projekty)

### Architektúra

- Vzdelávací repozitár so štruktúrou založenou na lekciách
- Každý priečinok lekcie obsahuje README, ukážky kódu a riešenia
- Samostatné projekty v oddelených adresároch (quiz-app, rôzne projekty lekcií)
- Prekladový systém využívajúci GitHub Actions (co-op-translator)
- Dokumentácia podávaná cez Docsify a dostupná ako PDF

## Príkazy na nastavenie

Tento repozitár je primárne na konzumáciu vzdelávacieho obsahu. Pre prácu s konkrétnymi projektmi:

### Nastavenie hlavného repozitára

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Nastavenie Quiz App (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Spustiť vývojový server
npm run build      # Vytvoriť pre produkciu
npm run lint       # Spustiť ESLint
```

### API Bankového projektu (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # Spustiť API server
npm run lint       # Spustiť ESLint
npm run format     # Naformátovať pomocou Prettier
```

### Projekty rozšírenia prehliadača

```bash
cd 5-browser-extension/solution
npm install
# Postupujte podľa pokynov na načítanie rozšírenia špecifických pre prehliadač
```

### Projekty vesmírnej hry

```bash
cd 6-space-game/solution
npm install
# Otvorte index.html v prehliadači alebo použite Live Server
```

### Projekt Chat (Python Backend)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Nastavte premennú prostredia GITHUB_TOKEN
python api.py
```

## Vývojový proces

### Pre prispievateľov obsahu

1. **Forknite repozitár** do svojho GitHub účtu
2. **Skloňujte svoj fork** lokálne
3. **Vytvorte novú vetvu** pre svoje zmeny
4. Robte zmeny v obsahu lekcií alebo príkladoch kódu
5. Testujte akékoľvek zmeny kódu v relevantných projektových adresároch
6. Podajte pull request podľa pravidiel prispievania

### Pre študentov

1. Forknite alebo naklonujte repozitár
2. Postupne prechádzajte adresáre lekcií
3. Čítajte README súbory pre každú lekciu
4. Vyplňte pre-lekčné kvízy na https://ff-quizzes.netlify.app/web/
5. Prejdite si príklady kódu v adresároch lekcií
6. Dokončite úlohy a výzvy
7. Absolvujte po-lekčné kvízy

### Živý vývoj

- **Dokumentácia**: Spustite `docsify serve` v koreňovom adresári (port 3000)
- **Quiz App**: Spustite `npm run dev` v adresári quiz-app
- **Projekty**: Použite VS Code Live Server rozšírenie pre HTML projekty
- **API projekty**: Spustite `npm start` v príslušných API adresároch

## Inštrukcie na testovanie

### Testovanie Quiz App

```bash
cd quiz-app
npm run lint       # Skontrolujte problémy so štýlom kódu
npm run build      # Overte, či zostavenie prebehne úspešne
```

### Testovanie Bank API

```bash
cd 7-bank-project/api
npm run lint       # Skontrolujte problémy so štýlom kódu
node server.js     # Overte, či server štartuje bez chýb
```

### Všeobecný prístup k testovaniu

- Ide o vzdelávací repozitár bez komplexných automatizovaných testov
- Manuálne testovanie sa zameriava na:
  - Príklady kódu bez chýb
  - Funkčnosť odkazov v dokumentácii
  - Úspešnosť buildov projektov
  - Dodržiavanie najlepších praktík v príkladoch

### Kontroly pred odoslaním

- Spustite `npm run lint` v adresároch s package.json
- Overte platnosť markdown odkazov
- Testujte príklady kódu v prehliadači alebo Node.js
- Skontrolujte, či preklady zachovávajú správnu štruktúru

## Pravidlá štýlu kódu

### JavaScript

- Používajte moderný ES6+ syntax
- Dodržiavajte štandardné ESLint konfigurácie v projektoch
- Používajte zrozumiteľné názvy premenných a funkcií pre vzdelávaciu jasnosť
- Pridávajte komentáre vysvetľujúce koncepty pre študentov
- Formátujte kód pomocou Prettier kde je nastavený

### HTML/CSS

- Semantické HTML5 prvky
- Principy responzívneho dizajnu
- Čisté pomenovanie tried
- Komentáre vysvetľujúce CSS techniky pre študentov

### Python

- Štýlové pravidlá PEP 8
- Jasné, vzdelávacie príklady kódu
- Typové anotácie tam, kde pomáhajú pri učení

### Markdown dokumentácia

- Jasná hierarchia nadpisov
- Kódové bloky s určením jazyka
- Odkazy na doplnkové zdroje
- Snímky obrazovky a obrázky v adresároch `images/`
- Alt text pre obrázky pre prístupnosť

### Organizácia súborov

- Lekcie číslované postupne (1-getting-started-lessons, 2-js-basics, atď.)
- Každý projekt má adresáre `solution/` a často `start/` alebo `your-work/`
- Obrázky uložené v špecifických priečinkoch lekcií `images/`
- Preklady v štruktúre `translations/{language-code}/`

## Build a nasadenie

### Nasadenie Quiz App (Azure Static Web Apps)

quiz-app je nakonfigurovaný pre nasadenie na Azure Static Web Apps:

```bash
cd quiz-app
npm run build      # Vytvára priečinok dist/
# Nasadzuje cez GitHub Actions workflow pri push do main
```

Konfigurácia Azure Static Web Apps:
- **Umiestnenie aplikácie**: `/quiz-app`
- **Výstupné miesto**: `dist`
- **Workflow**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### Generovanie PDF dokumentácie

```bash
npm install                    # Inštalujte docsify-to-pdf
npm run convert               # Vygenerujte PDF z docs
```

### Dokumentácia cez Docsify

```bash
npm install -g docsify-cli    # Nainštalujte Docsify globálne
docsify serve                 # Spustite na localhost:3000
```

### Buildy špecifické pre projekt

Každý projektový adresár môže mať svoj vlastný build proces:
- Vue projekty: `npm run build` vytvára produkčné balíky
- Statické projekty: žiadny build krok, súbory sa servujú priamo

## Pravidlá pre pull requesty

### Formát názvov

Používajte jasné a popisné názvy, ktoré indikujú oblasť zmeny:
- `[Quiz-app] Pridanie nového kvízu pre lekciu X`
- `[Lesson-3] Oprava preklepu v projekte terrarium`
- `[Translation] Pridanie španielskeho prekladu pre lekciu 5`
- `[Docs] Aktualizácia inštrukcií na nastavenie`

### Povinné kontroly

Pred podaním PR:

1. **Kvalita kódu**:
   - Spustite `npm run lint` v dotknutých projektových adresároch
   - Opravte všetky linting chyby a varovania

2. **Overenie build procesu**:
   - Spustite `npm run build` ak je to potrebné
   - Zabezpečte, že neexistujú chyby pri buildovaní

3. **Validácia odkazov**:
   - Otestujte všetky markdown odkazy
   - Overte funkčnosť referencií obrázkov

4. **Kontrola obsahu**:
   - Korektúra pravopisných a gramatických chýb
   - Overte správnosť a vzdelávací charakter príkladov kódu
   - Skontrolujte, či preklady zachovávajú pôvodný význam

### Požiadavky na príspevky

- Súhlas s Microsoft CLA (automatická kontrola pri prvom PR)
- Dodržiavanie [Microsoft Open Source Kódexu správania](https://opensource.microsoft.com/codeofconduct/)
- Viac informácií v [CONTRIBUTING.md](./CONTRIBUTING.md)
- Pri PR uvádzať čísla issues, ak sú relevantné

### Proces recenzie

- PR sú kontrolované správcami a komunitou
- Priorita na vzdelávaciu jasnosť
- Príklady kódu musia dodržiavať aktuálne najlepšie praktiky
- Preklady recenzované na presnosť a kultúrnu vhodnosť

## Prekladový systém

### Automatizovaný preklad

- Používa GitHub Actions s workflow co-op-translator
- Automaticky prekladá do 50+ jazykov
- Zdrojové súbory v hlavných adresároch
- Preložené súbory v adresároch `translations/{language-code}/`

### Pridávanie manuálnych vylepšení prekladu

1. Nájdite súbor v `translations/{language-code}/`
2. Vylepšujte obsah so zachovaním štruktúry
3. Zaistite, aby príklady kódu boli funkčné
4. Otestujte lokalizovaný kvízový obsah

### Metaúdaje prekladu

Preložené súbory obsahujú metaúdajový záhlavok:
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

## Ladenie a riešenie problémov

### Bežné problémy

**Quiz app sa nespustí**:
- Skontrolujte verziu Node.js (odporúčané v14+)
- Vymažte `node_modules` a `package-lock.json`, znova spustite `npm install`
- Skontrolujte konflikty portov (predvolené: Vite používa port 5173)

**API server sa nespustí**:
- Overte, že verzia Node.js je minimálne node >=10
- Skontrolujte, či port nie je už obsadený
- Uistite sa, že všetky závislosti sú nainštalované cez `npm install`

**Rozšírenie prehliadača sa nenačíta**:
- Skontrolujte správne naformátovanie manifest.json
- Prehliadačový konzolový výstup pre chyby
- Postupujte podľa inštrukcií inštalácie podľa prehliadača

**Problémy s Python chat projektom**:
- Skontrolujte inštaláciu balíčka OpenAI: `pip install openai`
- Overte nastavenie premennej prostredia GITHUB_TOKEN
- Skontrolujte oprávnenia prístupu k GitHub modelom

**Docsify neservíruje dokumentáciu**:
- Nainštalujte docsify-cli globálne: `npm install -g docsify-cli`
- Spusťte príkaz v koreňovom adresári repozitára
- Skontrolujte, že existuje `docs/_sidebar.md`

### Tipy pre vývojové prostredie

- Používajte VS Code s Live Server rozšírením pre HTML projekty
- Nainštalujte ESLint a Prettier rozšírenia pre konzistentné formátovanie
- Použite DevTools v prehliadači na ladenie JavaScriptu
- Pre Vue projekty nainštalujte Vue DevTools rozšírenie prehliadača

### Výkonnostné aspekty

- Veľký počet prekladových súborov (50+ jazykov) robí kompletné klony veľkými
- Pre prácu len s obsahom použite plytký klon: `git clone --depth 1`
- Vylúčte preklady z vyhľadávania pri práci s anglickým obsahom
- Build procesy môžu byť pomalé pri prvom spustení (npm install, Vite build)

## Bezpečnostné aspekty

### Premenné prostredia

- API kľúče nikdy neukladajte do repozitára
- Používajte `.env` súbory (už zahrnuté v `.gitignore`)
- Požadované premenné prostredia dokumentujte v README projektov

### Python projekty

- Používajte virtuálne prostredia: `python -m venv venv`
- Udržiavajte závislosti aktuálne
- GitHub tokeny majte s minimálnymi potrebnými právami

### Prístup k GitHub Modelom

- Vyžadujú sa osobné prístupové tokeny (PAT)
- Tokeny ukladajte ako premenné prostredia
- Nikdy neukladajte tokeny alebo prihlasovacie údaje do repozitára

## Doplnkové poznámky

### Cieľová skupina

- Úplní začiatočníci vo webovom vývoji
- Študenti a samoštudenti
- Učitelia používajúci kurz v triedach
- Obsah je navrhnutý pre prístupnosť a postupné zlepšovanie zručností

### Vzdelávacia filozofia

- Projektovo orientované učenie
- Časté kontrolné testy (kvízy)
- Praktické cvičenia v písaní kódu
- Príklady z reálneho sveta
- Zameranie na základy pred frameworkami

### Údržba repozitára

- Aktívna komunita študentov a prispievateľov
- Pravidelné aktualizácie závislostí a obsahu
- Sledovanie issues a diskusií správcami
- Automatizované aktualizácie prekladov cez GitHub Actions

### Súvisiace zdroje

- [Microsoft Learn moduly](https://docs.microsoft.com/learn/)
- [Student Hub zdroje](https://docs.microsoft.com/learn/student-hub/)
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) odporúčaný pre študentov
- Ďalšie kurzy: Generatívna AI, Data Science, ML, IoT dostupné

### Práca s konkrétnymi projektmi

Podrobné inštrukcie k jednotlivým projektom nájdete v README súboroch:
- `quiz-app/README.md` - Vue 3 quiz aplikácia
- `7-bank-project/README.md` - Banková aplikácia s autentifikáciou
- `5-browser-extension/README.md` - Vývoj rozšírenia prehliadača
- `6-space-game/README.md` - Vývoj hry na canvas
- `9-chat-project/README.md` - Projekt AI chat asistenta

### Štruktúra monorepa

Aj keď nejde o tradičné monorepo, tento repozitár obsahuje viacero nezávislých projektov:
- Každá lekcia je samostatná
- Projekty nesdielajú závislosti
- Pracujte na jednotlivých projektoch bez ovplyvnenia ostatných
- Naklonujte celý repozitár pre kompletný kurzový zážitok

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Zrieknutie sa zodpovednosti**:  
Tento dokument bol preložený pomocou služby AI prekladu [Co-op Translator](https://github.com/Azure/co-op-translator). Hoci sa snažíme o presnosť, majte, prosím, na pamäti, že automatizované preklady môžu obsahovať chyby alebo nepresnosti. Originálny dokument v jeho pôvodnom jazyku by mal byť považovaný za autoritatívny zdroj. Pre kritické informácie sa odporúča profesionálny ľudský preklad. Nie sme zodpovední za akékoľvek nepochopenia alebo nesprávne interpretácie vyplývajúce z použitia tohto prekladu.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->