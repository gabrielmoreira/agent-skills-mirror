# Security Best Practices

## Quick Reference: Secure Access Commands

### Connect to EC2 Instance (Secure Method)

```bash
# Get instance ID
INSTANCE_ID=$(aws cloudformation describe-stacks \
  --stack-name openclaw-bedrock \
  --query 'Stacks[0].Outputs[?OutputKey==`InstanceId`].OutputValue' \
  --output text \
  --region us-west-2)

# Connect via SSM (no SSH keys needed)
aws ssm start-session --target $INSTANCE_ID --region us-west-2

# Switch to ubuntu user
sudo su - ubuntu
```

### Port Forwarding (Secure Access to Web UI)

```bash
# Start port forwarding (keep terminal open)
aws ssm start-session \
  --target $INSTANCE_ID \
  --region us-west-2 \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["18789"],"localPortNumber":["18789"]}'

# Access Web UI at: http://localhost:18789/?token=<your-token>
```

---

## Overview

This deployment follows AWS security best practices and provides multiple layers of protection.

## Security Features

### 1. IAM Role-Based Authentication

**No API Keys**: The EC2 instance uses an IAM role to authenticate with Bedrock.

```json
{
  "Effect": "Allow",
  "Action": [
    "bedrock:InvokeModel",
    "bedrock:InvokeModelWithResponseStream",
    "bedrock:ListFoundationModels"
  ],
  "Resource": "*"
}
```

**Benefits**:
- ✅ Automatic credential rotation
- ✅ No secrets in code or config files
- ✅ Centralized access control
- ✅ CloudTrail audit logs

### 2. SSM Session Manager

**No SSH Keys Needed**: Access instances through AWS Systems Manager.

**Benefits**:
- ✅ No public SSH port (22) required
- ✅ Automatic session logging
- ✅ CloudTrail audit trail
- ✅ Session timeout controls
- ✅ No key management

**Enable SSM-only access**:
```yaml
AllowedSSHCIDR: 127.0.0.1/32  # Disables SSH
```

### 3. VPC Endpoints

**Private Network**: Bedrock API calls stay within AWS network.

**Benefits**:
- ✅ Traffic doesn't traverse internet
- ✅ Lower latency
- ✅ Compliance-friendly (HIPAA, SOC2)
- ✅ Reduced attack surface

**Cost**: ~$22/month for 3 endpoints

### 4. Docker Sandbox

**Isolated Execution**: Non-main sessions run in Docker containers.

```json
{
  "sandbox": {
    "mode": "non-main",
    "allowlist": ["bash", "read", "write", "edit"],
    "denylist": ["browser", "canvas", "nodes", "gateway"]
  }
}
```

**Benefits**:
- ✅ Limits blast radius
- ✅ Protects host system
- ✅ Safe for group chats

## Security Checklist

### Deployment

- [ ] Enable VPC endpoints for production
- [ ] Set `AllowedSSHCIDR` to your IP or disable SSH
- [ ] Enable Docker sandbox
- [ ] Use latest AMI
- [ ] Enable CloudTrail in your account

### Post-Deployment

- [ ] Rotate gateway token regularly
- [ ] Review CloudTrail logs weekly
- [ ] Monitor Bedrock usage
- [ ] Set up cost alerts
- [ ] Enable CloudWatch alarms

### Ongoing

- [ ] Update Clawdbot monthly
- [ ] Review IAM policies quarterly
- [ ] Audit session logs
- [ ] Test disaster recovery
- [ ] Review security group rules

## Audit & Compliance

### CloudTrail Logs

All Bedrock API calls are logged:

```bash
# View recent Bedrock calls
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=InvokeModel \
  --max-items 50 \
  --region us-west-2
```

### SSM Session Logs

All SSM sessions are logged:

```bash
# View session logs
aws logs tail /aws/ssm/session-logs --follow --region us-west-2
```

### Cost Tracking

```bash
# View Bedrock costs
aws ce get-cost-and-usage \
  --time-period Start=2026-01-01,End=2026-01-31 \
  --granularity DAILY \
  --metrics BlendedCost \
  --filter '{"Dimensions":{"Key":"SERVICE","Values":["Amazon Bedrock"]}}'
```

## Compliance Certifications

Amazon Bedrock supports:
- SOC 1, 2, 3
- ISO 27001, 27017, 27018, 27701
- PCI DSS
- HIPAA eligible
- FedRAMP Moderate (in supported regions)

## Incident Response

### Compromised Instance

```bash
# 1. Isolate instance
aws ec2 modify-instance-attribute \
  --instance-id $INSTANCE_ID \
  --groups sg-isolated

# 2. Create forensic snapshot
aws ec2 create-snapshot \
  --volume-id $VOLUME_ID \
  --description "Forensic snapshot"

# 3. Terminate instance
aws ec2 terminate-instances --instance-ids $INSTANCE_ID

# 4. Review CloudTrail logs
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=$INSTANCE_ID
```

### Leaked Gateway Token

```bash
# 1. Connect to instance
aws ssm start-session --target $INSTANCE_ID

# 2. Regenerate token
sudo su - ubuntu
NEW_TOKEN=$(openssl rand -hex 24)

# 3. Update config
python3 << EOF
import json
with open('/home/ubuntu/.clawdbot/clawdbot.json') as f:
    config = json.load(f)
config['gateway']['auth']['token'] = '$NEW_TOKEN'
with open('/home/ubuntu/.clawdbot/clawdbot.json', 'w') as f:
    json.dump(config, f, indent=2)
EOF

# 4. Restart service
systemctl --user restart clawdbot-gateway
```

## Security Recommendations

### For Development

- Use `t4g.small` instance (Graviton, cost-effective)
- Use Nova 2 Lite model (cheapest)
- Disable VPC endpoints (save $22/month)
- Allow SSH from your IP only
- Enable sandbox mode

### For Production

- Use `t4g.medium` or larger (Graviton recommended)
- Use Nova Pro or Claude models (better performance)
- **Enable VPC endpoints** (required for security)
- **Disable SSH** (`AllowedSSHCIDR: 127.0.0.1/32`)
- Enable sandbox mode
- Set up CloudWatch alarms
- Enable AWS Config rules
- Regular security audits

### For Compliance (HIPAA, PCI-DSS)

- **Must use Graviton or x86 instances in compliant regions**
- **Must enable VPC endpoints**
- **Must disable SSH**
- Enable CloudTrail
- Enable VPC Flow Logs
- Encrypt EBS volumes (enabled by default)
- Use AWS Secrets Manager for tokens
- Regular penetration testing
- Document security controls

## References

- [AWS Security Best Practices](https://aws.amazon.com/architecture/security-identity-compliance/)
- [Bedrock Security](https://docs.aws.amazon.com/bedrock/latest/userguide/security.html)
- [SSM Security](https://docs.aws.amazon.com/systems-manager/latest/userguide/security.html)
