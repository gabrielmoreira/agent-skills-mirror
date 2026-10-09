---
name: k8s_cluster_commander
description: Sovereign runbook for Kubernetes manifest orchestration, Pod lifecycle, Ingress routing, Helm charts, and cluster resource scaling
keywords: ["kubernetes commander", "k8s manifest", "pod lifecycle", "helm chart", "deployment spec", "service ingress", "configmap secret", "persistent volume", "cluster scaling", "horizontal pod autoscaler", "namespace isolation", "crd operator", "kubelet probe", "cluster security", "rbac policy", "daemonset controller", "statefulset storage", "rolling update", "cluster telemetry", "kubectl triage"]
---

# ⚙️ SKILL: K8S CLUSTER COMMANDER

## 1. Intent & Trigger Boundaries
- **Intent**: Orkestrasi kluster Kubernetes, pembuatan manifest deklaratif (Deployments, Services, Ingress, RBAC), deployment Helm chart, serta scaling dan triage resource produksi.
- **Trigger**: Diminta membuat spesifikasi Kubernetes, deployment mikroservis ke kluster K8s/k3s/Minikube, Helm templating, pemecahan masalah Pod crash/eviction, atau konfigurasi autoscaling.
- **Boundaries**: Tidak mengurusi arsitektur bare-metal Docker compose single-host (gunakan `docker_container_deployer`). Fokus pada ekosistem kluster Kubernetes.

## 2. Standard Operating Procedures (SOP)
1. **Declarative Manifest Design**:
   - Terapkan pemisahan resource berbasis namespace (`production`, `staging`, `monitoring`).
   - Setiap Deployment wajib memiliki `resources.requests` dan `resources.limits` (CPU & Memory) untuk mencegah noisy-neighbor dan Pod eviction.
   - Buat liveness probe (`/healthz`) dan readiness probe (`/ready`) deterministik dengan toleransi startup time.
2. **State & Configuration Decoupling**:
   - Pisahkan config non-sensitif ke dalam `ConfigMap` dan kredensial sensitif ke dalam `Secret` (atau sealed secrets/external secrets).
   - Layanan stateful wajib menggunakan `StatefulSet` dengan dynamic volume provisioning (`VolumeClaimTemplates`).
3. **Ingress & Service Topology**:
   - Definisikan Service abstraction (`ClusterIP`, `NodePort`, `LoadBalancer`) sesuai exposure layer.
   - Konfigurasi Ingress controller (Nginx/Traefik) dengan TLS termination cert-manager dan anotasi routing presisi.
4. **Helm Packaging & Lifecycle**:
   - Strukturkan Helm chart dengan parameterisasi fleksibel di `values.yaml`.
   - Gunakan `helm lint` dan `helm template` sebelum eksekusi deployment rollouts.

## 3. Strict Prohibitions & Edge Cases
- **PROHIBITION**: Dilarang menggunakan tag image `:latest` di production manifest K8s karena menghambat rollback deterministik.
- **PROHIBITION**: Dilarang membuat Pod tanpa resource requests & limits.
- **EDGE CASE**: Pod stuck di `CrashLoopBackOff` atau `ImagePullBackOff`: telusuri segera via `kubectl describe pod <pod>` dan `kubectl logs <pod> --previous`.

## 4. Verification & Exit Code 0 Proof
- Manifest Dry-run: `kubectl apply --dry-run=client -f <file.yaml>` menghasilkan exit code 0.
- Helm lint test: `helm lint ./chart` sukses dengan status 0 failure.
- Pod rollout check: `kubectl rollout status deployment/<nama>` exit dengan kode 0 (semua replika ready).
