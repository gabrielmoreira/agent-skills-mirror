# Keyboard input for browser-use snippets. Use these, not the built-in press_key() and fill_input():
# those send macOS native key codes, which headless Chrome on macOS reads as browser shortcuts,
# opening stray tabs and hiding the page.
# Usage, at the top of a snippet: exec(open("<skill-dir>/scripts/keyboard.py").read())
import json

_NAMED_KEYS = {"Enter": (13, "\r"), "Tab": (9, ""), "Backspace": (8, ""), "Escape": (27, ""), "Delete": (46, ""),
               "ArrowUp": (38, ""), "ArrowDown": (40, ""), "ArrowLeft": (37, ""), "ArrowRight": (39, "")}


def press(key):
    """Press one named key (Enter, Tab, Backspace, Escape, Delete, Arrow*) or type one character."""
    vk, text = _NAMED_KEYS.get(key, (0, key))
    event = {"key": key, "windowsVirtualKeyCode": vk, **({"code": key} if key in _NAMED_KEYS else {})}
    cdp("Input.dispatchKeyEvent", type="keyDown", **event, **({"text": text} if text else {}))
    cdp("Input.dispatchKeyEvent", type="keyUp", **event)


def type_keys(text):
    """Type into the focused element key by key, firing keydown, input and keyup per character."""
    for ch in text:
        press(ch)


def fill(selector, text):
    """Focus the field, select what's in it, and type over it key by key."""
    found = js(f"(() => {{ const e = document.querySelector({json.dumps(selector)}); if (!e) return false;"
               f" e.focus(); e.select?.(); return true; }})()")
    if not found:
        raise RuntimeError(f"fill: no element matches {selector!r}")
    if not text:
        press("Backspace")
    type_keys(text)
