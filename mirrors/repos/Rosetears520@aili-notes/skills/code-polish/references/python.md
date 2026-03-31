# Python high-risk refactors (add to "avoid" set)

- Generator vs list semantics changes; comprehension rewrites that change evaluation timing/memory use
- Exception handling and chaining changes (e.g., `raise ... from ...`, catching broader/narrower exceptions)
- Default mutable argument behaviors; dataclass defaults vs factories
- Dict/set ordering assumptions; relying on incidental iteration order
- Modifying type hints (e.g., `Optional[...]`, `Union[...]`, narrowing/widening annotations) without static-analysis confirmation; may break type-checker CI
