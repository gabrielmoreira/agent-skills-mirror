# Tenant Settings Checklist

Complete checklist for configuring Microsoft Fabric tenant settings required by the Fabric Data Agent.

## Access the Admin Portal

1. Sign in to Microsoft Fabric with a Fabric Admin account.
2. Select the gear icon (top-right) → **Admin Portal**.
3. Select **Tenant settings** from the left navigation.

> **Note**: Tenant setting changes can take up to one hour to take effect.

## Required Tenant Settings

Work through each setting in order. All are required unless marked optional.

### 1. Copilot and Azure OpenAI Service

**Setting**: "Users can use Copilot and other features powered by Azure OpenAI"

| Field | Value |
|-------|-------|
| Location | Tenant Settings → Copilot and Azure OpenAI Service |
| Required | Yes |
| Default | Varies by tenant |

**remediate**:
- If this toggle is off, users cannot create or interact with data agents at all.
- This can be scoped to specific security groups. Verify the affected user is in an allowed group.
- This setting is managed at both tenant AND capacity levels. Check both.

### 2. Cross-Geo Processing

**Setting**: "Data sent to Azure OpenAI can be processed outside your capacity's geographic region, compliance boundary, or national cloud instance"

| Field | Value |
|-------|-------|
| Location | Tenant Settings → Copilot and Azure OpenAI Service |
| Required | Yes (if capacity region is outside EU/US) |
| Default | Disabled |

**remediate**:
- Required for ALL capacities outside the EU data boundary and the US.
- If your capacity is in regions like Australia, Japan, Brazil, etc., this MUST be enabled.
- Even if this is on, you also need the related "storing" setting (next item).

### 3. Cross-Geo Storing

**Setting**: "Data sent to Azure OpenAI can be stored outside your capacity's geographic region, compliance boundary, or national cloud instance"

| Field | Value |
|-------|-------|
| Location | Tenant Settings → Copilot and Azure OpenAI Service |
| Required | Yes (if capacity region is outside EU/US) |
| Default | Disabled |

**remediate**:
- Must be enabled alongside the cross-geo processing setting.
- Frequently missed when only the processing setting is toggled on.

### 4. Conversation History Storage

**Setting**: "Conversation history stored outside your capacity's geographic region, compliance boundary, or national cloud instance"

| Field | Value |
|-------|-------|
| Location | Tenant Settings → Copilot and Azure OpenAI Service |
| Required | Yes (for full conversational experience outside EU/US) |
| Default | Disabled |

**remediate**:
- Without this, agents cannot maintain context across conversation turns.
- Conversation history is stored up to 28 days unless manually cleared.
- Users can delete history anytime via "Clear chat".

### 5. Fabric Copilot Capacities

**Setting**: "Capacities can be designated as Fabric Copilot capacities"

| Field | Value |
|-------|-------|
| Location | Tenant Settings → Copilot and Azure OpenAI Service |
| Required | Yes |
| Default | Varies |

**remediate**:
- After enabling at tenant level, the capacity admin must also designate the specific capacity.
- Check Capacity Settings → Copilot designation for the target capacity.

### 6. Fabric Data Agent Item Type

**Setting**: "Fabric data agent"

| Field | Value |
|-------|-------|
| Location | Tenant Settings → Fabric data agent section |
| Required | Yes |
| Default | Enabled |

**remediate**:
- If disabled, the "Fabric data agent" item type will not appear in the "+ New Item" dialog.
- Can be scoped to specific security groups.
- If recently changed, wait up to one hour for propagation.

### 7. XMLA Endpoints (Power BI Semantic Models Only)

**Setting**: "Allow XMLA endpoints and Analyze in Excel with on-premises datasets"

| Field | Value |
|-------|-------|
| Location | Tenant Settings → Integration settings |
| Required | Only if using Power BI semantic model data sources |
| Default | Varies |

**remediate**:
- Without this, data agents cannot connect to Power BI semantic models.
- This is a common miss because it is in a different settings section (Integration, not Copilot).
- Users only need Read permission on semantic models (Write is not required).

## Verification Steps

After enabling all settings, verify the configuration:

1. Wait at least 15 minutes for settings to propagate (up to 1 hour in some tenants).
2. Navigate to a workspace with F2+ capacity.
3. Select **+ New Item** → search for "data agent".
4. If the item type appears, tenant settings are correctly configured.
5. If it does not appear, re-verify each setting above and check security group scoping.

## Capacity Requirements

| Capacity Type | Supported |
|--------------|-----------|
| F2 or higher (Fabric) | Yes |
| Power BI Premium P1+ (with Fabric enabled) | Yes |
| Power BI Premium Per User (PPU) | No |
| Fabric Trial | Yes |
| F1 | No |
