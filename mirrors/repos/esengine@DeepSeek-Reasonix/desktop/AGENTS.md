# Desktop agent notes

Desktop Go is a separate module; root Go tests do not cover it.

For changes affecting transcript viewport, scrolling, virtualization,
measurement, or delayed geometry work, read the
[transcript scroll contract](../docs/TRANSCRIPT_SCROLL_CONTRACT.md)
([中文](../docs/TRANSCRIPT_SCROLL_CONTRACT.zh-CN.md)).
It preserves single-writer ownership, generation isolation, reader intent,
bounded rendering, and deterministic regression requirements.

Other Desktop work does not require the scroll-specific procedure.
