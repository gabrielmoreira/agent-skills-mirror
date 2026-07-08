# @elizaos/plugin-facewear

Even Realities G1/G2 smartglasses plugin for elizaOS. This package intentionally
does not ship alternate headset clients, spatial routes, terminal views, or separate view
bundles; the repo-wide `viewType` contracts remain in the shared/agent layers so
those modalities can be reintroduced deliberately later.

## Surface

### Services
| Name | Type key | File |
| --- | --- | --- |
| `FacewearService` | `"facewear"` | `src/services/facewear-service.ts` |
| `SmartglassesService` | `"smartglasses"` | `src/services/smartglasses-service.ts` |

### Actions
| Action name | File | What it does |
| --- | --- | --- |
| `FACEWEAR_CONNECT` | `src/actions/facewear-connect.ts` | Emit Even Realities connection instructions |
| `FACEWEAR_DEBUG` | `src/actions/facewear-debug.ts` | Report service and device diagnostics |
| `SMARTGLASSES_CONTROL` | `src/actions/facewear-control.ts` | Even G1/G2 control operations |
| `SMARTGLASSES_STATUS` | `src/actions/facewear-status.ts` | Report smartglasses state |
| `SMARTGLASSES_DISPLAY_TEXT` | `src/actions/display-text.ts` | Paginate and send display text |
| `SMARTGLASSES_MICROPHONE` | `src/actions/microphone.ts` | Enable, disable, or toggle the microphone |

### Providers
| Name | File | What it injects |
| --- | --- | --- |
| `facewearContext` | `src/providers/facewear-context.ts` | Connected smartglasses context |
| `smartglassesStatus` | `src/providers/smartglasses-status.ts` | Full Even G1/G2 status string |

### Routes
| Method + path | File | Purpose |
| --- | --- | --- |
| `GET /api/facewear/devices` | `src/routes/device-config.ts` | Supported device profiles |
| `GET /api/facewear/devices/:id` | `src/routes/device-config.ts` | One device profile |
| `GET /api/facewear/status` | `src/routes/device-config.ts` | Active smartglasses state |

## Layout

```
src/
  index.ts                    Plugin object and public exports
  register.ts                 Settings-section registration
  status-format.ts            Shared status formatting
  actions/                    Smartglasses actions
  components/                 Settings-section wrapper
  devices/                    Even Realities profile registry
  providers/                  Agent context providers
  routes/                     Device/status routes
  services/                   Facewear and smartglasses services
  protocol/                   Even Realities binary protocol
  transport/                  Native bridge, Noble, Web Bluetooth, mock transports
  ui/                         Smartglasses Settings UI
native/android/even-realities/ Native Android bridge companion
docs/                         Even Realities notes and proof workflow
```

## Commands

```bash
bun run --cwd plugins/plugin-facewear build
bun run --cwd plugins/plugin-facewear build:js
bun run --cwd plugins/plugin-facewear build:types
bun run --cwd plugins/plugin-facewear typecheck
bun run --cwd plugins/plugin-facewear lint
bun run --cwd plugins/plugin-facewear test
bun run --cwd plugins/plugin-facewear verify:app
```

## Config

| Setting / env var | Default | Description |
| --- | --- | --- |
| `FACEWEAR_SMARTGLASSES_TRANSPORT` | `"auto"` | `auto` \| `even-bridge` \| `web-bluetooth` \| `noble` |
| `FACEWEAR_SCAN_TIMEOUT_MS` | `10000` | Noble scan timeout in milliseconds |
| `FACEWEAR_AUTO_INIT` | `true` | Send G1/G2 connection-ready init packets automatically |
| `FACEWEAR_INIT_MODE` | `"lens-specific"` | `lens-specific` \| `official` \| `android-f4` |

Legacy `SMARTGLASSES_*` aliases are still read and mapped to the `FACEWEAR_*`
settings.

## Conventions

- `@abandonware/noble` is optional and must stay lazily imported.
- Transport auto-selection order is native bridge -> Web Bluetooth -> Noble.
- `DEVICE_REGISTRY` currently lists only `even-realities`; add device support by
  adding a real service/transport path, not a placeholder profile.
- Keep `CLAUDE.md` and `AGENTS.md` identical.
- Repo-wide conventions, error policy, evidence, and PR requirements live in the
  root `AGENTS.md`.
