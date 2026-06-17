# Classic Environment v2 — Types & Enums

This SDK has a very large type/enum surface (hundreds of exports). Rather than duplicate it all, this file groups the type families; for exact field definitions use the canonical reference:

Full types: https://developer.dynatrace.com/develop/sdks/client-classic-environment-v2/#types
Full enums: https://developer.dynatrace.com/develop/sdks/client-classic-environment-v2/#enums

## Type families (by domain)

- **Access tokens** — `ApiToken`, `ApiTokenCreate`, `ApiTokenCreated`, `ApiTokenList`, `ApiTokenSecret`, `ApiTokenUpdate`, `ActiveGateToken*`, `AgentConnectionToken`, `TenantToken*`.
- **ActiveGates** — `ActiveGate`, `ActiveGateList`, `ActiveGateGroup(s)`, `ActiveGateAutoUpdateConfig`, `ActiveGateGlobalAutoUpdateConfig`, `UpdateJob`, `UpdateJobList`.
- **Credential vault** — `Credentials`, `CredentialsList`, `CredentialsResponseElement`, `CredentialsDetailsList`, `*Credentials` (AWS/Azure/Hashicorp/CyberArk/Certificate/Token/UserPassword/SNMPV3), `ExternalVault(Config)`.
- **Settings** — `SettingsObject`, `SettingsObjectCreate`, `SettingsObjectUpdate`, `SettingsObjectResponse`, `ObjectsList`, `EffectiveSettingsValue(sList)`, `SchemaDefinitionRestDto*`, `SchemaStub`, `AccessorPermissions(List)`, `EffectivePermission`, `TransferOwnershipRequest`.
- **Events** — `Event`, `EventList`, `EventIngest`, `EventIngestResult(s)`, `EventType(List)`, `EventProperty`, `CloudEvent`, `BizEventIngestResult`.
- **Metrics** — `MetricDescriptor(Collection)`, `MetricData`, `MetricSeries(Collection)`, `MetricDto`, `Unit`, `UnitList`, `UnitConversionResult`.
- **Entities** — `Entity`, `EntitiesList`, `EntityType(List)`, `EntityId`, `CustomDeviceCreation`, `METag`, `AddEntityTag(s)`, `MonitoredEntityStates`.
- **Problems** — `Problem`, `Problems`, `Comment`, `CommentsList`, `ProblemCloseResult`.
- **Security** — `SecurityProblem(List/Details)`, `Attack(List)`, `RemediationItem(List)`, `RiskAssessment*`, `Vulnerability`, `VulnerableFunction(s)`, `DavisSecurityAdvice(List)`.
- **Synthetic** — `SyntheticLocation(s)`, `PrivateSyntheticLocation`, `Node(s)`, `SyntheticBrowserMonitor*`, `SyntheticMultiProtocolMonitor*`, `SyntheticOnDemand*`, monitor step/config DTOs.
- **SLO** — `SLO`, `SLOs`, `SloBurnRate(Config)`, `BurnRateAlert`, `StatusAlert`.
- **Network zones** — `NetworkZone(List)`, `NetworkZoneSettings`, `NetworkZoneConnectionStatistics`.
- **Extensions** — `Extension(List/Info)`, `ExtensionMonitoringConfiguration(sList)`, `MonitoringConfigurationDto`, `SchemaFiles`, `ExtensionEventDto`, UI customization DTOs (`Ui*Customization`).
- **Audit / releases / RUM** — `AuditLog(Entry)`, `Release(s)`, `ReleaseInstance`, `JavaScriptAgentSettingsDto`.
- **Errors / common** — `Error`, `ErrorEnvelope`, `ConstraintViolation`, `ConfigurationMetadata`, `ModificationInfo`, `Success(Envelope)`.

## Enums

Hundreds of enums exist, mostly query-parameter and status discriminators (e.g. `ProblemStatus`, `ProblemSeverityLevel`, `SecurityProblemStatus`, `AttackState`, `SLOStatus`, `ApiTokenScopesItem`, `ActiveGateType`, `MetricValueTypeType`, `SyntheticLocationStatus`, `AuditLogEntryEventType`). See the canonical enums page linked above for the full list and values.
