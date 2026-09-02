from src.device import Device


def test_device_to_dict():
    device = Device(serial="127.0.0.1:5555", state="device", extra="product:sdk_gphone64")
    assert device.to_dict() == {
        "serial": "127.0.0.1:5555",
        "state": "device",
        "extra": "product:sdk_gphone64"
    }

def test_device_with_empty_extra():
    device = Device(serial="127.0.0.1:5555", state="device")
    assert device.extra == ""
    assert device.to_dict()["extra"] == ""
