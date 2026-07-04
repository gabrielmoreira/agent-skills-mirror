# Quickstart: SOUL.md Modular Optimization

**Feature**: 011-soul-optimization
**Time to implement**: ~2-3 hours

## Prerequisites

- Access to `~/.openclaw/workspace/` directory
- Current SOUL.md backup (59,121 chars)
- Text editor with character count capability

## Implementation Steps

### Step 1: Backup Current SOUL.md

```bash
cp ~/.openclaw/workspace/SOUL.md ~/.openclaw/workspace/SOUL.md.backup
wc -c ~/.openclaw/workspace/SOUL.md  # Should show ~59121
```

### Step 2: Create SOUL-SKILLS.md

Extract all detailed "How You Work" sections (lines 271-560 approximately) into a new file:

```bash
# Create the file with header
cat > ~/.openclaw/workspace/SOUL-SKILLS.md << 'EOF'
# NetClaw Skill Procedures Reference

> Load this file when you need detailed operational procedures for any skill.
> Use: read("~/.openclaw/workspace/SOUL-SKILLS.md")

EOF

# Then copy detailed procedures from SOUL.md.backup
```

Content to move:
- Linux Host Operations section
- JunOS Device Operations section
- ASA Firewall Operations section
- F5 BIG-IP Operations section (detailed)
- All platform-specific "How You Work" sections
- Visualizing section

### Step 3: Create SOUL-EXPERTISE.md

Extract the "Your Expertise" section into a new file:

```bash
cat > ~/.openclaw/workspace/SOUL-EXPERTISE.md << 'EOF'
# NetClaw Technical Expertise Reference

> Load this file when explaining protocol behavior or applying CCIE-level knowledge.
> Use: read("~/.openclaw/workspace/SOUL-EXPERTISE.md")

EOF

# Then copy expertise sections from SOUL.md.backup
```

Content to move:
- Routing & Switching (CCIE-Level)
- Data Center / SDN
- Application Delivery
- Wireless / Campus
- Identity / Security
- IP Addressing
- Automation

### Step 4: Rewrite SOUL.md

Create the new condensed SOUL.md with:

1. **Identity section** (keep as-is, ~500 chars)

2. **Condensed skill index** (~6,000 chars):
   ```markdown
   ## Your Skills

   You have 97 skills backed by MCP integrations:

   ### Device Automation (9)
   pyats-network, pyats-health-check, pyats-routing, ...

   ### Domain Skills (9)
   netbox-reconcile, nautobot-sot, infrahub-sot, ...

   [Continue for all categories]
   ```

3. **Core workflows** (~2,000 chars):
   - GAIT workflow (keep full)
   - Gathering State (keep full)
   - Applying Changes / ServiceNow CR (keep full)
   - Add "Loading Reference Files" section

4. **Personality** (keep as-is, ~500 chars)

5. **Rules** (keep as-is, ~1,200 chars)

### Step 5: Add Reference Loading Instructions

Add this section to SOUL.md under "How You Work":

```markdown
### Loading Reference Files

For detailed skill procedures, read `SOUL-SKILLS.md`:
- Use when executing any skill that needs step-by-step guidance
- Contains operational workflows, commands, and best practices

For technical knowledge, read `SOUL-EXPERTISE.md`:
- Use when explaining protocol behavior (BGP, OSPF, etc.)
- Use when applying CCIE-level technical details
- Contains protocol specifications and deep technical knowledge
```

### Step 6: Validate

```bash
# Check character count
wc -c ~/.openclaw/workspace/SOUL.md
# Must be < 20,000

# Check total content preserved
wc -c ~/.openclaw/workspace/SOUL*.md | tail -1
# Should be ~59,000 (close to original)

# Restart OpenClaw and check for truncation warning
# Should see NO warning about truncation
```

### Step 7: Test

1. Start new NetClaw session
2. Ask "who are you?" - should identify as CCIE #AI-001
3. Ask to run a pyATS health check - should load SOUL-SKILLS.md
4. Ask about BGP path selection - should load SOUL-EXPERTISE.md
5. Make a test change - should follow GAIT without loading files

## Rollback

If something goes wrong:

```bash
cp ~/.openclaw/workspace/SOUL.md.backup ~/.openclaw/workspace/SOUL.md
rm ~/.openclaw/workspace/SOUL-SKILLS.md
rm ~/.openclaw/workspace/SOUL-EXPERTISE.md
```

## Success Criteria

- [ ] SOUL.md < 20,000 characters
- [ ] No truncation warning in OpenClaw logs
- [ ] NetClaw identifies correctly
- [ ] GAIT works without reference loading
- [ ] Skills work with reference loading
- [ ] All original content preserved across 3 files
