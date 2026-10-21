# QML Live Preview MCP Server

A local MCP server that starts a Qt Quick application and
pushes QML source changes into it live — no rebuild needed.

## Overview

The QML Live Preview MCP server connects an AI agent to the
`qmlpreview` service built into Qt's QmlDebug library. After you connect the
server, the agent can start a live preview session for your Qt and QML
application and show you the visual effect of the QML changes it makes,
in real time.

Instead of the usual edit, rebuild, and rerun cycle, the agent (or you,
working with it) can update `.qml` files and see the changes appear
immediately in the running application. This makes the server especially
useful for UI work, such as adjusting layout, styling, animations, and
component behavior, where seeing the result matters more than a full
build.

The server runs locally and communicates over standard input-output
(stdio), so you don't need any network configuration.

## Requirements

Before you use the QML Live Preview MCP server, make sure your project meets
these requirements.

- Qt 6.12 or later. The server depends on the `qmlpreview` service
  from the QmlDebug library, which is only available from Qt 6.12
  onward.
- QML debugging enabled in your build. Your application must be
  built with QML debugging support, which you can enable in CMake in **two ways**

  1. Define the `QT_QML_DEBUG` macro for your target in the CMakeLists.txt file

    ```cmake
    target_compile_definitions(MyApp PRIVATE QT_QML_DEBUG)
    ```

  2. Configure your application from the command line by passing
    `-DQT_QML_DEBUG` flag to cmake

    ```
    cmake -DCMAKE_CXX_FLAGS_INIT=-DQT_QML_DEBUG source-dir
    ```

   Important: Only enable `QT_QML_DEBUG` in development builds. If
   you leave it enabled in a release or production build, it exposes a
   debug port. Don't ship a build with QML debugging enabled.

- A built executable. The agent needs the path to an executable
  that's already built with the requirements above. It uses this path
  to start a preview session.

## Install the server

You can install the QML Live Preview MCP server from the Qt Online Installer

1. Open the Qt Online Installer, or the Qt Maintenance Tool if you
   already have Qt installed.
2. Select the components for Qt 6.12 or later.
3. Under Agentic Development Tools, select QML Live Preview for AI Agents.
4. Complete the installation.

After the server is installed, you can find the binary in the `bin`
folder of your Qt 6.12+ installation. For example

```
Qt-install-dir6.12.0compilerbinQmlPreviewMcpServer.exe
```

## Connect to an agent

After the download is complete, you can connect the server to the AI agent you use.
Register the server by pointing the agent to the absolute path of the server binary.
The server doesn’t take any arguments.

You can register the server by following the documentation and
guidelines of the AI agent of your choice. Check your agent provider’s documentation
for the exact steps. As an example, this guide shows how to register the
QML Live Preview MCP serverwith Claude, either through the Claude CLI
or by editing the Claude configuration file directly.

```bash
claude mcp add qmlpreview path-to-the-QmlPreviewMcpServer-binary
```

Editing `claude.conf` directly

Add an entry for the server under `mcpServers`

```json
mcpServers {
    qmlpreview {
        command path-to-the-QmlPreviewMcpServer-binary,
        args []
    }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `run-qmlpreview` | Starts a live preview of a Qt Quick application with hot reload, so edits to the project’s QML sources show up in the running app without a rebuild. |

## Limitations

QML Live Preview works by comparing the current state of your running
application to what the QML declarations say it should look like, and
then updating the difference. This approach works well for declarative
changes, but it has some natural limits

- Some changes rebuild part of the UI instead of patching it, and
  can lose state as a result. For example, changing a plain value
  into a script-based binding (or the other way around), or moving a
  binding from one property to another, can't be applied in place.
  QML Preview rebuilds that part of the UI instead. If you (or the
  agent) made procedural changes to objects in that area, such as
  creating extra objects at runtime, those changes are lost when the
  UI is rebuilt from the QML source. This doesn't always show up as an
  error; sometimes the only sign is that the preview looks wrong. If
  that happens, ask the agent to run `run-qmlpreview` again.

- Some changes can't be previewed at all, and require a full
  rebuild of the application. This includes adding a new file,
  making other C++ changes, and changing the C++ base type of an
  object. None of these can be patched in place, no matter how many
  times you run the preview again.

- Live preview isn't safe with QML engines running on multiple
  threads. It relies on being able to patch shared QML types safely,
  which only holds if your application uses a single QML engine, or if
  you can guarantee nothing else accesses QML types on another thread
  while a preview update is in progress. If your application uses
  multiple QML engines across threads, avoid relying on live preview,
  since its behavior in that case is unpredictable.
