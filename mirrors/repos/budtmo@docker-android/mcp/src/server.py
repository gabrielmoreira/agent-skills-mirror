import logging
import time

from fastmcp import FastMCP

from .adb import AdbClient, AdbConnectionError
from .config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

adb = AdbClient(host=settings.emulator_host, port=settings.emulator_port,
                adb_path=settings.adb_path, command_timeout=settings.adb_command_timeout_s)

mcp: FastMCP = FastMCP(
    name="android-mcp",
    instructions=(
        "Tool for controlling a remote Android emulator over adb: "
        "list devices, open an app, visit a URL in the browser, "
        "insect current foreground window, press a hardware button, "
        "and wait for a number of seconds between steps."
    )
)


def _ensure_connected() -> None:
    if adb.is_connected():
        return
    try:
        adb.connect(retries=settings.adb_connect_retries, delay=settings.adb_connect_retry_delay_s)
    except AdbConnectionError as ace:
        logger.error(f"Unable to connect to Android emulator {adb.serial}: {ace}")
        raise

@mcp.tool
def list_devices() -> dict:
    _ensure_connected()
    return {"devices": adb.devices()}

@mcp.tool
def open_app(app_name: str) -> dict:
    _ensure_connected()
    output = adb.open_app(app_name)
    return {"status": "ok", "app_name": app_name, "output": output}

@mcp.tool
def visit(url: str) -> dict:
    url = url.strip()
    if not url:
        raise ValueError("url must not be empty")
    if "://" not in url:
        url = f"https://{url}"

    _ensure_connected()
    output = adb.visit(url)
    return {"status": "ok", "url": url, "output": output}

@mcp.tool
def current_window() -> dict:
    _ensure_connected()
    return {"current_window": adb.current_window()}

@mcp.tool
def press_button(button:str) -> dict:
    _ensure_connected()
    output = adb.press_button(button)
    return {"status": "ok", "button": button, "output": output}

@mcp.tool
def wait(seconds: int) -> dict:
    _ensure_connected()
    if seconds < 0:
        raise ValueError("seconds must not be negative")
    time.sleep(seconds)
    return {"status": "ok", "waited_seconds": seconds}

def main() -> None:
    try:
        _ensure_connected()
    except AdbConnectionError as ace:
        logger.warning("Starting MCP server without a confirmed emulator connection. "
                       "Tool call will retry the connection automatically.")
    mcp.run(transport="http", host=settings.mcp_host, port=settings.mcp_port)


if __name__ == "__main__":
    main()
