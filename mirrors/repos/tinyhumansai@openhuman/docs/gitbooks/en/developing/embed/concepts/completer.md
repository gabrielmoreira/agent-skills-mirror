---
description: "Completer sends stateless model requests without booting a Runtime or entering the agent tool loop."
---

# Completer

Use `Completer` for one-shot text or structured generation when you do not need an agent, its tool loop or persistent transcript. It takes an explicit route and a `CompletionRequest`; the caller supplies the model and messages for every request.

A standalone completer does not claim the process runtime slot. An agent-backed completion uses the agent's effective configuration but still has no implicit durable session. Keep conversation state in your application if you need several completion calls to form a conversation.

## Runtime and agent scope

| Runtime responsibility | Agent or call responsibility |
| --- | --- |
| No runtime required for a standalone routed Completer | Optional effective agent configuration; no implicit tools or transcript |

## Verified example

<!-- BEGIN EMBED: crates/openhuman-embed/examples/completer.rs#completer -->

```rust
    let route = support::example_provider(&provider)?;
    let completer = openhuman_embed::Completer::new(route.route().expect("explicit route").clone());
    let response = completer
        .complete(openhuman_embed::CompletionRequest::new(
            route.model_id().expect("explicit model"),
            vec![openhuman_embed::ChatMessage::user("Say hello")],
        ))
        .await?;
    assert!(!response.text.is_empty());
    if support::offline() {
        assert_eq!(response.text, "completion reply");
        assert_eq!(support::chat_requests(&provider).await.len(), 1);
    }
    println!("{}", response.text);
```

<!-- END EMBED -->

[Complete runnable example](https://github.com/tinyhumansai/openhuman/blob/main/crates/openhuman-embed/examples/completer.rs). The full file includes imports, runtime setup and local fixtures used by this excerpt.

## Behavior to account for

The example checks that exactly one inference request was made and verifies the returned text. It uses a local provider fixture by default; the source contains the explicit opt-in live route path.

Choose `Agent` when a model should call tools, resume a durable thread or execute with an agent's access context. Choose the structured completion helpers when the host only needs a validated data result. For routes and transport failures see [providers](providers.md) and [errors](errors.md).
