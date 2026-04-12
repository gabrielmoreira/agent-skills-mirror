# OpenClaw on Amazon EKS

Deploy the [OpenClaw](https://www.npmjs.com/package/openclaw) Operator and AI agent instances on Amazon EKS. Supports **AWS Global** and **AWS China** regions.

## Quick Start

```bash
# 1. (China only) Mirror images to ECR — required before terraform apply
# bash scripts/china-image-mirror.sh --region cn-northwest-1 --name openclaw-cn --profile china

# 2. Deploy infrastructure
cd terraform
terraform init
terraform apply -var="name=openclaw-prod" -var="enable_efs=true"

# 3. Configure kubectl
$(terraform output -raw configure_kubectl)

# 4. Deploy an OpenClaw instance
kubectl apply -f ../manifests/examples/openclaw-bedrock-instance.yaml
```

## Directory Structure

```
eks/
├── terraform/                  # Terraform modules (the main deployment tool)
│   ├── main.tf                 # Providers, locals, ECR host construction
│   ├── root.tf                 # Module composition
│   ├── variables.tf            # Input variables
│   ├── outputs.tf              # Cluster endpoint, kubectl command, etc.
│   ├── versions.tf             # Provider version constraints
│   └── modules/
│       ├── vpc/                # VPC, subnets, NAT gateway
│       ├── eks-cluster/        # EKS cluster, managed node groups, CSI addons
│       ├── storage/            # EFS file system, EBS/EFS StorageClasses
│       ├── bedrock-iam/        # Bedrock IRSA role for OpenClaw instances
│       ├── operator/           # OpenClaw Operator Helm release
│       ├── networking/         # AWS Load Balancer Controller (optional)
│       ├── monitoring/         # Prometheus + Grafana (optional)
│       ├── litellm/            # LiteLLM AI proxy (optional, required for China)
│       ├── kata/               # Kata Containers + Karpenter (optional)
│       └── agent-sandbox/      # Agent sandbox CRDs (optional)
├── manifests/
│   └── examples/               # OpenClawInstance CRD examples
│       ├── openclaw-bedrock-instance.yaml    # Standard Bedrock instance
│       ├── openclaw-kata-instance.yaml       # Firecracker VM isolation
│       └── openclaw-slack-instance.yaml      # Slack bot integration
└── scripts/
    ├── china-image-mirror.sh   # Mirror images + Helm charts to ECR (China/air-gapped)
    ├── install.sh              # Interactive deployment wizard
    ├── cleanup.sh              # Tear down all resources
    ├── validate.sh             # Post-deploy validation checks
    └── integration-test.sh     # End-to-end deployment test
```

## Terraform Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `name` | `openclaw-eks` | Cluster and resource name prefix |
| `region` | `us-west-2` | AWS region (`cn-*` auto-detected as China) |
| `architecture` | `arm64` | `arm64` (Graviton) or `x86` |
| `enable_efs` | `true` | EFS persistent storage (default StorageClass) |
| `enable_alb_controller` | `false` | AWS Load Balancer Controller |
| `enable_kata` | `false` | Kata Containers (Firecracker VM isolation) |
| `enable_monitoring` | `false` | Prometheus + Grafana |
| `enable_litellm` | `false` | LiteLLM proxy (required for China) |

## China Region

China regions cannot reach ghcr.io, quay.io, Docker Hub, or registry.k8s.io. Run the mirror script **before** `terraform apply`:

```bash
bash scripts/china-image-mirror.sh \
  --region cn-northwest-1 \
  --name openclaw-cn \
  --profile china
```

This mirrors all container images and Helm chart OCI artifacts to your private China ECR. Terraform auto-detects China and uses the ECR mirrors.

When deploying OpenClaw instances in China, set `spec.registry` to your ECR host:

```yaml
spec:
  registry: "ACCOUNT.dkr.ecr.cn-northwest-1.amazonaws.com.cn"
```

## Image Version Pinning

Pin `spec.image.tag` to a known stable release. The `latest` tag may have regressions.

```yaml
spec:
  image:
    tag: "2026.4.2"   # Known stable
```

The mirror script defaults to `OPENCLAW_VERSION=2026.4.2` (override via environment variable).

## Guides

- **[Deployment Guide (EN)](../docs/DEPLOYMENT_EKS.md)** — Full walkthrough with examples
- **[部署指南 (中文)](../docs/DEPLOYMENT_EKS_CN.md)** — 包含中国区网络依赖矩阵和离线部署指南
