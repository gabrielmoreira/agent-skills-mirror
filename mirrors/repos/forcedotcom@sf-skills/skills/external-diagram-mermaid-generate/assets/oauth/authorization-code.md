# Authorization Code Flow Template

Standard OAuth 2.0 Authorization Code flow for web applications with backend servers.

## When to Use
- Web applications with secure backend servers
- Confidential clients that can protect client_secret
- When you need refresh tokens for long-lived access

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

    box rgba(165,243,252,0.3) BROWSER/USER
        participant U as 👤 User
        participant B as 🌐 Browser
    end

    box rgba(221,214,254,0.3) CLIENT APPLICATION
        participant A as 🖥️ App Server
    end

    box rgba(167,243,208,0.3) SALESFORCE
        participant SF as ☁️ Salesforce<br/>Authorization Server
    end

    Note over U,SF: Authorization Code Flow (RFC 6749)

    U->>B: 1. Click "Login with Salesforce"
    B->>A: 2. Initiate OAuth Login

    A->>A: 3. Generate state parameter (CSRF protection)

    A->>B: 4. Redirect to Salesforce /authorize
    Note over A,B: response_type=code<br/>client_id=CONSUMER_KEY<br/>redirect_uri=CALLBACK_URL<br/>scope=api refresh_token<br/>state=RANDOM_STATE

    B->>SF: 5. GET /services/oauth2/authorize

    SF->>B: 6. Display Login Page
    U->>SF: 7. Enter Username & Password

    SF->>SF: 8. Authenticate User

    SF->>B: 9. Display Consent Screen
    Note over SF,B: "App requests access to:<br/>• API Access<br/>• Refresh Token"

    U->>SF: 10. Grant Consent (Allow)

    SF->>SF: 11. Generate Authorization Code

    SF->>B: 12. Redirect to callback_uri
    Note over SF,B: ?code=AUTH_CODE_123<br/>&state=RANDOM_STATE

    B->>A: 13. Deliver Code to App Server

    A->>A: 14. Verify state matches

    A->>SF: 15. POST /services/oauth2/token
    Note over A,SF: grant_type=authorization_code<br/>code=AUTH_CODE_123<br/>client_id=CONSUMER_KEY<br/>client_secret=CONSUMER_SECRET<br/>redirect_uri=CALLBACK_URL

    SF->>SF: 16. Validate Code & Client

    SF->>A: 17. Return Tokens
    Note over SF,A: {<br/>  access_token: "...",<br/>  refresh_token: "...",<br/>  instance_url: "https://...",<br/>  token_type: "Bearer",<br/>  issued_at: "..."<br/>}

    A->>A: 18. Store tokens securely

    A->>B: 19. Set user session
    B->>U: 20. ✅ Successfully Logged In
```

## ASCII Fallback Template

```text
┌──────────┐     ┌───────────────┐     ┌────────────────────┐
│  User/   │     │  Application  │     │     Salesforce     │
│  Browser │     │    Server     │     │  (Auth Server)     │
└────┬─────┘     └───────┬───────┘     └─────────┬──────────┘
     │                   │                       │
     │  1. Click Login   │                       │
     │──────────────────>│                       │
     │                   │                       │
     │  2. Redirect to   │                       │
     │     /authorize    │                       │
     │<──────────────────│                       │
     │                   │                       │
     │  3. GET /authorize (client_id, scope, state)         │
     │───────────────────────────────────────────────────────>│
     │                   │                       │
     │           4. Login Page                   │
     │<───────────────────────────────────────────────────────│
     │                   │                       │
     │  5. Enter Credentials                     │
     │───────────────────────────────────────────────────────>│
     │                   │                       │
     │           6. Consent Screen               │
     │<───────────────────────────────────────────────────────│
     │                   │                       │
     │  7. Grant Consent (Allow)                 │
     │───────────────────────────────────────────────────────>│
     │                   │                       │
     │  8. Redirect with ?code=ABC123&state=xyz  │
     │<───────────────────────────────────────────────────────│
     │                   │                       │
     │  9. Deliver Code  │                       │
     │──────────────────>│                       │
     │                   │                       │
     │                   │  10. POST /token      │
     │                   │      (code, secret)   │
     │                   │──────────────────────>│
     │                   │                       │
     │                   │  11. Access Token +   │
     │                   │      Refresh Token    │
     │                   │<──────────────────────│
     │                   │                       │
     │ 12. Logged In ✅  │                       │
     │<──────────────────│                       │
```

## Key Endpoints

| Endpoint | URL | Purpose |
|----------|-----|---------|
| Authorization | `https://login.salesforce.com/services/oauth2/authorize` | Start OAuth flow |
| Token | `https://login.salesforce.com/services/oauth2/token` | Exchange code for tokens |

## Security Considerations

1. **Always use HTTPS** for redirect_uri in production
2. **Validate state parameter** to prevent CSRF attacks
3. **Store client_secret securely** (never in client-side code)
4. **Use short-lived access tokens** with refresh token rotation

## Customization Points

Replace these placeholders:
- `CONSUMER_KEY` → Your Connected App's Consumer Key
- `CONSUMER_SECRET` → Your Connected App's Consumer Secret
- `CALLBACK_URL` → Your registered callback URL
- `RANDOM_STATE` → Cryptographically random state value
