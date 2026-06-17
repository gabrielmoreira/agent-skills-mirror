# React Hooks (`@dynatrace-sdk/react-hooks`)

> Env: ⚠️ **BROWSER-ONLY — do NOT use in server-side JS runtime functions.**
> Status: current

React hooks for building app frontends. They require a React render context and **cannot run in the server-side JS runtime**. For equivalent server-side work, call the underlying `client-*` SDKs directly — e.g. use [`client-query`](../query/README.md) instead of `useDql`, [`client-document`](../document/README.md) instead of `useDocument`.

## Key exports (frontend use only)

`useDql`, `useDocument`, `useAppState`, `useAnalyzer`, `useAppFunction`, `useGrailFields`, `useUser` / `useUsers`, plus providers (`DqlQueryParamsProvider`, `UseUsersProvider`).

Full detail: [hooks.md](hooks.md) (all `use*` hooks, providers, functions, constants) · [types.md](types.md) (hook option/result types).

## Notes

- `useDql` caches results 60 s by default and retries on HTTP 429.
- Several v1 hooks are deprecated in favor of V2 variants.

Canonical reference: https://developer.dynatrace.com/develop/sdks/react-hooks/
