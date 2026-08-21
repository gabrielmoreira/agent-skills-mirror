---
name: react-i18next
description: "Sets up react-i18next on i18next: useTranslation, withTranslation, Trans, namespaces, plurals, interpolation, language detection, TypeScript resources, and Next/Remix/Gatsby SSR. Use when adding i18n, locales, RTL, or language switching in React or React Native. Not for Django/gettext backends, Expo +api.ts routes, or writing the marketing copy itself."
version: 1.0.1
---

# react-i18next Skill

## Overview

react-i18next is the standard internationalization framework for React / React Native, built on top of i18next. This skill covers installation, configuration, all four API surfaces (hooks, HOC, render prop, Trans), common patterns, TypeScript support, SSR, and testing.

> **Key mental model**: i18next is the core translation engine (config, plurals, interpolation, formatting). react-i18next is the React binding layer that connects i18next to your components via hooks, HOCs, render props, and the Trans component.

## When to Use

Use this skill whenever the user wants to:
- Add multi-language support to a React or React Native application
- Set up or configure i18next (inline resources, HTTP backend, language detection)
- Use `useTranslation`, `withTranslation`, `Translation` render prop, or `Trans` component
- Implement language switching, namespaces, plurals, interpolation, context, or nesting
- Set up TypeScript type-safe translations
- Configure SSR i18n for Next.js, Remix, or Gatsby
- Test components that use react-i18next

## Prerequisites

- A React or React Native project with a working build setup
- Node.js and npm/yarn/pnpm installed
- For SSR: Next.js, Remix, or Gatsby project scaffolded
- For TypeScript: react-i18next >= 13.0.0 and i18next >= 23.0.1

## Procedure

### 1. Install Packages

```bash
npm install react-i18next i18next --save

# Common companion packages:
npm install i18next-http-backend i18next-browser-languagedetector --save
```

### 2. Create i18n Configuration File

Create `i18n.js` (or `i18n.ts`) beside your entry point. This is the single source of truth for your i18n setup.

#### Minimal setup (inline resources)

```js
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: {
        translation: {
          "welcome": "Welcome to our app"
        }
      },
      tr: {
        translation: {
          "welcome": "Uygulamamıza hoş geldiniz"
        }
      }
    },
    lng: 'en',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false // React already escapes by default
    }
  });

export default i18n;
```

#### Production setup (with backend + language detection)

```js
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import Backend from 'i18next-http-backend';
import LanguageDetector from 'i18next-browser-languagedetector';

i18n
  .use(Backend) // loads translations from /public/locales/{lng}/{ns}.json
  .use(LanguageDetector) // detects user language
  .use(initReactI18next) // binds i18next to React
  .init({
    fallbackLng: 'en',
    debug: true, // set false in production
    interpolation: {
      escapeValue: false
    },
    // react-specific options (all optional):
    // react: {
    //   bindI18n: 'languageChanged',
    //   bindI18nStore: '',
    //   transEmptyNodeValue: '',
    //   transSupportBasicHtmlNodes: true,
    //   transKeepBasicHtmlNodesFor: ['br', 'strong', 'i', 'p'],
    //   useSuspense: true,
    // }
  });

export default i18n;
```

### 3. Import in Entry Point

```js
import './i18n'; // must be imported before App
```

### 4. Set Up Translation File Structure (when using i18next-http-backend)

Place files at:

```
public/
  locales/
    en/
      translation.json    # default namespace
      common.json         # additional namespace
    tr/
      translation.json
      common.json
```

### 5. Use Translations in Components

Choose the API based on your use case:

| Method | Use when |
|--------|----------|
| `useTranslation` hook | Functional components (recommended) |
| `withTranslation` HOC | Class components or wrapping any component |
| `Translation` render prop | Need `t` function in any component type |
| `Trans` component | Translating JSX trees with embedded HTML/components |

#### useTranslation Hook (primary API)

```jsx
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t, i18n } = useTranslation();
  return <h1>{t('welcome')}</h1>;
}
```

**Namespace loading:**

```jsx
const { t } = useTranslation('common'); // single namespace
const { t } = useTranslation(['ns1', 'ns2']); // multiple (first = default)
t('key'); // looks up in default ns
t('key', { ns: 'ns2' }); // explicit namespace
```

**keyPrefix** (react-i18next >= 11.12.0, i18next >= 20.6.0):

```jsx
// For deeply nested keys: { "very": { "deeply": { "nested": { "key": "value" }}}}
const { t } = useTranslation('translation', { keyPrefix: 'very.deeply.nested' });
t('key'); // "value"
```

**Fixed language** (react-i18next >= 12.3.1):

```jsx
const { t } = useTranslation('translation', { lng: 'de' });
```

**Without Suspense:**

```jsx
const { t, i18n, ready } = useTranslation('ns1', { useSuspense: false });
if (!ready) return <Loading />; // must handle loading state yourself
```

**Suspense behavior**: By default, `useTranslation` triggers React Suspense while translations load. Wrap your app (or relevant subtree) in `<Suspense fallback="loading">`.

#### withTranslation HOC

```jsx
import { withTranslation } from 'react-i18next';

function MyComponent({ t, i18n }) {
  return <p>{t('greeting')}</p>;
}
export default withTranslation()(MyComponent); // default ns
export default withTranslation('common')(MyComponent); // specific ns
export default withTranslation(['ns1', 'ns2'])(MyComponent); // multiple
```

Without Suspense: pass `useSuspense={false}` as a prop, then check `props.tReady`.

#### Translation Render Prop

```jsx
import { Translation } from 'react-i18next';

function MyComponent() {
  return (
    <Translation ns="common">
      {(t, { i18n }) => <p>{t('hello')}</p>}
    </Translation>
  );
}
```

#### Trans Component

Use Trans **only** when you need to embed React elements (links, bold text, components) within a translated string. For plain text, use `t()` instead.

```jsx
import { Trans, useTranslation } from 'react-i18next';

function Welcome({ name, count }) {
  const { t } = useTranslation();
  return (
    <Trans i18nKey="userMessages" count={count}>
      Hello <strong title={t('nameTitle')}>{{name}}</strong>,
      you have {{count}} unread message.
      <Link to="/msgs">Go to messages</Link>.
    </Trans>
  );
}
```

Translation JSON:

```json
{
  "userMessages_one": "Hello <1>{{name}}</1>, you have {{count}} unread message. <5>Go to messages</5>.",
  "userMessages_other": "Hello <1>{{name}}</1>, you have {{count}} unread messages. <5>Go to messages</5>."
}
```

**Named components (v11.6.0+)** — cleaner than indexed tags:

```jsx
<Trans
  i18nKey="myKey"
  defaults="hello <italic>beautiful</italic> <bold>{{what}}</bold>"
  values={{ what: 'world' }}
  components={{ italic: <i />, bold: <strong /> }}
/>
```

JSON: `"myKey": "hello <italic>beautiful</italic> <bold>{{what}}</bold>"`

**Simple HTML elements** (v10.4.0+): By default, `<br/>`, `<strong>`, `<i>`, `<p>` are kept as-is in translation strings (controlled by `transSupportBasicHtmlNodes` and `transKeepBasicHtmlNodesFor` options).

**Index numbering rules**: Children of Trans are numbered by their position in the children array. Strings and interpolation objects get indices but aren't wrapped in tags. Elements get `<N>...</N>` tags.

Trans props and advanced patterns: this section plus the official [Trans component](https://react.i18next.com/latest/trans-component) docs.

### 6. Implement Common Patterns

#### Language Switching

```jsx
function LanguageSwitcher() {
  const { i18n } = useTranslation();
  return (
    <select value={i18n.language} onChange={e => i18n.changeLanguage(e.target.value)}>
      <option value="en">English</option>
      <option value="tr">Türkçe</option>
    </select>
  );
}
```

#### Using t() Outside Components

```js
import i18n from './i18n';
i18n.t('my.key');
```

#### I18nextProvider (Multiple Instances)

Only needed if you support multiple i18next instances (e.g., component libraries) or SSR:

```jsx
import { I18nextProvider } from 'react-i18next';
import i18n from './i18n';

<I18nextProvider i18n={i18n} defaultNS="translation">
  <App />
</I18nextProvider>
```

#### Namespaces (Multiple Translation Files)

```jsx
const { t } = useTranslation(['page1', 'common']);
t('key'); // from 'page1' (first namespace)
t('key', { ns: 'common' }); // from 'common'
```

Components using `useTranslation`, `withTranslation`, or `Translation` will automatically Suspense until their requested namespaces are loaded — no need to load all translations upfront.

#### Interpolation

```json
{ "greeting": "Hello {{name}}, you are {{age}} years old" }
```
```jsx
t('greeting', { name: 'Ali', age: 28 })
```

#### Plurals

i18next uses ICU-like plural suffixes. For English:

```json
{
  "item_one": "{{count}} item",
  "item_other": "{{count}} items"
}
```
```jsx
t('item', { count: 5 }) // "5 items"
```

#### Context

```json
{
  "friend_male": "A boyfriend",
  "friend_female": "A girlfriend"
}
```
```jsx
t('friend', { context: 'male' })
```

#### Nesting

```json
{
  "app": { "name": "MyApp" },
  "intro": "Welcome to $t(app.name)"
}
```

### 7. TypeScript Setup (optional)

Requires react-i18next >= 13.0.0 and i18next >= 23.0.1.

Follow the official guide at https://www.i18next.com/overview/typescript. Key steps:

1. Create a resources type definition file
2. Augment the `i18next` module with your resource types
3. The `t` function then uses accessor syntax: `t($ => $.my.key)`

### 8. SSR Setup (Next.js, Remix, Gatsby)

- **Next.js (App Router)**: Use i18next directly with the App Router pattern (this section; official SSR notes: https://www.i18next.com/overview/getting-started)
- **Next.js (Pages Router)**: Use `next-i18next` which wraps react-i18next
- **Remix**: Use `remix-i18next`
- **Gatsby**: Use `gatsby-plugin-react-i18next`

For custom SSR, use `useSSR` hook or `withSSR` HOC:

```jsx
import { useSSR } from 'react-i18next';
function InitSSR({ initialI18nStore, initialLanguage }) {
  useSSR(initialI18nStore, initialLanguage);
  return <App />;
}
```

Framework adapters (`next-i18next`, `remix-i18next`, `gatsby-plugin-react-i18next`) own the remaining SSR wiring; do not invent a second i18n instance on the server.

### 9. Testing

Three approaches, from simplest to most thorough:

**1. Mock the hook (Jest):**

```js
jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key) => key,
    i18n: { changeLanguage: () => new Promise(() => {}) },
  }),
  initReactI18next: { type: '3rdParty', init: () => {} },
}));
```

**2. Export bare component + pass t as prop:**

```js
export { MyComponent }; // for testing
export default withTranslation('ns')(MyComponent); // for app
// In test: <MyComponent t={key => key} />
```

**3. Full i18next setup in tests (no mocking):**

```js
import i18n from 'i18next';
import { initReactI18next, I18nextProvider } from 'react-i18next';
i18n.use(initReactI18next).init({
  lng: 'en', fallbackLng: 'en',
  resources: { en: { translationsNS: {} } },
});
// Wrap component: <I18nextProvider i18n={i18n}><MyComponent /></I18nextProvider>
```

Spy on `t` only when the test must prove a key was requested; prefer passing `t` as a prop or a real `I18nextProvider` so interpolation and plurals stay honest.

## React Options Reference

Options under `i18next.init({ react: { ... } })`:

| Option | Default | Description |
|--------|---------|-------------|
| `bindI18n` | `'languageChanged'` | Events triggering rerender |
| `bindI18nStore` | `''` | Store events triggering rerender |
| `transEmptyNodeValue` | `''` | Value for failed lookups in Trans |
| `transSupportBasicHtmlNodes` | `true` | Keep `<br/>` etc. in translation strings |
| `transKeepBasicHtmlNodesFor` | `['br','strong','i','p']` | Which HTML tags to keep |
| `transWrapTextNodes` | `''` | Wrap text nodes (e.g. `'span'` for Google Translate fix) |
| `useSuspense` | `true` | Enable/disable Suspense |
| `keyPrefix` | `undefined` | Auto-prefix for useTranslation's t function |

## Official docs (load on demand)

This skill does not ship a companion pack. Procedure sections above cover Trans, SSR, and testing. Beyond that:

- Trans component: https://react.i18next.com/latest/trans-component
- TypeScript: https://www.i18next.com/overview/typescript
- Core i18next: https://www.i18next.com/

## Pitfalls

1. **Import order matters**: `import './i18n'` must come before `import App` in your entry point. If it's after, components render before i18next is initialized.
2. **Trans vs t()**: Do not use `<Trans>` for plain text. Use `t()` instead. Trans is only for JSX trees with embedded React elements.
3. **Suspense without fallback**: By default, `useTranslation` triggers Suspense. If you don't wrap your app in `<Suspense>`, it will throw. Either add Suspense or pass `{ useSuspense: false }` and handle `ready` yourself.
4. **escapeValue**: Set `interpolation.escapeValue: false` — React already escapes. Leaving it `true` can double-escape content.
5. **debug in production**: Set `debug: false` in production builds. Leaving it `true` logs verbose output to the console.
6. **Namespace ordering**: When using multiple namespaces `useTranslation(['ns1', 'ns2'])`, the first namespace is the default. `t('key')` looks up in `ns1`, not across all namespaces.
7. **Plural suffixes are language-specific**: English uses `_one`/`_other`. Other languages have different rules (e.g., Arabic has six plural forms). Don't assume English plural patterns apply universally.
8. **Trans index numbering**: Children of Trans are numbered by position. Strings and interpolation objects get indices but are NOT wrapped in tags. Only elements get `<N>...</N>` tags. Miscounting is the most common Trans bug.
9. **keyPrefix version requirement**: `keyPrefix` requires react-i18next >= 11.12.0 and i18next >= 20.6.0. Check versions before using.
10. **TypeScript version requirement**: Type-safe translations require react-i18next >= 13.0.0 and i18next >= 23.0.1.
11. **withTranslation useSuspense**: To disable Suspense with the HOC, pass `useSuspense={false}` as a prop to the wrapped component, then check `props.tReady`.
12. **Multiple i18next instances**: If you have a component library that bundles its own i18next, use `I18nextProvider` to pass the correct instance. Without it, the library may use its own instance and translations won't match.
13. **Backend file path**: `i18next-http-backend` loads from `/public/locales/{lng}/{ns}.json` by default. If files are missing or path is wrong, translations silently fall back to the fallback language.

## Verification

1. **Verify installation succeeded:**

```bash
npm ls react-i18next i18next
```

Expected output: both packages listed with installed versions, no `UNMET` or `missing`.

2. **Verify i18n config loads without errors:**

```bash
node -e "require('./i18n'); console.log('i18n loaded OK')"
```

If using ESM, use a quick test script that imports `./i18n` and logs a success message.

3. **Verify a translation key resolves:**

```bash
node -e "const i18n = require('./i18n').default || require('./i18n'); console.log(i18n.t('welcome'))"
```

Expected: prints the translated string for the default language, not the raw key.

4. **Verify language switching works:**

```jsx
// In a component:
const { i18n } = useTranslation();
console.log(i18n.language); // 'en'
i18n.changeLanguage('tr');
console.log(i18n.language); // 'tr'
```

5. **Verify plural resolution:**

```js
i18n.t('item', { count: 1 });  // "1 item"
i18n.t('item', { count: 5 });  // "5 items"
```

6. **Verify debug mode for missing keys:**

Set `debug: true` in config, then use a non-existent key. The console should log a missing-key warning with the key name and namespace.

7. **Verify Suspense fallback renders:**

Wrap a component using `useTranslation` in `<Suspense fallback={<div>Loading translations...</div>}>`. On first load with a backend, the fallback should briefly appear before translations load.

## Related Skills

- **ui-ux-design**: For accessibility, layout, and interaction-state guidance when building multilingual UIs (RTL support, text expansion, responsive layout with translated content).
- **next.js**: For Next.js-specific i18n routing and SSR patterns.
- **typescript**: For type-safe translation key setup.
