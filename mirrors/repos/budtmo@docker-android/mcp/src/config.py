import os


class Settings:
    def __init__(self) -> None:
        self.emulator_host = os.environ.get("EMULATOR_HOST", "127.0.0.1")
        self.emulator_port = int(os.environ.get("EMULATOR_PORT", "5555"))
        self.adb_path = os.environ.get("ADB_PATH", "adb")
        self.adb_connect_retries = int(os.environ.get("ADB_CONNECT_RETRIES", "20"))
        self.adb_connect_retry_delay_s = int(os.environ.get("ADB_CONNECT_RETRY_DELAY_SECONDS", "2"))
        self.adb_command_timeout_s = int(os.environ.get("ADB_COMMAND_TIMEOUT_SECONDS", "30"))
        self.mcp_host = os.environ.get("MCP_HOST", "0.0.0.0")
        self.mcp_port = int(os.environ.get("MCP_PORT", "8000"))


settings = Settings()
