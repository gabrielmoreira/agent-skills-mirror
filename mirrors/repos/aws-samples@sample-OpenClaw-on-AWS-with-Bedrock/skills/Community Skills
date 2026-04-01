# Community Skills

This repository can document useful third-party OpenClaw skills, but these are community-maintained integrations and are not part of the core AWS sample support surface.

## Backup and Restore (S3 + optional KMS)

- Skill repository: [genedragon/openclaw-aws-backup-skill](https://github.com/genedragon/openclaw-aws-backup-skill)
- Purpose: encrypted backup/restore for OpenClaw workspaces and state using S3, with optional KMS.
- Ownership: community-maintained (not maintained by `aws-samples`).

### Quick start

```bash
cd /home/ubuntu/.openclaw/workspace
git clone https://github.com/genedragon/openclaw-aws-backup-skill.git
cd openclaw-aws-backup-skill
npm install
sudo npm link

# first-time setup
openclaw-aws-backup setup
```

### Common commands

```bash
openclaw-aws-backup create
openclaw-aws-backup list
openclaw-aws-backup restore
openclaw-aws-backup test
```

### Security and operations notes

- Use least-privilege IAM permissions for S3 and KMS.
- Prefer KMS encryption for production backups.
- Configure and review retention policies regularly.
- Test restore paths before relying on backups in production.
