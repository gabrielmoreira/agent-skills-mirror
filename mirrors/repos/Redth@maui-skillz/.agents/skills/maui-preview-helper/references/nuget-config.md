# NuGet.config

Wire the workspace up so restore pulls the preview MAUI packages from the **local source**
you staged, plus whatever remote feeds the target release needs — and nothing that would let
a stale nuget.org copy win.

## Where the file goes

- **Workspace root** (next to the `.sln` or the repo root) — a `NuGet.config` here applies to
  every project under it. This is almost always what you want for dogfooding.
- NuGet merges configs up the directory tree and from the machine-global config. To avoid a
  surprise feed injecting a different package version, add `<clear/>` inside `<packageSources>`
  so only the sources you list are used.

## Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <clear />
    <add key="local-maui-preview" value="/Users/you/NuGet/Source" />
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
    <add key="dotnet-public" value="https://pkgs.dev.azure.com/dnceng/public/_packaging/dotnet-public/nuget/v3/index.json" />
    <add key="dotnet11" value="https://pkgs.dev.azure.com/dnceng/public/_packaging/dotnet11/nuget/v3/index.json" />
  </packageSources>
</configuration>
```

- Put the **local source first** — it's a folder path (absolute; Windows e.g.
  `C:\NuGet\Source`). NuGet resolves a version from whichever source has it; keeping local
  first is clearest and avoids ambiguity when a CI version also happens to exist on a feed.
- Include the **`dotnet{N}` feed** matching the target major (9/10/11…) — that's where the
  preview SDK-band packages live. Pull N from the chosen `SdkVersion`.
- Add `dotnet-public` for shared build dependencies. Keep `nuget.org` for everything else.
- Only add feeds the release actually needs — don't paste in every feed from
  [release-lookup.md](release-lookup.md).

## Prefer editing over clobbering

If a `NuGet.config` already exists, **merge** — don't overwrite the user's feeds:

- Add the local `<add key=… />` line if missing.
- Add the `dotnet{N}` feed if the target version needs it.
- Leave existing sources/credentials alone.
- Consider `dotnet nuget list source` to see what's already effective before editing.

You can also manage sources with the CLI instead of hand-editing (operates on the nearest
config, or pass `--configfile`):

```bash
dotnet nuget add source ~/NuGet/Source --name local-maui-preview
dotnet nuget add source https://pkgs.dev.azure.com/dnceng/public/_packaging/dotnet11/nuget/v3/index.json --name dotnet11
```

## Private / authenticated feeds & credentials

Some preview bits live on **authenticated** AzDO feeds. The public `dnceng/public` feeds
(`dotnet-public`, `dotnet{N}`, and the `darc-pub-dotnet-*` darc feeds) are **anonymous** — no
auth. But an **internal** feed (e.g. on `devdiv`, or an internal `dnceng` feed) returns **401**
on restore and needs a credential.

### 1. Detect that a feed needs auth

A `dotnet restore` against an authenticated feed fails with something like:

```
error NU1301: Unable to load the service index for source https://pkgs.dev.azure.com/<org>/<project>/_packaging/<feed>/nuget/v3/index.json
    Response status code does not indicate success: 401 (Unauthorized).
```

The `401` and the feed URL are the signal. Parse the **org** and **project** out of the URL:
`https://pkgs.dev.azure.com/{org}/{project}/_packaging/{feed}/nuget/v3/index.json` (a
project-scoped feed has `{project}`; an **org-scoped** feed omits it:
`https://pkgs.dev.azure.com/{org}/_packaging/{feed}/...`). You need a token for **that org**.

### 2. Mint a token with `az` (fastest, no portal)

Azure DevOps accepts an AAD access token for its resource GUID
`499b84ac-1321-427f-aa17-267ca6975798`. If the user is `az login`'d to the tenant that owns the
org, mint one:

```bash
# Ensure logged into the right tenant (the one that owns {org}); if unsure:
az account show --query tenantId -o tsv
# az login --tenant <tenantId>   # if you must switch tenants

TOKEN=$(az account get-access-token \
  --resource 499b84ac-1321-427f-aa17-267ca6975798 \
  --query accessToken -o tsv)
```

- ⚠️ **AAD tokens are short-lived (~1 hour).** Fine for a one-shot restore/workload install;
  re-mint if a later step 401s. For something durable, use a PAT (step 4).
- The token is for the **org's tenant**. If the org lives in a different tenant than the user's
  default, `az login --tenant <tenantId>` (or `az account set --subscription`) first — a token
  from the wrong tenant still 401s.

### 3. Wire the token into NuGet

Use `<packageSourceCredentials>` — the source **key** must match the `<add key=…>` exactly
(NuGet replaces `.` and spaces in the key with `_x…_`-style names, so prefer a simple key like
`internal-feed`). Username can be anything for AAD/PAT auth:

```xml
<configuration>
  <packageSources>
    <add key="internal-feed" value="https://pkgs.dev.azure.com/<org>/<project>/_packaging/<feed>/nuget/v3/index.json" />
  </packageSources>
  <packageSourceCredentials>
    <internal-feed>
      <add key="Username" value="AzureDevOps" />
      <add key="ClearTextPassword" value="%NUGET_FEED_TOKEN%" />
    </internal-feed>
  </packageSourceCredentials>
</configuration>
```

- **Never write the token literally into a committed file.** Put it in an env var
  (`export NUGET_FEED_TOKEN=$TOKEN`) and reference it as `%NUGET_FEED_TOKEN%` — NuGet expands
  env vars in `ClearTextPassword`. Or keep credentials in a **user-level** config
  (`~/.nuget/NuGet/NuGet.Config`, `%APPDATA%\NuGet\NuGet.Config`) that never gets committed.
- For a `--source` override on a `dotnet workload`/`restore` command, the credentials still come
  from a `NuGet.config` on the credential chain — the CLI has no inline password flag. Wire the
  creds in a config first, then pass `--source <url>`.

Alternatively, the **Azure Artifacts Credential Provider** handles this without a static token —
set `VSS_NUGET_EXTERNAL_FEED_ENDPOINTS` to a JSON blob of `{endpoint, password}` and let it
inject creds at restore. The `az`-token approach above is simpler for a quick dogfood loop.

### 4. PAT fallback (durable / CI)

If AAD tokens are inconvenient (expiring mid-session, or the user prefers a portal flow), have
the user create a **Personal Access Token** in the feed's org:
`https://dev.azure.com/<org>/_usersSettings/tokens` → **New Token** → scope **Packaging: Read**
(Read & write only if pushing) → copy it. Use it exactly like the token in step 3
(`ClearTextPassword`). PATs last up to the chosen expiry; still never commit them.

> Ask the user before wiring any authenticated feed, confirm which **org/tenant** owns it, and
> prefer the shortest-lived credential that gets the job done.

## Verify

```bash
dotnet nuget list source                 # confirm the sources are registered/enabled
dotnet restore                            # should pull the preview MAUI version from local
```

If restore still grabs a wrong version, check for a higher-priority `NuGet.config` (machine
global, or a parent dir) overriding you, and confirm `<MauiVersion>` matches a package that
actually exists in the local source ([download-builds.md](download-builds.md)).

## Stop signals

- Once `dotnet restore` resolves the target MAUI version from the local source, you're done —
  don't keep adding feeds.
- Don't add a feed "just in case"; every extra source slows restore and risks a version clash.
