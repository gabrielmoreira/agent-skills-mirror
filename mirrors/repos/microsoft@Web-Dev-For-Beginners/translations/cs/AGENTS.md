# AGENTS.md

## Přehled projektu

Toto je vzdělávací repozitář kurikula pro výuku základů webového vývoje pro začátečníky. Kurikulum je komplexní 12týdenní kurz vyvinutý týmem Microsoft Cloud Advocates, obsahující 24 praktických lekcí pokrývajících JavaScript, CSS a HTML.

### Klíčové komponenty

- **Vzdělávací obsah**: 24 strukturovaných lekcí uspořádaných do modulů založených na projektech
- **Praktické projekty**: Terrárium, Hra na psaní, Prodlžek prohlížeče, Hra ve vesmíru, Bankovní aplikace, Kódový editor a AI chatovací asistent
- **Interaktivní kvízy**: 48 kvízů po 3 otázkách (testy před a po lekci)
- **Podpora více jazyků**: Automatizované překlady do více než 50 jazyků pomocí GitHub Actions
- **Technologie**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (pro AI projekty)

### Architektura

- Vzdělávací repozitář se strukturou založenou na lekcích
- Každá složka lekce obsahuje README, příklady kódu a řešení
- Samostatné projekty v oddělených adresářích (quiz-app, různé projektové lekce)
- Překladový systém využívající GitHub Actions (co-op-translator)
- Dokumentace podávaná přes Docsify a dostupná jako PDF

## Příkazy k nastavení

Tento repozitář je primárně určen pro konzumaci vzdělávacího obsahu. Pro práci s konkrétními projekty:

### Nastavení hlavního repozitáře

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Nastavení Quiz App (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Spustit vývojový server
npm run build      # Sestavit pro produkci
npm run lint       # Spustit ESLint
```

### Bankovní API projekt (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # Spusťte API server
npm run lint       # Spusťte ESLint
npm run format     # Naformátujte pomocí Prettier
```

### Projekty pro prodloužení prohlížeče

```bash
cd 5-browser-extension/solution
npm install
# Postupujte podle pokynů pro načítání rozšíření specifických pro prohlížeč
```

### Projekty hry ve vesmíru

```bash
cd 6-space-game/solution
npm install
# Otevřete index.html v prohlížeči nebo použijte Live Server
```

### Chatovací projekt (Python Backend)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Nastavte proměnnou prostředí GITHUB_TOKEN
python api.py
```

## Vývojový pracovní postup

### Pro přispěvatele obsahu

1. **Vytvořte fork** repozitáře do svého GitHub účtu
2. **Klonujte svůj fork** lokálně
3. **Vytvořte novou větev** pro své změny
4. Proveďte změny ve vzdělávacím obsahu nebo příkladech kódu
5. Otestujte jakékoliv změny kódu v příslušných adresářích projektů
6. Odešlete pull requesty dle pokynů pro přispívání

### Pro studenty

1. Vytvořte fork nebo klonujte repozitář
2. Procházejte adresáře lekcí postupně
3. Čtěte README soubory ke každé lekci
4. Dokončete kvízy před lekcí na https://ff-quizzes.netlify.app/web/
5. Procházejte příklady kódu v adresářích lekcí
6. Splňte úkoly a výzvy
7. Dokončete kvízy po lekci

### Živý vývoj

- **Dokumentace**: Spusťte `docsify serve` v kořenovém adresáři (port 3000)
- **Quiz App**: Spusťte `npm run dev` v adresáři quiz-app
- **Projekty**: Použijte rozšíření VS Code Live Server pro HTML projekty
- **API projekty**: Spusťte `npm start` v příslušných API adresářích

## Pokyny k testování

### Testování Quiz App

```bash
cd quiz-app
npm run lint       # Zkontrolujte problémy se stylem kódu
npm run build      # Ověřte, zda sestavení proběhne úspěšně
```

### Testování Bank API

```bash
cd 7-bank-project/api
npm run lint       # Zkontrolujte problémy se stylem kódu
node server.js     # Ověřte, že server startuje bez chyb
```

### Obecný přístup k testování

- Jedná se o vzdělávací repozitář bez komplexních automatizovaných testů
- Manuální testování se zaměřuje na:
  - Příklady kódu bez chyb při spuštění
  - Funkčnost odkazů v dokumentaci
  - Úspěšné dokončení buildů projektů
  - Dodržování osvědčených postupů v příkladech

### Kontroly před odesláním PR

- Spusťte `npm run lint` v adresářích s package.json
- Ověřte platnost markdown odkazů
- Testujte příklady kódu v prohlížeči nebo Node.js
- Zkontrolujte správnou strukturu překladů

## Směrnice pro styl kódu

### JavaScript

- Používejte moderní syntax ES6+
- Dodržujte standardní konfigurace ESLint v projektech
- Používejte srozumitelné názvy proměnných a funkcí pro vzdělávací přehlednost
- Přidávejte komentáře vysvětlující koncepty studentům
- Formátujte pomocí Prettier tam, kde je nastaven

### HTML/CSS

- Sémantické HTML5 prvky
- Principy responzivního designu
- Jasné konvence pojmenování tříd
- Komentáře vysvětlující CSS techniky pro studenty

### Python

- Dodržujte PEP 8 styl
- Jasné, vzdělávací příklady kódu
- Používejte typové nápovědy, kde to pomáhá učení

### Dokumentace v Markdown

- Přehledná hierarchie nadpisů
- Kódové bloky s uvedením jazyka
- Odkazy na další zdroje
- Snímky obrazovky a obrázky v adresářích `images/`
- Alternativní text obrázků pro přístupnost

### Organizace souborů

- Lekce číslované sekvenčně (1-getting-started-lessons, 2-js-basics, atd.)
- Každý projekt má adresáře `solution/` a často `start/` nebo `your-work/`
- Obrázky uložené ve složkách `images/` specifických pro lekce
- Překlady v adresářové struktuře `translations/{language-code}/`

## Sestavení a nasazení

### Nasazení Quiz App (Azure Static Web Apps)

Quiz-app je nakonfigurován pro nasazení pomocí Azure Static Web Apps:

```bash
cd quiz-app
npm run build      # Vytváří složku dist/
# Nasazuje pomocí workflow GitHub Actions při push na main
```

Konfigurace Azure Static Web Apps:
- **Umístění aplikace**: `/quiz-app`
- **Výstupní umístění**: `dist`
- **Workflow**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### Generování PDF dokumentace

```bash
npm install                    # Nainstalujte docsify-to-pdf
npm run convert               # Vytvořte PDF z docs
```

### Dokumentace přes Docsify

```bash
npm install -g docsify-cli    # Nainstalujte Docsify globálně
docsify serve                 # Spusťte na localhost:3000
```

### Sestavení specifická pro projekt

Každý projekt může mít vlastní build proces:
- Vue projekty: `npm run build` vytváří produkční balíčky
- Statické projekty: Žádný build, soubory se podávají přímo

## Směrnice pro pull requesty

### Formát názvu

Používejte jasné, popisné názvy uvádějící oblast změny:
- `[Quiz-app] Přidat nový kvíz pro lekci X`
- `[Lesson-3] Opravit překlep v projektu terrárium`
- `[Translation] Přidat španělský překlad pro lekci 5`
- `[Docs] Aktualizovat instrukce k nastavení`

### Požadované kontroly

Před odesláním PR:

1. **Kvalita kódu**:
   - Spusťte `npm run lint` v dotčených projektech
   - Opravte všechny lintovací chyby a varování

2. **Ověření buildů**:
   - Spusťte `npm run build` pokud je relevantní
   - Ujistěte se, že build proběhl bez chyb

3. **Kontrola odkazů**:
   - Otestujte všechny markdown odkazy
   - Ověřte pracovní odkazy na obrázky

4. **Kontrola obsahu**:
   - Korektura pravopisu a gramatiky
   - Zajištění správnosti a vzdělávací hodnoty příkladů kódu
   - Ověření správnosti překladů

### Požadavky na přispívání

- Souhlas s Microsoft CLA (automatická kontrola při prvním PR)
- Dodržování [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/)
- Viz [CONTRIBUTING.md](./CONTRIBUTING.md) pro podrobné pokyny
- Uvádějte čísla issue v popisu PR, pokud jsou relevantní

### Proces revize

- PR kontrolují správci a komunita
- Upřednostňuje se vzdělávací jasnost
- Příklady kódu by měly odpovídat současným osvědčeným postupům
- Překlady se kontrolují na přesnost a kulturní vhodnost

## Překladový systém

### Automatický překlad

- Používá GitHub Actions s workflow co-op-translator
- Automaticky překládá do více než 50 jazyků
- Zdrojové soubory v hlavních adresářích
- Přeložené soubory v adresářích `translations/{language-code}/`

### Přidání ručních vylepšení překladu

1. Najděte soubor v `translations/{language-code}/`
2. Proveďte vylepšení při zachování struktury
3. Zajistěte funkčnost příkladů kódu
4. Otestujte případný lokalizovaný kvízový obsah

### Metadata překladu

Přeložené soubory obsahují hlavičku s metadaty:
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

## Ladění a řešení problémů

### Běžné problémy

**Quiz app se nespustí**:
- Zkontrolujte verzi Node.js (doporučeno v14+)
- Odstraňte `node_modules` a `package-lock.json`, spusťte `npm install` znovu
- Zkontrolujte konflikty portů (výchozí: Vite používá port 5173)

**API server se nespustí**:
- Ověřte minimální verzi Node.js (node >=10)
- Zkontrolujte, zda port není obsazen
- Ujistěte se, že všechny závislosti jsou nainstalovány pomocí `npm install`

**Prodlžek prohlížeče se nenačítá**:
- Zkontrolujte, že manifest.json je správně formátován
- Prohlédněte konzoli prohlížeče kvůli chybám
- Postupujte podle specifických instrukcí pro instalaci prodlužků v prohlížeči

**Problémy s Python chat projektem**:
- Ujistěte se, že je nainstalován balík OpenAI: `pip install openai`
- Zkontrolujte, že je nastavena proměnná prostředí GITHUB_TOKEN
- Prověřte oprávnění přístupu k GitHub Models

**Docsify nedoručuje dokumenty**:
- Globálně nainstalujte docsify-cli: `npm install -g docsify-cli`
- Spusťte ze základního adresáře repozitáře
- Ověřte, že existuje `docs/_sidebar.md`

### Tipy pro vývojové prostředí

- Používejte VS Code s rozšířením Live Server pro HTML projekty
- Nainstalujte rozšíření ESLint a Prettier pro konzistentní formátování
- Používejte DevTools prohlížeče pro ladění JavaScriptu
- Pro Vue projekty použijte Vue DevTools rozšíření do prohlížeče

### Výkonnostní úvahy

- Velké množství přeložených souborů (50+ jazyků) znamená, že plné klony jsou rozsáhlé
- Použijte shallow clone, pokud pracujete jen s obsahem: `git clone --depth 1`
- Při práci s angličtinou vylučte překlady z hledání
- Build procesy mohou být pomalé při prvním spuštění (npm install, Vite build)

## Bezpečnostní aspekty

### Proměnné prostředí

- API klíče nikdy nesmí být commitovány do repozitáře
- Používejte `.env` soubory (jsou v `.gitignore`)
- Dokumentujte požadované proměnné prostředí v README projektů

### Python projekty

- Používejte virtuální prostředí: `python -m venv venv`
- Udržujte závislosti aktuální
- GitHub tokeny by měly mít minimální potřebná oprávnění

### Přístup k GitHub Models

- Pro GitHub Models jsou vyžadovány Personal Access Tokens (PAT)
- Tokeny ukládejte jako proměnné prostředí
- Nikdy nesdílejte tokeny ani přihlašovací údaje v repozitáři

## Další poznámky

### Cílové publikum

- Absolutní začátečníci ve webovém vývoji
- Studenti a samouci
- Učitelé používající kurikulum ve třídách
- Obsah je navržen pro přístupnost a postupné budování dovedností

### Vzdělávací filozofie

- Přístup založený na projektech
- Časté kontroly znalostí (kvízy)
- Praktické kódovací cvičení
- Příklady aplikací z reálného světa
- Zaměření na základy před frameworky

### Údržba repozitáře

- Aktivní komunita studentů a přispěvatelů
- Pravidelné aktualizace závislostí a obsahu
- Problémy a diskuse spravovány správci
- Aktualizace překladů automatizovány přes GitHub Actions

### Související zdroje

- [Microsoft Learn moduly](https://docs.microsoft.com/learn/)
- [Student Hub zdroje](https://docs.microsoft.com/learn/student-hub/)
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) doporučen pro studenty
- Další kurzy: Generativní AI, Data Science, ML, IoT dostupné kurikula

### Práce s konkrétními projekty

Pro detailní instrukce u jednotlivých projektů nahlédněte do README souborů:
- `quiz-app/README.md` - Vue 3 aplikace kvízu
- `7-bank-project/README.md` - Bankovní aplikace s autentizací
- `5-browser-extension/README.md` - Vývoj prodlužků prohlížeče
- `6-space-game/README.md` - Vývoj hry na canvasu
- `9-chat-project/README.md` - Projekt AI chat asistenta

### Struktura monorepa

I když nejde o tradiční monorepo, tento repozitář obsahuje několik nezávislých projektů:
- Každá lekce je samostatná
- Projekty nesdílí závislosti
- Práce na jednotlivých projektech neovlivňuje ostatní
- Naklonujte celý repozitář pro plný zážitek kurikula

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Prohlášení o vyloučení odpovědnosti**:
Tento dokument byl přeložen pomocí AI překladatelské služby [Co-op Translator](https://github.com/Azure/co-op-translator). I když usilujeme o přesnost, mějte prosím na paměti, že automatické překlady mohou obsahovat chyby nebo nepřesnosti. Původní dokument v jeho rodném jazyce by měl být považován za autoritativní zdroj. Pro důležité informace se doporučuje profesionální lidský překlad. Nejsme zodpovědní za jakákoliv nedorozumění nebo nesprávné výklady vyplývající z použití tohoto překladu.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->