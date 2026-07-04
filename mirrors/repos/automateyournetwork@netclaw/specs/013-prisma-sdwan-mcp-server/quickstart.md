# Quickstart: Prisma SD-WAN MCP Server Integration

**Feature**: 013-prisma-sdwan-mcp-server
**Date**: 2026-04-03

## Prerequisites

Before starting, ensure you have:

1. **Palo Alto Networks Prisma Access/SASE tenant** with SD-WAN enabled
2. **Service account credentials** with API access:
   - Client ID (format: `name@tsg.iam.panserviceaccount.com`)
   - Client Secret
   - Tenant Service Group (TSG) ID
3. **Network connectivity** to Prisma SASE API:
   - Americas: `api.sase.paloaltonetworks.com`
   - Europe: `api.eu.sase.paloaltonetworks.com`

## Installation

### Option 1: Via install.sh (Recommended)

```bash
cd /path/to/netclaw
./scripts/install.sh
# Follow prompts to configure Prisma SD-WAN credentials
```

### Option 2: Manual Installation

1. **Clone the community MCP server**:
   ```bash
   cd mcp-servers
   git clone https://github.com/iamdheerajdubey/prisma-sdwan-mcp.git
   ```

2. **Install dependencies**:
   ```bash
   cd prisma-sdwan-mcp
   pip install -r requirements.txt
   # Or: pip install prisma-sase
   ```

3. **Configure environment variables** in `.env`:
   ```bash
   # Prisma SD-WAN Configuration
   PAN_CLIENT_ID=your-service-account@tsg.iam.panserviceaccount.com
   PAN_CLIENT_SECRET=your-secret-key
   PAN_TSG_ID=your-tenant-service-group-id
   PAN_REGION=americas  # or 'europe'
   ```

4. **Register in openclaw.json**:
   ```json
   {
     "mcpServers": {
       "prisma-sdwan": {
         "command": "python",
         "args": ["-m", "prisma_sdwan_mcp"],
         "cwd": "mcp-servers/prisma-sdwan-mcp",
         "env": {
           "PAN_CLIENT_ID": "${PAN_CLIENT_ID}",
           "PAN_CLIENT_SECRET": "${PAN_CLIENT_SECRET}",
           "PAN_TSG_ID": "${PAN_TSG_ID}",
           "PAN_REGION": "${PAN_REGION}"
         }
       }
     }
   }
   ```

5. **Restart NetClaw** to load the new MCP server.

## Verification

### Test 1: Connectivity Check

Ask NetClaw:
> "List all Prisma SD-WAN sites"

**Expected**: List of sites with names, IDs, and element counts

**If it fails**:
- Check `PAN_CLIENT_ID`, `PAN_CLIENT_SECRET`, `PAN_TSG_ID` are correct
- Verify network connectivity to `api.sase.paloaltonetworks.com`
- For EU deployments, set `PAN_REGION=europe`

### Test 2: Topology Discovery

Ask NetClaw:
> "Show the SD-WAN topology"

**Expected**: Network topology graph showing sites and VPN links

### Test 3: Element Status

Ask NetClaw:
> "Check status of all ION devices"

**Expected**: List of elements with online/offline status, software version

### Test 4: Alarms Check

Ask NetClaw:
> "Show active SD-WAN alarms"

**Expected**: List of critical/major alarms (or empty if no issues)

### Test 5: Configuration Inspection

Ask NetClaw:
> "Show interfaces on element [element-name]"

**Expected**: LAN/WAN interface details for the specified element

## Validation Scenarios (from spec)

### Scenario 1: Site Discovery
**Given** NetClaw is connected to Prisma SD-WAN
**When** user asks "list all SD-WAN sites"
**Then** all sites are returned with names, IDs, and element counts

### Scenario 2: Element Status at Site
**Given** a Prisma SD-WAN deployment with multiple sites
**When** user asks "show elements at site [site-name]"
**Then** all ION devices at that site are listed with status

### Scenario 3: Health Monitoring
**Given** a running SD-WAN fabric
**When** user asks "check status of all ION devices"
**Then** operational health status is returned for each element

### Scenario 4: Alarm Visibility
**Given** active issues in the fabric
**When** user asks "show SD-WAN alarms"
**Then** critical and major alarms are listed with severity and affected components

### Scenario 5: BGP Configuration
**Given** an element with BGP peering
**When** user asks "show BGP peers on element [element-name]"
**Then** BGP peer configurations are returned

### Scenario 6: Application Definitions
**Given** a Prisma SD-WAN deployment with application awareness
**When** user asks "list SD-WAN application definitions"
**Then** all defined applications are returned with classification details

## Troubleshooting

### Authentication Errors

**Error**: `AUTH_FAILED - Invalid credentials`

**Solution**:
1. Verify service account credentials in Prisma Access portal
2. Ensure service account has "Prisma SD-WAN" API permissions
3. Check TSG ID matches your tenant

### Region Mismatch

**Error**: `REGION_MISMATCH - Wrong regional endpoint`

**Solution**:
1. Determine your Prisma Access region (check portal URL)
2. Set `PAN_REGION=europe` for EU deployments
3. Default is `americas`

### Network Connectivity

**Error**: `NETWORK_ERROR - Cannot reach Prisma SASE API`

**Solution**:
1. Test connectivity: `curl -I https://api.sase.paloaltonetworks.com`
2. Check firewall rules allow HTTPS to Prisma endpoints
3. Verify DNS resolution for `api.sase.paloaltonetworks.com`

### Missing Resources

**Error**: `NOT_FOUND - Site/element not found`

**Solution**:
1. Run "list all SD-WAN sites" to see available sites
2. Run "list all elements" to see available devices
3. Verify spelling of site/element names

## Skills Reference

| Skill | Purpose | Key Tools |
|-------|---------|-----------|
| `prisma-sdwan-topology` | Discover fabric structure | get_sites, get_elements, get_topology |
| `prisma-sdwan-status` | Monitor health and issues | get_element_status, get_alarms, get_events |
| `prisma-sdwan-config` | Inspect configuration | get_interfaces, get_bgp_peers, get_static_routes |
| `prisma-sdwan-apps` | Application visibility | get_app_defs |

## Next Steps

After successful verification:

1. Explore your SD-WAN topology with natural language queries
2. Set up regular health checks using `prisma-sdwan-status` skill
3. Integrate with existing NetClaw workflows (packet capture handoff, etc.)
4. Document your specific site/element names for team reference
