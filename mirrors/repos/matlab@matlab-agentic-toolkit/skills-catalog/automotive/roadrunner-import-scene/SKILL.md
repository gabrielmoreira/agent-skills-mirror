---
name: roadrunner-import-scene
description: >
  Connect to RoadRunner and import HD Map or OpenDRIVE files into a new scene using MATLAB.
  Use when loading driving scenes in RoadRunner or RoadRunner Scene Builder, importing RRHD,
  OpenDRIVE, or other RoadRunner-supported formats for simulation, or verifying
  Lanelet2-to-RRHD conversion results visually.
license: MathWorks BSD-3-Clause
metadata:
  author: MathWorks
  version: "1.0"
---

# RoadRunner Scene Import

Connect to a running RoadRunner application and import map files into a new scene for visualization and verification.

## When to Use

- Importing a `.rrhd` file into RoadRunner for visual verification
- Importing an OpenDRIVE `.xodr` file into RoadRunner
- Connecting to a running RoadRunner instance from MATLAB
- Auto-launching RoadRunner when no instance is running
- Verifying converted maps after Lanelet2-to-RRHD or other conversions

## When NOT to Use

- Building RRHD map content — use `roadrunner-rrhd-authoring`
- Converting Lanelet2 to RRHD — use `roadrunner-convert-lanelet2-to-rrhd`
- Looking up asset paths — use `roadrunner-asset-mapping`
- RoadRunner is not installed or no valid project folder exists

## Key Rules

- **Always write to .m files.** Never put multi-line MATLAB code directly in `evaluate_matlab_code`. Write to a `.m` file, run with `run_matlab_file`, edit on error.
- **Only ONE RoadRunner instance per session.** Try `roadrunner.connect()` first; only launch if none exists.
- **Always copy file to project folder.** Use `status(rrApp).Project.Filename` and `copyfile()` explicitly in every import workflow — never omit or hide behind a variable.
- **Always set `bridgeOpts.IsEnabled = true` explicitly.** Never rely on constructor defaults for bridge auto-detection.
- **Run enforcement gates before `importScene`.** Connection, file location, and extension checks are mandatory.
- **Load before Build by default.** Use `ImportStep="Load"` unless user explicitly requests a full build.

## Prerequisites

- **RoadRunner** must be installed (R2025a or later) at a standard location under `C:/Program Files/`
- A **RoadRunner Project folder** must exist (the skill uses the Sample Project by default)
- If RoadRunner is already open, the skill reuses that instance
- If RoadRunner is NOT open, the skill **auto-launches it** — no manual steps required

## Connection Strategy

Always try `roadrunner.connect()` first to reuse an existing instance. **If no instance is running, launch one automatically** — never ask the user to open RoadRunner manually.

**IMPORTANT: Only ONE RoadRunner instance per session.** If the conversion pipeline already called `roadrunnerHDMap` (which may launch a background instance), retry `roadrunner.connect()` with a pause before launching a new one. Never call `roadrunner(InstallationFolder=...)` without first confirming no instance exists.

```matlab
% Try connecting (with retry for recently-launched instances)
rrApp = [];
for attempt = 1:3
    try
        rrApp = roadrunner.connect();
        fprintf('Connected to existing RoadRunner instance.\n');
        break;
    catch
        if attempt < 3
            pause(2);  % Wait for background instance to become ready
        end
    end
end

if isempty(rrApp)
    % No instance running — find installation and launch
    installPaths = { ...
        "C:/Program Files/RoadRunner R2026a/bin/win64", ...
        "C:/Program Files/RoadRunner R2025b/bin/win64", ...
        "C:/Program Files/RoadRunner R2025a/bin/win64"};

    installFolder = "";
    for i = 1:numel(installPaths)
        if isfolder(installPaths{i})
            installFolder = installPaths{i};
            break;
        end
    end
    if installFolder == ""
        error('RoadRunner:NotFound', ...
            'No RoadRunner installation found under C:/Program Files/.');
    end

    % Launch ONE instance
    rrApp = roadrunner(InstallationFolder=installFolder);
    fprintf('Launched RoadRunner from %s\n', installFolder);

    % Open or create a project (caller provides projectFolder, or use default)
    if ~exist('projectFolder', 'var') || projectFolder == ""
        projectFolder = fullfile(getenv("USERPROFILE"), "RoadRunner Projects", "ImportProject");
    end
    if isfolder(projectFolder)
        openProject(rrApp, projectFolder);
    else
        newProject(rrApp, projectFolder);
    end
    fprintf('Project: %s\n', projectFolder);
end
```

### Connect with Custom Port

```matlab
rrApp = roadrunner.connect(apiPort);        % default: 35707
rrApp = roadrunner.connect(apiPort, cosimPort); % default cosim: 35706
```

### Namespace Conflict Note

If you get `The class roadrunner has no Constant property or Static method 'hdmap'` after connecting, this means the `roadrunner` function is shadowed by the live `rrApp` variable. Clear and reinitialize:
```matlab
clear rrApp;
rrMap = roadrunnerHDMap;  % reload namespace
rrApp = roadrunner.connect();  % reconnect
```

## Import Workflow

### Step 1: Create a Fresh Scene

Always create a new scene before importing to avoid stale data:

```matlab
newScene(rrApp);
```

### Step 2: Copy File to Project (MANDATORY — always show explicitly)

RoadRunner requires imported files to be inside the project folder. You MUST always include this exact pattern in your generated code — never assume the file is already there or hide it behind a variable:

```matlab
st = status(rrApp);
projectFolder = st.Project.Filename;
[~, fileName, ext] = fileparts(sourceFile);
destFile = fullfile(projectFolder, fileName + ext);
copyfile(sourceFile, destFile);
```

**NEVER** omit the `copyfile()` call or the `status(rrApp).Project.Filename` lookup. Even if you define a `destFile` variable elsewhere, you MUST show both the project path retrieval and the copy operation explicitly in every import workflow.

### Step 3: Import the Map

#### RoadRunner HD Map (.rrhd)

**Load only (inspect RRHD view before build):**
```matlab
importOpts = roadrunnerHDMapImportOptions;
importOpts.ImportStep = "Load";
importScene(rrApp, destFile, "RoadRunner HD Map", importOpts);
```

**Full import with build:**
```matlab
importOpts = roadrunnerHDMapImportOptions;
buildOpts = roadrunnerHDMapBuildOptions;
buildOpts.ClearSceneOfExistingData = true;
buildOpts.DetectAsphaltSurfaces = true;

bridgeOpts = autoDetectBridgesOptions;
bridgeOpts.IsEnabled = true;   % MANDATORY: always set explicitly, never rely on default
buildOpts.AutoDetectBridgesOptions = bridgeOpts;

importOpts.BuildOptions = buildOpts;
importScene(rrApp, destFile, "RoadRunner HD Map", importOpts);
```

**IMPORTANT:** When enabling bridge auto-detection, you MUST always write `bridgeOpts.IsEnabled = true` explicitly. Do NOT rely on the constructor default — the line must appear in the generated code.

#### OpenDRIVE (.xodr)

```matlab
importOpts = openDriveImportOptions;
importOpts.ImportSignals = true;
importOpts.ImportObjects = true;
importScene(rrApp, destFile, "OpenDRIVE", importOpts);
```

### Step 4: Save the Scene

```matlab
[~, sceneName] = fileparts(sourceFile);
saveScene(rrApp, sceneName);
```

## Import Options Reference

### roadrunnerHDMapImportOptions

| Property | Description |
|----------|-------------|
| `ImportStep` | `"Load"` (RRHD view only) or `"Unspecified"` (full load+build) |
| `LoadOptions` | `roadrunnerHDMapLoadOptions` — offset, projection |
| `BuildOptions` | `roadrunnerHDMapBuildOptions` — build configuration |

### roadrunnerHDMapBuildOptions

| Property | Description | Default |
|----------|-------------|---------|
| `ClearSceneOfExistingData` | Remove existing scene content | auto |
| `DetectAsphaltSurfaces` | Generate road surfaces | auto |
| `FitCrossSections` | Fit lane cross sections | auto |
| `CurvatureBlend` | Curvature blending factor | auto |
| `UseLaneGroups` | Group lanes for editing (R2024a+) | auto |
| `CombineTransitionLanes` | Merge transition lanes (R2025a+) | auto |
| `AutoDetectBridgesOptions` | Bridge auto-detection settings | enabled |
| `PreserveJunctionLanes` | Keep original junction lanes (R2026a) | false |
| `PreserveJunctionShape` | Keep junction geometry (R2026a) | false |

### openDriveImportOptions

| Property | Description |
|----------|-------------|
| `ImportSignals` | Import traffic signals |
| `ImportObjects` | Import static objects |
| `LaneOptions` | Lane conversion settings |
| `Offset` | Scene position offset |
| `Projection` | Geospatial projection |
| `ImportRegion` | Region filter (R2024a+) |

## Supported Formats

| Format Name | File Type | Since |
|-------------|-----------|-------|
| `"RoadRunner HD Map"` | .rrhd | R2022b |
| `"OpenDRIVE"` | .xodr | R2022a |
| `"HERE HD Map"` | (catalog) | R2024a |
| `"TomTom HD Map"` | (catalog) | R2024b |

## Default Behavior

When the user asks to "import a map" or "load into RoadRunner":
1. Connect to existing RoadRunner via `roadrunner.connect()`
2. Create a new scene (clean slate)
3. Copy file to project Assets folder
4. Import with **Load only** (`ImportStep="Load"`) so user can verify RRHD view
5. Save the scene with the filename as scene name

Only perform a full build (with `BuildOptions`) when the user explicitly asks to build or the RRHD view has been verified.

## Key Functions

| Function | Purpose |
|----------|---------|
| `roadrunner.connect()` | Connect to existing RoadRunner instance |
| `roadrunner(InstallationFolder=...)` | Launch new RoadRunner instance |
| `newScene(rrApp)` | Create fresh scene (clean slate) |
| `status(rrApp)` | Get project info (`.Project.Filename`) |
| `importScene(rrApp, file, format, opts)` | Import map file into scene |
| `saveScene(rrApp, name)` | Save current scene |
| `roadrunnerHDMapImportOptions` | Create import options (set `ImportStep`, `BuildOptions`) |
| `roadrunnerHDMapBuildOptions` | Create build options (asphalt, bridges, clear) |
| `autoDetectBridgesOptions` | Bridge detection settings (`IsEnabled`) |
| `openDriveImportOptions` | OpenDRIVE-specific import options |

## Enforcement Gate (MANDATORY — run before import)

You MUST execute these checks before calling `importScene`. Do NOT skip.

```matlab
%% --- ENFORCEMENT: RoadRunner is connected ---
try
    st = status(rrApp);
    assert(~isempty(st.Project.Filename), 'No project open');
    fprintf('RoadRunner connected, project: %s\n', st.Project.Filename);
catch
    error('RoadRunner:NotConnected', ...
        'No RoadRunner instance connected. Run the Connection Strategy block first.');
end

%% --- ENFORCEMENT: File is inside project folder ---
projectFolder = st.Project.Filename;
assert(startsWith(destFile, projectFolder) || isfile(destFile), ...
    'Import file must be inside the project folder. Copy it first.');
fprintf('File location check: PASS\n');

%% --- ENFORCEMENT: File extension matches format ---
[~, ~, ext] = fileparts(destFile);
if formatName == "RoadRunner HD Map"
    assert(ext == ".rrhd", 'Expected .rrhd file for RoadRunner HD Map format');
elseif formatName == "OpenDRIVE"
    assert(ext == ".xodr", 'Expected .xodr file for OpenDRIVE format');
end
fprintf('Format check: PASS\n');
```

## Conventions

- Always specify format name string exactly: `"RoadRunner HD Map"`, `"OpenDRIVE"`
- Use `SOS` form for IIR stability (BuildOptions handles this internally)
- Show all file-staging code explicitly (`status`, `fileparts`, `fullfile`, `copyfile`)
- Use `tiledlayout`/`nexttile` for multi-panel figures (not `subplot`)
- Pin `destFile` to the project folder path — never use temp or relative paths for import

----

Copyright 2026 The MathWorks, Inc.
