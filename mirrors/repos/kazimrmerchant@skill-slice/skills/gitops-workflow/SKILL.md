---
name: gitops-workflow
description: "Installs and operates Kubernetes GitOps with ArgoCD or Flux: app-of-apps layouts, automated prune/selfHeal sync, canary and blue-green rollouts, multi-cluster promotion, and sealed or external secrets. Trigger on Git-as-desired-state delivery or OpenGitOps setup. Not for one-off kubectl apply; not a GitHub Actions or local-git workflow."
version: 1.0.1
risk: critical
source: community
date_added: "2026-02-27"
---

# GitOps Workflow

Complete guide to implementing declarative, Git-based continuous delivery for Kubernetes using ArgoCD or Flux CD, following OpenGitOps principles.

## When to Use

- Setting up GitOps for Kubernetes clusters
- Automating application deployments from Git
- Implementing progressive delivery strategies (canary, blue-green)
- Managing multi-cluster deployments
- Configuring automated sync policies
- Setting up secret management in GitOps

**Do not use this skill when:**
- You need a one-off manual deployment
- You cannot manage cluster access or repo permissions
- You are not deploying to Kubernetes

## Prerequisites

- A running Kubernetes cluster with `kubectl` configured and cluster-admin access
- A Git repository (GitHub, GitLab, or other) with push permissions
- `kubectl` installed and authenticated (`kubectl get nodes` must succeed)
- For ArgoCD: network access to apply manifests from `raw.githubusercontent.com`
- For Flux: `flux` CLI installed (see Procedure step for installation)
- For Windows/PowerShell hosts: `kubectl` works identically in PowerShell; use `Select-String` instead of `grep` and `$env:VAR` instead of `$VAR` for environment variables

## Procedure

### 1. Define Repository Layout and Desired-State Conventions

Establish a clear repo structure separating applications, infrastructure, and GitOps controller configs:

```
gitops-repo/
├── apps/
│   ├── production/
│   │   ├── app1/
│   │   │   ├── kustomization.yaml
│   │   │   └── deployment.yaml
│   │   └── app2/
│   └── staging/
├── infrastructure/
│   ├── ingress-nginx/
│   ├── cert-manager/
│   └── monitoring/
└── argocd/
    ├── applications/
    └── projects/
```

For Flux, use a `clusters/` directory layout:

```
gitops-repo/
├── clusters/
│   ├── production/
│   │   ├── flux-system/
│   │   ├── apps/
│   │   └── infrastructure/
│   └── staging/
└── apps/
    └── base/
```

### 2. Install ArgoCD

```bash
# Create namespace
kubectl create namespace argocd

# Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

> **Load `references/argocd-setup.md`** when the user needs detailed ArgoCD installation, ingress configuration, SSO setup, or RBAC customization beyond the basic install above.

### 3. Create an ArgoCD Application

```yaml
# argocd/applications/my-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/gitops-repo
    targetRevision: main
    path: apps/production/my-app
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

Apply it:

```bash
kubectl apply -f argocd/applications/my-app.yaml
```

### 4. App of Apps Pattern (ArgoCD)

For managing many applications from a single root Application:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: applications
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/gitops-repo
    targetRevision: main
    path: argocd/applications
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated: {}
```

### 5. Install Flux CD

```bash
# Install Flux CLI (macOS)
brew install fluxcd/tap/flux

# Alternative: download the official installer, inspect it, then execute it
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
curl -fsSLo "$tmpdir/flux-install.sh" https://fluxcd.io/install.sh
cat "$tmpdir/flux-install.sh"  # review the full installer before sudo
sudo bash "$tmpdir/flux-install.sh"

# Bootstrap Flux
flux bootstrap github \
  --owner=org \
  --repository=gitops-repo \
  --branch=main \
  --path=clusters/production \
  --personal
```

### 6. Create Flux GitRepository Source

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/org/my-app
  ref:
    branch: main
```

### 7. Create Flux Kustomization

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 5m
  path: ./deploy
  prune: true
  sourceRef:
    kind: GitRepository
    name: my-app
```

### 8. Configure Sync Policies

**ArgoCD auto-sync:**

```yaml
syncPolicy:
  automated:
    prune: true      # Delete resources not in Git
    selfHeal: true   # Reconcile manual changes
    allowEmpty: false
  retry:
    limit: 5
    backoff:
      duration: 5s
      factor: 2
      maxDuration: 3m
```

**Flux sync:**

```yaml
spec:
  interval: 1m
  prune: true
  wait: true
  timeout: 5m
```

> **Load `references/sync-policies.md`** when the user needs advanced sync configuration: retry/backoff tuning, health assessments, wave sync, or multi-environment promotion flows.

### 9. Progressive Delivery

**Canary deployment with ArgoCD Rollouts:**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app
spec:
  replicas: 5
  strategy:
    canary:
      steps:
      - setWeight: 20
      - pause: {duration: 1m}
      - setWeight: 50
      - pause: {duration: 2m}
      - setWeight: 100
```

**Blue-green deployment:**

```yaml
strategy:
  blueGreen:
    activeService: my-app
    previewService: my-app-preview
    autoPromotionEnabled: false
```

### 10. Secret Management

**Option A — External Secrets Operator (recommended):**

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: db-credentials
  data:
  - secretKey: password
    remoteRef:
      key: prod/db/password
```

**Option B — Sealed Secrets:**

```bash
# Encrypt secret
kubeseal --format yaml < secret.yaml > sealed-secret.yaml

# Commit sealed-secret.yaml to Git
```

> **HARD RULE:** Never commit plaintext Kubernetes Secrets to Git. Always use sealed secrets or an external secret manager (External Secrets Operator, Vault, cloud KMS).

## Pitfalls

1. **Auto-sync to production without approvals** — Avoid enabling `automated.sync` on production Applications without a prior approval gate. Use `autoPromotionEnabled: false` for blue-green or manual sync for production.
2. **Secrets in Git** — Never store raw Kubernetes Secret manifests in Git. Use Sealed Secrets or External Secrets Operator.
3. **Missing `prune: true`** — Without prune, deleted Git resources remain in the cluster, causing drift between Git and cluster state.
4. **`selfHeal: true` on namespaces with manual operators** — Self-heal will revert manual changes made by operators (e.g., HPA scaling), causing conflicts.
5. **Flux bootstrap with wrong `--path`** — The `--path` flag determines where Flux stores its manifests in the repo. Changing it later requires manual cleanup.
6. **ArgoCD `argocd-initial-admin-secret` not deleted** — After changing the admin password, delete the initial secret: `kubectl -n argocd delete secret argocd-initial-admin-secret`. Leaving it is a security risk.
7. **No RBAC on Git repo** — Anyone with push access can deploy anything. Implement branch protection and required reviews.
8. **No notifications on sync failure** — Without alerts, drift or sync failures go unnoticed. Enable ArgoCD notifications or Flux alert providers.
9. **Windows PowerShell line-continuation** — In PowerShell, use backtick `` ` `` instead of `\` for line continuation in multi-line commands. YAML files are unaffected.
10. **Flux installer not inspected before execution** — Always review the downloaded `flux-install.sh` before running with `sudo`, as shown in the procedure.

## Verification

### ArgoCD

```bash
# Check ArgoCD server is running
kubectl get pods -n argocd -l app.kubernetes.io/name=argocd-server

# Verify application sync status
argocd app get my-app

# Check for out-of-sync resources
argocd app diff my-app

# Force sync if needed
argocd app sync my-app --prune
argocd app sync my-app --force
```

Expected output: `Health: Healthy` and `Sync Status: Synced`.

### Flux

```bash
# Check Flux controllers are running
kubectl get pods -n flux-system

# Verify GitRepository is ready
flux get sources git

# Verify Kustomization is reconciling
flux get kustomizations

# Check reconciliation logs
flux logs --all-namespaces
```

Expected output: `Ready: True` for all sources and kustomizations.

### General Cluster Verification

```bash
# Confirm deployed resources match Git state
kubectl get all -n production

# Verify no orphaned resources (prune working)
kubectl get deployments -n production
```

## Related Skills

- `k8s-manifest-generator` — For creating Kubernetes manifests
- `helm-chart-scaffolding` — For packaging applications as Helm charts

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
