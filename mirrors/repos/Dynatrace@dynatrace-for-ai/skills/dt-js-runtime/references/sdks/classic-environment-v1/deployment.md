# `deploymentClient`

OneAgent/ActiveGate installer downloads, orchestration, BOSH releases, and Lambda layers. Import:

```ts
import { deploymentClient } from "@dynatrace-sdk/client-classic-environment-v1";
```

## Installers

| Method | Purpose |
|---|---|
| `downloadLatestAgentInstaller` | Download latest OneAgent installer (by OS/type/arch/bitness/flavor). |
| `downloadAgentInstallerWithVersion` | Download a specific OneAgent installer version. |
| `getAgentInstallerAvailableVersions` | List available OneAgent installer versions. |
| `getAgentInstallerMetaInfo` | Get installer meta info. |
| `getAgentInstallerWithVersionChecksum` | Get checksum for an installer version. |
| `getAgentInstallerConnectionInfo` / `getAgentInstallerConnectionInfoEndpoints` | Connection info / endpoints. |
| `getAgentProcessModuleConfig` | Get process-module config. |
| `downloadLatestGatewayInstaller` | Download latest ActiveGate installer. |
| `downloadGatewayInstallerWithVersion` | Download a specific ActiveGate installer version. |
| `getActiveGateInstallerAvailableVersions` | List ActiveGate installer versions. |
| `getActiveGateInstallerConnectionInfo` | ActiveGate connection info. |
| `getGatewayInstallerMetaInfo` | ActiveGate installer meta info. |

## Orchestration, BOSH, images, Lambda

| Method | Purpose |
|---|---|
| `downloadLatestAgentOrchestration` / `downloadAgentOrchestrationWithVersion` | Download agent orchestration. |
| `downloadLatestAgentOrchestrationSignature` / `downloadAgentOrchestrationSignatureWithVersion` | Orchestration signatures. |
| `downloadBoshReleaseWithVersion` / `getBoshReleaseAvailableVersions` / `getBoshReleaseChecksum` | BOSH release downloads/info. |
| `getLatestAgentImage` / `getLatestActiveGateImage` | Latest container images. |
| `getLambdaLayerBuildUnits` / `getLatestLambdaBuildUnits` | AWS Lambda layer build units. |
| `getPublicCommunicationAddresses` | Public communication addresses. |
