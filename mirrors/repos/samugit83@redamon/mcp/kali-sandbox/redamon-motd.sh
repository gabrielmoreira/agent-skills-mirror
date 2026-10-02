# Printed after the standard Kali MOTD on every login shell, so users see the
# redagraph hint without cluttering the webapp banner.
printf '\n'
printf '\033[1;33m  \xe2\x9a\xa1 redagraph\033[0m \033[2;37m\xe2\x80\x94 tenant-scoped graph CLI\033[0m\n'
printf '  \033[2;37mExample:\033[0m \033[1;32mredagraph ask list CVEs with cve_id severity cvss > cves.txt\033[0m\n'
printf '  \033[2;37mFor more info:\033[0m \033[1;32mredagraph -h\033[0m\n'
printf '\n'
