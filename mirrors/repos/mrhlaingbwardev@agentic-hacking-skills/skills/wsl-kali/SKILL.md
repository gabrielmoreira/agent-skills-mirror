---
name: wsl-kali
description: Use when running security tools that require Kali Linux. Routes all bash commands through WSL Kali environment (wsl -d kali-linux).
---

# WSL Kali Linux Skill

**Use this skill for ALL commands and operations. Always execute in WSL Kali Linux environment.**

## Core Rule

**CRITICAL:** All bash commands, file operations, and tool executions MUST run in WSL Kali Linux, NOT Windows CMD or PowerShell.

## Command Execution Pattern

### Always use this format:
```bash
wsl -d kali-linux -- bash -c 'YOUR_COMMAND_HERE'
```

### Examples:

```bash
# Check system info
wsl -d kali-linux -- bash -c 'uname -a'

# Navigate and list files
wsl -d kali-linux -- bash -c 'cd /home/youruser && ls -la'

# Install packages
wsl -d kali-linux -- bash -c 'sudo apt update && sudo apt install -y PACKAGE_NAME'

# Run Go commands
wsl -d kali-linux -- bash -c 'export PATH="$HOME/go/bin:$PATH" && go version'

# Execute security tools
wsl -d kali-linux -- bash -c 'export PATH="$HOME/go/bin:$PATH" && subfinder -version'

# Python commands
wsl -d kali-linux -- bash -c 'python3 --version'
wsl -d kali-linux -- bash -c 'pip3 install --break-system-packages PACKAGE_NAME'
```

## Path Conversions

### Windows â†’ WSL Path
- `C:\Users\YourUser\Desktop` â†’ `/mnt/c/Users/YourUser/Desktop`
- `C:\Users\YourUser\Documents` â†’ `/mnt/c/Users/YourUser/Documents`
- `D:\Projects` â†’ `/mnt/d/Projects`

### WSL â†’ Windows Path
- `/home/youruser` â†’ `\\wsl$\kali-linux\home\youruser`
- `/etc` â†’ `\\wsl$\kali-linux\etc`

## Environment Setup

### Always export PATH for Go tools:
```bash
wsl -d kali-linux -- bash -c 'export PATH="$HOME/go/bin:$PATH" && YOUR_COMMAND'
```

### Check installed tools:
```bash
wsl -d kali-linux -- bash -c 'export PATH="$HOME/go/bin:$PATH" && which subfinder httpx katana gf'
```

## Common Operations

### File Operations
```bash
# Read file
wsl -d kali-linux -- bash -c 'cat /path/to/file'

# Create file
wsl -d kali-linux -- bash -c 'echo "content" > /path/to/file'

# Edit file
wsl -d kali-linux -- bash -c 'nano /path/to/file'

# Make executable
wsl -d kali-linux -- bash -c 'chmod +x /path/to/script.sh'
```

### Package Management
```bash
# Update system
wsl -d kali-linux -- bash -c 'sudo apt update && sudo apt upgrade -y'

# Install packages
wsl -d kali-linux -- bash -c 'sudo apt install -y package1 package2'

# Python packages
wsl -d kali-linux -- bash -c 'pip3 install --break-system-packages package-name'
```

### Security Tools Workflow
```bash
# Install Go tool
wsl -d kali-linux -- bash -c 'go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest'

# Run recon tool
wsl -d kali-linux -- bash -c 'export PATH="$HOME/go/bin:$PATH" && subfinder -d example.com'

# Chain commands
wsl -d kali-linux -- bash -c 'export PATH="$HOME/go/bin:$PATH" && subfinder -d example.com | httpx -silent'
```

## Project Directory

### Default working directory:
```bash
# Home directory
/home/youruser

# Projects (Windows Desktop via WSL)
/mnt/c/Users/YourUser/Desktop

# Kali native directory
/home/youruser/projects
```

## Verification Commands

### Before executing any task, verify environment:
```bash
# Check you're in WSL Kali
wsl -d kali-linux -- bash -c 'cat /etc/os-release | grep "Kali Linux"'

# Check user
wsl -d kali-linux -- bash -c 'whoami'

# Check Go tools
wsl -d kali-linux -- bash -c 'export PATH="$HOME/go/bin:$PATH" && ls -la ~/go/bin/'
```

## Error Handling

### If command fails:
1. Check if in WSL: `wsl -d kali-linux -- bash -c 'uname -a'`
2. Check PATH: `wsl -d kali-linux -- bash -c 'echo $PATH'`
3. Check tool exists: `wsl -d kali-linux -- bash -c 'which tool-name'`
4. Install if missing: `wsl -d kali-linux -- bash -c 'sudo apt install tool-name'`

## Special Cases

### Interactive Commands
For commands requiring user input:
```bash
wsl -d kali-linux
# Then run interactive command in the spawned shell
```

### Long-running Commands
```bash
# With timeout
wsl -d kali-linux -- bash -c 'timeout 300 your-command'

# Run in background
wsl -d kali-linux -- bash -c 'nohup your-command &'
```

### Multi-line Scripts
```bash
wsl -d kali-linux -- bash -c '
export PATH="$HOME/go/bin:$PATH"
cd /home/youruser
command1
command2
command3
'
```

## Reminder

**NEVER use Windows CMD/PowerShell commands like:**
- âŒ `Get-ChildItem`
- âŒ `Test-Path`
- âŒ PowerShell cmdlets

**ALWAYS use Linux commands via WSL:**
- âœ… `wsl -d kali-linux -- bash -c 'ls -la'`
- âœ… `wsl -d kali-linux -- bash -c 'test -f /path/to/file'`
- âœ… Standard Unix/Linux commands

## When to Use This Skill

Use this skill for:
- Installing packages
- Running security tools (subfinder, httpx, katana, etc.)
- Python/pip operations
- Go tool installations
- File operations
- System administration
- Any command-line operation

**Exception:** Only use Windows commands for OpenCode config file editing in `C:\Users\YourUser\.config\opencode\`
