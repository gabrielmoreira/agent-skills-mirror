---
name: msix-servicing
description: Design and test MSIX install/update servicing tasks, including preinstall and update deployment tasks, ServicingComplete COM tasks, activation boundaries, migrations, and loose-registration update probes.
---

# MSIX Servicing

Use this guidance when an MSIX app must initialize or migrate state during
deployment or immediately after an update. First choose the execution model;
the similarly named mechanisms have different activation and registration
contracts.

## Choose the mechanism

| Mechanism | Registration and activation | Appropriate use |
|---|---|---|
| `windows.preInstalledConfigTask` | Manifest-declared deployment task implemented as a WinRT component whose public, sealed class implements `IBackgroundTask` | OEM/mobile-operator device-image preinstall work |
| `windows.updateTask` | Manifest-declared deployment task implemented the same way; no runtime registration is required | Post-update migration that must also work when the app has never launched |
| `ServicingComplete` | Runtime-registered background task using a `SystemTrigger`; a packaged Win32 app can bind the registration to a full-trust COM class with `SetTaskEntryPointClsid` | Post-update desktop work after the app has run and registered the task |
| Foreground migration | App startup detects and migrates old state | Required fallback when servicing work is missed, denied, cancelled, or fails |

Microsoft's deployment-task example registers each task class under the
package-level `windows.activatableClass.inProcessServer` extension and names it
from the application-level deployment extension. "In-process server" here is
the WinRT DLL activation model, not permission to point the extension at a
full-trust `com:ExeServer`.
This is an illustrative manifest fragment, not a complete manifest:

```xml
<Package>
  <Extensions>
    <Extension Category="windows.activatableClass.inProcessServer">
      <InProcessServer>
        <Path>Fabrikam.Servicing.dll</Path>
        <ActivatableClass
            ActivatableClassId="Fabrikam.Tasks.PreinstallTask"
            ThreadingModel="MTA" />
        <ActivatableClass
            ActivatableClassId="Fabrikam.Tasks.UpdateTask"
            ThreadingModel="MTA" />
      </InProcessServer>
    </Extension>
  </Extensions>
  <Applications>
    <Application>
      <Extensions>
        <Extension Category="windows.preInstalledConfigTask"
                   EntryPoint="Fabrikam.Tasks.PreinstallTask" />
        <Extension Category="windows.updateTask"
                   EntryPoint="Fabrikam.Tasks.UpdateTask" />
      </Extensions>
    </Application>
  </Applications>
</Package>
```

Apply these deployment-task constraints:

- Declare at most one preinstall task and one update task per app.
- Use a Windows Runtime component and implement `IBackgroundTask.Run`. Take a
  deferral for asynchronous work, observe cancellation, and always complete the
  deferral.
- Do not make the two tasks depend on each other. They run after deployment is
  committed; failure does not roll back deployment, is not retried, and is not
  resumed after reboot.
- Do not redirect either deployment extension to a `com:ExeServer` or assume
  that `runFullTrust` changes its activation model.

**Diagnostic qualification:** `0x80000020` has been observed when a deployment
task was incorrectly routed to a full-trust EXE. Public Microsoft documentation
shows the supported WinRT in-process-server shape, but does not document that
HRESULT as a definitive signature of this mismatch. Treat it as a clue: inspect
the manifest activation model and collect deployment/activation diagnostics
before assigning causality.

## Full-trust ServicingComplete path

For a packaged Win32 app, declare the COM local server and class with
`com:Extension Category="windows.comServer"`, implement `IBackgroundTask`, and
register the task at runtime. The essential registration shape is:

The server must also implement/register its COM class factory and handle the
documented activation/lifetime path; the manifest and builder alone do not host
the object. Use the matching packaged-Win32 sample for that infrastructure.
The GUID below is fictional and must match the actual registered COM class.

```csharp
// Snippet only: also handle existing registrations and Register exceptions.
BackgroundAccessStatus access =
    await BackgroundExecutionManager.RequestAccessAsync();
if (access != BackgroundAccessStatus.AlwaysAllowed &&
    access != BackgroundAccessStatus.AllowedSubjectToSystemPolicy)
{
    throw new InvalidOperationException($"Background access denied: {access}");
}

var builder = new BackgroundTaskBuilder
{
    Name = "Fabrikam.ServicingComplete"
};
builder.SetTaskEntryPointClsid(new Guid(
    "11111111-2222-3333-4444-555555555555"));
builder.SetTrigger(new SystemTrigger(
    SystemTriggerType.ServicingComplete, false));
BackgroundTaskRegistration registration = builder.Register();
```

Use the `Windows.ApplicationModel.Background` APIs only on supported packaged
Win32 targets; `SetTaskEntryPointClsid` starts with Windows 10, version 2004.
For Windows App SDK desktop apps, prefer its
`Microsoft.Windows.ApplicationModel.Background.BackgroundTaskBuilder`, which
is designed to register full-trust COM components, and follow the matching SDK
sample and manifest contract.

The manifest's COM declaration makes the class activatable; it does not create
the background-task registration. Therefore the foreground app must run and
successfully register the `ServicingComplete` trigger before an update can fire
it. Enumerate registrations by stable name before registering, and replace a
stale registration deliberately rather than accumulating duplicates.

Full trust means desktop medium-integrity access, not elevation. It does not
grant administrator rights, bypass background policy, or guarantee execution.
Handle denied background access, resource limits, cancellation, registration
exceptions, and unavailable APIs. Never use a servicing task as the only path
to critical state repair.

## Fires-when matrix

| Scenario | Expected result and confidence |
|---|---|
| Package provisioned in an OEM/MO device image | `preInstalledConfigTask` is the documented mechanism. Validate on the real provisioning path. |
| Ordinary first per-user install | Microsoft documents preinstall tasks for image preinstallation, not ordinary `Add-AppxPackage`/Store installation. The issue reports that neither deployment hook fires on a fresh user install; treat this as an empirical channel/OS test, not a universal contract. |
| Update of an already installed app that has never launched | `updateTask` is documented to run without prior app launch or runtime registration. Microsoft explicitly documents Store updates and legacy package-path combinations; verify other channels rather than claiming "any channel." |
| Update after successful runtime registration | `ServicingComplete` can run the registered task after servicing. A first update before registration cannot use this path. |
| Same-version loose re-registration | Negative control: do not assume this constitutes an update or fires `updateTask`. |
| Deployment task points to a COM EXE | Unsupported shape. Expect activation failure; `0x80000020` is an observed, not contractually guaranteed, symptom. |

## Make migrations safe

- Store an explicit schema/version checkpoint in durable app data. Compare the
  current state with the target package version before changing anything.
- Make each step idempotent and monotonic. Re-entry after cancellation must
  detect completed steps and must not duplicate records, ACLs, registrations,
  or external side effects.
- Commit data and the checkpoint atomically where possible. Write the checkpoint
  only after the corresponding migration succeeds.
- Keep work bounded and cancellation-aware. Record start, completion, failure,
  source version, target version, task kind, and an invocation ID without
  secrets or personal data.
- Do not write package installation files. Keep per-user state in supported app
  data. Do not attempt machine-wide mutation from an AppContainer task, and do
  not mistake a full-trust COM task for an elevated installer.
- Run the same migration coordinator from foreground startup as a repair path.
  Serialize it so startup and a servicing task cannot migrate concurrently.

## Verify with a disposable fictional app

These are test instructions, not permission to install, provision, register, or
run anything. Execute them only when the user explicitly authorizes system
changes, and use a disposable VM or test account.

1. Build a self-contained test layout for fictional
   `Fabrikam.ServicingProbe`; keep identity, publisher, architecture,
   dependencies, and entry points constant across revisions.
2. Have each task append a JSON record under its package-local test data with
   task kind, invocation ID, package version, timestamps, cancellation/result,
   and migration checkpoint. Also make one harmless, queryable schema change.
3. Start with manifest version `1.0.0.0`. On Windows 10 version 1809 or later
   with Developer Mode enabled, register the loose layout locally:

   ```powershell
   # Test command; do not run without explicit approval.
   $manifestPath = 'C:\ServicingLab\Fabrikam.ServicingProbe\AppxManifest.xml'
   Add-AppxPackage -Register $manifestPath
   ```

4. Without launching the app, change only the manifest version to `1.0.1.0`
   and re-run the same registration command. Microsoft documents version-bump
   deployment as the UpdateTask test technique and loose registration as a
   development feature, but does not explicitly guarantee their combination.
   Treat a fired task as empirical evidence for that OS build and layout.
5. Inspect the installed package version, the task's start/completion records,
   the migrated schema, and relevant AppX deployment/background-task
   diagnostics. Absence of a marker is not proof of successful non-execution;
   correlate it with activation and deployment evidence.
6. Run the matrix and retain its evidence:

   | Case | Setup | Expected evidence |
   |---|---|---|
   | Fresh per-user install | Register `1.0.0.0` without prior family registration | No migration expected from an update; record whether either deployment task appears |
   | Update before launch | Register `1.0.0.0`, do not launch, then register `1.0.1.0` | One completed `UpdateTask` marker and one schema transition; no `ServicingComplete` |
   | Update after launch | Launch once to register COM task, then update to `1.0.2.0` | `UpdateTask` plus registered `ServicingComplete`, without duplicate migration effects |
   | Same version | Re-register `1.0.2.0` | Negative control: no new update marker or schema transition |
   | Cancellation/failure | Inject cancellation or a failure before checkpoint commit | No success checkpoint; foreground repair safely completes once |
   | Provisioned install | Provision a clean disposable image through a supported OEM path | One `PreinstallTask` marker; a per-user loose registration is not a substitute |

7. Finally validate a signed packaged update through every supported production
   channel. Loose registration is development-only and cannot prove Store,
   enterprise-management, or provisioning behavior.

## Public references

- [Preinstall tasks](https://learn.microsoft.com/windows-hardware/customize/preinstall/preinstall-tasks); [UpdateTask](https://learn.microsoft.com/windows/uwp/launch-resume/run-a-background-task-during-updatetask)
- [Win32 COM background task](https://learn.microsoft.com/windows/uwp/launch-resume/create-and-register-a-winmain-background-task); [`ServicingComplete`](https://learn.microsoft.com/uwp/api/windows.applicationmodel.background.systemtriggertype)
- [Windows App SDK background tasks](https://learn.microsoft.com/windows/apps/windows-app-sdk/applifecycle/background-tasks); [background-task guidelines](https://learn.microsoft.com/windows/uwp/launch-resume/guidelines-for-background-tasks)
- [Loose file registration](https://learn.microsoft.com/windows/apps/develop/testing/loose-file-registration); [`Add-AppxPackage`](https://learn.microsoft.com/powershell/module/appx/add-appxpackage)
