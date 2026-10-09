---
name: linux_sysadmin_hardener
description: Sovereign runbook for Linux system administration, Systemd unit daemonization, journalctl diagnostics, permission auditing, and firewall hardening
keywords: ["linux sysadmin", "systemd service", "daemon management", "system hardening", "journalctl triage", "ufw firewall", "nftables security", "file permissions", "chown chmod", "selinux apparmor", "ssh hardening", "sudoers policy", "system performance tuning", "kernel parameter", "sysctl tuning", "disk partition lvm", "process signal", "cron systemd timer", "logrotate audit", "zero trust host"]
---

# ⚙️ SKILL: LINUX SYSADMIN HARDENER

## 1. Intent & Trigger Boundaries
- **Intent**: Administrasi sistem operasi Linux, pembuatan dan pengelolaan service daemon `systemd`, triage diagnostik log via `journalctl`, penegakan permission filesystem, hardening firewall (UFW/nftables), dan keamanan SSH host.
- **Trigger**: Diminta membuat systemd unit file, membuat service auto-start saat boot, audit keamanan host Linux, konfigurasi firewall, perbaikan permission file rusak, atau analisis kernel sysctl.
- **Boundaries**: Tidak mengurusi container orchestration Kubernetes (gunakan `k8s_cluster_commander`). Fokus pada level host OS kernel, daemons, dan sistem operasi Linux murni.

## 2. Standard Operating Procedures (SOP)
1. **Systemd Service Scaffolding & Hardening**:
   - Buat unit service di `/etc/systemd/system/<nama>.service` atau direktori user `~/.config/systemd/user/`.
   - Sertakan direktif keamanan systemd: `NoNewPrivileges=true`, `ProtectSystem=strict`, `ProtectHome=read-only`, `PrivateTmp=true`.
   - Tetapkan `Restart=always` atau `Restart=on-failure` disertai `RestartSec=5s` dan `LimitNOFILE=65535`.
2. **Log Triage & Incident Debugging**:
   - Gunakan `journalctl -u <service> -n 100 --no-pager` untuk mengecek log terkini tanpa pagination terminal gantung.
   - Analisis kegagalan unit via `systemctl status <service>` dan `systemctl --failed`.
3. **Security, Firewall & Access Hardening**:
   - Konfigurasi UFW/nftables dengan policy default deny incoming, allow outgoing, dan hanya buka port esensial (misal 22, 80, 443).
   - Hardening konfigurasi SSH (`/etc/ssh/sshd_config`): nonaktifkan `PermitRootLogin no`, `PasswordAuthentication no`, gunakan key-only ED25519.
4. **Filesystem Permission & Least Privilege**:
   - Pastikan kepemilikan file tepat sasaran (`chown user:group`) tanpa wildcard ceroboh.
   - Dilarang keras menggunakan `chmod 777`; gunakan least privilege (`640` untuk konfigurasi, `750` untuk binary executable).

## 3. Strict Prohibitions & Edge Cases
- **PROHIBITION**: Dilarang menggunakan `chmod -R 777` di direktori manapun di host OS.
- **PROHIBITION**: Dilarang me-reload service produksi tanpa validasi syntax konfigurasi terlebih dahulu.
- **EDGE CASE**: Service gagal restart karena bind address already in use: telusuri socket pemegang via `ss -tulpn | grep :<port>` dan lakukan graceful termination.

## 4. Verification & Exit Code 0 Proof
- Validasi Unit File: `systemd-analyze verify /etc/systemd/system/<service>.service` menghasilkan exit code 0.
- Service Runtime: `systemctl is-active <service>` mengembalikan string `active` dengan exit code 0.
- Firewall Verification: `ufw status verbose` mengembalikan status `Status: active` dengan aturan terdaftar.
