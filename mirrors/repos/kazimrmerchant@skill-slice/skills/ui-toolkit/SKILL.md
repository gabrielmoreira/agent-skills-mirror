---
name: ui-toolkit
description: "Integrates Zoom Video SDK UI Toolkit as drop-in gallery, controls, chat, and screen-share UI for custom sessions. Use when embedding branded video calling inside a web app without building conference chrome. Not for joining real Zoom meetings (component-view / Meeting SDK) and not for raw Video SDK custom rendering."
version: 1.0.1
risk: safe
source: modernized
date_modernized: "2026-05-31"
tags:
  - ui-ux
  - design
  - accessibility
  - visualization
  - zoom
  - video-sdk
tools:
  - gemini
  - codex
---

# Zoom Video SDK UI Toolkit

The Zoom Video SDK UI Toolkit is a drop-in web UI layer on top of the Video SDK. Use it when the user wants a video session inside their own app but doesn't want to build the conference UI (gallery, controls, chat, recordings) from scratch.

## When to Use

- The user wants **video calling inside their own app** with branding.
- They need standard conference UX: gallery view, controls, screen share, chat.
- They are willing to authenticate users via a server-issued JWT signature.
- Trigger keywords: "video call in my app", "Zoom UI toolkit", "drop-in video conference", "gallery view SDK", "branded video session".

## When NOT to Use

| Situation | Route to |
|---|---|
| User wants to join an actual Zoom meeting (not a custom SDK session) | `build-zoom-meeting-sdk-app` |
| User needs full control over media layout, custom rendering, or AI-on-frames | `build-zoom-video-sdk-app` (raw Video SDK Web) |
| Headless server-side processing of video streams | Raw Video SDK with Node + WebRTC bindings, not UI Toolkit |

## Prerequisites

- A Zoom **Video SDK** app credential (SDK Key + SDK Secret) — *not* a Meeting SDK or OAuth app.
- A server endpoint that signs JWTs. **Never ship the SDK secret to the browser.**
- Modern Chromium/WebKit browser.
- HTTPS enabled (required for camera/microphone permissions).
- Cross-origin isolation if you need SharedArrayBuffer features (`COOP: same-origin` + `COEP: require-corp`).
- Node.js and npm installed on the development machine.

## Procedure

### 1. Confirm product fit

UI Toolkit is for **Video SDK custom sessions**, not Meeting SDK joins. Ask the user explicitly: "Are you building a custom video session or joining an existing Zoom meeting?" If they want to join existing Zoom meetings, redirect to the Meeting SDK skill.

### 2. Provision credentials

1. Go to the Zoom Marketplace and create a **Video SDK** app (not a Meeting SDK app).
2. Capture the **SDK Key** and **SDK Secret** and store them server-side as environment variables.
3. Never commit these to source control or expose them in client bundles.

### 3. Generate JWT server-side

Sign a token per session on your server. Use short expirations (~2 hours). A leaked long-lived token is a hijackable session.

```javascript
// server/sign-token.js
import jwt from 'jsonwebtoken';

export function signSessionToken({ sessionName, userIdentity, roleType = 1 }) {
  const iat = Math.floor(Date.now() / 1000);
  return jwt.sign(
    {
      app_key:        process.env.ZOOM_SDK_KEY,
      tpc:            sessionName,
      role_type:      roleType,            // 1 = host, 0 = attendee
      user_identity:  userIdentity,
      version:        1,
      iat,
      exp:            iat + 60 * 60 * 2,   // 2 hours
    },
    process.env.ZOOM_SDK_SECRET,
    { algorithm: 'HS256' },
  );
}
```

**HARD RULE:** Never expose `ZOOM_SDK_SECRET` to the browser. Sign on the server only.

### 4. Install the toolkit and mount it

```bash
npm install @zoom/videosdk-ui-toolkit
```

```typescript
// src/zoom.ts
import { UIToolkit } from '@zoom/videosdk-ui-toolkit';
import '@zoom/videosdk-ui-toolkit/dist/videosdk-ui-toolkit.css';

const root = document.getElementById('zoom-root')!;

const config = {
  videoSDKJWT: await fetchSignatureFromYourServer(),
  sessionName: 'team-standup',
  userName: 'ExampleUser',
  sessionPasscode: '',                 // optional
  features: ['video', 'audio', 'share', 'chat', 'users', 'settings'],
};

UIToolkit.joinSession(config, root);

UIToolkit.subscribe(UIToolkit.events.UI_TOOLKIT_LEAVE_SESSION, () => {
  UIToolkit.destroy();
});
```

### 5. Configure features and theming

Enable features on the `features` array in the config object: `video`, `audio`, `share`, `chat`, `users`, `settings`. Some features (chat, recording, captions) are **plan-gated** on the Zoom account — verify they are enabled in the Marketplace dashboard.

Override CSS custom properties for branding:

```css
:root {
  --videosdk-primary-color: oklch(0.65 0.16 250);
  --videosdk-on-primary-color: white;
  --videosdk-background-color: #0b0c10;
}
```

### 6. Debug at the right layer

Check in this order:
1. **Browser permissions** — camera/mic access granted? Is the page HTTPS?
2. **CORS / cross-origin isolation** — SharedArrayBuffer errors mean missing COOP/COEP headers.
3. **Token validity** — clock skew between sign-server and Zoom (>5 min) causes "Invalid signature". Sync server NTP.
4. **Plan-gated features** — chat/recording missing from UI means the Zoom account plan doesn't include them.

### 7. Load reference files when needed

- Load `references/full-guide.md` when the user needs the complete preserved integration guide with advanced configuration options.
- Load `references/environment-variables.md` when setting up server-side environment configuration for SDK keys and secrets.
- Load `troubleshooting/common-issues.md` when debugging runtime errors, black tiles, or token failures.
- Reference `../video-sdk/web/SKILL.md` when the user's needs shift toward raw Video SDK Web (custom rendering, headless processing).

## Pitfalls

- **Embedding the SDK secret in client code.** Sign tokens server-side, full stop. No exceptions.
- **Calling `UIToolkit.joinSession()` from inside a page that's also rendering the Meeting SDK.** Two SDKs in one page conflict on audio/video device handles.
- **Long-lived JWTs.** Use short expirations (~2 hours); a leaked long-lived token is a hijackable session.
- **Skipping `UIToolkit.destroy()` on cleanup.** WebRTC peer connections and media tracks leak; the next session will fail or duplicate audio. Always call `destroy()` on the `UI_TOOLKIT_LEAVE_SESSION` event.
- **Mixing UI Toolkit with custom UI for the same session.** Pick one — they fight over DOM ownership.
- **Clock skew on the signing server.** If the server clock drifts more than 5 minutes from Zoom's servers, JWT validation fails with "Invalid signature". Sync NTP.
- **Missing HTTPS.** Camera and microphone APIs require a secure context. `localhost` is exempt, but production must serve HTTPS.
- **Missing cross-origin isolation headers.** SharedArrayBuffer-dependent features fail without `COOP: same-origin` and `COEP: require-corp` headers.

## Verification

1. **Confirm the package is installed:**
   ```bash
   npm ls @zoom/videosdk-ui-toolkit
   ```
   Expected: `@zoom/videosdk-ui-toolkit@<version>` listed.

2. **Verify environment variables are set server-side (never client-side):**
   ```bash
   echo $ZOOM_SDK_KEY   # should print the SDK key
   echo $ZOOM_SDK_SECRET # should print the SDK secret
   ```
   On Windows PowerShell:
   ```powershell
   $env:ZOOM_SDK_KEY
   $env:ZOOM_SDK_SECRET
   ```

3. **Verify the JWT is valid before sending to client:**
   ```bash
   # Decode the JWT header and payload (does not verify signature)
   echo "<YOUR_JWT>" | cut -d. -f2 | base64 -d 2>/dev/null
   ```
   Confirm `tpc`, `role_type`, `app_key`, `exp` are present and `exp` is within ~2 hours of `iat`.

4. **Verify the session mounts in the browser:**
   - Open DevTools Console.
   - Check for the `#zoom-root` element containing toolkit DOM after `joinSession` is called.
   - Confirm no console errors about permissions, CORS, or invalid signature.

5. **Verify cleanup on leave:**
   - Join a session, then leave.
   - Inspect the DOM — the toolkit container should be removed after `UIToolkit.destroy()`.
   - Check that no WebRTC peer connections remain open in `chrome://webrtc-internals`.

## Examples

### Minimal HTML page

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Video Session</title>
  <link rel="stylesheet" href="/dist/videosdk-ui-toolkit.css" />
</head>
<body>
  <div id="zoom-root" style="width: 100vw; height: 100vh;"></div>
  <script type="module" src="/src/zoom.ts"></script>
</body>
</html>
```

### Server endpoint example (Express)

```javascript
import express from 'express';
import { signSessionToken } from './sign-token.js';

const app = express();
app.use(express.json());

app.post('/api/zoom-signature', (req, res) => {
  const { sessionName, userIdentity, roleType } = req.body;
  const token = signSessionToken({ sessionName, userIdentity, roleType });
  res.json({ signature: token });
});

app.listen(3000);
```

## Related skills

- `build-zoom-meeting-sdk-app` — for joining actual Zoom meetings.
- `build-zoom-video-sdk-app` — for raw Video SDK Web with full custom rendering control.
- `../video-sdk/web/SKILL.md` — raw Video SDK Web reference.
