---
name: devops-specialist
description: "Deep domain knowledge for DevOps — Azure DevOps pipeline templates, Docker multi-stage builds, Helm/K8s deployment patterns, environment promotion flow, Confix configuration management, and pipeline troubleshooting. Triggers on: azure-pipelines YAML, Dockerfile, Helm values.yaml, k8s-deployment, Confix decrypt, ACR push, environment promotion A/UAT/PAV, release pipeline, pipeline template, HelmChartVersion, k8s-vars, service connection, pod CrashLoopBackOff, ImagePullBackOff."
---

# DevOps Specialist

Domain knowledge for CI/CD pipelines, Docker builds, Helm/K8s deployments, and environment promotion.

> **Scope**: Project-specific DevOps patterns only. For general DevOps workflow and investigation → `DevOps Expert` agent.

## Azure DevOps Organization

<!-- TODO: Replace with your actual Azure DevOps project names and purposes -->
| Project | Purpose |
|---|---|
| **Main** | Main development — Backend services, Pipeline-Templates |
| **ReleaseManagement** | Change/Test/Release Management — wikis, release process docs, Developer-Handbook |
| **IaC** | Infrastructure as Code — Terraform modules, Azure resource provisioning |

Key repos in the **Main** project:
- **My-Backend** — main monorepo for all domain services
- **Pipeline-Templates** — shared pipeline templates (`Deployment/k8s-deployment.yaml`, variable templates)

## Branching Strategy

GitHub Flow:
- `master` is always deployable
- Feature branches from `master`, PRs trigger validation (`test-pr` + `sonar-pr`)
- Tags on `master` trigger release pipelines
- Preview tags on feature branches deploy to A environment

## Pipeline Architecture

### Pipeline Types

| Pipeline | Trigger | Purpose |
|---|---|---|
| **test-pr** | PR to master | Unit/integration tests, build validation |
| **sonar-pr** | PR to master | SonarQube code quality analysis |
| **release** | Tag on master | Build Docker images, push to ACR, deploy |

### Repository Pipeline Structure

```
.devops/
├── azure-pipelines.release-<Service>.yml
├── azure-pipelines.sonar-pr.yml
├── azure-pipelines.test-pr.yml
└── templates/
    ├── template.detect-changes.yml
    ├── template.release.yml
    ├── template.sonar-pr.yml
    └── template.test-pr.yml
```

### Shared Templates (Pipeline-Templates)

K8s Deployment Template (`Deployment/k8s-deployment.yaml`) key parameters:

| Parameter | Purpose |
|---|---|
| `DockerImageName` | Docker image name |
| `HelmReleaseName` | Helm release name in cluster |
| `HelmChartName` | Defaults to `deployment-ng` (<!-- TODO: replace with your chart name -->) |
| `HelmChartVersion` | Chart version (e.g., `12.12.0`) |
| `Environment` | Target: A, A2, UAT, UAT2, PAV, PAV2, DEV001 |
| `Namespace` | Kubernetes namespace |
| `KubernetesFilePath` | Path to K8s values (default: `app/k8s`) |

Agent pool: `scm-vmss-agentpool-001` (fallback: `ubuntu-latest`)

### Environment Variable Templates

Per-environment variables from `k8s-vars-{env}.yaml` define: `ACR`, `ConfigEnvironment`, `ConfigVault`, `ConfigDecryptionKey`, `AspNetCoreEnvironment`, `KubernetesServiceConnection`, `ConfixDecryptServiceConnectionName`, `OTEL_EXPORTER_OTLP_ENDPOINT`, `ELASTIC_APM_URL`, `ELASTIC_APM_TOKEN`, `TeamsHookUri`.

## Environments & Promotion

| Environment | Purpose | Deployment | Approval |
|---|---|---|---|
| **A / A2** | Development | Auto on preview tags / Manual | None |
| **UAT / UAT2** | Business testing | Tag-triggered / Manual | May require approval |
| **PAV / PAV2** | Production | Tag-triggered / Manual | Approval gate required |
| **DEV001** | Isolated sandbox | Manual | None |

Promotion flow: `A` → `UAT` → `PAV`

## Docker & Container Build

### Multi-Stage Dockerfile Pattern

```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 8080

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["src/<Service>/Host/Host.csproj", "src/<Service>/Host/"]
RUN dotnet restore "src/<Service>/Host/Host.csproj"
COPY . .
WORKDIR "/src/src/<Service>/Host"
RUN dotnet build "Host.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "Host.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "Host.dll"]
```

### Image Structure per Service

```
docker/<service-name>/
├── Dockerfile
└── k8s/
    ├── A/
    │   ├── values.yaml
    │   └── appsettings.json    # Confix-encrypted
    ├── UAT/
    └── PAV/
```

### ACR

- Images via `$(ACR)` variable, tag = `$(Build.SourceBranchName)` (git tag, SemVer)
- Helm chart registry: `$(HelmRepoName).azurecr.io` (OCI-based)

## Helm Deployment Flow

1. Download Docker artifact from build stage
2. Copy K8s manifests + values.yaml
3. **Confix Decrypt** — `dotnet confix decrypt` via Azure CLI service connection
4. Split `BffContainer` from `appsettings.json` → `appsettings.bff.json`
5. Helm login: `helm registry login $(HelmRepoName).azurecr.io`
6. Helm pull: `oci://$(HelmRepoName).azurecr.io/deployment-ng`
7. **Helm upgrade** `--atomic --timeout=600s --create-namespace` with environment values
8. Teams notification

### Helm Values Set During Deployment

```
image.name, image.repository=$(ACR), image.tag=$(Build.SourceBranchName)
env.DEPLOYMENT_ENVIRONMENT, env.DEPLOYMENT_VAULT, env.ASPNETCORE_ENVIRONMENT
env.OTEL_EXPORTER_OTLP_ENDPOINT, env.REMOTE_CONFIGURATION_URL
envSecrets.DEPLOYMENT_DECRYPTIONKEY, envSecrets.DEPLOYMENT_SHAREDSECRET
envSecrets.REMOTE_CONFIGURATION_TOKEN
```

### Health Probes

All services: `/_health/live` (liveness), `/_health/ready` (readiness)

## Versioning & Release

- SemVer: `MAJOR.MINOR.PATCH`, preview: `MAJOR.MINOR.PATCH-preview.N`
- Release tags on `master` → full deployment pipeline
- Flow: feature branch → PR → merge → release tag → A (auto) → UAT (approval) → PAV (approval)

## Configuration Management

### Confix

Encrypts `appsettings.json` at rest. Pipeline decrypts using `$(ConfixDecryptServiceConnectionName)`.

### Azure Key Vault

Secrets via `DEPLOYMENT_VAULT` + `DEPLOYMENT_DECRYPTIONKEY`. Managed Identity in production.

## Infrastructure as Code

- **Terraform** for Azure resources (I_IaC project)
- **Helm** for K8s packages
- **ARM Templates** for legacy resources
- CCOE manages foundational infra, quarterly compliance reviews

## Observability

| Component | Purpose |
|---|---|
| **OpenTelemetry** | Distributed tracing, metrics |
| **Elastic APM** | Performance monitoring |
| **Structured logging** | ILogger + Serilog → Elasticsearch |
| **Health checks** | K8s liveness/readiness probes |

## Pipeline Troubleshooting

### Build Failures

| Symptom | Likely Cause | Resolution |
|---|---|---|
| `dotnet restore` fails | NuGet feed auth, version mismatch | Check `nuget.config`, `Directory.Packages.props` |
| Docker build fails | Missing COPY files, SDK mismatch | Check paths, `global.json` |
| Test failures | Flaky tests, missing infra | Run locally, check Squadron containers |

### Deployment Failures

| Symptom | Likely Cause | Resolution |
|---|---|---|
| Helm upgrade fails | Chart not found, values.yaml error | Verify `HelmChartVersion`, validate YAML |
| Confix decrypt fails | Service connection permissions | Check `ConfixDecryptServiceConnectionName` |
| CrashLoopBackOff | Config error, missing secrets | `kubectl logs`, verify appsettings |
| ImagePullBackOff | ACR auth, tag not found | Verify ACR creds, confirm image push |
| Timeout (600s) | Pod not ready, low resources | Increase resources in values.yaml |

### Pipeline Permission Issues

| Symptom | Likely Cause | Resolution |
|---|---|---|
| `Authorization failed` | Service connection expired | Renew ADO service connections |
| Pipeline not triggered | Tag trigger mismatch | Verify trigger in pipeline YAML |
| Template not found | Repo resource ref wrong | Check `resources.repositories` branch |

### Diagnostic Commands

```bash
kubectl get pods -n <ns> -l app=<svc>
kubectl logs -n <ns> -l app=<svc> --tail=100
kubectl describe pod <pod> -n <ns>
kubectl rollout status deployment/<svc> -n <ns>
kubectl rollout undo deployment/<svc> -n <ns>
helm list -n <ns>
helm history <release> -n <ns>
```

## Key File Locations

| File | Purpose |
|---|---|
| `.devops/azure-pipelines.release-*.yml` | Release pipelines per service |
| `.devops/azure-pipelines.test-pr.yml` | PR test pipeline |
| `.devops/templates/template.*.yml` | Shared pipeline templates |
| `docker/<service>/Dockerfile` | Docker build |
| `docker/<service>/k8s/{A,UAT,PAV}/values.yaml` | Helm values per environment |
| `Directory.Build.props` | Central MSBuild properties |
| `Directory.Packages.props` | Central NuGet package versions |
| `global.json` | .NET SDK version pinning |

## Key Pipeline Variables

| Variable | Source | Purpose |
|---|---|---|
| `$(ACR)` | Variable template | Azure Container Registry URL |
| `$(ConfigEnvironment)` | Variable template | Target environment name |
| `$(ConfigVault)` | Variable template | Key Vault name |
| `$(KubernetesServiceConnection)` | Variable template | K8s service connection |
| `$(ConfixDecryptServiceConnectionName)` | Variable template | Confix decrypt service connection |
| `$(HelmRepoName)` | Variable template | Helm OCI registry name |
| `$(TeamsHookUri)` | Variable template | Teams webhook |
| `$(Build.SourceBranchName)` | Built-in | Git tag / branch name (image tag) |
