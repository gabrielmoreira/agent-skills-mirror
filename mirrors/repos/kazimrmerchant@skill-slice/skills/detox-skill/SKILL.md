---
name: detox-skill
description: "Writes and debugs Detox gray-box E2E tests for React Native (Jest-circus, .detoxrc.js, testID matchers, device sync). Use when authoring, running, configuring, or fixing flaky Detox tests on iOS simulators or Android emulators. Not for web or hybrid browser E2E (browser-automation) and not for YAML-first Maestro suites."
version: 1.0.1
domain: Developer-Tools
risk: safe
last_verified: '2026-05-30'
self_updating: true
---

## When to Use

Use when:
- Authoring E2E test suites for React Native mobile applications.
- Configuring simulator or emulator settings for local and remote device execution.
- Fixing flaky tests by leveraging Detox's internal sync engine rather than manual timeouts.

## Prerequisites

- **Node runtime**: Requires Node.js version 18 or above.
- **macOS Dependencies**: iOS testing requires homebrew package `applesimutils` to handle simulator permissions dynamically.
- **Framework Compatibility**: Fully compatible with React Native's New Architecture (TurboModules, Fabric renderer) up to React Native 0.84+.
- **Legacy compatibility**: Covers Detox versions 20.x through 22.x.
- **Test Runner**: Configured to run with Jest-circus as the underlying test runner environment.

## Procedure

1. **Initialize E2E Suite Structure**
   Ensure the following directory structure exists in your codebase:
   ```text
   e2e/
    .detoxrc.js
    jest.config.js
    init.js
    authentication.test.js
   ```

2. **Configure Detox (`.detoxrc.js`)**
   Define app binaries, build commands, and target devices.
   ```javascript
   module.exports = {
     testRunner: { args: { config: 'e2e/jest.config.js' } },
     apps: {
       'ios.release': {
         type: 'ios.app',
         binaryPath: 'ios/build/Build/Products/Release-iphonesimulator/MyApp.app',
         build: 'xcodebuild -workspace ios/MyApp.xcworkspace -scheme MyApp -configuration Release -sdk iphonesimulator -derivedDataPath ios/build',
       },
       'android.release': {
         type: 'android.apk',
         binaryPath: 'android/app/build/outputs/apk/release/app-release.apk',
         build: 'cd android && ./gradlew assembleRelease assembleAndroidTest -DtestBuildType=release',
       },
     },
     devices: {
       simulator: { type: 'ios.simulator', device: { type: 'iPhone 15' } },
       emulator: { type: 'android.emulator', device: { avdName: 'Pixel_6_API_33' } },
     },
     configurations: {
       'ios.sim.release': { device: 'simulator', app: 'ios.release' },
       'android.emu.release': { device: 'emulator', app: 'android.release' },
     },
   };
   ```

3. **Write Tests Using Core Patterns**
   Use `describe`, `beforeAll`, and `beforeEach` blocks. Launch the app in `beforeAll` and use `device.reloadReactNative()` in `beforeEach` to reset state.
   ```javascript
   describe('Authentication Flow', () => {
     beforeAll(async () => {
       await device.launchApp();
     });

     beforeEach(async () => {
       await device.reloadReactNative();
     });

     it('logs in successfully with valid credentials', async () => {
       await element(by.id('emailInput')).typeText('user@test.com');
       await element(by.id('passwordInput')).typeText('password123');
       await element(by.id('loginButton')).tap();
       await expect(element(by.id('dashboardTitle'))).toBeVisible();
     });
   });
   ```

4. **Use Selector Matchers**
   Always assign a unique, descriptive `testID` to all components requiring user interaction. Prefer `by.id('testID')` for stability.
   ```javascript
   element(by.id('uniqueId'))                    // Select by testID prop (Preferred)
   element(by.text('Submit'))                    // Select by visible text
   element(by.label('Submit Button'))             // Select by accessibility label
   element(by.type('RCTTextInput'))              // Select by native component class type

   // Combined Hierarchical Matchers
   element(by.id('list').withDescendant(by.text('Target Item')))
   element(by.id('item').withAncestor(by.id('parentContainer')))

   // Index Selection (when encountering duplicate matches)
   element(by.text('Delete')).atIndex(0)
   ```

5. **Perform Common Actions**
   ```javascript
   await element(by.id('btn')).tap();
   await element(by.id('btn')).longPress();
   await element(by.id('input')).typeText('text to enter');
   await element(by.id('input')).replaceText('replacement text');
   await element(by.id('input')).clearText();
   await element(by.id('scrollView')).scroll(200, 'down');
   await element(by.id('scrollView')).scrollTo('bottom');
   await element(by.id('item')).swipe('left', 'fast');
   await element(by.id('input')).tapReturnKey();
   ```

6. **Apply Expectations**
   ```javascript
   await expect(element(by.id('title'))).toBeVisible();
   await expect(element(by.id('title'))).not.toBeVisible();
   await expect(element(by.id('title'))).toExist();
   await expect(element(by.id('title'))).toHaveText('Welcome');
   await expect(element(by.id('toggle'))).toHaveToggleValue(true);
   await expect(element(by.id('input'))).toHaveValue('input value');
   ```

7. **Control Device State**
   ```javascript
   await device.launchApp({ newInstance: true });
   await device.reloadReactNative();
   await device.sendToHome();
   await device.terminateApp();
   await device.installApp();
   await device.shake();
   await device.setLocation(37.7749, -122.4194);
   await device.setURLBlacklist(['.*cdn.example.*']); // Block network endpoints from halting sync
   ```

## Pitfalls

- **Manual Sleep/Timeouts**: Do not inject manual sleep or `waitFor().withTimeout()` globally. Trust the Detox automatic synchronization engine, which watches the React Native bridge and halts actions until operations complete.
- **Missing `testID` Props**: Do not omit `testID` props and rely on text matches. Define explicit `testID` properties on interactive targets to avoid breakage from localization or UI styling adjustments.
- **Relaunching App in `beforeEach`**: Do not run `device.launchApp()` in `beforeEach()` blocks. Use `device.reloadReactNative()` to reset state between tests to decrease test runner cycle duration significantly.
- **Network Synchronization Hangs**: Add network domains to the blacklists (`device.setURLBlacklist()`) for analytical, logging, or third-party CDN domains that are not critical for functional verification to prevent synchronization hangs.
- **Wrong Build Profile**: Do not use `Release` profiles when writing tests interactively. Build with `Debug` profiles for writing tests. Execute `Release` builds on CI pipelines to catch bundle-dependent bugs and optimize run speed.

## Verification

1. **Verify Build Configuration**: Ensure the app builds successfully for the target platform.
   ```bash
   npx detox build -c ios.sim.release
   ```
2. **Run Tests**: Execute the test suite against the configured simulator/emulator.
   ```bash
   npx detox test -c ios.sim.release
   ```
3. **Check Test Output**: Verify that tests pass and expectations are met. The output should show `PASS` for each test suite without synchronization timeouts.

## Related skills

- `browser-automation`: Route to this skill if target platforms include hybrid web apps or standard web applications instead of React Native.
- `maestro`: Route to Maestro if working with cross-platform codebases that require quick YAML test suites with minimal native environment setup. Use Detox for native testing scenarios needing white-box access, React Native bridge monitoring, mock servers, or mock location injections.
