# Containerization Plan Checklist

## Image

- Base image
- Multi-stage build
- Dependency cache
- Runtime user
- Working directory
- Startup command
- Exposed ports
- Healthcheck

## Runtime

- Environment variables
- Secrets
- Volumes
- Network
- Resource limits
- Logs
- Shutdown behavior

## Security

- No secrets in image
- Non-root user when practical
- Minimal packages
- Pinned base image where appropriate
- Build context excludes unnecessary files
