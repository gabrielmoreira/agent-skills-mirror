# Quickstart: Azure Networking MCP Server

**Feature**: 004-azure-network-mcp | **Date**: 2026-03-26

## Prerequisites

- Python 3.10+
- Azure subscription with a service principal (App Registration)
- Service principal granted **Reader** role on target subscription(s)
- Azure SDK packages installed

## 1. Install Dependencies

```bash
cd mcp-servers/azure-network-mcp
pip install -r requirements.txt
```

The `requirements.txt` includes:
- `mcp[cli]` (FastMCP framework)
- `azure-identity`
- `azure-mgmt-network`
- `azure-mgmt-resource`
- `azure-mgmt-dns`
- `azure-mgmt-frontdoor`

## 2. Configure Environment Variables

Copy the `.env.example` and fill in your Azure credentials:

```bash
cp .env.example .env
```

Required variables:

```env
# Azure Service Principal
AZURE_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_CLIENT_SECRET=your-client-secret-value
AZURE_SUBSCRIPTION_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

## 3. Register with OpenClaw

The MCP server is registered in `config/openclaw.json` (added by install.sh). Verify the entry:

```json
{
  "mcpServers": {
    "azure-network-mcp": {
      "command": "python",
      "args": ["mcp-servers/azure-network-mcp/azure_network_mcp_server.py"],
      "env": {
        "AZURE_TENANT_ID": "${AZURE_TENANT_ID}",
        "AZURE_CLIENT_ID": "${AZURE_CLIENT_ID}",
        "AZURE_CLIENT_SECRET": "${AZURE_CLIENT_SECRET}",
        "AZURE_SUBSCRIPTION_ID": "${AZURE_SUBSCRIPTION_ID}"
      }
    }
  }
}
```

## 4. Verify It Works

Test the MCP server directly:

```bash
python mcp-servers/azure-network-mcp/azure_network_mcp_server.py
```

Or through OpenClaw, ask:

> "List all VNets in my Azure subscription"

Expected result: A JSON list of VNets with name, address space, region, and provisioning state.

## 5. Common First Commands

| What You Want | Tool | Example Prompt |
|---------------|------|----------------|
| See all VNets | `azure_list_vnets` | "Show me all Azure VNets" |
| VNet details | `azure_get_vnet_details` | "Get details for VNet 'prod-vnet' in resource group 'networking-rg'" |
| Check NSG rules | `azure_get_nsg_rules` | "Show the rules for NSG 'web-nsg' in resource group 'app-rg'" |
| Security audit | `azure_audit_nsg_compliance` | "Audit all NSGs for CIS compliance violations" |
| ExpressRoute health | `azure_get_expressroute_status` | "Check ExpressRoute circuit status" |
| VPN status | `azure_get_vpn_gateway_status` | "Show VPN Gateway connection status" |
| Firewall rules | `azure_get_firewall_policy` | "Get firewall policy details for 'prod-fw-policy'" |
| Load balancer health | `azure_get_lb_backend_health` | "Check backend health for load balancer 'web-lb'" |

## 6. Multi-Subscription Queries

Pass `subscription_id` to query a different subscription:

> "List VNets in subscription xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

The tool accepts up to 5 concurrent subscription queries per session.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "ClientAuthenticationError" | Verify AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET are correct |
| "AuthorizationFailed" | Grant the service principal Reader role on the target subscription |
| "SubscriptionNotFound" | Verify subscription ID and that the service principal has access |
| "Too many requests (429)" | Azure rate limit; server auto-retries with backoff |
| Empty results | Subscription may have no resources of that type; this is not an error |
