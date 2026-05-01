# Workflow: Spark Session Startup Delays

## Table of Contents

- [Diagnosis](#diagnosis)
- [Resolution Steps](#resolution-steps)
- [Starter Pool Behavior](#starter-pool-behavior)
- [Network Security Impact](#network-security-impact)
- [Library Dependencies](#library-dependencies)

## Diagnosis

1. Confirm the symptom: first query after idle period takes 2-5 minutes, subsequent queries
   respond in seconds.
2. Check workspace networking configuration:
   - Navigate to **Fabric Admin Portal** > **Workspace Settings** > **Networking**.
   - If **Private Links** or **Managed VNets** are enabled, Starter Pools are not supported.
3. Check regional Starter Pool availability:
   - During peak hours, regional pools may be exhausted.
   - Fabric spins up a new cluster (2-5 minutes).

## Resolution Steps

### Step 1: Verify Starter Pool Eligibility

```powershell
# Check workspace settings via REST API
$workspaceId = "<your-workspace-id>"
$token = (Get-AzAccessToken -ResourceUrl "https://api.fabric.microsoft.com").Token
$headers = @{ Authorization = "Bearer $token" }

$workspace = Invoke-RestMethod `
    -Uri "https://api.fabric.microsoft.com/v1/workspaces/$workspaceId" `
    -Headers $headers `
    -Method Get

Write-Host "Workspace: $($workspace.displayName)"
Write-Host "Capacity ID: $($workspace.capacityId)"
```

### Step 2: Reduce Library Dependency Overhead

Custom libraries add 30 seconds to 5 minutes to session startup.

**Mitigation strategies:**
- Pin library versions to avoid resolution overhead.
- Use Fabric Environments to pre-install common libraries.
- Minimize the number of custom packages.
- Prefer built-in libraries where possible.

### Step 3: Configure Environment for Faster Startup

1. Navigate to **Workspace** > **Environments**.
2. Create or edit an environment.
3. Under **Libraries**, add only essential packages.
4. Under **Spark Properties**, set:
   ```
   spark.ms.autotune.enabled = true
   ```
5. Publish the environment and attach it to the notebook or job definition.

### Step 4: Consider Autoscale Billing

When Autoscale Billing is enabled, Spark jobs use dedicated serverless resources instead of
consuming from shared capacity. This can reduce contention-related startup delays.

## Starter Pool Behavior

Starter Pools are pre-warmed Spark clusters that Fabric maintains per region. Default sessions
with no custom libraries start in 5-10 seconds using these pools.

**Conditions that bypass Starter Pools:**
- Private Links enabled on workspace
- Managed VNet configured
- Regional pool exhaustion (high traffic)
- High Concurrency mode enabled

## Network Security Impact

When Private Links or Managed VNets are active:
- Every session requires on-demand cluster creation (2-5 minutes).
- Library installation adds another 30 seconds to 5 minutes on top.
- No workaround exists; this is by design for network isolation.

**Recommendation:** For agent workloads requiring low latency, evaluate whether Private
Links are necessary for the specific workspace hosting the Data Agent.

## Library Dependencies

| Scenario | Additional Startup Time |
|----------|------------------------|
| No custom libraries | 0 seconds (Starter Pool) |
| Few pip packages | 30-60 seconds |
| Complex conda environment | 2-5 minutes |
| Large custom wheels | 1-3 minutes |

**Best practice:** Create a dedicated Fabric Environment with pre-installed libraries and
attach it to all agent-related notebooks.
