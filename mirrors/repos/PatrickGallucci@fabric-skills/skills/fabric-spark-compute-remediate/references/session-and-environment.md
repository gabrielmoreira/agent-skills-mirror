# Session and Environment Guide

## Table of Contents

- [Slow Startup Diagnosis](#slow-startup)
- [Publishing Failures](#publishing-failures)
- [Library Issues](#library-issues)
- [VNet Provisioning Delay](#vnet-delay)
- [Spark Properties Configuration](#spark-properties)
- [Environment Best Practices](#environment-best-practices)

---

## Slow Startup

### Expected Startup Times

| Scenario | Expected Time | Notes |
|----------|--------------|-------|
| Starter Pool, no custom libraries/properties | 5-10 seconds | Pre-warmed cluster, fastest path |
| Starter Pool with custom libraries/properties | 30 seconds - 5 minutes | Session personalization required |
| Non-Medium node size on Starter Pool | 2-5 minutes | Falls back to on-demand provisioning |
| Custom Pool, cold start | 2-5 minutes | Cluster provisioning from cloud |
| First job after Private Link enabled | +10-15 minutes | One-time VNet provisioning |

### Diagnostic Decision Tree

1. **Check pool type**: Workspace Settings > Data Engineering/Science > Pool tab
   - If Starter Pool → proceed to step 2
   - If Custom Pool → cold start of 2-5 minutes is normal; proceed to step 4

2. **Check node size**: Starter Pools only support Medium nodes for fast startup
   - If non-Medium node size is selected → on-demand start (2-5 min) is expected
   - If Medium → proceed to step 3

3. **Check environment attachments**: Open your notebook's environment settings
   - Custom libraries attached? → 30s-5min personalization delay is expected
   - Custom Spark properties? → same delay applies
   - Neither? → check capacity utilization (Monitoring Hub); may be waiting for cores

4. **Check Private Link**: Workspace Settings > Azure Connections
   - If Private Link enabled and this is the first Spark job → 10-15 min VNet provisioning
   - This is a one-time delay per workspace

### Resolution Actions

| Cause | Fix |
|-------|-----|
| Custom libraries adding startup time | Pre-install in environment and publish; avoid inline %pip in pipelines |
| Non-Medium nodes on Starter Pool | Switch to Medium or accept longer startup |
| Capacity fully utilized | Cancel idle sessions or upgrade SKU |
| Private Link first-job delay | Expected one-time cost; plan accordingly |

---

## Publishing Failures

### Common Causes

1. **Concurrent publish**: An environment accepts only one Publish action at a time. Wait for the current publish to complete or cancel it via View Progress.

2. **Runtime incompatibility**: If you changed the Spark runtime version, existing libraries or configurations may be incompatible.
   - Remove incompatible libraries
   - Republish with the updated runtime

3. **Library conflicts**: Dependencies may have version conflicts that the resolver cannot reconcile.
   - Check the error notification for specific conflict details
   - Remove the conflicting library and try alternative versions

4. **Private Link first-job delay**: Environment publishing runs as a Spark job. If Private Link is enabled and this is the first Spark job, VNet provisioning adds 10-15 minutes.

### Publishing Workflow

1. Make changes to Libraries and/or Spark compute sections
2. Select **Save** to cache changes (prevents loss on browser refresh)
3. Select **Publish** to apply changes
4. Review the **Pending Changes** page
5. Select **Publish All** to initiate
6. Wait for completion notification (may take several minutes for library changes)

**Important**: Saving does NOT apply changes. Only Publish applies configurations. Unsaved changes are lost if you refresh or leave the browser.

### Canceling a Publish

1. Look for the progress banner in the environment
2. Select **View Progress**
3. Cancel the operation if needed

---

## Library Issues

### Library Types and Management Approaches

| Library Type | Environment Management | Inline Installation |
|-------------|----------------------|-------------------|
| Python Public (PyPI/Conda) | Supported | Supported |
| Python Custom (.whl) | Supported | Supported |
| R Public (CRAN) | Not supported | Supported |
| R Custom (.tar.gz) | Supported as custom | Supported |
| JAR | Supported as custom | Supported |

### When to Use Environment Libraries vs Inline

**Use environment libraries when**:
- Common libraries shared across multiple notebooks
- Pipeline scenarios (stability is critical)
- Libraries don't change frequently
- You need guaranteed availability at session start

**Use inline installation when**:
- Interactive one-time exploration
- Validating a custom library quickly
- Adding a new PyPI/Conda package temporarily

**Critical warning**: Inline `%pip install` generates different dependency trees over time and can cause conflicts. Inline commands are **turned off by default for pipeline runs** and are NOT recommended for pipelines.

### Network-Restricted Environments

When **Workspace Outbound Access Protection** or **Managed VNets** are enabled, access to public repositories (PyPI, Conda) is blocked. Follow Microsoft's guidance on managing libraries with limited network access to use private feeds (Azure Artifact Feed) or pre-uploaded custom packages.

### remediate Library Conflicts

1. Check the publish error notification for the specific conflict
2. Download current configurations: Environment Home tab > Download All Files
3. Review `Publiclibrary.yml` for conflicting version pins
4. Remove the conflicting library or adjust version constraints
5. Republish the environment

---

## VNet Delay

### When It Occurs

When **Private Link** is enabled for a workspace, the first Spark job triggers VNet provisioning. This is a one-time operation that takes approximately **10-15 minutes**.

### What It Affects

- First interactive notebook session
- First Spark job definition run
- First environment publish (publishing runs as a Spark job)
- First lakehouse operation

### Mitigation

- Plan for the initial delay during workspace setup
- Run a lightweight warm-up job (empty notebook execution) after enabling Private Link
- Subsequent jobs will not experience this delay

---

## Spark Properties

### Configuration Levels

Spark properties can be set at multiple levels, with narrower scopes overriding broader ones:

1. **Workspace default**: Via Workspace Settings > Data Engineering/Science
2. **Environment**: Via the Spark compute section of an environment
3. **Session-level** (`spark.conf.set`): Controls application-level parameters within a notebook

### Customizing Executor Configuration

Within an environment's Compute section, you can tune:

- **Spark driver cores**: Choose from available options within your node size bounds
- **Spark executor memory**: Select from memory options within node limits

Example for a Large node (16 VCores, 128 GB):
- Driver cores: 4, 8, or 16
- Executor memory: 28g, 56g, or 112g

### Enabling Compute Customization

Workspace admins control whether users can customize compute:

1. Workspace Settings > Data Engineering/Science
2. Pool tab > **Customize compute configurations for items** toggle
3. When OFF: all environments use workspace default pool settings
4. When ON: members and contributors can customize session-level compute in environments

---

## Environment Best Practices

### Recommended Setup Workflow

1. Create a new environment and select the appropriate Spark runtime
2. Install common public libraries in the Libraries section
3. Upload any custom .whl or .jar files
4. Configure Spark properties if needed
5. Publish the environment (allow 5-15 minutes for library resolution)
6. Attach as workspace default or to specific notebooks/Spark jobs
7. Share with Read permission to team members who need to use it

### Migration from Workspace Settings

If migrating from legacy workspace-level settings to environments:

1. Go to Workspace Settings > Data Engineering/Science
2. Download existing configurations (Download All Files)
3. Note the current Runtime version
4. Create a new environment with matching runtime
5. Upload public library definitions from `Publiclibrary.yml`
6. Upload custom library files
7. Upload Spark properties from `Sparkproperties.yml`
8. Publish and verify
9. Enable environment in Workspace Settings (this removes legacy configurations)

**Warning**: Enabling the environment setting discards all existing workspace-level configurations. Ensure successful migration before switching.
