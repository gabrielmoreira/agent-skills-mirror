---
type: skill
lifecycle: stable
inheritance: inheritable
name: python-mock-patching-location
description: Python mock.patch must target the import location, not the definition location
tier: standard
applyTo: '**/*python*,**/*mock*,**/*patching*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Python Mock Patching Location

**Category**: Testing
**Time Saved**: 30+ minutes debugging "mock not working"
**Battle-tested**: Yes — ChessCoach, multiple Python projects

---

## The Problem

You're writing a test that needs to mock `get_client()` from `module_a`. You patch `module_a.get_client`. The mock doesn't work — the real function still runs.

## Why It Happens

Python's import system creates a **reference** to the function in the importing module. When `module_b` does `from module_a import get_client`, it creates `module_b.get_client` as a separate reference. Patching the original doesn't affect the copy.

## The Rule

**Patch where the function is USED, not where it's DEFINED**

```python
# module_a.py defines get_client()
# module_b.py imports and calls it

# ❌ WRONG — patches the definition, not the usage
@patch('module_a.get_client')
def test_something(mock_client):
    result = module_b.do_work()  # Still calls real get_client!

# ✅ CORRECT — patches where it's called
@patch('module_b.get_client')
def test_something(mock_client):
    result = module_b.do_work()  # Uses mock
```

## Decision Table

| Import Style in Target Module | Patch Target |
|-------------------------------|--------------|
| `from module_a import func` | `target_module.func` |
| `import module_a` then `module_a.func()` | `module_a.func` |
| `from module_a import func as alias` | `target_module.alias` |

## Async Context Manager Trap

`MagicMock` doesn't support `async with` by default:

```python
# ❌ FAILS — MagicMock can't handle async context manager
mock_lock = MagicMock()
async with mock_lock:  # TypeError

# ✅ WORKS — proper async mock
class MockAsyncLock:
    async def __aenter__(self):
        return self
    async def __aexit__(self, *args):
        pass

mock_lock = MockAsyncLock()
```

## Verification

Test passes AND you've confirmed the mock was actually called:

```python
@patch('module_b.get_client')
def test_something(mock_client):
    mock_client.return_value = fake_response
    result = module_b.do_work()
    
    mock_client.assert_called_once()  # Verify mock was hit
```

If `assert_called_once()` fails with "Expected call not found", you patched the wrong location.

---

**Source**: Promoted from AI-Memory global-knowledge.md (2026-04-27)
