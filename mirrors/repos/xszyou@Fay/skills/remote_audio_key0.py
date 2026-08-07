import socket
import time
import threading
import wave
import ctypes
import json
import urllib.parse
import urllib.request

import pyaudio
import pygame


# 按住键盘 0 键时才拾音并发送给fay；松开则暂停拾音
# 按下瞬间自动关闭 Fay 唤醒；松开瞬间：若原本开启则恢复，原本关闭则保持

is_speaking = False
reconnect_event = threading.Event()

FAY_HOST = "192.168.1.26"
FAY_API_PORT = 5000
FAY_API_BASE = f"http://{FAY_HOST}:{FAY_API_PORT}"


def get_wake_word_enabled() -> bool:
    """查询 Fay 当前唤醒开关状态"""
    try:
        req = urllib.request.Request(f"{FAY_API_BASE}/api/get-data", method="POST")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return bool(data.get("config", {}).get("source", {}).get("wake_word_enabled", False))
    except Exception as exc:
        print(f"\n[warn] 获取唤醒状态失败: {exc}")
        return False


def set_wake_word_enabled(enabled: bool) -> bool:
    """切换 Fay 唤醒开关"""
    try:
        payload = {"config": {"source": {"wake_word_enabled": enabled}}}
        body = urllib.parse.urlencode({"data": json.dumps(payload)}).encode("utf-8")
        req = urllib.request.Request(
            f"{FAY_API_BASE}/api/submit",
            data=body,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        urllib.request.urlopen(req, timeout=3).read()
        print(f"\n[info] 唤醒已{'开启' if enabled else '关闭'}")
        return True
    except Exception as exc:
        print(f"\n[warn] 设置唤醒状态失败: {exc}")
        return False


def get_stream(device_id: int = 0):
    paudio = pyaudio.PyAudio()
    if device_id < 0:
        return None
    return paudio.open(
        input_device_index=device_id,
        rate=16000,
        format=pyaudio.paInt16,
        channels=1,
        input=True,
    )


def send_audio(client: socket.socket):
    global is_speaking
    stream = get_stream()
    user32 = ctypes.windll.user32
    prev_key_down = False
    wake_was_enabled = False  # 按下瞬间记录的原始唤醒状态
    while True:
        if reconnect_event.is_set():
            break
        if not stream:
            time.sleep(0.05)
            continue

        time.sleep(0.0001)
        if is_speaking:
            continue

        # 检测键盘 0 是否按下：主键盘 0（0x30）、小键盘 0 NumLock 开（VK_NUMPAD0=0x60）、
        # 小键盘 0 NumLock 关时会被识别为 VK_INSERT（0x2D）
        key_down = bool(user32.GetAsyncKeyState(0x30) & 0x8000) or \
                   bool(user32.GetAsyncKeyState(0x60) & 0x8000) or \
                   bool(user32.GetAsyncKeyState(0x2D) & 0x8000)

        # 边沿检测：按下瞬间关闭唤醒；松开瞬间若原本开启则恢复
        if key_down and not prev_key_down:
            wake_was_enabled = get_wake_word_enabled()
            if wake_was_enabled:
                set_wake_word_enabled(False)
        elif prev_key_down and not key_down:
            if wake_was_enabled:
                set_wake_word_enabled(True)
        prev_key_down = key_down

        if not key_down:
            time.sleep(0.01)
            continue

        try:
            data = stream.read(1024, exception_on_overflow=False)
            client.send(data)
            time.sleep(0.005)
            print(".", end="", flush=True)
        except Exception:
            reconnect_event.set()
            break


def receive_audio(client: socket.socket):
    global is_speaking
    while True:
        if reconnect_event.is_set():
            break
        try:
            data = client.recv(9)
        except Exception:
            reconnect_event.set()
            break
        filedata = b""
        # 文件开始标记
        if data == b"\x00\x01\x02\x03\x04\x05\x06\x07\x08":
            while True:
                try:
                    chunk = client.recv(1024)
                except Exception:
                    reconnect_event.set()
                    break
                filedata += chunk
                # 去除心跳噪声
                filedata = filedata.replace(b"\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8", b"")
                # 文件结束标记
                if filedata.endswith(b"\x08\x07\x06\x05\x04\x03\x02\x01\x00"):
                    filedata = filedata[:-9]
                    break
            print(f"\n[info] receive audio end: {len(filedata)}", end="")

            filename = f"samples/recv_{time.time()}.mp3"
            with open(filename, "wb") as wf:
                wf.write(filedata)
            with wave.open(filename, "rb") as wav_file:
                audio_length = wav_file.getnframes() / float(wav_file.getframerate())
            is_speaking = True
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            time.sleep(audio_length)
            is_speaking = False


if __name__ == "__main__":
    pygame.mixer.init()
    server_addr = ("192.168.1.26", 10001)

    while True:
        reconnect_event.clear()
        try:
            client = socket.socket()
            client.connect(server_addr)
            client.send(b"<username>User</username>")
            time.sleep(1)
            client.send(b"<output>False<output>")
            time.sleep(1)

            threading.Thread(target=send_audio, args=(client,), daemon=True).start()
            threading.Thread(target=receive_audio, args=(client,), daemon=True).start()

            print(f"已连接 {server_addr[0]}:{server_addr[1]}，按住 0 键才会拾音发送；松开暂停。Ctrl+C 退出。")
            while not reconnect_event.is_set():
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n退出。")
            break
        except Exception as exc:
            print(f"\n连接异常：{exc}")
        finally:
            try:
                client.close()
            except Exception:
                pass
            print("连接断开，3 秒后重连...")
            time.sleep(3)
