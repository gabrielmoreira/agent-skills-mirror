# Secrets Handling Review Checklist

## Secret-Like Values

- API keys
- OAuth tokens
- SSH keys
- Cookies
- Session tokens
- Database URLs
- Cloud credentials
- `.env` files
- Private certificates
- Webhook secrets

## Exposure Paths

- Logs
- Screenshots
- Error output
- Generated reports
- Committed examples
- Test fixtures
- Network sends
- Shell history
- Trace exports

## Mitigations

- Redact values.
- Use placeholders.
- Add `.gitignore` coverage.
- Avoid printing environment variables.
- Require approval before reading credential locations.
- Document least-privilege scopes.
- Rotate if exposure is suspected.
