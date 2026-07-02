# Troubleshooting

Use this path when OpenTag setup, startup, platform delivery, execution, or callbacks do not work.

## Start With The CLI

Use these first:

```bash
opentag status
opentag doctor
opentag config path
opentag config show
```

`opentag config show` redacts secrets. Do not ask the user to paste raw tokens unless a specific credential must be re-entered.

## Split The Failure

Check one layer at a time. Stop at the first failing layer and explain the concrete fix.

1. CLI config exists and parses.
2. The selected platform is configured.
3. `opentag start` is still running.
4. The local dispatcher is healthy.
5. The platform listener is connected or reachable.
6. The platform can deliver the mention or webhook.
7. The runner is bound to the selected project.
8. The selected executor is available.
9. Callback credentials can post the reply.

## Common Platform Checks

Slack:

- Socket Mode needs `xapp-` App-Level Token and `xoxb-` Bot User OAuth Token.
- The Slack app must be invited to the target channel.
- The app needs `app_mentions:read`, `chat:write`, and channel history permissions for the channel type.

GitHub:

- A tunnel must forward to the local GitHub listener port.
- The webhook URL must end with `/github/webhooks`.
- The webhook secret must match the OpenTag config.
- The token needs write access to issues and pull requests.
- `apply 1` PR creation also needs a pushed run branch and working local git remote credentials.

Lark / Feishu:

- The Personal Agent QR scan must complete before setup can save the app credentials.
- Saved Personal Agent details should show safe App ID and Bot Open ID prefixes.
- The selected domain must match the tenant: Lark for larksuite.com, Feishu for feishu.cn.

## Common Errors

- `unauthorized`: pairing token mismatch or missing bearer token.
- `repo_not_bound`: the project target is not bound to the local runner.
- `channel_binding_not_found`: the platform conversation is not mapped to a project.
- `actor_not_allowed_for_write`: the actor is not allowed to request write-capable work.
- `No OpenTag run available`: no pending run is claimable by this runner.

## Callback Debugging

Execution success and callback delivery are separate.

- Slack callbacks need the Slack bot token.
- GitHub callbacks need the GitHub token.
- Lark / Feishu callbacks need saved app credentials.

If the executor completed but the platform did not receive a reply, focus on callback credentials, platform permissions, and listener logs rather than executor behavior.
