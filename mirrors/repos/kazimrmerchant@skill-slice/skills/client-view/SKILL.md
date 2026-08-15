---
name: client-view
description: "Embeds Zoom Meeting SDK Web Client View through the ZoomMtg singleton: system check, WASM preload, init/join with passWord (capital W), and inMeetingServiceListener. Use for full-page Zoom meeting embeds or debugging blank-screen, black-overlay, and join-payload failures. Not for Zoom Component View custom tile layouts or Zoom Video SDK canvases."
version: 1.0.1
---

# Zoom Meeting SDK Web — Client View

Client View renders a **full-page Zoom meeting experience** identical to the Zoom Web Client.
It uses the `ZoomMtg` global singleton with a callback-based API — minimal customization,
familiar Zoom UI, fast integration.

| Aspect | Details |
|--------|---------|
| **API Object** | `ZoomMtg` (global singleton) |
| **API Style** | Callback-based (`success` / `error`) |
| **UI** | Full-page takeover (occupies entire viewport) |
| **Password param** | `passWord` — **capital W** |
| **Events** | `ZoomMtg.inMeetingServiceListener()` |
| **Best For** | Quick integration, standard Zoom UI, minimal branding needs |

---

## When to Use

- You need to embed a **complete Zoom meeting** in a web app with the standard Zoom interface.
- You want **minimal customization** — Client View gives you Zoom's own UI, not a custom layout.
- You are integrating via **NPM** or **CDN** and need the callback-based `ZoomMtg` API.
- You are debugging **blank screen**, **black overlay**, **join payload**, or **SPA z-index** issues.
- You need to wire up **event listeners** (user join/leave, chat, recording, breakout rooms, etc.).

**Do NOT use Client View if** you need pixel-level control over the meeting UI layout — use
Component View instead (see Related Skills).

---

## Prerequisites

1. **Zoom Meeting SDK credentials** — SDK Key and SDK Secret (or Server-to-Server OAuth app
   credentials) from the [Zoom App Marketplace](https://marketplace.zoom.us/).
2. **Backend endpoint** to generate the SDK JWT signature. Never expose SDK secrets in the
   browser. Example placeholder: `YOUR_SDK_SECRET`.
3. **HTTPS** — required for media (WebRTC) and SharedArrayBuffer (gallery view).
4. **Supported browser** — call `ZoomMtg.checkSystemRequirements()` to verify.
5. **Node.js 18+** if using the NPM package.
6. **Windows host (PowerShell)** is the primary development environment. All path examples use
   Windows-style paths (e.g. `~\agent-skills\library\client-view\`).

### Reference Files

Load these reference files at the indicated points:

| File | When to Load |
|------|--------------|
| `references/index.md` | At the start — lists all available reference docs and their purposes. |
| `../troubleshooting/error-codes.md` | When debugging join failures, init errors, or unexpected SDK errors. |
| `../troubleshooting/common-issues.md` | When encountering black screen, audio issues, or CORS errors. |
| `../concepts/sharedarraybuffer.md` | When enabling gallery view or multi-speaker view (requires SharedArrayBuffer + COOP/COEP headers). |
| `RUNBOOK.md` | Before deploying or debugging — 5-minute preflight and debugging checklist. |

---

## Procedure

### Step 1 — Install the SDK

**NPM (recommended for bundlers):**

```bash
npm install @zoom/meetingsdk --save
```

```javascript
import { ZoomMtg } from '@zoom/meetingsdk';
```

**CDN (script tags — replace `{VERSION}` with your target SDK version):**

```html
<script src="https://source.zoom.us/{VERSION}/lib/vendor/react.min.js"></script>
<script src="https://source.zoom.us/{VERSION}/lib/vendor/react-dom.min.js"></script>
<script src="https://source.zoom.us/{VERSION}/lib/vendor/redux.min.js"></script>
<script src="https://source.zoom.us/{VERSION}/lib/vendor/redux-thunk.min.js"></script>
<script src="https://source.zoom.us/{VERSION}/lib/vendor/lodash.min.js"></script>
<script src="https://source.zoom.us/zoom-meeting-{VERSION}.min.js"></script>
```

### Step 2 — Complete Initialization Flow

This is the canonical 7-step flow. Follow it in order — skipping steps causes black screens
and join failures.

```javascript
// Step 1: Check browser compatibility
console.log('Requirements:', ZoomMtg.checkSystemRequirements());

// Step 2: Set CDN path (optional — for China region or custom hosting)
// ZoomMtg.setZoomJSLib('https://source.zoom.us/{VERSION}/lib', '/av');

// Step 3: Preload WebAssembly modules
ZoomMtg.preLoadWasm();
ZoomMtg.prepareWebSDK();

// Step 4: Load language resources
ZoomMtg.i18n.load('en-US');
ZoomMtg.i18n.onLoad(() => {

  // Step 5: Initialize SDK
  ZoomMtg.init({
    leaveUrl: '/meeting-ended',
    patchJsMedia: true,
    disableCORP: !window.crossOriginIsolated,
    success: () => {
      console.log('SDK initialized');

      // Step 6: Join meeting
      const joinPayload = {
        signature: signature,
        meetingNumber: meetingNumber,
        userName: userName,
        passWord: passWord,
        success: (res) => {
          console.log('Joined meeting');

          // Step 7: Post-join operations
          ZoomMtg.getAttendeeslist({});
          ZoomMtg.getCurrentUser({
            success: (res) => console.log('Current user:', res.result.currentUser)
          });
        },
        error: (err) => console.error('Join failed:', err)
      };

      // CRITICAL: only include optional fields when they have real values.
      // Passing undefined for optional fields can cause runtime join errors.
      if (userEmail) joinPayload.userEmail = userEmail;
      if (tk) joinPayload.tk = tk;
      if (zak) joinPayload.zak = zak;

      ZoomMtg.join(joinPayload);
    },
    error: (err) => console.error('Init failed:', err)
  });
});
```

### Step 3 — Configure `ZoomMtg.init()` Options

#### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| `leaveUrl` | `string` | URL to redirect to after leaving the meeting |

#### UI Customization

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `showMeetingHeader` | `boolean` | `true` | Show meeting number and topic |
| `disableInvite` | `boolean` | `false` | Hide invite button |
| `disableCallOut` | `boolean` | `false` | Hide call out option |
| `disableRecord` | `boolean` | `false` | Hide record button |
| `disableJoinAudio` | `boolean` | `false` | Hide join audio option |
| `disablePreview` | `boolean` | `false` | Skip audio/video preview |
| `audioPanelAlwaysOpen` | `boolean` | `false` | Keep audio panel open |
| `showPureSharingContent` | `boolean` | `false` | Prevent overlays on shared content |
| `videoHeader` | `boolean` | `true` | Show video tile header |
| `isLockBottom` | `boolean` | `true` | Show/hide footer |
| `videoDrag` | `boolean` | `true` | Enable dragging video tiles |
| `sharingMode` | `string` | `'both'` | `'both'` or `'fit'` |
| `screenShare` | `boolean` | `true` | Enable browser URL sharing |
| `hideShareAudioOption` | `boolean` | `false` | Hide "Share tab audio" checkbox |
| `disablePictureInPicture` | `boolean` | `false` | Disable PiP mode |
| `disableZoomLogo` | `boolean` | `false` | Remove Zoom logo (deprecated) |
| `defaultView` | `string` | `'speaker'` | `'gallery'`, `'speaker'`, or `'multiSpeaker'` |

#### Feature Toggles

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `isSupportAV` | `boolean` | `true` | Enable audio/video |
| `isSupportChat` | `boolean` | `true` | Enable in-meeting chat |
| `isSupportQA` | `boolean` | `true` | Enable webinar Q&A |
| `isSupportCC` | `boolean` | `true` | Enable closed captions |
| `isSupportPolling` | `boolean` | `true` | Enable polling |
| `isSupportBreakout` | `boolean` | `true` | Enable breakout rooms |
| `isSupportNonverbal` | `boolean` | `true` | Enable nonverbal feedback |
| `isSupportSimulive` | `boolean` | `false` | Enable Simulive |
| `disableVoIP` | `boolean` | `false` | Disable VoIP |
| `disableReport` | `boolean` | `false` | Disable report feature |

#### Video Quality

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enableHD` | `boolean` | `true` (≥2.8.0) | Enable 720p video |
| `enableFullHD` | `boolean` | `false` | Enable 1080p for webinar attendees |

#### Advanced

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `debug` | `boolean` | `false` | Enable debug logging |
| `patchJsMedia` | `boolean` | `false` | Auto-apply media fixes |
| `disableCORP` | `boolean` | `false` | Disable web isolation |
| `helper` | `string` | `''` | Path to helper.html |
| `externalLinkPage` | `string` | — | Page for external links |
| `webEndpoint` | `string` | — | For ZFG environments |
| `leaveOnPageUnload` | `boolean` | `false` | Auto cleanup on page close |
| `isShowJoiningErrorDialog` | `boolean` | `true` | Show error dialog on join failure |
| `meetingInfo` | `Array<string>` | `[...]` | Meeting info fields to display |
| `inviteUrlFormat` | `string` | `''` | Custom invite URL format |
| `loginWindow` | `object` | `{width: 400, height: 380}` | Login popup size |

#### Callbacks

| Parameter | Type | Description |
|-----------|------|-------------|
| `success` | `Function` | Called on successful init |
| `error` | `Function` | Called on init failure |

### Step 4 — Configure `ZoomMtg.join()` Options

#### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| `signature` | `string` | SDK JWT from backend (v5.0+: must include `appKey` prefix) |
| `meetingNumber` | `string \| number` | Meeting or webinar number |
| `userName` | `string` | Display name |
| `passWord` | `string` | Meeting password (**capital W**) |

#### Authentication (conditional)

| Parameter | Type | When Required | Description |
|-----------|------|---------------|-------------|
| `zak` | `string` | Starting as host | Host's Zoom Access Key |
| `tk` | `string` | Registration required | Registrant token |
| `userEmail` | `string` | Webinars | User email |
| `obfToken` | `string` | March 2026+ | App Privilege Token |

#### Optional

| Parameter | Type | Description |
|-----------|------|-------------|
| `customerKey` | `string` | Custom ID (max 36 chars) |
| `recordingToken` | `string` | Local recording permission |

#### Callbacks

| Parameter | Type | Description |
|-----------|------|-------------|
| `success` | `Function` | Called on successful join |
| `error` | `Function` | Called on join failure |

### Step 5 — Wire Event Listeners

Register listeners **after** `ZoomMtg.init()` success, before or inside `join()` success.

#### User Events

```javascript
ZoomMtg.inMeetingServiceListener('onUserJoin', (data) => {
  console.log('User joined:', data);
  // { userId, userName, ... }
});

ZoomMtg.inMeetingServiceListener('onUserLeave', (data) => {
  console.log('User left:', data);
  // Reason codes:
  // 0: OTHER
  // 1: HOST_ENDED_MEETING
  // 2: SELF_LEAVE_FROM_IN_MEETING
  // 3: SELF_LEAVE_FROM_WAITING_ROOM
  // 4: SELF_LEAVE_FROM_WAITING_FOR_HOST_START
  // 5: MEETING_TRANSFER
  // 6: KICK_OUT_FROM_MEETING
  // 7: KICK_OUT_FROM_WAITING_ROOM
  // 8: LEAVE_FROM_DISCLAIMER
});

ZoomMtg.inMeetingServiceListener('onUserUpdate', (data) => {
  console.log('User updated:', data);
});

ZoomMtg.inMeetingServiceListener('onUserIsInWaitingRoom', (data) => {
  console.log('User in waiting room:', data);
});
```

#### Meeting Status

```javascript
ZoomMtg.inMeetingServiceListener('onMeetingStatus', (data) => {
  // status: 1=connecting, 2=connected, 3=disconnected, 4=reconnecting
  console.log('Status:', data.status);
});
```

#### Audio/Video Events

```javascript
ZoomMtg.inMeetingServiceListener('onActiveSpeaker', (data) => {
  // [{userId, userName}]
  console.log('Active speaker:', data);
});

ZoomMtg.inMeetingServiceListener('onNetworkQualityChange', (data) => {
  // {level: 0-5, userId, type: 'uplink'}
  // 0-1=bad, 2=normal, 3-5=good
  console.log('Network quality:', data);
});

ZoomMtg.inMeetingServiceListener('onAudioQos', (data) => {
  console.log('Audio QoS:', data);
});

ZoomMtg.inMeetingServiceListener('onVideoQos', (data) => {
  console.log('Video QoS:', data);
});
```

#### Chat & Communication

```javascript
ZoomMtg.inMeetingServiceListener('onReceiveChatMsg', (data) => {
  console.log('Chat message:', data);
});

ZoomMtg.inMeetingServiceListener('onReceiveTranscriptionMsg', (data) => {
  console.log('Transcription:', data);
});

ZoomMtg.inMeetingServiceListener('onReceiveTranslateMsg', (data) => {
  console.log('Translation:', data);
});
```

#### Recording & Sharing

```javascript
ZoomMtg.inMeetingServiceListener('onRecordingChange', (data) => {
  console.log('Recording status:', data);
});

ZoomMtg.inMeetingServiceListener('onShareContentChange', (data) => {
  console.log('Share content:', data);
});

ZoomMtg.inMeetingServiceListener('receiveSharingChannelReady', (data) => {
  console.log('Sharing channel ready:', data);
});
```

#### Breakout Rooms

```javascript
ZoomMtg.inMeetingServiceListener('onRoomStatusChange', (data) => {
  // status: 2=InProgress, 3=Closing, 4=Closed
  console.log('Breakout room status:', data);
});
```

#### Other Events

```javascript
ZoomMtg.inMeetingServiceListener('onJoinSpeed', (data) => {
  console.log('Join metrics:', data);
});

ZoomMtg.inMeetingServiceListener('onVbStatusChange', (data) => {
  console.log('Virtual background status:', data);
});

ZoomMtg.inMeetingServiceListener('onFocusModeStatusChange', (data) => {
  console.log('Focus mode:', data);
});

ZoomMtg.inMeetingServiceListener('onPictureInPicture', (data) => {
  console.log('PiP status:', data);
});

ZoomMtg.inMeetingServiceListener('onClaimStatus', (data) => {
  console.log('Host claim status:', data);
});
```

### Step 6 — Use Common Methods (as needed)

#### Meeting Info

```javascript
ZoomMtg.getCurrentUser({
  success: (res) => console.log(res.result.currentUser)
});

ZoomMtg.getAttendeeslist({});

ZoomMtg.getCurrentMeetingInfo({
  success: (res) => console.log(res)
});

ZoomMtg.getWebSDKVersion({
  success: (version) => console.log(version)
});
```

#### Audio/Video Control

```javascript
ZoomMtg.mute({ userId, mute: true });
ZoomMtg.muteAll({ muteAll: true });
ZoomMtg.stopIncomingAudio({ stop: true });
ZoomMtg.mirrorVideo({ mirror: true });
```

#### Chat

```javascript
ZoomMtg.sendChat({
  message: 'Hello!',
  userId: 0  // 0 = everyone
});
```

#### Meeting Control

```javascript
ZoomMtg.leaveMeeting({});
ZoomMtg.endMeeting({});        // host only
ZoomMtg.lockMeeting({ lock: true });
```

#### Host Controls

```javascript
ZoomMtg.makeHost({ userId });
ZoomMtg.makeCoHost({ userId });
ZoomMtg.withdrawCoHost({ userId });
ZoomMtg.expel({ userId });
ZoomMtg.putOnHold({ userId, bHold: true });
ZoomMtg.claimHostWithHostKey({ hostKey: '123456' });
ZoomMtg.reclaimHost({});
ZoomMtg.admitAll({});
```

#### Raise Hand

```javascript
ZoomMtg.raiseHand({ userId });
ZoomMtg.lowerHand({ oderId });
ZoomMtg.lowerAllHands({});
```

#### Spotlight & Pin

```javascript
ZoomMtg.operateSpotlight({ oderId, action: 'add' });    // or 'remove'
ZoomMtg.operatePin({ oderId, action: 'add' });           // or 'remove'
ZoomMtg.allowMultiPin({ allow: true });
```

#### Screen Share

```javascript
ZoomMtg.startScreenShare({});
ZoomMtg.shareSource({ source });  // Electron only
```

#### Recording

```javascript
ZoomMtg.record({ record: true });   // or false
ZoomMtg.showRecordFunction({ show: true });
```

#### Breakout Rooms

```javascript
ZoomMtg.createBreakoutRoom({
  rooms: [{ name: 'Room 1' }, { name: 'Room 2' }]
});
ZoomMtg.openBreakoutRooms({});
ZoomMtg.closeBreakoutRooms({});
ZoomMtg.joinBreakoutRoom({ roomId });
ZoomMtg.leaveBreakoutRoom({});
ZoomMtg.moveUserToBreakoutRoom({ oderId, roomId });
ZoomMtg.getBreakoutRoomStatus({
  success: (res) => console.log(res)
});
```

#### Virtual Background

```javascript
ZoomMtg.isSupportVirtualBackground({
  success: (data) => console.log(data.result.isSupport)
});
ZoomMtg.setVirtualBackground({ imageUrl: '...' });
ZoomMtg.getVirtualBackgroundStatus({
  success: (data) => console.log(data)
});
ZoomMtg.lockVirtualBackground({ lock: true });
```

#### UI Control

```javascript
ZoomMtg.showMeetingHeader({ show: true });
ZoomMtg.showInviteFunction({ show: true });
ZoomMtg.showJoinAudioFunction({ show: true });
ZoomMtg.showCalloutFunction({ show: true });
ZoomMtg.reRender({ lang: 'de-DE' });
```

#### Language

```javascript
ZoomMtg.i18n.load('de-DE');
ZoomMtg.i18n.reload('de-DE');
ZoomMtg.i18n.getCurrentLang();
ZoomMtg.i18n.getAll();
```

---

## Pitfalls

### HARD RULES (do not violate)

1. **`passWord` — capital W.** The join parameter is `passWord`, not `password`. Using the
   wrong casing silently fails the join.

2. **Never pass `undefined` for optional join fields.** If `userEmail`, `tk`, `zak`, or other
   optional fields are `undefined`, the SDK can throw `Cannot read properties of undefined
   (reading 'toString')` and the screen turns black. Only attach keys when they are non-empty
   strings.

3. **Never expose SDK credentials in the browser.** The `signature` (SDK JWT) must be generated
   on a backend. Use placeholder `YOUR_SDK_SECRET` in all example code — never commit real
   secrets.

4. **Do NOT manually create or remove `#zmmtg-root` or `#aria-notify-area`.** The SDK creates
   these DOM elements automatically. Manual manipulation breaks rendering.

5. **Rate limits are enforced — do not exceed:**

   | Method | Limit |
   |--------|-------|
   | `join()` | 10 seconds between calls |
   | `callOut()` | 10 seconds between calls |
   | `mute()` | 1 second between calls |
   | `muteAll()` | 5 seconds between calls |

6. **`defaultView: 'gallery'` requires SharedArrayBuffer.** Without COOP/COEP headers and
   `crossOriginIsolated === true`, gallery view fails silently. Use `defaultView: 'speaker'`
   unless you have fully configured SharedArrayBuffer. Load `../concepts/sharedarraybuffer.md`
   before attempting gallery or multi-speaker view.

7. **`disableCORP` must reflect `crossOriginIsolated` status.** Always set
   `disableCORP: !window.crossOriginIsolated` — hardcoding `false` without cross-origin
   isolation breaks media.

### SPA (React/Next) Overlay Gotcha

If you call `join()` but see a **blank or black area** instead of the meeting UI, the Zoom
UI is likely rendering **behind** your app shell. Ensure `#zmmtg-root` occupies the viewport
and sits above all other fixed elements:

```css
#zmmtg-root {
  position: fixed !important;
  inset: 0 !important;
  z-index: 9999 !important;
}
```

### Join Payload Sanitization Gotcha

If `ZoomMtg.join()` appears to succeed but the screen turns black and the console shows
`Cannot read properties of undefined (reading 'toString')`, you are passing `undefined` for
an optional field. Build the payload object with only required fields first, then
conditionally add optional fields:

```javascript
const joinPayload = {
  signature,
  meetingNumber,
  userName,
  passWord,
  success: (res) => { /* ... */ },
  error: (err) => { /* ... */ }
};

if (userEmail) joinPayload.userEmail = userEmail;
if (tk) joinPayload.tk = tk;
if (zak) joinPayload.zak = zak;

ZoomMtg.join(joinPayload);
```

### CDN Version Mismatch

All CDN script tags must use the **same `{VERSION}`**. Mixing versions of React, Redux, or
the Zoom SDK causes silent failures. Verify version consistency across all `<script>` tags.

### `i18n.load` Must Complete Before `init`

`ZoomMtg.init()` must be called **inside** the `i18n.onLoad()` callback. Calling `init()`
before language resources finish loading causes rendering issues.

---

## Verification

### 1. Check System Requirements

```javascript
console.log('Requirements:', ZoomMtg.checkSystemRequirements());
```

Confirm the output lists your browser as supported.

### 2. Verify SDK Initialization

After `ZoomMtg.init()` success callback fires, check the console for `SDK initialized`.
If the error callback fires, load `../troubleshooting/error-codes.md` and match the error code.

### 3. Verify Join Success

After `ZoomMtg.join()` success callback fires, check the console for `Joined meeting`.
Then verify post-join calls return data:

```javascript
ZoomMtg.getCurrentUser({
  success: (res) => {
    console.log('Current user:', res.result.currentUser);
    // Should print a user object with userId, userName, etc.
  }
});

ZoomMtg.getAttendeeslist({});
// Should return the attendees list object
```

### 4. Verify DOM Elements Exist

Open browser DevTools → Elements and confirm these elements exist (created by the SDK):

- `#zmmtg-root` — main meeting container
- `#aria-notify-area` — accessibility announcements

### 5. Verify Event Listeners Fire

```javascript
ZoomMtg.inMeetingServiceListener('onMeetingStatus', (data) => {
  console.log('Status:', data.status);
  // Expect: 1 (connecting) → 2 (connected)
});
```

### 6. Verify SDK Version

```javascript
ZoomMtg.getWebSDKVersion({
  success: (version) => console.log('SDK version:', version)
});
```

Confirm the version matches your installed NPM package or CDN script version.

### 7. Run the Preflight Checklist

Load `RUNBOOK.md` and follow the 5-minute preflight checklist before deploying to production.

---

## Related Skills

- **Main Web SDK Skill** — `../SKILL.md` — overview of all Web SDK views and shared concepts.
- **Component View** — `../component-view/SKILL.md` — for custom UI layouts with embedded
  Zoom video tiles instead of full-page takeover.
- **Reference Index** — `references/index.md` — complete list of reference docs.
- **Error Codes** — `../troubleshooting/error-codes.md` — SDK error code lookup.
- **Common Issues** — `../troubleshooting/common-issues.md` — black screen, audio, CORS fixes.
- **SharedArrayBuffer Setup** — `../concepts/sharedarraybuffer.md` — COOP/COEP configuration
  for gallery view.
- **Official API Reference** —
  [marketplacefront.zoom.us/sdk/meeting/web/index.html](https://marketplacefront.zoom.us/sdk/meeting/web/index.html)
