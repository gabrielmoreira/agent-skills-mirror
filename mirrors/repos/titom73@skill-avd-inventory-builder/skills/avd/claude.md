---
name: pyavd-network-config-builder
description: Full PyAVD skill for Claude Code with examples and advanced patterns
version: full
includes: core.md + advanced sections
---

<!--
  CLAUDE VERSION (Full)
  =====================
  This file extends core.md with detailed examples, schema references,
  and advanced integration patterns for Claude Code's large context window.
-->

# PyAVD Network Configuration Builder - Advanced

## Role

You are a **Network Automation Expert** specialized in PyAVD for Arista EOS.

Your capabilities:

- Build valid Arista EOS configurations using PyAVD schemas
- Design intent-based network architectures (EOS Designs)
- Generate device-specific configurations (EOS CLI Config Gen)
- Validate and convert network data models
- Use 450+ schema fragments for comprehensive coverage

---

## Quick Start Example

```python
from pyavd import validate_inputs, get_avd_facts, get_device_structured_config, get_device_config

# 1. Define network intent
design_intent = {
    "fabric_name": "MY_FABRIC",
    "spine": {
        "defaults": {"platform": "vEOS-lab", "bgp_as": "65000"},
        "nodes": [{"name": "spine1", "id": 1, "mgmt_ip": "192.168.0.10/24"}]
    },
    "l3leaf": {
        "defaults": {
            "platform": "vEOS-lab",
            "loopback_ipv4_pool": "10.255.0.0/27",
            "vtep_loopback_ipv4_pool": "10.255.1.0/27"
        },
        "node_groups": [{
            "group": "LEAF1",
            "bgp_as": "65001",
            "nodes": [{"name": "leaf1", "id": 1, "mgmt_ip": "192.168.0.11/24"}]
        }]
    }
}

# 2. Validate and generate
result = validate_inputs(design_intent)
assert not result.failed

avd_facts = get_avd_facts(design_intent)
structured_config = get_device_structured_config("leaf1", design_intent, avd_facts)
eos_config = get_device_config(structured_config)
print(eos_config)
```

---

## Core Functions

```python
from pyavd import (
    validate_inputs,              # Validate eos_designs inputs
    validate_structured_config,   # Validate eos_cli_config_gen inputs
    get_device_structured_config, # Generate structured config from design
    get_device_config,            # Generate CLI config from structured config
    get_avd_facts,                # Generate AVD facts from inputs
)
```

---

## Two Main Schemas

### EOS CLI Config Gen (210 fragments)

**Purpose**: Low-level, device-specific configuration

| Category   | Elements                                            |
| ---------- | --------------------------------------------------- |
| Interfaces | ethernet, loopback, vlan, port-channel, tunnel      |
| Routing    | router_bgp, router_ospf, router_isis, static_routes |
| VLANs/VRFs | vlans, vrfs, vxlan_interface                        |
| ACLs       | access_lists, ip_access_lists, mac_access_lists     |
| Management | aaa, snmp, logging, ntp, management_api_http        |
| QoS        | qos, qos_profiles, policy_maps, class_maps          |

### EOS Designs (243 fragments)

**Purpose**: High-level, intent-based design

| Category         | Elements                                             |
| ---------------- | ---------------------------------------------------- |
| Fabric Topology  | fabric_name, spine, l3leaf, l2leaf, super_spine      |
| Node Config      | devices, device_profiles, connected_endpoints        |
| Network Services | network_services, l2vlan_profiles, svi_profiles      |
| BGP              | bgp_as, bgp_peer_groups, evpn_*                      |
| Underlay/Overlay | underlay_routing_protocol, overlay_routing_protocol  |
| CV Pathfinder    | wan_mode, wan_carriers, cv_pathfinder_regions        |

---

## Schema Structure

```yaml
# Example: VLANs schema
vlans:
  type: list
  primary_key: id
  items:
    type: dict
    keys:
      id:
        type: int
        description: VLAN ID
      name:
        type: str
        description: VLAN Name
      state:
        type: str
        valid_values: ["active", "suspend"]
```

---

## Network Services Design Pattern

```python
# Add VLANs and VRFs to fabric
network_services = {
    "tenants": [{
        "name": "TENANT_A",
        "mac_vrf_vni_base": 10000,
        "vrfs": [{
            "name": "VRF_A",
            "vrf_vni": 20,
            "svis": [
                {"id": 10, "name": "VLAN10", "ip_address_virtual": "10.10.10.1/24"},
                {"id": 20, "name": "VLAN20", "ip_address_virtual": "10.10.20.1/24"}
            ]
        }]
    }]
}
```

---

## Connected Endpoints Pattern

```python
# Connect servers/hosts to leaf switches
connected_endpoints = {
    "servers": [{
        "name": "SERVER01",
        "adapters": [{
            "endpoint_ports": ["Eth1", "Eth2"],
            "switch_ports": ["Ethernet5", "Ethernet5"],
            "switches": ["leaf1", "leaf2"],
            "port_channel": {"mode": "active", "description": "To Server01"},
            "vlans": 10
        }]
    }]
}
```

---

## MLAG Configuration Pattern

```python
# L3 Leaf MLAG pair
l3leaf_node_group = {
    "group": "LEAF_PAIR1",
    "bgp_as": 65101,
    "mlag": True,
    "mlag_peer_ipv4_pool": "10.255.252.0/24",
    "nodes": [
        {"name": "leaf1a", "id": 1, "mgmt_ip": "192.168.0.11/24"},
        {"name": "leaf1b", "id": 2, "mgmt_ip": "192.168.0.12/24"}
    ],
    "uplink_interfaces": ["Ethernet49", "Ethernet50"],
    "mlag_interfaces": ["Ethernet51", "Ethernet52"]
}
```

---

## Validation Workflow

```python
from pyavd import validate_inputs, validate_structured_config

# 1. Validate design inputs
design_result = validate_inputs(design_intent)
if design_result.failed:
    for error in design_result.validation_errors:
        print(f"Design Error: {error}")

# 2. Validate structured config
struct_result = validate_structured_config(structured_config)
if struct_result.failed:
    for error in struct_result.validation_errors:
        print(f"Config Error: {error}")

# 3. Check deprecation warnings
for warning in design_result.deprecation_warnings:
    print(f"Deprecation: {warning}")
```

---

## Schema Tools Advanced Usage

```python
from pyavd._schema_tools import AvdSchemaTools

# Get schema documentation
schema_tools = AvdSchemaTools(schema_id="eos_designs")
doc = schema_tools.get_documentation(key_path="spine.defaults.bgp_as")
print(doc)

# Convert data types automatically
data = {"bgp_as": "65000"}  # String
converted = schema_tools.convert_data(data)
# bgp_as is now properly typed
```

---

## Troubleshooting

### Common Validation Errors

| Error | Cause | Solution |
| ----- | ----- | -------- |
| `Invalid type` | Wrong data type | Check schema for expected type |
| `Missing required` | Required field absent | Add the required field |
| `Invalid value` | Value not in valid_values | Use allowed values |
| `Key not allowed` | Unknown key | Check schema for valid keys |

### Debug Pattern

```python
import json

# Pretty print structured config for debugging
print(json.dumps(structured_config, indent=2))

# Check generated config sections
for section in ["router_bgp", "vlans", "ethernet_interfaces"]:
    if section in structured_config:
        print(f"=== {section} ===")
        print(json.dumps(structured_config[section], indent=2))
```

---

## Resources

- [PyAVD Documentation](https://avd.arista.com/stable/docs/pyavd/pyavd.html)
- [EOS CLI Config Gen](https://avd.arista.com/stable/roles/eos_cli_config_gen/index.html)
- [EOS Designs](https://avd.arista.com/stable/roles/eos_designs/index.html)
- [GitHub](https://github.com/aristanetworks/avd)
