---
name: openapi-client-generation
description: Reproducible .NET OpenAPI client generation with provenance, safe base-URL ownership, fake-transport tests, and qualified trimming guidance
---

When generating .NET HTTP clients from OpenAPI, treat the description,
enrichment, generator, and runtime as separately versioned inputs. Regenerate;
never repair generated source by hand.

# Reproducible .NET OpenAPI Clients

## Keep three boundaries

1. **Original description** - preserve the downloaded or producer-owned OpenAPI
   document byte-for-byte. Record its origin, version or commit, retrieval date,
   and SHA-256. Do not add local fixes to this file.
2. **Enriched description** - apply reviewed, deterministic local changes such
   as a stable `operationId`, missing schema metadata, or the intended default
   `servers` URL. This checked file is the generator input. Keep the diff from
   the original small enough to audit.
3. **Generated output** - recreate it only from the enriched description,
   pinned generator, and checked command/config. Generated files are build
   artifacts, not a second place to encode fixes.

If the producer changes the original, first update its provenance, then reapply
or revise enrichment, and only then inspect a clean generated diff. Mixing all
three changes makes contract drift indistinguishable from generator churn.

## Pin and record every effective input

Use a repository-local .NET tool manifest rather than a global tool:

```powershell
dotnet tool restore --tool-manifest .\.config\dotnet-tools.json `
  --add-source https://api.nuget.org/v3/index.json
dotnet tool run kiota -- `
  generate --language CSharp --class-name WidgetApiClient `
  --namespace-name OpenApiClientFixture.Generated `
  --openapi .\openapi.enriched.yaml --output $generated `
  --exclude-backward-compatible
```

Check in the manifest and generator config/command, but write generated output
to a disposable build directory. Beside each generated tree, emit provenance
containing:

- original and enriched input paths and SHA-256 hashes;
- generator name and exact version;
- target language, class, namespace, filters, and compatibility flags;
- normalized regeneration command;
- SDK/runtime and generated-client runtime package versions.

Run `dotnet tool run` from the manifest directory; unlike `tool restore`, that
command discovers the manifest from the working directory and has no
`--tool-manifest` option.

Run generation twice into clean directories and compare relative paths plus
content hashes. A clean second result proves deterministic regeneration for
those inputs; it does not prove that a later generator version is diff-free.
Choose a new output directory for each run. Never point a cleanup-enabled
generator at an existing user/project directory. The wrapper rejects an existing
output and reparse-point traversal rather than guessing ownership.

The fixture in `examples/` exercises this workflow:

```powershell
$example = Resolve-Path .\examples
$scratch = 'C:\Temp\OpenApiLab' # existing, user-owned, non-reparse directory
& "$example\Test-Fixture.ps1" -ScratchRoot $scratch `
  -TrimmedRuntimeIdentifier win-x64 -KeepArtifacts
```

`Test-Fixture.ps1` restores only the pinned local tool and package, generates
twice, compares trees, compiles the generated client, sends through an in-memory
fake `HttpMessageHandler`, optionally publishes/runs one trimmed RID, and
allocates a unique child beneath `ScratchRoot`. Successful runs remove only that
child unless `-KeepArtifacts` is set; failed runs retain it for diagnosis. The
caller-selected parent is never deleted. Dependency restoration uses the
configured/public NuGet sources and can need network access; generated API calls
use only fake transport. Do not suppress audit/restore failures to claim success.
Binlogs are retained with the artifacts; review them before sharing.

The provenance records the installed runtime candidate, not proof that it ran;
the executable prints its actual `Environment.Version`. Framework roll-forward
or deployment settings can select a different runtime.

## Choose a client generator, not a server generator

**Kiota `generate`** emits client-side request builders and models over Kiota
request-adapter abstractions. It does not generate ASP.NET controllers or host
an API. The application selects concrete authentication, transport, and
serialization packages; `Microsoft.Kiota.Bundle` is the convenient default set.

**NSwag client generation** is a valid alternative when its generated
`HttpClient`-oriented shape and serializer options fit the application. Pin
`NSwag.ConsoleCore` and use its C# client command/config. Do not confuse that
with NSwag's controller/server generation or ASP.NET middleware that publishes
an OpenAPI document. Verify command names and switches against the pinned
NSwag help because its runtime selection and settings vary by release.

Prefer one maintained generator stack per client. Comparing Kiota and NSwag can
inform a one-time choice, but maintaining both outputs doubles drift, runtime,
and test obligations.

## Make one component own the base URL

An OpenAPI `servers` URL is generation input, not necessarily deployment
configuration. In the tested Kiota output, the generated client constructor
uses that URL only when `IRequestAdapter.BaseUrl` is empty. Configure the
adapter first:

```csharp
var adapter = new HttpClientRequestAdapter(authProvider, httpClient: httpClient);
adapter.BaseUrl = options.ApiBaseUrl; // the application is the sole owner
var client = new WidgetApiClient(adapter); // preserves that value
```

Choose one owner:

- For a fixed public service, let the generated constructor own the URL.
- For environment-specific deployment, assign validated application
  configuration before constructing the generated client.
- Do not also treat `HttpClient.BaseAddress`, middleware, and per-call mutation
  as competing owners.

A later assignment overwrites the adapter property and the tested request URI
uses that later URL. That single-threaded last-writer behavior is not evidence
of a race. Real concurrency trouble begins when requests or client constructors
mutate a shared adapter's `BaseUrl` while other requests use it. Give clients
requiring different origins separate, stable adapters; never switch a shared
adapter per request.

Test the resolved request URI, not just the property. The fixture proves that a
preconstruction value produces
`https://configured.example.test/v3/widgets/widget-1`. It then changes the
adapter property after constructing another client and proves that the later
assignment produces
`https://later-assignment.example.test/v4/widgets/widget-2`, all without
network access. This verifies order; it does not recommend per-request mutation.

## Test contract and regeneration behavior

Use a fake `HttpMessageHandler` or generator-native transport abstraction to
capture method, URI, headers, and body. Return schema-valid responses so the
real generated deserializer runs. Cover:

- representative path and query expansion, escaping, and nullable fields;
- configured base URL and absence of accidental double path prefixes;
- expected media type and error mapping;
- cancellation and disposal for streams or response bodies;
- regeneration idempotence and a reviewed diff after input/tool updates.

Reserved `.test` hosts and fictional data keep a failed fake from reaching a
production service. The fixture performs no DNS or HTTP network request.

## Qualify serializers, trimming, and Native AOT

Do not label a generator "AOT compatible" in isolation. Compatibility is the
combination of:

- generated source from an exact generator version and flags;
- target framework and RID;
- request adapter and authentication implementation;
- every registered serialization format and its exact package version;
- application code, interceptors, and error models.

For C#, Kiota's JSON package currently relies on `System.Text.Json`, while the
bundle also registers other format implementations. That fact alone does not
prove the selected Kiota packages use an application `JsonSerializerContext`
or are warning-free under trimming. Likewise, general `System.Text.Json`
source-generation support does not certify a generated client.

Before claiming trimming or Native AOT support, publish the actual application
for every supported RID with trim/AOT analyzers enabled and warnings treated as
errors, then execute generated-client smoke tests through fake transport on the
published binary. Repeat after generator, runtime-package, TFM, serializer, or
auth changes. If a combination has not passed, state **not validated** rather
than extrapolating from a different serializer or runtime.

This fixture validates Kiota 1.35.0, its recommended
`Microsoft.Kiota.Bundle` 2.0.0, and
`net10.0` on .NET SDK 10.0.401 and Microsoft.NETCore.App 10.0.12. Its tested
`win-x64` combination passes both a JIT run and a self-contained trimmed
publish/run with linker warnings treated as errors. That is not a blanket claim
for other RIDs, serializers, auth packages, or versions. Native AOT remains
**not validated** by this fixture.

During validation, NuGet vulnerability-data retrieval emitted `NU1900` because
the feed was unavailable. The strict fixture command fails on that condition.
Separate runtime diagnostics kept that warning visible while exercising the
JIT/trimmed binaries; those runs are **not** evidence of a completed vulnerability
audit. Restore feed availability and rerun the strict command for a complete
validation result.

## Update discipline

1. Update and hash the original description.
2. Review the original-to-enriched diff.
3. Update one pinned generator or runtime dependency at a time.
4. Run clean generation twice and compare.
5. Review generated API surface and behavior through fake transport.
6. Build/publish every claimed runtime mode.
7. Commit inputs, provenance mechanism, and intentional generated diff - never
   manual edits inside generated files.

Useful first-party references:

- [Kiota .NET quickstart](https://learn.microsoft.com/openapi/kiota/quickstarts/dotnet)
- [Kiota dependency selection](https://learn.microsoft.com/openapi/kiota/dependencies)
- [Kiota abstractions](https://learn.microsoft.com/openapi/kiota/abstractions)
- [System.Text.Json source generation](https://learn.microsoft.com/dotnet/standard/serialization/system-text-json/source-generation)
- [.NET trimming guidance](https://learn.microsoft.com/dotnet/core/deploying/trimming/prepare-libraries-for-trimming)
- [NSwag with ASP.NET Core](https://learn.microsoft.com/aspnet/core/tutorials/getting-started-with-nswag)
