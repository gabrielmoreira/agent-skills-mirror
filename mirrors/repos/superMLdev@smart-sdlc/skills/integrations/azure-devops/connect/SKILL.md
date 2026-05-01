---
name: azure-devops-connect
description: "Set up and verify Azure DevOps integration. Use when the user says 'connect to Azure DevOps', 'set up ADO', or 'configure Azure DevOps'."
---

# Azure DevOps — Connect and Verify

## Goal

Verify Azure DevOps authentication and store the organisation / project details in config so work item creation, PR creation, and pipeline integrations work seamlessly.

---

## Step 1: Check Azure CLI is Available

```bash
which az && az --version | head -1
```

If not found:
> "Azure CLI (`az`) is not installed. Install it from https://aka.ms/installazurecli"

⏸️ **STOP** — `az` must be installed.

---

## Step 2: Install Azure DevOps Extension

```bash
az extension add --name azure-devops --upgrade
```

---

## Step 3: Authenticate

```bash
az devops configure --defaults organization=https://dev.azure.com/{org}
az devops login
```

Ask for:
1. Organisation name (e.g., `mycompany`)
2. Personal Access Token (PAT) with scope: Work Items (read/write), Code (read/write)

> Security note: do NOT paste the PAT into chat. Run `az devops login` interactively in your terminal.

---

## Step 4: Verify Connection

```bash
az devops project list --top 5 --output table
```

If it returns projects: ✅ Connected.

---

## Step 5: Set Default Project

Ask: "Which Azure DevOps project should be the default?"

```bash
az devops configure --defaults project="{project_name}"
```

---

## Step 6: Save to Config

Update `_superml/config.yml`:

```yaml
integrations:
  azure_devops:
    org: "{org}"
    project: "{project_name}"
    connected: true
    connected_at: "{date}"
```

---

## Done

> ✅ Azure DevOps connected. You can now use `azure-devops-create-work-item` and `azure-devops-create-pr`.
