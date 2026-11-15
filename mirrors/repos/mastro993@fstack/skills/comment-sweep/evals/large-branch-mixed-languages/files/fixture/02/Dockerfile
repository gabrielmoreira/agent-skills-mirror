FROM node:22-alpine AS build
WORKDIR /app
# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npx prisma generate && npm run build

FROM node:22-alpine AS api
WORKDIR /app
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY web/public ./web/public
COPY emails ./emails
CMD ["node", "dist/server.js"]

FROM node:22-alpine AS worker
WORKDIR /app
# Copy the worker files
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY emails ./emails
COPY templates ./templates
COPY vendor ./vendor
ENV NODE_ENV=production
CMD ["node", "dist/notifications/worker.js"]
