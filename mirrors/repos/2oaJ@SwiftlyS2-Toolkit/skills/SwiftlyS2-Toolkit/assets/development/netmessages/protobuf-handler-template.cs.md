# SwiftlyS2 Protobuf / NetMessage Template

Official docs sections:
- `Network Messages`
- `Thread Safety`

Suitable for: `CSGOUserCmdPB`, typed netmessages, user-message hooks, and command snapshot sampling.

## Usage principles

- Treat protobuf / usercmd reads and writes as main-thread-sensitive by default.
- Before entering async work, prefer converting them into plain C# snapshots.
- Do not pass protobuf handles or entity handles directly across threads.
- Prefer typed protobuf / typed netmessage APIs over hard-coded message IDs.

## Example skeleton

```csharp
using SwiftlyS2.Shared.Protobufs;

namespace MyNamespace;

public partial class MyPlugin
{
    public void HandleUserCmd(ulong steamId, CSGOUserCmdPB userCmd)
    {
        var snapshot = new UserCmdSnapshot(
            steamId,
            userCmd.Buttons,
            userCmd.Viewangles?.X ?? 0f,
            userCmd.Viewangles?.Y ?? 0f,
            userCmd.ForwardMove,
            userCmd.SideMove);

        _commandRecordingWorker.Enqueue(snapshot);
    }

    public void SendCustomMessage()
    {
        using var message = Core.NetMessage.Create<MyTypedMessage>();
        message.SetIntValue(1);
        message.SetStringValue("payload");
        message.Recipients.AddAllPlayers();
        message.Send();
    }
}

public sealed record UserCmdSnapshot(
    ulong SteamId,
    int Buttons,
    float Pitch,
    float Yaw,
    float ForwardMove,
    float SideMove);
```

## Checklist

- Is protobuf being read and written on the main thread?
- Is snapshot conversion completed before entering async work?
- Are protobuf handles prevented from crossing threads?
- Are typed APIs preferred?
- Has usercmd / subtick timing consistency been considered?
