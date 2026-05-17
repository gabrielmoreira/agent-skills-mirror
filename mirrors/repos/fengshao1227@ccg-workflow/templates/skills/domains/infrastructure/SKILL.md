---
name: infrastructure
description: 云原生基础设施。Kubernetes、Helm、Kustomize、Operator、CRD、GitOps、ArgoCD、Flux、IaC、Terraform、Pulumi、CDK。当用户提到 K8s、Helm、GitOps、IaC 时路由到此。
license: MIT
user-invocable: false
disable-model-invocation: false
---

# 云原生基础设施 · Infrastructure

## 域概览

```
                    GitOps 控制平面
                          |
        +-----------------+-----------------+
        |                 |                 |
    ArgoCD/Flux      Kubernetes         IaC 层
        |                 |                 |
   Git Repo ------> Helm/Kustomize --> Terraform/Pulumi
        |                 |                 |
    声明式配置        容器编排          云资源管理
```

---

## Kubernetes 容器编排

### Helm Chart 开发

标准结构：`Chart.yaml` + `values.yaml` + `templates/` + `charts/`

核心要点：
- Chart.yaml：`apiVersion: v2`, dependencies 声明子 Chart（condition 控制启用）
- values.yaml 设计：image / replicaCount / resources / autoscaling / service / ingress / probes / env / persistence
- Deployment 模板：使用 `_helpers.tpl` 定义 `fullname` / `labels` / `selectorLabels`
- 配置校验：`checksum/config: {{ include ... | sha256sum }}` 触发滚动更新
- 安全上下文：`runAsNonRoot: true, runAsUser: 1000`

关键命令：
- `helm lint` / `helm template --debug` 验证
- `helm install -f values-prod.yaml` 部署
- `helm upgrade --reuse-values` 升级
- `helm rollback <release> <revision>` 回滚
- `helm push <chart>.tgz oci://registry` 推送 OCI

### Kustomize 配置管理

目录结构：`base/` + `overlays/{dev,staging,production}/`

核心能力：
- base/kustomization.yaml：resources / commonLabels / images / configMapGenerator / secretGenerator
- overlay：namespace / patchesStrategicMerge / patchesJson6902 / replicas / images / configMapGenerator(behavior: merge)
- 命令：`kubectl apply -k overlays/production` / `kubectl diff -k`

### Operator 模式

- CRD 定义：openAPIV3Schema 声明 spec/status，subresources(status/scale)
- Controller 核心循环：Get CR → 构建期望状态 → Create/Update 子资源 → 更新 Status
- OwnerReferences：子资源关联 CR，级联删除
- 初始化：`operator-sdk init` → `create api` → `make manifests` → `make install`

### 部署策略

| 策略 | 实现方式 | 适用场景 |
|------|----------|----------|
| 滚动更新 | `strategy.rollingUpdate` maxSurge/maxUnavailable | 默认策略 |
| 蓝绿部署 | 两个 Deployment + Service selector 切换 | 零停机切换 |
| 金丝雀 | stable(9) + canary(1) 共享 Service | 渐进式验证 |
| Flagger | `Canary` CRD + 自动分析指标 | 自动化金丝雀 |

### K8s Checklist

- [ ] 健康检查：livenessProbe + readinessProbe 必配
- [ ] 资源限制：requests + limits 防止资源耗尽
- [ ] HPA：CPU/Memory/自定义指标自动扩缩容
- [ ] PDB：`minAvailable` 防止滚动更新中断
- [ ] ResourceQuota + LimitRange：命名空间资源配额
- [ ] 镜像使用 Digest 确保一致性
- [ ] Pod 反亲和性分散到不同节点
- [ ] 密钥外部化：External Secrets Operator

---

## GitOps 持续部署

### ArgoCD vs Flux

| 特性 | ArgoCD | Flux |
|------|--------|------|
| Web UI | 功能强大 | 无（可用 Weave GitOps） |
| 多租户 | Projects + RBAC | 需额外配置 |
| 多集群 | 原生支持 | 原生支持 |
| 镜像自动更新 | 需 Image Updater | 原生支持 |
| 渐进式交付 | Argo Rollouts | Flagger |
| CNCF | Graduated | Graduated |

### ArgoCD 核心模式

- Application：source(repoURL/path/targetRevision) + destination(server/namespace)
- syncPolicy：`automated(prune: true, selfHeal: true)` + retry
- ignoreDifferences：忽略 HPA 修改的 `/spec/replicas`
- ApplicationSet：Git 目录生成器，一套模板管理多环境
- 多集群：`argocd cluster add` 注册集群
- Notifications：ConfigMap 配置 Slack/Email 通知模板
- Rollouts：`Canary` CRD + steps(setWeight/pause) + AnalysisTemplate(Prometheus 查询)

### Flux 核心模式

- GitRepository：`interval: 1m`, ref branch, secretRef
- Kustomization：path + prune + healthChecks + postBuild substitute
- HelmRepository + HelmRelease：chart + values + install/upgrade remediation
- ImageRepository + ImagePolicy + ImageUpdateAutomation：自动检测新镜像并提交 Git

### 多环境管理

```
fleet-infra/
├── clusters/{dev,staging,production}/  # 每集群入口
├── infrastructure/base + overlays/     # 基础组件
└── apps/base + overlays/              # 应用配置
```

### 密钥管理

- Sealed Secrets：`kubeseal` 加密 → 提交 Git → Controller 解密
- External Secrets Operator：SecretStore(AWS SM) + ExternalSecret → 自动同步

### GitOps Checklist

- [ ] Git 为唯一真相源，所有变更通过 PR
- [ ] 自动同步 + 自愈（selfHeal）
- [ ] 密钥加密存储（Sealed Secrets / External Secrets）
- [ ] 渐进式交付（Rollouts / Flagger）
- [ ] 多环境目录隔离
- [ ] 回滚策略：保留历史版本

---

## 基础设施即代码 (IaC)

### 工具对比

| 工具 | 语言 | 状态管理 | 云支持 | 学习曲线 |
|------|------|----------|--------|----------|
| Terraform | HCL | 显式(S3/TF Cloud) | 全平台 | 中等 |
| Pulumi | Python/TS/Go | 自动(Pulumi Cloud) | 全平台 | 较低 |
| AWS CDK | Python/TS | CloudFormation | AWS | 中等 |

### Terraform 核心模式

项目结构：`modules/{vpc,eks,rds}/` + `environments/{dev,staging,prod}/`

- Provider：版本锁定 `required_providers` + `default_tags`
- Backend：S3 + DynamoDB 锁 + KMS 加密
- 模块化：`variable` → `resource` → `output`，环境通过 `module` 引用
- 远程状态：`data "terraform_remote_state"` 跨模块引用
- 命令流：`init` → `validate` → `fmt` → `plan -out=tfplan` → `apply tfplan`
- 状态管理：`state list/show/mv/rm` / `import` 导入现有资源
- Workspace：`workspace new/select` 多环境隔离

### Pulumi 核心模式

- ComponentResource：自定义资源组（VPC/EKS 封装为类）
- Config：`pulumi.Config()` 读取 stack 配置
- Outputs：`pulumi.export()` 导出值
- 命令：`preview` → `up` → `stack output` / `destroy`

### AWS CDK 核心模式

- Stack：继承 `Stack`，使用 L2 Constructs（`ec2.Vpc` / `eks.Cluster`）
- 跨 Stack 引用：通过构造函数参数传递
- 命令：`synth` → `diff` → `deploy --all` / `bootstrap`

### IaC Checklist

- [ ] 模块化：可复用组件抽象为模块
- [ ] 环境隔离：不同环境不同 State
- [ ] 远程状态 + 状态锁定
- [ ] Provider 版本锁定
- [ ] 密钥管理：Secrets Manager / SSM
- [ ] 统一资源标签
- [ ] Plan 后人工审查再 Apply
- [ ] CI/CD 集成自动化

---

## 最佳实践

| 层级 | 工具选择 | 原则 |
|------|----------|------|
| 应用部署 | Helm + Kustomize | 模板化 + 环境差异 |
| 持续交付 | ArgoCD / Flux | Git 为唯一真相源 |
| 基础设施 | Terraform / Pulumi | 声明式 + 状态管理 |
| 配置管理 | External Secrets | 密钥外部化 |
| 可观测性 | Prometheus + Grafana | 指标 + 可视化 |

## 触发词

Kubernetes、K8s、Helm、Kustomize、Operator、CRD、GitOps、ArgoCD、Flux、IaC、Terraform、Pulumi、CDK、基础设施即代码
