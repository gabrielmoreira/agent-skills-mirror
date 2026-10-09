---
name: network_packet_analyst
description: Sovereign runbook for low-level network packet analysis, tcpdump captures, socket inspection, DNS resolution triage, and TLS handshake auditing
keywords: ["network packet analysis", "tcpdump capture", "socket inspection", "dns troubleshooting", "tls handshake audit", "pcap analysis", "wireshark trace", "packet loss diagnostic", "latency triage", "mtu path discovery", "curl network debug", "dig dns lookup", "netstat ss socket", "tcp retransmission", "http response timing", "iperf bandwidth", "firewall packet drop", "arp resolution", "ssl certificate chain", "network benchmark"]
---

# ⚙️ SKILL: NETWORK PACKET ANALYST

## 1. Intent & Trigger Boundaries
- **Intent**: Investigasi jaringan tingkat rendah, analisis traffic TCP/UDP, penangkapan paket data (PCAP/tcpdump), diagnostik DNS resolution, inspeksi socket OS, dan audit jabat tangan TLS/SSL.
- **Trigger**: Diminta menganalisis packet loss, timeout koneksi HTTP/TCP, sertifikat SSL invalid, lookup DNS lambat/gagal, kebocoran port, atau bottleneck throughput bandwidth.
- **Boundaries**: Tidak mengurusi arsitektur logika aplikasi web internal (gunakan `api_gateway_integrator`). Fokus pada lapisan jaringan L3/L4 (IP, ICMP, TCP, UDP) hingga handshake L7 (TLS/DNS/HTTP latency).

## 2. Standard Operating Procedures (SOP)
1. **Socket & Port Inspection**:
   - Periksa port terbuka dan socket aktif tanpa lag DNS: `ss -tulpn` atau `netstat -tlpn`.
   - Pastikan local interface (`127.0.0.1`) vs universal interface (`0.0.0.0`) sesuai dengan kebutuhan arsitektur.
2. **DNS & Resolution Tracing**:
   - Gunakan `dig +trace +nocmd +noall +answer <domain>` untuk menelusuri delegasi nameserver dari root hingga authoritative.
   - Periksa respons cache lokal di `/etc/resolv.conf` dan `systemd-resolved` status jika DNS resolving inkonsisten.
3. **Low-Level Packet Capture & Analysis**:
   - Ambil paket spesifik dengan filter presisi: `tcpdump -nn -i <interface> port <port> -c 100 -w capture.pcap`.
   - Telusuri TCP 3-Way Handshake (SYN, SYN-ACK, ACK), TCP RST (connection reset), dan TCP Retransmissions untuk mendeteksi saturasi jaringan.
4. **TLS Handshake & Latency Breakdown**:
   - Audit rantai sertifikat dan negosiasi cipher: `openssl s_client -connect <host>:<port> -servername <host> -tlsextdebug`.
   - Ukur komponen latency detail dengan cURL: `curl -w "@curl-format.txt" -o /dev/null -s <url>` untuk membedah time_namelookup, time_connect, time_appconnect, time_starttransfer, dan time_total.

## 3. Strict Prohibitions & Edge Cases
- **PROHIBITION**: Dilarang menjalankan `tcpdump` tanpa filter port/host atau tanpa batas kuantitas paket (`-c`) di production link ber-traffic tinggi (risiko disk full & CPU spike).
- **PROHIBITION**: Dilarang menyimpan capture PCAP yang memuat data payload plaintext sensitif (passwords, auth bearer headers).
- **EDGE CASE**: Koneksi macet karena MTU mismatch / black hole ICMP: uji MTU via `ping -M do -s <size> <host>` untuk menentukan MTU optimal tanpa fragmentasi.

## 4. Verification & Exit Code 0 Proof
- DNS Resolution Success: `dig +short <domain>` mengembalikan record IP valid dengan status `NOERROR` dan exit code 0.
- Socket Connectivity: `nc -zv <host> <port>` atau `curl -I -s -f <endpoint>` menghasilkan exit code 0.
- PCAP Integrity: File capture pcap valid dan dapat dibaca via `tcpdump -r capture.pcap -c 1` dengan exit code 0.
