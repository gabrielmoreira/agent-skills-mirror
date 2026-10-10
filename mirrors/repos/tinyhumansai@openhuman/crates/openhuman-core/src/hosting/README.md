# hosting

Puts a workspace on the internet. This domain is the thin seam between
OpenHuman and [`tinyhosts`](../../../../vendor/tinyhosts), the unified hosting
API. TinyHosts owns everything about a provider (today, Vercel): its REST
endpoints, the upload-then-build deployment protocol, how a marketplace
database is provisioned and connected, and the order a launch runs in. This
module owns the OpenHuman side: where the credential comes from, which
workspace the agent deploys from, and whether the tools are offered at all.

The whole domain is one file, [`mod.rs`](./mod.rs), around a single type, `Account`.

## How it works

At tool-registry build time, `tools::ops` (in [`src/tools/ops.rs`](../tools/ops.rs)) asks this
module for an account. If one resolves, the account's ten tools are appended
to the agent's tool list. If none resolves, nothing is registered.

```text
 tools::ops (registry build, #[cfg(feature = "hosting")])
     |
     v
 Account::from_config(&Config)
     |
     |-- [hosting].enabled == false ----------------> Ok(None)  (no tools)
     |
     |-- ProviderKind::from_str(provider)  (bad slug -> Err, logged at warn)
     |
     |-- [hosting].api_key set?
     |      yes -> Credentials::new(key) [+ with_team(team)]
     |      no  -> provider.credentials_from_env()
     |                 not found ---------------------> Ok(None)  (no tools)
     |
     v
 tinyhosts::connect(provider, credentials) -> Arc<dyn Host>
     |
     v
 Account { host, workspace_dir }
     |
     v
 account.tools() = tinyhosts::tools::hosting_tools(&host, &workspace_dir)
```

`from_config` separates "absent" from "wrong". Hosting switched off, or
switched on with no key anywhere, is the ordinary state of a host nobody has
connected a provider to, so it returns `Ok(None)` and logs at `debug`. An
unknown provider slug, a blank configured key, or a client that fails to build
is a misconfiguration: it returns an error, which `tools::ops` logs at `warn`
and then skips. Startup does not fail, since nothing else in the process
depends on hosting.

The reason absent credentials mean absent tools: a tool that is present and
cannot work is worse than one that is missing, because a model will retry it.

Embedders that hold their own credential use `Account::connect(provider,
api_key, team, workspace_dir)` instead. It takes the provider slug and key as
plain strings, so a host (OpenCompany keeps one hosting key per company in that
company's secret store) can reach the tools without naming `tinyhosts` in its
own dependency graph.

Configuration lives in `HostingConfig` ([`src/config/schema/hosting.rs`](../config/schema/hosting.rs)):
`enabled`, `provider` (default `vercel`), `api_key` (empty means "read the
provider's environment variable"), and `team` (empty means the personal
account). Its `Debug` impl redacts the key.

## Layout

| Path | What it does |
| --- | --- |
| `mod.rs` | `Account`: `from_config` credential resolution, `connect` for embedders, the shared `Arc<dyn Host>`, `tools()`, and the `resolve_in_workspace` re-export. |

## Key types and entry points

- `Account` (`mod.rs`) is one hosting account plus the workspace it deploys
  from. Its `Debug` prints the provider slug and workspace, never the client.
- `Account::from_config` resolves an account from `[hosting]` and the
  environment, as described above.
- `Account::connect` builds an account from credentials an embedder resolved.
- `Account::tools` returns the ten `hosting_*` tools as
  `Vec<Box<dyn tinytools::Tool>>`.
- `resolve_in_workspace` is re-exported from `tinyhosts::tools`. It decides
  which directory an agent may deploy.

## Agent tools

All ten are implemented in [`vendor/tinyhosts/src/tools/`](../../../../vendor/tinyhosts/src/tools/). Tools with an
external effect return `true` from `Tool::external_effect`, which the agent
harness reads to route the call through approval.

| Tool | Effect |
| --- | --- |
| `hosting_launch_site` | Deploys a workspace directory as a live site, optionally provisioning a database and wiring it in, setting environment variables, and attaching domains. External effect. |
| `hosting_deployment_status` | Whether a build has finished. Read-only. |
| `hosting_list_deployments` | A site's recent deployments, newest first, with status and target. Read-only. |
| `hosting_deployment_logs` | A deployment's build and runtime log events, oldest first, trimmed to the most recent. Read-only. |
| `hosting_rollback` | Points production back at an earlier deployment that already built. External effect. |
| `hosting_list_sites` | The sites on the account. Read-only. |
| `hosting_set_env` | Sets environment variables on an existing site. External effect. |
| `hosting_add_domain` | Attaches a custom domain. External effect. |
| `hosting_domain_status` | Whether a site's domains are verified and serving. Read-only. |
| `hosting_analytics` | Traffic over the last N days. Read-only. |

### Rollback, and why there is no separate promote

`Host::promote` covers both: a rollback is a promote of an older deployment,
and the crate models it once. The tool is named for the reason an agent
reaches for it, which is recovering a site a deploy broke.

`hosting_rollback` reads the deployment before promoting it and refuses one
that did not finish building. `hosting_list_deployments` returns failed and
still-building deployments too, because they are the history an agent is
reading, so the id an agent picks is not necessarily one that can serve
traffic. Promoting a failed build would take the site down during an attempt
to bring it back up.

The tool does not check that the deployment belongs to the named site. A
deployment is looked up by id alone and the provider's response may omit the
project name, so that check would refuse legitimate rollbacks. The provider
enforces it.

## Boundaries

- Provider behavior (endpoints, deployment states, database provisioning,
  launch ordering, the tool implementations and their argument validation)
  belongs to `tinyhosts` ([`vendor/tinyhosts`](../../../../vendor/tinyhosts/), upstream
  `tinyhumansai/tinyhosts`). Nothing in this module knows the word
  `readyState`, and nothing in `tinyhosts` knows what a workspace is.
- Approval routing belongs to the agent harness, via `external_effect`.
- There are no RPC controllers and no events: no `schemas.rs`, no `bus.rs`.

## Gotchas

- Two gates both have to pass. The `hosting` Cargo feature (default-off in the
  contributor build, on in `scripts/ci/product-features.txt`) decides whether
  `openhuman::hosting` compiles at all. A resolving credential decides whether
  the tools register at runtime.
- This process never reads a managed database's secret. The provider injects
  the connection string into the site's environment; OpenHuman learns only the
  variable names. That is why `hosting_launch_site` reports `DATABASE_URL`
  rather than a URL.
- `resolve_in_workspace` refuses absolute paths, `..` escapes, and
  non-directories. It is the only place that decides what may leave the
  machine, and a deployment uploads every byte under the directory it is given.
- The doc comment in `src/config/schema/hosting.rs` mentions
  `crate::hosting::credentials`, which does not exist. Credential resolution is
  `Account::from_config`.

## Tests

[`hosting_tests.rs`](./hosting_tests.rs) covers the seam only: account resolution from config and
the tool set handed back. The tools themselves, workspace containment, and the
rollback guard are tested in `tinyhosts` against a mock of the provider API.

```bash
cargo test -p openhuman --features hosting hosting::
```

## Further reading

- [Parent module README](../../README.md)
- [Hosting](../../../../gitbooks/features/hosting.md)
- [Cloud deploy](../../../../gitbooks/features/cloud-deploy.md)
- [tinyhosts](../../../../vendor/tinyhosts/README.md)
