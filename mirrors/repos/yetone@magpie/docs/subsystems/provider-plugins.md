# Provider and plugin ownership

Some built-in subscriptions are deprecated and have community plugins that provide the same service. A subscription can still use its built-in implementation or move to its plugin. That ownership determines where sign-in, refresh, model discovery, requests, usage, and errors are handled.

## Responsibilities and sources of truth

| Part | Responsibility | Source |
| --- | --- | --- |
| Provider migration | Match subscriptions to plugins, record ownership, transfer accounts, and maintain required plugin versions | [`migrate.go`](../../internal/provider/migrate.go) and `migrate_*.go` in the same directory |
| Provider integration | Expose plugin-backed provider cards, usage, sign-in, and the plugin's own daily check-in | [`plugins.go`](../../internal/provider/plugins.go), [`plugin_usage.go`](../../internal/provider/plugin_usage.go), [`pluginsignin.go`](../../internal/provider/pluginsignin.go), [`plugin_checkin.go`](../../internal/provider/plugin_checkin.go) |
| Plugin host | Load plugins and execute their code | [`internal/plugin`](../../internal/plugin), [`host.js`](../../internal/plugin/host.js) |
| Gateway | Dispatch requests through the implementation that owns the subscription | [`internal/gateway`](../../internal/gateway) |
| GUI | Present available subscriptions, migration state, and plugin sign-in | [`app.js`](../../internal/gui/assets/app.js) |
| Community plugin | Implement the moved subscription's upstream behavior | [magpie-community/plugins](https://github.com/magpie-community/plugins), `packages/<name>` |

The `movers` map assembled in `internal/provider/migrate*.go` is the authoritative subscription-to-plugin mapping. Each mover's `min` is the minimum plugin version required by magpie. The list of moved subscriptions in [AGENTS.md](../../AGENTS.md#built-in-subscriptions-that-a-plugin-serves) is a contributor lookup; confirm the mapping in source when changing it.

## Ownership and runtime paths

`provider.Moved(id)` identifies a subscription whose migration state in `migrations.json` is `plugin`. In `/api/providers`, its row exposes `move.state == "plugin"`; the GUI also receives its id in `onPlugins`.

| Operation | Built-in owns the subscription | Plugin owns the subscription |
| --- | --- | --- |
| Sign-in, refresh, and models | Built-in provider implementation | Community plugin through magpie's plugin integration |
| Upstream requests and translation | Built-in gateway adapter | Plugin fetch through the plugin host |
| Usage and upstream errors | Built-in implementation | Plugin, exposed through magpie's provider integration |
| Migration state and required version | Magpie | Magpie |

For a moved subscription, its built-in upstream implementation does not run. Plugin accounts use `Account.Agent == "plugin"`; requests reach `plugin.Fetch` through `Provider.Do` and bypass the built-in subscription adapter. Magpie still handles routing, protocol conversion, quota handling, and compatibility adjustments, as well as the plugin host, provider integration, migration code, and GUI plugin paths.

Quota aggregation in [`quotas.go`](../../internal/provider/quotas.go) suppresses a key's GLM Coding Plan card only when its comparable reset windows match a ZCode subscription card: built-in or moved `zcode`, or independently installed `zcode-plugin`. [`PlanQuotas`](../../internal/provider/planquota.go) identifies GLM plans by their quota endpoint, including custom provider ids. Matching reset schedules from unrelated vendors do not hide cards. Within this pair, resets remain a heuristic for the shared account; a plan's `User` is a key label or mask, not a login identity. Errors, conflicting resets, or no comparable resets keep the plan visible. This applies to the Usage page, tray, quota reports, alerts, and quota waits; it does not change plugin ownership or upstream requests.

## Usage a plugin collects late

A plugin that learns a step's usage only after the step has ended reports it with a later step, in `usage.magpie_deferred` (`prompt_tokens`, `completion_tokens`, `cached_tokens`, `cache_write_tokens`) beside that step's own usage fields. The Cursor plugin does this: a tool step's usage event shows seconds after the step, so the step says 0 and the conversation's next step collects the event ([#1053](https://github.com/yetone/magpie/issues/1053)).

The gateway parses the field into `Usage.Deferred` ([`cUsage`](../../internal/gateway/chat.go)) and adds it only where it bills: the usage records, the OTel attempt spans and route pricing, which prices it as a tier before the request's own ([`routeUsage`](../../internal/gateway/trace.go), [`Usage.billed`](../../internal/gateway/ir.go)). What a client is told stays the request's own, because agents read `prompt_tokens` as how full their context is: the passthrough forwards the plugin's bytes as they are, whose standard fields are the step's own, and a translated reply is encoded from the own count alone. `promptCounted` also reads the request's own. A reply without the field is handled as before. With an older magpie the field is ignored and the owed step goes unbilled in the ledger. [`deferred_usage_test.go`](../../internal/gateway/deferred_usage_test.go) covers the passthrough, the translated reply, the ledger, the OTel span and the pricing tiers.

## A plugin's daily check-in

A plugin can press its vendor's daily check-in (签到) itself: its `auth` hook gains `checkin(getAuth, provider)`, beside `usage`. The host lists the provider with `checkin: true` (`plugin.Provider.Checkin`) and answers `checkin({provider, account})` (`plugin.AccountCheckin`) by refreshing the account as `usage` does and calling the hook with the account's auth.

The hook returns `{outcome, credit?, streak?, message?}`. `outcome` is one of `claimed` (checked in now), `done` (already in today), `ineligible`, `inactive` (no check-in event now), `captcha` or `failed`. A throw, or an outcome not in that list, is `failed` with the reason. `captcha` means the vendor wants a captcha: magpie never solves one, and says "check in in its own app" instead. A plugin must not solve captchas either.

[`plugin_checkin.go`](../../internal/provider/plugin_checkin.go) runs these through the same `checkiner` as the built-in check-ins ([`checkin.go`](../../internal/provider/checkin.go)): each signed-in, in-use account once a Beijing day, the first look 2 minutes after start and then every 30 minutes, a `failed` asked again after 30 minutes, every other outcome settled for the day. Results are kept in `plugin-checkin.json` by `provider|account`; a failure is recorded as failed and never resets an account, a key or a previous day's result. Each account's Usage card has the check-in row (`checkinBy: "plugin:<provider>"`), and Settings → Usage has a Plugins tab with a Daily check-in switch per provider (`settings.PluginCheckins`, `POST /api/settings/plugin-checkin {provider, on}`; *Check in now* is `POST /api/usage/plugin-checkin {provider}`). `magpie accounts checkin` and `c` on the TUI's Usage page include them. Every check-in, built-in or a plugin's, also skips an account listed in `settings.CheckinOff` by its file key (#1902): `checkinNow` asks nothing for it, by the loop or a press, `CheckinAccounts()` lists each account with its own `on` for Settings (`checkinAccounts`, a row each under the vendor's switch when it has two or more, `POST /api/settings/checkin-account {key, on}`), and its card carries `checkinOff`.

The switch is off by default. For a provider whose vendor magpie checked in through the plugin's fetch before (WorkBuddy, Trae CN, MiniMax Code, Qoder), it follows that vendor's existing switch until set on its own, and magpie's own check-in leaves that provider's accounts to the plugin (`pluginChecksIn`), so an account is never checked in twice.

Trae CN plugins without `auth.checkin` use [`trae_checkin.go`](../../internal/provider/trae_checkin.go) through the plugin's fetch: `/status`, then `/claim` while the check-in is on and today's isn't in. A claim answered 9074 (当前参与用户太多，请稍后再试) is saved as `own-app`, settled for the Beijing day like any answer other than `failed`: Trae CN pays check-in credits only to a device its own app registered, so neither the loop nor Check in now claims again that day, and the card, Settings, TUI and CLI say to check in in the Trae CN app (#808). 9074 on `/status`, and every other code, keep their previous handling. `own-app` is not a plugin hook outcome.

WorkBuddy's check-in ([`workbuddy_checkin.go`](../../internal/provider/workbuddy_checkin.go), built-in or through the plugin's fetch) tells a 401 apart. WorkBuddy's gateway answers a token it refuses with a bare HTML 401, which the card said only as "Unauthorized" and retried every 30 minutes. On a 401 from `/v2/billing/meter/checkin-activity-status` or `/daily-checkin`, the account's credits (`/billing/meter/get-user-resource-summary`) are read with the same headers: when they read, the sign-in is good and the check-in alone refuses magpie (WorkBuddy's own app sends its check-in, and only that, with an `X-Device-Token` from its security SDK), so it is saved as `own-app` for the day; when they don't, it is `failed` with "sign in to it again".

Qoder plugins without `auth.checkin` still use [`qoder_checkin.go`](../../internal/provider/qoder_checkin.go) through the plugin's fetch. The server's `CLAIMABLE` status decides whether to claim; the local `[startAt, endAt)` check only recognizes an already-claimed campaign and its expiry, including one that crosses Beijing midnight. Successful results keep the active campaign's end in the optional `until` field of `qoder-checkin.json`. Scheduled checks reuse results from the same Beijing day for at most 30 minutes and never past that end, so a long campaign cannot hide new or reset campaigns indefinitely. The existing loop looks every 30 minutes and on a Beijing day change; a midnight refresh saves today's result for the Usage card and TUI. An `inactive` result is now asked again after 30 minutes rather than settled for the day; failures retain their existing retry schedule. A manual check-in always asks immediately. Saved results without `until` remain readable and use the same 30-minute refresh, with no migration needed. Other vendors and plugins with their own check-in retain their daily settlement.

## A plugin's own options

A plugin can declare switches for its provider (#2038): its `auth` hook gains `options: [{key, label, description?, default?, confirm?}]`. The host ([`host.js`](../../internal/plugin/host.js) `optionsOf`) keeps an option whose `key` matches `[a-z0-9_-]{1,40}` and whose `label` isn't empty, drops a key seen before, caps the label at 60 characters and the description and `confirm` at 300, takes `default` only when it is `true`, and keeps the first 16. The provider is listed with them (`plugin.Provider.Options`).

The user's values are kept in `settings.PluginOptions` by the plugin's own provider id and the option's key, and set with `POST /api/settings/plugin-option {provider, key, on}`, which checks the key the same way. The host is handed them at `init` (`options`) and again after each change (`setProviderOptions`, `plugin.SetProviderOptions`, sent only to a host already running). A plugin reads them through `input.magpie.option(provider, key)` (the user's value, else the default; false for a key it didn't declare) or `input.magpie.options(provider)` (every declared key). Both read the current values each time, so a change reaches the plugin without a restart. A plugin written for older hosts checks `input.magpie?.option` first. Nothing runs when an option changes: magpie only keeps and hands over the value. The check-in switch is separate and unchanged.

The provider's editor lists them under *Plugin options* (`pluginOptionsField` in [`app.js`](../../internal/gui/assets/app.js), the values from `/api/providers`' `plugins[].options[].on`), an Off/On each beside the plugin's label and description, put in as text. One with `confirm` asks it before it is turned on. Changes wait for Save, which posts each changed one before the provider.

## A plugin whose upstream searches

A plugin in front of Anthropic's or OpenAI's own API (a CPA or sub2api relay, say) can say its upstream answers a web search tool by itself (#2027). Its `config` hook sets `searches: true` on the provider; the host passes it through (`plugin.Provider.Searches`), and [`pluginProvider`](../../internal/provider/plugins.go) sets the provider's `Searches`, as a custom provider's "Searches the web by itself" does (#359). [`searchesItself`](../../internal/gateway/search.go) honours it for a plugin's provider only, on Anthropic's or Responses' API, and only for one the plugin has a model on: a client's `web_search` then goes to the plugin's `fetch` as sent, not through magpie's search. Another sign-in's `Searches` is never read, and Codex's and Grok's stay as they were. As with a relay, `searchRank` leaves it out, so magpie never picks it to search for other models; Settings can name it by hand (`namedSearcherRank`).

## A plugin's decision API

A plugin can serve TypeSafe's System One for its provider (#1514). Its `config` hook sets `decide: true` on the provider, and `decides: true` on a model that answers questions rather than a conversation, in the `config` hook or on the `models` hook's list. The host passes both through (`plugin.Provider.Decide`, `plugin.Model.Decides`). [`pluginProvider`](../../internal/provider/plugins.go) then sets the provider's `Decide` to `plugin://<id>/v1`, its own base: `pluginFetch` sends nowhere but the loader's host, so a decision address of the plugin's own couldn't be reached. `AskSystemOne` and the gateway's classifier post `/v1/systemone` with `Provider.Do`, which reaches the loader's `fetch` as `{baseURL}/systemone` with the account's sign-in.

In [`decide.go`](../../internal/provider/decide.go) a plugin provider's decision models are the ones it marks (`pluginMarks`, read from the plugin's current listing) and Jev's by name (`jev-*`). They are kept from agents (`isDecision` in `buildEntries`), refused for chat ("only decides"), refused as a member of a group beside models that hold a conversation (a group of decision models alone answers `/v1/systemone`: [gateway-routing](gateway-routing.md#remote-magpie-apis)), and offered as a group's classifier (`Deciders`, `DecisionModels`). A mark counts only when the provider says `decide`; without it every model stays one to chat with. A plugin provider's editor (the account editor) has no address fields, so this address is never typed; the GUI marks the decision models from `deciders`.

## Where the agent works, for a plugin's fetch

A plugin's fetch runs in magpie's plugin host, so its `process.cwd()` is magpie's own folder, not the folder of the agent that asked. A plugin that tells its vendor the user's environment, as the ZCode plugin's Start Plan request does in its `# Environment` section, said magpie's `~/.config/magpie` as the working directory, and the model went looking there (magpie-community/plugins#86).

The gateway tells the plugin instead. On every request to a plugin's provider, `forwardOnce` calls `tellWorkPlace` ([`workdir.go`](../../internal/gateway/workdir.go)), which reads the request as sent to the plugin with the same `workPlace` that rules by folder use ([gateway-routing](gateway-routing.md)) and sets two headers on the plugin's fetch:

| Header | Value |
| --- | --- |
| `x-magpie-work-dir` (`provider.WorkDirHeader`) | The folder the agent says it works in, percent-encoded UTF-8 (`decodeURIComponent` reads it). |
| `x-magpie-work-git` (`provider.WorkGitHeader`) | `yes` or `no`: whether that folder is in a git repository. The agent's own word beside the folder when it says one (Claude Code's `Is a git repository: true`/`false`, OpenCode's `Is directory a git repo: yes`/`no`), else a `.git` in the folder or above it when the folder is on this computer (`provider.GitSaid`, `provider.GitOnDisk` in [`workplace.go`](../../internal/provider/workplace.go)). |

Each is left off when it isn't known: no folder said, or a folder not on this computer that the agent didn't say is a repository. A plugin then leaves out what it can't know rather than saying magpie's. The host's `fetch` (`unsaid` in `host.js`) takes both headers off every request a plugin sends, so a plugin that sends on the headers it was given sends them to no vendor.

`TestPluginToldWhereTheAgentWorks` ([`plugin_workdir_test.go`](../../internal/gateway/plugin_workdir_test.go)) sends Claude Code's and Codex's captured requests and Pi-style ones from a folder in a repository and one not, through the fake plugin, and checks what the plugin read and that the vendor got neither header.

## Two plugins for one provider id

The host runs one plugin per provider id. When two installed plugins have `auth` hooks for the same id, such as a third-party plugin and the user's own copy added by its folder, `auths()` in `host.js` takes the one picked for that id in `plugins.json`'s `prefer` map (provider id → spec). Without a pick it takes the last one in the list, as OpenCode does. Only the serving plugin's `provider.models` hook runs for that id. Every plugin's `config` hook still runs, so another plugin can still add models or a name to `config.provider[id]`.

Before this, the plugin that lost the id disappeared silently: its row read "Signs in to nothing magpie can use", and `keepUnloaded` could list the id twice, once from the old `plugin-providers.json` (neiko on Discord). Now:

- `init` returns each plugin's `provides` (the ids its auth hooks name) and `servedBy` (id → the other spec, for each id it doesn't serve).
- `plugin.Clashes` turns these into `{id, by, with}` per spec.
- `/api/plugins` gives each row its `clashes`, along with the provider's listed name.
- `keepUnloaded` doesn't keep a provider from before when another plugin serves its id now.

Both rows stay visible on the Plugins page:

- The serving row says "{other} signs in to {name} too; this one serves it".
- The other row says, in amber, "{name} is served by {other}, which signs in to it too". It has a **Use for {name}** button, which calls `POST /api/plugins/prefer {spec, provider}` (`plugin.Prefer`) and restarts the host.

In the CLI, `magpie plugin list` prints the same two lines, and `magpie plugin use <name> <provider>` makes the pick.

How the store handles picks and names:

- Removing a plugin drops its picks.
- Switching a plugin off hands the id to the other plugin until it is switched on again.
- Re-adding a plugin under a new version or spec keeps its picks.
- Remove, off, options and prefer find a plugin by its exact spec first, then by package name (`indexOf` in `store.go`). This way, acting on one plugin never reaches another plugin that has the same package name.

## How ownership changes

Migration records use four states:

| State | Meaning |
| --- | --- |
| `moving` | Migration is in progress or was interrupted. An explicit retry first rolls back the interrupted move. |
| `plugin` | The plugin owns the built-in provider id. This is the only state recognized by `Moved`. |
| `back` | Ownership returned to the built-in. Automatic handover leaves it there. |
| `failed` | Migration failed and the built-in continues serving. Automatic retry waits six hours. |

The editor's "Move to plugin" action calls `provider.Adopt`. With accounts, adoption delegates to `Move`, which imports and validates accounts and model coverage before committing plugin ownership. With no accounts, adoption verifies the package and the provider it serves, then records plugin ownership without account checks.

Installing the plugin independently can also hand over ownership through `provider.HandOver`. The package must be enabled, meet the mover's minimum version, and serve the expected provider. After add, update, or upgrade, the GUI calls `HandOver(ctx, false)`, which can adopt a built-in with no accounts. Existing built-in accounts wait for `HandOver(ctx, true)` in gateway maintenance.

`KeepRetiringMoved` first runs after 20 seconds, then hourly. Each cycle maintains moved plugin versions, calls `MoveRetiring`, then performs automatic handover. `MoveRetiring` moves subscriptions listed in `provider.Retiring` that have built-in accounts, preserving move-back choices and waiting six hours after a failed attempt. That list is currently empty. Handover preserves a plugin already signed in under its separate `-plugin` id and skips existing migration records except a `failed` record old enough to retry.

`MoveBack` restores built-in ownership and records `back`. Compatible accounts added through the plugin can return too; incompatible accounts can remain with the plugin under its separate id. Removing or disabling a plugin first moves affected built-ins back and stops if that fails. A package installed by the user remains after moving back; a migration-installed package is removed only when no remaining signed-in or moved provider needs it.

Removing a plugin also sets aside the model picks its providers left in `providers.json` (#2057, `plugin_left.go`). Before, nothing listed those records and `magpie provider rm` couldn't find them, so sync and backup asked for a sign-in to them on every run (`NotSignedIn`).

- `RemovePlugin` reads which ids the plugin's providers have (`pluginRecordIDs`: `PluginID` of each provider `plugin.Listed` last gave for its spec, an off plugin's included) while it is still installed. It leaves out:
  - a built-in's id;
  - any id another installed plugin also serves.
- After `plugin.Remove`, only records under those ids that hold picks alone (`OnlyPicks`) move into `providers.json`'s `pluginLeft`, under the package's name. A record with an endpoint or a key is the user's own provider and stays.
- With no listing known (no cache and no readable `plugin-providers.json`), nothing is set aside.
- `provider.AddPlugin` is what the GUI, the CLI and `AddPlugins` (backup and sync) add through. It puts the package's records back, each one whose id has no record now. One the user gave to a provider since stays aside.
- Switching a plugin off sets nothing aside, since off is undone by switching it back on. Records left behind by removals before this change stay as they are; they can't be told from picks a sync brought for a plugin not installed here yet.

New users do not see an unused deprecated built-in in the Add sheet. `unusedSub` leaves it out when it has no account. Until an installed replacement takes ownership, `replacedSub` makes the Add sheet show the plugin tile. The Plugins page is the installation entry point.

`keepMovedCurrent` maintains the required plugin version for moved subscriptions. Raising the owning mover's `min` after publishing a plugin fix triggers this update path. Update failures are logged; disabled packages and local-folder installations are not automatically replaced.

The editor's *Update* button and *Update all* install npm's newest version; a pin the user set is kept until they update it themselves, and is then unpinned. `keepMovedCurrent` is the one path that acts without the user pressing anything, so `installPlugin` leaves what the user chose: a pinned npm version below the move's `min` is not reinstalled, and the move says it is pinned and which version it needs; a git install is reinstalled from its own spec; an unpinned npm one goes through `plugin.Upgrade` (npm's newest, which bun says why it won't install under a `minimumReleaseAge`, where `Add`'s `@latest` would quietly give an older one); a plugin the user turned off is left alone.

A `@magpie-community` package npm doesn't give is installed from the community repo's `dist` branch ([`dist.go`](../../internal/plugin/dist.go)). npm can't take a new package's first version without an owner's 2FA (Trusted Publishing sets up only a package that exists), so reviewed plugins sat unmerged waiting for someone to publish them (magpie-community/plugins#84); a Trusted Publisher made after 2026-09-03 allows stage publish only, and zed 0.1.7 and zen-free 0.1.7 were refused that way. The repo's `publish.yml` now packs every merged version onto `dist` (`scripts/dist.mjs`: `tgz/<file>` and `index.json` with each version's sha512, manifest and the README) with nobody's credentials, and npm is published to beside it. `install` asks npm first, as before; only when `bun add` fails for a community package at `latest` or an exact version (`distWanted`), and not because of the user's `minimumReleaseAge` (that hold is kept), does `installDist` fetch the tarball, refuse it unless its sha512 is the index's, keep it in `plugins/dist` and `bun add ./dist/<file>`. A later install from npm takes its place and `pruneDist` removes tarballs `package.json` no longer names. `npmAsk` (the market's version, *Update*, the hourly check) takes `dist`'s latest when npm errors or is behind, and `Readme` falls back to its README. The branch is read through the 「国内镜像」 switch's jsDelivr copy when that is on (`fetchJSONFaithful`), else raw.githubusercontent.com. `TestDistInstallsAPackageNPMDoesntHave`, `TestDistServesAVersionNPMRefused`, `TestDistRefusesATarballNotItsIndexs` and `TestUpdateBunHoldsBackSaysWhy` (with `dist` holding the held version) in [`dist_test.go`](../../internal/plugin/dist_test.go) and [`update_held_test.go`](../../internal/plugin/update_held_test.go) cover these.

A plugin on the list whose package isn't in `plugins/` is installed again from its own spec, switched off or not, by `plugin.InstallMissing`. `KeepUpdated` runs it 30 seconds after start and then hourly, before `CheckUpdates`. Nothing else did this. An update skips a plugin with no installed version, so the host said `no such plugin: …\node_modules\…` at every start until the user removed the plugin and added it again (#2002, Windows, after an update). Every bun command that changes `plugins/` runs one at a time under `installMu`: `install` (with the first `package.json` it writes), `reinstall`'s `bun update`, and `Remove`'s and `add`'s `bun remove`. At start, `KeepUpdated` and `keepMovedCurrent` both run `bun add`. Two at once each read `package.json` before either writes it, so one change was lost (reproduced with Bun 1.4.3 on Windows), and a git plugin whose dependency was dropped can't be found. `TestMissingPluginsInstalledAgain` and `TestBunCommandsOneAtATime` in [`plugin_missing_test.go`](../../internal/plugin/plugin_missing_test.go) cover both.

A plugin the user turned off stays off through every install path: `add` keeps `Off` when it replaces an existing entry, so Add, Update, Update all and Upgrade all leave it as the user left it.

## Constraints for fixes

Determine ownership before choosing the fix location. A bug affecting a moved subscription usually needs a change in the community plugin. A built-in-only fix does not reach moved users.

For a plugin fix, publish the corrected community package and raise the owning mover's `min` to that version. Change the built-in too when the fix must reach users who have not moved.

Keep the migration, host, and upstream behavior separate when investigating failures. A plugin bug can require a community change; a host, provider-card, sign-in orchestration, or migration bug can require a magpie change even for moved users.

The host gets magpie's proxy only as `MAGPIE_*_PROXY` and applies it to each fetch itself (`proxyFor`), and to each HTTP/2 session a plugin opens (`http2.connect`, `tunnel`, #1035). A host on the user's own network goes around that proxy as it does for magpie's own requests (`onLAN` in `host.js`, a port of `internal/netproxy/lan.go`'s: a private, link-local, loopback or CGNAT address, a `.local` name, or a name every address of which is one of those, looked up for 400 ms at most and kept a minute; #1572). A provider's own proxy is still taken as it is. The two rules are kept the same: a change to one is made in the other. A program a plugin starts, such as the Grok plugin's `grok login`, gets it back as `HTTPS_PROXY`/`HTTP_PROXY` from the spawn wrapper in `host.js`, unless the plugin set one. A sign-in that works in the built-in and fails through the plugin may be a host difference like this one, not a plugin bug.

magpie downloads the Bun build for this machine (`bunTarget` in [`bun.go`](../../internal/plugin/bun.go)): the baseline build on x64 Linux and Windows, the native `bun-windows-aarch64` on Windows on ARM (it was turned away as having no build until #2183), and on a musl Linux such as Alpine (`libc.Musl`, the check Claude Code's download uses too) the musl one, `bun-linux-x64-musl-baseline` or `bun-linux-aarch64-musl`. A glibc build names glibc's loader, which Alpine lacks, so it couldn't start there and exec said "no such file or directory" (#1877). A musl Linux keeps its Buns and their `state.json` under `bun/musl`, so a machine whose C library changed never runs the other one's build or takes its set-aside versions; everywhere else they stay in `bun`, where a Bun downloaded before is. A bun that is on disk but can't be started says it is a build for another C library and names `MAGPIE_BUN` (`cantStart`), and it isn't fallen back from or set aside: the version before is the same build. Bun's musl build needs libstdc++ and libgcc; on an Alpine without them, `bun add` and the host's start say which library is missing and `apk add libstdc++ libgcc` (`missingLibs`). `TestBunTargetForMusl`, `TestMuslBunKeptApartFromGlibc`, `TestCantStartSaysCLibrary`, `TestHostOnUnstartableBunSaysCLibrary`, `TestMissingLibsNamesThem` and `TestHostOnBunLackingLibsSaysWhich` in [`bunmusl_test.go`](../../internal/plugin/bunmusl_test.go) cover these.

Bun takes only http:// and https:// proxies. A SOCKS5 one, such as a Mac's system SOCKS proxy, is given to every bun magpie starts as a loopback HTTP proxy in front of it (`netproxy.Bridge`): to the host through `hostEnv`, and to `bun add`, `bun update` and `bun remove` through `bunCommand` (`netproxy.EnvForBun`). Before, an install with only a SOCKS system proxy failed as `UnsupportedProxyProtocol` (#1409). An agent CLI that bun installed is updated through the bridge too (`updateEnv` in `internal/agent/cliupdate.go`).

The host reads its proxy once, when it starts. When the proxy magpie would give a new host differs from the one the running host got (the system proxy set after magpie started, as at login before Clash is up, or Settings changed), the next call to the host replaces it (`proxyMoved` in [`host.go`](../../internal/plugin/host.go), looked at no more than every 15s, or every 2s while the host has no proxy: `proxyLookNone`, #1518). A call made for a read nobody asked for, while allowances are read only when asked (`netproxy.Held`), never reaches the host. Before this, a host started without a proxy kept none, so the Grok plugin's `grok models` couldn't renew its token and the account read as signed out after each restart (#1363).

What a plugin writes with `console.log`, `console.warn` and the rest goes to the host's stderr, which magpie logs a line at a time (`drainStderr` in [`host.go`](../../internal/plugin/host.go)). A line over 4 MiB ends the logging: magpie logs that it did, and reads and drops the rest, so the host never blocks on a full pipe. Before, nothing read the pipe after such a line: on Windows the host hung on its next write, and on Linux Bun kept everything written after it in memory.

A plugin's account whose sign-in its vendor refused (`lapsed`, or an allowance read saying so) keeps Sign in again and Remove on its row, whether it is in use or the agent's own (`signedOut` in `renderAccounts`, `app.js`).

The GUI's plugin integration includes `subOf`, `pluginSubs`, and `startPluginSignIn`. A change to sign-in or provider presentation must follow these paths as well as the built-in paths it affects.

## Verification

[`migrate_notice_test.go`](../../internal/provider/migrate_notice_test.go) includes `TestMovedBuiltinsSayTheirPlugin`, which checks that moved built-ins tell contributors which plugin serves them. Migration tests live beside [`migrate.go`](../../internal/provider/migrate.go).

Gateway parity tests in [`plugin_parity_test.go`](../../internal/gateway/plugin_parity_test.go) and other `plugin_*_test.go` files compare or exercise plugin paths. A built-in test alone does not establish moved-user behavior. Inspect each test's fixture to confirm that it covers the provider and operation being changed.

[`plugin_decide_test.go`](../../internal/gateway/plugin_decide_test.go) runs the fake plugin (`FAKE_DECIDE`) with a decision API: its marked and `jev-*` models are classifiers and not offered to agents, chat to one is refused, a group saves one as classifier, not beside a chat model, and a group of decision models alone, and each classifier's question reaches the fake vendor at `/v1/systemone` through the plugin's fetch. With `FAKE_DECIDE=models` the marks without `decide` change nothing.

[`plugin_checkin_test.go`](../../internal/provider/plugin_checkin_test.go) runs the fake plugin's `auth.checkin` (`FAKE_CHECKIN`) through the schedule: off, each outcome, no second press the same day, failures only after the retry window, the next day, cards and Settings, and the vendor check-in stepping aside. `plugin-checkin.test.cjs` covers the card row and the Settings tab.

[`plugin_options_test.go`](../../internal/plugin/plugin_options_test.go) loads `testdata/options` in a real host: which declared options are kept and how they are capped, the user's value over the default at start, and a change read by the plugin after `SetProviderOptions` without a restart. [`plugin_option_api_test.go`](../../internal/gui/plugin_option_api_test.go) covers the endpoint, a bad key, and a Settings save keeping the values. `plugin-options.test.cjs` covers the editor in Chromium and WebKit, 1100 and 420 wide, in every language.

[`plugin_cliproxy_test.go`](../../internal/plugin/plugin_cliproxy_test.go)'s `TestPluginHostTakesANewProxy` starts a real host without a proxy, sets one, and checks that a program the plugin starts gets it. [`plugin_lan_test.go`](../../internal/plugin/plugin_lan_test.go)'s `TestPluginLeavesTheUserNetworkDirect` checks with a real host that fetches (http:// and https://) and an HTTP/2 session to this computer's private address reach it directly with a proxy set, and that a public address and an unresolvable name still go through the proxy. `plugin-signed-out-account.test.cjs` covers a moved Grok account signed out while in use and as the agent's own, in Chromium and WebKit, en and zh, 420 and 1100 wide.

[`stderr_drain_test.go`](../../internal/plugin/stderr_drain_test.go)'s `TestDrainStderrKeepsTheChildGoing` checks that a child writing 8 MiB to stderr with no newline finishes, and that the log says its stderr was dropped. [`stderr_e2e_test.go`](../../internal/plugin/stderr_e2e_test.go)'s `TestHostStartsPastAnOverlongStderrLine` starts a real host whose plugin logs one 5 MiB line while it loads, and checks that the host starts; without the fix it fails on Windows only.

These tests cover two plugins on one provider id:

- [`plugin_clash_test.go`](../../internal/plugin/plugin_clash_test.go)'s `TestTwoPluginsOneProvider` loads two copies of the fake plugin in a real host. It checks `provides`/`servedBy`, `Clashes`, that the id is listed only once, and that the pick survives Prefer, a restart, off/on and Remove.
- `TestPluginNamedExactlyFirst` and `TestKeepUnloadedLeavesAServedID` cover the store and the providers cache.
- `TestPluginsClashRows` (`internal/gui`) and `TestPluginListSaysClash` (the CLI) check what the user sees.
- `plugin-clash.test.cjs` covers both rows and Use for, in Chromium and WebKit, in en, zh, zh-TW, ja and de, at 1100 and 560 wide.

[`quotas_dedupe_test.go`](../../internal/provider/quotas_dedupe_test.go) checks unrelated reset collisions and ZCode deduplication, including plugin usage window conversion for both plugin ids. [`TestPlanQuotas`](../../internal/provider/planquota_test.go) checks the custom GLM endpoint, cached cards, and fallback readings restored from disk. These fixtures do not contact the live vendors or run the community ZCode plugin.

Run the relevant package tests with an isolated home directory. Resolve GOPATH and Go's caches before changing HOME, so repeated runs reuse dependencies and downloaded toolchains. The subshell makes temporary files writable and cleans up its home on exit, including when tests fail, and returns the test command's exit status.

```sh
(
	verification_home=$(mktemp -d) || exit
	trap 'chmod -R u+w "$verification_home"; rm -rf "$verification_home"' EXIT
	verification_gopath=$(go env GOPATH) || exit
	verification_modcache=$(go env GOMODCACHE) || exit
	verification_buildcache=$(go env GOCACHE) || exit
	HOME="$verification_home" GOPATH="$verification_gopath" GOMODCACHE="$verification_modcache" GOCACHE="$verification_buildcache" \
		go test -tags nogui ./internal/provider ./internal/gateway ./internal/plugin
)
```

Some migration and gateway plugin tests require Bun on PATH and use local plugin fixtures; they skip when Bun is unavailable. Report any skipped tests and verify the community package separately when its implementation changes.
