# Relay

Relay is the account service behind the Acme dashboard: users, sessions, and the web client.

## Develop

```bash
npm ci
npx prisma migrate dev
npm run dev
```

The web client runs with `npm run web` and proxies `/api` to port 3000.
