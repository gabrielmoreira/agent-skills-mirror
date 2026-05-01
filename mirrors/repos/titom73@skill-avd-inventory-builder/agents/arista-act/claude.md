---
name: arista-act-topology-builder
description: Arista Cloud Test (ACT) topology builder agent. Full version with workflows, advanced patterns, and troubleshooting.
version: full
includes: core.md + advanced sections
---

<!--
  CLAUDE VERSION (Full)
  =====================
  Deploy: Copy core.md content first, then add these advanced sections
-->

# Advanced Sections for Claude

The following sections extend the core instructions with detailed workflows, advanced topology patterns, troubleshooting guides, and additional examples suited for Claude's large context window.

---

## Workflow: Build Topology from Scratch

**Input**: Requirements (device count, topology type, features)

### Steps

1. **Gather requirements**
   - How many spines? How many leaf pairs?
   - CVP auto-configuration needed?
   - ZTP required?
   - Multi-DC or single-DC?
   - Host/server nodes?
   - Automation server (generic node)?

2. **Choose naming convention**
   - Single DC: `spine01`, `leaf01a`, `leaf01b`
   - Multi-DC: `dc1-spine01`, `dc2-leaf01a`

3. **Allocate management IPs** (use /24 subnet pattern from core.md)
   - CVP: .5
   - Automation: .6
   - DC1 Spines: .11-.12
   - DC1 Leaves: .101-.106
   - Hosts: .201+

4. **Set global defaults** (`veos`, `cvp`, `generic` sections)
   - EOS version (e.g., `4.33.1.1F`)
   - CVP version (e.g., `2025.3.0`)
   - Credentials

5. **Define nodes**
   - Add each device with `node_type` and `ip_addr`
   - For CVP: add `auto_configuration: true` if needed
   - For vEOS: add `device_model` if using specific platform
   - For ZTP: add `ztp: true`

6. **Define links**
   - Spine-to-leaf: Spine Ethernet1/1–N to each leaf
   - MLAG peer-links: Two connections (Ethernet3 + Ethernet4)
   - Leaf-to-host: Ethernet5+

7. **Validate** using checklist from core.md

8. **Save** as `<topology-name>.yaml`

---

## Workflow: Convert AVD Inventory to ACT Topology

**Input**: AVD inventory (YAML) + group_vars

### Steps

1. Extract device list from `inventory.yml`
2. Map AVD groups to ACT node types:
   - `spines` → `node_type: veos`
   - `l3leafs` → `node_type: veos`
   - `l2leafs` → `node_type: veos`
   - `cvp` → `node_type: cvp`
3. Extract management IPs from `group_vars` or inventory
4. Reconstruct links from AVD fabric topology variables
5. Generate ACT YAML

**Mapping Example**:

```yaml
# AVD inventory.yml
all:
  children:
    DC1_SPINES:
      hosts:
        DC1-SPINE1: {mgmt_ip: 192.168.0.10}
```

→

```yaml
# ACT topology
nodes:
- DC1-SPINE1:
    ip_addr: 192.168.0.10
    node_type: veos
```

---

## Workflow: Multi-DC Topology with DCI

**Input**: Multi-site requirements (2+ DCs, border leaves for DCI)

### Topology Structure

```
DC1:                    DC2:
  spine01                 spine01
  spine02                 spine02
  leaf01a/b               leaf01a/b
  leaf02a/b               leaf02a/b
  br01a/b (border)        br01a/b (border)

DCI: dc1-br01a ↔ dc2-br01a (Ethernet6)
     dc1-br01b ↔ dc2-br01b (Ethernet6)
```

### Naming Pattern

Use DC prefix for all devices:
- `dc1-spine01`, `dc1-leaf01a`, `dc1-br01a`
- `dc2-spine01`, `dc2-leaf01a`, `dc2-br01a`

### IP Allocation

```
192.168.0.5    cvp
192.168.0.6    automation server
192.168.0.11–12  dc1-spine01, dc1-spine02
192.168.0.21–22  dc2-spine01, dc2-spine02
192.168.0.101–106  dc1 leaves
192.168.0.111–116  dc2 leaves
```

### Border Leaf Links

```yaml
links:
  # DCI — dc1 to dc2
  - connection:
    - dc1-br01a:Ethernet6
    - dc2-br01a:Ethernet6
  - connection:
    - dc1-br01b:Ethernet6
    - dc2-br01b:Ethernet6
```

---

## Advanced ZTP Patterns

### Pattern 1: Partial ZTP (specific devices only)

Use when some devices are pre-configured and others need ZTP.

```yaml
nodes:
- cvp:
    ip_addr: 192.168.0.5
    node_type: cvp
    auto_configuration: true
    ztp_dhcp:
      enabled: true
- spine01:
    ip_addr: 192.168.0.11
    node_type: veos
    # No ztp flag — pre-configured
- leaf01:
    ip_addr: 192.168.0.101
    node_type: veos
    ztp: true   # Boots in ZTP mode, auto-onboarded by CVP
```

### Pattern 2: ZTP with Staged Onboarding

1. Deploy topology with `ztp: true` on all vEOS
2. CVP auto-configures and onboards devices to **Undefined** container
3. Use CVP configlets to move devices to proper containers
4. Apply device-specific configuration via CVP Change Control

### Pattern 3: Manual ZTP (no CVP DHCP)

```yaml
nodes:
- cvp:
    ip_addr: 192.168.0.5
    node_type: cvp
    auto_configuration: true
    # No ztp_dhcp here
- generic-dhcp:
    ip_addr: 192.168.0.6
    node_type: generic
    # Configure ISC DHCP server manually on this node
- leaf01:
    ip_addr: 192.168.0.101
    node_type: veos
    ztp: true
```

**Post-deployment**: Configure DHCP on `generic-dhcp` node to serve ZTP requests.

---

## Multi-CVP Patterns

### Pattern 1: CVP per DC (multi-DC topology)

Each DC has its own CVP managing local devices.

```yaml
nodes:
- cvp1:
    ip_addr: 192.168.0.5
    node_type: cvp
    auto_configuration: true
- cvp2:
    ip_addr: 192.168.0.25
    node_type: cvp
    auto_configuration: true

links:
  # CVP1 manages DC1 devices via Management0
  - connection:
    - cvp1:Management0
    - dc1-spine01:Ethernet1
  # CVP2 manages DC2 devices
  - connection:
    - cvp2:Management0
    - dc2-spine01:Ethernet1
```

**Important**: Use `Management0` on CVP nodes for CVP-to-device connections in multi-CVP setups.

### Pattern 2: Shared CVP with Containerized Devices

Single CVP managing multiple DCs. No topology changes needed — CVP auto-configuration uses the management subnet to discover all devices.

---

## Troubleshooting Guide

### Issue: "Interface already in use" error

**Cause**: An interface appears in multiple `connection` entries.

**Solution**: Check all connections referencing the interface. Each interface can only appear ONCE across all links.

```yaml
# WRONG — Ethernet1 used twice
links:
  - connection:
    - leaf01a:Ethernet1
    - spine01:Ethernet1
  - connection:
    - leaf01a:Ethernet1   # ERROR: duplicate
    - spine02:Ethernet1

# CORRECT
links:
  - connection:
    - leaf01a:Ethernet1
    - spine01:Ethernet1
  - connection:
    - leaf01a:Ethernet2
    - spine02:Ethernet1
```

### Issue: MLAG not forming

**Cause**: Peer-link VLAN 4094 missing trunk group or only one peer-link connection defined.

**Solution**: Always create TWO peer-link connections (Ethernet3 + Ethernet4) and configure VLAN 4094 with trunk group in EOS config.

```yaml
# Topology — two peer-link connections required
- connection:
  - leaf01a:Ethernet3
  - leaf01b:Ethernet3
- connection:
  - leaf01a:Ethernet4
  - leaf01b:Ethernet4
```

```eos
! EOS config post-deployment
vlan 4094
   trunk group MLAG
!
interface Port-Channel3
   switchport mode trunk
   switchport trunk group MLAG
```

### Issue: CVP auto-configuration fails

**Possible causes**:
1. CVP version not supported (see core.md — supported: 2020.1.x through 2025.1.x)
2. `instance_type` not `xlarge`
3. Devices have `ztp: true` but CVP missing `ztp_dhcp: {enabled: true}`

**Solution**:

```yaml
- cvp:
    ip_addr: 192.168.0.5
    node_type: cvp
    auto_configuration: true
    instance_type: xlarge   # REQUIRED for auto-config
    ztp_dhcp:
      enabled: true         # REQUIRED if devices have ztp: true
```

### Issue: Devices not accessible after deployment

**Cause**: IP address conflicts or default gateway not configured.

**Solution**:
1. Verify unique IP addresses across all nodes in topology
2. ACT assigns /24 by default — ensure all devices in same /24 subnet (e.g., 192.168.0.0/24)
3. Default gateway is auto-configured by ACT — check `show ip route` on vEOS

### Issue: ZTP device only has `cvptemp` user

**Expected behavior**: Devices with `ztp: true` boot with only the `cvptemp` user (no `cvpadmin` or credentials from global `veos` section).

**Solution**: Use `cvptemp` to log in, or wait for CVP to onboard the device (credentials will be configured via ZTP).

---

## Complete Multi-DC Example with Border Leaves

```yaml
veos:
  username: arista
  password: arista
  version: 4.33.1.1F

cvp:
  username: root
  password: cvproot
  version: 2025.3.0

generic:
  version: ubuntu-2204-lts
  username: arista
  password: arista

nodes:
# CVP
- cvp:
    ip_addr: 192.168.0.5
    node_type: cvp
    instance_type: xlarge
    auto_configuration: true

# Automation server
- avd:
    ip_addr: 192.168.0.6
    node_type: generic

# DC1 Spines
- dc1-spine01:
    ip_addr: 192.168.0.11
    node_type: veos
    device_model: 7050SX3-48YC8
- dc1-spine02:
    ip_addr: 192.168.0.12
    node_type: veos
    device_model: 7050SX3-48YC8

# DC1 Leaves
- dc1-leaf01a:
    ip_addr: 192.168.0.101
    node_type: veos
- dc1-leaf01b:
    ip_addr: 192.168.0.102
    node_type: veos
- dc1-leaf02a:
    ip_addr: 192.168.0.103
    node_type: veos
- dc1-leaf02b:
    ip_addr: 192.168.0.104
    node_type: veos

# DC1 Border Leaves
- dc1-br01a:
    ip_addr: 192.168.0.105
    node_type: veos
- dc1-br01b:
    ip_addr: 192.168.0.106
    node_type: veos

# DC2 Spines
- dc2-spine01:
    ip_addr: 192.168.0.21
    node_type: veos
    device_model: 7050SX3-48YC8
- dc2-spine02:
    ip_addr: 192.168.0.22
    node_type: veos
    device_model: 7050SX3-48YC8

# DC2 Leaves
- dc2-leaf01a:
    ip_addr: 192.168.0.111
    node_type: veos
- dc2-leaf01b:
    ip_addr: 192.168.0.112
    node_type: veos

# DC2 Border Leaves
- dc2-br01a:
    ip_addr: 192.168.0.113
    node_type: veos
- dc2-br01b:
    ip_addr: 192.168.0.114
    node_type: veos

# Hosts
- server01:
    ip_addr: 192.168.0.201
    node_type: generic
- server02:
    ip_addr: 192.168.0.202
    node_type: generic

links:
  # DC1 Spine-to-Leaf
  - connection:
    - dc1-spine01:Ethernet1
    - dc1-leaf01a:Ethernet1
  - connection:
    - dc1-spine01:Ethernet2
    - dc1-leaf01b:Ethernet1
  - connection:
    - dc1-spine01:Ethernet3
    - dc1-leaf02a:Ethernet1
  - connection:
    - dc1-spine01:Ethernet4
    - dc1-leaf02b:Ethernet1
  - connection:
    - dc1-spine02:Ethernet1
    - dc1-leaf01a:Ethernet2
  - connection:
    - dc1-spine02:Ethernet2
    - dc1-leaf01b:Ethernet2
  - connection:
    - dc1-spine02:Ethernet3
    - dc1-leaf02a:Ethernet2
  - connection:
    - dc1-spine02:Ethernet4
    - dc1-leaf02b:Ethernet2

  # DC1 Spine-to-Border
  - connection:
    - dc1-spine01:Ethernet5
    - dc1-br01a:Ethernet1
  - connection:
    - dc1-spine01:Ethernet6
    - dc1-br01b:Ethernet1
  - connection:
    - dc1-spine02:Ethernet5
    - dc1-br01a:Ethernet2
  - connection:
    - dc1-spine02:Ethernet6
    - dc1-br01b:Ethernet2

  # DC1 MLAG Peer-Links
  - connection:
    - dc1-leaf01a:Ethernet3
    - dc1-leaf01b:Ethernet3
  - connection:
    - dc1-leaf01a:Ethernet4
    - dc1-leaf01b:Ethernet4
  - connection:
    - dc1-leaf02a:Ethernet3
    - dc1-leaf02b:Ethernet3
  - connection:
    - dc1-leaf02a:Ethernet4
    - dc1-leaf02b:Ethernet4
  - connection:
    - dc1-br01a:Ethernet3
    - dc1-br01b:Ethernet3
  - connection:
    - dc1-br01a:Ethernet4
    - dc1-br01b:Ethernet4

  # DC2 Spine-to-Leaf
  - connection:
    - dc2-spine01:Ethernet1
    - dc2-leaf01a:Ethernet1
  - connection:
    - dc2-spine01:Ethernet2
    - dc2-leaf01b:Ethernet1
  - connection:
    - dc2-spine02:Ethernet1
    - dc2-leaf01a:Ethernet2
  - connection:
    - dc2-spine02:Ethernet2
    - dc2-leaf01b:Ethernet2

  # DC2 Spine-to-Border
  - connection:
    - dc2-spine01:Ethernet3
    - dc2-br01a:Ethernet1
  - connection:
    - dc2-spine01:Ethernet4
    - dc2-br01b:Ethernet1
  - connection:
    - dc2-spine02:Ethernet3
    - dc2-br01a:Ethernet2
  - connection:
    - dc2-spine02:Ethernet4
    - dc2-br01b:Ethernet2

  # DC2 MLAG Peer-Links
  - connection:
    - dc2-leaf01a:Ethernet3
    - dc2-leaf01b:Ethernet3
  - connection:
    - dc2-leaf01a:Ethernet4
    - dc2-leaf01b:Ethernet4
  - connection:
    - dc2-br01a:Ethernet3
    - dc2-br01b:Ethernet3
  - connection:
    - dc2-br01a:Ethernet4
    - dc2-br01b:Ethernet4

  # DCI — DC1 to DC2 Border Leaves
  - connection:
    - dc1-br01a:Ethernet6
    - dc2-br01a:Ethernet6
  - connection:
    - dc1-br01b:Ethernet6
    - dc2-br01b:Ethernet6

  # Hosts
  - connection:
    - dc1-leaf01a:Ethernet5
    - server01:Ethernet1
  - connection:
    - dc2-leaf01a:Ethernet5
    - server02:Ethernet1
```

---

## Common Mistakes and How to Avoid Them

### 1. Forgetting to add both MLAG peer-link connections

**Mistake**:
```yaml
- connection:
  - leaf01a:Ethernet3
  - leaf01b:Ethernet3
# Missing second peer-link
```

**Fix**: Always add TWO peer-link connections.

### 2. Using spaces around colons in interface references

**Mistake**:
```yaml
- connection:
  - leaf01a: Ethernet1   # Space before interface
```

**Fix**:
```yaml
- connection:
  - leaf01a:Ethernet1    # No space
```

### 3. Inconsistent device naming (mixed case, special chars)

**Mistake**: `DC1-Leaf_01`, `dc2-SPINE#1`

**Fix**: Use `[a-zA-Z0-9\-.]` only — `DC1-LEAF01`, `dc2-spine01`

### 4. IP address conflicts

**Mistake**: Two devices with same IP.

**Fix**: Use the IP allocation table from core.md — assign unique IPs per role.

### 5. Missing `instance_type: xlarge` for CVP auto-config

**Mistake**:
```yaml
- cvp:
    node_type: cvp
    auto_configuration: true
    # Missing instance_type
```

**Fix**:
```yaml
- cvp:
    node_type: cvp
    auto_configuration: true
    instance_type: xlarge
```

### 6. Not specifying EOS/CVP versions

**Mistake**: Using default versions (may be outdated or incompatible).

**Fix**: Always set explicit versions in global sections:
```yaml
veos:
  version: 4.33.1.1F

cvp:
  version: 2025.3.0
```

### 7. Over-defining ports when using device_model

**Mistake**:
```yaml
- spine01:
    device_model: 7050SX3-48YC8
    ports:
      - Ethernet1-48   # Redundant — device_model auto-creates ports
```

**Fix**: Omit `ports` when using `device_model` — ACT auto-creates interfaces based on the model.

---

## Advanced Validation Techniques

### 1. Link Symmetry Check

For each connection, verify the reverse exists in your mental model:
- If `leaf01a:Ethernet1 → spine01:Ethernet1`, then spine01 expects a cable on Ethernet1.

### 2. Interface Numbering Consistency

Spines: Use sequential Ethernet ports starting from Ethernet1 (or Ethernet1/1 for modular).
Leaves: Ethernet1–2 = uplinks to spines, Ethernet3–4 = MLAG peer-link, Ethernet5+ = downlinks.

### 3. MLAG Pair Validation

For each MLAG pair (`<device>a`, `<device>b`):
- Exactly 2 peer-link connections
- Both devices in same IP range (e.g., .101 and .102)
- Same `device_model` (if specified)

### 4. CVP Connectivity Validation

If `auto_configuration: true`:
- CVP IP in same /24 as all vEOS devices
- No firewall/ACL blocking CVP-to-device communication
- CVP version supported (2020.1.x – 2025.1.x)

---

# Resources

- [ACT Documentation](https://www.arista.com/en/support/act)
- [Arista vEOS-lab User Guide](https://www.arista.com/en/support/software-download)
- [CloudVision Portal Documentation](https://www.arista.com/en/cg-cv)
- [AVD Documentation](https://avd.arista.com/)
