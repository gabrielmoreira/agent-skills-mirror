# SwiftlyS2 Thread Sensitivity Checklist

Official docs sections:
- `Thread Safety`
- `Using attributes`
- `Menus`

> Use this to review thread-sensitive APIs, async-context patterns, reasons for scheduler usage, and player / entity lifecycle risks.

## 1. Determine first which context the current code is running in

- Is it a command entry point, menu callback, event callback, hook, worker, or delayed task?
- Is the current code already in an `async` / `await` chain?
- Is it running on a high-frequency hot path?
- Could it cross threads, frames, maps, or disconnect / reconnect boundaries?

## 2. In async contexts, first check whether an Async API already exists

Prefer using:
- `PrintToChatAsync`
- `PrintToConsoleAsync`
- `ReplyAsync`
- `EmitSoundFilterAsync`
- `SetModelAsync`
- `AcceptInputAsync`
- `KickAsync`
- `SwitchTeamAsync`

Hard rules:
- **If an Async API already exists and the current code is already in an async context, prefer using the Async API directly.**
- **Do not treat `NextTick` / `NextWorldUpdate` as the default solution for thread-sensitivity problems.**

## 3. Known high-priority thread-sensitive method list

- `IPlayer.Send* / Kick / ChangeTeam / SwitchTeam / TakeDamage / Teleport / ExecuteCommand`
- `IGameEventService.Fire*`
- `IEngineService.ExecuteCommand*`
- `CEntityInstance.AcceptInput / AddEntityIOEvent / DispatchSpawn / Despawn`
- `ICommandContext.Reply`
- `CBaseModelEntity.SetModel / SetBodygroupByName`
- `CCSPlayerController.Respawn`
- `CPlayer_ItemServices.* / CPlayer_WeaponServices.*`

## 4. Menu callbacks are a high-risk area

- `ButtonMenuOption.Click`
- `ToggleMenuOption.ValueChanged`
- `ChoiceMenuOption.ValueChanged`
- `SliderMenuOption.ValueChanged`
- `SubmenuMenuOption(async () => ...)`

Review questions:
- Do callbacks prefer `Async` APIs internally?
- Is `args.Player.Valid()` rechecked after crossing `await` boundaries?
- Are blocking IO, `.Wait()`, and `.Result` avoided inside callbacks?

## 5. Player / entity lifecycle review

- `player != null && player.Valid()`
- `player.PlayerPawn != null`
- `pawn.Valid()` / `pawn.IsValid`
- whether the map has already changed
- whether the current runtime state still belongs to the current session
- whether long-lived entity references across ticks / delays were converted to `CHandle<T>`
