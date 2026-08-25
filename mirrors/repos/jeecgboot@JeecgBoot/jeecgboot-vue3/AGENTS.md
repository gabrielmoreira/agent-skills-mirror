# AGENTS.md

This file provides repository guidance for Codex when working in this project.

## Communication

- Always answer in Simplified Chinese first, unless the user explicitly requests another language.

## Project Overview

JeecgBoot Vue3 (v3.8.3) is an enterprise low-code admin platform frontend. It is built on Vue 3, TypeScript, Vite, Ant Design Vue 4, and Pinia. It was originally forked from Vben Admin and customized with JeecgBoot-specific components such as online forms, code generation, workflow, and related low-code modules.

This workspace uses SVN for version control. Do not assume Git is available in this directory.

Backend: Spring Boot (JeecgBoot), expected at `http://127.0.0.1:8080/jeecg-boot` during development.

## Related Projects

| Project | Path |
| --- | --- |
| Frontend (Vue3, this repo) | `E:\workspace-cc-jeecg\jeecgboot-vue3-2026` |
| Backend (Spring Boot 3) | `E:\workspace-cc-jeecg\jeecg-boot-framework-2026` |

## Commands

```bash
pnpm install
pnpm dev
pnpm build
pnpm batch:prettier
```

- `pnpm dev` starts the dev server on port 3100.
- `pnpm build` creates the production build in `dist/`.
- `pnpm batch:prettier` formats all matching files under `src/`; run it only when broad formatting is intended.
- No regular test script is configured in `package.json`; a Jest config exists, but there is no `test` script.

## Path Aliases

- `/@/` or `@/` maps to `src/`.
- `/#/` or `#/` maps to `types/`.
- Prefer the `/@/` prefix with the leading slash, which is the convention used throughout this codebase.

## Source Structure

| Directory | Purpose |
| --- | --- |
| `src/api/` | HTTP request functions organized by domain, such as `sys/` and `common/`. |
| `src/components/` | Reusable components, including generic components and JeecgBoot-specific components under `jeecg/`. |
| `src/hooks/` | Composition API hooks, including `web/`, `setting/`, and `system/`. |
| `src/layouts/` | App layouts, including `default/`, `iframe/`, and `page/`. |
| `src/router/` | Vue Router setup with dynamic route registration based on backend permissions. |
| `src/store/` | Pinia stores for app, user, permission, tabs, locale, and lock state. |
| `src/settings/` | Global project, component, and design settings. |
| `src/utils/` | HTTP client, auth/token management, encryption, dict helpers, and shared utilities. |
| `src/views/` | Feature pages, including `system/`, `dashboard/`, `monitor/`, and `super/`. |
| `src/locales/` | i18n files such as `zh_CN` and `en`. |
| `src/enums/` | TypeScript enums for constants. |
| `src/directives/` | Custom directives such as `v-auth`, `v-loading`, `v-click-outside`, and `v-ripple`. |

## View Conventions

Each feature module in `src/views/` typically includes:

- `index.vue` for the main list page.
- `*.data.ts` for table column definitions and form schemas.
- `*.api.ts` for API endpoint calls.
- `*Modal.vue` or `*Drawer.vue` for detail and edit components.

## Component Patterns

Use `BasicTable` and `BasicForm` for list pages:

```ts
import { BasicTable, useTable } from '/@/components/Table';

const [registerTable] = useTable({ api, columns, formConfig: { schemas } });
```

Use `useModal` and `useDrawer` for detail panels:

```ts
const [registerModal, { openModal }] = useModal();
openModal(true, { isUpdate: true, record });
```

Use `useListPage` from `src/hooks/system/` for standard CRUD pages that combine table, form, modal, and drawer behavior.

Form schemas use `FormSchema[]` with `component` specifying Ant Design Vue or custom components such as `Input`, `Select`, `JDictSelectTag`, and `JSearchSelect`.

## HTTP Client

`defHttp` in `src/utils/http/axios/` wraps Axios with:

- Token injection through interceptors.
- MD5 request signing for API security.
- Multi-tenant header support.
- Standard response unwrapping through the `result` field.

API functions usually follow this pattern:

```ts
enum Api {
  List = '/sys/user/list',
}

export const list = (params) => defHttp.get({ url: Api.List, params });
```

## Authentication And Permissions

- Tokens are stored in localStorage through auth utilities.
- `src/router/guard/permissionGuard.ts` fetches user info and dynamic menus from the backend.
- Permission mode is `BACK`, meaning routes and button permissions are backend-driven.
- Button-level auth uses the `v-auth="'system:user:add'"` directive or the `usePermission()` hook.

## Component Settings

Table pagination uses `pageNo` and `pageSize` params and expects `records` and `total` in the response. This is configured in `src/settings/componentSetting.ts`.

## Environment Variables

- `.env` contains base config such as port, app title, SSO, and qiankun toggles.
- `.env.development` contains dev proxy, mock toggle, and backend URL.
- `.env.production` contains production API URL and gzip config.
- Key variables include `VITE_GLOB_DOMAIN_URL`, `VITE_GLOB_API_URL`, and `VITE_PROXY`.

## Build System

`vite.config.ts` delegates plugin setup to `build/vite/plugin/`. Plugins include HTML template handling, mock data, gzip compression, SVG sprites, dynamic theme, qiankun micro-frontend, and PWA. Build scripts under `build/script/` handle post-build tasks.

## Online Forms

Online forms are a JeecgBoot low-code core feature. They generate CRUD pages from configuration. The full schema reference is in `src/views/super/online/cgform/online-form-schema.md` and covers table metadata, field configuration, control types, validation rules, and JavaScript enhancements.

## Code Style

- Prettier uses 150 character line width, single quotes, trailing commas for ES5, semicolons, and 2-space indentation.
- ESLint uses `vue/vue3-recommended`, `@typescript-eslint/recommended`, and Prettier with Prettier rules disabled.
- Unused variables prefixed with `_` are allowed.
- Prefer `<script setup>` for new Vue components.
- Use Less for styling.

## Working Exclusions

Treat the existing `.claudeignore` as the source for routine Codex work exclusions.

Avoid broad searches, reads, or edits in these paths unless the task explicitly targets them or verification requires them:

- `.git/`, `.svn/`, `.idea/`, `.vscode/`
- `node_modules/`, `dist/`, `target/`, `docker/data/`
- `backup/`, `.history/`, `.cursor/`
- `doc/`, `docs/`
- IDE metadata such as `*.iml`, `*.iws`, `*.ipr`, `.classpath`, `.project`, `.settings/`, and `out/`
- OS files such as `.DS_Store`, `Thumbs.db`, and `desktop.ini`
- Logs and generated artifacts such as `*.log`, `logs/`, `*.class`, `*.zip`, `*.qqy`, `代码修改.log`, and `代码修改日志`

The `.claudeignore` file lists `build/`, but this frontend uses `build/` for Vite plugins and build scripts. Avoid broad scans there, but allow targeted reads and edits when working on build tooling.
