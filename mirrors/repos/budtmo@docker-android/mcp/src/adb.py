import logging
import re
import shlex
import subprocess
import time

from .device import Device

logger = logging.getLogger(__name__)


class AdbCommandError(RuntimeError):
    "Raised when adb command exits"
    def __init__(self, args: list[str], rc: int, stderr: str):
        self.args = args
        self.rc = rc
        self.stderr = stderr
        super().__init__(
            f"adb {" ".join(args)} failed with exit code {rc}: {stderr.strip()}"
        )


class AdbConnectionError(RuntimeError):
    "Raised when client cannot connect to the device"


_APP_PACKAGES: dict[str, str] = {
    "browser": "com.android.chrome",
    "chrome": "com.android.chrome",
    "calendar": "com.google.android.calendar",
    "contacts": "com.google.android.contacts",
    "messages": "com.google.android.apps.messaging",
    "photo": "com.google.android.apps.photos",
    "settings": "com.android.settings"
}

_KEY_EVENTS: dict[str, str] = {
    "home": "KEYCODE_HOME",
    "back": "KEYCODE_BACK",
    "enter": "KEYCODE_ENTER"
}


class AdbClient:
    def __init__(self, host: str, port: int, adb_path: str = "adb", command_timeout: int = 30) -> None:
        self.host = host
        self.port = port
        self.adb_path = adb_path
        self.command_timeout = command_timeout
        self.serial = f"{host}:{port}"
        self._connected = False

    def _run(self, args: list[str]) -> tuple[int, str, str]:
        result = subprocess.run([self.adb_path, *args], capture_output=True,
                                text=True, timeout=self.command_timeout)
        return result.returncode, result.stdout, result.stderr

    def _adb(self, *args: str) -> str:
        rc, stdout, stderr = self._run(list(args))
        if rc != 0:
            raise AdbCommandError(list(args), rc, stderr)
        return stdout

    def _device_shell(self, command: str) -> str:
        args = ["-s", self.serial, "shell", command]
        rc, stdout, stderr = self._run(args)
        if rc != 0:
            raise AdbCommandError(args, rc, stderr)
        return stdout

    def is_connected(self) -> bool:
        return self._connected

    def connect(self, retries: int = 20, delay: int = 5):
        last_error: str | None = None
        for attempt in range(1, retries + 1):
            try:
                output = self._adb("connect", self.serial)
            except AdbCommandError as ace:
                last_error = str(ace)
            else:
                normalized = output.strip().lower()
                if "connected to" in normalized or "already connected" in normalized:
                    self._connected = True
                    logger.info(f"Connected to device {self.serial} ({attempt}/{retries})")
                    return output.strip()
                last_error = output.strip()

            logger.error(f"Failed to connect to device {self.serial} ({attempt}/{retries}) - {last_error}")
            self._connected = False
            if attempt < retries:
                time.sleep(delay)

        raise AdbConnectionError(f"Could not connect to {self.serial} ({retries}/{retries})")

    def devices(self) -> list[dict]:
        output = self._adb("devices", "-l")
        devices: list[Device] = []
        for line in output.splitlines()[1:]:
            line = line.strip()
            if not line or line.startswith("*"):
                continue
            parts = re.split(r"\s+", line, maxsplit=2)
            serial = parts[0]
            state = parts[1] if len(parts) > 1 else "unknown"
            extra = parts[2] if len(parts) > 2 else ""
            devices.append(Device(serial=serial, state=state, extra=extra))
        return [d.to_dict() for d in devices]

    def open_app(self, app_name: str) -> str:
        try:
            package = _APP_PACKAGES[app_name.strip().lower()]
        except KeyError as ke:
            supported = ", ".join(sorted(_APP_PACKAGES))
            raise ValueError(f"App {app_name} not supported. Supported apps: {supported}") from ke
        command = f"monkey -p {package} -c android.intent.category.LAUNCHER 1"
        return self._device_shell(command).strip()

    def visit(self, url: str) -> str:
        # shlex is to avoid url injection e.g. https://example.com/$(reboot)
        # it neutralized it as single quotes so it will be passed as one argument,
        command = f"am start -a android.intent.action.VIEW -d {shlex.quote(url)}"
        return self._device_shell(command).strip()

    def current_window(self) -> str:
        # Contains 2 different approaches because it depends on Android version
        output = self._device_shell("dumpsys window windows")
        for line in output.splitlines():
            if "mCurrentFocus" in line or "mFocusedApp" in line:
                return line.strip()
        output = self._device_shell("dumpsys activity activities")
        for line in output.splitlines():
            if "mResumedActivity" in line:
                return line.strip()
        return ""

    def press_button(self, button: str) -> str:
        try:
            keycode = _KEY_EVENTS[button.strip().lower()]
        except KeyError as ke:
            supported = ", ".join(sorted(_KEY_EVENTS))
            raise ValueError(f"Button {button} not supported. Supported buttons: {supported}")
        return self._device_shell(f"input keyevent {keycode}").strip()
