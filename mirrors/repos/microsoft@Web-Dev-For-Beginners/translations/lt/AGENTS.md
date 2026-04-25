# AGENTS.md

## Projekto apžvalga

Tai yra švietimo programa skirta mokyti pradedančiuosius interneto kūrimo pagrindų. Programa yra išsami 12 savaičių kursų sistema, sukurta Microsoft Cloud Advocates komandos, apimanti 24 praktines pamokas apie JavaScript, CSS ir HTML.

### Pagrindinės sudedamosios dalys

- **Švietimo turinys**: 24 struktūruotos pamokos, suskirstytos į projektų modulius
- **Praktiniai projektai**: Terariumas, Rašymo žaidimas, Naršyklės plėtinys, Kosminis žaidimas, Banko programa, Kodo redaktorius ir AI pokalbių asistentas
- **Interaktyvūs testai**: 48 testai po 3 klausimus kiekviename (prieš ir po pamokų įvertinimai)
- **Daugiakalbė palaikymas**: Automatizuoti vertimai į 50+ kalbų naudojant GitHub Actions
- **Technologijos**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (AI projektams)

### Architektūra

- Švietimo saugykla su pamokomis pagrįsta struktūra
- Kiekvienos pamokos aplanke yra README, kodo pavyzdžiai ir sprendimai
- Atskiri projektai atskiruose kataloguose (quiz-app, įvairūs pamokų projektai)
- Vertimo sistema naudojant GitHub Actions (co-op-translator)
- Dokumentacija pateikiama per Docsify ir prieinama PDF formatu

## Diegimo komandos

Šis saugykla yra skirta pirminiam švietimo turinio vartojimui. Dirbant su konkrečiais projektais:

### Pagrindinės saugyklos paruošimas

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Testų programėlės paruošimas (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Paleisti kūrimo serverį
npm run build      # Sukurti gamybai
npm run lint       # Vykdyti ESLint
```

### Banko projekto API (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # Paleisti API serverį
npm run lint       # Vykdyti ESLint
npm run format     # Formatuoti su Prettier
```

### Naršyklės plėtinių projektai

```bash
cd 5-browser-extension/solution
npm install
# Vadovaukitės naršyklei būdingomis plėtinių įkėlimo instrukcijomis
```

### Kosminio žaidimo projektai

```bash
cd 6-space-game/solution
npm install
# Atidarykite index.html naršyklėje arba naudokite Live Server
```

### Pokalbių projektas (Python serveris)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Nustatyti GITHUB_TOKEN aplinkos kintamąjį
python api.py
```

## Vystymo darbo eiga

### Turinį prisidedantiems

1. **Atšakokite saugyklą** į savo GitHub paskyrą
2. **Klonuokite savo atšaką** lokaliai
3. **Sukurkite naują šaką** savo pakeitimams
4. Atlikite turinio ar kodo pavyzdžių pakeitimus pamokose
5. Patikrinkite kodo pakeitimus atitinkamuose projekto kataloguose
6. Pateikite pull requests laikantis indėlio taisyklių

### Mokiniams

1. Atšakokite arba klonuokite saugyklą
2. Eikite sekantiems pamokų katalogams paeiliui
3. Skaitykite kiekvienos pamokos README failus
4. Atlikite priešpamokinius testus https://ff-quizzes.netlify.app/web/
5. Dirbkite su kodo pavyzdžiais pamokų aplankuose
6. Atlikite užduotis ir iššūkius
7. Atlikite pastraipinius testus

### Tiesioginis vystymas

- **Dokumentacija**: paleiskite `docsify serve` pagrindiniame kataloge (portas 3000)
- **Testų programėlė**: paleiskite `npm run dev` quiz-app kataloge
- **Projektai**: naudokite VS Code Live Server plėtinį HTML projektams
- **API projektai**: paleiskite `npm start` atitinkamuose API kataloguose

## Testavimo instrukcijos

### Testų programėlės testavimas

```bash
cd quiz-app
npm run lint       # Patikrinkite kodo stiliaus problemas
npm run build      # Patikrinkite, ar statyba sėkminga
```

### Banko API testavimas

```bash
cd 7-bank-project/api
npm run lint       # Patikrinti kodo stiliaus problemas
node server.js     # Patvirtinti, kad serveris paleidžiamas be klaidų
```

### Bendras testavimo metodas

- Tai švietimo saugykla be išsamios automatizuotos testavimo sistemos
- Rankinis testavimas orientuotas į:
  - Kodo pavyzdžių vykdymą be klaidų
  - Dokumentacijos nuorodų veikimą
  - Projekto sėkmingą sudarymą
  - Pavyzdžius atitinkančius gerąsias praktikas

### Prieš pateikiant patikrinimus

- Paleiskite `npm run lint` kataloguose su package.json
- Patikrinkite markdown nuorodų galiojimą
- Testuokite kodo pavyzdžius naršyklėje arba Node.js aplinkoje
- Įsitikinkite, kad vertimai išlaiko tinkamą struktūrą

## Kodo stiliaus gairės

### JavaScript

- Naudoti modernią ES6+ sintaksę
- Laikytis standartinių ESLint konfigūracijų projektuose
- Naudoti prasmingus kintamųjų ir funkcijų pavadinimus švietimui aiškinti
- Pridėti komentarus konceptų paaiškinimui mokiniams
- Formatuoti su Prettier, jei konfigūruota

### HTML/CSS

- Semantikos atitinkantys HTML5 elementai
- Reaguojantis dizainas
- Aiškios klasių pavadinimų konvencijos
- Komentarai CSS technikoms paaiškinti mokiniams

### Python

- PEP 8 stiliaus gairės
- Aiškūs, švietimui skirti kodo pavyzdžiai
- Tipo užuominos, jei padeda mokymuisi

### Markdown dokumentacija

- Aiški antraščių hierarchija
- Kodo blokai su kalbos nurodymu
- Nuorodos į papildomus išteklius
- Ekrano kopijos ir paveikslėliai `images/` kataloguose
- Alternatyvus tekstas paveikslėliams, siekiant prieinamumo

### Failų organizavimas

- Pamokos su numeriais paeiliui (1-getting-started-lessons, 2-js-basics ir kt.)
- Kiekvienas projektas turi `solution/` ir dažnai `start/` arba `your-work/` katalogus
- Paveikslėliai saugomi pamokai priskirtuose `images/` aplankuose
- Vertimai saugomi `translations/{language-code}/` kataloguose

## Sudarymas ir diegimas

### Testų programėlės diegimas (Azure Static Web Apps)

quiz-app yra sukonfigūruota Azure Static Web Apps diegimui:

```bash
cd quiz-app
npm run build      # Sukuria dist/ aplanką
# Diegia naudojant GitHub Actions darbo eigą, kai stumiama į main
```

Azure Static Web Apps konfiguracija:
- **Programėlės vieta**: `/quiz-app`
- **Išvesties vieta**: `dist`
- **Darbo eiga**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### Dokumentacijos PDF generavimas

```bash
npm install                    # Įdiekite docsify-to-pdf
npm run convert               # Sugeneruoti PDF iš dokumentų
```

### Docsify dokumentacija

```bash
npm install -g docsify-cli    # Įdiekite Docsify globaliai
docsify serve                 # Paleiskite serveryje localhost:3000
```

### Projektui specifiniai sudarymai

Kiekvienas projekto katalogas gali turėti savo sudarymo procesą:
- Vue projektai: `npm run build` sukuria gamybines pakuotes
- Statiniai projektai: nėra sudarymo žingsnio, failai pateikiami tiesiogiai

## Pull Request gairės

### Antraštės formatas

Naudokite aiškius, aprašomuosius pavadinimus, nurodančius pakeitimo sritį:
- `[Quiz-app] Pridėti naują testą pamokai X`
- `[Lesson-3] Ištaisyti klaidą terariumo projekte`
- `[Translation] Pridėti ispanų vertimą pamokai 5`
- `[Docs] Atnaujinti diegimo instrukcijas`

### Būtini patikrinimai

Prieš pateikiant PR:

1. **Kodo kokybė**:
   - Paleiskite `npm run lint` paveiktuose projekto kataloguose
   - Ištaisykite visas lint klaidas ir įspėjimus

2. **Sudarymo patikra**:
   - Jei taikoma, paleiskite `npm run build`
   - Užtikrinkite, kad nėra sudarymo klaidų

3. **Nuorodų validacija**:
   - Išbandykite visas markdown nuorodas
   - Patikrinkite, ar paveikslėlių nuorodos veikia

4. **Turinio peržiūra**:
   - Tikrinkite rašybą ir gramatiką
   - Užtikrinkite, kad kodo pavyzdžiai tinkami ir švietimo tikslais
   - Patikrinkite, ar vertimai išlaiko pradinę prasmę

### Indėlio reikalavimai

- Sutikite su Microsoft CLA (automatinis tikrinimas pirmo PR metu)
- Vadovaukitės [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/)
- Peržiūrėkite [CONTRIBUTING.md](./CONTRIBUTING.md) dėl išsamios informacijos
- Nurodykite klausimų numerius PR aprašyme, jei taikoma

### Apžvalgos procesas

- PR apžvelgia priežiūrėtojai ir bendruomenė
- Prioritetas teikiamas mokymosi aiškumui
- Kodo pavyzdžiai turi laikytis dabartinių geriausių praktikų
- Vertimai peržiūrimi dėl tikslumo ir kultūrinio atitikimo

## Vertimo sistema

### Automatizuotas vertimas

- Naudoja GitHub Actions su co-op-translator darbo eiga
- Automatiškai verčia į 50+ kalbų
- Šaltinio failai pagrindiniuose kataloguose
- Išversti failai saugomi `translations/{language-code}/` kataloguose

### Rankinių vertimo patobulinimų pridedimas

1. Suraskite failą `translations/{language-code}/`
2. Atlikite patobulinimus išlaikant struktūrą
3. Įsitikinkite, kad kodo pavyzdžiai veikia teisingai
4. Išbandykite lokalizuotą testų turinį

### Vertimų metaduomenys

Išversti failai turi metaduomenų antraštę:
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

## Derinimas ir problemų sprendimas

### Dažniausios problemos

**Testų programėlė nesikrauna**:
- Patikrinkite Node.js versiją (rekomenduojama v14+)
- Ištrinkite `node_modules` ir `package-lock.json`, paleiskite dar kartą `npm install`
- Patikrinkite ar nėra uosto konflikto (numatytas: Vite naudoja 5173 portą)

**API serveris nesikrauna**:
- Įsitikinkite, kad Node.js versija atitinka minimalią (node >=10)
- Patikrinkite, ar uostas jau nenaudojamas
- Įsitikinkite, kad visos priklausomybės įdiegtos su `npm install`

**Naršyklės plėtinys nesikrauna**:
- Patikrinkite, ar manifest.json teisingai suformatuotas
- Peržiūrėkite naršyklės konsolę dėl klaidų
- Sekite naršyklės specifines plėtinių diegimo instrukcijas

**Python pokalbių projekto problemos**:
- Įdiekite OpenAI paketą: `pip install openai`
- Įsitikinkite, kad GITHUB_TOKEN aplinkos kintamasis nustatytas
- Patikrinkite GitHub Models prieigos teises

**Docsify neduoda dokumentų**:
- Įdiekite docsify-cli globaliai: `npm install -g docsify-cli`
- Paleiskite iš saugyklos šaknies
- Patikrinkite, ar egzistuoja `docs/_sidebar.md`

### Vystymo aplinkos patarimai

- Naudokite VS Code su Live Server plėtiniu HTML projektams
- Įdiekite ESLint ir Prettier plėtinius nuosekliam formatavimui
- Naudokite naršyklės DevTools JavaScript derinimui
- Vue projektams naudokite Vue DevTools naršyklės plėtinį

### Veikimo efektyvumo patarimai

- Didelis išverstų failų kiekis (50+ kalbų) reiškia, kad pilni klonai dideli
- Naudokite paviršinį klonavimą, jei dirbate tik su turiniu: `git clone --depth 1`
- Dirbant su anglišku turiniu, išimkite vertimus iš paieškos
- Sudarymo procesai pirmą kartą gali būti lėti (npm install, Vite build)

## Saugumo aspektai

### Aplinkos kintamieji

- API raktai niekada neturi būti įtraukiami į saugyklą
- Naudokite `.env` failus (jau įtraukti į `.gitignore`)
- Reikalingi aplinkos kintamieji dokumentuojami projekto README

### Python projektai

- Naudokite virtualias aplinkas: `python -m venv venv`
- Laikykite priklausomybes atnaujintas
- GitHub tokenai turėtų turėti minimalias būtinas teises

### GitHub Models prieiga

- Reikalingi asmeniniai prieigos raktai (PAT)
- Raktai turi būti saugomi kaip aplinkos kintamieji
- Niekada neįtraukti jų į saugyklą ar viešinti

## Papildomos pastabos

### Tikslinė auditorija

- Visiškai pradedantieji interneto kūrime
- Studentai ir savarankiški besimokantieji
- Mokytojai, naudojantys programą klasėje
- Turinys sukonstruotas prieinamumui ir nuosekliam įgūdžių įgijimui

### Švietimo filosofija

- Mokymasis pagrįstas projektais
- Dažni žinių patikrinimai (testai)
- Praktiniai kodavimo užsiėmimai
- Realių projektų pavyzdžiai
- Dėmesys pagrindams prieš frameworks

### Saugyklos priežiūra

- Aktyvi mokinių ir prisidėjusių bendruomenė
- Reguliarūs priklausomybių ir turinio atnaujinimai
- Klausimai ir diskusijos prižiūrimi saugyklos savininkų
- Vertimų atnaujinimai automatizuoti per GitHub Actions

### Susiję ištekliai

- [Microsoft Learn moduliai](https://docs.microsoft.com/learn/)
- [Studentų centras](https://docs.microsoft.com/learn/student-hub/)
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) rekomenduojamas besimokantiesiems
- Papildomi kursai: Generatyvioji AI, Duomenų mokslas, ML, IoT programos

### Darbas su konkrečiais projektais

Išsamios individualių projektų instrukcijos pateiktos README failuose:
- `quiz-app/README.md` - Vue 3 testų programėlė
- `7-bank-project/README.md` - Banko programa su autentifikacija
- `5-browser-extension/README.md` - Naršyklės plėtinių kūrimas
- `6-space-game/README.md` - Žaidimas su Canvas
- `9-chat-project/README.md` - AI pokalbių asistento projektas

### Monorepo struktūra

Nors tai nėra tradicinis monorepo, ši saugykla turi kelis nepriklausomus projektus:
- Kiekviena pamoka yra savarankiška
- Projektai nesidalina priklausomybėmis
- Darbai su atskirais projektais neturi įtakos kitiems
- Klonuokite visą saugyklą pilnam kursui gauti

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Atsakomybės ribojimas**:
Šis dokumentas buvo išverstas naudojant dirbtinio intelekto vertimo paslaugą [Co-op Translator](https://github.com/Azure/co-op-translator). Nors stengiamės užtikrinti tikslumą, atkreipkite dėmesį, kad automatizuoti vertimai gali turėti klaidų ar netikslumų. Originalus dokumentas jo gimtąja kalba yra laikomas autoritetingu šaltiniu. Svarbiai informacijai rekomenduojamas profesionalus žmogiškasis vertimas. Mes neatsakome už bet kokius nesusipratimus ar klaidingas interpretacijas, kylančias naudojant šį vertimą.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->