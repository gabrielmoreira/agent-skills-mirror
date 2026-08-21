---
name: robius-app-architecture
description: "Structures Robius and Makepad apps using Robrix/Moly patterns: App and MatchEvent, Tokio worker, submit_async_request, Cx::post_action, and lock-free SignalToUI queues. Use when wiring async backends into a Makepad UI thread or designing Robius startup and shutdown. Not for turtle Walk/Layout debugging (makepad-2-0-layout). Do not block handle_event with await."
version: 1.0.1
risk: unknown
source: community
---

# Robius App Architecture Skill

Production-grade patterns for structuring Makepad applications built on the Robius framework, derived from the **Robrix** (Matrix chat client) and **Moly** (AI chat application) codebases.

**Source codebases:**
- **Robrix**: Complex sync/async with background subscriptions, full Tokio runtime integration.
- **Moly**: Cross-platform (native + WASM) with streaming APIs and platform-agnostic async primitives.

## When to Use

Use this skill when:
- Building a Makepad application with async backend integration.
- Designing sync/async communication patterns in Makepad.
- Structuring a Robius-style application (App struct, `live_register`, `MatchEvent`, startup/shutdown).
- Handling high-frequency background updates with lock-free queues.
- Integrating Tokio runtime into a Makepad UI thread.
- Keywords: `robrix`, `robius`, `makepad app structure`, `async makepad`, `tokio makepad`, `submit_async_request`, `SignalToUI`, `Cx::post_action`, `worker task`, `MatchEvent`, `handle_startup`.

## Prerequisites

- Rust toolchain with Makepad and Robius dependencies configured.
- Familiarity with `live_design!`, `Live`, `LiveHook`, `LiveRegister`, `AppMain`, and `MatchEvent` traits.
- For Tokio integration: `tokio` and `crossbeam-queue` crates available in the workspace.
- For cross-platform (native + WASM): follow Procedure steps 3–6 and the WASM pitfall below before writing platform-specific async code. Use `PlatformSend` / `UiRunner` / `spawn()` instead of raw `tokio::spawn`.

## Procedure

### 1. Define the Top-Level App

```rust
use makepad_widgets::*;

live_design! {
    use link::theme::*;
    use link::widgets::*;

    App = {{App}} {
        ui: <Root>{
            main_window = <Window> {
                window: {inner_size: vec2(1280, 800), title: "MyApp"},
                body = {
                    // Main content here
                }
            }
        }
    }
}

app_main!(App);

#[derive(Live)]
pub struct App {
    #[live] ui: WidgetRef,
    #[rust] app_state: AppState,
}

impl LiveRegister for App {
    fn live_register(cx: &mut Cx) {
        // Order matters: register base widgets first
        makepad_widgets::live_design(cx);
        // Then shared/common widgets
        crate::shared::live_design(cx);
        // Then feature modules
        crate::home::live_design(cx);
    }
}

impl LiveHook for App {
    fn after_new_from_doc(&mut self, cx: &mut Cx) {
        // One-time initialization after widget tree is created
    }
}
```

### 2. Implement AppMain with MatchEvent and Scope

```rust
impl AppMain for App {
    fn handle_event(&mut self, cx: &mut Cx, event: &Event) {
        // Forward to MatchEvent trait
        self.match_event(cx, event);

        // Pass AppState through widget tree via Scope
        let scope = &mut Scope::with_data(&mut self.app_state);
        self.ui.handle_event(cx, event, scope);
    }
}
```

### 3. Initialize the Tokio Runtime (Static Singletons)

```rust
use std::sync::Mutex;
use tokio::sync::mpsc::{UnboundedReceiver, UnboundedSender};

static TOKIO_RUNTIME: Mutex<Option<tokio::runtime::Runtime>> = Mutex::new(None);
static REQUEST_SENDER: Mutex<Option<UnboundedSender<AppRequest>>> = Mutex::new(None);

pub fn start_async_runtime() -> Result<tokio::runtime::Handle> {
    let (request_sender, request_receiver) = tokio::sync::mpsc::unbounded_channel();

    let rt_handle = TOKIO_RUNTIME.lock().unwrap()
        .get_or_insert_with(|| {
            tokio::runtime::Runtime::new()
                .expect("Failed to create Tokio runtime")
        })
        .handle()
        .clone();

    // Store sender for UI thread to use
    *REQUEST_SENDER.lock().unwrap() = Some(request_sender);

    // Spawn the main worker task
    rt_handle.spawn(worker_task(request_receiver));

    Ok(rt_handle)
}
```

### 4. Define Request Types and Submission Helper

```rust
pub enum AppRequest {
    FetchData { id: String },
    SendMessage { content: String },
    // ... other request types
}

/// Submit a request from UI thread to async runtime
pub fn submit_async_request(req: AppRequest) {
    if let Some(sender) = REQUEST_SENDER.lock().unwrap().as_ref() {
        sender.send(req)
            .expect("BUG: worker task receiver has died!");
    }
}
```

### 5. Implement the Worker Task

```rust
async fn worker_task(mut request_receiver: UnboundedReceiver<AppRequest>) -> Result<()> {
    while let Some(request) = request_receiver.recv().await {
        match request {
            AppRequest::FetchData { id } => {
                let _task = tokio::spawn(async move {
                    let result = fetch_data(&id).await;
                    Cx::post_action(DataFetchedAction { id, result });
                });
            }
            AppRequest::SendMessage { content } => {
                let _task = tokio::spawn(async move {
                    match send_message(&content).await {
                        Ok(()) => Cx::post_action(MessageSentAction::Success),
                        Err(e) => Cx::post_action(MessageSentAction::Failed(e)),
                    }
                });
            }
        }
    }
    Ok(())
}
```

### 6. Set Up the Lock-Free Update Queue for High-Frequency Updates

```rust
use crossbeam_queue::SegQueue;
use makepad_widgets::SignalToUI;

pub enum DataUpdate {
    NewItem { item: Item },
    ItemChanged { id: String, changes: Changes },
    Status { message: String },
}

static PENDING_UPDATES: SegQueue<DataUpdate> = SegQueue::new();

/// Called from background async tasks
pub fn enqueue_update(update: DataUpdate) {
    PENDING_UPDATES.push(update);
    SignalToUI::set_ui_signal();  // Wake UI thread
}
```

### 7. Drain Updates in Widget handle_event

```rust
impl Widget for MyWidget {
    fn handle_event(&mut self, cx: &mut Cx, event: &Event, scope: &mut Scope) {
        if let Event::Signal = event {
            while let Some(update) = PENDING_UPDATES.pop() {
                match update {
                    DataUpdate::NewItem { item } => {
                        self.items.push(item);
                        self.redraw(cx);
                    }
                    // ... handle other updates
                }
            }
        }
    }
}
```

### 8. Implement the Startup Sequence

```rust
impl MatchEvent for App {
    fn handle_startup(&mut self, cx: &mut Cx) {
        // 1. Initialize logging
        let _ = tracing_subscriber::fmt::try_init();

        // 2. Initialize app data directory
        let _app_data_dir = crate::app_data_dir();

        // 3. Load persisted state
        if let Err(e) = persistence::load_window_state(
            self.ui.window(ids!(main_window)), cx
        ) {
            error!("Failed to load window state: {}", e);
        }

        // 4. Update UI based on loaded state
        self.update_ui_visibility(cx);

        // 5. Start async runtime
        let _rt_handle = crate::start_async_runtime().unwrap();
    }
}
```

### 9. Implement the Shutdown Sequence

```rust
impl AppMain for App {
    fn handle_event(&mut self, cx: &mut Cx, event: &Event) {
        if let Event::Shutdown = event {
            // Save window geometry
            let window_ref = self.ui.window(ids!(main_window));
            if let Err(e) = persistence::save_window_state(window_ref, cx) {
                error!("Failed to save window state: {e}");
            }

            // Save app state
            if let Some(user_id) = current_user_id() {
                if let Err(e) = persistence::save_app_state(
                    self.app_state.clone(), user_id
                ) {
                    error!("Failed to save app state: {e}");
                }
            }
        }
        // ... rest of event handling
    }
}
```

## Core Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     UI Thread (Makepad)                     │
│  ┌─────────┐     ┌──────────┐     ┌──────────────────────┐ │
│  │   App   │────▶│ WidgetRef │────▶│ Widget Tree (View)  │ │
│  │ State   │     │    ui     │     │ Scope::with_data()  │ │
│  └────┬────┘     └──────────┘     └──────────────────────┘ │
│       │                                                     │
│       │ submit_async_request()                              │
│       ▼                                                     │
│  ┌─────────────────┐          ┌─────────────────────────┐  │
│  │ REQUEST_SENDER  │─────────▶│  Crossbeam SegQueue     │  │
│  │ (MPSC Channel)  │          │  (Lock-free Updates)    │  │
│  └─────────────────┘          └─────────────────────────┘  │
└───────────────────────────────────┬─────────────────────────┘
                                    │
                    SignalToUI::set_ui_signal()
                                    │
┌───────────────────────────────────┴─────────────────────────┐
│                   Tokio Runtime (Async)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           worker_task (Request Handler)               │   │
│  │  - Receives Request from UI                           │   │
│  │  - Spawns async tasks per request                     │   │
│  │  - Posts actions back via Cx::post_action()           │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Per-Item Subscriber Tasks                     │   │
│  │  - Listens to external data stream                    │   │
│  │  - Sends Update via crossbeam channel                 │   │
│  │  - Calls SignalToUI::set_ui_signal() to wake UI       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Best Practices

1. **Separation of Concerns**: Keep UI logic on the main thread; async operations in the Tokio runtime.
2. **Request/Response Pattern**: Use typed enums for requests and actions.
3. **Lock-Free Updates**: Use `crossbeam::SegQueue` for high-frequency background updates.
4. **SignalToUI**: Always call `SignalToUI::set_ui_signal()` after enqueueing updates.
5. **Cx::post_action()**: Use for async task results that need action handling.
6. **Scope::with_data()**: Pass shared state through the widget tree.
7. **Module Registration Order**: Register base widgets before dependent modules in `live_register()`.

## Where the patterns live

This skill does not ship a companion pack. The execute path is the Procedure:

| Topic | Where in this file |
|------|---------------------|
| Tokio runtime, worker tasks, request channels | Procedure 3–5 |
| Sync/async message passing (`SegQueue`, `SignalToUI`) | Procedure 6–7 |
| Cross-platform native + WASM (`PlatformSend`, `UiRunner`, `spawn()`) | Prerequisites + WASM pitfall |

### Production Patterns in `_base/`

| Pattern | Description |
|---------|-------------|
| `08-async-loading` | Async data loading with loading states |
| `09-streaming-results` | Incremental results with SignalToUI |
| `13-tokio-integration` | Full tokio runtime integration |

## Pitfalls

- **Module registration order**: Registering feature modules before `makepad_widgets::live_design(cx)` causes widget resolution failures. Always register base widgets first.
- **Forgetting `SignalToUI::set_ui_signal()`**: If you push to `PENDING_UPDATES` without signaling, the UI thread will never drain the queue and updates will appear lost.
- **Worker task panic**: If the `worker_task` receiver dies, `submit_async_request()` will panic with `"BUG: worker task receiver has died!"`. Ensure the runtime is started before any request submission.
- **Blocking the UI thread**: Never call `.await` or blocking I/O directly in `handle_event`. Always dispatch through `submit_async_request()`.
- **WASM compatibility**: Tokio's multi-threaded runtime is not available on WASM. For cross-platform targets, use `PlatformSend` / `UiRunner` / `spawn()` instead of raw `tokio::spawn`.
- **Non-Send types on WASM**: Use `ThreadToken` patterns from Moly for types that cannot cross thread boundaries on WASM targets.
- **Shutdown without saving**: If `Event::Shutdown` is not handled, window geometry and app state will not persist across restarts.
- **Scope misuse**: `Scope::with_data()` must reference the same `AppState` instance passed from `App::handle_event`; creating a separate scope in child widgets breaks shared state propagation.

## Verification

1. **Runtime started**: After `handle_startup`, confirm the runtime handle is valid:
   ```rust
   assert!(TOKIO_RUNTIME.lock().unwrap().is_some(), "Tokio runtime not initialized");
   assert!(REQUEST_SENDER.lock().unwrap().is_some(), "Request sender not initialized");
   ```

2. **Request round-trip**: Submit a test request and verify the corresponding action is posted back:
   ```rust
   submit_async_request(AppRequest::FetchData { id: "test".into() });
   // In the action handler, assert DataFetchedAction is received with id == "test"
   ```

3. **Lock-free queue drain**: After `enqueue_update()`, verify `SignalToUI` fires and the widget drains the queue:
   ```rust
   enqueue_update(DataUpdate::Status { message: "ok".into() });
   // On next Event::Signal, assert PENDING_UPDATES.pop() returns the Status update
   ```

4. **Module registration**: Confirm `live_register()` calls base widgets before feature modules. A missing widget at runtime indicates incorrect ordering.

5. **Shutdown persistence**: After closing the app, verify saved state files exist in the app data directory and contain expected window geometry and app state.

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.

## Related Skills

- `_base/08-async-loading` — Async data loading with loading states.
- `_base/09-streaming-results` — Incremental results with SignalToUI.
- `_base/13-tokio-integration` — Full Tokio runtime integration.
