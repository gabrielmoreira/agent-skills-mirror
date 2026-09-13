# `openhuman-embed`

`openhuman-embed` is the host-facing library package for products that run the
OpenHuman core in-process, including Medulla and OpenCompany. It re-exports the
runtime builder from `openhuman-core` and owns the typed embedding facade.

Use the default contributor feature set:

```toml
[dependencies]
openhuman-embed = { git = "https://github.com/tinyhumansai/openhuman", package = "openhuman-embed" }
```

Or select a narrow host build:

```toml
[dependencies]
openhuman-embed = { git = "https://github.com/tinyhumansai/openhuman", package = "openhuman-embed", default-features = false, features = ["inference", "mcp"] }
```

```rust,no_run
use std::sync::Arc;

use openhuman_embed::{Core, CoreBuilder, DomainSet, HostKind, ServiceSet};

# async fn run() -> Result<(), Box<dyn std::error::Error>> {
let runtime = CoreBuilder::new(HostKind::Library)
    .domains(DomainSet::embedded())
    .services(ServiceSet::none())
    .build()
    .await?;
let core = Core::from_runtime(Arc::new(runtime));
let flags = core.config().runtime_flags().await?;
println!("log_prompts={}", flags.log_prompts);
# Ok(())
# }
```

Embedding products should set their product identity once during startup,
before constructing backend clients:

```rust
use openhuman_embed::{set_product_identity, ProductIdentity};

if let Some(identity) = ProductIdentity::new("opencompany") {
    set_product_identity(identity);
}
```

Use `Core::raw()` only as a temporary escape hatch when the typed facade does
not yet model a required call. A repeated raw call is a candidate for a typed
embedding method in `openhuman-embed`.
