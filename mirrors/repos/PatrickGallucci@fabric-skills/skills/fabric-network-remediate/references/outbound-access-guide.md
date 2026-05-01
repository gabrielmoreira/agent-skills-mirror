# Outbound Access Protection Guide

## Table of Contents

- [Overview](#overview)
- [Impact on Library Management](#impact-on-library-management)
- [Installing Libraries in Secured Environments](#installing-libraries-in-secured-environments)
- [Admin API for Network Policy Auditing](#admin-api-for-network-policy-auditing)
- [Known Limitations](#known-limitations)

## Overview

Workspace Outbound Access Protection restricts all outbound connections from Fabric workspace items to external resources. When enabled, public repositories (PyPI, Conda) and external URLs are blocked. Only traffic to approved managed private endpoints is permitted.

This feature is configured at the workspace level and affects all Spark workloads, notebooks, and pipelines within the workspace.

## Impact on Library Management

When outbound access protection is enabled:

- **PyPI**: Blocked — `pip install` fails from notebooks and environments
- **Conda**: Blocked — Conda package installs fail
- **Azure Artifact Feed**: Not supported in Private Link or outbound access protection enabled workspaces
- **Custom libraries**: Must be uploaded manually as packages
- **Built-in libraries**: Unaffected — pre-installed with each Spark runtime

## Installing Libraries in Secured Environments

### Recommended: Upload Custom Packages

Since the environment cannot reach public repos, download packages externally and upload them.

#### Step 1: Prerequisites

- A compute resource with internet access (local machine, Azure VM, or WSL)
- Download the Fabric Runtime setup file from the [Fabric Runtime GitHub repo](https://github.com/microsoft/fabric-runtime) matching your Runtime version
- Remove Microsoft-hosted private libraries from the setup file:
  - `library-metadata-cooker`, `mmlspark`, `azureml-synapse`, `notebookutils`, `flt-python`, `synapse-jupyter-notebook`, `synapse-jupyter-proxy`, `azure-synapse-ml-predict`, `fsspec_wrapper`, `horovod`, `sqlanalyticsconnectorpy`, `synapseml`, `control-script`, `impulse-python-handler`

#### Step 2: Create Requirements File

```text
# requirements.txt
pandas>=2.0.0
scikit-learn>=1.3.0
plotly>=5.15.0
```

#### Step 3: Download Packages with Dependencies

```bash
# On a machine with internet access
pip download -r requirements.txt -d ./packages --platform manylinux2014_x86_64 --python-version 3.11 --only-binary=:all:
```

For packages that only provide source distributions:

```bash
pip download -r requirements.txt -d ./packages
```

#### Step 4: Build Virtual Environment (Optional Verification)

```bash
# Create a venv matching Fabric runtime
python3.11 -m venv fabric-test-env
source fabric-test-env/bin/activate
pip install --no-index --find-links=./packages -r requirements.txt
# Verify installations
pip list
deactivate
```

#### Step 5: Upload to Fabric Environment

1. Navigate to your Fabric workspace
2. Open the **Environment** item
3. Select the **Libraries** tab
4. Under **Custom libraries**, upload the `.whl` or `.tar.gz` files from the `./packages` directory
5. **Publish** the environment changes
6. Wait for the environment to rebuild (this may take several minutes)

#### Step 6: Attach Environment to Notebook

1. Open the notebook that needs the libraries
2. In the notebook toolbar, select the Environment dropdown
3. Choose the environment with the uploaded packages

### PowerShell: Bulk Package Download

```powershell
# Download packages for Fabric runtime
$requirementsPath = './requirements.txt'
$outputDir = './packages'

if (-not (Test-Path $outputDir)) { New-Item -ItemType Directory -Path $outputDir }

& pip download `
    -r $requirementsPath `
    -d $outputDir `
    --platform manylinux2014_x86_64 `
    --python-version 3.11 `
    --only-binary=:all:

Write-Host "Downloaded $(Get-ChildItem $outputDir | Measure-Object | Select-Object -ExpandProperty Count) packages to $outputDir"
```

## Admin API for Network Policy Auditing

Fabric administrators can monitor workspace network policies using the REST API:

**API**: `Workspaces - List Networking Communication Policies`
**Permission**: `Tenant.Read.All` or `Tenant.ReadWrite.All`
**Caller**: Fabric administrator or service principal

### What the API Returns

For each workspace with access protection enabled:

- **Workspace ID**: Unique identifier
- **Inbound policies**: Public access rules (Allow/Deny)
- **Outbound policies**: Public access rules, connection rules with allowed endpoints/workspaces, gateway rules, git access rules

### PowerShell Example

```powershell
# Get network policies across the tenant
$token = (Get-AzAccessToken -ResourceUrl 'https://api.fabric.microsoft.com').Token
$headers = @{ Authorization = "Bearer $token"; 'Content-Type' = 'application/json' }

$response = Invoke-RestMethod `
    -Uri 'https://api.fabric.microsoft.com/v1/admin/workspaces/networkingCommunicationPolicies' `
    -Headers $headers `
    -Method Get

$response.value | ForEach-Object {
    [PSCustomObject]@{
        WorkspaceId    = $_.workspaceId
        OutboundPolicy = $_.outboundPolicy.defaultAction
        InboundPolicy  = $_.inboundPolicy.defaultAction
    }
} | Format-Table -AutoSize
```

## Known Limitations

1. **Azure Artifact Feed** is not supported in workspaces with outbound access protection
2. **Spark views** are not supported in schema-enabled lakehouses with outbound protection — use Materialized Lake Views instead
3. **Cross-workspace Spark SQL** with schema-enabled lakehouses under outbound protection requires using non-schema lakehouses as a workaround
4. **Library installation time** increases because packages must be uploaded manually rather than pulled from repos
5. Environments from **different workspaces** cannot be attached if they have different network security settings — the session will fail to start
