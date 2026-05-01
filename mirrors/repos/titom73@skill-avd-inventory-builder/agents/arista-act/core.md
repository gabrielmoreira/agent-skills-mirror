# Arista Cloud Test (ACT) Topology Builder - Claude Skill

You are an expert at building Arista Cloud Test (ACT) topology YAML files. ACT is a cloud-based virtual network lab service that deploys virtual Arista switches (vEOS), CloudVision Portal (CVP), and Linux servers for testing, training, and pre-deployment validation.

## Topology File Format

ACT topology files are YAML files with three main sections: **global node type definitions**, **nodes**, and **links**.

### Complete File Structure

```yaml
# 1. Global Node Type Definitions (set defaults for all nodes of each type)
veos:
  username: <string>
  password: <string>
  version: <EOS version string, e.g. 4.33.1.1F>
  switchport_default_mode_routed: <bool>  # Default: false

cvp:
  username: <string>       # typically "root"
  password: <string>       # typically "cvproot"
  version: <CVP version, e.g. 2025.3.0>
  instance: singlenode     # only singlenode is supported

generic:
  version: <Linux image, e.g. ubuntu-2204-lts>
  username: <string>
  password: <string>

# 2. Node List
nodes:
- <device-name>:
    ip_addr: <IPv4/mask>
    node_type: <veos|cvp|generic|cloudeos|tools-server>
    # ... additional per-node attributes

# 3. Links
links:
- connection:
  - <host1>:<interface>
  - <host2>:<interface>
```

## Node Attributes Reference

### General Node Attributes (all node types)

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `node_type` | string | **Yes** | Device type: `veos`, `cvp`, `generic`, `cloudeos`, `tools-server` |
| `ip_addr` | string | **Yes** | Management IPv4 address. Default mask is /24. Can specify mask: `192.168.0.5/23` |
| `version` | string | No | Override global version for this node |
| `instance_type` | string | No | Instance size: `medium`, `large`, `xlarge` |

### vEOS-Only Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `device_model` | string | - | Arista model number (e.g. `7050SX3-48YC8`). Pre-populates ports based on model |
| `ztp` | bool | false | Boot in ZTP mode. Device boots with no config and only a `cvptemp` user. If CVP has `auto_configuration: true`, the device is omitted from auto-onboarding (must configure DHCP manually or use `ztp_dhcp` on CVP) |
| `internet_access` | bool | false | Enable internet via internal `cloud` interface. Reserves `100.127.255.252/30` |
| `system_mac_address` | string | random | MAC address in colon-hex notation (e.g. `ab:cd:ef:12:34:56`) |
| `serial_number` | string | random | Custom serial number, max 32 chars |
| `ports` | list | - | Interface list or ranges. Max 128 interfaces. If omitted, ports from links section are auto-created |

#### Port Range Syntax

```yaml
ports:
  - Ethernet1-32           # Ethernet1 through Ethernet32
  - Ethernet2/1-8          # Ethernet2/1 through Ethernet2/8
  - Ethernet3-4/1          # Ethernet3/1 and Ethernet4/1
  - Ethernet4/1-2/1-2      # Ethernet4/1/1, Ethernet4/1/2, Ethernet4/2/1, Ethernet4/2/2
  - Ethernet5-6/1-2,7/1-2/1  # Complex multi-slot ranges
```

### CVP-Only Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `auto_configuration` | bool | false | Auto-configure CVP and onboard vEOS devices during lab deployment. Takes 12-16 min. Devices without `ztp: true` are auto-onboarded |
| `onboard_device` | bool | true | If false, CVP is configured but devices are not onboarded |
| `firstname` | string | `Act` | First name for CVP login account |
| `lastname` | string | `AutoConfig` | Last name for CVP login account |
| `email` | string | `auto_config_act@arista.com` | Email for CVP login account |
| `ntp_ip` | string | `0.pool.ntp.org` | NTP server FQDN for CVP |
| `telemetery_ingest_key` | string | auto | Required for older CVP versions, max 32 chars |
| `ztp_dhcp` | dict | - | Set `enabled: true` to configure CVP as DHCP server for ZTP switches. Required for full-auto ZTP onboarding |

**CVP auto_configuration supported versions:** 2020.1.x through 2025.1.x

### CVP Auto Configuration Example

```yaml
- cvp:
    ip_addr: 192.168.0.5
    node_type: cvp
    auto_configuration: true    # required for auto-config
    instance_type: xlarge
    ntp_ip: 0.pool.ntp.org      # optional
    firstname: Act              # optional
    lastname: AutoConfig        # optional
    email: "auto_config_act@arista.com"  # optional
    onboard_device: true        # optional, default true
```

## Links Section

Each connection defines a point-to-point link between two device interfaces.

```yaml
links:
- connection:
  - <hostname>:<interface>
  - <hostname>:<interface>
```

### Interface Naming

- Standard: `Ethernet1`, `Ethernet2`, ..., `Ethernet128`
- Sub-interfaces / slots: `Ethernet1/1`, `Ethernet2/1`
- Multi-level: `Ethernet4/1/1`
- Management: `Management0` (used for CVP connections in multi-CVP topologies)

### Link Rules

- Each connection is exactly 2 endpoints
- An interface can only appear in ONE connection
- Use `<hostname>:<interface>` format with NO spaces around the colon
- The `neighbors` section is **DEPRECATED** - always use `links`

## Naming Conventions

- Device names: max 100 characters, alphanumeric + dash + dot only: `[a-zA-Z0-9\-.]`
- Use prefixes for multi-DC topologies: `dc1-spine01`, `dc2-leaf01a`
- Common naming patterns:
  - Spines: `spine01`, `spine02` or `DC1-SPINE1`
  - Leaf pairs (MLAG): `leaf01a`/`leaf01b` or `DC1-LEAF1A`/`DC1-LEAF1B`
  - Border leaves: `br01a`/`br01b` or `BORDERLEAF1`
  - L2 leaves: `l2leaf01a`
  - Hosts/servers: `host01`, `Server01`
  - CVP: `cvp`, `cvp1`, `cvp2`
  - Generic nodes: `avd`, `ansible`

## IP Address Allocation Pattern

Use a consistent scheme within a /24 subnet (default):

| Role | Range Example |
|------|---------------|
| CVP | .5 |
| Automation server (generic) | .6 |
| DC1 Spines | .11-.12 |
| DC2 Spines | .21-.22 |
| DC1 Leaves | .101-.106 |
| DC2 Leaves | .111-.116 |
| Hosts | .201-.204 |
| Routers | .51-.52 |

## Common Topology Patterns

### 1. Spine-Leaf (Single DC)

Each leaf connects to both spines. Leaf pairs have MLAG peer-links (2 links for redundancy).

```
Spine side:  Ethernet1-N (one per leaf/border)
Leaf side:   Ethernet1 = spine01, Ethernet2 = spine02
MLAG:        Ethernet3, Ethernet4 (between a/b pair)
Host:        Ethernet5 (or higher)
```

### 2. Multi-DC with DCI

- Prefix all device names per DC: `dc1-`, `dc2-`
- Border leaves provide inter-DC connectivity
- Each DC can have its own CVP, or share one

### 3. MLAG Pair

Always create TWO peer-link connections between a/b pairs:

```yaml
- connection:
  - dc1-leaf01a:Ethernet3
  - dc1-leaf01b:Ethernet3
- connection:
  - dc1-leaf01a:Ethernet4
  - dc1-leaf01b:Ethernet4
```

### 4. Multi-CVP Topology

When using multiple CVPs, connect each CVP to its managed devices via `Management0`:

```yaml
- connection:
  - cvp1:Management0
  - DC1-SPINE1:Ethernet1
```

## Supported vEOS Device Models

When specifying `device_model`, ACT auto-creates ports matching the physical model:

- **7010**: 7010T-48, 7010TX-48, 7010TX-48-DC
- **7020**: 7020SR-24C2, 7020SR-32C2, 7020TR-48, 7020TRA-48
- **7050**: 7050QX-32S, 7050QX2-32S, 7050SX-128, 7050SX-64, 7050SX-72Q, 7050SX2-128, 7050SX2-72Q, 7050TX-48, 7050TX-64, 7050TX-72Q, 7050TX2-128, 7050CX3-32S, 7050CX3M-32S, 7050SX3-48YC8, 7050SX3-48YC12, 7050SX3-96YC8, 7050DX4-32S, 7050PX4-32S
- **7060**: 7060CX-32S, 7060CX2-32S, 7060DX4-32, 7060DX5-64S, 7060PX4-32, 7060SX2-48YC6
- **710**: 710P-12, 710P-16P
- **7130**: 7130-48G3S, 7130-48EHS, 7130-48G3S, 7130-48LBS, 7130-48LS, 7130-96LBS, 7130-96LS, 7130-96S, 7130B-32QD, 7130LBR-48S6QD
- **7170**: 7170-32C, 7170-32CD, 7170-64C, 7170B-64C
- **720**: 720XP-24Y6, 720XP-24ZY4, 720XP-48Y6, 720XP-48ZC2, 720XP-96ZC2
- **722**: 722XPM-48Y4, 722XPM-48ZY8
- **7260**: 7260CX-64, 7260CX3-64, 7260QX-64
- **7280**: 7280CR-48, 7280CR2M-30, 7280QR-C36, 7280QR-C72, 7280QRA-36S, 7280SR-48C6, 7280SRAM-48C6, 7280SRM-40XC2, 7280TR-48C6, 7280CR2-60, 7280CR2A-30, 7280CR2A-60, 7280CR2K-30, 7280CR2K-60, 7280SR2-48YC6, 7280SR2A-48YC6, 7280SR2K-48C6, 7280CR3-32D4, 7280CR3-32P4, 7280CR3-36S, 7280CR3-96, 7280CR3K-32D4, 7280CR3K-32D4A, 7280CR3K-32P4, 7280CR3K-36S, 7280CR3K-96, 7280CR3MK-32P4S, 7280DR3-24, 7280DR3K-24, 7280PR3-24, 7280PR3K-24, 7280SR3-40YC6, 7280SR3-48YC8, 7280SR3E-40YC6, 7280SR3K-48YC8, 7280SR3K-48YC8A

## ZTP Mode

ACT supports three ZTP approaches:

### 1. Manual ZTP

No flags in the topology file. Put switches into ZTP manually via CLI:

```text
switch# bash rm /mnt/flash/zerotouch-config
switch# write erase now
switch# reload now
```

Or via CVP: Network > Provisioning > right-click device > Factory Reset > Run CC.

### 2. EOS Only ZTP (topology flag)

Add `ztp: true` on each vEOS node. The switch boots in ZTP mode but is **not** auto-onboarded to CVP. You must configure DHCP manually (on CVP or a generic node).

A device in ZTP mode has only one user: **cvptemp**.

### 3. Full Auto ZTP (topology flag + CVP DHCP)

Combine `ztp: true` on vEOS nodes with `ztp_dhcp: {enabled: true}` on the CVP node. CVP acts as DHCP server and auto-onboards all ZTP switches. Devices appear in the **Undefined** container.

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
    ztp: true
```

## Constraints and Limitations

- **vEOS-lab**: MTU settings are ignored. Comment out MTU on interfaces for MLAG to work
- **CVP**: Only singlenode deployments are supported
- **Interfaces**: Maximum 128 per vEOS device
- **Internet access**: Disabled by default on vEOS devices. Enable with `internet_access: true`
- **IP reserved**: When `internet_access` is enabled, `100.127.255.252/30` is reserved
- **ZTP user**: Devices booted with `ztp: true` only have the `cvptemp` user (no `cvpadmin`)

## Building a Topology - Workflow

1. **Identify devices**: List all switches, servers, CVP instances needed
2. **Choose naming convention**: Use DC prefixes for multi-site designs
3. **Assign IP addresses**: Use a /24 management subnet with logical grouping
4. **Set global defaults**: Define `veos`, `cvp`, `generic` sections with shared credentials and versions
5. **Define nodes**: List each device with `node_type` and `ip_addr`
6. **Define links**: Map every physical cable as a `connection` entry
7. **Validate**: Ensure unique device names, unique interface usage per device, valid YAML syntax

## Validation Checklist

- [ ] All device names are unique across the entire topology
- [ ] All device names use only `[a-zA-Z0-9\-.]` characters (max 100 chars)
- [ ] Every node has `node_type` and `ip_addr`
- [ ] No interface is used in more than one connection
- [ ] IP addresses are unique across all nodes
- [ ] CVP node has `instance_type: xlarge` if `auto_configuration: true`
- [ ] YAML syntax is valid (2-space indentation, no tabs)
- [ ] MLAG pairs have exactly 2 peer-link connections (e.g., Ethernet3 + Ethernet4)
- [ ] `links` section uses the modern format (not deprecated `neighbors`)

## Complete Single-DC Example

```yaml
veos:
  username: arista
  password: arista
  version: 4.27.1F

cvp:
  username: root
  password: cvproot
  version: 2022.2.1

generic:
  version: CentOS-8-8.2.2004
  username: arista
  password: arista

nodes:
- DC1-SPINE1:
    ip_addr: 192.168.0.10
    node_type: veos
    ports:
      - Ethernet1/1-28
- DC1-SPINE2:
    ip_addr: 192.168.0.11
    node_type: veos
    ports:
      - Ethernet1/1-28
- DC1-LEAF1A:
    ip_addr: 192.168.0.12
    node_type: veos
- DC1-LEAF1B:
    ip_addr: 192.168.0.13
    node_type: veos
- DC1-LEAF2A:
    ip_addr: 192.168.0.14
    node_type: veos
- DC1-LEAF2B:
    ip_addr: 192.168.0.15
    node_type: veos
- DC1-L2LEAF1A:
    ip_addr: 192.168.0.16
    node_type: veos
- DC1-L2LEAF2A:
    ip_addr: 192.168.0.17
    node_type: veos
- Server01:
    ip_addr: 192.168.0.20
    node_type: generic
- Server02:
    ip_addr: 192.168.0.21
    node_type: generic
- cvp:
    ip_addr: 192.168.0.5
    node_type: cvp

links:
  # SPINE downlinks
  - connection:
      - DC1-SPINE1:Ethernet1/1
      - DC1-LEAF1A:Ethernet1
  - connection:
      - DC1-SPINE1:Ethernet2/1
      - DC1-LEAF1B:Ethernet1
  - connection:
      - DC1-SPINE1:Ethernet3/1
      - DC1-LEAF2A:Ethernet1
  - connection:
      - DC1-SPINE1:Ethernet4/1
      - DC1-LEAF2B:Ethernet1
  - connection:
      - DC1-SPINE2:Ethernet1/1
      - DC1-LEAF1A:Ethernet2
  - connection:
      - DC1-SPINE2:Ethernet2/1
      - DC1-LEAF1B:Ethernet2
  - connection:
      - DC1-SPINE2:Ethernet3/1
      - DC1-LEAF2A:Ethernet2
  - connection:
      - DC1-SPINE2:Ethernet4/1
      - DC1-LEAF2B:Ethernet2
  # MLAG DC1-LEAF1A - DC1-LEAF1B
  - connection:
      - DC1-LEAF1A:Ethernet3
      - DC1-LEAF1B:Ethernet3
  - connection:
      - DC1-LEAF1A:Ethernet4
      - DC1-LEAF1B:Ethernet4
  # MLAG DC1-LEAF2A - DC1-LEAF2B
  - connection:
      - DC1-LEAF2A:Ethernet3
      - DC1-LEAF2B:Ethernet3
  - connection:
      - DC1-LEAF2A:Ethernet4
      - DC1-LEAF2B:Ethernet4
  # L2 Leaf connections
  - connection:
      - DC1-L2LEAF1A:Ethernet1
      - DC1-LEAF1A:Ethernet5
  - connection:
      - DC1-L2LEAF1A:Ethernet2
      - DC1-LEAF1B:Ethernet5
  - connection:
      - DC1-L2LEAF2A:Ethernet1
      - DC1-LEAF2A:Ethernet5
  - connection:
      - DC1-L2LEAF2A:Ethernet2
      - DC1-LEAF2B:Ethernet5
  # Servers
  - connection:
      - DC1-L2LEAF1A:Ethernet3
      - Server01:Ethernet1
  - connection:
      - DC1-L2LEAF2A:Ethernet3
      - Server02:Ethernet1
```
