# OpenClaw on Amazon EKS

Deploy the [OpenClaw](https://www.npmjs.com/package/openclaw) Operator and AI agent instances on Amazon EKS with Graviton ARM64. Supports **AWS Global** and **AWS China** regions.

## Quick Start

### Workshop Studio (recommended)

Use the CloudFormation template for one-click deployment:

```bash
# Upload eks/cloudformation/workshop-studio-template.yaml to CloudFormation
# or use it with Workshop Studio events
```

The template triggers CodeBuild → Terraform, deploying the full stack automatically.

### Self-managed

```bash
cd terraform
terraform init
terraform apply \
  -var="name=openclaw-workshop" \
  -var="region=us-west-2" \
  -var="enable_efs=true"

# Configure kubectl
$(terraform output -raw configure_kubectl)

# Deploy an OpenClaw instance
kubectl apply -f ../manifests/examples/openclaw-bedrock-instance.yaml
```

## Directory Structure

```
eks/
├── cloudformation/
│   └── workshop-studio-template.yaml   # One-click CFN → CodeBuild → Terraform
├── terraform/                          # Terraform modules
│   ├── main.tf                         # Providers, locals, ECR host
│   ├── root.tf                         # Module composition
│   ├── variables.tf                    # Input variables
│   ├── outputs.tf                      # Cluster endpoint, kubectl, etc.
│   ├── versions.tf                     # Provider version constraints
│   └── modules/
│       ├── vpc/                # VPC, subnets, NAT gateway
│       ├── eks-cluster/        # EKS 1.35, managed node groups, 5 managed add-ons
│       ├── storage/            # EFS file system, EBS/EFS StorageClasses
│       ├── bedrock-iam/        # Bedrock IRSA role for OpenClaw instances
│       ├── operator/           # OpenClaw Operator Helm release
│       ├── networking/         # AWS Load Balancer Controller + CloudFront (optional)
│       ├── monitoring/         # Prometheus + Grafana (optional)
│       ├── litellm/            # LiteLLM AI proxy + PostgreSQL + Pod Identity (optional)
│       ├── kata/               # Kata Containers + Karpenter (optional)
│       └── agent-sandbox/      # Agent Sandbox CRDs (optional)
├── manifests/
│   └── examples/               # OpenClawInstance CRD examples
│       ├── openclaw-bedrock-instance.yaml    # Standard Bedrock instance
│       ├── openclaw-kata-instance.yaml       # Firecracker VM isolation
│       ├── openclaw-slack-instance.yaml      # Slack bot integration
│       └── openclaw-wecom-instance.yaml      # WeCom (企业微信) integration
└── scripts/
    ├── china-image-mirror.sh   # Mirror images + Helm charts to ECR (China/air-gapped)
    ├── cleanup.sh              # Tear down all resources
    └── validate.sh             # Post-deploy validation checks
```

## EKS Managed Add-ons

The EKS cluster module deploys 5 managed add-ons with automatic version updates:

| Add-on | Pod Identity | Description |
|--------|-------------|-------------|
| `coredns` | — | DNS resolution |
| `vpc-cni` | ✅ `AmazonEKS_CNI_Policy` | Pod networking (ENI management) |
| `eks-pod-identity-agent` | — | Pod Identity token vending |
| `aws-ebs-csi-driver` | ✅ `AmazonEBSCSIDriverPolicy` | EBS volume provisioning |
| `aws-efs-csi-driver` | ✅ `AmazonEFSCSIDriverPolicy` | EFS mount targets |

## Terraform Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `name` | `openclaw-eks` | Cluster and resource name prefix |
| `region` | `us-west-2` | AWS region (`cn-*` auto-detected as China) |
| `architecture` | `arm64` | `arm64` (Graviton) or `x86` |
| `eks_cluster_version` | `1.35` | EKS Kubernetes version |
| `enable_efs` | `true` | EFS persistent storage |
| `enable_alb_controller` | `false` | AWS Load Balancer Controller + CloudFront |
| `enable_kata` | `false` | Kata Containers (Firecracker VM isolation) |
| `enable_karpenter` | `false` | Karpenter auto-scaling for Kata bare metal nodes |
| `enable_monitoring` | `false` | Prometheus + Grafana |
| `enable_litellm` | `false` | LiteLLM proxy (Claude Sonnet 4.5 default model) |
| `enable_agent_sandbox` | `false` | Agent Sandbox CRDs (namespace only) |

Workshop Studio events enable all optional modules via CFN parameters.

## CloudFormation Template

`eks/cloudformation/workshop-studio-template.yaml` deploys:

1. **Code Editor IDE** — EC2 + CloudFront with kubectl/helm/terraform pre-installed
2. **CodeBuild Project** — Clones this repo, runs `terraform apply` with retry logic
3. **Terraform State** — S3 bucket for shared state
4. **IAM Identity Center** — SSO for EKS access
5. **Wait Condition** — CFN waits for CodeBuild to complete before reporting success

The buildspec includes a 3-attempt retry loop with 30s delays to handle transient failures (e.g., EKS API DNS propagation).

## China Region

China regions cannot reach ghcr.io, quay.io, Docker Hub, or registry.k8s.io. Run the mirror script **before** `terraform apply`:

```bash
bash scripts/china-image-mirror.sh \
  --region cn-northwest-1 \
  --name openclaw-cn \
  --profile china
```

This mirrors all container images and Helm chart OCI artifacts to your private China ECR. Terraform auto-detects China and uses the ECR mirrors.

## Image Version Pinning

Pin `spec.image.tag` to a known stable release:

```yaml
spec:
  image:
    tag: "2026.4.2"   # Known stable
```

## Guides

- **[Deployment Guide (EN)](../docs/DEPLOYMENT_EKS.md)** — Full walkthrough with examples
- **[部署指南 (中文)](../docs/DEPLOYMENT_EKS_CN.md)** — 包含中国区网络依赖矩阵和离线部署指南
