---
name: eve-lab-topology-design
description: Design and validate EVE-NG topologies before build — requirements, trade-offs, link plan, and UNL validation.
---

# EVE Lab Topology Design

Use this skill for planning and review work before touching the lab.

## When to Use

- The user wants a topology proposal
- Requirements are incomplete and need structure
- You need a build plan before creating nodes or links
- You need to validate a `.unl` file against design intent

## Design Workflow

1. Classify the lab: campus, branch/WAN, ISP, data center, or hybrid.
2. Gather the minimum requirements.
3. State assumptions explicitly.
4. Present 2-3 viable design options when trade-offs matter.
5. Recommend one design.
6. Produce a physical link plan and logical/protocol plan.
7. Validate the design before build.
8. If a `.unl` exists, run the validator.

## Minimum Discovery Set

Ask for these if the request is underspecified:
- topology type
- number of sites or devices
- desired hierarchy or fabric style
- routing or control-plane protocols
- redundancy target
- image/platform choices
- host resource limits
- design-only vs build/config help

If the user does not answer, offer a clearly labeled default that is resilient and realistic for lab scale.

## Required Output

For every design, provide:

### 1) Requirement summary
A short bullet list of scope, assumptions, and constraints.

### 2) Connectivity matrix
```text
NODE      ROLE          LINKS  NEIGHBORS
CORE1     core          2      DIST1, DIST2
DIST1     distribution  3      CORE1, CORE2, ACC1
ACC1      access        2      DIST1, DIST2
HOST1     host          1      ACC1
```

### 3) Required links
```text
CORE1 <-> DIST1
CORE2 <-> DIST1
DIST1 <-> ACC1
ACC1  <-> HOST1
```

### 4) Redundancy statement
Spell out what single-node or single-link failures the design should tolerate.

### 5) Validator input JSON
```json
{
  "required_links": [
    {"from": "CORE1", "to": "DIST1"},
    {"from": "CORE2", "to": "DIST1"}
  ],
  "redundancy_groups": [
    {"nodes": ["CORE1", "CORE2"], "role": "core", "min_uplinks": 1}
  ],
  "forbidden_links": [
    {"from": "HOST1", "to": "CORE1"}
  ]
}
```

## UNL Validator

Validator path:

```bash
python3 workspace/skills/eve-lab-topology-design/scripts/validate_unl_topology.py --help
```

Typical usage:

```bash
python3 workspace/skills/eve-lab-topology-design/scripts/validate_unl_topology.py /path/to/lab.unl --verbose
python3 workspace/skills/eve-lab-topology-design/scripts/validate_unl_topology.py /path/to/lab.unl --reqs design_reqs.json --roles roles.json
python3 workspace/skills/eve-lab-topology-design/scripts/validate_unl_topology.py /path/to/lab.unl --json
```

The validator checks:
- orphan nodes
- dangling network references
- isolated networks
- disconnected graph components
- forbidden adjacencies
- articulation-point node SPOFs
- bridge-link SPOFs
- asymmetric peer redundancy
- required and forbidden links from the JSON spec

## Design Defaults

Prefer simple, supportable defaults:
- **Campus**: dual distribution or collapsed core
- **WAN**: dual hub/edge when scale allows
- **ISP/MPLS**: small redundant P/PE layout
- **Data center**: compact leaf-spine before larger meshes

## Integration with Other Skills

- **eve-ng-lab-management**: create or export the target lab
- **eve-ng-node-operations**: map design to nodes and images
- **eve-lab-topology-build**: implement the network objects and links
- **eve-ng-config-ops**: preload configs once the design is settled
- **eve-ng-console-ops**: verify the resulting topology live

## Notes

- Separate physical topology from protocol topology.
- Avoid over-designing for lab scale.
- Prefer small outputs with explicit assumptions to long generic design essays.
