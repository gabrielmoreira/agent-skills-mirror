# Classic Environment v1 — Types & Enums

Full field definitions: https://developer.dynatrace.com/develop/sdks/client-classic-environment-v1/#types
Full enum definitions (deprecated in favor of literal values): https://developer.dynatrace.com/develop/sdks/client-classic-environment-v1/#enums

## Deployment / installer types

`AgentInstallerMetaInfoDto`, `AgentInstallerVersions`, `AllAvailableVersions`, `ActiveGateInstallerVersions`, `ActiveGateConnectionInfo`, `ConnectionInfo`, `Address(es)`, `AgentProcessModuleConfigResponse`, `BoshReleaseAvailableVersions`, `BoshReleaseChecksum`, `OneAgentInstallerChecksum`, `GatewayInstallerMetaInfoDto`, `ImageDto`, `LambdaDto`, `LatestLambdaLayerNames`, `LatestLambdaLayersMetainfo`, `ModuleInfo`, `PluginInfo`.

## Host types

`Host`, `HostsListPage`, `HostAgentInfo`, `HostGroup`, `HostKubernetesLabels`, `HostFromRelationships`, `HostToRelationships`, `AgentPotentialProblem(sState)`, `ModuleInstance`, `PluginInstance`, `TechnologyInfo`.

## RUM / user-session types

`ManualApplication`, `ConfiguredVersions`, `UserSession`, `UserSessionUserAction`, `UserSessionEvents`, `UserSessionErrors`, `UserSessionSyntheticEvent`, `UsqlResultAsTable`, `UsqlResultAsTree`, `KeyPerformanceMetrics`.

## Synthetic types

`SyntheticMonitor(Update)`, `BrowserSyntheticMonitor(Update)`, `HttpSyntheticMonitor(Update)`, `Monitors`, `MonitorCollectionElement`, `Node(s)`, `NodeCollectionElement`, `OutageHandlingPolicy`, `GlobalOutagePolicy`, `LocalOutagePolicy`, `LoadingTimeThreshold(sPolicyDto)`.

## Common / property types

`ClusterId`, `ClusterVersion`, `ManagementZone`, `TagInfo`, `TagWithSourceInfo`, `EntityIdDto`, `EntityShortRepresentation`, `EventDto`, `Error`, `ErrorEnvelope`, `ConstraintViolation`, and property wrappers (`StringProperty`, `LongProperty`, `DoubleProperty`, `DateProperty`, `SectionProperty`).

## Enums

> All enums in this SDK are deprecated in favor of literal string values.

Mostly installer download discriminators (OS type, architecture, bitness, flavor, installer type, orchestration type) and host query filters (`GetHostsWithSpecificAgentsQuery*`), plus host attribute enums (`HostOsType`, `HostCloudType`, `HostMonitoringMode`, `HostBitness`, …), synthetic monitor enums (`SyntheticMonitorType`, …), and user-session enums (`UserSessionUserType`, `UserSessionUserActionType`, …). See the canonical enums page for the full list.
