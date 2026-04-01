# OpenClaw.Anywhere

A self-hostable cloud hosting management platform built as a TypeScript monorepo.

## Project Structure

```
openclaw.anywhere/
├── apps/
│   ├── api/              # Hono.js backend API (Node.js)
│   └── web/              # React + Vite frontend
├── packages/
│   ├── shared/           # @openclaw/shared - HTTP client, constants, validation
│   └── i18n/             # @openclaw/i18n - Internationalization (EN, FR, ES, DE)
├── scripts/              # Utility scripts
└── turbo.json            # Turborepo build orchestration
```

## Tech Stack

### Backend (apps/api)

- **Framework**: Hono.js
- **Database**: Neon (serverless PostgreSQL) with Drizzle ORM
- **Authentication**: Firebase Admin SDK + OTP (email-based) + OAuth (Google, GitHub)
- **Email**: Resend + React Email
- **Payments**: Polar SDK
- **Cloud Providers**: Hetzner Cloud, DigitalOcean, Vultr
- **DNS**: Cloudflare
- **SSH/Terminal**: SSH2 + WebSocket (ws) for remote terminal access
- **Text-to-Speech**: Piper TTS engine
- **Runtime**: Node.js 20+ with tsx

### Frontend (apps/web)

- **Framework**: React 18 with Vite
- **Routing**: React Router DOM
- **State**: Zustand (with persist middleware)
- **Data Fetching**: TanStack React Query
- **UI**: shadcn/ui + Radix UI + Tailwind CSS
- **Icons**: Phosphor Icons
- **Animation**: Framer Motion
- **Auth**: Firebase
- **Graph Visualization**: React Flow (playground canvas)
- **Terminal**: xterm.js (in-browser terminal emulation)
- **Code Editing**: CodeMirror (file editor)
- **Blog**: MDX for content authoring

### Shared Packages

- **@openclaw/shared**: HTTP RequestClient, cloud provider/status constants, input validation, user roles, API envelope types
- **@openclaw/i18n**: Internationalization framework with `t()` function, parameter interpolation, 4 languages

## Code Conventions

### Import Rules

**CRITICAL: Always use `@/` path aliases in both the web app and the API app. Never use `../` relative imports under any circumstance. This applies to ALL `.ts` and `.tsx` files — including files in `scripts/`, entry points, and any other directory outside `src/`.**

```typescript
// CORRECT - Use @ path aliases
import { Button } from '@/components/ui/button'
import { api } from '@/lib/api'
import { db } from '@/db'
import { hetzner } from '@/services/hetzner'

// CORRECT - Script files also use @/ aliases
// apps/api/scripts/example.ts
import { hetzner } from '@/services/hetzner'

// INCORRECT - Never use ../ relative imports
import { Button } from '../components/ui/button' // DO NOT USE
import { db } from '../../db' // DO NOT USE
import { hetzner } from '../src/services/hetzner' // DO NOT USE (even in scripts/)
```

**`./` imports are NEVER allowed.** All imports must use `@/` path aliases — including barrel exports, same-directory siblings, and subdirectory imports.

**For workspace packages, use the package name:**

```typescript
import { RequestClient } from '@openclaw/shared'
import { t } from '@openclaw/i18n'
```

### Phosphor Icons Import Rule

**CRITICAL: Always import Phosphor icons with the `Icon` suffix from `@phosphor-icons/react`. The non-suffixed names (e.g., `Check`, `Copy`, `Eye`) are deprecated. Every icon import must end with `Icon`.**

```typescript
// CORRECT - Always use the Icon suffix
import {
    CheckIcon,
    CopyIcon,
    EyeIcon,
    EyeSlashIcon
} from '@phosphor-icons/react'
import {
    CircleNotchIcon,
    WarningIcon,
    LightningIcon
} from '@phosphor-icons/react'
import {
    GithubLogoIcon,
    DiscordLogoIcon,
    SlackLogoIcon
} from '@phosphor-icons/react'

// INCORRECT - Non-suffixed names are deprecated
import { Check, Copy, Eye, EyeSlash } from '@phosphor-icons/react' // DO NOT USE
import { CircleNotch, Warning, Lightning } from '@phosphor-icons/react' // DO NOT USE
import { GithubLogo, DiscordLogo, SlackLogo } from '@phosphor-icons/react' // DO NOT USE
```

**In JSX, use the suffixed names:**

```tsx
// CORRECT
<CheckIcon size={16} />
<CircleNotchIcon className='animate-spin' />

// INCORRECT
<Check size={16} />  // DO NOT USE
<CircleNotch className='animate-spin' />  // DO NOT USE
```

### One Export Per File Rule

**CRITICAL: Every `.ts` and `.tsx` file must export exactly ONE function, component, constant, or class via `export default`. No file should have multiple exports.**

**When a module needs multiple exports, convert it to a folder:**

```
lib/example.ts (BEFORE - multiple exports)
↓
lib/example/           (AFTER - one per file)
  doThing.ts           → export default doThing
  doOtherThing.ts      → export default doOtherThing
  index.ts             → barrel re-exports
```

**Barrel `index.ts` syntax:**

```typescript
import doThing from '@/lib/example/doThing'
import doOtherThing from '@/lib/example/doOtherThing'

export { doThing, doOtherThing }
```

**NEVER use `export { default as X } from` syntax in barrel files.** Always import the default first, then re-export by name.

**Private/internal modules** (shared state, config) within a folder don't need to be in the barrel.

**Exempt from this rule:**

- `ts/Types.ts` and `ts/Interfaces.ts` — type centralization files
- `ts/index.ts` — type barrel
- Barrel `index.ts` files — they are the aggregation mechanism
- shadcn/ui components in `components/ui/` — third-party generated

**Reference pattern:** See `apps/api/src/controllers/claws/` for the canonical example.

### Types and Interfaces Rules

**CRITICAL: All types and interfaces must be centralized in `@/ts/`. This applies to BOTH `apps/web` AND `apps/api`. Never define types, interfaces, or inline object types anywhere else — not in components, hooks, services, controllers, lib files, or scripts.**

**This includes:**

- `interface` definitions
- `type` alias definitions
- Inline object types in function parameters (e.g., `(data: { name: string })`)
- Inline object types in return types (e.g., `Promise<{ id: string }>`)
- Inline union types used as standalone types
- Props types for React components

**Centralized Type Files:**

| App | Interfaces                      | Types                      | Barrel                     |
| --- | ------------------------------- | -------------------------- | -------------------------- |
| Web | `apps/web/src/ts/Interfaces.ts` | `apps/web/src/ts/Types.ts` | `apps/web/src/ts/index.ts` |
| API | `apps/api/src/ts/Interfaces.ts` | `apps/api/src/ts/Types.ts` | `apps/api/src/ts/index.ts` |

**Type Imports Must Be at the Top of Files, Separated by an Empty Line:**

```typescript
// CORRECT - Type imports first, then empty line, then regular imports
import type { Claw, Plan, SSHKey, StatusConfig } from '@/ts/Interfaces'
import type { ViewMode, ToastType } from '@/ts/Types'

import { useState } from 'react'
import { api } from '@/lib/api'

// INCORRECT - Missing empty line between type and regular imports
import type { Claw } from '@/ts/Interfaces' // DO NOT USE
import { useState } from 'react' // (no blank line above)

// INCORRECT - Type imports after regular imports
import { useState } from 'react' // DO NOT USE
import type { Claw } from '@/ts/Interfaces' // (type import must be above)

// INCORRECT - Regular imports for types
import { Claw, Plan } from '@/ts/Interfaces' // DO NOT USE

// INCORRECT - Inline type definitions
interface MyComponentProps {
    // DO NOT USE - put in @/ts/Interfaces.ts
    title: string
}

// INCORRECT - Inline object types in functions
async function getUser(): Promise<{ id: string; name: string }> {} // DO NOT USE
function create(data: { email: string; name?: string }): void {} // DO NOT USE

// CORRECT - Use named interfaces from @/ts/Interfaces
async function getUser(): Promise<UserProfile> {} // USE THIS
function create(data: CreateUserParams): void {} // USE THIS
```

**File Organization:**

- `@/ts/Types.ts` - All type aliases (e.g., `type ViewMode = 'list' | 'grid'`)
- `@/ts/Interfaces.ts` - All interfaces (e.g., `interface Claw { ... }`)
- `@/ts/index.ts` - Barrel export for convenient imports

**Categories in web Interfaces.ts:**

- API / Data Models: `Claw`, `Plan`, `Location`, `SSHKey`, `Volume`, `UserProfile`, `UserStats`, `BillingOrder`, etc.
- Store Interfaces: `UIState`, `PreferencesState`, `ToastData`
- Auth Interfaces: `AuthContextType`, `VerifyOtpResponse`, `CachedProfile`, `ResolveCredentialConflictData`
- Component Props: `HeaderProps`, `EmptyStateProps`, `ClawCardProps`, `PlaygroundCanvasProps`, `PlaygroundDetailPanelProps`, etc.
- Hook Data Types: `CreateClawData`, `PurchaseClawData`, `CreateSSHKeyData`, `RenameClawData`, `UpdateClawSubdomainData`, etc.
- Playground Types: `PlaygroundClawNodeData`, `PlaygroundAgentNodeData`
- Agent/Chat Types: `ClawAgent`, `ChatMessage`, `ChatAttachment`, `ChatHistoryEntry`, `UseAgentChatParams`, `UseAgentChatReturn`
- File System Types: `ClawFileEntry`, `ClawFilesResponse`, `ReadClawFileResponse`, `UpdateClawFileData`
- Channel/Binding Types: `ChannelConfig`, `Binding`, `ClawChannelsResponse`, `ClawBindingsResponse`
- Skills/ClawHub Types: `BundledSkillInfo`, `ClawSkillsResponse`, `ClawHubSearchResult`, `ClawHubBrowseResponse`
- Version Types: `ClawVersionResponse`, `ClawVersionsResponse`
- Blog Types: `BlogPostFrontmatter`, `BlogPostMeta`, `Testimonial`, `Faq`, `CompareCompetitor`, `CompareFeature`

**Categories in api Interfaces.ts:**

- API Response: `ApiResponse<T>`
- Cloud Provider Interface: `CloudProvider`, `CreateServerResult`, `ServerStatus`, `ServerTypeInfo`, `LocationInfo`
- Hetzner Types: `HetznerServer`, `HetznerServerType`, `HetznerLocation`, `HetznerDatacenter`, `HetznerVolume`, `HetznerSSHKey`, etc.
- DigitalOcean Types: `DigitalOceanDroplet`, `DigitalOceanSize`, `DigitalOceanRegion`, `DigitalOceanSSHKey`, `DigitalOceanVolume`, etc.
- Vultr Types: `VultrInstance`, `VultrPlan`, `VultrRegion`, `VultrSSHKey`, `VultrVolume`, etc.
- Polar/Payment Types: `CheckoutSession`, `PolarSubscription`, `PolarOrder`, `PolarProduct`, `PolarCustomer`, webhook data types
- Claw Operation Types: `CreateClawBody`, `InitiateClawPurchase`, `ProvisionClawParams`
- Agent Types: `ClawAgent`, `ClawChannelsResponse`, `ClawSkillsResponse`, `ClawBindingsResponse`
- Auth Types: `SendOtpBody`, `VerifyOtpBody`, `ResolveCredentialConflictBody`
- ClawHub Types: `ClawHubSearchResult`, `ClawHubInstalledSkill`, `ClawHubBrowseResultPage`
- File Types: `ClawFileEntry`, `ReadClawFileBody`, `UpdateClawFileBody`
- Diagnostics Types: `DiagnosticsStatusResponse`, `DiagnosticsLogsResponse`
- WhatsApp Types: `WhatsAppPairResponse`, `WhatsAppPairStatusResponse`
- Cache Types: `CacheEntry<T>`, `SkillsCacheEntry`
- TTS Types: `PiperVoice`, `PiperSynthesisResult`, `GenerateSpeechBody`
- DNS Types: `CloudflareDNSRecord`
- Email Props: `OtpCodeEmailProps`

### React Component Function Pattern

**CRITICAL: All React functional components must use the `const ComponentName: FC = (): ReactNode => { ... }` pattern with a separate export at the end.**

**For components without props:**

```typescript
import type { FC, ReactNode } from 'react'

const MyComponent: FC = (): ReactNode => {
  return <div>Content</div>
}

export default MyComponent
// or for named exports: export { MyComponent }
```

**For components with props:**

```typescript
import type { FC, ReactNode } from 'react'
import type { MyComponentProps } from '@/ts/Interfaces'

const MyComponent: FC<MyComponentProps> = ({ title, description }): ReactNode => {
  return (
    <div>
      <h1>{title}</h1>
      <p>{description}</p>
    </div>
  )
}

export default MyComponent
```

**INCORRECT patterns - Never use:**

```typescript
// DO NOT USE - function declaration with inline export
export default function MyComponent() { ... }

// DO NOT USE - function declaration without FC type
function MyComponent() { ... }

// DO NOT USE - arrow function without FC type
const MyComponent = () => { ... }
```

**Key rules:**

1. Always import `FC` and `ReactNode` from 'react' using `import type`
2. Use `FC` for components without props, `FC<PropsType>` for components with props
3. Always include `: ReactNode` as the return type annotation
4. Use `export default ComponentName` at the end of the file for default exports
5. Use `export { ComponentName }` for named exports
6. Internal/helper components within a file should also follow this pattern

### File Organization

**API Controllers** (`apps/api/src/controllers/`):

- Group by resource (ai, auth, claws, plans, ssh-keys, users, webhooks)
- Each controller exports individual functions
- Use barrel exports in index.ts
- Claws controller has `helpers/` subdirectory for shared utilities

**API Routes** (`apps/api/src/routes/`):

- One file per resource
- Import controllers and wire to Hono routes
- Combine in routes/index.ts

**Web Pages** (`apps/web/src/pages/`):

- One component per page
- Use PageTitle for document title management
- Include PageBackground for consistent styling
- Public pages: Landing, Login, Blog, BlogPost, Compare, Terms, Privacy, Changelog, NotFound
- Protected pages: Dashboard (with Chat and Playground tabs), Account, SSHKeys, Billing

**Web Components** (`apps/web/src/components/`):

- `ui/` for shadcn/ui primitives
- `dashboard/` for dashboard-specific components (CreateClawModal, ClawCard dropdowns/dialogs, diagnostics, logs, terminal, config, file explorer)
- `chat/` for chat interface (ChatView, ChatSidebar with tree/list views, ChatSidebarItem, ChatEmptyState)
- `agent-chat/` for agent communication (AgentChat, ChatBubble, ChatInput, ChatMarkdown, VoiceOrb, VoiceModeOverlay, ChatSpeechButton, ChatTypingIndicator)
- `playground/` for graph visualization (PlaygroundCanvas, ClawNode, AgentNode, DetailPanel, Toolbar, ChannelsContent, VariablesContent, BindingsContent, SkillsContent, ClawHubContent, VersionsContent)
- Root level for shared components (Header, Footer, Logo, EmptyState, Toast, ProtectedRoute, etc.)
- Keep components focused and composable

### Database

**Schema Location**: `apps/api/src/db/schema.ts`

**Tables**:

- `users` - Firebase authenticated users (with authMethods array, polarCustomerId, role)
- `claws` - Cloud server instances (multi-provider: Hetzner, DigitalOcean, Vultr) with gateway tokens, Polar subscription tracking, deletion scheduling
- `pendingClaws` - Claws awaiting payment confirmation (with expiry)
- `sshKeys` - SSH key management (with per-provider key IDs: Hetzner, DigitalOcean, Vultr)
- `volumes` - Persistent storage volumes
- `clawExports` - Exported claw configurations
- `otpCodes` - OTP authentication codes (hashed, with attempt tracking)
- `rateLimits` - Rate limiting for auth endpoints

**Migrations**: Use Drizzle Kit

```bash
pnpm --filter api db:generate  # Generate migration
pnpm --filter api db:migrate   # Run migrations
```

### API Structure

**Authentication**: Bearer token middleware validates Firebase tokens. Auto-creates/updates user record on first auth. Admin-only routes protected by `adminOnly` middleware.

**Unauthenticated endpoints** (no token required):

- `GET /` - Health check
- `GET /clawhub/skills` - Public ClawHub skill browsing

**Auth Routes** (`/auth`):

- `POST /send-otp` - Send OTP code via email (rate-limited)
- `POST /verify-otp` - Verify OTP and get Firebase token
- `POST /resolve-credential-conflict` - Handle auth method conflicts

**Plans Routes** (`/plans`) - No auth required:

- `GET /` - Available plans by provider
- `GET /locations` - Deployment locations
- `GET /volume-pricing` - Storage pricing
- `GET /availability` - Plan availability by location

**AI Routes** (`/ai`):

- `POST /tts` - Text-to-speech generation (Piper)
- `GET /voices` - Available TTS voices

**Claws Routes** (`/claws`):

- `GET /` - List user's claws
- `GET /admin` - List all claws (admin-only)
- `GET /:id` - Get single claw
- `POST /` - Create free claw
- `POST /purchase` - Initiate paid claw purchase
- `DELETE /pending/:id` - Cancel pending purchase
- `PATCH /:id` - Rename claw
- `DELETE /:id` - Soft delete (schedules deletion)
- `POST /:id/sync` - Sync status with cloud provider
- `POST /:id/start` - Start server
- `POST /:id/stop` - Stop server
- `POST /:id/restart` - Restart server
- `POST /:id/cancel-deletion` - Cancel scheduled deletion
- `POST /:id/hard-delete` - Permanent delete (admin-only)
- `POST /:id/diagnostics/status` - Service diagnostics
- `POST /:id/diagnostics/logs` - Retrieve logs
- `POST /:id/diagnostics/repair` - Attempt repair (admin-only)
- `POST /:id/reinstall` - Reinstall OpenClaw (admin-only)
- `GET /:id/export` - Export claw configuration
- `POST /:id/agents` - List agents
- `POST /:id/agents/create` - Create agent
- `POST /:id/agents/delete` - Delete agent
- `POST /:id/agent-config` - Get agent config
- `PUT /:id/agent-config` - Update agent config
- `GET /:id/env` - Get environment variables
- `PUT /:id/env` - Update environment variables
- `POST /:id/channels` - Get channel configs
- `PUT /:id/channels` - Update channel configs
- `POST /:id/channels/whatsapp/pair` - Initiate WhatsApp pairing
- `POST /:id/channels/whatsapp/pair-status` - Check pairing status
- `POST /:id/bindings` - Get agent-channel bindings
- `PUT /:id/bindings` - Update bindings
- `POST /:id/skills` - Get bundled skills
- `PUT /:id/skills` - Update bundled skills
- `POST /:id/agents/:agentId/skills` - Get agent skills
- `PUT /:id/agents/:agentId/skills` - Update agent skills
- `POST /:id/files` - List files
- `POST /:id/files/read` - Read file content
- `PUT /:id/files` - Update file content
- `POST /:id/version` - Get current version
- `POST /:id/versions` - List available versions
- `POST /:id/install-version` - Install version (admin-only)
- `POST /:id/credentials` - Get credentials
- `GET /:id/clawhub/skills` - Browse ClawHub skills
- `POST /:id/clawhub/installed` - Get installed ClawHub skills
- `POST /:id/clawhub/install` - Install ClawHub skill
- `POST /:id/clawhub/remove` - Remove ClawHub skill
- `POST /:id/clawhub/update` - Update ClawHub skill
- `POST /:id/clawhub/updates` - Check for skill updates
- WebSocket: `/:id/terminal` - Real-time terminal access

**SSH Keys Routes** (`/ssh-keys`):

- `GET /` - List SSH keys
- `POST /` - Create SSH key
- `DELETE /:id` - Delete SSH key

**Users Routes** (`/users`):

- `GET /me` - Get profile
- `PUT /me` - Update profile
- `GET /me/stats` - User statistics
- `GET /me/billing` - Billing history
- `GET /me/billing/:orderId/invoice` - Download invoice
- `POST /me/billing/portal` - Polar customer portal link
- `POST /me/auth/:method` - Connect auth method (Google, GitHub)
- `DELETE /me/auth/:method` - Disconnect auth method

**Webhooks Routes** (`/webhooks`):

- `POST /polar` - Polar payment webhook (handles checkout, subscription lifecycle)

### Cloud Provider Abstraction

All three providers (Hetzner, DigitalOcean, Vultr) implement the `CloudProvider` interface with a unified API:

- `createServer`, `getServer`, `getServers`, `startServer`, `stopServer`, `restartServer`, `deleteServer`
- `createSSHKey`, `deleteSSHKey`
- `getServerTypes`, `getLocations`, `getDatacenters`
- `createVolume`, `attachVolume`, `detachVolume`, `deleteVolume`, `getVolume`

Use `getProvider(providerType)` from `@/services/provider` to resolve the correct service. The provider resolver includes in-memory caching with TTL (5 min for server types/locations/pricing, 10 sec for individual servers).

### External Services Setup

- **Firebase**: Enable Authentication with Email/Password, Google, and GitHub sign-in methods. Generate a service account key for the Admin SDK
- **Cloudflare**: API token needs DNS edit permissions for the zone. Creates A records for each claw subdomain (60s TTL)
- **Resend**: Verify your sending domain. `FROM_EMAIL` defaults to `OpenClaw <noreply@openclaw.com>`
- **Polar**: Create an organization, generate an access token, and configure a webhook pointing to `POST /api/webhooks/polar` with the secret
- **Piper TTS** (optional): Install the Piper binary and download voice models. Set `PIPER_BINARY` and `PIPER_MODELS_DIR` env vars

### State Management (Web)

**Zustand Stores** (`apps/web/src/lib/store/`):

- `useUIStore` - Toast notifications, create modal state, ProductHunt banner
- `usePreferencesStore` - User preferences (persisted): theme, language, admin mode, chat sidebar view mode

### Naming Conventions

- **Files**: kebab-case for utilities, PascalCase for React components
- **Functions**: camelCase
- **Types/Interfaces**: PascalCase
- **Constants**: SCREAMING_SNAKE_CASE for routes, camelCase otherwise
- **Database columns**: camelCase (Drizzle handles snake_case conversion)

## Development

### Prerequisites

- **Node.js**: >= 20
- **pnpm**: 10.29.3 (`corepack enable` or `npm install -g pnpm@10.29.3`)

### Initial Setup

```bash
pnpm install                           # Install all dependencies
pnpm --filter api db:migrate           # Run database migrations
```

To set up Polar payment products for a provider:

```bash
pnpm --filter api exec tsx scripts/create-polar-products.ts hetzner
pnpm --filter api exec tsx scripts/create-polar-products.ts digitalocean
pnpm --filter api exec tsx scripts/create-polar-products.ts vultr
```

Each command outputs `POLAR_PRODUCT_*` env vars to add to `apps/api/.env`.

### Commands

```bash
# Development
pnpm dev          # Run all apps
pnpm dev:web      # Run web only (port 1111)
pnpm dev:api      # Run API only (port 2222)
# Building
pnpm build        # Build all apps

# Database
pnpm --filter api db:generate
pnpm --filter api db:migrate
pnpm --filter api db:studio

# Linting & Formatting
pnpm check        # tsc + eslint for all apps
pnpm lint         # ESLint check
pnpm format       # Prettier + ESLint auto-fix
```

### Ports

- Web: 1111 (proxies /api to 2222)
- API: 2222

### Environment Variables

**API** (apps/api/.env):

```
PORT=2222
CLIENT=localhost:1111

DATABASE_URL=postgresql://...

# Firebase Admin SDK
FIREBASE_PROJECT_ID=...
FIREBASE_PRIVATE_KEY=...
FIREBASE_CLIENT_EMAIL=...

# Cloud Providers (at least one required)
HETZNER_API_TOKEN=...
DIGITALOCEAN_API_TOKEN=...
VULTR_API_TOKEN=...

# Cloudflare DNS
CLOUDFLARE_API_TOKEN=...
CLOUDFLARE_ZONE_ID=...

# Resend (email)
RESEND_API_KEY=...
FROM_EMAIL=OpenClaw <noreply@yourdomain.com>

# Polar (payments)
POLAR_ACCESS_TOKEN=...
POLAR_ORGANIZATION_ID=...
POLAR_WEBHOOK_SECRET=...
POLAR_PRODUCT_HETZNER_CX23=...
POLAR_PRODUCT_DIGITALOCEAN_S_1VCPU_1GB=...
POLAR_PRODUCT_VULTR_VC2_1C_1GB=...
# ... (one POLAR_PRODUCT_* per provider/plan, generated by create-polar-products script)

# Piper TTS (optional)
PIPER_BINARY=piper
PIPER_MODELS_DIR=./models
```

**Web** (apps/web/.env):

```
VITE_API_URL=/api
VITE_FIREBASE_API_KEY=...
VITE_FIREBASE_AUTH_DOMAIN=...
VITE_FIREBASE_PROJECT_ID=...
VITE_FIREBASE_STORAGE_BUCKET=...
VITE_FIREBASE_MESSAGING_SENDER_ID=...
VITE_FIREBASE_APP_ID=...
```

## Key Files

| Purpose              | Path                                            |
| -------------------- | ----------------------------------------------- |
| API Entry            | `apps/api/src/index.ts`                         |
| API App Setup        | `apps/api/src/app.ts`                           |
| DB Schema            | `apps/api/src/db/schema.ts`                     |
| API Routes           | `apps/api/src/routes/index.ts`                  |
| Admin Middleware     | `apps/api/src/middleware/adminOnly.ts`          |
| Provider Resolver    | `apps/api/src/services/provider/getProvider.ts` |
| Hetzner Service      | `apps/api/src/services/hetzner.ts`              |
| DigitalOcean Service | `apps/api/src/services/digitalocean.ts`         |
| Vultr Service        | `apps/api/src/services/vultr.ts`                |
| Cloudflare Service   | `apps/api/src/services/cloudflare.ts`           |
| SSH Service          | `apps/api/src/services/ssh.ts`                  |
| Terminal WebSocket   | `apps/api/src/services/terminalSocket.ts`       |
| Piper TTS Service    | `apps/api/src/services/piper.ts`                |
| Polar Services       | `apps/api/src/services/polar/`                  |
| ClawHub Service      | `apps/api/src/services/clawhub/`                |
| Claw Helpers         | `apps/api/src/controllers/claws/helpers/`       |
| Web Entry            | `apps/web/src/main.tsx`                         |
| Web Routes           | `apps/web/src/App.tsx`                          |
| Auth Context         | `apps/web/src/lib/auth/`                        |
| API Client (Web)     | `apps/web/src/lib/api.ts`                       |
| URL Paths            | `apps/web/src/lib/paths.ts`                     |
| Web Routes           | `apps/web/src/lib/routes.ts`                    |
| Stores               | `apps/web/src/lib/store/`                       |
| Gateway Client       | `apps/web/src/lib/gateway/`                     |
| Dashboard Tabs       | `apps/web/src/lib/dashboardTabs.ts`             |
| Claw Detail Tabs     | `apps/web/src/lib/clawDetailTabs.ts`            |
| Agent Detail Tabs    | `apps/web/src/lib/agentDetailTabs.ts`           |
| Blog Utilities       | `apps/web/src/lib/blog/`                        |
| Claw Utilities       | `apps/web/src/lib/claw-utils/`                  |
| Types (Web)          | `apps/web/src/ts/Types.ts`                      |
| Interfaces (Web)     | `apps/web/src/ts/Interfaces.ts`                 |
| Types (API)          | `apps/api/src/ts/Types.ts`                      |
| Interfaces (API)     | `apps/api/src/ts/Interfaces.ts`                 |
| Input Validation     | `packages/shared/src/inputValidation.ts`        |
| OpenClaw Version     | `packages/shared/src/openclawVersion.ts`        |

### Internationalization (i18n)

**CRITICAL: Never use hardcoded text strings in the UI. All user-facing text must use the translation function.**

**How it works:**

1. All translations are defined in `packages/i18n/src/langs/en.ts`
2. Import and use the `t()` function from `@openclaw/i18n`
3. Use dot notation for nested keys (e.g., `t('dashboard.status.running')`)
4. For dynamic text with parameters, use `t('key', { param: value })`

```typescript
// CORRECT - Use translation function
import { t } from '@openclaw/i18n'

<Button>{t('common.save')}</Button>
<p>{t('dashboard.noClawsDescription')}</p>
<span>{t('common.copiedWithLabel', { label: 'Password' })}</span>

// INCORRECT - Never hardcode text
<Button>Save</Button>  // DO NOT USE
<p>Deploy OpenClaw on your first VPS</p>  // DO NOT USE
```

**Translation keys are organized by category:**

- `common.*` - Shared UI text (Save, Cancel, Delete, Loading, etc.)
- `setup.*` - Initial setup/onboarding
- `language.*` - Language selection
- `theme.*` - Theme toggle
- `nav.*` - Navigation items
- `footer.*` - Footer content
- `errors.*` - Error messages
- `api.*` - API response messages
- `emails.*` - Email templates
- `auth.*` - Authentication pages
- `account.*` - Account management
- `billing.*` - Billing and payment
- `dashboard.*` - Dashboard/Claws page
- `chat.*` - Chat and playground chat interface
- `createClaw.*` - Create Claw modal
- `sshKeys.*` - SSH Keys page
- `landing.*` - Landing page
- `blog.*` - Blog pages
- `changelog.*` - Release notes
- `comparison.*` - Competitor comparison
- `compare.*` - Full comparison table
- `privacy.*` - Privacy policy
- `terms.*` - Terms of service
- `announcement.*` - Service announcements
- `productHunt.*` - ProductHunt banner
- `playground.*` - Playground/agent management

**When adding new features:**

1. First add all text strings to `packages/i18n/src/langs/en.ts`
2. **Add the same keys with translated values to ALL language files:** `fr.ts`, `es.ts`, `de.ts`
3. Use descriptive, hierarchical key names
4. Then reference them in components using `t('category.keyName')`

**CRITICAL: Every new translation key MUST be added to ALL four language files (en, fr, es, de) simultaneously. Never add a key to only one language file — this will cause missing translations in other languages.**

**Date and number formatting must be locale-aware:**

```typescript
// CORRECT - Use getLocale() for locale-sensitive formatting
import { getLocale } from '@/lib'

new Date(dateString).toLocaleDateString(getLocale(), { year: 'numeric', month: 'long', day: 'numeric' })
new Intl.NumberFormat(getLocale(), { style: 'currency', currency: 'USD' }).format(amount)

// INCORRECT - Never hardcode locale strings
new Date(dateString).toLocaleDateString('en-US', { ... })  // DO NOT USE
new Intl.NumberFormat('en-US', { ... }).format(amount)  // DO NOT USE
```

## Formatting & Linting Rules

**CRITICAL: All code written or modified must strictly follow these formatting and linting rules. These are enforced by ESLint and Prettier and checked by Husky pre-commit hooks. Never deviate from them.**

### Prettier Rules (enforced by `.prettierrc`)

- **Single quotes** — Always use single quotes (`'`), never double quotes (`"`)
- **No semicolons** — Never end statements with semicolons
- **4-space indentation** — Use 4 spaces for all indentation, never tabs, never 2 spaces
- **No trailing commas** — Never add trailing commas in arrays, objects, function params, or imports
- **Single JSX quotes** — Use single quotes in JSX attributes (`<div className='foo'>`)
- **Tailwind class sorting** — Classes are auto-sorted by `prettier-plugin-tailwindcss`

### ESLint Rules (enforced by `eslint.config.js`)

These apply to **both api and web** — every `.js`, `.mjs`, `.cjs`, `.ts`, and `.tsx` file:

- **4-space indentation** — `indent: ['error', 4]`
- **Single quotes** — `quotes: ['error', 'single']`
- **No semicolons** — `semi: ['error', 'never']`
- **No trailing commas** — `comma-dangle: ['error', 'never']`
- **Single JSX quotes** — `jsx-quotes: ['error', 'prefer-single']`
- **No multiple empty lines** — Max 1 empty line between code, 0 at start of file, 0 at end of file
- **No newline at end of file** — `eol-last: ['error', 'never']`
- **No `@ts-ignore` restrictions** — `@typescript-eslint/ban-ts-comment` is off
- **Linebreak style** — Disabled (cross-platform)

TypeScript-specific rules (`.ts` and `.tsx` files):

- **Warn on unused variables** — Except those prefixed with `_`
- **Warn on `any` type** — Prefer explicit types over `any`
- **Enforce `import type`** — Always use `import type` for type-only imports with separate-type-imports style

React-specific rules (web app only):

- **React Hooks rules** — Enforced (deps arrays, rules of hooks)
- **React Refresh** — Warns on non-component exports in component files

### Pre-commit Hook (Husky)

On every commit, Husky runs:

1. `pnpm check` — Runs `tsc --noEmit` and `eslint .` for api and web
2. `pnpm version:patch` — Auto-bumps patch version in `apps/api/package.json` and `apps/web/package.json`
3. Stages the bumped `package.json` files

### How to Follow These Rules

When writing any code:

```typescript
// CORRECT
const myFunction = (param: string): string => {
    const result = doSomething(param)
    return result
}

const myObject = {
    key: 'value',
    nested: {
        foo: 'bar'
    }
}

import type { MyType } from '@/ts/Interfaces'
import { useState } from 'react'

// INCORRECT — violates multiple rules
const myFunction = (param: string): string => {
    const result = doSomething(param) // 2-space indent + semicolons
    return result
}

const myObject = {
    key: 'value', // double quotes + 2-space indent
    nested: {
        foo: 'bar' // trailing comma + double quotes
    }
}
```

### Verification Commands

```bash
pnpm format:check    # Check if all files match Prettier rules
pnpm format          # Auto-fix Prettier formatting
pnpm lint            # Check ESLint rules
pnpm lint:fix        # Auto-fix ESLint issues
pnpm check           # Run tsc + eslint for both api and web
```

## Guidelines for AI

1. **Always read files before modifying** - Understand existing patterns first
2. **Use `@/` imports everywhere** - Always use path aliases in both web and API apps, never use `../` or `./` relative imports anywhere
3. **Centralize types in `@/ts/`** - Never define types/interfaces inline; add to Types.ts or Interfaces.ts
4. **Use `import type` for types** - Always use `import type` syntax and place at top of file
5. **Use FC pattern for components** - Always use `const ComponentName: FC = (): ReactNode => { ... }` with `export default ComponentName` at the end
6. **Follow existing patterns** - Match the style of surrounding code
7. **Keep it simple** - Avoid over-engineering or adding unnecessary abstractions
8. **Controllers handle logic** - Routes should be thin wrappers
9. **Use RequestClient** - For API calls, use the shared HTTP client
10. **Zustand for state** - Don't introduce additional state management
11. **shadcn/ui components** - Prefer existing UI components over custom ones
12. **Use translations for all text** - Never hardcode user-facing text; always use `t()` from `@openclaw/i18n`. When adding new translation keys, add them to ALL four language files (`en.ts`, `fr.ts`, `es.ts`, `de.ts`) simultaneously. Use `getLocale()` from `@/lib` for all date/number formatting — never hardcode `'en-US'`
13. **Never write comments** - Do not add code comments, JSX comments, section markers, or doc comments. The code should be self-explanatory. The only exception is when logic is truly non-obvious (e.g., bitwise operations, crypto algorithms, or workarounds for framework bugs)
14. **Never add console.log** - Do not add `console.log` statements. Use `console.error` only for actual error handling in catch blocks. No debug logging, no request logging, no data logging
15. **No section markers** - Never write comments like `// Section Name`, `{/* Section */}`, `// ========`, or category headers in files
16. **Strict formatting compliance** - Every line of code must follow the Prettier and ESLint rules defined above. 4-space indentation, single quotes, no semicolons, no trailing commas, no end-of-file newlines. No exceptions
17. **Run checks after changes** - After writing or modifying code, verify with `pnpm lint` and `pnpm format:check` to ensure compliance
18. **Use camelCase for SVG attributes in JSX** - React requires camelCase for SVG/HTML attributes. Use `stopColor` not `stop-color`, `stopOpacity` not `stop-opacity`, `fillRule` not `fill-rule`, `clipPath` not `clip-path`, `strokeWidth` not `stroke-width`, etc.
19. **Full cleanup on feature removal** - When removing a feature, delete ALL related code: components, hooks, store properties, interfaces/types, translation keys, utility functions, data files, barrel exports, API routes/controllers, and constants. Never leave orphaned code behind
20. **Use PATHS for all URL path segments** - Never hardcode URL path segments like `'/blog'` or `'claws'`. Always use `PATHS` from `@/lib/paths` (or `@/lib`) for path segments and `ROUTES` from `@/lib/routes` (or `@/lib`) for full route strings. When constructing URLs in scripts, components, or SEO metadata, use `PATHS.BLOG`, `PATHS.LOGIN`, etc. To change a URL, update it only in `paths.ts` — everything else derives from it
21. **Toast punctuation convention** - All toast/notification messages must follow consistent punctuation: success messages end with `.` (period) and error messages end with `!` (exclamation mark). This applies to all four language files. Note: French uses a space before `!` per French typographic rules (e.g., `claw !` not `claw!`)
22. **Centralized validation constants** - All input validation length limits must be defined in `packages/shared/src/inputValidation.ts` as a single source of truth. Never hardcode min/max lengths in controllers, components, or translation strings. Import `inputValidation` from `@openclaw/shared` and reference the constants (e.g., `inputValidation.CLAW_NAME.MAX`). Translation error messages must use `{{min}}`/`{{max}}` interpolation parameters filled from these constants. When adding new validated fields, add the limits to `inputValidation.ts` first, then use them everywhere
23. **DropdownMenu must be non-modal** - The `DropdownMenu` component defaults to `modal={false}` (set in `components/ui/dropdown-menu.tsx`). This prevents the dropdown from blocking page scroll when open. Never override this with `modal={true}` unless there is a specific reason. If adding new overlay/popover components from Radix, always set `modal={false}` to preserve scroll behavior
