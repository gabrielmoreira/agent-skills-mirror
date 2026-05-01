---
name: upgrading-expo
description: Guidelines for upgrading Expo SDK versions and fixing dependency issues
version: 1.0.0
license: MIT
---

## References

- ./references/new-architecture.md -- SDK +53: New Architecture migration guide
- ./references/react-19.md -- SDK +54: React 19 changes (useContext → use, Context.Provider → Context, forwardRef removal)
- ./references/react-compiler.md -- SDK +54: React Compiler setup and migration guide
- ./references/native-tabs.md -- SDK +55: Native tabs changes (Icon/Label/Badge now accessed via NativeTabs.Trigger.\*)
- ./references/expo-av-to-audio.md -- Migrate audio playback and recording from expo-av to expo-audio
- ./references/expo-av-to-video.md -- Migrate video playback from expo-av to expo-video

## Beta/Preview Releases

Beta versions use `.preview` suffix (e.g., `55.0.0-preview.2`), published under `@next` tag.

Check if latest is beta: https://exp.host/--/api/v2/versions (look for `-preview` in `expoVersion`)

```bash
npx expo install expo@next --fix  # install beta
```

## Step-by-Step Upgrade Process

1. Upgrade Expo and dependencies

```bash
npx expo install expo@latest
npx expo install --fix
```

2. Run diagnostics: `npx expo-doctor`

3. Clear caches and reinstall

```bash
npx expo export -p ios --clear
rm -rf node_modules .expo
watchman watch-del-all
```

## Breaking Changes Checklist

- Check for removed APIs in release notes
- Update import paths for moved modules
- Review native module changes requiring prebuild
- Test all camera, audio, and video features
- Verify navigation still works correctly

## Prebuild for Native Changes

If upgrading requires native changes:

```bash
npx expo prebuild --clean
```

This regenerates the `ios` and `android` directories. Ensure the project is not a bare workflow app before running this command.

## Clear caches for bare workflow

- Clear the cocoapods cache for iOS: `cd ios && pod install --repo-update`
- Clear derived data for Xcode: `npx expo run:ios --no-build-cache`
- Clear the Gradle cache for Android: `cd android && ./gradlew clean`

## Housekeeping

- Review release notes for the target SDK version at https://expo.dev/changelog
- If using Expo SDK 54 or later, ensure react-native-worklets is installed — this is required for react-native-reanimated to work.
- Enable React Compiler in SDK 54+ by adding `"experiments": { "reactCompiler": true }` to app.json — it's stable and recommended
- Delete sdkVersion from `app.json` to let Expo manage it automatically
- Remove implicit packages from `package.json`: `@babel/core`, `babel-preset-expo`, `expo-constants`.
- If the babel.config.js only contains 'babel-preset-expo', delete the file
- If the metro.config.js only contains expo defaults, delete the file

## Deprecated Packages

| Old Package          | Replacement                                          |
| -------------------- | ---------------------------------------------------- |
| `expo-av`            | `expo-audio` and `expo-video`                        |
| `expo-permissions`   | Individual package permission APIs                   |
| `@expo/vector-icons` | `expo-symbols` (for SF Symbols)                      |
| `AsyncStorage`       | `expo-sqlite/localStorage/install`                   |
| `expo-app-loading`   | `expo-splash-screen`                                 |
| expo-linear-gradient | experimental_backgroundImage + CSS gradients in View |

When migrating deprecated packages, update all code usage before removing the old package. For expo-av, consult the migration references to convert Audio.Sound to useAudioPlayer, Audio.Recording to useAudioRecorder, and Video components to VideoView with useVideoPlayer.

## expo.install.exclude

Check if package.json has excluded packages:

```json
{
  "expo": { "install": { "exclude": ["react-native-reanimated"] } }
}
```

Exclusions are often workarounds that may no longer be needed after upgrading. Review each one.
## Removing patches

Check if there are any outdated patches in the `patches/` directory. Remove them if they are no longer needed.

## Postcss

- `autoprefixer` isn't needed in SDK +53. Remove it from dependencies and check `postcss.config.js` or `postcss.config.mjs` to remove it from the plugins list.
- Use `postcss.config.mjs` in SDK +53.

## Metro

Remove redundant metro config options:

- resolver.unstable_enablePackageExports is enabled by default in SDK +53.
- `experimentalImportSupport` is enabled by default in SDK +54.
- `EXPO_USE_FAST_RESOLVER=1` is removed in SDK +54.
- cjs and mjs extensions are supported by default in SDK +50.
- Expo webpack is deprecated, migrate to [Expo Router and Metro web](https://docs.expo.dev/router/migrate/from-expo-webpack/).

## Hermes engine v1

Since SDK 55, users can opt-in to use Hermes engine v1 for improved runtime performance. This requires setting `useHermesV1: true` in the `expo-build-properties` config plugin, and may require a specific version of the `hermes-compiler` npm package. Hermes v1 will become a default in some future SDK release.

## New Architecture

The new architecture is enabled by default, the app.json field `"newArchEnabled": true` is no longer needed as it's the default. Expo Go only supports the new architecture as of SDK +53.

# Upgrading Expo


## Overview

Upgrade Expo SDK versions safely, handling breaking changes, dependencies, and configuration updates.


## When to Use This Skill

Use this skill when you need to upgrade Expo SDK versions.

Use this skill when:
- Upgrading to a new Expo SDK version
- Handling breaking changes between SDK versions
- Updating dependencies for compatibility
- Migrating deprecated APIs to new versions
- Preparing apps for new Expo features


## Instructions

This skill guides you through upgrading Expo SDK versions:

1. **Pre-Upgrade Planning**: Review release notes and breaking changes
2. **Dependency Updates**: Update packages for SDK compatibility
3. **Configuration Migration**: Update app.json and configuration files
4. **Code Updates**: Migrate deprecated APIs to new versions
5. **Testing**: Verify app functionality after upgrade


## Upgrade Process


### 1. Pre-Upgrade Checklist

- Review Expo SDK release notes
- Identify breaking changes affecting your app
- Check compatibility of third-party packages
- Backup current project state
- Create a feature branch for the upgrade


### 2. Update Expo SDK

```bash

# Update Expo CLI
npm install -g expo-cli@latest


# Upgrade Expo SDK
npx expo install expo@latest


# Update all Expo packages
npx expo install --fix
```


### 3. Handle Breaking Changes

- Review migration guides for breaking changes
- Update deprecated API calls
- Modify configuration files as needed
- Update native dependencies if required
- Test affected features thoroughly


### 4. Update Dependencies

```bash

# Check for outdated packages
npx expo-doctor


# Update packages to compatible versions
npx expo install --fix


# Verify compatibility
npx expo-doctor
```


### 5. Testing

- Test core app functionality
- Verify native modules work correctly
- Check for runtime errors
- Test on both iOS and Android
- Verify app store builds still work


## Common Issues


### Dependency Conflicts

- Use `expo install` instead of `npm install` for Expo packages
- Check package compatibility with new SDK version
- Resolve peer dependency warnings


### Configuration Changes

- Update `app.json` for new SDK requirements
- Migrate deprecated configuration options
- Update native configuration files if needed


### Breaking API Changes

- Review API migration guides
- Update code to use new APIs
- Test affected features after changes


## Best Practices

- Always upgrade in a feature branch
- Test thoroughly before merging
- Review release notes carefully
- Update dependencies incrementally
- Keep Expo CLI updated
- Use `expo-doctor` to verify setup


## Resources

For more information, see the [source repository](https://github.com/expo/skills/tree/main/plugins/upgrading-expo).

