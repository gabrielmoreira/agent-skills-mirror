# Geistdocs agent instructions

This project uses the packaged Geistdocs architecture. The `@vercel/geistdocs` package owns shared runtime behavior; this app owns local content, configuration, adapters, and site-specific routes.

Use these instructions when an AI coding agent edits this project.

## Architecture

- Runtime features come from `@vercel/geistdocs`, including the docs page renderer, layout helpers, MDX components, search, Ask AI, markdown routes, proxy helpers, and source helpers.
- Geistdocs exposes shared UI primitives through documented `@vercel/geistdocs/components/*` paths. Keep template code package-backed instead of importing provider internals directly.
- `@vercel/geistdocs` owns the Ask AI client, server route behavior, and AI SDK v6 runtime dependencies. Do not fork package internals to fit an older app-level `ai` version.
- Local files are user-owned adapters. They should stay thin and call public package exports from `@vercel/geistdocs/*`.
- Do not copy package internals into the app to make a customization. Prefer configuring an adapter file or upgrading `@vercel/geistdocs`.
- Do not deep import from `@vercel/geistdocs/dist` or edit files in `node_modules/@vercel/geistdocs`.
- Do not edit generated directories such as `.source/`, `.next/`, `node_modules/`, or build output.

## Package Docs For Agents

- When package API behavior is unclear, read the installed package docs in `node_modules/@vercel/geistdocs/docs` before guessing.
- Start with `node_modules/@vercel/geistdocs/docs/agents.md` and `node_modules/@vercel/geistdocs/docs/sitemap.md` to identify the relevant focused page.
- Use `node_modules/@vercel/geistdocs/docs/pages/*.md` for task-specific guidance and `node_modules/@vercel/geistdocs/docs/llms.txt` only when you need broad package context.
- These package docs are read-only generated artifacts. Do not edit files under `node_modules/@vercel/geistdocs`; change local adapter files or update the package instead.

## Common edit targets

| Task | Edit |
| --- | --- |
| Configure site title, logo, nav, GitHub links, AI prompt, retrieval, suggestions, translations, `basePath`, or `siteId` | `geistdocs.tsx` |
| Add or update documentation pages | `content/docs/**/*.mdx` |
| Control sidebar order, groups, and folder labels | `content/docs/meta.json` |
| Give a page a shorter navigation label | Set `navTitle` in the page's frontmatter |
| Override MDX components | `components/geistdocs/mdx-components.tsx` |
| Wrap the site provider, analytics, or global client behavior | `components/geistdocs/provider.tsx` |
| Customize the docs layout shell | `components/geistdocs/docs-layout.tsx` |
| Configure the Fumadocs source adapter or versioned docs | `lib/geistdocs/source.ts` |
| Configure Fumadocs collections and source-safe MDX processing | `source.config.ts` |
| Configure the docs page renderer | `app/[lang]/docs/[[...slug]]/page.tsx` |
| Configure AI-readable markdown output and recovery | `app/[lang]/desktop/llms.txt/route.ts`, `app/[lang]/desktop/llms.mdx/[[...slug]]/route.ts`, `app/[lang]/desktop/sitemap.md/route.ts` |
| Configure chat or search APIs | `app/api/chat/route.ts`, `app/api/search/route.ts`, `app/api/search/export/route.ts` |
| Add request handling before or after Geistdocs routing | `proxy.ts` |
| Edit the marketing home page | `app/[lang]/(home)/**` |
| Edit shared styles | `app/global.css`, `app/styles/geistdocs.css` |

## Content guidelines

- Put docs in `content/docs` unless the project has added another source in `lib/geistdocs/source.ts`.
- Add each new page to `content/docs/meta.json` so it appears in the sidebar.
- Use MDX frontmatter with at least `title` and `description` for documentation pages. Set `navTitle` only when the navigation label should differ from the page heading.
- Keep slugs stable unless the task explicitly includes redirects or link updates.
- When adding translated content, follow the existing locale suffix pattern, such as `page.cn.mdx`.
- Use `CopyPrompt` when a page should give readers a prompt they can copy into a coding agent.

## Routing and proxy guidelines

- Keep App Router route files as thin adapters around package helpers such as `createDocsPage`, `createChatRoute`, `createLlmsRoute`, and `createProxy`.
- Keep `createGeistdocs` from `@vercel/geistdocs/next` as the `next.config.ts` wrapper. It composes Fumadocs MDX and generates the app-route manifest used by `createProxy`; do not replace it with `createMDX` directly.
- Keep `cacheComponents: true` and `partialPrefetching: true` in `next.config.ts`. Do not export `dynamic`, `revalidate`, or `fetchCache` from App Router pages or route handlers.
- Read `[lang]` from `next/root-params` in Server Components. Keep route context `params` in Route Handlers and Server Actions.
- Use `prefetch={true}` for app-owned links to fully static documentation pages so navigation does not stop at the generic route shell.
- Keep `export const config` in `proxy.ts` as a static object. Next.js must parse proxy matchers at build time.
- Use proxy matcher exclusions that only match `/api` and `/api/...`, such as `api(?:/|$)`. Do not exclude broad prefixes like `api`, because that also excludes routes such as `/api-reference`.
- Preserve markdown negotiation unless the task explicitly changes AI-readable output. Geistdocs serves `/desktop/llms.txt` and per-page Markdown for `.md`, `.mdx`, and `Accept: text/markdown` requests.
- Restart `next dev` after adding, deleting, or renaming an App Router page or route so `createGeistdocs` regenerates its route manifest.
- When adding custom proxy behavior, prefer `before`, `after`, `transformRewrite`, and `markdownRoutes` options on `createProxy` instead of replacing the proxy. Use `transformRewrite` for internal route segments that must apply after locale and Markdown resolution.
- Use explicit `markdownRoutes` for root-mounted docs or any site where homepage/app routes coexist with docs routes.
- Keep source URLs, navigation links, `getPageUrl`, and `markdownRoutes` app-local when `config.basePath` is set. Geistdocs derives public page-action and Markdown URLs separately.
- Use `createDocsPage({ canViewPage })` and its returned `getPageTree(params)` for request-specific page access. Use one synchronous public filter as `canViewPage` for per-page Markdown and as `filterPage` for llms.txt, sitemap, search, search export, and chat routes.
- Include `"/"` explicitly in the static proxy matcher when a Next.js base-path application serves documentation at its app root.

## Ask AI and Vertex proxy guidelines

- Leave `GEISTDOCS_CHAT_PROXY_URL` unset and `ai.eveAgent` unconfigured to use the default AI Gateway path. In that mode, `app/api/chat/route.ts` calls `createChatRoute` without a `proxy` option and uses the local docs search tool during the AI SDK `streamText` loop.
- Set `ai.retrieval: "mixedbread"` with a unique `siteId` to use Mixedbread semantic retrieval for Ask AI. The visible search dialog continues to use local Orama search.
- Provision a Mixedbread Store from the root of this consumer site's repository, where Vercel CLI is linked to this site's Vercel project. Never run `vercel integration add mixedbread` from the Geistdocs package repository or another consumer repository.
- Keep `MXBAI_API_KEY` and `MXBAI_STORE_ID` in environment variables. Never put them in `geistdocs.tsx`, because config is available to client components.
- Keep `app/api/search/export/route.ts` and the `next build && geistdocs search sync` build script when Mixedbread retrieval is enabled. Production builds incrementally sync chat-visible Markdown; local and preview builds skip remote sync unless `--allow-non-production` is passed.
- Mixedbread failures fall back to local Orama retrieval. Keep the local source definitions and `excludeFrom: [chat]` visibility behavior intact.
- Set `ai.eveAgent: { url }` in `geistdocs.tsx` to answer Ask AI with a hosted eve framework agent instead. The URL flows through the config object; the route file needs no changes. Set `prewarm: true` for eve 0.59+ responders when the site should prepare an empty durable session as the chat client loads. Requests authenticate with a per-request Vercel OIDC bearer token by default; pass server-only headers through the `eveAgent` option on `createChatRoute` for custom auth. Never put auth material in `geistdocs.tsx`. Configuring both `proxy` and an eve agent throws at route creation.
- Set the server-only `GEISTDOCS_CHAT_SECRET` (at least 32 bytes, generate with `openssl rand -base64 32`) for eve agent mode. It signs the httpOnly `geistdocs_eve_session` cookie that binds a browser to its eve session (the cookie is `SameSite=Strict`, so keep the chat route on the same site as the docs pages); without it every turn starts a new eve session and prewarm requests are refused. Never prefix it with `NEXT_PUBLIC_` or put it in `geistdocs.tsx`.
- `createChatRoute` caps request size (1,000,000-byte body, 200 messages, 200,000-character `pageContext.content` by default; override with the `limits` option). It does not rate limit, so wrap `POST` with the site's own rate limiting.
- Geistdocs Ask AI targets AI SDK v6: `ai` v6 and `@ai-sdk/react` v3. Keep those dependencies on the generated package versions unless a `@vercel/geistdocs` release changes them.
- If the app uses `ai` or `@ai-sdk/react` for product code outside Geistdocs, migrate that app code separately or let the package manager install separate versions. Do not downgrade Geistdocs Ask AI to match unrelated app code.
- Set `GEISTDOCS_CHAT_PROXY_URL` only when Ask AI should route through the central Vertex-backed proxy. The value must include the `/vertex` route, such as `https://<geistdocs-platform-deployment>/vertex`.
- Do not add Vertex credentials to a Geistdocs site. The central platform proxy forwards the Vercel OIDC token in `x-vercel-trusted-oidc-idp-token`; the Vertex deployment should trust the platform Vercel project through Deployment Protection Trusted Sources.
- Set the server-only `GEISTDOCS_CHAT_PROXY_TOKEN` when using the Geistdocs platform `/vertex` proxy. Its value must match the platform deployment's `GEISTDOCS_VERTEX_PROXY_TOKEN`, which must contain at least 32 bytes. Never expose either token with a `NEXT_PUBLIC_` prefix.
- Keep `app/api/chat/route.ts` as a thin adapter around `createChatRoute`. Prefer configuring `GEISTDOCS_CHAT_PROXY_URL` and `GEISTDOCS_CHAT_PROXY_TOKEN` over forking the package chat route.
- If custom chat client code uses `DefaultChatTransport.prepareSendMessagesRequest`, preserve `messages` in the returned `body` when adding fields such as `currentRoute`. Returning a custom `body` replaces the AI SDK default request body.

## Migration guidelines

- When migrating from Fumadocs or a custom Geist docs site, inventory `source.config.ts`, route files, `middleware.ts` or `proxy.ts`, `public/llms.txt`, OG routes, Tailwind CSS setup, and required environment variables before editing.
- Use `@vercel/geistdocs` for public repositories. Use `@vercel/geistdocs-private` only in internal environments with access to the restricted `@vercel/geistcn` and `@vercel/geistcn-assets` packages.
- Keep private npm credentials out of source files; configure them through local npm authentication, Vercel project settings, and GitHub Actions secrets.
- Inventory direct app usage of `ai` and `@ai-sdk/react`. Package-owned Ask AI uses AI SDK v6; migrate local AI SDK code separately from Geistdocs route adapters.
- Import source-config helpers from `@vercel/geistdocs/source-config` in `source.config.ts`. Do not import runtime component entry points from source config.
- Move existing `middleware.ts` behavior into `createProxy({ before })` or `createProxy({ after })` hooks.
- Delete `public/llms.txt` when using `createLlmsRoute`; otherwise the static file can mask the App Router route.
- Set `openGraph.images` in `createDocsPage` only when the app includes the Geistdocs OG route, or override metadata to avoid broken `/og/...` URLs.
- Keep the generated package-specific Next.js configuration. The private template includes the additional Geistcn transpilation settings it requires.
- Apply `geistFontClasses`, `tailwind`, and `tailwind-preflight` to the root `<html>` element.
- Import the selected Geistdocs package's stylesheet and keep its generated Tailwind source configuration.
- Add local fallbacks for production-only environment variables so migration builds do not require production secrets.

## Package updates

- Use `pnpm exec geistdocs update` to update package-based Geistdocs projects.
- `geistdocs update` updates the `@vercel/geistdocs` dependency. It does not overwrite local adapter files.
- On a canary project, `geistdocs update` follows the current `canary` dist-tag. Check and test that version before updating an active migration.
- Review dependency changes and run the verification commands before committing an update.

## Commands

- Start development: `pnpm dev`
- Build for production: `pnpm build`
- Start the built app: `pnpm start`
- Regenerate Fumadocs output after dependency installation: `pnpm postinstall`
- Update Geistdocs: `pnpm exec geistdocs update`
- Run translations if configured: `pnpm translate`
- Sync the Mixedbread Store outside production when explicitly needed: `pnpm exec geistdocs search sync --allow-non-production`

## Verification

- Run `pnpm build` after changing routes, config, source setup, MDX components, or package versions.
- Run `pnpm dev` and open the changed pages when visual layout, navigation, or MDX rendering changes.
- Check `/desktop` and AI-readable routes such as `/desktop/llms.txt` or a page-level `.md` URL when changing content routing or proxy behavior.
- Confirm `/api/search/export` is statically generated after changing Mixedbread retrieval or source configuration.
- Confirm no secrets were added to source files. Use `.env.local` for local values and keep it out of Git.

<!-- BEGIN:nextjs-agent-rules -->

# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->
