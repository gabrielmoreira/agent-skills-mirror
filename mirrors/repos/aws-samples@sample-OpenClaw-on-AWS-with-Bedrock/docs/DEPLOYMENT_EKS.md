# Deploying OpenClaw on Amazon EKS

Deploy the OpenClaw Operator and AI agent instances on Amazon EKS. Supports both **AWS Global** regions (us-west-2, us-east-1, etc.) and **AWS China** regions (cn-northwest-1, cn-north-1).

---

## Prerequisites

### All Regions

| Requirement | Version | Check |
|-------------|---------|-------|
| AWS CLI     | >= 2.27 | `aws --version` |
| kubectl     | >= 1.28 | `kubectl version --client` |
| Terraform   | >= 1.3  | `terraform --version` |
| Docker      | >= 20.0 | `docker --version` |
| Helm        | >= 3.12 | `helm version` |

### EKS Pod Identity Agent

Uses [EKS Pod Identity](https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html) (not IRSA) for AWS access. Terraform installs it automatically as a managed addon.

### China Region Additional Prerequisites

AWS China regions (`cn-northwest-1`, `cn-north-1`) have network restrictions:

| Requirement | Why | How |
|-------------|-----|-----|
| **Image mirror to China ECR** | `ghcr.io`, Docker Hub, `quay.io` inaccessible | Run `china-image-mirror.sh` **before** `terraform apply` |
| **Third-party model provider** | Amazon Bedrock is **not available** in China | Use LiteLLM proxy or direct API keys |
| **AWS China account** | Separate partition (`aws-cn`) | Separate IAM credentials |
| **AWS CLI profile** | China account needs its own profile | `aws configure --profile china` |

#### Model provider for China

Amazon Bedrock does not operate in AWS China regions. Two options:

1. **LiteLLM proxy** (recommended): Deploy on the same cluster (`enable_litellm = true`). Provides an OpenAI-compatible endpoint that routes to any model provider.

2. **Direct API keys**: Create a Kubernetes Secret with provider keys and reference it in the OpenClawInstance CRD:

```bash
kubectl -n openclaw create secret generic model-api-keys \
  --from-literal=ANTHROPIC_API_KEY=sk-ant-...

kubectl -n openclaw patch openclawinstance AGENT_NAME --type=merge \
  -p '{"spec":{"envFrom":[{"secretRef":{"name":"model-api-keys"}}]}}'
```

#### Mirror container images to China ECR

Run from a machine with global internet access (e.g., a global-region EC2):

```bash
bash eks/scripts/china-image-mirror.sh \
  --region cn-northwest-1 \
  --name openclaw-cn \
  --profile china
```

This mirrors all container images and Helm chart OCI artifacts to China ECR:

| Image | Purpose |
|-------|---------|
| `ghcr.io/openclaw/openclaw:2026.4.2` | OpenClaw main container + init containers |
| `ghcr.io/astral-sh/uv:0.6-bookworm-slim` | Python deps init container |
| `busybox:1.37` | Config copy init container (overwrite mode) |
| `nginx:1.27-alpine` | Gateway proxy sidecar |
| `otel/opentelemetry-collector:0.120.0` | Observability sidecar |
| `chromedp/headless-shell:stable` | Browser automation sidecar |
| `ghcr.io/tailscale/tailscale:latest` | Tailscale VPN sidecar |
| `ollama/ollama:latest` | Local LLM inference sidecar |
| `tsl0922/ttyd:latest` | Web terminal sidecar |
| `rclone/rclone:1.68` | S3 backup/restore job |
| `ghcr.io/openclaw-rocks/openclaw-operator:v0.26.2` | Operator controller |

---

## Deploy with Terraform

Creates the full stack: VPC, EKS cluster, EFS storage, OpenClaw Operator, and optionally ALB Controller, Kata Containers, monitoring, and LiteLLM.

### Step 1: Mirror images (China only)

> **China regions must run this before `terraform apply`.** All upstream registries (ghcr.io, quay.io, Docker Hub, registry.k8s.io) are blocked. The script mirrors images and Helm charts to ECR. Skipping this will cause `terraform apply` to fail.

```bash
bash eks/scripts/china-image-mirror.sh --region cn-northwest-1 --name openclaw-cn --profile china
```

Global regions pull directly from upstream — no mirroring needed.

### Step 2: Terraform apply

**Global region:**

```bash
cd eks/terraform
terraform init

terraform apply \
  -var="name=openclaw-prod" \
  -var="region=us-west-2" \
  -var="architecture=arm64" \
  -var="enable_efs=true"
```

**China region:**

```bash
cd eks/terraform
terraform workspace new china
terraform init

AWS_PROFILE=china terraform apply \
  -var="name=openclaw-cn" \
  -var="region=cn-northwest-1" \
  -var="architecture=arm64" \
  -var="enable_efs=true"
```

### Step 3: Configure kubectl

```bash
# Global
aws eks --region us-west-2 update-kubeconfig --name openclaw-prod

# China
AWS_PROFILE=china aws eks --region cn-northwest-1 update-kubeconfig --name openclaw-cn
```

### Terraform variables reference

| Variable | Default | Description |
|----------|---------|-------------|
| `name` | `openclaw-eks` | Cluster and resource name prefix |
| `region` | `us-west-2` | AWS region (China auto-detected from `cn-` prefix) |
| `architecture` | `arm64` | `arm64` (Graviton) or `x86` |
| `enable_efs` | `true` | EFS for workspace persistence (set as default StorageClass) |
| `enable_alb_controller` | `false` | AWS Load Balancer Controller for ALB Ingress |
| `enable_kata` | `false` | Kata Containers for Firecracker VM isolation |
| `enable_monitoring` | `false` | Prometheus + Grafana monitoring stack |
| `enable_litellm` | `false` | LiteLLM OpenAI-compatible proxy (required for China) |

---

## Deploying OpenClaw Instances

After Terraform completes, deploy AI agent instances via `kubectl`.

### Basic instance (global region)

```yaml
apiVersion: openclaw.rocks/v1alpha1
kind: OpenClawInstance
metadata:
  name: my-agent
  namespace: openclaw
spec:
  config:
    raw:
      models:
        providers:
          amazon-bedrock:
            baseUrl: "https://bedrock-runtime.us-west-2.amazonaws.com"
            models:
              - id: us.amazon.nova-2-lite-v1:0
                name: Nova 2 Lite
                contextWindow: 300000
                maxTokens: 5120
      agents:
        defaults:
          model:
            primary: amazon-bedrock/us.amazon.nova-2-lite-v1:0
  gateway:
    enabled: true
  resources:
    requests:
      cpu: "500m"
      memory: "1Gi"
    limits:
      cpu: "2"
      memory: "4Gi"
  storage:
    persistence:
      size: 5Gi
```

```bash
kubectl apply -f my-agent.yaml
kubectl get pods -n openclaw -w
```

### China region instance (with ECR registry override)

Add `spec.registry` to rewrite all image registries to China ECR:

```yaml
spec:
  registry: "ACCOUNT.dkr.ecr.cn-northwest-1.amazonaws.com.cn"
  config:
    raw:
      models:
        providers:
          amazon-bedrock:
            baseUrl: "https://bedrock-runtime.us-west-2.amazonaws.com"
            models:
              - id: us.amazon.nova-2-lite-v1:0
                name: Nova 2 Lite
                contextWindow: 300000
                maxTokens: 5120
      agents:
        defaults:
          model:
            primary: amazon-bedrock/us.amazon.nova-2-lite-v1:0
```

### Instance with LiteLLM (China)

If you deployed LiteLLM (`enable_litellm = true`), point agents to the in-cluster endpoint:

```yaml
spec:
  registry: "ACCOUNT.dkr.ecr.cn-northwest-1.amazonaws.com.cn"
  config:
    raw:
      models:
        providers:
          litellm:
            baseUrl: "http://litellm.litellm.svc:4000/v1"
            apiKey: "not-needed"
            models:
              - id: bedrock/claude-sonnet
                name: Claude Sonnet
                contextWindow: 200000
                maxTokens: 8192
      agents:
        defaults:
          model:
            primary: litellm/bedrock/claude-sonnet
```

### Managing instances

```bash
# List instances
kubectl get openclawinstances -n openclaw

# Check pod status
kubectl get pods -n openclaw

# View logs
kubectl logs -n openclaw my-agent-0 -c openclaw --tail=50

# Delete instance
kubectl delete openclawinstance my-agent -n openclaw
```

### CRD examples

See `eks/manifests/examples/` for pre-built examples:
- `openclaw-bedrock-instance.yaml` — Standard Bedrock instance
- `openclaw-kata-instance.yaml` — Instance with Firecracker VM isolation
- `openclaw-slack-instance.yaml` — Instance with Slack bot integration

---

## Architecture

```
┌────────────────────────────────────────────────────────┐
│  EKS Cluster                                            │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  openclaw namespace                                 │ │
│  │                                                     │ │
│  │  ┌──────────────────┐  ┌──────────────────┐        │ │
│  │  │ OpenClawInstance  │  │ OpenClawInstance  │  ...   │ │
│  │  │ StatefulSet + Svc │  │ StatefulSet + Svc │        │ │
│  │  │ + PVC (EFS)       │  │ + PVC (EFS)       │        │ │
│  │  └──────────────────┘  └──────────────────┘        │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  openclaw-operator-system                           │ │
│  │  OpenClaw Operator (reconciles CRDs → K8s resources)│ │
│  └────────────────────────────────────────────────────┘ │
└───────────────────────────┬──────────────────────────────┘
                            │
                 ┌──────────┴──────────┐
                 │    AWS Services     │
                 │  Bedrock   EFS      │
                 │  ECR       IAM      │
                 └─────────────────────┘
```

### Runtime comparison

| Runtime | Isolation | Storage | Image Source |
|---------|-----------|---------|--------------|
| **EKS Pods** | cgroups / namespaces | EFS | ghcr.io (global) / ECR mirror (China) |
| **EKS + Kata** | Firecracker microVM | EFS | Same, with `runtimeClass: kata-qemu` |

---

## Security

### Compute Isolation

| Runtime | Kernel | Prompt injection risk |
|---------|--------|----------------------|
| **EKS Pods** | **Shared host kernel** | Kernel exploit theoretically possible |
| EKS + Kata | Dedicated Firecracker VM | Container escape impossible |

For production with untrusted code execution, enable Kata Containers (`enable_kata = true`).

---

## Troubleshooting

### Pod `ImagePullBackOff` (China)

Images can't be pulled from blocked registries. Set `spec.registry` in the OpenClawInstance:

```yaml
spec:
  registry: "ACCOUNT.dkr.ecr.cn-northwest-1.amazonaws.com.cn"
```

### Pod `Pending` (unbound PVC)

No default StorageClass. Terraform sets EFS as default automatically. For manual clusters:

```bash
kubectl annotate storageclass efs-sc \
  storageclass.kubernetes.io/is-default-class=true
```

### Operator not running

```bash
kubectl get deployment -n openclaw-operator-system
kubectl logs -n openclaw-operator-system deployment/openclaw-operator
```

### Pod Identity 403

```bash
# Verify addon
kubectl get pods -n kube-system -l app.kubernetes.io/name=eks-pod-identity-agent

# Verify association
aws eks list-pod-identity-associations \
  --cluster-name CLUSTER --namespace openclaw --region REGION
```

---

## China Region Offline Deployment Guide

For environments where even the machine running `terraform apply` cannot reach overseas registries, use S3 to relay images from your local PC.

### Network Assumptions

| Environment | Network Access |
|-------------|---------------|
| **Local PC** (Windows/Mac) | Can access GitHub, ghcr.io, Docker Hub, quay.io |
| **China EC2 instance** | No overseas access; can access same-region S3 and ECR |
| **EKS cluster nodes** | Can only pull from same-region ECR |

### Step 1: Clone and Package (Local PC)

```bash
git clone https://github.com/aws-samples/sample-OpenClaw-on-AWS-with-Bedrock.git
cd sample-OpenClaw-on-AWS-with-Bedrock

tar czf openclaw-eks-project.tar.gz eks/ docs/ CLAUDE.md README.md
```

### Step 2: Pull and Save Container Images (Local PC)

```bash
PLATFORM="linux/arm64"  # Graviton nodes
# PLATFORM="linux/amd64"  # Intel/AMD nodes

# Core images (required)
docker pull --platform $PLATFORM ghcr.io/openclaw/openclaw:2026.4.2
docker pull --platform $PLATFORM ghcr.io/astral-sh/uv:0.6-bookworm-slim
docker pull --platform $PLATFORM busybox:1.37
docker pull --platform $PLATFORM nginx:1.27-alpine
docker pull --platform $PLATFORM otel/opentelemetry-collector:0.120.0
docker pull --platform $PLATFORM ghcr.io/openclaw-rocks/openclaw-operator:v0.26.2

# Optional sidecar images
docker pull --platform $PLATFORM chromedp/headless-shell:stable
docker pull --platform $PLATFORM rclone/rclone:1.68
docker pull --platform $PLATFORM tsl0922/ttyd:latest
docker pull --platform $PLATFORM ghcr.io/tailscale/tailscale:latest

# Pull Helm chart OCI artifact
helm pull oci://ghcr.io/openclaw-rocks/charts/openclaw-operator --version 0.26.2 --destination .

# Save images
docker save \
  ghcr.io/openclaw/openclaw:2026.4.2 \
  ghcr.io/astral-sh/uv:0.6-bookworm-slim \
  busybox:1.37 \
  nginx:1.27-alpine \
  otel/opentelemetry-collector:0.120.0 \
  ghcr.io/openclaw-rocks/openclaw-operator:v0.26.2 \
  | gzip > core-images.tar.gz

docker save \
  chromedp/headless-shell:stable \
  rclone/rclone:1.68 \
  tsl0922/ttyd:latest \
  ghcr.io/tailscale/tailscale:latest \
  | gzip > sidecar-images.tar.gz
```

### Step 3: Transfer via S3

```bash
aws configure --profile china  # Region: cn-northwest-1

S3_BUCKET="your-china-s3-bucket"
aws s3 cp core-images.tar.gz s3://$S3_BUCKET/openclaw-deploy/ --profile china --region cn-northwest-1
aws s3 cp sidecar-images.tar.gz s3://$S3_BUCKET/openclaw-deploy/ --profile china --region cn-northwest-1
aws s3 cp openclaw-eks-project.tar.gz s3://$S3_BUCKET/openclaw-deploy/ --profile china --region cn-northwest-1
aws s3 cp openclaw-operator-0.26.2.tgz s3://$S3_BUCKET/openclaw-deploy/ --profile china --region cn-northwest-1
```

### Step 4: Load and Push on China EC2

```bash
REGION="cn-northwest-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com.cn"

# Download from S3
aws s3 cp s3://$S3_BUCKET/openclaw-deploy/ /tmp/openclaw-deploy/ --recursive
cd ~ && tar xzf /tmp/openclaw-deploy/openclaw-eks-project.tar.gz

# Load images
gunzip -c /tmp/openclaw-deploy/core-images.tar.gz | docker load
gunzip -c /tmp/openclaw-deploy/sidecar-images.tar.gz | docker load

# Login to ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR
helm registry login "$ECR" --username AWS \
  --password "$(aws ecr get-login-password --region $REGION)"

# Create repos and push images
for repo in openclaw/openclaw astral-sh/uv library/busybox library/nginx \
            otel/opentelemetry-collector openclaw-rocks/openclaw-operator \
            chromedp/headless-shell rclone/rclone tsl0922/ttyd \
            tailscale/tailscale charts/openclaw-operator; do
  aws ecr create-repository --repository-name $repo --region $REGION 2>/dev/null || true
done

docker tag ghcr.io/openclaw/openclaw:2026.4.2 $ECR/openclaw/openclaw:2026.4.2
docker tag ghcr.io/astral-sh/uv:0.6-bookworm-slim $ECR/astral-sh/uv:0.6-bookworm-slim
docker tag busybox:1.37 $ECR/library/busybox:1.37
docker tag nginx:1.27-alpine $ECR/library/nginx:1.27-alpine
docker tag otel/opentelemetry-collector:0.120.0 $ECR/otel/opentelemetry-collector:0.120.0
docker tag ghcr.io/openclaw-rocks/openclaw-operator:v0.26.2 $ECR/openclaw-rocks/openclaw-operator:v0.26.2

for img in openclaw/openclaw:2026.4.2 astral-sh/uv:0.6-bookworm-slim \
           library/busybox:1.37 library/nginx:1.27-alpine \
           otel/opentelemetry-collector:0.120.0 \
           openclaw-rocks/openclaw-operator:v0.26.2; do
  docker push $ECR/$img
done

# Push sidecar images
docker tag chromedp/headless-shell:stable $ECR/chromedp/headless-shell:stable
docker tag rclone/rclone:1.68 $ECR/rclone/rclone:1.68
docker tag tsl0922/ttyd:latest $ECR/tsl0922/ttyd:latest
docker tag ghcr.io/tailscale/tailscale:latest $ECR/tailscale/tailscale:latest

for img in chromedp/headless-shell:stable rclone/rclone:1.68 \
           tsl0922/ttyd:latest tailscale/tailscale:latest; do
  docker push $ECR/$img
done

# Push Helm chart
helm push /tmp/openclaw-deploy/openclaw-operator-0.26.2.tgz oci://$ECR/charts
```

### Step 5: Terraform Deploy

```bash
cd ~/eks/terraform
terraform workspace new china 2>/dev/null || terraform workspace select china
terraform init -input=false

terraform apply -auto-approve \
  -var="region=cn-northwest-1" \
  -var="name=openclaw-cn" \
  -var="architecture=arm64" \
  -var="enable_efs=true"
```

### Step 6: Deploy Instance

```bash
aws eks --region cn-northwest-1 update-kubeconfig --name openclaw-cn
kubectl apply -f eks/manifests/examples/openclaw-bedrock-instance.yaml
# Edit the manifest to add spec.registry pointing to your China ECR
```

### File Manifest

| File | Size (approx.) | Description |
|------|----------------|-------------|
| `openclaw-eks-project.tar.gz` | ~5 MB | Terraform modules, scripts |
| `core-images.tar.gz` | ~1 GB | OpenClaw + operator + base images |
| `sidecar-images.tar.gz` | ~100 MB | Optional sidecars (excludes ollama) |
| `openclaw-operator-0.26.2.tgz` | ~50 KB | Operator Helm chart |
| **Total** | **~1.1 GB** | |

> `ollama/ollama` (~3.4 GB) is too large for routine transfer. Only include it if you need local LLM inference.
