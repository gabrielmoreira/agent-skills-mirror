# Relay

Relay is the account service behind the Acme dashboard: users, sessions, notifications, and the
web client.

## Develop

```bash
npm ci
npx prisma migrate dev
npm run dev
```

The web client runs with `npm run web` and proxies `/api` to port 3000.

## Notifications

Notifications need Redis and a worker next to the API:

```bash
docker run -d -p 6379:6379 redis:7-alpine
npm run worker
```

Set `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, and `UNSUBSCRIBE_SECRET` in `.env`; email goes out
through SES with the usual AWS credentials. See [docs/notifications.mdx](docs/notifications.mdx)
for how delivery works and [docs/notifications-runbook.mdx](docs/notifications-runbook.mdx) when
it doesn't.
