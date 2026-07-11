# Authorization Code + PKCE Flow Template

OAuth 2.0 Authorization Code flow with Proof Key for Code Exchange (PKCE) for public clients.

## When to Use
- Single Page Applications (SPAs)
- Mobile native applications
- Desktop applications
- Any client that cannot securely store a client_secret

## Mermaid Template

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {
  'actorBkg': '#ddd6fe',
  'actorTextColor': '#1f2937',
  'actorBorder': '#6d28d9',
  'signalColor': '#334155',
  'signalTextColor': '#1f2937',
  'noteBkgColor': '#f8fafc',
  'noteTextColor': '#1f2937',
  'noteBorderColor': '#334155'
}}}%%
sequenceDiagram
    autonumber

    box rgba(165,243,252,0.3) USER DEVICE
        participant U as 👤 User
        participant App as 📱 Mobile App<br/>or SPA
    end

    box rgba(167,243,208,0.3) SALESFORCE
        participant SF as ☁️ Salesforce<br/>Authorization Server
    end

    Note over U,SF: Authorization Code + PKCE Flow (RFC 7636)

    U->>App: 1. Tap "Login with Salesforce"

    App->>App: 2. Generate PKCE Parameters
    Note over App: code_verifier = random(128 bytes)<br/>code_challenge = BASE64URL(SHA256(code_verifier))

    App->>App: 3. Generate state (CSRF protection)

    App->>SF: 4. Open browser/webview to /authorize
    Note over App,SF: response_type=code<br/>client_id=CONSUMER_KEY<br/>redirect_uri=CALLBACK_URL<br/>scope=api refresh_token<br/>state=RANDOM_STATE<br/>code_challenge=CODE_CHALLENGE<br/>code_challenge_method=S256

    SF->>U: 5. Display Login Page
    U->>SF: 6. Enter Username & Password

    SF->>SF: 7. Authenticate User

    SF->>U: 8. Display Consent Screen
    Note over SF,U: "App requests access to:<br/>• API Access<br/>• Refresh Token"

    U->>SF: 9. Grant Consent (Allow)

    SF->>SF: 10. Generate Authorization Code
    Note over SF: Store code_challenge with code

    SF->>App: 11. Redirect to callback with code
    Note over SF,App: scheme://callback?code=AUTH_CODE<br/>&state=RANDOM_STATE

    App->>App: 12. Verify state matches

    App->>SF: 13. POST /services/oauth2/token
    Note over App,SF: grant_type=authorization_code<br/>code=AUTH_CODE<br/>client_id=CONSUMER_KEY<br/>redirect_uri=CALLBACK_URL<br/>code_verifier=CODE_VERIFIER

    SF->>SF: 14. Validate Code & PKCE
    Note over SF: Verify: BASE64URL(SHA256(code_verifier))<br/>== stored code_challenge

    SF->>App: 15. Return Tokens
    Note over SF,App: {<br/>  access_token: "...",<br/>  refresh_token: "...",<br/>  instance_url: "https://...",<br/>  token_type: "Bearer"<br/>}

    App->>App: 16. Store tokens securely
    Note over App: Use Keychain (iOS)<br/>or Keystore (Android)

    App->>U: 17. ✅ Successfully Logged In
```

## ASCII Fallback Template

```text
┌──────────┐     ┌───────────────┐     ┌────────────────────┐
│  User    │     │  Mobile App   │     │     Salesforce     │
│          │     │   or SPA      │     │   (Auth Server)    │
└────┬─────┘     └───────┬───────┘     └─────────┬──────────┘
     │                   │                       │
     │  1. Tap Login     │                       │
     │──────────────────>│                       │
     │                   │                       │
     │                   │  2. Generate PKCE:    │
     │                   │     code_verifier     │
     │                   │     code_challenge    │
     │                   │                       │
     │  3. Open Browser/WebView to /authorize    │
     │<──────────────────│                       │
     │                   │                       │
     │  4. GET /authorize                        │
     │      (client_id, code_challenge, state)   │
     │───────────────────────────────────────────────────────>│
     │                   │                       │
     │           5. Login Page                   │
     │<───────────────────────────────────────────────────────│
     │                   │                       │
     │  6. Enter Credentials                     │
     │───────────────────────────────────────────────────────>│
     │                   │                       │
     │           7. Consent Screen               │
     │<───────────────────────────────────────────────────────│
     │                   │                       │
     │  8. Grant Consent                         │
     │───────────────────────────────────────────────────────>│
     │                   │                       │
     │  9. Redirect with ?code=ABC123            │
     │<───────────────────────────────────────────────────────│
     │                   │                       │
     │ 10. Deliver Code  │                       │
     │──────────────────>│                       │
     │                   │                       │
     │                   │ 11. POST /token       │
     │                   │     (code_verifier)   │
     │                   │──────────────────────>│
     │                   │                       │
     │                   │ 12. Verify PKCE:      │
     │                   │     SHA256(verifier)  │
     │                   │     == challenge      │
     │                   │                       │
     │                   │ 13. Access Token +    │
     │                   │     Refresh Token     │
     │                   │<──────────────────────│
     │                   │                       │
     │ 14. Logged In ✅  │                       │
     │<──────────────────│                       │
```

## PKCE Parameter Generation

### JavaScript/TypeScript
```javascript
// Generate code_verifier (43-128 characters)
const codeVerifier = base64URLEncode(crypto.getRandomValues(new Uint8Array(32)));

// Generate code_challenge
const encoder = new TextEncoder();
const data = encoder.encode(codeVerifier);
const digest = await crypto.subtle.digest('SHA-256', data);
const codeChallenge = base64URLEncode(new Uint8Array(digest));

function base64URLEncode(buffer) {
  return btoa(String.fromCharCode(...buffer))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}
```

### Python
```python
import hashlib
import base64
import secrets

# Generate code_verifier
code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b'=').decode()

# Generate code_challenge
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode()).digest()
).rstrip(b'=').decode()
```

## Key Differences from Standard Auth Code

| Aspect | Standard | PKCE |
|--------|----------|------|
| Client Secret | Required | Not required |
| code_challenge | Not used | Required in /authorize |
| code_verifier | Not used | Required in /token |
| Security | Secret-based | Cryptographic proof |
| Client Type | Confidential | Public |

## Security Considerations

1. **Generate new PKCE values** for each authorization request
2. **Use S256 method** (SHA-256), never "plain"
3. **Store code_verifier securely** until token exchange
4. **Use secure storage** for tokens (Keychain/Keystore)
5. **Implement refresh token rotation** for additional security

## Customization Points

Replace these placeholders:
- `CONSUMER_KEY` → Your Connected App's Consumer Key
- `CALLBACK_URL` → Your registered callback URL (custom scheme for mobile)
- `CODE_VERIFIER` → Generated 43-128 character random string
- `CODE_CHALLENGE` → BASE64URL(SHA256(CODE_VERIFIER))
