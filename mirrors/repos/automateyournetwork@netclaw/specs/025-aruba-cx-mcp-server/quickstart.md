# Quickstart Guide: Aruba CX MCP Server

**Feature**: 025-aruba-cx-mcp-server
**Date**: 2026-04-08

## Prerequisites

1. Access to one or more Aruba CX switches running AOS-CX 10.x or later
2. REST API enabled on the switches
3. Valid credentials with appropriate privileges
4. Network connectivity from NetClaw host to switch management IPs

## Configuration

### Option 1: Environment Variable (Recommended)

Set `ARUBA_CX_TARGETS` with a JSON array of switch configurations:

```bash
export ARUBA_CX_TARGETS='[
  {
    "name": "core-sw-1",
    "host": "10.1.1.1",
    "username": "admin",
    "password": "YourPassword123"
  },
  {
    "name": "core-sw-2",
    "host": "10.1.1.2",
    "username": "admin",
    "password": "YourPassword123"
  }
]'
```

### Option 2: Configuration File

Create `aruba-cx-config.json` and set `ARUBA_CX_CONFIG`:

```json
[
  {
    "name": "core-sw-1",
    "host": "10.1.1.1",
    "username": "admin",
    "password": "YourPassword123",
    "port": 443,
    "api_version": "v10.13",
    "verify_ssl": true
  }
]
```

```bash
export ARUBA_CX_CONFIG=/path/to/aruba-cx-config.json
```

### Optional: ITSM Integration

For production environments with ServiceNow:

```bash
export ITSM_ENABLED=true
# For lab/testing without ServiceNow validation:
export ITSM_LAB_MODE=true
```

## Test Scenarios

### Scenario 1: System Discovery (User Story 1)

**Objective**: Verify system info, firmware, and VSF topology retrieval.

```text
# Natural language request to NetClaw:
"Show me the system information for core-sw-1"

# Expected: Hostname, model, serial, version, uptime

"What firmware versions are running on core-sw-1?"

# Expected: Primary/secondary versions, boot image, ISSU capability

"Show the VSF topology for core-sw-1"

# Expected: VSF members with roles, or "not configured" if standalone
```

**Verification**:
- [ ] System info returns hostname, model, serial number
- [ ] Firmware info shows primary and secondary versions
- [ ] VSF topology shows member roles or indicates not configured

---

### Scenario 2: Interface Monitoring (User Story 1)

**Objective**: Verify interface status, LLDP, and DOM diagnostics.

```text
"Show all interfaces on core-sw-1"

# Expected: List of interfaces with admin/oper state, speed

"What LLDP neighbors does core-sw-1 see?"

# Expected: Neighbor devices with ports and capabilities

"Show optical transceiver health for core-sw-1"

# Expected: DOM readings with threshold status (normal/warning/alarm)
```

**Verification**:
- [ ] Interface list includes state, speed, description
- [ ] LLDP neighbors show remote device info
- [ ] DOM diagnostics include threshold violation detection

---

### Scenario 3: Layer 2 Operations (User Story 3)

**Objective**: Verify VLAN and MAC table queries.

```text
"Show all VLANs on core-sw-1"

# Expected: VLAN IDs, names, port assignments

"Find MAC address aa:bb:cc:dd:ee:ff on core-sw-1"

# Expected: VLAN and port where MAC is learned

"Show the MAC address table for VLAN 100 on core-sw-1"

# Expected: All MACs in VLAN 100 with ports
```

**Verification**:
- [ ] VLANs show ID, name, and member ports
- [ ] MAC search finds specific address
- [ ] MAC table can be filtered by VLAN

---

### Scenario 4: Configuration Viewing (User Story 4)

**Objective**: Verify running and startup config retrieval.

```text
"Show the running config for core-sw-1"

# Expected: Full running configuration

"Show the startup config for core-sw-1"

# Expected: Saved startup configuration

"Compare running and startup config for core-sw-1"

# Expected: Differences between configs
```

**Verification**:
- [ ] Running config retrieved successfully
- [ ] Startup config retrieved successfully
- [ ] Configs can be compared for differences

---

### Scenario 5: Write Operations (User Story 4, Lab Mode)

> **Note**: Enable ITSM_LAB_MODE=true for testing without ServiceNow.

**Objective**: Verify write operations with ITSM gating.

```text
"Shutdown interface 1/1/10 on core-sw-1 with CR CHG0001234"

# Expected: Interface admin state changed to down

"Create VLAN 200 named 'Test_VLAN' on core-sw-1 with CR CHG0001234"

# Expected: VLAN 200 created

"Save the running config on core-sw-1 with CR CHG0001234"

# Expected: Config saved to startup
```

**Verification**:
- [ ] Interface config change succeeds with CR
- [ ] VLAN creation succeeds with CR
- [ ] Config save succeeds with CR
- [ ] Operations blocked without CR when ITSM_ENABLED=true

---

### Scenario 6: Error Handling

**Objective**: Verify error handling for edge cases.

```text
"Show system info for nonexistent-switch"

# Expected: Clear error - target not found

"Show system info for unreachable-switch" (configure with bad IP)

# Expected: Clear error - connection timeout with switch name

"Create VLAN 100 on core-sw-1" (without CR when ITSM_ENABLED=true)

# Expected: Clear error - ITSM CR required
```

**Verification**:
- [ ] Unknown target returns clear error
- [ ] Unreachable switch returns timeout with name
- [ ] Missing CR blocks write operations with clear message

---

## Skill Verification

After installation, verify all 4 skills appear in NetClaw:

```text
"What Aruba CX skills do you have?"

# Expected skills:
# - aruba-cx-system
# - aruba-cx-interfaces
# - aruba-cx-switching
# - aruba-cx-config
```

## Troubleshooting

### Connection Issues

1. Verify REST API is enabled on switch: `show rest-api`
2. Check firewall allows HTTPS (443) to switch management IP
3. Verify credentials work via curl:
   ```bash
   curl -k -u admin:password https://10.1.1.1/rest/v10.13/system
   ```

### SSL Certificate Errors

If using self-signed certificates, set `verify_ssl: false` in target config.
For production, use proper CA-signed certificates.

### ITSM Errors

- Verify ITSM_ENABLED and ITSM_LAB_MODE settings
- Ensure CR number format matches ServiceNow patterns (e.g., CHG0001234)
- Check ServiceNow MCP server connectivity if not in lab mode
