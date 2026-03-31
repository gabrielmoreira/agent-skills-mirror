import socket
import time
import threading
import wave
import ctypes

import pyaudio
import pygame


# 按住键盘 0 键时才拾音并发送给fay；松开则暂停拾音

is_speaking = False
reconnect_event = threading.Event()


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
    while True:
        if reconnect_event.is_set():
            break
        if not stream:
            time.sleep(0.05)
            continue

        time.sleep(0.0001)
        if is_speaking:
            continue

        # 检测键盘 0 是否按下（虚拟键码 0x30）
        key_down = bool(user32.GetAsyncKeyState(0x30) & 0x8000)
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
    server_addr = ("127.0.0.1", 10001)

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
