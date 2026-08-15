---
name: k8s-security-policies
description: "Applies namespace Pod Security Standards, default-deny NetworkPolicy, least-privilege RBAC, Gatekeeper/Kyverno admission, and optional Istio STRICT mTLS on Kubernetes. Use when the work is network segmentation, pod hardening, or CIS/NIST control mapping. Not for Docker Compose, Swarm, or Nomad; not a generic app-manifest deploy chair."
version: 1.0.1
risk: unknown
source: community
date_added: "2026-02-27"
---

# Kubernetes Security Policies

Defense-in-depth security for Kubernetes clusters using Pod Security Standards, NetworkPolicy, RBAC, admission control (OPA Gatekeeper), and service mesh policies (Istio). Use this skill whenever the task involves securing pods, restricting network traffic, configuring role-based access, or enforcing compliance controls in a Kubernetes cluster.

## When to Use

- Implementing network segmentation between namespaces or tiers (frontend → backend → database)
- Configuring Pod Security Standards (privileged, baseline, restricted) at the namespace level
- Setting up least-privilege RBAC for users and service accounts
- Creating admission control policies with OPA Gatekeeper or Kyverno
- Securing multi-tenant clusters
- Hardening pod security contexts (non-root, read-only FS, dropped capabilities)
- Implementing mTLS and authorization policies with Istio service mesh
- Meeting compliance requirements (CIS Benchmark, NIST CSF)

## Do Not Use This Skill When

- The task is unrelated to Kubernetes security policies
- You need a different domain or tool outside this scope
- The cluster is not running Kubernetes (e.g., Docker Swarm, Nomad)

## Prerequisites

- A running Kubernetes cluster (v1.25+ recommended for Pod Security Standards)
- `kubectl` installed and configured with cluster admin access
- A CNI plugin that supports NetworkPolicy (Calico, Cilium, Weave Net, or similar)
- For OPA Gatekeeper: Gatekeeper controller installed in the cluster
- For Istio policies: Istio service mesh installed

**Windows (PowerShell) note:** All `kubectl` commands work identically in PowerShell. Use `kubectl` directly — no path adjustments needed. For multi-line YAML, save to a file first and apply with `kubectl apply -f <file>.yaml`.

## Procedure

### 1. Apply Pod Security Standards at the Namespace Level

Pod Security Standards replace the deprecated PodSecurityPolicy (removed in v1.25). They are enforced via namespace labels.

**Restricted namespace (most secure — recommended for production workloads):**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: restricted-ns
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

**Baseline namespace (minimally restrictive):**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: baseline-ns
  labels:
    pod-security.kubernetes.io/enforce: baseline
    pod-security.kubernetes.io/audit: baseline
    pod-security.kubernetes.io/warn: baseline
```

**Privileged namespace (unrestricted — use only for system components):**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: privileged-ns
  labels:
    pod-security.kubernetes.io/enforce: privileged
    pod-security.kubernetes.io/audit: privileged
    pod-security.kubernetes.io/warn: privileged
```

Apply:

```powershell
kubectl apply -f restricted-ns.yaml
```

The three modes work together:
- **enforce** — blocks pods that violate the policy
- **audit** — logs a violation audit event but allows the pod
- **warn** — returns a warning to the API client but allows the pod

### 2. Implement Network Policies

Start with a default-deny-all policy, then layer allow rules on top.

**Default deny all ingress and egress:**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

**Allow frontend → backend on port 8080:**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
```

**Allow DNS egress (required for pod DNS resolution):**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53
```

Apply:

```powershell
kubectl apply -f default-deny-all.yaml
kubectl apply -f allow-frontend-to-backend.yaml
kubectl apply -f allow-dns.yaml
```

> **When to load reference files:**
> - Load `assets/network-policy-template.yaml` when you need additional NetworkPolicy patterns (database access, namespace isolation, egress to external services).
> - Load `assets/pod-security-template.yaml` when you need pre-built pod security context templates.

### 3. Configure RBAC (Least Privilege)

**Namespace-scoped Role (read pods only):**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: production
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
```

**Cluster-wide ClusterRole (read secrets — use sparingly):**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "watch", "list"]
```

**RoleBinding (bind Role to users and service accounts):**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: production
subjects:
- kind: User
  name: jane
  apiGroup: rbac.authorization.k8s.io
- kind: ServiceAccount
  name: default
  namespace: production
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

Apply:

```powershell
kubectl apply -f role.yaml
kubectl apply -f rolebinding.yaml
```

> **When to load reference files:**
> - Load `references/rbac-patterns.md` when you need advanced RBAC patterns (aggregated ClusterRoles, service account token rotation, impersonation rules, multi-tenant isolation).

### 4. Harden Pod Security Context

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: myapp:1.0
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
```

Key hardening controls:
- `runAsNonRoot: true` — prevents running as UID 0
- `runAsUser: 1000` — explicit non-root UID
- `allowPrivilegeEscalation: false` — blocks `setuid` binaries
- `readOnlyRootFilesystem: true` — prevents writes to root filesystem
- `capabilities.drop: [ALL]` — drops all Linux capabilities
- `seccompProfile: RuntimeDefault` — applies default seccomp profile

### 5. Enforce Policies with OPA Gatekeeper

**ConstraintTemplate (define the policy logic in Rego):**

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          type: object
          properties:
            labels:
              type: array
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels
        violation[{"msg": msg, "details": {"missing_labels": missing}}] {
          provided := {label | input.review.object.metadata.labels[label]}
          required := {label | label := input.parameters.labels[_]}
          missing := required - provided
          count(missing) > 0
          msg := sprintf("missing required labels: %v", [missing])
        }
```

**Constraint (enforce the policy on Deployments):**

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: require-app-label
spec:
  match:
    kinds:
      - apiGroups: ["apps"]
        kinds: ["Deployment"]
  parameters:
    labels: ["app", "environment"]
```

Apply:

```powershell
kubectl apply -f constraint-template.yaml
kubectl apply -f constraint.yaml
```

### 6. Service Mesh Security (Istio)

**Enforce strict mTLS namespace-wide:**

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT
```

**AuthorizationPolicy (allow only frontend service account to reach backend):**

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-frontend
  namespace: production
spec:
  selector:
    matchLabels:
      app: backend
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/production/sa/frontend"]
```

Apply:

```powershell
kubectl apply -f peer-authentication.yaml
kubectl apply -f authorization-policy.yaml
```

## Best Practices

1. **Implement Pod Security Standards** at namespace level — use `restricted` for production, `baseline` for dev, `privileged` only for system namespaces
2. **Default-deny all NetworkPolicy** first, then add allow rules incrementally
3. **Apply least-privilege RBAC** — prefer namespace-scoped Roles over ClusterRoles; never grant `*` verbs on `*` resources
4. **Enable admission control** (OPA Gatekeeper or Kyverno) to enforce policies before resources are created
5. **Run containers as non-root** with `runAsNonRoot: true` and explicit `runAsUser`
6. **Use read-only root filesystem** (`readOnlyRootFilesystem: true`) and mount writable volumes explicitly
7. **Drop all capabilities** (`capabilities.drop: [ALL]`) and add back only what is needed
8. **Implement resource quotas and limit ranges** per namespace to prevent resource exhaustion
9. **Enable audit logging** for security events — configure audit policy to log authentication, authorization, and admission decisions
10. **Regular security scanning** of container images (Trivy, Grype, Snyk)

## Compliance Frameworks

### CIS Kubernetes Benchmark

- Use RBAC authorization (not ABAC or AlwaysAllow)
- Enable audit logging with appropriate retention
- Use Pod Security Standards (restricted level for workloads)
- Configure network policies for namespace isolation
- Implement secrets encryption at rest (`--encryption-provider-config`)
- Enable node authentication with client certificates or cloud IAM

### NIST Cybersecurity Framework

- **Identify** — inventory all RBAC bindings, service accounts, and network policies
- **Protect** — implement defense in depth (pod security, network policies, mTLS)
- **Detect** — enable audit logging and security monitoring
- **Respond** — configure alerting on policy violations
- **Recover** — maintain GitOps-managed policy definitions for rapid redeployment

## Pitfalls

- **CNI does not support NetworkPolicy** — Not all CNI plugins enforce NetworkPolicy. Flannel alone does not; you need Calico, Cilium, or a compatible plugin. Check with `kubectl get nodes -o wide` and verify your CNI. A default-deny policy with an unsupported CNI silently does nothing.
- **Default-deny blocks DNS** — Applying a default-deny egress policy without an explicit DNS allow rule breaks pod name resolution. Always apply the DNS egress policy alongside or before the default-deny.
- **PodSecurityPolicy is removed** — PSP was removed in Kubernetes v1.25. Do not create PSP resources on v1.25+ clusters; use Pod Security Standards (namespace labels) instead.
- **ClusterRole with secret access** — Granting `get/list/watch` on secrets cluster-wide is a high-risk privilege. Prefer namespace-scoped Roles and use `serviceAccountToken` projection instead of mounting secrets.
- **enforce mode blocks existing pods** — Applying `enforce: restricted` to a namespace with non-compliant running pods does not evict them, but blocks updates and new pods. Audit first with `audit` mode before enforcing.
- **NetworkPolicy podSelector is not a label selector for namespaces** — To select pods in another namespace, you need both `namespaceSelector` and `podSelector` in the same `from` entry (AND logic). Placing them in separate entries creates OR logic.
- **Gatekeeper constraints do not retroactively check** — Existing resources are not validated when a constraint is applied. Use `kubectl get k8srequiredlabels require-app-label -o yaml` to see violations, or run `gatekeeper audit` manually.
- **Istio STRICT mTLS breaks non-mesh clients** — If external clients call services directly (not through the ingress gateway), STRICT mTLS will reject them. Use PERMISSIVE mode during migration.

## Verification

**Verify Pod Security Standards are applied:**

```powershell
kubectl get namespace restricted-ns --show-labels
# Expected: pod-security.kubernetes.io/enforce=restricted
```

**Verify NetworkPolicy is active:**

```powershell
kubectl get networkpolicy -n production
kubectl describe networkpolicy default-deny-all -n production
```

**Verify RBAC permissions (check what a service account can do):**

```powershell
kubectl auth can-i list pods --as system:serviceaccount:production:default
# Expected: yes

kubectl auth can-i '*' '*' --as system:serviceaccount:production:default
# Expected: no (unless explicitly granted)
```

**Verify pod security context is enforced:**

```powershell
kubectl get pod secure-pod -o jsonpath='{.spec.securityContext}' | ConvertFrom-Json
# Expected: runAsNonRoot=true, runAsUser=1000
```

**Verify Gatekeeper constraint violations:**

```powershell
kubectl get k8srequiredlabels require-app-label -o yaml
# Check status.violations section for non-compliant resources
```

**Verify Istio mTLS and authorization:**

```powershell
kubectl get peerauthentication -n production
kubectl get authorizationpolicy -n production
```

**Test network isolation (from a frontend pod, try to reach backend):**

```powershell
kubectl exec -it deploy/frontend -n production -- curl -s -o /dev/null -w "%{http_code}" http://backend:8080
# Expected: 200 (allowed by NetworkPolicy)
```

**Test denied traffic (from a non-frontend pod, try to reach backend):**

```powershell
kubectl exec -it deploy/debug -n production -- curl -s -o /dev/null -w "%{http_code}" http://backend:8080
# Expected: connection refused or timeout (denied by NetworkPolicy)
```

## Reference Files

- `assets/network-policy-template.yaml` — Additional NetworkPolicy examples (database isolation, egress to external APIs, namespace-wide defaults)
- `assets/pod-security-template.yaml` — Pod security context templates for common workloads
- `references/rbac-patterns.md` — Advanced RBAC patterns (aggregated roles, service account token projection, multi-tenant isolation, break-glass access)

## Related Skills

- `k8s-manifest-generator` — For creating secure Kubernetes manifests with built-in security contexts
- `gitops-workflow` — For automated policy deployment and GitOps-based policy management

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
- NetworkPolicy enforcement depends on the CNI plugin — verify CNI compatibility before applying policies.
- OPA Gatekeeper and Istio require their respective controllers installed in the cluster.
