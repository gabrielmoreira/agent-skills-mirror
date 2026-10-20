# How to bring up your first production deploy

Use this when `/setup-deploy` stops with "Nothing is deployed yet". It walks through a first production deploy, so you finish with a live URL that `/setup-deploy` can record and `/land-and-deploy` can verify. It names no hosting provider or deploy tool; use whichever fits your project.

`/setup-deploy` writes nothing at that stop. It configures how `/land-and-deploy` checks a deploy, so it needs a production deploy that already exists.

## Prerequisites

- The app builds and starts locally with the commands production will run.
- The code is in its GitHub repository. `/setup-deploy` and `/land-and-deploy` read it through the GitHub CLI, so `gh auth status` should pass.
- An account with the hosting provider you choose, with billing set up if it needs it.
- Optional: a domain you control, if users won't use the host's default address.

## Steps

### 1. Choose where the app runs

Pick a host for the kind of app you have: static files, a long-running server or container, or functions. List what the app needs at runtime: the language runtime and its version, a database or other services, background jobs, and any disk that has to survive a restart.

Then choose how production deploys start. `/land-and-deploy` only watches a trigger that already exists; it never creates one. When `/setup-deploy` asks how deploys are triggered, the choices are:

- automatically on push to the default branch
- a CI workflow in the repository
- a deploy script or CLI command
- manually

A trigger that runs on merge to the default branch keeps `/land-and-deploy` hands-off. With a command trigger, nothing deploys until the command runs: `/land-and-deploy` asks you to run it after the merge, or runs it only with your explicit approval.

### 2. Create the services the app depends on

Create production instances of every service the app uses, such as its database, cache, file storage, email or payments, separate from your development ones. Run the database schema setup or migrations against production before the app serves traffic.

### 3. Set environment variables and secrets

1. List every variable the app reads, at build time and at runtime.
2. Set each one in the host's environment or secrets settings.
3. Keep secret values out of the repository. Commit only an example file with placeholder values, such as `.env.example`.
4. Enter secret values yourself. Don't paste them into a chat with your agent.

Some hosts inject variables only at runtime. A value the build needs, such as a public client-side key, has to be available when the build runs.

### 4. Run the first deploy

Start a deploy with the trigger you chose: push to the default branch, run the workflow, or run the command. Watch the build and release logs until they finish, and note the address the host assigns. If the build fails, fix it and deploy again before you go on.

### 5. Point your domain at it (optional)

1. At your DNS provider, add the records the host asks for: usually a CNAME record for a subdomain, or A and AAAA records for the root domain.
2. Wait until the name resolves:

   ```bash
   dig +short app.example.com
   ```

3. Check that HTTPS works for the domain with a valid certificate:

   ```bash
   curl -sI https://app.example.com | head -1
   ```

Decide which address is the production URL, your domain or the host's default address. That is the URL you give `/setup-deploy`.

### 6. Check that it works

1. Open the production URL in a browser and walk through one real flow, such as signing in or loading data.
2. If the app has a health endpoint, check that it returns a 2xx status:

   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" https://app.example.com/health
   ```

   A useful health endpoint exercises the app, for example by reaching its database, instead of returning a fixed page.
3. Make sure you can tell which revision is live: a status command that prints the deployed commit, or a page or endpoint that shows it. `/land-and-deploy` treats a page that loads as site health, not as proof that the merged commit is live.
4. Check the host's logs for errors after your first requests.

### 7. Hand the deploy back to gstack

Run `/setup-deploy` again. If the project now has a config file for a platform it recognizes, it starts from that platform's settings; otherwise it asks. Either way, have these answers ready:

- how deploys are triggered (step 1)
- the production URL (step 5)
- how to check that a deploy succeeded: a health check URL, a status command, the CI workflow's status, or just checking that the URL loads
- the merge method your repository allows (squash, merge or rebase), and any command to run before merging

It writes the answers to the `## Deploy Configuration` section of the project's CLAUDE.md, then tries the health check and the status command once. From then on, `/land-and-deploy` uses that section to merge your PR, watch the deploy and check production. Its first run walks you through a dry run of the pipeline before anything irreversible happens.

## Verification

- `/setup-deploy` ends with `DEPLOY CONFIGURATION — COMPLETE`.
- The project's CLAUDE.md has the section, with your production URL:

  ```bash
  grep -A 20 "## Deploy Configuration" CLAUDE.md
  ```

- Its health check did not print `UNREACHABLE`, and its status command did not print `COMMAND_FAILED`.

## Troubleshooting

**`/setup-deploy` stops at "Nothing is deployed yet" again.**
That answer means there is no production deploy to record. Once the app is live, pick the answer that says how it deploys: on push, through a CI workflow, with a script or command, or by hand.

**The health check fails or prints `UNREACHABLE`.**
Open the URL yourself. A 404 means the health path doesn't exist, so give `/setup-deploy` a path that returns 2xx, or the plain production URL. `/setup-deploy` keeps the configuration even when this check fails, so you can fix the URL later by running it again or by editing the section in CLAUDE.md.

**The app works on the host's address but not on your domain.**
Check the DNS records (`dig +short <domain>`) and the certificate (`curl -sI https://<domain>`). New records can take a while to resolve everywhere.

**The build works locally but fails on the host.**
Compare the host's build environment with yours. A missing build-time variable or a different runtime version is the usual cause.

**You deploy by running a command by hand.**
Record it as the deploy trigger. After each merge, `/land-and-deploy` tells you production hasn't moved yet and asks you to run it.

## Related

- [`/setup-deploy`](./skills.md#setup-deploy) and [`/land-and-deploy`](./skills.md#land-and-deploy): what each skill does
- [`/canary`](./skills.md#canary): post-deploy monitoring once production is live
- Reference: [`setup-deploy/SKILL.md`](../setup-deploy/SKILL.md), [`land-and-deploy/SKILL.md`](../land-and-deploy/SKILL.md)
