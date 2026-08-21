---
name: component-view
description: "Embeds live Zoom meetings in a custom web container via Meeting SDK Component View (ZoomMtgEmbedded.createClient, Promise init/join, lowercase password). Use when integrating real Zoom meetings into React/Vue/Angular layouts with embeddable UI. Not for Zoom Video SDK custom sessions (ui-toolkit) and not for full-page callback-based Client View (passWord / #zmmtg-root)."
version: 1.0.1
---

## When to Use

Use this skill when the user needs to embed a **real Zoom meeting** inside a custom web UI container with a Promise-based (async/await) API. This is the correct web skill for:

- Custom layouts around a live Zoom meeting
- React, Vue, Angular, or any framework-based integration
- Applications requiring embeddable meeting components (not full-page takeover)
- Promise-based async/await patterns instead of callbacks

**Do NOT route here if:** the user is building a non-meeting custom session product — that belongs to the Video SDK. If the user wants full-page Zoom UI with callback-based APIs, use the Client View skill instead.

## Prerequisites

- Node.js and npm installed on the development machine
- A Zoom Meeting SDK app registered in the Zoom App Marketplace (yields SDK Key / Client ID and SDK Secret)
- A backend endpoint to generate SDK JWT signatures (never expose SDK Secret in frontend code)
- A container `HTMLElement` in the DOM where the meeting UI will render
- For SharedArrayBuffer-dependent features (gallery view, virtual background, etc.): proper COOP/COEP headers must be set on the hosting page. See `references/index.md` → SharedArrayBuffer Setup

## Procedure

### 1. Install the SDK

**NPM (recommended):**

```powershell
npm install @zoom/meetingsdk --save
```

Import in your application:

```javascript
import ZoomMtgEmbedded from '@zoom/meetingsdk/embedded';
```

**CDN (alternative):**

```html
<script src="https://source.zoom.us/{VERSION}/lib/vendor/react.min.js"></script>
<script src="https://source.zoom.us/{VERSION}/lib/vendor/react-dom.min.js"></script>
<script src="https://source.zoom.us/{VERSION}/lib/vendor/redux.min.js"></script>
<script src="https://source.zoom.us/{VERSION}/lib/vendor/redux-thunk.min.js"></script>
<script src="https://source.zoom.us/{VERSION}/lib/vendor/lodash.min.js"></script>
<script src="https://source.zoom.us/zoom-meeting-embedded-{VERSION}.min.js"></script>
```

Replace `{VERSION}` with the exact SDK version you are targeting (e.g., `3.9.2`). Do not mix versions across vendor scripts and the main embedded script.

### 2. Create the Client Instance (Once)

Create the client **once** — not on every render cycle. In React, store it in a `useRef`.

```javascript
import ZoomMtgEmbedded from '@zoom/meetingsdk/embedded';

const client = ZoomMtgEmbedded.createClient();
```

### 3. Initialize the Client

Call `client.init()` with the container element and options:

```javascript
async function joinMeeting() {
  try {
    const meetingSDKElement = document.getElementById('meetingSDKElement');

    await client.init({
      zoomAppRoot: meetingSDKElement,
      language: 'en-US',
      debug: true,
      patchJsMedia: true,
      leaveOnPageUnload: true,
    });

    // Continue to step 4...
  } catch (error) {
    console.error('Init failed:', error);
  }
}
```

**Required `init` parameter:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `zoomAppRoot` | `HTMLElement` | Container element for meeting UI |

**Optional `init` parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `language` | `string` | `'en-US'` | UI language |
| `debug` | `boolean` | `false` | Enable debug logging |
| `patchJsMedia` | `boolean` | `false` | Auto-apply media fixes |
| `leaveOnPageUnload` | `boolean` | `false` | Cleanup on page unload |
| `enableHD` | `boolean` | `true` | Enable 720p video |
| `enableFullHD` | `boolean` | `false` | Enable 1080p video |
| `customize` | `object` | — | UI customization options |
| `webEndpoint` | `string` | — | For ZFG: `'www.zoomgov.com'` |
| `assetPath` | `string` | — | Custom path for AV libraries |

### 4. Join the Meeting

```javascript
await client.join({
  signature: signature,       // SDK JWT from your backend
  sdkKey: sdkKey,             // SDK Key / Client ID
  meetingNumber: meetingNumber,
  userName: userName,
  password: password,         // lowercase 'password' — NOT 'passWord'
  userEmail: userEmail,
});

console.log('Joined successfully!');
```

**Required `join` parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `signature` | `string` | SDK JWT from backend |
| `sdkKey` | `string` | SDK Key / Client ID |
| `meetingNumber` | `string \| number` | Meeting number |
| `userName` | `string` | Display name |

**Conditional `join` parameters:**

| Parameter | Type | When Required | Description |
|-----------|------|---------------|-------------|
| `password` | `string` | If meeting has a password | **Lowercase** `password` — not `passWord` |
| `zak` | `string` | Starting as host | Host's ZAK token |
| `tk` | `string` | Registration required | Registrant token |
| `userEmail` | `string` | Webinars | User email |

### 5. Register Event Listeners

Use `client.on()` / `client.off()` for event subscriptions:

```javascript
// Connection
client.on('connection-change', (payload) => {
  // payload.state: 'Connecting', 'Connected', 'Reconnecting', 'Closed'
  console.log('Connection state:', payload.state);
  if (payload.state === 'Closed') {
    console.log('Reason:', payload.reason);
  }
});

// Users
client.on('user-added', (payload) => {
  payload.forEach(user => {
    console.log('User ID:', user.oderId);  // note: 'oderId' in SDK
    console.log('Name:', user.displayName);
  });
});
client.on('user-removed', (payload) => console.log('Users removed:', payload));
client.on('user-updated', (payload) => console.log('Users updated:', payload));

// Audio
client.on('active-speaker', (payload) => console.log('Active speaker:', payload));
client.on('audio-statistic-data-change', (payload) => console.log('Audio stats:', payload));

// Video
client.on('video-active-change', (payload) => console.log('Video active:', payload));
client.on('video-statistic-data-change', (payload) => console.log('Video stats:', payload));

// Share
client.on('active-share-change', (payload) => console.log('Share status:', payload));
client.on('share-statistic-data-change', (payload) => console.log('Share stats:', payload));

// Chat
client.on('chat-on-message', (payload) => console.log('Chat message:', payload));

// Recording
client.on('recording-change', (payload) => console.log('Recording status:', payload));

// Media devices
client.on('media-sdk-change', (payload) => console.log('Media SDK:', payload));
client.on('device-change', () => console.log('Device changed'));
```

Always unsubscribe in cleanup (especially in React `useEffect` return):

```javascript
client.off('connection-change', handleConnectionChange);
```

### 6. Use Common Methods

```javascript
// User info
const currentUser = client.getCurrentUser();
const participants = client.getParticipantsList();
const isHost = client.isHost();

// Audio
await client.mute(true);       // mute self
await client.mute(false);      // unmute self
await client.muteAudio(userId, true);   // host only
await client.muteAllAudio(true);        // host only

// Video
await client.startVideo();
await client.stopVideo();
await client.muteVideo(userId, true);   // host only

// Meeting control
client.leaveMeeting();
client.endMeeting();                    // host only

// Screen share
await client.startShareScreen();
await client.stopShareScreen();

// Recording (cloud)
await client.startCloudRecording();
await client.stopCloudRecording();

// Virtual background
const isSupported = await client.isSupportVirtualBackground();
await client.setVirtualBackground(imageUrl);
await client.removeVirtualBackground();

// Rename
await client.rename(userId, 'New Name');
```

### 7. Customize the UI (Optional)

```javascript
await client.init({
  zoomAppRoot: element,
  customize: {
    meetingInfo: [
      'topic', 'host', 'mn', 'pwd', 'telPwd',
      'invite', 'participant', 'dc', 'enctype'
    ],
    video: {
      isResizable: true,
      viewSizes: {
        default: { width: 1000, height: 600 },
        ribbon:   { width: 300,  height: 700 }
      },
      popper: { disableDraggable: false }
    },
    toolbar: {
      buttons: [
        {
          text: 'Custom Button',
          className: 'custom-btn',
          onClick: () => console.log('Custom button clicked')
        }
      ]
    },
    activeSpaker: {              // note: SDK spelling is 'activeSpaker'
      strokeColor: '#00FF00'
    }
  }
});
```

### 8. Position and Resize

The container element size determines the meeting UI size. To resize dynamically:

```javascript
document.getElementById('meetingSDKElement').style.width = '1200px';
document.getElementById('meetingSDKElement').style.height = '800px';
```

Enable user-resizable video via `customize.video.isResizable: true`.

### 9. React Integration Pattern

```tsx
import { useEffect, useRef, useState, useCallback } from 'react';
import ZoomMtgEmbedded from '@zoom/meetingsdk/embedded';

type ZoomClient = ReturnType<typeof ZoomMtgEmbedded.createClient>;

function ZoomMeeting({ meetingNumber, password, userName }: Props) {
  const clientRef = useRef<ZoomClient | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isJoined, setIsJoined] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Create client once
  useEffect(() => {
    if (!clientRef.current) {
      clientRef.current = ZoomMtgEmbedded.createClient();
    }
  }, []);

  // Event listeners
  useEffect(() => {
    if (!clientRef.current) return;

    const handleConnectionChange = (payload: any) => {
      if (payload.state === 'Connected') setIsJoined(true);
      else if (payload.state === 'Closed') setIsJoined(false);
    };

    const handleUserAdded = (payload: any) => {
      console.log('Users joined:', payload);
    };

    clientRef.current.on('connection-change', handleConnectionChange);
    clientRef.current.on('user-added', handleUserAdded);

    return () => {
      clientRef.current?.off('connection-change', handleConnectionChange);
      clientRef.current?.off('user-added', handleUserAdded);
    };
  }, []);

  const joinMeeting = useCallback(async () => {
    if (!clientRef.current || !containerRef.current) return;

    try {
      const { signature, sdkKey } = await fetchSignature(meetingNumber);

      await clientRef.current.init({
        zoomAppRoot: containerRef.current,
        language: 'en-US',
        patchJsMedia: true,
        leaveOnPageUnload: true,
      });

      await clientRef.current.join({
        signature,
        sdkKey,
        meetingNumber,
        password,   // lowercase
        userName,
      });

      setIsJoined(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to join');
    }
  }, [meetingNumber, password, userName]);

  return (
    <div>
      <div ref={containerRef} style={{ width: '100%', height: '500px' }} />
      {!isJoined && <button onClick={joinMeeting}>Join Meeting</button>}
      {error && <div className="error">{error}</div>}
    </div>
  );
}
```

### 10. Handle Errors

```javascript
try {
  await client.join({ /* ... options */ });
} catch (error) {
  // error.reason contains error code
  // error.message contains description

  switch (error.reason) {
    case 'WRONG_MEETING_PASSWORD':
      console.error('Incorrect password');
      break;
    case 'MEETING_NOT_START':
      console.error('Meeting has not started');
      break;
    case 'INVALID_PARAMETERS':
      console.error('Invalid join parameters');
      break;
    default:
      console.error('Join failed:', error.message);
  }
}
```

For a full list of error codes, load `references/index.md` and navigate to the error-codes reference.

## Pitfalls

1. **Password parameter name is lowercase `password`** — Component View uses `password`, NOT `passWord` (which is Client View). Mixing these up silently fails to authenticate.

2. **Creating the client on every render** — In React, calling `ZoomMtgEmbedded.createClient()` inside a render function (not in a `useRef` or module scope) causes duplicate client instances and meeting UI corruption. Create once, reuse.

3. **SDK Secret in frontend code** — Never embed the SDK Secret in client-side code. Always generate the SDK JWT signature on a backend endpoint and fetch it from the frontend.

4. **Missing COOP/COEP headers** — Gallery view, virtual background, and other SharedArrayBuffer-dependent features silently fail without proper cross-origin isolation headers. See `references/index.md` → SharedArrayBuffer Setup.

5. **Not unsubscribing events** — In React, forgetting `client.off()` in the `useEffect` cleanup function causes duplicate event handlers after re-renders, leading to duplicate callbacks and memory leaks.

6. **SDK property spelling quirks** — The SDK uses `oderId` (not `orderId`) in user payloads and `activeSpaker` (not `activeSpeaker`) in the customize object. Use the exact SDK spellings.

7. **Mixing CDN script versions** — All vendor scripts and the main embedded script must use the same `{VERSION}`. Mismatched versions cause runtime errors.

8. **Container element not in DOM at init time** — `zoomAppRoot` must be a real `HTMLElement` when `client.init()` is called. In React, ensure the ref is populated before calling init (e.g., trigger join on user click, not on mount before paint).

9. **Component View vs Client View feature gaps** — Some features available in Client View may not be available in Component View. Check the supported features table below before committing to Component View.

## Verification

### Verify SDK Installation

```powershell
npm ls @zoom/meetingsdk
```

Expected output: `@zoom/meetingsdk@{VERSION}` with no `UNMET DEPENDENCY` warnings.

### Verify Client Creation

```javascript
const client = ZoomMtgEmbedded.createClient();
console.log(typeof client.init);   // 'function'
console.log(typeof client.join);    // 'function'
console.log(typeof client.on);     // 'function'
```

### Verify Init and Join

```javascript
try {
  await client.init({
    zoomAppRoot: document.getElementById('meetingSDKElement'),
    language: 'en-US',
  });
  console.log('Init OK');

  await client.join({
    signature: 'YOUR_SIGNATURE',
    sdkKey: 'YOUR_SDK_KEY',
    meetingNumber: '123456789',
    userName: 'Test User',
  });
  console.log('Join OK');
} catch (error) {
  console.error('Error reason:', error.reason);
  console.error('Error message:', error.message);
}
```

### Verify Connection Event

```javascript
client.on('connection-change', (payload) => {
  console.log('State:', payload.state);
  // Should log 'Connecting' → 'Connected' on successful join
});
```

### Verify Supported Features

| Feature | Supported |
|---------|----------|
| Audio/Video | ✅ |
| Screen Share | ✅ |
| Chat | ✅ |
| Virtual Background | ✅ |
| Breakout Rooms | ✅ |
| Cloud Recording | ✅ |
| Closed Captions | ✅ |
| Live Transcription | ✅ |
| Waiting Room | ✅ |
| Gallery View | ✅ |
| Reactions | ✅ |
| Raise Hand | ✅ |

Contact Zoom Developer Support to request additional features not listed here.

## Component View vs Client View Quick Reference

| Aspect | Component View | Client View |
|--------|---------------|-------------|
| API Style | Promises (async/await) | Callbacks |
| Password param | `password` | `passWord` |
| Container | Custom element | Auto `#zmmtg-root` |
| UI | Embeddable | Full-page |
| Preloading | Not needed | `preLoadWasm()` |
| Language | Init option | `i18n.load()` |
| Events | `on()` / `off()` | `inMeetingServiceListener()` |

## Related Skills

- [Main Web SDK Skill](../SKILL.md) — Overview and routing for all Zoom Web SDK views
- [Client View](../client-view/SKILL.md) — Full-page callback-based Zoom meeting UI
- [Video SDK](../video-sdk/SKILL.md) — For non-meeting custom video sessions

## References

Load these reference files from the `references/` directory when needed:

- **`references/index.md`** — Load first for a full index of available reference documents, including error codes, common issues, and SharedArrayBuffer setup guides.
- **Error Codes** — Load when debugging `error.reason` values from `client.join()` failures.
- **Common Issues** — Load when encountering unexpected SDK behavior or integration problems.
- **SharedArrayBuffer Setup** — Load when gallery view, virtual background, or other advanced media features are not working (COOP/COEP header configuration).

## Operations

- **`RUNBOOK.md`** — Load when performing a preflight check before deployment or when debugging a failed meeting join. Contains a 5-minute checklist.
