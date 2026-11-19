# Docker deployment

Run OpenMotion in a container on the machine you work on. The image is built
from this checkout and contains Node.js, Chromium, FFmpeg/ffprobe and CJK fonts,
so the host needs only Docker.

This is a local deployment: the Studio is opened from the same machine at
`http://127.0.0.1:4173`. Access from another machine is not supported yet.

## Start

```bash
cd deploy
cp .env.example .env
docker compose build
docker compose up -d
```

Open `http://127.0.0.1:4173`.

Projects, exports and settings are stored in the `openmotion_data` volume,
mounted at `/data` (`MOTION_DATA_DIR`). `docker compose down` keeps the volume;
`docker compose down -v` deletes it together with every project in it.

## Connect an Agent

Install the primary OpenMotion Skill in your host Agent using the standard
[Quick Start](../README.md#quick-start) command:

```sh
npx skills add nexu-io/openmotion --skill openmotion
```

This installs Agent guidance. Reuse the running container for the application;
do not install a second runtime on the host. Complete the Skill's onboarding in
the current Agent after its actual MCP connection is verified.

The MCP server is a stdio process. Start it inside the running container so it
shares the Studio's data directory and service:

The Studio's **MCP · Connect Agent** page detects this Compose deployment.
Its copied commands and downloaded configurations run `docker exec` from the
host, preserving the container's workspace and runtime. Use those instructions
for Codex, Claude Code, DeepSeek Harness or another stdio client; do not run
container paths such as `/app/mcp.ts` directly on the host. The Agent setup
instruction and Connection guide also retain this Docker installation.

```json
{
  "mcpServers": {
    "openmotion": {
      "command": "docker",
      "args": ["exec", "-i", "openmotion", "node", "--experimental-strip-types", "mcp.ts"]
    }
  }
}
```

Paths passed to MCP tools are container paths. To import local media with
`openmotion_import_assets`, mount the folder into the container and pass the
mounted path.

Compose sets `MOTION_CONTAINER_NAME=openmotion` to match `container_name`.
If you rename the container, update both values so the generated host commands
enter the right container. When running the image without Compose, set
`MOTION_CONTAINER_NAME` to the actual container name to enable these commands.

## Settings

| Variable | Default | Purpose |
| --- | --- | --- |
| `OPENMOTION_PORT` | `4173` | Port on the host's `127.0.0.1` and inside the container. Both sides use the same value so returned URLs open on the host. |
| `OPENMOTION_MEM_LIMIT` | `4g` | Container memory limit. Rendering runs Chromium and FFmpeg. |
| `DO_NOT_TRACK` | empty | Set to `1` to disable analytics. |

## How access is restricted

The container sets `MOTION_BIND_HOST=0.0.0.0` so Docker can publish the port,
and Compose publishes it on the host's `127.0.0.1` only. That loopback
publication is what keeps other machines out. Keep it: do not change the
`ports` entry to another interface or to `0.0.0.0`.

The server also rejects requests whose `Host` header is not `localhost`,
`127.0.0.1` or `[::1]`, and writes that do not come from its own origin. These
checks protect a browser on this machine from other websites. They are not
authentication: a client that is not a browser can send any `Host` and `Origin`,
and the Studio has no sign-in.

`MOTION_BIND_HOST` accepts `127.0.0.1` (default), `0.0.0.0` and `::`. A specific
interface address is rejected, because the readiness probe and the URLs returned
to Agents use `127.0.0.1`.

## Known limits

- The web browser tab inside the Studio starts Chromium with its sandbox, which
  is not available to an unprivileged container. Video preview and export are
  not affected.
- Linux is not a pinned native runtime target; the image uses Debian's Chromium
  and FFmpeg instead of the versions in `scripts/runtime-lock.json`.
