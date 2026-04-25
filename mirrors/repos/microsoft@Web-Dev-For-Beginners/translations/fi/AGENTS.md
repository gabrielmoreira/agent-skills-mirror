# AGENTS.md

## Projektin yleiskatsaus

Tämä on opetussisältöjen arkisto, joka on tarkoitettu web-kehityksen perusteiden opettamiseen aloittelijoille. Oppimateriaali on kattava 12 viikon kurssi, jonka ovat kehittäneet Microsoft Cloud Advocates -tiimin jäsenet. Kurssi koostuu 24 käytännönlähtöisestä oppitunnista, jotka käsittelevät JavaScriptiä, CSS:ää ja HTML:ää.

### Keskeiset osat

- **Opetussisältö**: 24 jäsenneltyä oppituntia, jotka on järjestetty projektipohjaisiksi moduuleiksi
- **Käytännön projektit**: Terrarium, Typing Game, selainlaajennus, Space Game, Banking App, Code Editor ja AI Chat Assistant
- **Interaktiiviset tietovisat**: 48 tietovisaa, joissa on 3 kysymystä kukin (ennen ja jälkeen oppitunnin arvioinnit)
- **Monikielinen tuki**: Automaattiset käännökset yli 50 kielelle GitHub Actionsin avulla
- **Teknologiat**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (tekoälyprojekteissa)

### Arkkitehtuuri

- Opetussisältöön perustuva arkisto oppituntirakenteella
- Jokaisessa oppitunnin kansiossa on README, koodiesimerkkejä ja ratkaisumalleja
- Itsenäiset projektit omissa hakemistoissaan (quiz-app, eri oppituntiprojektit)
- Käännösjärjestelmä käyttää GitHub Actionsia (co-op-translator)
- Dokumentaatio näytetään Docsifylla ja on saatavilla PDF-muodossa

## Asennuskomennot

Tätä arkistoa käytetään ensisijaisesti opetussisältöjen lukemiseen. Työskennellessäsi tiettyjen projektien parissa:

### Pääarkiston asennus

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Quiz-sovelluksen asennus (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Käynnistä kehityspalvelin
npm run build      # Rakenna tuotantoon
npm run lint       # Suorita ESLint
```

### Bank-projektin API (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # Käynnistä API-palvelin
npm run lint       # Suorita ESLint
npm run format     # Muotoile Prettierilla
```

### Selainlaajennusprojektit

```bash
cd 5-browser-extension/solution
npm install
# Noudata selaimen erityisiä laajennusten latausohjeita
```

### Space Game -projektit

```bash
cd 6-space-game/solution
npm install
# Avaa index.html selaimessa tai käytä Live Serveriä
```

### Chat-projekti (Python Backend)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Aseta GITHUB_TOKEN-ympäristömuuttuja
python api.py
```

## Kehityskäytännöt

### Sisällöntuottajille

1. **Forkkaa arkisto** omaan GitHub-tiliisi
2. **Kloonaa fork** paikallisesti
3. **Luo uusi haara** muutoksillesi
4. Tee muutoksia oppimateriaalin sisältöön tai koodiesimerkkeihin
5. Testaa muutoksia liittyvissä projektihakemistoissa
6. Lähetä pull-pyyntöjä ohjeiden mukaisesti

### Oppijoille

1. Forkkaa tai kloonaa arkisto
2. Siirry oppituntien hakemistoihin peräjälkeen
3. Lue kunkin oppitunnin README-tiedostot
4. Suorita ennen oppituntia tehtävät tietovisat osoitteessa https://ff-quizzes.netlify.app/web/
5. Kokeile koodiesimerkkejä oppituntikansioissa
6. Tee annettuja tehtäviä ja haasteita
7. Suorita oppitunnin jälkeiset tietovisat

### Live-kehitys

- **Dokumentaatio**: Aja `docsify serve` juurihakemistosta (portti 3000)
- **Quiz-sovellus**: Aja `npm run dev` quiz-app kansiossa
- **Projektit**: Käytä VS Code Live Server -laajennusta HTML-projekteissa
- **API-projektit**: Aja `npm start` vastaavissa API-kansioissa

## Testausohjeet

### Quiz-sovelluksen testaus

```bash
cd quiz-app
npm run lint       # Tarkista koodityyliongelmat
npm run build      # Varmista, että käännös onnistuu
```

### Bank-API:n testaus

```bash
cd 7-bank-project/api
npm run lint       # Tarkista koodityylin ongelmat
node server.js     # Varmista, että palvelin käynnistyy ilman virheitä
```

### Yleinen testauslähestymistapa

- Tämä on opetussisältöarkisto, jossa ei ole kattavia automaattisia testejä
- Manuaalinen testaus keskittyy:
  - Koodiesimerkkien toimivuuteen ilman virheitä
  - Dokumentaation linkkien toimivuuteen
  - Projektien kääntöjen onnistumiseen
  - Esimerkkien noudattavan hyviä käytäntöjä

### Ennen lähettämistä tarkistettavaa

- Aja `npm run lint` kaikissa package.json-hakemistoissa
- Tarkista markdown-linkkien toimivuus
- Testaa koodiesimerkit selaimessa tai Node.js:ssä
- Varmista, että käännökset säilyttävät oikean rakenteen

## Koodityyliohjeet

### JavaScript

- Käytä modernia ES6+ syntaksia
- Noudata ESLintin standardikonfiguraatioita projekteissa
- Käytä merkityksellisiä muuttujien ja funktioiden nimiä opetustarkoituksiin
- Lisää kommentteja, jotka selittävät käsitteitä oppijoille
- Muotoile koodi Prettierillä, kun se on asetettu

### HTML/CSS

- Semanttiset HTML5-elementit
- Responsiivisen suunnittelun periaatteet
- Selkeät luokkien nimeämiskäytännöt
- Kommentit, jotka selittävät CSS-tekniikoita oppijoille

### Python

- Noudata PEP 8 -tyyliohjeita
- Selkeät, opetukselliset koodiesimerkit
- Käytä tyyppivihjeitä, kun ne auttavat oppimista

### Markdown-dokumentaatio

- Selkeä otsikkohierarkia
- Koodilohkot kielellä merkattuina
- Linkit lisäresursseihin
- Kuvakaappaukset ja kuvat `images/` kansioissa
- Kuvien alt-tekstit saavutettavuutta varten

### Tiedostojen järjestely

- Oppitunnit numeroitu järjestyksessä (1-getting-started-lessons, 2-js-basics jne.)
- Jokaisella projektilla on `solution/` ja usein myös `start/` tai `your-work/` kansiot
- Kuvat tallennettu oppituntikohtaisiin `images/` kansioihin
- Käännökset rakenteessa `translations/{language-code}/`

## Käännös- ja julkaisuohjeet

### Quiz-sovelluksen julkaisu (Azure Static Web Apps)

Quiz-sovellus on konfiguroitu julkaistavaksi Azure Static Web Apps -palveluun:

```bash
cd quiz-app
npm run build      # Luo dist/ -kansion
# Ottaa käyttöön GitHub Actions -työnkulun push-tapahtumassa main-haaraan
```

Azure Static Web Apps -konfiguraatio:
- **Sovelluksen sijainti**: `/quiz-app`
- **Tulostuskansio**: `dist`
- **Työnkulku**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### Dokumentaation PDF:n luonti

```bash
npm install                    # Asenna docsify-to-pdf
npm run convert               # Luo PDF docsista
```

### Docsify-dokumentaatio

```bash
npm install -g docsify-cli    # Asenna Docsify globaalisti
docsify serve                 # Palvele localhost:3000:ssa
```

### Projektikohtaiset buildit

Jokaisella projekti-hakemistolla voi olla oma build-prosessinsa:
- Vue-projektit: `npm run build` luo tuotantokokoelmat
- Staattiset projektit: Ei build-vaihetta, tiedostot palvelimelle sellaisenaan

## Pull request -ohjeet

### Otsikkomuoto

Käytä selkeitä ja kuvaavia otsikoita, jotka kertovat muutoksen kohteen:
- `[Quiz-app] Lisää uusi tietovisa oppitunnille X`
- `[Lesson-3] Korjaa kirjoitusvirhe terrarium-projektissa`
- `[Translation] Lisää espanjankielinen käännös oppitunnille 5`
- `[Docs] Päivitä asennusohjeet`

### Pakolliset tarkistukset

Ennen PR:n lähettämistä:

1. **Koodin laatu**:
   - Aja `npm run lint` asianomaisissa projektihakemistoissa
   - Korjaa kaikki lint-virheet ja varoitukset

2. **Buildin toimivuus**:
   - Aja `npm run build`, jos sovellettavissa
   - Varmista, ettei build-virheitä ilmene

3. **Linkkien toimivuus**:
   - Testaa kaikki markdown-linkit
   - Varmista kuvaviitteiden toimivuus

4. **Sisällön tarkistus**:
   - Tarkista oikeinkirjoitus ja kielioppi
   - Varmista koodiesimerkkien oikeellisuus ja opetuksellisuus
   - Tarkista, että käännökset säilyttävät alkuperäisen merkityksen

### Osallistumisvaatimukset

- Hyväksy Microsoft CLA (automaattinen tarkistus ensimmäisen PR:n yhteydessä)
- Noudata [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/) -käyttäytymissääntöjä
- Katso tarkemmat ohjeet [CONTRIBUTING.md](./CONTRIBUTING.md) -tiedostosta
- Viittaa tarvittaessa issue-numeroihin PR-kuvauksessa

### Arviointiprosessi

- PR:t katselmoidaan ylläpitäjien ja yhteisön toimesta
- Painotus opetuksellisessa selkeydessä
- Koodiesimerkkien tulee noudattaa ajantasaisia hyviä käytäntöjä
- Käännökset tarkistetaan paikkansapitävyyden ja kulttuurisen sopivuuden osalta

## Käännösjärjestelmä

### Automaattinen käännös

- Käyttää GitHub Actionsia ja co-op-translator -työnkulkua
- Kääntää automaattisesti yli 50 kielelle
- Lähdetiedostot ovat pääkansioissa
- Käännetyt tiedostot löytyvät `translations/{language-code}/` -hakemistoista

### Manuaalisten parannusten lisääminen

1. Etsi tiedosto `translations/{language-code}/` -hakemistosta
2. Tee parannuksia säilyttäen rakenne
3. Varmista, että koodiesimerkit toimivat edelleen
4. Testaa mahdolliset paikallistetut tietovisa-aiheet

### Käännösmetadata

Käännetyissä tiedostoissa on mukana metadataotsikko:
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

## Virheenkorjaus ja vianetsintä

### Yleisiä ongelmia

**Quiz-sovellus ei käynnisty**:
- Tarkista Node.js:n versio (v14+ suositeltu)
- Poista `node_modules` ja `package-lock.json`, suorita `npm install` uudelleen
- Tarkista, ettei portti ole käytössä (oletus: Vite käyttää porttia 5173)

**API-palvelin ei käynnisty**:
- Varmista, että Node.js-versio täyttää vähimmäisvaatimuksen (node >=10)
- Tarkista portin vapautuminen
- Varmista, että kaikki riippuvuudet on asennettu komennolla `npm install`

**Selainlaajennus ei lataudu**:
- Tarkista, että manifest.json on oikein muotoiltu
- Katso selaimen konsolista virheilmoituksia
- Noudata selaimen erityisohjeita laajennuksen asennukseen

**Python chat -projektin ongelmat**:
- Varmista, että OpenAI-paketti on asennettu: `pip install openai`
- Tarkista, että GITHUB_TOKEN-ympäristömuuttuja on määritelty
- Tarkista GitHub Models -käyttöoikeudet

**Docsify ei tarjoile dokumentaatiota**:
- Asenna docsify-cli globaalisti: `npm install -g docsify-cli`
- Aja komento arkiston juurihakemistosta
- Varmista, että `docs/_sidebar.md` on olemassa

### Kehitysympäristövinkit

- Käytä VS Codea Live Server -laajennuksen kanssa HTML-projekteissa
- Asenna ESLint ja Prettier -laajennukset yhdenmukaisen muotoilun varmistamiseksi
- Käytä selaimen DevTools-työkaluja JavaScriptin debuggaamiseen
- Vue-projekteissa asenna Vue DevTools selaimen laajennus

### Suorituskyky

- Valtava määrä käännettyjä tiedostoja (yli 50 kieltä) tekee kokonaisklooneista suuria
- Käytä pinnallista kloonausta, jos työskentelet vain sisällön parissa: `git clone --depth 1`
- Poista käännökset hausta, kun työskentelet englanninkielisen sisällön kanssa
- Build-prosessit voivat olla hitaita ensimmäisellä ajokerralla (npm install, Vite build)

## Turvakäytännöt

### Ympäristömuuttujat

- API-avaimia ei koskaan saa tallentaa arkistoon
- Käytä `.env`-tiedostoja (sisältyvät jo `.gitignore`-tiedostoon)
- Dokumentoi vaaditut ympäristömuuttujat projektien READMEssa

### Python-projektit

- Käytä virtuaaliympäristöjä: `python -m venv venv`
- Pidä riippuvuudet ajan tasalla
- GitHub-tokenit tulee rajoittaa minimitason käyttöoikeuksiin

### GitHub Models -käyttö

- Tarvitaan henkilökohtaiset käyttöoikeustokenit (PAT)
- Tokenit tulee tallentaa ympäristömuuttujiksi
- Älä koskaan tallenna tokeneita tai tunnuksia arkistoon

## Lisätietoja

### Kohdeyleisö

- Täysin aloittelijat web-kehityksessä
- Opiskelijat ja itseopiskelijat
- Opettajat, jotka käyttävät opetussuunnitelmaa luokkahuoneissa
- Sisältö on suunniteltu saavutettavaksi ja asteittaisen taitojen kehittämisen mahdollistavaksi

### Opetussuunnitelman filosofia

- Projektipohjainen oppimismenetelmä
- Tiheät tietovisat oppimisen tarkistamiseen
- Käytännön ohjelmointiharjoitukset
- Käytännön esimerkit todellisesta maailmasta
- Perusteiden korostaminen ennen kehysten opettelua

### Arkiston ylläpito

- Aktiivinen oppijoiden ja avustajien yhteisö
- Riittävä päivitystahti riippuvuuksille ja sisällölle
- Ylläpitäjät seuraavat ongelmia ja keskusteluja
- Käännösten päivitys on automatisoitu GitHub Actionsilla

### Liittyvät resurssit

- [Microsoft Learn -moduulit](https://docs.microsoft.com/learn/)
- [Student Hubin materiaalit](https://docs.microsoft.com/learn/student-hub/)
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) suositellaan oppijoille
- Lisäkursseja: Generative AI, Data Science, ML, IoT -opetussuunnitelmat ovat saatavilla

### Työskentely tietyissä projekteissa

Yksityiskohtaiset ohjeet eri projekteihin löytyvät niihin liittyvistä README-tiedostoista:
- `quiz-app/README.md` - Vue 3 tietovisasovellus
- `7-bank-project/README.md` - Pankkisovellus autentikoinnilla
- `5-browser-extension/README.md` - Selainlaajennuksen kehitys
- `6-space-game/README.md` - Canvas-pohjainen peli
- `9-chat-project/README.md` - AI chat assistant -projekti

### Monorepo-rakenne

Vaikka tämä ei ole perinteinen monorepo, arkisto sisältää useita itsenäisiä projekteja:
- Jokainen oppitunti on itsenäinen kokonaisuus
- Projektit eivät jaa riippuvuuksia keskenään
- Työskentele yksittäisten projektien parissa vaikuttamatta muihin
- Kloonaa koko repositorio saadaksesi täyden opetussuunnitelman kokemuksen

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Vastuuvapauslauseke**:
Tämä asiakirja on käännetty käyttämällä tekoälypohjaista käännöspalvelua [Co-op Translator](https://github.com/Azure/co-op-translator). Vaikka pyrimme tarkkuuteen, ota huomioon, että automaattikäännöksissä saattaa esiintyä virheitä tai epätarkkuuksia. Alkuperäistä asiakirjaa sen alkuperäisellä kielellä pidetään auktoritatiivisena lähteenä. Tärkeiden tietojen osalta suositellaan ammattimaista ihmiskäännöstä. Emme ole vastuussa tämän käännöksen käytöstä aiheutuvista väärinymmärryksistä tai virhetulkinnoista.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->