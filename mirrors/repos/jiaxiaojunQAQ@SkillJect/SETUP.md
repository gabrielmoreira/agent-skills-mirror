# Setup Guide

## Overview

This guide covers the complete setup process for the Security Evaluation Framework, including OpenSandbox server installation and Docker image preparation.

## Prerequisites

- Docker installed and running
- Python 3.10+
- (Optional) `uv` for faster package installation

## Step 1: OpenSandbox Server Setup

OpenSandbox is a required dependency for running security tests in isolated sandboxes.

### Option A: Quick Install (Recommended)

```bash
# Install OpenSandbox server
pip install opensandbox-server

# Initialize configuration
opensandbox-server init-config ~/.sandbox.toml --example docker
```

### Option B: Install from Source

```bash
# Clone the repository
git clone https://github.com/alibaba/OpenSandbox.git
cd OpenSandbox/server

# Install dependencies
pip install -e .

# Copy configuration file
cp example.config.toml ~/.sandbox.toml
```

### Start the Server

```bash
# Start OpenSandbox server
opensandbox-server

# Or from source:
cd OpenSandbox/server
python -m src.main
```

**Verify the server is running:**
```bash
curl http://localhost:8080/health
```

## Step 2: Build Docker Image

The framework requires a Docker image with Claude Code CLI installed.

```bash
# Build the image from Dockerfile
docker build -f Dockerfile.claude -t claude_code:latest .

# Verify the image
docker images | grep claude_code
```

## Step 3: Configure Environment

Create or edit `.env` file:

```bash
# API Keys
ANTHROPIC_AUTH_TOKEN=sk-ant-xxx
ZHIPU_API_KEY=xxx.xxx  # For GLM models
OPENAI_API_KEY=sk-xxx  # For GPT models

# OpenSandbox Configuration
SANDBOX_DOMAIN=localhost:8080
SANDBOX_IMAGE=claude_code:latest

# Optional: Model Configuration
ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic
ANTHROPIC_MODEL=glm-4.7
```

## Step 4: Run Evaluation

```bash
# Example: Run with GLM configuration
python run.py -c config/main_glm.yaml

# Example: Run with specific skills
python run.py -c config/main_glm.yaml --skills adaptyv hmdb-database

# Example: Run with verbose output
python run.py -c config/main_glm.yaml --verbose
```

## Troubleshooting

### OpenSandbox Server Issues

**Server won't start:**
- Check if port 8080 is available: `lsof -i :8080`
- Verify Docker is running: `docker ps`
- Check `~/.sandbox.toml` configuration

**Connection refused:**
- Ensure OpenSandbox server is running: `curl http://localhost:8080/health`
- Check `SANDBOX_DOMAIN` in your .env file

### Docker Image Issues

**Build fails:**
- Check Docker daemon is running
- Ensure you have sufficient disk space
- Try building with no-cache: `docker build --no-cache -f Dockerfile.claude -t claude_code:latest .`

### Configuration Issues

**Authentication errors:**
- Verify API keys in `.env` file
- Check `ANTHROPIC_AUTH_TOKEN` is set correctly
- For GLM models, verify `ZHIPU_API_KEY` format

## Additional Resources

- [OpenSandbox Documentation](https://github.com/alibaba/OpenSandbox) - Official OpenSandbox repository and docs
- [README.md](README.md) - Main project documentation
- [RUNBOOK.md](docs/RUNBOOK.md) - Operations manual
