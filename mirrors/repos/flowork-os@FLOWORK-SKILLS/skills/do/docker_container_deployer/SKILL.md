---
name: docker_container_deployer
description: Sovereign runbook for Docker multi-stage containerization, Compose orchestration, volume lifecycle, and rootless security hardening
keywords: ["docker deployer", "containerization", "dockerfile build", "docker compose", "multi stage build", "container hardening", "rootless docker", "container networking", "volume persistence", "healthcheck probe", "entrypoint script", "image layer cache", "docker registry", "container isolation", "restart policy", "resource limits", "port forwarding", "environment injection", "oci container", "docker inspect"]
---

# ⚙️ SKILL: DOCKER CONTAINER DEPLOYER

## 1. Intent & Trigger Boundaries
- **Intent**: Scaffolding, containerization, dan orkestrasi container Docker untuk service Flowork OS, microservices, database engine, serta pipeline CI/CD portabel.
- **Trigger**: Diminta membuat Dockerfile, docker-compose.yml, container hardening, isolasi microservice, konfigurasi volume data, atau debugging runtime container yang bermasalah.
- **Boundaries**: Tidak mengurus kluster multi-node Kubernetes enterprise (gunakan `k8s_cluster_commander`). Fokus pada Docker engine dan Compose runtime lokal / standalone host.

## 2. Standard Operating Procedures (SOP)
1. **Multi-Stage Build Scaffolding**:
   - Selalu pisahkan `builder` stage dan `runtime` stage untuk memangkas image size (gunakan Alpine/Distroless/Debian-slim).
   - Manfaatkan cache layer: copy dependensi (`package.json`, `Cargo.toml`, `requirements.txt`) sebelum source code.
2. **Container Security & Rootless Hardening**:
   - Jangan pernah menjalankan proses container sebagai user `root`. Definisikan user non-root (`USER node`, `USER 1000:1000`).
   - Terapkan read-only root filesystem jika memungkinkan dengan mount ephemeral `/tmp` via `tmpfs`.
   - Gunakan `.dockerignore` ketat untuk memblokir secret keys (`.env`, `auth_vault.json`, `.git/`, `.fl_brain/`).
3. **Docker Compose & Healthcheck Orchestration**:
   - Tentukan `healthcheck` dengan `interval`, `timeout`, `retries`, dan `start_period`.
   - Gunakan `depends_on` dengan condition `service_healthy` untuk mencegah race condition antar service.
   - Definisi persistent storage menggunakan named volumes dan isolasi jaringan via custom bridge networks.
4. **Multi-OS Host Portability**:
   - Gunakan newline LF pada seluruh shell script entrypoint (`dos2unix`).
   - Bind mounts wajib menghindari absolute path host Linux/Windows spesifik; gunakan path relatif compose project (`./data:/app/data`).

## 3. Strict Prohibitions & Edge Cases
- **PROHIBITION**: Dilarang hardcode secret / token / API credentials di dalam Dockerfile `ENV` atau image build layers.
- **PROHIBITION**: Dilarang expose port berbahaya ke `0.0.0.0` di environment produksi tanpa otentikasi atau reverse proxy TLS.
- **EDGE CASE**: Masalah file permission bind mount di Linux (UID mismatch) diatasi dengan menyelaraskan UID/GID saat run atau entrypoint mapping dinamis.

## 4. Verification & Exit Code 0 Proof
- Validasi sintaks: `docker compose config` menghasilkan exit code 0 tanpa syntax error.
- Linting Dockerfile: Lolos Docker build sanity check (`docker build --check .` atau `hadolint Dockerfile`).
- Healthcheck runtime: Status container berubah menjadi `healthy` setelah bootstrap.
