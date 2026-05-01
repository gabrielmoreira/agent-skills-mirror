# Game UI Checklist

Use this checklist for HUDs, menus, overlays, and game interface flows.

## Player Decisions

- The UI emphasizes what the player needs next, not every available statistic.
- Urgent information is readable in peripheral vision where needed.
- Secondary information remains accessible without competing with moment-to-moment play.
- Warnings arrive early enough for the player to respond.

## Interaction

- Mouse, keyboard, controller, and touch behavior are complete for the target platforms.
- Focus order, default selection, cancel/back, confirm, tabs, wrap, and disabled states are explicit.
- Repeated actions are fast and do not require needless confirmation.
- Destructive or irreversible actions communicate consequences.

## States

- Empty, loading, disabled, locked, selected, hover, pressed, focused, error, warning, success, and cooldown states exist where relevant.
- Text fits at target resolutions and remains safe for localization.
- UI respects safe areas, split-screen constraints, and platform overlays.
- Pause, disconnect, focus loss, and modal stacking are handled.

## Accessibility

- Contrast, font size, icon labels, remapping, subtitle options, colorblind-safe signals, and motion reduction are considered.
- Color is not the only signal for critical state.
- Audio-only cues have visual alternatives when they affect play.

## Visual Quality

- Materials, typography, icons, and motion match the game's genre and world.
- HUD elements do not hide important gameplay space.
- Menus feel like part of the game, not a disconnected web app, unless that is the intended fiction.
