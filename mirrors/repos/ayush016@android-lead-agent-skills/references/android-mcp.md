# Android MCP Integration Guide

## Mental Model

**MCP is your eyes on the device. Code is your hands in the codebase.**

You write composables and logic in files. Android MCP shows you what those files produce when they run on real hardware. The workflow loops: write → build → install → screenshot → inspect → refine. MCP closes the feedback loop that text-only development leaves open.

Without MCP you are building blind — you're guessing that your 16dp padding works, that your animation fires at the right moment, that your shared element transition doesn't clip incorrectly. With MCP you verify.

---

## Available MCP Capabilities

| Action | What It Does |
|--------|-------------|
| `adb install` / `adb push` | Install APK or push files to device |
| `adb shell am start` | Launch activity or deep-link directly |
| `adb shell input tap / swipe` | Simulate touch events |
| `adb shell screencap` | Capture screenshot to device storage |
| `adb pull` | Download screenshot or file to workstation |
| `adb shell uiautomator dump` | Dump accessibility/UI hierarchy to XML |
| `adb logcat` | Stream or filter device logs |
| `adb shell dumpsys activity` | Inspect running activities, back stack, task state |
| `adb shell dumpsys gfxinfo` | Frame timing data — jank detection |
| `adb shell wm size` | Change display resolution for responsive testing |
| `adb shell wm density` | Change display density |

---

## Screenshot-Driven UI Review Workflow

Use this loop whenever you add or change a screen:

```bash
# 1. Build debug APK
./gradlew :app:assembleDebug

# 2. Install on connected device/emulator
adb install -r app/build/outputs/apk/debug/app-debug.apk

# 3. Launch the target screen via deep link or activity
adb shell am start -n com.example.app/.MainActivity \
    --es "destination" "profile/123"

# 4. Capture screenshot
adb shell screencap /sdcard/screen.png
adb pull /sdcard/screen.png /tmp/review/screen.png

# 5. Inspect the screenshot
# - Does it match the design?
# - Are spacing values correct (4dp multiples)?
# - Does the typography hierarchy read clearly?
# - Is the color palette using design system roles?

# 6. Refine code and repeat from step 1
```

For systematic review against the ui-excellence-checklist.md, capture screenshots in:
- Light theme (`adb shell cmd uimode night no`)
- Dark theme (`adb shell cmd uimode night yes`)
- Large font (`adb shell settings put system font_scale 1.5`)
- RTL (`adb shell setprop persist.demo.forcertl 1 && adb reboot`)

---

## Log-Driven Debugging Workflow

```bash
# Filter logs by your app's tag
adb logcat -v time AppTag:D *:S

# Filter all ERROR and above
adb logcat *:E

# Capture a window of logs around a crash
adb logcat -d > /tmp/crash.log  # dump current buffer to file

# Watch for a specific tag in real-time
adb logcat | grep "ViewModel"

# Clear log buffer before reproducing a bug
adb logcat -c && adb logcat -v time AppTag:V *:S
```

Tag your own logs consistently:

```kotlin
private const val TAG = "ProfileViewModel"
Log.d(TAG, "Loading profile id=$id")
Log.e(TAG, "Failed to load profile", exception)
```

---

## UI Hierarchy Inspection

The UI hierarchy dump shows the full accessibility/semantic tree — composable sizes, content descriptions, focus order, and roles. Use it to verify:
- Shared element keys are on the right composables
- Content descriptions exist on images
- Custom components declare the correct semantic role
- Focus traversal order makes sense for screen-reader users

```bash
# Dump UI hierarchy to device
adb shell uiautomator dump /sdcard/ui.xml

# Pull to workstation
adb pull /sdcard/ui.xml /tmp/ui.xml

# Search for a specific composable by content description
cat /tmp/ui.xml | grep -A 3 "articleTitle"
```

In Compose, verify your semantic tree in tests:

```kotlin
composeTestRule
    .onNode(hasContentDescription("Back"))
    .assertIsDisplayed()
    .assertHasClickAction()
```

---

## Animation Debugging

### Frame Timing

```bash
# Reset gfxinfo counters
adb shell dumpsys gfxinfo com.example.app reset

# Trigger the animation (screenshot, swipe, etc.)
adb shell input tap 540 960

# Read frame timing
adb shell dumpsys gfxinfo com.example.app

# Look for:
# "Janky frames" — frames that took > 16ms
# "50th/90th/95th/99th percentile" — frame duration in ms
# A 90th percentile under 16ms = silky smooth
```

### Snapshot-Based Transition Review

Capture frames at intervals during a transition to verify the animation is correct at each stage:

```bash
# Trigger navigation and immediately capture multiple frames
adb shell input tap 200 400  # tap list item
sleep 0.1 && adb shell screencap /sdcard/frame1.png && adb pull /sdcard/frame1.png /tmp/frame1.png
sleep 0.1 && adb shell screencap /sdcard/frame2.png && adb pull /sdcard/frame2.png /tmp/frame2.png
sleep 0.1 && adb shell screencap /sdcard/frame3.png && adb pull /sdcard/frame3.png /tmp/frame3.png
sleep 0.2 && adb shell screencap /sdcard/frame4.png && adb pull /sdcard/frame4.png /tmp/frame4.png
```

Review the frame sequence to verify:
- Shared element starts from the correct position
- Clipping shape is correct throughout
- Z-ordering is correct (correct element on top)
- Fade timing feels right

---

## Responsive Testing

```bash
# Simulate tablet (1280x800 @ 240dpi)
adb shell wm size 1280x800
adb shell wm density 240

# Simulate phone (360x800 @ 420dpi)
adb shell wm size 1080x2400
adb shell wm density 420

# Reset to device default
adb shell wm size reset
adb shell wm density reset

# Test folded/unfolded states (on compatible emulator)
adb shell cmd device_state state 1  # folded
adb shell cmd device_state state 2  # unfolded
```

---

## Feature Build Workflow — MCP Command Map

| Workflow Step | MCP Command |
|---|---|
| Step 7: Verify composable renders correctly | `screencap` + `pull` + visual review |
| Step 8: Verify shared element transition | Frame-interval screenshot sequence |
| Step 9: Verify dark/light theme | `cmd uimode night yes/no` + screenshot |
| Step 10: Verify edge-to-edge & insets | Screenshot + check status/nav bar areas |
| Step 11: Verify accessibility | `uiautomator dump` + review content descriptions |
| Step 12: Detect jank | `gfxinfo reset` → interact → `gfxinfo` |
| Step 13: UI excellence review | Systematic screenshot against checklist items |
| Step 14: Large font & RTL | `font_scale 1.5` + `forcertl 1` + screenshots |

---

## Logcat Patterns for Common Issues

```bash
# Recomposition debugging (Compose internals)
adb logcat -v time | grep "Recomposing\|recomposition"

# Navigation issues
adb logcat | grep "NavController\|navigation"

# Shared element transition issues  
adb logcat | grep "SharedElement\|SharedTransition"

# Compose rendering errors
adb logcat | grep -E "AndroidRuntime|FATAL|compose"

# Memory pressure
adb logcat | grep "OnLowMemory\|GC\|OutOfMemory"
```
