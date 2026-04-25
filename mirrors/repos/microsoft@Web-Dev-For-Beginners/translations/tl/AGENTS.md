# AGENTS.md

## Project Overview

Ito ay isang edukasyonal na repositoryo ng kurikulum para sa pagtuturo ng mga pangunahing kaalaman sa web development sa mga nagsisimula. Ang kurikulum ay isang komprehensibong 12-linggong kurso na binuo ng Microsoft Cloud Advocates, na nagtatampok ng 24 na hands-on na aralin na sumasaklaw sa JavaScript, CSS, at HTML.

### Key Components

- **Nilalaman Pang-edukasyon**: 24 na istrukturadong aralin na inayos sa mga proyekto bilang mga modulo
- **Praktikal na Mga Proyekto**: Terrarium, Typing Game, Browser Extension, Space Game, Banking App, Code Editor, at AI Chat Assistant
- **Interaktibong Mga Quiz**: 48 na quiz na may tig-3 tanong bawat isa (pagsusulit bago/pagkatapos ng aralin)
- **Suporta sa Maraming Wika**: Awtomatikong pagsasalin para sa 50+ na wika gamit ang GitHub Actions
- **Mga Teknolohiya**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (para sa mga AI na proyekto)

### Architecture

- Edukasyonal na repositoryo na may istruktura batay sa mga aralin
- Ang bawat folder ng aralin ay naglalaman ng README, mga halimbawa ng code, at mga solusyon
- Mga standalone na proyekto sa hiwalay na mga direktoryo (quiz-app, iba't ibang mga proyekto sa aralin)
- Sistema ng pagsasalin gamit ang GitHub Actions (co-op-translator)
- Dokumentasyon na ibinibigay sa pamamagitan ng Docsify at available bilang PDF

## Setup Commands

Ang repositoryong ito ay pangunahing para sa konsumpsyon ng edukasyonal na nilalaman. Para sa pagtatrabaho sa mga partikular na proyekto:

### Main Repository Setup

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Quiz App Setup (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Simulan ang development server
npm run build      # I-build para sa produksyon
npm run lint       # Patakbuhin ang ESLint
```

### Bank Project API (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # Simulan ang API server
npm run lint       # Patakbuhin ang ESLint
npm run format     # I-format gamit ang Prettier
```

### Browser Extension Projects

```bash
cd 5-browser-extension/solution
npm install
# Sundin ang mga tagubilin sa pag-load ng extension na partikular sa browser
```

### Space Game Projects

```bash
cd 6-space-game/solution
npm install
# Buksan ang index.html sa browser o gamitin ang Live Server
```

### Chat Project (Python Backend)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Itakda ang GITHUB_TOKEN na variable ng kapaligiran
python api.py
```

## Development Workflow

### Para sa mga Contributor ng Nilalaman

1. **I-fork ang repositoryo** sa iyong GitHub account
2. **I-clone ang iyong fork** nang lokal
3. **Gumawa ng bagong sanga** para sa iyong mga pagbabago
4. Gawin ang mga pagbabago sa nilalaman ng aralin o mga halimbawa ng code
5. Subukan ang anumang pagbabago sa code sa mga kaukulang direktoryo ng proyekto
6. Mag-submit ng pull requests alinsunod sa mga gabay sa kontribusyon

### Para sa mga Nag-aaral

1. I-fork o i-clone ang repositoryo
2. Mag-navigate sa mga direktoryo ng aralin sunod-sunod
3. Basahin ang mga README file para sa bawat aralin
4. Kumpletuhin ang mga pre-lesson quizzes sa https://ff-quizzes.netlify.app/web/
5. Trabahuhin ang mga halimbawa ng code sa mga folder ng aralin
6. Kumpletuhin ang mga takdang-aralin at hamon
7. Sagutan ang mga post-lesson quizzes

### Live Development

- **Dokumentasyon**: Patakbuhin ang `docsify serve` sa root (port 3000)
- **Quiz App**: Patakbuhin ang `npm run dev` sa folder ng quiz-app
- **Mga Proyekto**: Gamitin ang VS Code Live Server extension para sa mga HTML na proyekto
- **API Projects**: Patakbuhin ang `npm start` sa mga kaukulang API na direktoryo

## Testing Instructions

### Quiz App Testing

```bash
cd quiz-app
npm run lint       # Suriin kung may mga isyu sa istilo ng kodigo
npm run build      # Tiyakin na matagumpay ang pagbuo
```

### Bank API Testing

```bash
cd 7-bank-project/api
npm run lint       # Suriin ang mga isyu sa estilo ng code
node server.js     # Tiyaking nagsisimula ang server nang walang mga error
```

### Pangkalahatang Paraan ng Pagsusuri

- Ito ay isang edukasyonal na repositoryo na walang komprehensibong automated tests
- Ang manual na pagsusuri ay nakatuon sa:
  - Hindi nagkakaroon ng error ang mga halimbawa ng code kapag pinatakbo
  - Gumagana nang maayos ang mga links sa dokumentasyon
  - Matagumpay ang pagbuo ng mga proyekto
  - Sumusunod ang mga halimbawa sa pinakamahusay na mga kasanayan

### Mga Pre-submission Checks

- Patakbuhin ang `npm run lint` sa mga direktoryong may package.json
- Tiyakin na wasto ang mga markdown links
- Subukan ang mga halimbawa ng code sa browser o Node.js
- Suriin na ang mga pagsasalin ay nananatiling maayos ang istruktura

## Code Style Guidelines

### JavaScript

- Gumamit ng makabagong ES6+ na syntax
- Sundin ang mga standard ESLint na konfigurasyon na ibinigay sa mga proyekto
- Gumamit ng makabuluhang mga pangalan ng variable at function para sa kalinawan sa edukasyon
- Magdagdag ng mga paliwanag na komentaryo tungkol sa mga konsepto para sa mga nag-aaral
- I-format gamit ang Prettier kung saan naka-configure

### HTML/CSS

- Semantic HTML5 elements
- Mga prinsipyo ng responsive design
- Malinaw na conventions sa pagbibigay ng pangalan sa mga klase
- Mga komentaryo na nagpapaliwanag ng mga teknik sa CSS para sa mga nag-aaral

### Python

- Mga patnubay sa estilo ayon sa PEP 8
- Malinaw, pang-edukasyonal na mga halimbawa ng code
- Mga type hint kung nakakatulong sa pag-aaral

### Markdown Documentation

- Malinaw na hierarchy ng mga heading
- Mga code block na may pagspecify ng wika
- Mga link sa karagdagang mga mapagkukunan
- Mga screenshot at larawan sa mga `images/` na mga direktoryo
- Alt text para sa mga larawan para sa accessibility

### File Organization

- Ang mga aralin ay may sunud-sunod na bilang (1-getting-started-lessons, 2-js-basics, atbp.)
- Ang bawat proyekto ay may `solution/` at madalas `start/` o `your-work/` na mga direktoryo
- Ang mga larawan ay naka-imbak sa mga lesson-specific na `images/` folder
- Mga pagsasalin sa istrukturang `translations/{language-code}/`

## Build and Deployment

### Quiz App Deployment (Azure Static Web Apps)

Ang quiz-app ay naka-configure para sa Azure Static Web Apps deployment:

```bash
cd quiz-app
npm run build      # Lumilikha ng dist/ folder
# Nagde-deploy gamit ang GitHub Actions workflow kapag may push sa main
```

Azure Static Web Apps na konfigurasyon:
- **App location**: `/quiz-app`
- **Output location**: `dist`
- **Workflow**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### Documentation PDF Generation

```bash
npm install                    # I-install ang docsify-to-pdf
npm run convert               # Gumawa ng PDF mula sa docs
```

### Docsify Documentation

```bash
npm install -g docsify-cli    # I-install ang Docsify nang globally
docsify serve                 # I-serve sa localhost:3000
```

### Mga Build na Nakatuon sa Proyekto

Ang bawat direktoryo ng proyekto ay maaaring may sariling proseso ng build:
- Vue projects: `npm run build` na lumilikha ng mga production bundles
- Static projects: Walang build step, direktang pag-serbisyo ng mga file

## Pull Request Guidelines

### Format ng Pamagat

Gumamit ng malinaw, deskriptibong mga pamagat na nagpapakita ng bahagi ng pagbabago:
- `[Quiz-app] Add new quiz for lesson X`
- `[Lesson-3] Fix typo in terrarium project`
- `[Translation] Add Spanish translation for lesson 5`
- `[Docs] Update setup instructions`

### Mga Kinakailangang Pag-check

Bago magsumite ng PR:

1. **Kalidad ng Code**:
   - Patakbuhin ang `npm run lint` sa mga apektadong proyekto
   - Ayusin ang lahat ng linting error at babala

2. **Pag-verify ng Build**:
   - Patakbuhin ang `npm run build` kung kinakailangan
   - Siguraduhing walang error sa build

3. **Pag-validate ng Link**:
   - Subukan ang lahat ng markdown link
   - Siguraduhing gumagana ang mga reference ng larawan

4. **Pagsusuri ng Nilalaman**:
   - Proofread para sa baybay at gramatika
   - Siguraduhing tama at edukasyonal ang mga halimbawa ng code
   - I-verify ang mga pagsasalin ay nananatili ang orihinal na kahulugan

### Mga Kinakailangan sa Kontribusyon

- Sumang-ayon sa Microsoft CLA (automated check sa unang PR)
- Sundin ang [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/)
- Tumingin sa [CONTRIBUTING.md](./CONTRIBUTING.md) para sa mga detalyadong gabay
- Banggitin ang mga numero ng isyu sa paglalarawan ng PR kung angkop

### Proseso ng Review

- Ang mga PR ay sinusuri ng mga maintainer at komunidad
- Pinapahalagahan ang kalinawan sa edukasyon
- Dapat sundin ng mga halimbawa ng code ang kasalukuyang best practices
- Sinusuri ang mga pagsasalin para sa katumpakan at angkop na kultura

## Translation System

### Automated Translation

- Gumagamit ng GitHub Actions na may co-op-translator workflow
- Nagsasalin sa 50+ na wika nang awtomatiko
- Mga source file sa mga pangunahing direktoryo
- Mga naisaling file sa `translations/{language-code}/` na mga direktoryo

### Pagdaragdag ng Manual na Pagpapabuti sa Pagsasalin

1. Hanapin ang file sa `translations/{language-code}/`
2. Gawin ang mga pagpapabuti nang pinananatili ang istruktura
3. Siguraduhing nananatiling gumagana ang mga halimbawa ng code
4. Subukan ang anumang lokal na nilalamang quiz

### Metadata ng Pagsasalin

Ang mga naisaling file ay may kasamang metadata header:
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

## Debugging and Troubleshooting

### Mga Karaniwang Isyu

**Hindi nagsisimula ang quiz app**:
- Suriin ang bersyon ng Node.js (inirekomenda v14+)
- Burahin ang `node_modules` at `package-lock.json`, patakbuhin muli ang `npm install`
- Suriin kung may conflict sa port (default: Vite gumagamit ng port 5173)

**Hindi nagsisimula ang API server**:
- Tiyakin ang bersyon ng Node.js ay sapat (node >=10)
- Suriin kung ginagamit na ng iba ang port
- Siguraduhing naka-install lahat ng dependencies gamit ang `npm install`

**Hindi naglo-load ang browser extension**:
- Siguraduhing tama ang format ng manifest.json
- Tingnan ang browser console para sa mga error
- Sundin ang mga instruksyon sa pag-install ng extension para sa partikular na browser

**Mga isyu sa Python chat project**:
- Siguraduhing naka-install ang OpenAI package: `pip install openai`
- Tiyakin na nakaset ang GITHUB_TOKEN environment variable
- Suriin ang mga permiso sa access ng GitHub Models

**Hindi nagseserbisyo ang Docsify ng docs**:
- I-install ang docsify-cli globally: `npm install -g docsify-cli`
- Patakbuhin mula sa root directory ng repositoryo
- Siguraduhing may `docs/_sidebar.md`

### Mga Tip para sa Development Environment

- Gumamit ng VS Code kasama ang Live Server extension para sa mga HTML na proyekto
- Mag-install ng ESLint at Prettier extensions para sa konsistenteng pag-format
- Gamitin ang browser DevTools para i-debug ang JavaScript
- Para sa mga Vue na proyekto, mag-install ng Vue DevTools browser extension

### Mga Pagsasaalang-alang sa Performance

- Malaki ang bilang ng naisaling mga file (50+ na wika) kaya malaki ang buong clone
- Gumamit ng shallow clone kung nilalaman lang ang kanilang tinatrabaho: `git clone --depth 1`
- I-exclude ang mga pagsasalin sa mga paghahanap kapag nagtatrabaho sa English na nilalaman
- Maaaring mabagal ang build processes sa unang takbo (npm install, Vite build)

## Security Considerations

### Mga Environment Variable

- Huwag kailanman i-commit ang API keys sa repositoryo
- Gumamit ng `.env` files (nasa `.gitignore` na)
- I-dokumento ang kinakailangang environment variables sa mga README ng proyekto

### Python Projects

- Gumamit ng virtual environments: `python -m venv venv`
- Panatilihing updated ang mga dependencies
- Dapat may minimal na permiso lamang ang mga GitHub token

### GitHub Models Access

- Kinakailangan ang Personal Access Tokens (PAT) para sa GitHub Models
- Itago ang mga token bilang environment variables
- Huwag kailanman i-commit ang mga token o kredensyal

## Additional Notes

### Target Audience

- Mga ganap na nagsisimula sa web development
- Mga estudyante at self-learners
- Mga guro na gumagamit ng kurikulum sa mga silid-aralan
- Ang nilalaman ay dinisenyo para sa accessibility at unti-unting pagbuo ng kakayahan

### Educational Philosophy

- Pagsasanay sa pag-aaral batay sa proyekto
- Madalas na pagsusuri sa kaalaman (mga quiz)
- Hands-on na coding exercises
- Mga halimbawa ng aplikasyon sa tunay na mundo
- Pagtuon sa mga pundasyon bago ang mga framework

### Repository Maintenance

- Aktibong komunidad ng mga nag-aaral at contributor
- Regular na pag-update ng dependencies at nilalaman
- Sina-subsaybayan ang mga isyu at talakayan ng mga maintainer
- Awtomatikong pag-update ng pagsasalin gamit ang GitHub Actions

### Related Resources

- [Microsoft Learn modules](https://docs.microsoft.com/learn/)
- [Student Hub resources](https://docs.microsoft.com/learn/student-hub/)
- Inirerekomenda ang [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) para sa mga nag-aaral
- Karagdagang mga kurso: Generative AI, Data Science, ML, IoT curricula ang available

### Pagtatrabaho sa Partikular na Mga Proyekto

Para sa detalyadong mga instruksyon sa mga indibidwal na proyekto, tingnan ang mga README file sa:
- `quiz-app/README.md` - Vue 3 quiz application
- `7-bank-project/README.md` - Banking application na may authentication
- `5-browser-extension/README.md` - Pag-develop ng browser extension
- `6-space-game/README.md` - Pag-develop ng game gamit ang canvas
- `9-chat-project/README.md` - AI chat assistant project

### Monorepo Structure

Bagamat hindi tradisyunal na monorepo, ang repositoryong ito ay naglalaman ng maraming independiyenteng proyekto:
- Ang bawat aralin ay nakahiwalay
- Hindi nagbabahagi ng dependencies ang mga proyekto
- Puwedeng magtrabaho sa bawat proyekto nang hindi naaapektuhan ang iba
- I-clone ang buong repo para sa buong karanasan ng kurikulum

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Paunawa**:  
Ang dokumentong ito ay isinalin gamit ang AI translation service na [Co-op Translator](https://github.com/Azure/co-op-translator). Bagaman nagsusumikap kami para sa katuparan, pakatandaan na ang mga awtomatikong pagsasalin ay maaaring maglaman ng mga pagkakamali o hindi pagkakatugma. Ang orihinal na dokumento sa orihinal nitong wika ang dapat ituring na pangunahing sanggunian. Para sa mga mahalagang impormasyon, inirerekomenda ang propesyonal na pagsasalin ng tao. Hindi kami mananagot para sa anumang hindi pagkakaunawaan o maling interpretasyon na nagmumula sa paggamit ng pagsasaling ito.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->