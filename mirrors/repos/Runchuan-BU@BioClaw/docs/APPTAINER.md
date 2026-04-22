# Apptainer (HPC) Setup / Apptainer（HPC）部署指南

BioClaw supports **Apptainer** (formerly Singularity) as an alternative container runtime, enabling deployment on HPC clusters where Docker is unavailable and users have no root privileges.

BioClaw 支持 **Apptainer**（前身 Singularity）作为替代容器运行时，适用于没有 Docker 且用户无 root 权限的 HPC 集群。

---

## Quick Start / 快速开始

### 1. Build the SIF image / 构建 SIF 镜像

You need to build the image once on a machine that has either Docker or Apptainer with fakeroot.

需要在有 Docker 或有 fakeroot 权限的机器上构建一次镜像。

**Option A — Convert from Docker image (recommended):**

```bash
# Build Docker image first
cd container && ./build.sh

# Convert to Apptainer SIF
./build-apptainer.sh --from-docker
```

**Option B — Build directly with Apptainer (requires fakeroot):**

```bash
cd container && ./build-apptainer.sh
```

### 2. Transfer to cluster / 传到集群

```bash
scp container/bioclaw-agent.sif your-cluster:~/bioclaw/
```

### 3. Configure and run / 配置并运行

On the cluster:

```bash
cd ~/bioclaw    # your BioClaw directory

# Set runtime in .env
echo 'CONTAINER_RUNTIME=apptainer' >> .env
echo 'CONTAINER_IMAGE=/path/to/bioclaw-agent.sif' >> .env

# Install Node.js dependencies
npm install

# Run
ENABLE_LOCAL_WEB=true npm run dev
```

---

## How It Works / 工作原理

| | Docker | Apptainer |
|---|---|---|
| **Daemon** | Requires `dockerd` running (root) | No daemon, runs as user process |
| **Image format** | OCI layers (`bioclaw-agent:latest`) | Single `.sif` file |
| **Root needed** | Yes (daemon) or rootless mode | No — designed for unprivileged users |
| **Mount syntax** | `-v host:container[:ro]` | `--bind host:container[:ro]` |
| **Container lifecycle** | `docker stop NAME` | Kill the process (SIGTERM) |
| **Orphan cleanup** | `docker ps` + `docker stop` | Not needed (no daemon) |
| **Isolation** | Full namespace isolation | `--containall --no-home --writable-tmpfs` |

BioClaw abstracts these differences in `src/container-runtime.ts`. The rest of the codebase is runtime-agnostic.

BioClaw 在 `src/container-runtime.ts` 中抽象了这些差异，其余代码与运行时无关。

---

## Environment Variables / 环境变量

| Variable | Default | Description |
|----------|---------|-------------|
| `CONTAINER_RUNTIME` | `docker` | `docker` or `apptainer` |
| `CONTAINER_IMAGE` | `bioclaw-agent:latest` | Docker image tag or absolute path to `.sif` file |

---

## Cluster-Specific Notes / 集群注意事项

### Node.js on HPC

Most clusters don't have Node.js pre-installed. Options:

大部分集群没有预装 Node.js，可以：

- **module load**: `module load nodejs` (if available)
- **nvm**: Install [nvm](https://github.com/nvm-sh/nvm) in your home directory (no root needed)
- **conda**: `conda install -c conda-forge nodejs`

### Apptainer version

BioClaw requires **Apptainer ≥ 1.1** (for `--writable-tmpfs` and `--containall` support). Check with:

```bash
apptainer --version
```

Most HPC clusters running CentOS 7+ / Rocky 8+ / Ubuntu 20.04+ have a compatible version.

### Shared filesystem

HPC clusters typically use shared filesystems (NFS, Lustre, GPFS). BioClaw's bind mounts work transparently — your group workspaces and IPC directories are on the shared filesystem automatically.

HPC 集群通常使用共享文件系统。BioClaw 的 bind mount 可以透明地工作。

### SLURM integration

To run BioClaw as a SLURM job:

```bash
#!/bin/bash
#SBATCH --job-name=bioclaw
#SBATCH --output=bioclaw-%j.log
#SBATCH --time=8:00:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=4

module load nodejs  # or use nvm

export CONTAINER_RUNTIME=apptainer
export CONTAINER_IMAGE=$HOME/bioclaw-agent.sif
export ENABLE_LOCAL_WEB=true

cd $HOME/bioclaw
npm run dev
```

Then access the web UI via SSH tunnel:

```bash
ssh -L 3000:localhost:3000 your-cluster
# Open http://localhost:3000 in your browser
```

---

## Troubleshooting / 排障

### "Apptainer is required but not found"

Apptainer is not installed or not in PATH. Try:

```bash
module load apptainer    # or singularity
which apptainer
```

Some clusters still use the `singularity` command. Create an alias:

```bash
alias apptainer=singularity
```

### "FATAL: container creation failed: mount ..."

Bind mount path doesn't exist on the host. Ensure all group directories are created before running:

```bash
npm run build   # creates necessary directories during first build
```

### Permission denied in container

Apptainer maps your host UID into the container. If files in the SIF are owned by root but writable paths are needed, `--writable-tmpfs` (already set by BioClaw) creates a temporary overlay.

### Slow first run

The first `apptainer exec` on a new `.sif` file may be slow as the cluster caches the image. Subsequent runs are fast.
