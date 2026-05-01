# EOS Fabric Design Copilot

## Description

**Senior Network Architect** skill specialized in Arista EOS data center fabrics.

## Covered Domains

- EVPN / VXLAN fabrics
- Leaf-spine architectures
- BGP underlay / EVPN overlay
- MLAG configuration
- Border leaf architectures
- VRF segmentation
- Multi-tenant fabrics

## Use Cases

- **Design**: Build scalable and supportable fabrics
- **Review**: Identify risks and inconsistencies in designs
- **Configuration**: Generate production-ready EOS configs
- **Migration**: Plan migrations with rollback
- **Troubleshooting**: Diagnose architectural issues

## Installation

### Claude Code

```bash
# Copy the file to the project's .claude/ folder
cp claude.md /path/to/your/project/.claude/eos-fabric-design.md

# Or use the CLI
claude project add-instructions skills/eos-fabric-design/claude.md
```

### GitHub Copilot

```bash
# Copy to .github/copilot-instructions.md
cp copilot.md /path/to/your/repo/.github/copilot-instructions.md
```

## Files

| File        | Platform       | Description                              |
| ----------- | -------------- | ---------------------------------------- |
| `core.md`   | Shared         | Essential instructions (source of truth) |
| `claude.md` | Claude Code    | Full format with examples and templates  |
| `copilot.md`| GitHub Copilot | Format adapted for Copilot instructions  |

## Response Structure

The skill enforces a standardized response structure:

1. Understanding of the Request
2. Known Inputs
3. Assumptions
4. Design Assessment or Recommendation
5. EOS Configuration Candidate
6. Validation Commands
7. Risks and Caveats
8. Rollback Considerations
9. Open Questions

## Resources

- [Arista EOS User Guide](https://www.arista.com/en/um-eos)
- [Arista Validated Designs (AVD)](https://avd.arista.com/)
- [CloudVision Documentation](https://www.arista.com/en/cg-cv)
