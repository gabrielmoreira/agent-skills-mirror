# Session Startup remediate

## Table of Contents

- [How Fabric Spark Sessions Start](#how-fabric-spark-sessions-start)
- [Starter Pools vs Custom Pools](#starter-pools-vs-custom-pools)
- [Diagnosing Slow Startup](#diagnosing-slow-startup)
- [Fixes for Common Startup Issues](#fixes-for-common-startup-issues)

## How Fabric Spark Sessions Start

Fabric uses pre-warmed **Starter Pools** to deliver 5–10 second session startup for most
workloads. When a Starter Pool node is available, Fabric attaches a session instantly. When
not available, Fabric provisions a new cluster (2–5 minutes).

### Expected Startup Times

| Scenario | Typical Startup |
|----------|----------------|
| Default settings, no custom libraries | 5–10 seconds |
| Default + library dependencies | 5–10 sec + 30 sec–5 min (library install) |
| High regional traffic, no libraries | 2–5 minutes |
| High traffic + library dependencies | 2–5 min + 30 sec–5 min |
| Private Links / Managed VNets | 2–5 minutes (Starter Pools not supported) |
| Private Links + libraries | 2–5 min + 30 sec–5 min |

## Starter Pools vs Custom Pools

**Starter Pools** are managed by Fabric. Pre-warmed medium-size nodes available instantly
in most cases. No configuration needed.

**Custom Pools** are created by workspace admins. You choose node size (Small, Medium,
Large, XL, XXL), min/max node counts, and autoscaling behavior. Minimum node count
of 1 is allowed since Fabric provides restorable availability for single-node clusters.

### When Custom Pools Help Startup

- Set `minNodes = 1` or higher to keep nodes warm
- Avoid cold-start penalties for scheduled jobs
- Lock in specific node sizes for memory-intensive workloads

### When Custom Pools Hurt Startup

- If `minNodes = 0`, first session still requires provisioning
- Custom libraries on the pool still need installation time
- Over-provisioning wastes capacity units

## Diagnosing Slow Startup

### Step 1: Check Networking Configuration

Navigate to: **Workspace Settings > Data Engineering/Science > Networking**

If Private Links or Managed VNets are enabled, Starter Pools are bypassed entirely.
Every session provisions a new cluster (2–5 min minimum).

### Step 2: Check Library Dependencies

Navigate to: **Environment > Libraries**

Custom libraries (pip packages, conda packages, or uploaded JARs/wheels) must be
installed after the cluster starts. Complex dependency trees add 30 seconds to 5 minutes.

**Optimization**: Pre-install common libraries into a published environment. Publishing
bakes libraries into the environment image, reducing per-session install time.

### Step 3: Check Regional Capacity

During peak hours, Starter Pool nodes may be exhausted. Check the Fabric capacity
metrics in the Admin Portal for utilization patterns.

### Step 4: Check for First-Run VNet Provisioning

If Private Link was recently enabled, the first Spark job in the workspace triggers VNet
provisioning (10–15 minutes one-time delay). Subsequent jobs use the provisioned VNet.

## Fixes for Common Startup Issues

### Reduce Library Install Time

1. Pin exact versions to avoid dependency resolution overhead
2. Use `conda` for packages with native dependencies (faster than pip for scipy, etc.)
3. Pre-publish the environment: libraries are baked into the image
4. Remove unused libraries to shrink the install surface

### Mitigate Networking Overhead

1. If Private Links are not strictly required, disable them for faster Starter Pool access
2. Accept the 2–5 min startup for security-critical workspaces
3. Use custom pools with `minNodes >= 1` to keep warm nodes available

### Optimize for Scheduled Jobs

1. Stagger job start times to avoid simultaneous cluster provisioning
2. Use Spark Job Definitions (not notebooks) for production workloads
3. Enable retry policies on Spark Job Definitions for infrastructure recovery
4. Consider keeping a lightweight "warm-up" job running on a schedule

### Monitor Startup Times

```python
# Log session startup duration in your notebook
import time
start = time.time()
spark.sql("SELECT 1")  # Force session initialization
elapsed = time.time() - start
print(f"Session startup took {elapsed:.1f} seconds")
```
