class Device:
    def __init__(self, serial: str = "127.0.0.1:5555", state: str = "device", extra: str = ""):
        self.serial = serial
        self.state = state # device=ready, offline,unauthorized
        self.extra = extra

    def to_dict(self) -> dict:
        return {"serial": self.serial, "state": self.state, "extra": self.extra}
