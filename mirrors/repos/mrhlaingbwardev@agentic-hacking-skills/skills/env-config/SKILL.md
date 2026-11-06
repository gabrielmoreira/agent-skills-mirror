---
name: env-config
description: Use when user says "env", ".env", "secret", "api key config", "config file", "credentials", "gitignore secret", "လျှို့ဝှက်", "config ထည့်", "secret သိမ်း". Manages environment/secret configuration for tools and scripts safely — .env files, loading, gitignore, and never hardcoding keys.
---

# Env & Secret Config

## TRIGGER
Activate when building/fixing a tool that needs API keys, tokens, passwords, or any secret — or when user mentions `.env`, config, credentials, gitignore secrets.

## RULES

1. **Never hardcode secrets in source**
   - Read from env vars or `.env`, not inline strings.
   - Bad: `TOKEN = "ghp_xxxx"`
   - Good: `TOKEN = os.getenv("TOKEN")`

2. **Use `.env` for local, never commit it**
   - `.env` holds `KEY=value` lines (no quotes needed).
   - Always add `.env` to `.gitignore`.
   - Provide `.env.example` with dummy/empty values for sharing.

3. **Load pattern per language**
   - Python: `python-dotenv`
     ```python
     from dotenv import load_dotenv
     import os
     load_dotenv()
     TOKEN = os.getenv("TOKEN")
     ```
   - Node: `dotenv`
     ```js
     require("dotenv").config();
     const TOKEN = process.env.TOKEN;
     ```
   - Go: `godotenv` or read os env directly.
   - PowerShell: `$env:TOKEN = (Get-Content .env | ...)` or `$env:TOKEN`.

4. **`.env.example` template**
   ```
   # Copy to .env and fill in
   API_KEY=
   TOKEN=
   PROXY_URL=
   ```

5. **Fail safe**
   - If a required var is missing, print clear error + exit:
     `print("[!] API_KEY not set — copy .env.example to .env"); sys.exit(1)`
   - Never continue with empty secret (silent failures waste time).

6. **OPSEC**
   - Rotate user-agents / proxies via env, not code.
   - Keep real location hidden: read VPN/cover settings from env.
   - Never echo secrets to logs or console.

## WORKFLOW
1. Create `.env.example` with all needed keys (blank).
2. Load vars at tool start; validate presence.
3. Add `.env` to `.gitignore`.
4. Tell user: `cp .env.example .env` then fill values.
