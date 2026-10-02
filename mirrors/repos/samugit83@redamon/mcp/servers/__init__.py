"""
RedAmon MCP Servers

MCP (Model Context Protocol) servers for agentic penetration testing.
These servers expose security tools to AI agents via the MCP protocol.

Servers:
    - network_recon_server: HTTP client (curl) & port scanning (naabu)
    - nuclei_server: Vulnerability scanning (dynamic CLI)
    - nmap_server: Network mapper (service detection, OS fingerprint, NSE scripts)
    - metasploit_server: Exploitation framework (structured tools)
"""

__version__ = "0.1.0"
