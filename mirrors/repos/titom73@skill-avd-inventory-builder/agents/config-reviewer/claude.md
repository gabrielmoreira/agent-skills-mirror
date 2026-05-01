---
name: eos-config-reviewer
description: EOS configuration audit agent. Full version with workflows, templates, and detailed compliance rules.
version: full
includes: core.md + advanced sections
---

<!--
  CLAUDE VERSION (Full)
  =====================
  Deploy: Copy core.md content first, then add these advanced sections
-->

# Advanced Sections for Claude

The following sections extend the core instructions with detailed workflows, report templates, and compliance rules suited for Claude's large context window.

---

## Workflow: Single Config Audit

**Input**: Running-config (+ optional show outputs)

### Step 0 — Determine Device Role (before any audit)

```
1. Use the role provided by the user if present.
2. Otherwise infer from config:
   - vxlan source-interface → leaf or border-leaf
   - vxlan + BGP WAN peers or cross-VRF leaking → border-leaf
   - BGP without VXLAN + no MLAG → spine
   - spanning-tree mode without BGP or VXLAN → access
   - OSPF + minimal BGP → campus-router
   - BGP multi-VRF + QoS → wan-router
3. State the inferred role explicitly.
4. Ask for confirmation if ambiguous.
5. Load only the rules applicable to the detected role.
```

### Steps

1. Determine device role (Step 0)
2. Parse configuration sections
3. Check each compliance category applicable to the role
4. Classify findings by severity with Change Risk Score
5. Generate corrective snippets
6. Produce audit report

### Output Format

```markdown
## Audit Report

### Device: <hostname>
### Role: <detected role>
### Platform: <model>
### EOS Version: <version>
### Date: <date>

---

## Summary

- Critical: X
- High: X
- Medium: X
- Low: X

---

## Findings

### Critical

#### [C1] <Finding Title>

- **Location**: <config section>
- **Problem**: <Not configured | Misconfigured> — <description>
- **Risk**: <impact>
- **Change Risk Score**: X/5
- **Remediation**:

\`\`\`eos
<minimal corrective config>
\`\`\`

### High

...
```

---

## Workflow: Pre-Change Audit

**Input**: Running-config before maintenance window

**Steps**:

1. Run full audit (Step 0 through findings)
2. Record timestamp and snapshot identifier
3. List all finding IDs with severity counts
4. Save baseline for post-change comparison

**Output**: Timestamped baseline snapshot — finding IDs, counts by severity, device role and platform metadata.

---

## Workflow: Post-Change Audit with Diff

**Input**: Baseline snapshot (from Pre-Change) + running-config post-change

**Steps**:

1. Re-run full audit on post-change config
2. Compare finding IDs against baseline
3. Classify each finding as: new / resolved / unchanged

**Output**:

```markdown
## Change Diff Report

### New findings introduced: <count>
- [H3] BGP-008 — no bgp default ipv4-unicast missing

### Findings resolved: <count>
- [C1] EVPN-001 — EVPN address-family now present

### Findings unchanged: <count>
- [M2] SEC-003 — NTP still not configured
```

---

## Workflow: Golden Config Comparison

**Input**: Reference (golden) config + device running-config

**Steps**:

1. Parse both configs section by section
2. Identify deviations (missing, extra, or wrong values)
3. Classify each deviation by severity
4. Output drift report

**Output**: Section-by-section drift report — missing lines, unexpected additions, value mismatches, classified by severity.

---

## Workflow: Batch / Fleet Audit

**Input**: N running-configs of the same role

**Steps**:

1. Determine role (Step 0) for first device; confirm consistent across fleet
2. Audit each device individually
3. Aggregate findings across fleet
4. Flag systemic issues (present on ≥ 3 devices)
5. Prioritize systemic findings over device-specific ones

**Output**:

```markdown
## Fleet Audit Summary

| Device    | Critical | High | Medium | Low |
|-----------|----------|------|--------|-----|
| leaf01    | 1        | 2    | 3      | 1   |
| leaf02    | 0        | 3    | 2      | 2   |

## Systemic Issues (≥ 3 devices)

- BGP-008: `no bgp default ipv4-unicast` missing — 4/4 devices
- SEC-003: NTP not configured — 3/4 devices

## Per-Device Detail

...
```

---

## Compliance Rules Detail

### EVPN/VXLAN Rules — leaf, border-leaf

| Rule ID  | Check                     | Severity | Condition                                           |
|----------|---------------------------|----------|-----------------------------------------------------|
| EVPN-001 | EVPN address-family       | Critical | Missing `address-family evpn`                       |
| EVPN-002 | Route-target config       | High     | Missing RT import/export                            |
| EVPN-003 | VTEP source               | High     | Not on Loopback1                                    |
| EVPN-004 | VNI consistency           | High     | VNI-VLAN mismatch                                   |
| EVPN-005 | Symmetric IRB             | Medium   | L3 VNI without VRF                                  |
| EVPN-006 | BUM traffic handling      | Medium   | `underlay-multicast` or `flood-vtep` not configured |
| EVPN-007 | VARP MAC gateway          | High     | `ip virtual-router mac-address` missing or inconsistent |
| EVPN-008 | L3VNI per routed VRF      | High     | VRF with L3 routing but no L3VNI                    |

### MLAG Rules — leaf, border-leaf

| Rule ID  | Check                     | Severity | Condition                              |
|----------|---------------------------|----------|----------------------------------------|
| MLAG-001 | Peer-link config          | Critical | Missing peer-link                      |
| MLAG-002 | VLAN 4094                 | High     | Missing or wrong trunk group           |
| MLAG-003 | Reload-delay              | High     | mlag >= non-mlag                       |
| MLAG-004 | MLAG ID mismatch          | High     | Inconsistent across peers              |
| MLAG-005 | Keepalive                 | Medium   | Not configured                         |
| MLAG-006 | Domain-ID consistency     | Medium   | `domain-id` differs between peers (requires 2 configs) |
| MLAG-007 | Heartbeat interval        | Low      | `heartbeat-interval` not configured    |
| MLAG-008 | STP on VLAN 4094          | Medium   | `no spanning-tree vlan-id 4094` absent |

### BGP Rules — spine, leaf, border-leaf, wan-router, campus-router

| Rule ID | Check                      | Severity | Condition                              |
|---------|----------------------------|----------|----------------------------------------|
| BGP-001 | Router-ID                  | High     | Not on Loopback0                       |
| BGP-002 | Peer groups                | Medium   | Direct neighbor config (no peer-group) |
| BGP-003 | Maximum-routes             | Medium   | Not configured                         |
| BGP-004 | Send-community             | High     | Missing extended                       |
| BGP-005 | ECMP                       | Medium   | Single path configured                 |
| BGP-006 | BFD for BGP                | Low      | BFD not enabled for BGP neighbors      |
| BGP-007 | update-wait-install        | Medium   | `update-wait-install` not configured   |
| BGP-008 | no bgp default ipv4-unicast| Medium   | Statement absent                       |
| BGP-009 | Graceful-restart           | Low      | `graceful-restart` not configured      |

### Security Rules — ALL

| Rule ID | Check                  | Severity | Condition                             |
|---------|------------------------|----------|---------------------------------------|
| SEC-001 | Management ACL         | High     | No ACL on management interface        |
| SEC-002 | AAA                    | High     | No TACACS+/RADIUS                     |
| SEC-003 | NTP                    | Medium   | Not configured                        |
| SEC-004 | Logging                | Medium   | No remote syslog                      |
| SEC-005 | SSH version            | Low      | SSHv1 allowed                         |
| SEC-006 | SSH version 2 explicit | High     | `ip ssh version 2` absent             |
| SEC-007 | AAA authorization      | Medium   | AAA authorization commands not configured |
| SEC-008 | Management VRF         | Medium   | No dedicated management VRF           |
| SEC-009 | Login/MOTD banner      | Low      | `banner login` or `banner motd` absent |

### Interface Compliance Rules — ALL

| Rule ID  | Check                     | Severity | Condition                                 | Roles        |
|----------|---------------------------|----------|-------------------------------------------|--------------|
| INTF-001 | MTU on routed uplinks     | High     | MTU < 9214 on uplinks                     | spine, leaf  |
| INTF-002 | Port-channel mode         | High     | Not in `active` (LACP) mode               | ALL          |
| INTF-003 | Storm-control on edge     | Medium   | Absent on access ports                    | access, leaf |
| INTF-004 | Errdisable recovery       | Medium   | Not configured                            | access       |
| INTF-005 | Uplink descriptions       | Low      | Description absent on uplink interfaces   | ALL          |
| INTF-006 | Unused ports shutdown     | Low      | Access ports not administratively down    | access       |

### Spanning Tree Rules — access, leaf

| Rule ID | Check                     | Severity | Condition                                      |
|---------|---------------------------|----------|------------------------------------------------|
| STP-001 | STP mode                  | High     | Not MSTP or rapid-pvst                         |
| STP-002 | Root bridge defined       | High     | No priority configured                         |
| STP-003 | PortFast on edge ports    | Medium   | Absent on access ports                         |
| STP-004 | BPDU Guard on edge ports  | Medium   | Absent on access ports                         |
| STP-005 | Root Guard on uplinks     | Medium   | Absent on trunk uplinks                        |
| STP-006 | STP disabled VLAN 4094    | Medium   | STP active on MLAG peer-link VLAN              |

### OSPF Underlay Rules — spine, leaf, campus-router

| Rule ID  | Check                     | Severity | Condition                                      |
|----------|---------------------------|----------|------------------------------------------------|
| OSPF-001 | Explicit router-id        | High     | No `router-id` configured                      |
| OSPF-002 | BFD for OSPF              | Medium   | BFD absent on OSPF interfaces                  |
| OSPF-003 | Passive-interface default | Medium   | Not configured                                 |
| OSPF-004 | Point-to-point type       | Medium   | P2P links without `ip ospf network point-to-point` |
| OSPF-005 | Authentication            | Low      | No MD5/SHA authentication on OSPF interfaces   |

### QoS / Traffic Policy Rules — campus-router, wan-router, ALL

| Rule ID | Check                         | Severity | Condition                                   | Roles                        |
|---------|-------------------------------|----------|---------------------------------------------|------------------------------|
| QOS-001 | Policy on uplinks             | Medium   | No `service-policy` on uplinks              | campus-router, wan-router    |
| QOS-002 | DSCP trust on server ports    | Medium   | `qos trust dscp` absent on server-facing    | leaf, access                 |
| QOS-003 | Unapplied traffic-policy      | Low      | Stanzas defined but not applied to interface | ALL                         |
| QOS-004 | Priority queue voice/video    | Low      | No strict-priority queue configured         | campus-router                |

### VRF and Routing Policy Rules — leaf, border-leaf, wan-router

| Rule ID | Check                       | Severity | Condition                                       |
|---------|-----------------------------|----------|-------------------------------------------------|
| VRF-001 | Route-target per VRF        | High     | VRF missing import/export RT                    |
| VRF-002 | Prefix-list on redistribution | High   | Redistribution without prefix-list filter       |
| VRF-003 | Route-map on BGP neighbor   | Medium   | BGP neighbor missing `route-map in/out`         |
| VRF-004 | Unambiguous default-route   | Medium   | Multiple default-route sources in a single VRF  |
| VRF-005 | Scoped route leaking        | Low      | Leaking without explicit prefix-list            |

### LLDP Rules — ALL

| Rule ID  | Check                       | Severity | Condition                                      |
|----------|-----------------------------|----------|------------------------------------------------|
| LLDP-001 | LLDP enabled globally       | Medium   | `no lldp run` present                          |
| LLDP-002 | LLDP disabled on mgmt       | Low      | LLDP transmit enabled on management interface  |
| LLDP-003 | Neighbor count (show)       | Info     | Fewer neighbors than expected from topology    |

### Multicast / PIM Rules — campus-router, wan-router, border-leaf

| Rule ID  | Check                 | Severity | Condition                                        |
|----------|-----------------------|----------|--------------------------------------------------|
| MCAST-001 | PIM on SVIs          | High     | Multicast routing enabled without `ip pim sparse-mode` on SVIs |
| MCAST-002 | RP address           | High     | No `ip pim rp-address` configured                |
| MCAST-003 | RP redundancy        | Medium   | Static RP with no redundancy (no Anycast-RP)     |
| MCAST-004 | IGMP version         | Low      | IGMPv2 on links expecting IGMPv3                 |

### Hardware / Platform Health Rules — ALL (requires show outputs)

| Rule ID | Check                      | Severity | Condition                                         |
|---------|----------------------------|----------|---------------------------------------------------|
| HW-001  | TCAM profile               | High     | Profile mismatched to enabled features            |
| HW-002  | FIB table headroom         | High     | Route table > 80% capacity                        |
| HW-003  | MAC table utilization      | Medium   | MAC table > 75% capacity                          |
| HW-004  | Hardware errors on uplinks | Medium   | Non-zero error counters on uplink interfaces      |
| HW-005  | Optical DOM alarms         | Low      | Transceiver power outside valid operating range   |

---

## Validation Command Library

```text
# Core
show running-config | section <area>
show version

# EVPN / VXLAN
show bgp evpn summary
show interfaces Vxlan1
show bgp evpn instance

# MLAG
show mlag config-sanity
show mlag detail

# BGP
show ip bgp summary
show bfd peers

# Interfaces
show interfaces status
show interfaces counters errors
show port-channel summary
show storm-control

# Spanning Tree
show spanning-tree
show spanning-tree blockedports
show spanning-tree inconsistentports
show spanning-tree detail

# OSPF
show ip ospf neighbor
show ip ospf interface brief
show ip ospf database summary
show bfd peers

# QoS
show qos interfaces
show traffic-policies
show policy-map interface

# VRF / Routing Policy
show vrf
show ip route vrf all summary
show route-map
show ip prefix-list

# LLDP
show lldp neighbors
show lldp neighbors detail

# Multicast
show ip pim neighbor
show ip pim rp
show ip multicast
show ip igmp groups

# Hardware
show hardware capacity utilization
show interfaces transceiver
show hardware counter drop

# Management
show ntp status
show tacacs
show logging
```

---

## Example 1: Audit Report — Leaf EVPN/MLAG

```markdown
## Audit Report

### Device: leaf01
### Role: leaf
### Platform: DCS-7050CX3-32S
### EOS Version: 4.28.3M
### Date: 2026-03-18

---

## Summary

- Critical: 1
- High: 3
- Medium: 3
- Low: 1

---

## Findings

### Critical

#### [C1] Missing EVPN Address-Family

- **Location**: router bgp 65001
- **Problem**: Not configured — `address-family evpn` missing
- **Risk**: EVPN routes not advertised, fabric isolation
- **Change Risk Score**: 5/5
- **Remediation**:

\`\`\`eos
router bgp 65001
   address-family evpn
      neighbor SPINE_PEERS activate
\`\`\`

### High

#### [H1] MLAG Reload-Delay Misconfigured

- **Location**: mlag configuration
- **Problem**: Misconfigured — reload-delay mlag (330) >= reload-delay non-mlag (300)
- **Risk**: Traffic blackhole during reload
- **Change Risk Score**: 3/5
- **Remediation**:

\`\`\`eos
mlag configuration
   reload-delay mlag 300
   reload-delay non-mlag 330
\`\`\`

#### [H2] Missing Route-Target Export

- **Location**: router bgp 65001 / vrf TENANT-A
- **Problem**: Not configured — no route-target export for VRF TENANT-A
- **Risk**: VRF routes not advertised to remote VTEPs
- **Change Risk Score**: 4/5
- **Remediation**:

\`\`\`eos
router bgp 65001
   vrf TENANT-A
      route-target export evpn 10001:10001
\`\`\`

#### [H3] EVPN-007: VARP MAC Gateway Not Configured

- **Location**: ip virtual-router
- **Problem**: Not configured — `ip virtual-router mac-address` absent; IRB gateway MAC will be per-device
- **Risk**: Inconsistent gateway MAC causes ARP instability for hosts moving between VTEPs
- **Change Risk Score**: 4/5
- **Remediation**:

\`\`\`eos
ip virtual-router mac-address 00:1c:73:00:00:01
\`\`\`

### Medium

#### [M1] EVPN-006: BUM Traffic Handling Not Configured

- **Location**: router bgp 65001 / address-family evpn
- **Problem**: Not configured — neither `underlay-multicast` nor `flood-vtep` configured
- **Risk**: BUM traffic handling undefined; may default to head-end replication with suboptimal performance
- **Change Risk Score**: 2/5
- **Remediation**:

\`\`\`eos
router bgp 65001
   address-family evpn
      no flood-vtep
\`\`\`

#### [M2] MLAG-008: STP Active on VLAN 4094

- **Location**: spanning-tree
- **Problem**: Misconfigured — STP not disabled on VLAN 4094 (MLAG peer-link VLAN)
- **Risk**: STP reconvergence on peer-link VLAN may cause MLAG instability
- **Change Risk Score**: 3/5
- **Remediation**:

\`\`\`eos
no spanning-tree vlan-id 4094
\`\`\`

#### [M3] BGP-003: Maximum-Routes Not Configured

- **Location**: router bgp 65001 / neighbor SPINE_PEERS
- **Problem**: Not configured — no maximum-routes limit
- **Risk**: Route table exhaustion could destabilize the device
- **Change Risk Score**: 2/5
- **Remediation**:

\`\`\`eos
router bgp 65001
   neighbor SPINE_PEERS maximum-routes 12000
\`\`\`

### Low

#### [L1] BGP-006: BFD Not Enabled for BGP Neighbors

- **Location**: router bgp 65001
- **Problem**: Not configured — BFD absent on BGP peer-group
- **Risk**: Slower BGP failure detection; convergence relies on BGP hold-timer only
- **Change Risk Score**: 1/5
- **Remediation**:

\`\`\`eos
router bgp 65001
   neighbor SPINE_PEERS bfd
\`\`\`

---

## Validation Commands

\`\`\`text
show bgp evpn summary
show mlag config-sanity
show mlag detail
show vrf
show interfaces Vxlan1
\`\`\`
```

---

## Example 2: Audit Report — Access Switch Campus

```markdown
## Audit Report

### Device: acc-sw-01
### Role: access
### Platform: DCS-7020SR-32C2
### EOS Version: 4.27.5M
### Date: 2026-03-18

---

## Summary

- Critical: 1
- High: 1
- Medium: 2
- Low: 0

> Note: EVPN/VXLAN, MLAG, OSPF, VRF, and Multicast categories skipped — not applicable to role: access.

---

## Findings

### Critical

#### [C1] STP-001: Spanning Tree Mode Not MSTP

- **Location**: spanning-tree
- **Problem**: Misconfigured — `spanning-tree mode pvst` configured; MSTP or rapid-pvst required
- **Risk**: Per-VLAN STP does not scale; convergence performance degrades with many VLANs
- **Change Risk Score**: 4/5
- **Remediation**:

\`\`\`eos
spanning-tree mode mstp
\`\`\`

### High

#### [H1] SEC-002: No AAA Configuration

- **Location**: aaa
- **Problem**: Not configured — no TACACS+ or RADIUS server defined
- **Risk**: Local authentication only; no central access control or audit trail
- **Change Risk Score**: 2/5
- **Remediation**:

\`\`\`eos
tacacs-server host 10.0.0.100 key 7 <encrypted>
aaa authentication login default group tacacs+ local
aaa authorization commands all default group tacacs+ local
\`\`\`

### Medium

#### [M1] INTF-003: Storm-Control Absent on Access Ports

- **Location**: interface Ethernet1–24
- **Problem**: Not configured — no storm-control on edge-facing ports
- **Risk**: Broadcast/multicast storms can saturate uplinks
- **Change Risk Score**: 2/5
- **Remediation**:

\`\`\`eos
interface Ethernet1-24
   storm-control broadcast level 10
   storm-control multicast level 10
\`\`\`

#### [M2] LLDP-001: LLDP Disabled Globally

- **Location**: global
- **Problem**: Misconfigured — `no lldp run` present
- **Risk**: No topology visibility; troubleshooting and NMS discovery impaired
- **Change Risk Score**: 1/5
- **Remediation**:

\`\`\`eos
lldp run
\`\`\`

---

## Validation Commands

\`\`\`text
show spanning-tree
show spanning-tree inconsistentports
show lldp neighbors
show interfaces counters errors
\`\`\`
```

---

## Workflow: Design vs Implementation

**Input**: Design document + Running-configs

**Steps**:

1. Extract design requirements
2. Map requirements to config elements
3. Check implementation against design
4. Identify gaps
5. Generate gap report

---

## Workflow: Multi-Device Audit with Cross-Device Consistency

**Input**: Multiple running-configs

**Steps**:

1. Determine role for each device (Step 0)
2. Apply role-specific compliance rules per device
3. Run cross-device consistency checks (see below)
4. Generate consolidated report
5. Prioritize findings by blast radius

### Cross-Device Consistency Checks

**MLAG Pairs**:
- Same `domain-id` on both peers
- Same VLANs allowed on peer-link Port-Channel
- Same MLAG IDs for shared port-channels
- `reload-delay` values symmetric

**BGP Peers**:
- Peer-group parameters match on both sides (timers, maximum-routes)
- `send-community` configured consistently
- Route-maps present and mirrored in/out

**Spanning Tree (same segment)**:
- Root bridge assignment consistent across the segment
- No competing root bridge priorities

**VXLAN / VNI (all leaves)**:
- VNI-to-VLAN mappings identical across all leaf switches
- L3VNI for each tenant VRF present on all leaves
- VARP MAC address identical on all leaves

---

# Resources

- [Arista EOS User Guide](https://www.arista.com/en/um-eos)
- [AVD Documentation](https://avd.arista.com/)
- [CloudVision Documentation](https://www.arista.com/en/cg-cv)
