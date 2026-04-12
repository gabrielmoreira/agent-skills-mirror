# 在 Amazon EKS 上部署 OpenClaw

在 Amazon EKS 上部署 OpenClaw Operator 和 AI Agent 实例。支持 **AWS 全球区域**（us-west-2、us-east-1 等）和 **AWS 中国区域**（cn-northwest-1、cn-north-1）。

---

## 前提条件

### 通用要求

| 工具        | 版本要求  | 验证命令 |
|-------------|----------|---------|
| AWS CLI     | >= 2.27  | `aws --version` |
| kubectl     | >= 1.28  | `kubectl version --client` |
| Terraform   | >= 1.3   | `terraform --version` |
| Docker      | >= 20.0  | `docker --version` |
| Helm        | >= 3.12  | `helm version` |

### EKS Pod Identity Agent

使用 [EKS Pod Identity](https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html)（非 IRSA）进行 AWS 权限管理。Terraform 会作为 Managed Addon 自动安装。

### 中国区域额外要求

AWS 中国区域（`cn-northwest-1`、`cn-north-1`）存在网络限制：

| 要求 | 原因 | 处理方式 |
|------|------|---------|
| **镜像同步至中国区 ECR** | `ghcr.io`、Docker Hub 不可访问 | 运行 `china-image-mirror.sh` **在 `terraform apply` 之前** |
| **第三方模型提供商** | Amazon Bedrock **不在中国区域运营** | 使用 LiteLLM 代理或直接 API Key |
| **AWS 中国账户** | 独立分区（`aws-cn`） | 需要单独的 IAM 凭证 |
| **AWS CLI Profile** | 中国账户需要独立的 Profile | `aws configure --profile china` |

#### 中国区网络依赖全景

以下表格列出所有被中国区域防火墙阻断或受影响的外部网络依赖：

| 依赖类型 | 来源地址 | 用途 | 阻断级别 | 解决方案 |
|----------|---------|------|---------|---------|
| **Helm Chart (OCI)** | `oci://ghcr.io/openclaw-rocks/charts` | OpenClaw Operator | 完全阻断 | `china-image-mirror.sh` 同步至 ECR，TF 自动使用 `chart_repository` |
| **Helm Chart (OCI)** | `oci://ghcr.io/kata-containers/kata-deploy-charts` | Kata Containers（可选） | 完全阻断 | 同上 |
| **Helm Chart (OCI)** | `oci://ghcr.io/berriai/litellm-helm` | LiteLLM 代理（可选） | 完全阻断 | 同上 |
| **Helm Chart (HTTPS)** | `https://aws.github.io/eks-charts` | ALB Controller（可选） | 间歇性慢 | GitHub Pages 通常可达；超时则需 VPN |
| **容器镜像** | `ghcr.io/*` | OpenClaw、Operator、uv、Tailscale | 完全阻断 | `china-image-mirror.sh` 同步 + `spec.registry` 重写 |
| **容器镜像** | Docker Hub (`docker.io`) | nginx、OTel、chromium、ollama、ttyd、rclone、busybox | 完全阻断 | 同上 |
| **容器镜像** | `quay.io` | Kata Containers 默认镜像 | 完全阻断 | TF 模块已重写至 `public.ecr.aws` |
| **容器镜像** | `public.ecr.aws` | 监控栈、Karpenter、LiteLLM、Kata、ALB Controller 镜像 | **可访问**（AWS 服务） | 无需额外操作 |
| **EKS Managed Addons** | AWS 内部 | EBS/EFS CSI、Pod Identity Agent | **可访问** | 无需额外操作 |
| **Terraform Registry** | `registry.terraform.io` | Provider 下载 | **可访问** | 无需额外操作 |
| **npm Registry** | `registry.npmjs.org` | Operator init-skills（运行时） | 完全阻断 | 避免在 CRD 中使用 `spec.skills`（npm 前缀）；或预装至镜像 |
| **GitHub API** | `api.github.com` | Operator init-skills（pack: 前缀） | 完全阻断 | 避免使用 `pack:` 前缀的 skills |

> **重要：** `terraform apply` 需要拉取 Helm Chart。在中国区域运行 Terraform 时，必须先执行 `china-image-mirror.sh` 将 Helm Chart 同步至 ECR，Terraform 会自动使用 ECR 作为 Chart 仓库。在全球区域运行 Terraform（远程连接中国 EKS API Server）则无此限制。

#### Helm Chart 使用的容器镜像全景

以下列出所有 Terraform 模块安装的 Helm Chart 及其使用的容器镜像。`public.ecr.aws` 上的镜像可从中国区域直接拉取（AWS 全球服务），无需额外同步。

| Helm Chart | Chart 来源 | 容器镜像（上游） | 镜像来源 | 中国可用 |
|------------|-----------|---------|---------|---------|
| **openclaw-operator** | `oci://ghcr.io/openclaw-rocks/charts` | `ghcr.io/openclaw-rocks/openclaw-operator:v0.26.2` | ghcr.io | 需同步 |
| **aws-load-balancer-controller** | `https://aws.github.io/eks-charts` | `public.ecr.aws/eks/aws-load-balancer-controller:v3.2.1` | ECR Public | 可直接拉取 |
| **kube-prometheus-stack** | `https://prometheus-community.github.io/helm-charts` | `quay.io/prometheus/prometheus:v2.54.1` | quay.io | 需同步 |
| | | `quay.io/prometheus-operator/prometheus-operator:v0.77.1` | quay.io | 需同步 |
| | | `quay.io/prometheus-operator/prometheus-config-reloader:v0.77.1` | quay.io | 需同步 |
| | | `registry.k8s.io/ingress-nginx/kube-webhook-certgen:v20221220-...` | registry.k8s.io | 需同步 |
| | | `registry.k8s.io/kube-state-metrics/kube-state-metrics:v2.13.0` | registry.k8s.io | 需同步 |
| | | `quay.io/prometheus/node-exporter:1.8.2` | quay.io | 需同步 |
| **grafana** | `https://grafana.github.io/helm-charts` | `docker.io/grafana/grafana:11.2.1` | Docker Hub | 需同步 |
| | | `quay.io/kiwigrid/k8s-sidecar:1.27.4` | quay.io | 需同步 |
| **karpenter** | `oci://public.ecr.aws/karpenter` | `public.ecr.aws/karpenter/controller:1.7.4` | ECR Public | 可直接拉取 |
| **kata-deploy** | `oci://ghcr.io/kata-containers/kata-deploy-charts` | `quay.io/kata-containers/kata-deploy:3.27.0` | quay.io | 需同步 |
| **litellm** | `oci://ghcr.io/berriai/litellm-helm` | `docker.litellm.ai/berriai/litellm:main-latest` | docker.litellm.ai | 需同步 |
| | | `public.ecr.aws/bitnami/postgresql:latest` | ECR Public | 可直接拉取 |

> **结论：** `china-image-mirror.sh` 会将所有上游镜像同步至中国区私有 ECR，Terraform 自动为中国区域使用 ECR 镜像。仅 `public.ecr.aws` 上的镜像（ALB Controller、Karpenter、PostgreSQL）无需额外同步。

#### 中国区模型提供商

Amazon Bedrock 不在 AWS 中国区域运营。两种替代方案：

1. **LiteLLM 代理**（推荐）：在同一集群部署（Terraform 设置 `enable_litellm = true`）。提供 OpenAI 兼容接口，可路由至任意模型提供商。

2. **直接 API Key**：创建 Kubernetes Secret 并在 OpenClawInstance CRD 中引用：

```bash
kubectl -n openclaw create secret generic model-api-keys \
  --from-literal=ANTHROPIC_API_KEY=sk-ant-...

kubectl -n openclaw patch openclawinstance AGENT名称 --type=merge \
  -p '{"spec":{"envFrom":[{"secretRef":{"name":"model-api-keys"}}]}}'
```

#### 同步容器镜像至中国区 ECR

在具有良好国际网络的机器上运行（如全球区域的 EC2 实例）：

```bash
bash eks/scripts/china-image-mirror.sh \
  --region cn-northwest-1 \
  --name openclaw-cn \
  --profile china
```

该脚本同步全部容器镜像至中国区 ECR，并同步 Helm Chart OCI 制品：

**容器镜像（11 个）：**

| 镜像 | 用途 | 来源 |
|------|------|------|
| `ghcr.io/openclaw/openclaw:2026.4.2` | OpenClaw 主容器 + init 容器 | ghcr.io |
| `ghcr.io/astral-sh/uv:0.6-bookworm-slim` | Python 依赖安装 Init 容器 | ghcr.io |
| `busybox:1.37` | 配置文件复制 Init 容器（overwrite 模式） | Docker Hub |
| `nginx:1.27-alpine` | Gateway 代理 Sidecar | Docker Hub |
| `otel/opentelemetry-collector:0.120.0` | 可观测性 Sidecar | Docker Hub |
| `chromedp/headless-shell:stable` | 浏览器自动化 Sidecar | Docker Hub |
| `ghcr.io/tailscale/tailscale:latest` | Tailscale VPN Sidecar | ghcr.io |
| `ollama/ollama:latest` | 本地 LLM 推理 Sidecar | Docker Hub |
| `tsl0922/ttyd:latest` | Web 终端 Sidecar | Docker Hub |
| `rclone/rclone:1.68` | S3 备份/恢复 Job | Docker Hub |
| `ghcr.io/openclaw-rocks/openclaw-operator:v0.26.2` | Operator 本身 | ghcr.io |

**Helm Chart OCI 制品（1-3 个）：**

| Chart | 用途 | 来源 |
|-------|------|------|
| `oci://ghcr.io/openclaw-rocks/charts/openclaw-operator` | Operator 部署（必需） | ghcr.io |
| `oci://ghcr.io/kata-containers/kata-deploy-charts/kata-deploy` | Kata Containers（可选） | ghcr.io |
| `oci://ghcr.io/berriai/litellm-helm/litellm-helm` | LiteLLM 代理（可选） | ghcr.io |

---

## 使用 Terraform 部署

创建完整基础设施：VPC、EKS 集群、EFS 存储、OpenClaw Operator，以及可选的 ALB Controller、Kata Containers、监控栈和 LiteLLM。

### 第一步：同步镜像至 ECR（仅中国区域）

> **中国区域必须在 `terraform apply` 之前执行此步骤。** 所有上游镜像仓库（ghcr.io、quay.io、Docker Hub、registry.k8s.io）均被阻断。脚本会将所有镜像和 Helm Chart 同步至 ECR。**跳过此步骤将导致 `terraform apply` 失败。**

```bash
bash eks/scripts/china-image-mirror.sh --region cn-northwest-1 --name openclaw-cn --profile china
```

全球区域直接从上游拉取，无需同步。

### 第二步：Terraform apply

**全球区域：**

```bash
cd eks/terraform
terraform init

terraform apply \
  -var="name=openclaw-prod" \
  -var="region=us-west-2" \
  -var="architecture=arm64" \
  -var="enable_efs=true"
```

**中国区域：**

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

### 第三步：配置 kubectl

```bash
# 全球区域
aws eks --region us-west-2 update-kubeconfig --name openclaw-prod

# 中国区域
AWS_PROFILE=china aws eks --region cn-northwest-1 update-kubeconfig --name openclaw-cn
```

### Terraform 变量参考

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `name` | `openclaw-eks` | 集群和资源名称前缀 |
| `region` | `us-west-2` | AWS 区域（自动检测 `cn-` 前缀为中国区） |
| `architecture` | `arm64` | `arm64`（Graviton）或 `x86` |
| `enable_efs` | `true` | 启用 EFS 持久化存储（设为默认 StorageClass） |
| `enable_alb_controller` | `false` | 启用 AWS Load Balancer Controller（ALB Ingress） |
| `enable_kata` | `false` | 启用 Kata Containers（Firecracker 虚拟机隔离） |
| `enable_monitoring` | `false` | 启用 Prometheus + Grafana 监控栈 |
| `enable_litellm` | `false` | 启用 LiteLLM 代理（中国区域必需） |

---

## 部署 OpenClaw Agent 实例

Terraform 完成后，通过 `kubectl` 部署 AI Agent 实例。

### 基本实例（全球区域）

```yaml
apiVersion: openclaw.rocks/v1alpha1
kind: OpenClawInstance
metadata:
  name: my-agent
  namespace: openclaw
spec:
  image:
    tag: "2026.4.2"
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

### 中国区域实例（ECR 镜像仓库覆盖）

添加 `spec.registry` 将所有镜像地址重写到中国区 ECR：

```yaml
apiVersion: openclaw.rocks/v1alpha1
kind: OpenClawInstance
metadata:
  name: my-agent
  namespace: openclaw
spec:
  image:
    tag: "2026.4.2"
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

### LiteLLM 实例（中国区域）

如果部署了 LiteLLM（`enable_litellm = true`），将 Agent 指向集群内端点：

```yaml
apiVersion: openclaw.rocks/v1alpha1
kind: OpenClawInstance
metadata:
  name: my-agent
  namespace: openclaw
spec:
  image:
    tag: "2026.4.2"
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

### 管理实例

```bash
# 列出实例
kubectl get openclawinstances -n openclaw

# 查看 Pod 状态
kubectl get pods -n openclaw

# 查看日志
kubectl logs -n openclaw my-agent-0 -c openclaw --tail=50

# 删除实例
kubectl delete openclawinstance my-agent -n openclaw
```

### CRD 示例

参见 `eks/manifests/examples/` 目录下的预置示例：
- `openclaw-bedrock-instance.yaml` — 标准 Bedrock 实例
- `openclaw-kata-instance.yaml` — 使用 Firecracker 虚拟机隔离的实例
- `openclaw-slack-instance.yaml` — 集成 Slack Bot 的实例

---

## 架构

```
┌────────────────────────────────────────────────────────┐
│  EKS 集群                                               │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  openclaw 命名空间                                  │ │
│  │                                                     │ │
│  │  ┌──────────────────┐  ┌──────────────────┐        │ │
│  │  │ OpenClawInstance  │  │ OpenClawInstance  │  ...   │ │
│  │  │ StatefulSet + Svc │  │ StatefulSet + Svc │        │ │
│  │  │ + PVC (EFS)       │  │ + PVC (EFS)       │        │ │
│  │  └──────────────────┘  └──────────────────┘        │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  openclaw-operator-system 命名空间                   │ │
│  │  OpenClaw Operator（监听 CRD → 创建 K8s 资源）       │ │
│  └────────────────────────────────────────────────────┘ │
└───────────────────────────┬──────────────────────────────┘
                            │
                 ┌──────────┴──────────┐
                 │    AWS 服务          │
                 │  Bedrock   EFS      │
                 │  ECR       IAM      │
                 └─────────────────────┘
```

### 运行时对比

| 运行时 | 隔离级别 | 存储 | 镜像来源 |
|--------|---------|------|---------|
| **EKS Pod** | cgroups / 命名空间 | EFS | ghcr.io（全球）/ ECR 镜像（中国） |
| **EKS + Kata** | Firecracker 微虚拟机 | EFS | 同上，加 `runtimeClass: kata-qemu` |

---

## 安全考量

### 计算隔离

| 运行时 | 内核 | Prompt 注入风险 |
|--------|------|----------------|
| **EKS Pod** | **共享宿主机内核** | 内核漏洞理论上可利用 |
| EKS + Kata | 独立 Firecracker 虚拟机 | 容器逃逸不可能 |

生产环境如有不可信代码执行需求，建议启用 Kata Containers（`enable_kata = true`）。

---

## 故障排查

### Pod `ImagePullBackOff`（中国区域）

镜像无法从被阻断的仓库拉取。在 OpenClawInstance 中设置 `spec.registry`：

```yaml
spec:
  registry: "ACCOUNT.dkr.ecr.cn-northwest-1.amazonaws.com.cn"
```

### Pod `Pending`（PVC 未绑定）

未设置默认 StorageClass。Terraform 自动将 EFS 设为默认。手动部署的集群需执行：

```bash
kubectl annotate storageclass efs-sc \
  storageclass.kubernetes.io/is-default-class=true
```

### Operator 未运行

```bash
kubectl get deployment -n openclaw-operator-system
kubectl logs -n openclaw-operator-system deployment/openclaw-operator
```

### Pod Identity 403 错误

```bash
# 检查 addon
kubectl get pods -n kube-system -l app.kubernetes.io/name=eks-pod-identity-agent

# 检查关联
aws eks list-pod-identity-associations \
  --cluster-name 集群名称 --namespace openclaw --region 区域
```

---

## 中国区域纯本地部署指南

中国区域（cn-northwest-1、cn-north-1）无法直接访问 ghcr.io、Docker Hub 等境外镜像仓库。以下说明如何在 **仅有中国区域 EC2 实例** 的情况下完成部署，所有境外资源通过本地 PC 中转。

### 网络环境假设

| 环境 | 网络条件 |
|------|---------|
| **本地 PC**（Windows/Mac） | 可访问 GitHub、ghcr.io、Docker Hub |
| **中国 EC2 实例** | 无法访问 ghcr.io/Docker Hub；可访问同区域 S3 和 ECR |
| **EKS 集群节点** | 仅可拉取同区域 ECR 镜像 |

### 前提条件

**本地 PC 需安装：**

| 工具 | 用途 | 下载 |
|------|------|------|
| Docker Desktop | 拉取和保存镜像 | https://www.docker.com/products/docker-desktop |
| AWS CLI v2 | 上传到 S3 | https://aws.amazon.com/cli |
| Git | 克隆仓库 | https://git-scm.com |

**中国 EC2 实例需安装：**

| 工具 | 用途 |
|------|------|
| Docker | 加载和推送镜像到 ECR |
| AWS CLI v2 | S3 下载、ECR 操作 |
| kubectl | 集群管理 |
| Terraform >= 1.3 | 基础设施部署 |
| Helm >= 3.12 | 应用部署 |

### 步骤 1：在本地 PC 克隆仓库并打包

```bash
# 克隆仓库
git clone https://github.com/aws-samples/sample-OpenClaw-on-AWS-with-Bedrock.git
cd sample-OpenClaw-on-AWS-with-Bedrock

# 打包项目（含 Terraform 模块、脚本）
tar czf openclaw-eks-project.tar.gz eks/ docs/ CLAUDE.md README.md
```

### 步骤 2：在本地 PC 拉取并保存容器镜像

根据 EKS 节点架构选择 `--platform`（Graviton 用 `linux/arm64`，Intel/AMD 用 `linux/amd64`）。

```bash
PLATFORM="linux/arm64"  # Graviton 节点
# PLATFORM="linux/amd64"  # Intel/AMD 节点

# 核心镜像（必需）
docker pull --platform $PLATFORM ghcr.io/openclaw/openclaw:2026.4.2
docker pull --platform $PLATFORM ghcr.io/astral-sh/uv:0.6-bookworm-slim
docker pull --platform $PLATFORM busybox:1.37
docker pull --platform $PLATFORM nginx:1.27-alpine
docker pull --platform $PLATFORM otel/opentelemetry-collector:0.120.0
docker pull --platform $PLATFORM ghcr.io/openclaw-rocks/openclaw-operator:v0.26.2

# 可选 sidecar 镜像
docker pull --platform $PLATFORM chromedp/headless-shell:stable       # 浏览器沙箱
docker pull --platform $PLATFORM rclone/rclone:1.68                   # 备份/恢复
docker pull --platform $PLATFORM tsl0922/ttyd:latest                  # Web 终端
docker pull --platform $PLATFORM ghcr.io/tailscale/tailscale:latest   # VPN

# 拉取 Helm Chart OCI 制品（Terraform 部署需要）
helm pull oci://ghcr.io/openclaw-rocks/charts/openclaw-operator --version 0.26.2 --destination .
# 如使用 Kata/LiteLLM 模块，取消注释：
# helm pull oci://ghcr.io/kata-containers/kata-deploy-charts/kata-deploy --version 3.27.0 --destination .
# helm pull oci://ghcr.io/berriai/litellm-helm/litellm-helm --destination .

# 保存为 tar.gz（批量打包减少传输次数）
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

### 步骤 3：通过 S3 中转到中国区域

S3 多部分上传比直接 `docker push` 跨境更可靠、可断点续传。

```bash
# 配置中国区域 AWS CLI profile（如尚未配置）
aws configure --profile china
# Region: cn-northwest-1
# Output: json

S3_BUCKET="你的中国S3桶名"  # 使用已有桶或先创建一个

# 上传镜像文件、Helm Chart 和项目包
aws s3 cp core-images.tar.gz s3://$S3_BUCKET/openclaw-deploy/ --profile china --region cn-northwest-1
aws s3 cp sidecar-images.tar.gz s3://$S3_BUCKET/openclaw-deploy/ --profile china --region cn-northwest-1
aws s3 cp openclaw-eks-project.tar.gz s3://$S3_BUCKET/openclaw-deploy/ --profile china --region cn-northwest-1
# Helm Chart OCI 制品
aws s3 cp openclaw-operator-0.26.2.tgz s3://$S3_BUCKET/openclaw-deploy/ --profile china --region cn-northwest-1
```

> **提示：** 跨境 S3 上传速度约 1-2 MiB/s。核心镜像（~1GB）约需 15-20 分钟。上传完成后，中国区域内 S3 到 EC2 下载速度可达 200+ MiB/s。

### 步骤 4：在中国 EC2 实例上加载并推送镜像

```bash
S3_BUCKET="你的中国S3桶名"
REGION="cn-northwest-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com.cn"

# 下载文件（同区域，速度很快）
aws s3 cp s3://$S3_BUCKET/openclaw-deploy/ /tmp/openclaw-deploy/ --recursive
cd ~ && tar xzf /tmp/openclaw-deploy/openclaw-eks-project.tar.gz

# 加载 Docker 镜像
gunzip -c /tmp/openclaw-deploy/core-images.tar.gz | docker load
gunzip -c /tmp/openclaw-deploy/sidecar-images.tar.gz | docker load

# 登录 ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR
helm registry login "$ECR" --username AWS \
  --password "$(aws ecr get-login-password --region $REGION)"

# 创建 ECR 仓库（幂等操作）
for repo in openclaw/openclaw astral-sh/uv library/busybox library/nginx \
            otel/opentelemetry-collector openclaw-rocks/openclaw-operator \
            chromedp/headless-shell rclone/rclone tsl0922/ttyd \
            tailscale/tailscale charts/openclaw-operator; do
  aws ecr create-repository --repository-name $repo --region $REGION 2>/dev/null || true
done

# 标记并推送核心镜像
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

# 推送可选 sidecar 镜像
docker tag chromedp/headless-shell:stable $ECR/chromedp/headless-shell:stable
docker tag rclone/rclone:1.68 $ECR/rclone/rclone:1.68
docker tag tsl0922/ttyd:latest $ECR/tsl0922/ttyd:latest
docker tag ghcr.io/tailscale/tailscale:latest $ECR/tailscale/tailscale:latest

for img in chromedp/headless-shell:stable rclone/rclone:1.68 \
           tsl0922/ttyd:latest tailscale/tailscale:latest; do
  docker push $ECR/$img
done

# 推送 Helm Chart OCI 制品
helm push /tmp/openclaw-deploy/openclaw-operator-0.26.2.tgz oci://$ECR/charts

echo "所有镜像和 Helm Chart 已推送到 $ECR"
```

### 步骤 5：Terraform 部署

> **前置条件：** 步骤 4 必须已完成（所有容器镜像和 Helm Chart 已推送至中国区 ECR）。否则 `terraform apply` 将因无法拉取镜像/Chart 而失败。

```bash
cd ~/eks/terraform

# 初始化（Terraform provider 从 HashiCorp registry 下载，中国区域可访问）
terraform workspace new china 2>/dev/null || terraform workspace select china
terraform init -input=false

# 部署
terraform apply -auto-approve \
  -var="region=cn-northwest-1" \
  -var="name=openclaw-cn" \
  -var="architecture=arm64" \
  -var="enable_efs=true"
```

> **注意：** 首次 apply 可能因 EKS access entry 传播延迟报 K8s 权限错误，重新执行 `terraform apply` 即可。如 Helm release 卡住，执行 `helm uninstall <name> -n <ns>` 清理后重试。

### 步骤 6：部署实例

```bash
# 配置 kubectl
aws eks --region cn-northwest-1 update-kubeconfig --name openclaw-cn

# 检查节点和 Pod
kubectl get nodes
kubectl get pods -A

# 部署 OpenClaw 实例（编辑 manifest 中的 spec.registry 指向中国区 ECR）
kubectl apply -f eks/manifests/examples/openclaw-bedrock-instance.yaml
```

### 镜像更新流程

后续更新镜像时，重复步骤 2-4（仅拉取变更的镜像）。也可使用 `china-image-mirror.sh` 的 `--platform` 参数：

```bash
# 在可访问境外 registry 的机器上
bash eks/scripts/china-image-mirror.sh \
  --region cn-northwest-1 \
  --name openclaw-cn \
  --profile china \
  --platform linux/arm64 \
  --mirror
```

### 文件清单

部署所需的完整文件列表：

| 文件 | 大小（约） | 说明 |
|------|-----------|------|
| `openclaw-eks-project.tar.gz` | ~5 MB | Terraform 模块、脚本 |
| `core-images.tar.gz` | ~1 GB | OpenClaw + operator + busybox + 基础镜像 |
| `sidecar-images.tar.gz` | ~100 MB | 可选 sidecar（不含 ollama） |
| `openclaw-operator-0.26.2.tgz` | ~50 KB | Operator Helm Chart OCI 制品 |
| **合计** | **~1.1 GB** | |

> `ollama/ollama` 镜像（~3.4 GB）体积过大，建议仅在需要本地 LLM 推理时单独传输。
