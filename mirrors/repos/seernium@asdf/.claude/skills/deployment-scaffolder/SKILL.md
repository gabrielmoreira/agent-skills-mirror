# Skill: Multi-Stage Deployment Configuration

Generates optimized multi-stage Dockerfiles, Docker Compose files, and cloud infrastructure manifests.

## Steps
1. Build multi-stage Docker configurations minimizing production image sizes
2. Define local Compose environments with service links and health checks
3. Structure infrastructure-as-code cloud task manifests (e.g., AWS ECS)

## Templates
- See `Dockerfile.template` — Multi-stage Node.js production build
- See `docker-compose.template.yml` — Web app + PostgreSQL stack
- See `ecs-task-definition.template.json` — AWS FARGATE task definition