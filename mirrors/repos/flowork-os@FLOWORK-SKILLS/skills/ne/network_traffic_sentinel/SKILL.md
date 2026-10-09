---
name: network_traffic_sentinel
description: Sovereign runbook for network traffic analysis, packet/TLS handshakes, open port auditing, reverse proxy tuning, and connection diagnostics
keywords: ["network sentinel", "traffic analysis", "packet inspection", "tls handshake", "port scanning audit", "firewall rules", "reverse proxy tuning", "websocket monitoring", "grpc diagnostics", "iptables configuration", "nginx proxy setup", "caddy reverse proxy", "connection latency", "tcp dump analysis", "dns resolution audit", "http keepalive", "rate limiting proxy", "network sockets audit", "ssl certificate validation", "host networking triage"]
---
# 🌐 SKILL: NETWORK TRAFFIC SENTINEL

Prosedur Operasi Standar (SOP) resmi kedaulatan Flowork OS untuk monitoring lalu lintas jaringan, audit listening ports, dan optimasi reverse proxy:

## 1. Intent & Trigger Boundaries
- **Pemicu**: Masalah konektivitas IPC, tabrakan port listening, degradasi latency WebSocket/gRPC, sertifikat SSL kedaluwarsa, atau konfigurasi reverse proxy.
- **Batasan**: Agnostik stack jaringan host Linux/POSIX dan Windows.

## 2. Standard Operating Procedures (SOP)
1. **Auditing Listening Ports & Sockets**:
   - Periksa port aktif dengan utilitas portable (`ss -tulpn` atau `netstat -ano`).
   - Identifikasi PID proses yang menduduki port dan pastikan tidak terjadi benturan port daemon.
2. **Reverse Proxy Configuration (Nginx / Caddy)**:
   - Konfigurasi headers upstream wajib: `Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`.
   - Pastikan header upgrade protokol aktif untuk jalur WebSocket (`Upgrade $http_upgrade`, `Connection "upgrade"`).
3. **TLS & Handshake Inspection**:
   - Validasi masa berlaku dan rantai sertifikat SSL/TLS menggunakan utilitas terminal (`openssl s_client`).
   - Terapkan cipher suite modern (TLS 1.3) dan mitigasi handshake overhead dengan TLS session resumption.
4. **Network Latency & Timeout Hardening**:
   - Set timeout eksplisit untuk connect, read, dan write guna mencegah resource exhaustion akibat connection hanging.

## 3. Strict Prohibitions & Edge Cases
- **Dilarang**: Membiarkan port internal non-otentikasi terekspos ke interface publik (`0.0.0.0`). Bind selalu ke `127.0.0.1` kecuali dirancang untuk public ingress.
- **Dilarang**: Hardcode IP publik statis dalam skrip service.

## 4. Verification & Exit Code 0 Proof
- Jalankan pemeriksaan port dan konektivitas endpoint: `curl -Isf http://127.0.0.1:<port>/health`
- Verifikasi respons HTTP 200 OK (Exit Code 0).
