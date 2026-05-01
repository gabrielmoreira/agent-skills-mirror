---
name: cisco-log-to-json-parsing
description: Parse Cisco switch terminal log files (.log) into structured JSON. Covers IOS, IOS-XE, and NX-OS platforms. Use when asked to parse switch logs, extract network device info, build topology from CDP, or structure Cisco CLI output.
metadata:
  author: louie
  version: "1.0.0"
  argument-hint: <log-file-or-directory>
---

# Cisco Switch Log → Structured JSON

Parse Cisco switch terminal session log files into `devices.json` and `topology.json`. Supports IOS, IOS-XE, and NX-OS platforms. Uses only Python stdlib (`json`, `re`, `os`, `sys`, `pathlib`).

## When to Apply

- Parsing Cisco switch `.log` files (terminal session captures)
- Extracting device info, interfaces, VLANs, CDP neighbors, phones
- Building network topology from CDP data
- Generating replacement/migration documentation
- Any task involving structured data extraction from Cisco CLI output

## Input Format

Log files are terminal session captures (UTF-8 with BOM, CRLF line endings). Each file contains output from multiple `show` commands executed on one switch. Command sections are delimited by the switch prompt pattern:

```
hostname#show version
... output ...
hostname#show cdp nei
... output ...
```

### Prompt Detection Regex

```python
PROMPT_CMD_RE = re.compile(r"^(?P<host>[^#\s]+(?:\([^\)]*\))?)#\s*(?P<cmd>.*)$")
```

This matches lines like `Switch01#show version`, `N5K-01(config)#show run`, etc.

---

## Supported Commands & Parsing Details

### 1. `show version`

**Purpose**: Extract hostname, IOS version, uptime, serial number, model, platform type.

**Canonical match**: Any command starting with `show version`, `sh version`.

**Platform detection**:
| Text in output | Platform |
|---|---|
| `Nexus Operating System` or `NX-OS` | NX-OS |
| `IOS XE` or `IOS-XE` | IOS-XE |
| `Cisco IOS Software` (without XE) | IOS |
| None of the above | Default to IOS |

**Key regex patterns**:
```python
# NX-OS version
r"^\s*(?:kickstart|system):\s*version\s+(.+)"

# IOS/IOS-XE version: line containing "Cisco IOS" AND "Version"

# Uptime
r"\buptime is (.+)"            # IOS/IOS-XE
r"Kernel uptime is (.+)"       # NX-OS

# Serial number
r"System serial number\s*[: ]\s*(\S+)"   # NX-OS
r"Processor\s+Board\s+ID\s+(\S+)"        # IOS

# Model
r"^cisco\s+(\S+)"  # + line must contain "processor" or "chassis"
r"Model Number\s*:\s*(\S+)"              # NX-OS
```

**Fallback**: If model/serial not found in `show version`, fall back to `show inventory` (prefer entries named "chassis", "switch", or "stack").

---

### 2. `show inventory`

**Purpose**: Extract SFP/optic modules and fallback model/serial.

**Canonical match**: `show inv`, `show inventory`, `sh inv`.

**Parsing**: Two-line blocks:
```
NAME: "TenGigabitEthernet1/1", DESCR: "SFP-10G-SR"
PID: SFP-10GBase-SR , VID: V03 , SN: AVD2048S14A
```

**Key regex**:
```python
r'NAME:\s*"([^"]+)"'
r'DESCR:\s*"([^"]+)"'
r'PID:\s*([^,]+)'
r'SN:\s*([^,\s]+)'
```

**SFP module filter**: Entry `name` must contain a digit AND contain `/` or start with `letter+digit` (e.g., `GigabitEthernet0/1`, `Ethernet1/1`).

---

### 3. `show vlan brief`

**Purpose**: Extract VLAN ID, name, status.

**Canonical match**: `show vlan`, `sh vlan`.

**Table header**: `VLAN  Name  Status`

**Row regex**:
```python
r"^\s*(\d+)\s+(\S+)\s+(\S+)"
```

Deduplicate by VLAN ID (keep last seen).

---

### 4. `show int description`

**Purpose**: Extract interface operational status, protocol status, description.

**Canonical match**: Commands containing `int` + `description` or `interface` + `description`.

**Three sub-table modes** (detected by header line):

| Header pattern | Mode | Platform |
|---|---|---|
| `Interface  Status  Protocol` | `ios` | IOS / IOS-XE |
| `Port  Type  Speed  Description` | `nxos_physical` | NX-OS physical ports |
| `Interface  Description` (no "Status") | `nxos_logical` | NX-OS logical interfaces |

**IOS parsing regex**:
```python
r"^\s*(\S+)\s{2,}(.+?)\s{2,}(\S+)\s*(.*)$"
# Groups: interface, status, protocol, description
```

**NX-OS physical**:
```python
r"^\s*(\S+)\s+(\S+)\s+(\S+)\s*(.*)$"
# Groups: interface, type, speed, description
```

**NX-OS logical**:
```python
r"^\s*(\S+)\s+(.*)$"
# Groups: interface, description
```

---

### 5. `show int status`

**Purpose**: Extract interface name (description), oper status, VLAN, duplex, speed, media type.

**Canonical match**: Commands containing `int` + `status` or `interface` + `status`.

**Table header**: `Port  Name  Status  Vlan  Duplex  Speed  Type`

**CRITICAL: Column-position-based parsing**. The header line is used to find the start position of each column:

```python
col_pos = {
    "Port": line.find("Port"),
    "Name": line.find("Name"),
    "Status": line.find("Status"),
    "Vlan": line.find("Vlan"),
    "Duplex": line.find("Duplex"),
    "Speed": line.find("Speed"),
    "Type": line.find("Type"),
}
# Then slice each data line by column positions:
port   = line[col_pos["Port"]   : col_pos["Name"]].strip()
name   = line[col_pos["Name"]   : col_pos["Status"]].strip()
status = line[col_pos["Status"] : col_pos["Vlan"]].strip()
vlan   = line[col_pos["Vlan"]   : col_pos["Duplex"]].strip()
duplex = line[col_pos["Duplex"] : col_pos["Speed"]].strip()
speed  = line[col_pos["Speed"]  : col_pos["Type"]].strip()
media  = line[col_pos["Type"]:].strip()
```

**Fallback** (if line too short for column slicing): split by whitespace, take first 5 fields as `port, status, vlan, duplex, speed`, rest as media.

---

### 6. `show cdp nei` (brief)

**Purpose**: Extract CDP neighbor device ID, local interface, capability, platform, remote port.

**Canonical match**: Commands containing `cdp` + `nei` (but NOT `detail`).

**Table header regex**:
```python
r"Device[\s-]ID\s+Local Intrfce\s+H[ol]*dtme\s+Capability\s+Platform\s+Port ID"
```

**Platform detection from header**:
- `Device-ID` or `Hldtme` in header → NX-OS mode
- Otherwise → IOS mode

**Column positions** are detected from header (same approach as `show int status`).

**NX-OS special handling**: Device IDs can wrap to the next line. If a line is shorter than the `Port ID` column position and contains no double-spaces, it's a "pending device" that belongs to the next data line.

**NX-OS multi-split parsing** (by `\s{2,}`):
- 6 parts → `device_id, local_if, holdtme, capability, platform, port_id`
- 5 parts → either `device_id` is pending (starts with interface-like pattern) or last field combines `platform + port_id`
- 4 parts → `device_id` is pending; `local_if, holdtme, capability, platform+port_id`

**Interface-like detection** (for NX-OS pending device logic):
```python
r"^(?:Eth|Po|Port-channel|Vlan|Lo|mgmt)\S*"
```

**Platform+Port splitting** (when combined in one field):
```python
re.split(r"\s+(?=\S+$)", text.strip(), maxsplit=1)
```

**Deduplication key**: `(normalized_device_id, normalized_local_if, normalized_remote_port)` — all lowercased.

---

### 7. `show cdp nei detail`

**Purpose**: Extract detailed CDP info: IP address, platform, capabilities, interfaces, native VLAN, software version, power drawn.

**Canonical match**: Commands containing `cdp` + `nei` + `detail`.

**Block delimiter**: `Device ID: <name>`

**Key regex patterns**:
```python
# IP address
r"IP address:\s*([0-9.]+)"

# Platform + Capabilities (single line)
r"Platform:\s*([^,]+),\s*Capabilities:\s*(.+)$"

# Interface mapping
r"Interface:\s*([^,]+),\s*Port ID \(outgoing port\):\s*(.+)$"

# Native VLAN
r"Native VLAN:\s*(\S+)"

# Power drawn
r"Power drawn:\s*(.+)$"
```

**Software version**: Lines after `Version` until blank line. Take first non-blank line.

---

### 8. `show running-config`

**Purpose**: Extract per-interface configuration and hostname.

**Canonical match**: `show run`, `show running`, `sh run`.

**Hostname**: `hostname <name>` line.

**Interface blocks**: Start with `interface <name>` line. All indented lines below belong to that interface until the next `interface` or non-indented line.

**Config fields extracted per interface**:

| Config line | JSON field | Notes |
|---|---|---|
| `description <text>` | `description` | |
| `switchport mode access\|trunk` | `switchport_mode` | Only `access` or `trunk` |
| `switchport access vlan <N>` | `switchport_access_vlan` | Integer |
| `switchport trunk allowed vlan [add] <list>` | `switchport_trunk_allowed_vlans` | String, handles `add` keyword |
| `switchport voice vlan <N>` | `switchport_voice_vlan` | Integer |
| `switchport trunk native vlan <N>` | `switchport_trunk_native_vlan` | Integer |
| `shutdown` / `no shutdown` | `shutdown` | Boolean |
| `spanning-tree portfast` | `spanning_tree_portfast` | Boolean |
| `speed <value>` | `speed` | String |
| `channel-group <N>` | `channel_group` | Integer (group number) |
| `ip address <IP> <mask>` | `ip_address` | IP string (not `dhcp`) |
| `no ip address` | `ip_address` | Set to `null` |

---

### 9. `show ip int brief`

**Purpose**: Extract IP addresses assigned to interfaces.

**Canonical match**: Commands starting with `show ip` + containing `int`/`inter` + `bri`/`brief`.

**Two table formats**:

| Header | Platform | Columns |
|---|---|---|
| `Interface  IP-Address  OK?  Method` | IOS | 6+ columns: iface, ip, ok, method, status, protocol |
| `Interface  IP Address  Interface Status` | NX-OS | 3+ columns: iface, ip, status (rest joined) |

**Management IP selection priority**:
1. `mgmt0` / `management0` (NX-OS management port)
2. `Vlan102`
3. `Vlan1`
4. Any `Vlan` interface
5. Any other interface
- Within each tier, prefer `up` status over down.
- Exclude `unassigned` and `0.0.0.0`.

---

### 10. `show inter trunk`

**Purpose**: Extract trunk interface native VLAN and allowed VLANs.

**Canonical match**: Commands containing `trunk` + (`show inter` or `show int` or `show interface`).

**Two sub-tables**:

1. **Native VLAN table** — header: `Port  Mode  Encapsulation  Status  Native`
   - Column-position parsing (same pattern as `show int status`)
   
2. **Allowed VLANs table** — header: `Port  Vlans allowed on trunk`
   - Whitespace split: first token = port, rest = allowed VLANs

**Fallback**: If `show inter trunk` yields no trunks, derive from `show running-config` — any interface with `switchport_mode == "trunk"` becomes a trunk entry.

---

## Interface Name Normalization

All interface names are normalized to their full form:

```python
prefix_map = {
    "Gi":  "GigabitEthernet",
    "Gig": "GigabitEthernet",
    "Te":  "TenGigabitEthernet",
    "Ten": "TenGigabitEthernet",
    "Fa":  "FastEthernet",
    "Eth": "Ethernet",
    "Po":  "Port-channel",
    "Vl":  "Vlan",
}
```

**Pattern**: `^([A-Za-z]+)([\d/].*)$` → lookup prefix → `{full_prefix}{rest}`

Whitespace is stripped first (`re.sub(r"\s+", "", raw)`). Names without digits are returned as-is.

---

## Device ID Normalization

```python
def normalize_device_id(device_id):
    base = device_id.strip()
    base = re.sub(r"\(.*\)$", "", base)  # strip parenthesized suffix
    if "." in base:
        base = base.split(".", 1)[0]     # strip domain (e.g., "switch.domain" → "switch")
    return base
```

---

## CDP Neighbor Merging & Phone Detection

### Merge Logic

Brief (`show cdp nei`) and detail (`show cdp nei detail`) are parsed separately, then merged by key `(normalized_device_id, normalized_local_interface)`. Detail enriches brief with: IP address, full capabilities list, remote interface, native VLAN, software version, power drawn.

### Phone Detection

A CDP neighbor is classified as a phone when:
```python
def is_phone_neighbor(capabilities, platform, remote_port):
    caps = " ".join(capabilities).lower()
    # Infrastructure devices are NEVER phones
    if any(kw in caps for kw in ("switch", "router", "bridge")):
        return False
    # Explicit phone capability
    if "phone" in caps:
        return True
    # Platform-based detection
    if any(kw in platform.lower() for kw in ("t27g", "yealink", "spa")):
        return True
    # Port-based detection
    if "wan port" in remote_port.lower():
        return True
    return False
```

---

## Port-Channel Derivation

Port-channels are derived from `show running-config`:
1. Scan all interfaces for `channel-group <N>` → build member lists per group
2. Scan interfaces named `Port-channel<N>` → get their config (mode, etc.)
3. Combine: `{ name: "Port-channel{N}", members: [...], mode: "trunk"|"access"|null }`

---

## Topology Building

### Nodes
One node per parsed device: `{ id, model, serial, role, management_ip, platform_type }`.

**Role assignment**:
| Model contains | Role |
|---|---|
| `N5K`, `NEXUS5548`, `C9300` | core |
| `C9200` | distribution |
| `2960`, `C2960` | access |
| Other | access (default) |

### Links
Built from CDP neighbors (excluding phones):
1. Match `neighbor_device` against known hostnames (case-insensitive, normalized)
2. Sort source/target alphabetically for consistent deduplication
3. Dedup key: `(source, target, source_port, target_port)` — all lowercased
4. On collision, keep link with highest "score" (count of non-null fields: speed, media, link_type)

**Link type**: `trunk` if either endpoint's port appears in trunk map; else `access`.

**Speed label**:
| Speed value | Label |
|---|---|
| Contains `10g` or `10000` | 10G |
| Contains `1000` or `1g` | 1G |
| Contains `100` | 100M |

### External Devices
CDP neighbors not matching any known hostname → `external_devices` list. Type is `router` if capabilities contain "router"/"r" or platform contains "c1111"; else `switch`.

---

## Output JSON Schema

### `devices.json`

```json
[
  {
    "hostname": "Switch01",
    "model": "WS-C2960X-48FPD-L",
    "serial_number": "FCW2048S14A",
    "ios_version": "Cisco IOS Software, ...",
    "uptime": "1 year, 2 weeks, 3 days, ...",
    "platform_type": "IOS",
    "management_ip": "10.1.1.1",
    "vlans": [
      { "id": 1, "name": "default", "status": "active" }
    ],
    "interfaces": {
      "GigabitEthernet0/1": {
        "description": "To-Server",
        "oper_status": "connected",
        "protocol": null,
        "vlan": "102",
        "duplex": "a-full",
        "speed": "a-1000",
        "media_type": "10/100/1000BaseTX",
        "config": {
          "switchport_mode": "access",
          "switchport_access_vlan": 102,
          "switchport_trunk_allowed_vlans": null,
          "switchport_voice_vlan": 50,
          "switchport_trunk_native_vlan": null,
          "description": "To-Server",
          "shutdown": false,
          "spanning_tree_portfast": true,
          "speed": null,
          "channel_group": null,
          "ip_address": null
        }
      }
    },
    "cdp_neighbors": [
      {
        "neighbor_device": "CoreSwitch",
        "local_interface": "GigabitEthernet0/49",
        "remote_interface": "GigabitEthernet1/0/1",
        "neighbor_platform": "cisco WS-C9300-24T",
        "neighbor_ip": "10.1.1.254",
        "capabilities": ["Switch", "IGMP"],
        "is_phone": false
      }
    ],
    "phones": [
      {
        "device_id": "SEP001122334455",
        "local_interface": "GigabitEthernet0/5",
        "ip": "10.1.50.10",
        "platform": "Cisco IP Phone 8845",
        "power_drawn": "12600 mW"
      }
    ],
    "ip_interfaces": [
      { "interface": "Vlan1", "ip_address": "10.1.1.1", "status": "up" }
    ],
    "trunks": [
      {
        "interface": "GigabitEthernet0/49",
        "native_vlan": "1",
        "allowed_vlans": "1-4094"
      }
    ],
    "port_channels": [
      {
        "name": "Port-channel1",
        "members": ["GigabitEthernet0/49", "GigabitEthernet0/50"],
        "mode": "trunk"
      }
    ],
    "sfp_modules": [
      {
        "interface": "TenGigabitEthernet1/1",
        "pid": "SFP-10GBase-SR",
        "sn": "AVD2048S14A",
        "description": "SFP-10G-SR"
      }
    ]
  }
]
```

### `topology.json`

```json
{
  "nodes": [
    {
      "id": "Switch01",
      "model": "WS-C2960X-48FPD-L",
      "serial": "FCW2048S14A",
      "role": "access",
      "management_ip": "10.1.1.1",
      "platform_type": "IOS"
    }
  ],
  "links": [
    {
      "source": "CoreSwitch",
      "source_port": "GigabitEthernet1/0/1",
      "target": "Switch01",
      "target_port": "GigabitEthernet0/49",
      "speed": "1G",
      "link_type": "trunk",
      "media": "10/100/1000BaseTX"
    }
  ],
  "external_devices": [
    {
      "device_id": "ISP-Router",
      "platform": "cisco C1111-8P",
      "ip": "203.0.113.1",
      "connected_to": "CoreSwitch",
      "connected_port": "GigabitEthernet1/0/24",
      "type": "router"
    }
  ]
}
```

---

## Command Canonicalization

The parser recognizes abbreviated Cisco commands and maps them to canonical forms:

```python
def canonical_command(cmd_text):
    cmd = cmd_text.strip().lower()
    # show version / sh version         → "show version"
    # show inv / show inventory / sh inv → "show inventory"
    # show vlan / sh vlan                → "show vlan brief"
    # cdp + nei + detail                 → "show cdp nei detail"
    # cdp + nei (no detail)              → "show cdp nei"
    # int + description                  → "show int description"
    # int + status                       → "show int status"
    # show run / show running / sh run   → "show running-config"
    # show ip + int/inter + bri/brief    → "show ip int brief"
    # trunk + show int/inter/interface   → "show inter trunk"
```

---

## Processing Pipeline

```
1. read_log()               → lines[] (UTF-8-sig, error=replace)
2. parse_command_sections()  → sections[] {cmd, raw_cmd, hostname, lines[]}
3. Group sections by canonical cmd
4. For each device log file:
   a. parse_show_version()     → hostname, model, serial, ios_version, uptime, platform_type
   b. parse_inventory()        → sfp_modules[], fallback model/serial
   c. parse_running_config()   → per-interface configs, hostname fallback
   d. parse_vlan_brief()       → vlans[]
   e. parse_int_description()  → populate interfaces{} oper_status, protocol, description
   f. parse_int_status()       → populate interfaces{} vlan, duplex, speed, media_type
   g. parse_cdp_neighbors()    → cdp brief list
   h. parse_cdp_detail()       → cdp detail list
   i. merge_cdp()              → cdp_neighbors[], phones[]
   j. parse_ip_int_brief()     → ip_interfaces[], management_ip
   k. parse_interface_trunks() → trunks[] (fallback from running-config)
   l. derive_port_channels()   → port_channels[]
5. build_topology()            → { nodes[], links[], external_devices[] }
6. Write devices.json, topology.json
```

---

## Common Pitfalls

1. **NX-OS CDP wrapping**: Device IDs longer than the column width wrap to the next line. Must buffer "pending device" lines.
2. **Column-position parsing**: `show int status` and `show cdp nei` use fixed-width columns. DO NOT split by whitespace — interface names can contain spaces in the Name column.
3. **Trunk fallback**: Some switches don't support `show inter trunk`. Fall back to running-config `switchport mode trunk` interfaces.
4. **Phone vs infrastructure**: Nexus 5K with CVTA advertises "Phone" capability but is a switch. Always check for infrastructure keywords first.
5. **BOM handling**: Log files may have UTF-8 BOM. Use `encoding="utf-8-sig"` when reading.
6. **CDP dedup**: Same neighbor can appear in both brief and detail. Merge by `(device_id, local_interface)` key, don't create duplicates.
