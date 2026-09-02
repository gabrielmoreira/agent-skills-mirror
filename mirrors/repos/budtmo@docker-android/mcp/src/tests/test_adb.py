import shlex
import pytest

from src.adb import AdbClient, AdbCommandError, AdbConnectionError


def make_client(text_responses=None):
    calls: list[list[str]] = []
    responses = iter(text_responses or [])

    client = AdbClient(host="127.0.0.1", port=5555)

    def fake_run(args):
        calls.append(list(args))
        return next(responses)

    client._run = fake_run
    return client, calls

def test_serial():
    client, _ = make_client()
    assert client.serial == "127.0.0.1:5555"

def test_successfully_connected():
    client, calls = make_client(text_responses=[(0, "connected to 127.0.0.1:5555", "")])
    output = client.connect(retries=3, delay=0)
    assert output == "connected to 127.0.0.1:5555"
    assert client.is_connected() is True
    assert calls == [["connect", "127.0.0.1:5555"]]

def test_connect_to_connected_client():
    client, calls = make_client(text_responses=[(0, "already connected to 127.0.0.1:5555", "")])
    client.connect(retries=3, delay=0)
    assert client.is_connected() is True

def test_connect_retry_and_success(monkeypatch):
    sleeps = []
    monkeypatch.setattr("src.adb.time.sleep", lambda s: sleeps.append(s))
    client, calls = make_client(
        text_responses=[
            (1, "", "connection refused"),
            (0, "connected to 127.0.0.1:5555", "")
        ]
    )
    output = client.connect(retries=3, delay=2)
    assert output == "connected to 127.0.0.1:5555"
    assert client.is_connected() is True
    assert len(calls) == 2
    assert sleeps == [2]

def test_unable_to_connect(monkeypatch):
    monkeypatch.setattr("src.adb.time.sleep", lambda s: None)
    client, calls = make_client(
        text_responses=[
            (1, "", "connection refused"),
            (1, "", "connection refused")
        ]
    )
    with pytest.raises(AdbConnectionError):
        client.connect(retries=2, delay=0)
    assert client.is_connected() is False
    assert len(calls) == 2

def test_adb_error():
    client, _ = make_client(text_responses=[(1, "", "server not running")])
    with pytest.raises(AdbCommandError):
        client.devices()

def test_visit_url():
    client, calls = make_client(text_responses=[(0, "Starting: Intent { act=android.intent.action.VIEW }\n", "")])
    url = "https://example.com"
    output = client.visit(url)
    assert output == "Starting: Intent { act=android.intent.action.VIEW }"
    assert calls[0][-1].startswith(f"am start -a android.intent.action.VIEW -d {url}")

def test_visit_url_with_url_injection():
    client, calls = make_client(text_responses=[(0, "Starting: Intent { act=android.intent.action.VIEW }\n", "")])
    url = "https://example.com/`rm -rf *`"
    output = client.visit(url)
    assert output == "Starting: Intent { act=android.intent.action.VIEW }"
    # passed as one argument
    assert calls[0][-1].startswith(f"am start -a android.intent.action.VIEW -d {shlex.quote(url)}")

def test_current_opened_app():
    client, calls = make_client(text_responses=[(0, "mCurrentFocus=Window{chrome com.android.chrome}\n", "")])
    assert "com.android.chrome" in client.current_window()

def test_press_hardware_supported_buttons():
    supported_buttons = ["home", "back", "enter"]
    for button in supported_buttons:
        client, calls = make_client(text_responses=[(0, "", "")])
        output = client.press_button(button)
        assert output == ""
        assert calls[0][-1] == f"input keyevent KEYCODE_{button.upper()}"

def test_press_hardware_unknown_button():
    client, calls = make_client()
    with pytest.raises(ValueError):
        client.press_button("screenshot")
