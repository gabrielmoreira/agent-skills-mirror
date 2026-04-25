# AGENTS.md

## Projekt Áttekintés

Ez egy oktatási tanterv-tárhely, amely kezdők számára tanítja a webfejlesztés alapjait. A tanterv egy átfogó, 12 hetes kurzus, amelyet a Microsoft Cloud Advocates fejlesztett ki, és 24 gyakorlati leckét tartalmaz, amelyek JavaScriptet, CSS-t és HTML-t fednek le.

### Főbb összetevők

- **Oktatási tartalom**: 24 strukturált lecke, amely projektalapú modulokba rendezett
- **Gyakorlati projektek**: Terrárium, Gépelő játék, Böngésző kiterjesztés, Űr játék, Bank alkalmazás, Kód szerkesztő és AI chat asszisztens
- **Interaktív kvízek**: 48 kvíz, mindegyik 3 kérdéssel (leckék előtti/utáni értékelések)
- **Többnyelvű támogatás**: Automatikus fordítás 50+ nyelvre GitHub Actions segítségével
- **Technológiák**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (AI projektekhez)

### Architektúra

- Oktatási tárhely leckealapú felépítéssel
- Minden lecke mappa tartalmaz README-t, kód példákat és megoldásokat
- Önálló projektek külön könyvtárakban (quiz-app, különféle lecke projektek)
- Fordítási rendszer GitHub Actions használatával (co-op-translator)
- Dokumentáció Docsify segítségével szolgálva, PDF formátumban is elérhető

## Beállítási parancsok

Ez a tárhely elsősorban oktatási tartalom fogyasztására szolgál. Specifikus projektekkel való munkához:

### Fő tárhely beállítása

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Kvíz alkalmazás beállítása (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Indítsa el a fejlesztői szervert
npm run build      # Készítsen buildet produkcióhoz
npm run lint       # Futtassa az ESLint-et
```

### Bank projekt API (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # Indítsa el az API szervert
npm run lint       # Futtassa az ESLint-et
npm run format     # Formázás Prettier-rel
```

### Böngésző kiterjesztés projektek

```bash
cd 5-browser-extension/solution
npm install
# Kövesse a böngésző-specifikus bővítmény betöltési utasításait
```

### Űr játék projektek

```bash
cd 6-space-game/solution
npm install
# Nyisd meg az index.html fájlt a böngészőben vagy használd a Live Servert
```

### Chat projekt (Python háttér)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Állítsa be a GITHUB_TOKEN környezeti változót
python api.py
```

## Fejlesztési munkafolyamat

### Tartalom hozzájárulók számára

1. **Forkoljuk a tárhelyet** a saját GitHub fiókunkba
2. **Klonoljuk a forkot** helyileg
3. **Hozzunk létre új ágat** a változtatásokhoz
4. Végezzen változtatásokat a lecke tartalmában vagy kód példákban
5. Teszteljük a kódváltozásokat a kapcsolódó projekt könyvtárakban
6. Küldjünk be pull requesteket a hozzájárulási irányelvek szerint

### Tanulók számára

1. Forkoljuk vagy klonoljuk a tárhelyet
2. Lépjünk végig sorban a lecke könyvtárakon
3. Olvassuk el az egyes leckék README fájljait
4. Töltsük ki a lecke előtti kvízeket a https://ff-quizzes.netlify.app/web/ oldalon
5. Dolgozzunk a lecke mappákban lévő kód példákon
6. Teljesítsük a feladatokat és kihívásokat
7. Írjuk meg a lecke utáni kvízeket

### Élő fejlesztés

- **Dokumentáció**: Fussuk a `docsify serve` parancsot a gyökérben (3000-es port)
- **Kvíz alkalmazás**: Fussuk az `npm run dev` parancsot a quiz-app könyvtárban
- **Projektek**: Használjuk a VS Code Live Server bővítményét HTML projektekhez
- **API projektek**: Fussuk az `npm start` parancsot az adott API könyvtárakban

## Tesztelési útmutató

### Kvíz alkalmazás tesztelése

```bash
cd quiz-app
npm run lint       # Ellenőrizze a kódstílus problémákat
npm run build      # Ellenőrizze, hogy a build sikeres legyen
```

### Bank API tesztelése

```bash
cd 7-bank-project/api
npm run lint       # Ellenőrizze a kód stílusproblémáit
node server.js     # Ellenőrizze, hogy a szerver hibák nélkül elindul-e
```

### Általános tesztelési megközelítés

- Ez egy oktatási tárhely átfogó automatizált tesztek nélkül
- Manuális tesztelés a következőkre fókuszál:
  - Kód példák hibamentes futtatása
  - Dokumentációban lévő linkek helyes működése
  - Projektek sikeres buildelése
  - Példák legjobb gyakorlati elvek szerinti követése

### Benyújtás előtti ellenőrzések

- Futtassuk az `npm run lint` parancsot azokban a könyvtárakban, ahol van package.json
- Ellenőrizzük a markdown linkek érvényességét
- Teszteljük a kód példákat böngészőben vagy Node.js-ben
- Ellenőrizzük, hogy a fordítások megőrzik a helyes struktúrát

## Kódstílus irányelvek

### JavaScript

- Használj modern ES6+ szintaxist
- Kövesd a projektekben megadott ESLint konfigurációkat
- Használj érthető változó- és függvénynév- megnevezéseket a tanulási cél érdekében
- Adj hozzászólásokat a fogalmak magyarázatához
- Használj Prettier-t a formázáshoz ahol konfigurálva van

### HTML/CSS

- Szemantikus HTML5 elemek
- Reszponzív tervezési elvek
- Egyértelmű osztálynevek használata
- Kommentárok magyarázzák a CSS technikákat a tanulók számára

### Python

- PEP 8 stílusirányelvek
- Tiszta, oktatási célú kód példák
- Típus annotációk, ahol hasznos a tanuláshoz

### Markdown dokumentáció

- Tiszta címsor hierarchia
- Kódblokkok nyelvi megjelöléssel
- Hivatkozások további erőforrásokra
- Képernyőképek és képek az `images/` könyvtárakban
- Alt szövegek a képekhez az akadálymentesség érdekében

### Fájl szervezés

- A leckék számozva, sorban (1-getting-started-lessons, 2-js-basics, stb.)
- Minden projekt tartalmaz `solution/` és gyakran `start/` vagy `your-work/` mappákat
- Képek a lecke specifikus `images/` mappákban tárolva
- Fordítások `translations/{language-code}/` struktúrában találhatók

## Build és Telepítés

### Kvíz alkalmazás telepítése (Azure Static Web Apps)

A quiz-app konfigurálva van Azure Static Web Apps telepítésére:

```bash
cd quiz-app
npm run build      # Létrehozza a dist/ mappát
# Közzéteszi a GitHub Actions munkafolyamattal push esetén a main ágra
```

Azure Static Web Apps beállítás:
- **App hely**: `/quiz-app`
- **Kimeneti mappa**: `dist`
- **Munkafolyamat**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### Dokumentáció PDF generálás

```bash
npm install                    # docsify-to-pdf telepítése
npm run convert               # PDF generálása a dokumentációból
```

### Docsify Dokumentáció

```bash
npm install -g docsify-cli    # Telepítsd a Docsify-t globálisan
docsify serve                 # Szolgáltasd a localhost:3000 címen
```

### Projekt-specifikus buildelések

Minden projekt könyvtár saját build folyamatot tartalmazhat:
- Vue projektek: `npm run build` létrehozza a gyártási csomagokat
- Statikus projektek: nincs build lépés, fájlok közvetlen kiszolgálása

## Pull Request irányelvek

### Cím formátuma

Használjunk világos, leíró címeket, amelyek jelzik a változtatás területét:
- `[Quiz-app] Új lecke kvíz hozzáadása X`
- `[Lesson-3] Elírás javítása a terrárium projektben`
- `[Translation] Spanyol fordítás hozzáadása az 5. leckéhez`
- `[Docs] Frissített beállítási utasítások`

### Kötelező ellenőrzések

PR benyújtása előtt:

1. **Kódminőség**:
   - Futtassuk az `npm run lint` parancsot az érintett projekt könyvtárakban
   - Javítsuk az összes lint hibát és figyelmeztetést

2. **Build ellenőrzés**:
   - Futtassuk az `npm run build` parancsot, ha alkalmazható
   - Biztosítsuk, hogy ne legyen build hiba

3. **Linkek érvényessége**:
   - Teszteljük az összes markdown linket
   - Ellenőrizzük a kép hivatkozások működését

4. **Tartalom felülvizsgálat**:
   - Ellenőrizzük helyesírást és nyelvtant
   - Győződjünk meg a kód példák helyességéről és oktató jellegéről
   - Validáljuk, hogy a fordítások megőrzik az eredeti jelentést

### Hozzájárulási feltételek

- Elfogadás a Microsoft CLA-t (automatikus ellenőrzés az első PR-nél)
- Kövessük a [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/) irányelveit
- Részletes útmutató a [CONTRIBUTING.md](./CONTRIBUTING.md) fájlban
- Hivatkozzunk issue számokra a PR leírásában, ha vonatkozik

### Áttekintési folyamat

- PR-eket a karbantartók és a közösség átnézi
- Oktatási érthetőség elsődleges szempont
- Kód példák kövessék a legjobb aktuális gyakorlatokat
- Fordítások pontosságát és kulturális megfelelősségét ellenőrzik

## Fordítási rendszer

### Automatikus fordítás

- GitHub Actions használ co-op-translator munkafolyamatot
- Több mint 50 nyelvre fordít automatikusan
- Forrásfájlok a fő könyvtárakban vannak
- Fordított fájlok a `translations/{language-code}/` könyvtárakban

### Kézi fordítási fejlesztések hozzáadása

1. Keressük meg a fájlt a `translations/{language-code}/` mappában
2. Végezzük el a fejlesztéseket, megőrizve a struktúrát
3. Biztosítsuk, hogy a kód példák működőképesek maradjanak
4. Teszteljük a lokalizált kvíz tartalmat

### Fordítási metaadatok

A fordított fájlok tartalmaznak metaadat fejlécet:
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

## Hibakeresés és problémamegoldás

### Gyakori problémák

**Kvíz alkalmazás nem indul el**:
- Ellenőrizzük a Node.js verziót (v14+ ajánlott)
- Töröljük a `node_modules` és `package-lock.json` fájlokat, majd futtassuk újra az `npm install`-t
- Ellenőrizzük, hogy nincs-e port konfliktus (alapértelmezett: Vite a 5173-as portot használja)

**API szerver nem indul**:
- Győződjünk meg, hogy a Node.js verzió megfelel (node >=10)
- Ellenőrizzük, nincs-e használatban a port
- Biztosítsuk, hogy minden függőség telepítve van az `npm install` lefuttatásával

**Böngésző kiterjesztés nem töltődik be**:
- Ellenőrizzük a manifest.json helyes formátumát
- Nézzük meg a böngésző konzolt hibákért
- Kövessük a böngésző-specifikus kiterjesztés telepítési utasításait

**Python chat projekt problémák**:
- Győződjünk meg, hogy az OpenAI csomag telepítve van: `pip install openai`
- Ellenőrizzük a GITHUB_TOKEN környezeti változó beállítását
- Nézzük meg a GitHub Modellek elérési engedélyeit

**Docsify nem szolgál ki dokumentációt**:
- Telepítsük globálisan a docsify-cli-t: `npm install -g docsify-cli`
- Futassuk a repository gyökérkönyvtárából
- Ellenőrizzük, hogy létezik-e a `docs/_sidebar.md`

### Fejlesztői környezet tippek

- Használjuk a VS Code-ot Live Server bővítménnyel HTML projektekhez
- Telepítsük az ESLint és Prettier bővítményeket az egységes formázáshoz
- Használjuk a böngésző fejlesztői eszközeit JavaScript hibakereséshez
- Vue projektekhez telepítsük a Vue DevTools böngésző bővítményt

### Teljesítmény szempontok

- Nagyszámú fordított fájl (50+ nyelv) miatt a teljes klón nagy méretű
- Használjuk a sekély klónozást, ha csak tartalmon dolgozunk: `git clone --depth 1`
- Kizárhatjuk a fordításokat a keresésekből, ha csak angol tartalmat dolgozunk
- Build folyamatok lassúak lehetnek első futtatáskor (npm install, Vite build)

## Biztonsági megfontolások

### Környezeti változók

- API kulcsokat soha ne tegyünk be a tárhelybe
- Használjunk `.env` fájlokat (már benne vannak `.gitignore`-ban)
- Dokumentáljuk a szükséges környezeti változókat a projekt README-kben

### Python projektek

- Virtuális környezet használata: `python -m venv venv`
- Függőségek naprakészen tartása
- GitHub tokenek minimális szükséges jogosultsággal

### GitHub Modellek elérés

- Személyes hozzáférési tokeneket (PAT) igényel a GitHub Modellek használata
- A tokeneket környezeti változóként kell tárolni
- Soha ne kerüljön be token vagy hitelesítő adat a forrásba

## További megjegyzések

### Célközönség

- Teljesen kezdők a webfejlesztésben
- Diákok és önálló tanulók
- Tanárok, akik az oktatási anyagot osztályokban használják
- A tartalom akadálymentesített és fokozatos képességfejlesztésre tervezett

### Oktatási filozófia

- Projektalapú tanulási módszer
- Gyakori tudásellenőrzések (kvízek)
- Gyakorlati kódolási feladatok
- Valós példák alkalmazása
- Az alapokra fókuszál a keretrendszerek előtt

### Tárhely karbantartás

- Aktív tanuló és hozzájáruló közösség
- Függőségek és tartalom rendszeres frissítése
- Issue-k és megbeszélések folyamatos követése a karbantartók által
- Fordítás frissítések automatizáltan GitHub Actions segítségével

### Kapcsolódó források

- [Microsoft Learn modulok](https://docs.microsoft.com/learn/)
- [Student Hub források](https://docs.microsoft.com/learn/student-hub/)
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) ajánlott tanulóknak
- Egyéb kurzusok: Generatív AI, Adattudomány, ML, IoT tananyagok elérhetők

### Specifikus projektek kezelése

Részletes utasítások az egyes projektekhez a README fájlokban:
- `quiz-app/README.md` - Vue 3 kvíz alkalmazás
- `7-bank-project/README.md` - Bank alkalmazás hitelesítéssel
- `5-browser-extension/README.md` - Böngésző kiterjesztés fejlesztés
- `6-space-game/README.md` - Vászon alapú játék fejlesztés
- `9-chat-project/README.md` - AI chat asszisztens projekt

### Monorepo struktúra

Habár nem hagyományos monorepo, ez a tárhely több önálló projektet tartalmaz:
- Minden lecke önálló
- Projektek nem osztanak meg függőségeket
- Egyedi projektek fejlesztése anélkül, hogy másokat befolyásolnánk
- Teljes tanterv élményéhez a teljes tárhely klónozása ajánlott

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Nyilatkozat**:
Ez a dokumentum az AI fordítási szolgáltatás, a [Co-op Translator](https://github.com/Azure/co-op-translator) segítségével készült. Bár törekszünk a pontosságra, kérjük, vegye figyelembe, hogy az automatikus fordítások hibákat vagy pontatlanságokat tartalmazhatnak. Az eredeti dokumentum az anyanyelvén tekintendő hiteles forrásnak. Kritikus információk esetén javasolt a professzionális emberi fordítás. Nem vállalunk felelősséget ezen fordítás használatából eredő félreértésekért vagy félreértelmezésekért.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->