---
name: fail2ban
description: "Installs Linux Fail2Ban with jail.local overrides so sshd, nginx, and mail log matches become nftables, iptables, or UFW bans, managed through fail2ban-client. Trigger when SSH, HTTP basic-auth, WordPress logins, or SMTP/IMAP face brute-force and bot probes. Not a WAF, IDS, or CDN bot-management product. Do not use on Windows hosts or behind a load balancer without real client IPs in logs."
version: 1.0.1
tags:
  - devops
  - cloud
  - automation
  - operations
  - security
tools:
  - gemini
  - codex
---

## Overview
Fail2Ban is an intrusion prevention framework written in Python. It scans system logs (e.g., auth logs, mail server logs, web server logs) for patterns matching malicious activities—such as brute-force authentication attacks, port scanning, and vulnerability probing—and dynamically adjusts firewall rules (using `iptables`, `nftables`, or `UFW`) to ban the offending IP addresses for a specified duration.

## When to Use
- Hardening SSH access endpoints on public cloud instances.
- Protecting web applications (e.g., Nginx HTTP Basic Auth, WordPress login portals) against dictionary brute-force attacks.
- Mitigating bot probing and search engine crawler spam on public web apps.
- Securing SMTP, IMAP, or database ports from automated connection floods.

## Prerequisites
- Linux server (Debian/Ubuntu systems used in examples).
- `sudo` or root access.
- Firewall backend installed (`iptables`, `nftables`, or `UFW`).

## Procedure

1. **Install Fail2Ban**
   ```bash
   sudo apt update
   sudo apt install fail2ban -y
   ```

2. **Enable and start the systemd daemon**
   ```bash
   sudo systemctl enable fail2ban
   sudo systemctl start fail2ban
   ```

3. **Configure Jails**
   Never modify `jail.conf` directly. Always write overriding rules in `/etc/fail2ban/jail.local`.
   ```ini
   # /etc/fail2ban/jail.local - Custom server override rules

   [DEFAULT]
   bantime = 1h       # Duration of the ban (m=minutes, h=hours, d=days)
   findtime = 10m     # Period within which failed retries trigger a ban
   maxretry = 5       # Number of failures allowed within findtime
   banaction = nftables-multiport # Firewall backend choice
   ignoreip = 127.0.0.1/8 192.168.1.0/24 # Trust local subnets

   [sshd]
   enabled = true
   port = ssh
   maxretry = 3       # Stricter retry limits for SSH
   bantime = 24h      # Ban SSH attackers for a full day
   logpath = /var/log/auth.log

   [nginx-http-auth]
   enabled = true
   port = http,https
   filter = nginx-http-auth
   logpath = /var/log/nginx/error.log
   maxretry = 5

   [nginx-limit-req]
   enabled = true
   port = http,https
   filter = nginx-limit-req
   logpath = /var/log/nginx/error.log
   maxretry = 10
   bantime = 2h
   ```

4. **Create Custom Filters (Optional)**
   For custom applications, write a filter pattern file in `/etc/fail2ban/filter.d/my-app.conf`:
   ```ini
   # /etc/fail2ban/filter.d/my-app.conf
   [Definition]
   failregex = ^<HOST> - - \[.*\] "POST /api/login HTTP/.*" 401 .*$
   ignoreregex = 
   ```

5. **Validate Custom Filters**
   Before activating the filter, validate your regular expression against target log lines:
   ```bash
   fail2ban-regex /var/log/nginx/access.log /etc/fail2ban/filter.d/my-app.conf
   ```

6. **Manage Active Bans via Client CLI**
   ```bash
   # Get overall status
   sudo fail2ban-client status

   # Get detailed statistics for a specific jail
   sudo fail2ban-client status sshd

   # Manually ban an offending IP
   sudo fail2ban-client set sshd banip 198.51.100.42

   # Unban a mistakenly blocked IP
   sudo fail2ban-client set sshd unbanip 198.51.100.42
   ```

## Pitfalls
- **Systemd Journal Logs**: Modern Linux installations (like Debian 12 or Ubuntu 24.04) log auth attempts via `systemd-journald` instead of writing raw text files to `/var/log/auth.log`. If Fail2Ban is not monitoring attempts, configure the backend parameter: `backend = systemd` in `jail.local`.
- **Log Rotation Delays**: If log rotation utilities compress logs (e.g., `auth.log.1.gz`) too frequently, Fail2Ban can lose track of the open file descriptors, missing failed attempts during rotation windows.
- **Lockout Risk**: Never configure Fail2Ban without white-listing your local IP ranges or corporate VPN subnets in the `ignoreip` parameter. Doing so runs the risk of locking yourself out of your remote server if you mistype your password a few times.
- **Proxy Load Balancers**: If your application is deployed behind a proxy load balancer (like Cloudflare, AWS ALB, or HAProxy), you must configure your web servers to parse `X-Forwarded-For` headers so Fail2Ban logs the real client IP rather than the proxy's IP. Banning the proxy IP will block access for all users.

## Verification
1. **Verify service runtime status**
   ```bash
   sudo systemctl status fail2ban
   ```
2. **Verify jail status and banned IPs**
   ```bash
   sudo fail2ban-client status
   sudo fail2ban-client status sshd
   ```
3. **Verify custom regex matches**
   ```bash
   fail2ban-regex /var/log/nginx/access.log /etc/fail2ban/filter.d/my-app.conf
   ```

## Related skills
- `ufw` - Uncomplicated Firewall configuration
- `nftables` - Modern Linux firewalling
- `ssh-hardening` - Securing SSH daemon configurations
