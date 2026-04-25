# AGENTS.md

## Przegląd Projektu

To repozytorium edukacyjne służące do nauczania podstaw web developmentu dla początkujących. Program nauczania to kompleksowy 12-tygodniowy kurs opracowany przez Microsoft Cloud Advocates, obejmujący 24 praktyczne lekcje dotyczące JavaScript, CSS i HTML.

### Kluczowe Komponenty

- **Treści edukacyjne**: 24 ustrukturyzowane lekcje zorganizowane w moduły oparte na projektach
- **Projekty praktyczne**: Terrarium, Gra Typowania, Rozszerzenie przeglądarki, Gra Kosmiczna, Aplikacja Bankowa, Edytor kodu i Asystent czatu AI
- **Interaktywne quizy**: 48 quizów po 3 pytania (oceny przed i po lekcji)
- **Wsparcie wielojęzyczne**: Automatyczne tłumaczenia na 50+ języków za pomocą GitHub Actions
- **Technologie**: HTML, CSS, JavaScript, Vue.js 3, Vite, Node.js, Express, Python (dla projektów AI)

### Architektura

- Edukacyjne repozytorium o strukturze opartej na lekcjach
- Każdy folder lekcji zawiera README, przykłady kodu i rozwiązania
- Samodzielne projekty w osobnych katalogach (quiz-app, różne projekty lekcji)
- System tłumaczeń wykorzystujący GitHub Actions (co-op-translator)
- Dokumentacja serwowana przez Docsify i dostępna jako PDF

## Komendy do Ustawienia

To repozytorium jest głównie do konsumpcji treści edukacyjnych. Do pracy z konkretnymi projektami:

### Podstawowa konfiguracja repozytorium

```bash
git clone https://github.com/microsoft/Web-Dev-For-Beginners.git
cd Web-Dev-For-Beginners
```

### Konfiguracja Quiz App (Vue 3 + Vite)

```bash
cd quiz-app
npm install
npm run dev        # Uruchom serwer deweloperski
npm run build      # Buduj na produkcję
npm run lint       # Uruchom ESLint
```

### Bank Project API (Node.js + Express)

```bash
cd 7-bank-project/api
npm install
npm start          # Uruchom serwer API
npm run lint       # Uruchom ESLint
npm run format     # Sformatuj za pomocą Prettier
```

### Projekty Rozszerzenia Przeglądarki

```bash
cd 5-browser-extension/solution
npm install
# Postępuj zgodnie z instrukcjami ładowania rozszerzeń specyficznymi dla przeglądarki
```

### Projekty Gry Kosmicznej

```bash
cd 6-space-game/solution
npm install
# Otwórz index.html w przeglądarce lub użyj Live Server
```

### Projekt Czat (Backend Python)

```bash
cd 9-chat-project/solution/backend/python
pip install openai
# Ustaw zmienną środowiskową GITHUB_TOKEN
python api.py
```

## Przebieg Rozwoju

### Dla wniesienia treści

1. **Zrób fork repozytorium** na swoje konto GitHub
2. **Sklonuj swojego forka** lokalnie
3. **Utwórz nową gałąź** na swoje zmiany
4. Wprowadź zmiany w treści lekcji lub przykładach kodu
5. Testuj zmiany kodu w odpowiednich katalogach projektów
6. Prześlij pull requesty zgodnie z wytycznymi contribution

### Dla uczących się

1. Zrób fork lub sklonuj repozytorium
2. Przechodź przez katalogi lekcji kolejno
3. Czytaj pliki README dla każdej lekcji
4. Wykonaj quizy przed lekcjami na https://ff-quizzes.netlify.app/web/
5. Pracuj z przykładami kodu w folderach lekcji
6. Wykonuj zadania i wyzwania
7. Przejdź quizy po lekcji

### Live Development

- **Dokumentacja**: Uruchom `docsify serve` w katalogu głównym (port 3000)
- **Quiz App**: Uruchom `npm run dev` w katalogu quiz-app
- **Projekty**: Użyj rozszerzenia VS Code Live Server dla projektów HTML
- **Projekty API**: Uruchom `npm start` w odpowiednich katalogach API

## Instrukcje Testowania

### Testowanie Quiz App

```bash
cd quiz-app
npm run lint       # Sprawdź problemy ze stylem kodu
npm run build      # Zweryfikuj, czy kompilacja zakończyła się sukcesem
```

### Testowanie Bank API

```bash
cd 7-bank-project/api
npm run lint       # Sprawdź problemy ze stylem kodu
node server.js     # Sprawdź, czy serwer uruchamia się bez błędów
```

### Ogólne podejście do testowania

- To repozytorium edukacyjne bez rozbudowanych testów automatycznych
- Testowanie ręczne skupia się na:
  - Przykłady kodu działają bez błędów
  - Linki w dokumentacji działają poprawnie
  - Budowy projektów kończą się sukcesem
  - Przykłady są zgodne z najlepszymi praktykami

### Kontrole przed wysłaniem

- Uruchom `npm run lint` w katalogach z package.json
- Sprawdź poprawność linków markdown
- Testuj przykłady kodu w przeglądarce lub Node.js
- Zweryfikuj, że tłumaczenia zachowują właściwą strukturę

## Zasady Stylu Kodu

### JavaScript

- Używaj nowoczesnej składni ES6+
- Stosuj standardowe konfiguracje ESLint podane w projektach
- Używaj czytelnych nazw zmiennych i funkcji dla jasności edukacyjnej
- Dodawaj komentarze objaśniające koncepcje dla uczących się
- Formatuj przy użyciu Prettier tam, gdzie jest skonfigurowany

### HTML/CSS

- Semantyczne elementy HTML5
- Zasady projektowania responsywnego
- Jasna konwencja nazewnictwa klas
- Komentarze objaśniające techniki CSS dla uczących

### Python

- Zasady stylu PEP 8
- Jasne, edukacyjne przykłady kodu
- Adnotacje typów tam, gdzie pomagają w nauce

### Dokumentacja w Markdown

- Jasna hierarchia nagłówków
- Bloki kodu z określeniem języka
- Linki do dodatkowych zasobów
- Zrzuty ekranów i obrazy w katalogach `images/`
- Tekst alternatywny dla obrazów dla dostępności

### Organizacja Plików

- Lekcje numerowane kolejno (1-getting-started-lessons, 2-js-basics, itd.)
- Każdy projekt posiada katalogi `solution/` oraz często `start/` lub `your-work/`
- Obrazy przechowywane w folderach `images/` specyficznych dla lekcji
- Tłumaczenia w strukturze `translations/{language-code}/`

## Budowa i Wdrożenie

### Wdrożenie Quiz App (Azure Static Web Apps)

Quiz-app jest skonfigurowany do wdrożenia na Azure Static Web Apps:

```bash
cd quiz-app
npm run build      # Tworzy folder dist/
# Wdraża za pomocą workflow GitHub Actions przy pushu do gałęzi main
```

Konfiguracja Azure Static Web Apps:
- **Lokalizacja aplikacji**: `/quiz-app`
- **Lokalizacja outputu**: `dist`
- **Workflow**: `.github/workflows/azure-static-web-apps-ashy-river-0debb7803.yml`

### Generowanie dokumentacji PDF

```bash
npm install                    # Zainstaluj docsify-to-pdf
npm run convert               # Wygeneruj plik PDF z docs
```

### Dokumentacja Docsify

```bash
npm install -g docsify-cli    # Zainstaluj Docsify globalnie
docsify serve                 # Serwuj na localhost:3000
```

### Budowy specyficzne dla projektów

Każdy katalog projektu może mieć własny proces budowy:
- Projekty Vue: `npm run build` tworzy produkcyjne bundlery
- Projekty statyczne: brak kroku budowania, serwuj pliki bezpośrednio

## Wytyczne dla Pull Requestów

### Format tytułu

Używaj jasnych, opisowych tytułów wskazujących obszar zmian:
- `[Quiz-app] Dodaj nowy quiz do lekcji X`
- `[Lesson-3] Popraw literówkę w projekcie terrarium`
- `[Translation] Dodaj tłumaczenie na hiszpański dla lekcji 5`
- `[Docs] Aktualizuj instrukcje konfiguracji`

### Wymagane kontrole

Przed wysłaniem PR:

1. **Jakość kodu**:
   - Uruchom `npm run lint` w katalogach projektów
   - Napraw wszystkie błędy i ostrzeżenia lintingu

2. **Weryfikacja builda**:
   - Uruchom `npm run build` jeśli dotyczy
   - Upewnij się, że brak błędów budowania

3. **Walidacja linków**:
   - Testuj wszystkie linki markdown
   - Sprawdź działanie odwołań do obrazów

4. **Przegląd zawartości**:
   - Korekta ortografii i gramatyki
   - Upewnij się, że przykłady kodu są poprawne i edukacyjne
   - Sprawdź, czy tłumaczenia zachowują oryginalne znaczenie

### Wymagania dotyczące wkładu

- Zgoda na Microsoft CLA (automatyczna kontrola przy pierwszym PR)
- Przestrzeganie [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/)
- Szczegółowe wytyczne w [CONTRIBUTING.md](./CONTRIBUTING.md)
- W referencji do PR podaj numery zgłoszeń, jeśli dotyczy

### Proces przeglądu

- PRy recenzowane przez opiekunów i społeczność
- Priorytetem jest jasność edukacyjna
- Przykłady kodu powinny korzystać z aktualnych najlepszych praktyk
- Tłumaczenia sprawdzane pod kątem dokładności i odpowiedniości kulturowej

## System Tłumaczeń

### Automatyczne tłumaczenie

- Wykorzystuje GitHub Actions z workflow co-op-translator
- Automatyczne tłumaczenie na ponad 50 języków
- Pliki źródłowe w głównych katalogach
- Pliki tłumaczeń w katalogach `translations/{language-code}/`

### Dodawanie ręcznych poprawek tłumaczeń

1. Znajdź plik w `translations/{language-code}/`
2. Dokonaj poprawek zachowując strukturę
3. Upewnij się, że przykłady kodu działają
4. Testuj wszelkie zlokalizowane treści quizowe

### Metadane tłumaczenia

Pliki przetłumaczone zawierają nagłówek metadanych:
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

## Debugowanie i Rozwiązywanie Problemów

### Najczęstsze problemy

**Quiz app nie startuje**:
- Sprawdź wersję Node.js (zalecana v14+)
- Usuń `node_modules` i `package-lock.json`, uruchom ponownie `npm install`
- Sprawdź konflikty portów (domyślnie Vite używa portu 5173)

**Serwer API nie uruchamia się**:
- Sprawdź, czy wersja Node.js spełnia minimum (node >=10)
- Sprawdź, czy port nie jest już zajęty
- Upewnij się, że wszystkie zależności zainstalowane `npm install`

**Rozszerzenie przeglądarki się nie ładuje**:
- Sprawdź poprawność manifest.json
- Sprawdź konsolę przeglądarki pod kątem błędów
- Postępuj zgodnie z instrukcjami instalacji rozszerzeń specyficznych dla przeglądarki

**Problemy z projektem czatu w Pythonie**:
- Upewnij się, że pakiet OpenAI jest zainstalowany: `pip install openai`
- Sprawdź, czy zmienna środowiskowa GITHUB_TOKEN jest ustawiona
- Zweryfikuj uprawnienia dostępu do GitHub Models

**Docsify nie serwuje dokumentów**:
- Zainstaluj docsify-cli globalnie: `npm install -g docsify-cli`
- Uruchom z katalogu root repozytorium
- Sprawdź, czy istnieje `docs/_sidebar.md`

### Wskazówki dotyczące środowiska programistycznego

- Używaj VS Code z rozszerzeniem Live Server dla projektów HTML
- Zainstaluj rozszerzenia ESLint i Prettier dla spójnego formatowania
- Korzystaj z DevTools przeglądarki do debugowania JavaScript
- Dla projektów Vue zainstaluj rozszerzenie Vue DevTools do przeglądarki

### Względy wydajnościowe

- Duża liczba plików tłumaczeń (50+ języków) powoduje duże klony
- Używaj płytkiego klonu jeśli pracujesz tylko nad treścią: `git clone --depth 1`
- Wyklucz tłumaczenia z wyszukiwań podczas pracy nad angielską wersją
- Procesy budowania mogą być wolne przy pierwszym uruchomieniu (npm install, build Vite)

## Aspekty Bezpieczeństwa

### Zmienne środowiskowe

- Klucze API nie powinny być nigdy commitowane do repozytorium
- Używaj plików `.env` (już w `.gitignore`)
- Udokumentuj wymagane zmienne środowiskowe w README projektów

### Projekty Python

- Używaj wirtualnych środowisk: `python -m venv venv`
- Aktualizuj zależności na bieżąco
- Tokenty GitHub powinny mieć minimalne wymagane uprawnienia

### Dostęp do GitHub Models

- Personal Access Tokens (PAT) wymagane do GitHub Models
- Tokenty powinny być przechowywane jako zmienne środowiskowe
- Nigdy nie commituj tokenów ani danych uwierzytelniających

## Dodatkowe Uwagi

### Grupa docelowa

- Całkowici początkujący w web developmencie
- Studenci i samoucy
- Nauczyciele korzystający z programu w klasie
- Treść zaprojektowana z myślą o dostępności i stopniowym rozwoju umiejętności

### Filozofia edukacyjna

- Nauka oparta na projektach
- Częste sprawdzanie wiedzy (quizy)
- Praktyczne ćwiczenia kodowania
- Przykłady zastosowań w realnym świecie
- Skupienie na podstawach przed frameworkami

### Utrzymanie repozytorium

- Aktywna społeczność uczących się i współtwórców
- Regularne aktualizacje zależności i treści
- Monitorowane zgłoszenia i dyskusje przez opiekunów
- Automatyczne aktualizacje tłumaczeń przez GitHub Actions

### Powiązane zasoby

- [Moduły Microsoft Learn](https://docs.microsoft.com/learn/)
- [Zasoby Student Hub](https://docs.microsoft.com/learn/student-hub/)
- [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) rekomendowane dla uczących się
- Dodatkowe kursy: Generative AI, Data Science, ML, IoT dostępne

### Praca z konkretnymi projektami

Dla szczegółowych instrukcji dot. poszczególnych projektów zobacz pliki README w:
- `quiz-app/README.md` - aplikacja quizowa Vue 3
- `7-bank-project/README.md` - aplikacja bankowa z autentykacją
- `5-browser-extension/README.md` - rozwój rozszerzenia przeglądarki
- `6-space-game/README.md` - rozwój gry na canvasie
- `9-chat-project/README.md` - projekt asystenta czatu AI

### Struktura Monorepo

Chociaż to nie jest tradycyjne monorepo, repozytorium zawiera wiele niezależnych projektów:
- Każda lekcja jest autonomiczna
- Projekty nie dzielą zależności
- Pracuj nad pojedynczymi projektami bez wpływu na inne
- Sklonuj całe repo dla pełnego doświadczenia kursu

---

<!-- CO-OP TRANSLATOR DISCLAIMER START -->
**Zastrzeżenie**:
Niniejszy dokument został przetłumaczony przy użyciu usługi tłumaczeń AI [Co-op Translator](https://github.com/Azure/co-op-translator). Chociaż dążymy do dokładności, prosimy mieć na uwadze, że automatyczne tłumaczenia mogą zawierać błędy lub nieścisłości. Oryginalny dokument w języku źródłowym powinien być uważany za źródło autorytatywne. W przypadku istotnych informacji zaleca się profesjonalne tłumaczenie przez człowieka. Nie ponosimy odpowiedzialności za jakiekolwiek nieporozumienia lub błędne interpretacje wynikające z korzystania z tego tłumaczenia.
<!-- CO-OP TRANSLATOR DISCLAIMER END -->