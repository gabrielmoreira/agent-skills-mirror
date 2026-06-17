# Synthetic clients

Synthetic locations/nodes, network-availability monitors, and on-demand/HTTP executions. Import from `@dynatrace-sdk/client-classic-environment-v2`.

## `syntheticLocationsNodesAndConfigurationClient`

| Method | Purpose |
|---|---|
| `getLocations` / `getLocation` | List / get synthetic locations. |
| `addLocation` / `updateLocation` / `removeLocation` | Manage private locations. |
| `getLocationsStatus` / `updateLocationsStatus` | Get/set public location status. |
| `getConfiguration` / `updateConfiguration` | Get/update synthetic configuration. |
| `getNodes` / `getNode` | List / get synthetic nodes. |
| `getLocationDeploymentApplyCommands` / `…DeleteCommands` / `getLocationDeploymentYaml` | Private location deployment helpers. |
| `getMetricAdapterDeploymentApplyCommands` / `…DeleteCommands` / `getMetricAdapterDeploymentYaml` | Metric adapter deployment helpers. |

## `syntheticNetworkAvailabilityMonitorsClient`

| Method | Purpose |
|---|---|
| `getMonitors` / `getMonitor` | List / get network-availability monitors. |
| `createMonitor` / `updateMonitor` / `deleteMonitor` | Manage monitors. |

## `syntheticOnDemandMonitorExecutionsClient`

| Method | Purpose |
|---|---|
| `execute` | Trigger on-demand monitor execution(s). |
| `rerun` | Re-run an execution. |
| `getExecutions` / `getExecution` | List / get executions. |
| `getBatch` | Get an execution batch status. |
| `getExecutionFullReport` | Get the full report of an execution. |

## `syntheticHttpMonitorExecutionsClient`

| Method | Purpose |
|---|---|
| `getExecutionResult` | Get the result of an HTTP monitor execution. |
