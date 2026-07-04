# Quickstart: HashiCorp Vault MCP Server Integration

**Feature**: 019-vault-mcp-server | **Date**: 2026-04-04

## Prerequisites

1. HashiCorp Vault server running (dev or production)
2. Vault token with appropriate policies
3. NetClaw OpenClaw gateway running

## Setup (5 minutes)

### Step 1: Install Vault MCP Server

```bash
# Using Go
go install github.com/hashicorp/vault-mcp-server@latest

# Or download binary from releases
curl -LO https://releases.hashicorp.com/vault-mcp-server/latest/vault-mcp-server_linux_amd64.zip
unzip vault-mcp-server_linux_amd64.zip
sudo mv vault-mcp-server /usr/local/bin/
```

### Step 2: Create Vault Policy

Create a policy file `netclaw-policy.hcl`:

```hcl
# Read network secrets
path "secret/data/network/*" {
  capabilities = ["read", "list"]
}

# Issue certificates
path "pki/issue/network-devices" {
  capabilities = ["update"]
}

# List mounts (discovery)
path "sys/mounts" {
  capabilities = ["read"]
}
```

Apply the policy:

```bash
vault policy write netclaw netclaw-policy.hcl
vault token create -policy=netclaw -ttl=24h
```

### Step 3: Configure Environment

Add to your `.env` file:

```bash
# Vault MCP Server
VAULT_ADDR=https://vault.example.com:8200
VAULT_TOKEN=hvs.your_token_here

# Optional: Enterprise namespace
# VAULT_NAMESPACE=network-ops
```

### Step 4: Register MCP Server

Add to `config/openclaw.json`:

```json
{
  "mcpServers": {
    "vault-mcp": {
      "command": "vault-mcp-server",
      "args": [],
      "env": {
        "VAULT_ADDR": "${VAULT_ADDR}",
        "VAULT_TOKEN": "${VAULT_TOKEN}",
        "VAULT_NAMESPACE": "${VAULT_NAMESPACE}"
      }
    }
  }
}
```

### Step 5: Restart OpenClaw Gateway

```bash
# Restart to load new MCP server
openclaw restart
```

## Verification

### Test 1: List Mounts

```
List all Vault secret engine mounts
```

**Expected**: List of mounts with types (kv, pki, etc.).

### Test 2: List Secrets

```
List secrets under the network path in Vault
```

**Expected**: List of secret paths (values NOT displayed).

### Test 3: Read Secret (Metadata Only)

```
Read the router-01 credentials from Vault
```

**Expected**: Confirmation that secret exists with key names (values REDACTED).

### Test 4: Issue Certificate

```
Issue a certificate for switch.example.com using the network-devices role
```

**Expected**: Certificate serial number and expiration (cert saved to file if inject_to specified).

## Skills Available

| Skill | Invocation | Description |
|-------|------------|-------------|
| `/vault-secrets` | KV operations | Read, write, list secrets |
| `/vault-pki` | Certificate management | Issue and manage certificates |
| `/vault-mounts` | Mount discovery | List and manage secret engines |

## Common Queries

### Secret Operations

```
# List available secrets
List all secrets under secret/network in Vault

# Check if secret exists
Does the router-01 credential exist in Vault?

# Read secret to file
Read router-01 credentials and save to /tmp/creds.json
```

### PKI Operations

```
# Issue certificate
Issue a certificate for router.example.com with 30-day TTL

# Issue with SANs
Issue certificate for api.example.com with SANs: api-01.example.com, api-02.example.com

# List roles
List available PKI roles in Vault
```

### Mount Operations

```
# Discover mounts
List all secret engine mounts in Vault

# Find network mounts
Show mounts related to network credentials
```

## Security Notes

**IMPORTANT**: Secret values are NEVER displayed in NetClaw output.

- Use `inject_to` parameter to save secrets to files
- Secrets are injected directly to integrations (pyATS, gNMI)
- Vault audit log tracks all access
- Use minimum-privilege tokens
- Rotate tokens regularly

## Troubleshooting

### "Permission Denied" Error

- Verify token has correct policy
- Check path matches policy exactly
- Ensure namespace is correct (Enterprise)

### "Connection Refused" Error

- Verify `VAULT_ADDR` is correct
- Check network connectivity to Vault
- Ensure Vault is unsealed

### "Token Expired" Error

- Create new token with `vault token create`
- Update `VAULT_TOKEN` in environment
- Consider using longer TTL for service accounts

### Secret Not Found

- Verify secret path is correct
- Check KV version (v1 vs v2)
- Ensure secret hasn't been deleted
