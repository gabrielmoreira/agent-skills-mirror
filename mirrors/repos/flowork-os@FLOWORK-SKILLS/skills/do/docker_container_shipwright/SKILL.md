---
name: docker_container_shipwright
description: Sovereign runbook for multi-stage Docker builds, rootless container security, compose orchestration, and zero-leak deployment
keywords: ["docker container", "dockerfile build", "container security", "multi stage build", "docker compose", "container orchestration", "rootless docker", "image size optimization", "layer caching", "container hardening", "docker entrypoint", "environment secrets", "volume management", "container networking", "podman migration", "docker healthcheck", "scratch base image", "alpine minimization", "cve container scan", "container lifecycle"]
---
# 🐳 SKILL: DOCKER CONTAINER SHIPWRIGHT

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk perancangan, optimasi citra Docker, dan orkestrasi container:

## 1. Intent & Trigger Boundaries
- **Pemicu**: Pembuatan containerization baru, pembuatan `Dockerfile` atau `docker-compose.yml`, optimasi ukuran image, dan hardening container.
- **Batasan**: Agnostik arsitektur mesin (Linux amd64/arm64), tanpa membocorkan credential dalam layer build Docker.

## 2. Standard Operating Procedures (SOP)
1. **Multi-Stage Build Minimalis**:
   - Selalu pisahkan build environment (Node, Rust, Golang, Python) dari runtime image akhir.
   - Gunakan base image minimal seperti `distroless`, `alpine`, atau `scratch` untuk container produksi.
2. **Layer Caching Optimization**:
   - Copy dependency manifest lebih awal (`package.json`, `Cargo.toml`, `requirements.txt`) sebelum source code penuh untuk memaksimalkan layer cache.
3. **Rootless & Security Hardening**:
   - Haram menjalankan container sebagai `USER root` di tahap akhir produksi. Buat user dan group khusus (`USER nonroot` / `USER appuser`).
   - Berikan izin file hanya baca (`read-only`) pada filesystem yang tidak membutuhkan persistensi data.
4. **Environment Secret Protection**:
   - Dilarang hardcode credential/secret dalam `ARG` atau `ENV`.
   - Gunakan BuildKit secret mounts (`--mount=type=secret`) atau inject variabel runtime melalui environment vault.

## 3. Strict Prohibitions & Edge Cases
- **Dilarang**: Menyertakan cache package manager (`apk cache`, `apt-get clean`, `rm -rf /var/lib/apt/lists/*`) di layer akhir.
- **Port Mapping**: Gunakan port dinamis/variabel environment, cegah tabrakan port host.

## 4. Verification & Exit Code 0 Proof
- Jalankan build test: `docker build -t test-img .`
- Verifikasi keamanan dan non-root status: `docker run --rm test-img whoami` (harus non-root, Exit Code 0).
