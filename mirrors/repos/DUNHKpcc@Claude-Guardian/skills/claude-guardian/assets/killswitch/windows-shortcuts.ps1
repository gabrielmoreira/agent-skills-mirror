param(
    [Parameter(Mandatory=$true)][string]$Config,
    [string]$OutputDirectory = [Environment]::GetFolderPath('Desktop')
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'windows-desktop.ps1') -Config $Config
$configPath = (Resolve-Path -LiteralPath $Config).Path
$null = Read-DesktopConfig $configPath On
$entry = Join-Path $PSScriptRoot 'windows-desktop.ps1'
$icon = Join-Path $PSScriptRoot 'icon.ico'
foreach ($path in @($entry,$icon,(Join-Path $PSScriptRoot 'windows-switch.ps1'))) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "缺少随包资产：$path" }
}
$items = @(@{Action='On';Name='开启保护（限制直连）'},@{Action='Off';Name='关闭保护（恢复联网）'})
foreach ($item in $items) {
    if (Test-Path -LiteralPath (Join-Path $OutputDirectory ($item.Name + '.lnk'))) { throw '同名快捷方式已存在，请先核对，避免覆盖已有入口。' }
}
if (-not (Test-Path -LiteralPath $OutputDirectory)) { $null = New-Item -ItemType Directory -Path $OutputDirectory }
$directory = Get-Item -LiteralPath $OutputDirectory
# WScript.Shell loses Chinese paths on non-Chinese Windows; use the Unicode Shell API.
if (-not ('GuardianShortcut' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using System.Runtime.InteropServices.ComTypes;
[ComImport, Guid("000214F9-0000-0000-C000-000000000046"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IGuardianShellLinkW {
    void GetPath(IntPtr path, int count, IntPtr data, uint flags);
    void GetIDList(out IntPtr id);
    void SetIDList(IntPtr id);
    void GetDescription(IntPtr text, int count);
    void SetDescription([MarshalAs(UnmanagedType.LPWStr)] string text);
    void GetWorkingDirectory(IntPtr path, int count);
    void SetWorkingDirectory([MarshalAs(UnmanagedType.LPWStr)] string path);
    void GetArguments(IntPtr text, int count);
    void SetArguments([MarshalAs(UnmanagedType.LPWStr)] string text);
    void GetHotkey(out short key);
    void SetHotkey(short key);
    void GetShowCmd(out int command);
    void SetShowCmd(int command);
    void GetIconLocation(IntPtr path, int count, out int index);
    void SetIconLocation([MarshalAs(UnmanagedType.LPWStr)] string path, int index);
    void SetRelativePath([MarshalAs(UnmanagedType.LPWStr)] string path, uint reserved);
    void Resolve(IntPtr window, uint flags);
    void SetPath([MarshalAs(UnmanagedType.LPWStr)] string path);
}
public static class GuardianShortcut {
    public static void Save(string path, string target, string arguments, string workingDirectory, string icon, string description) {
        object instance = Activator.CreateInstance(Type.GetTypeFromCLSID(new Guid("00021401-0000-0000-C000-000000000046")));
        try {
            var link = (IGuardianShellLinkW)instance;
            link.SetPath(target);
            link.SetArguments(arguments);
            link.SetWorkingDirectory(workingDirectory);
            link.SetIconLocation(icon, 0);
            link.SetDescription(description);
            link.SetShowCmd(1);
            ((IPersistFile)instance).Save(path, true);
        } finally { Marshal.ReleaseComObject(instance); }
    }
}
'@
}
foreach ($item in $items) {
    $arguments = '-NoProfile -ExecutionPolicy Bypass -File "' + $entry + '" -Action ' + $item.Action + ' -Config "' + $configPath + '"'
    [GuardianShortcut]::Save((Join-Path $directory.FullName ($item.Name + '.lnk')), "$PSHOME\powershell.exe", $arguments, $PSScriptRoot, $icon,
        ($item.Name + '；操作后显示真实状态，图标不代表当前状态'))
}
Write-Output '已生成两个 PowerShell 桌面快捷方式。请保持 Skill 及配置路径固定。'
