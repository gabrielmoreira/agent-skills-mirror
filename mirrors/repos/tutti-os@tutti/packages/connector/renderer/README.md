# @tutti-os/connector-renderer

Host-neutral Connector frontend application services and shared React UI.

The package exposes three narrow entries and no root barrel:

```ts
import {
  ConnectorMarketModule,
  IConnectorMarketModule
} from "@tutti-os/connector-renderer/application";
import {
  ConnectorComposerMenu,
  ConnectorMarketDialogHost,
  ConnectorMarketPanel,
  ConnectorPaletteItem,
  ConnectorSelectionList
} from "@tutti-os/connector-renderer/ui";
import {
  connectorMarketI18nResources,
  createConnectorMarketI18nRuntime
} from "@tutti-os/connector-renderer/i18n";
```

## Ownership

`src/application` is React-free. It owns host-neutral backend/event/admission
ports, Root/Lifecycle/StartupJob services, state, View projection, dialog
intents, and declarative authorization mapping.

`src/ui` is the only owner of Connector-specific React, including Catalog,
dialogs, authorization rendering, Composer controls, selection chips, Palette
items, icons, toolbar, and default i18n resources. It uses the repository UI
System and accepts neutral Connector models and semantic callbacks.

Desktop supplies generated-client, account, event, and navigation adapters.
AgentGUI owns Agent draft and prompt semantics, then projects those models into
the neutral Renderer UI contracts. Neither host is imported by this package.

Wire authorization schemas and the OpenAPI fragment are published by
`@tutti-os/connector-contracts`.

## Validation

```sh
pnpm --filter @tutti-os/connector-renderer test
pnpm --filter @tutti-os/connector-renderer typecheck
pnpm --filter @tutti-os/connector-renderer build
pnpm check:connector-boundaries
```
