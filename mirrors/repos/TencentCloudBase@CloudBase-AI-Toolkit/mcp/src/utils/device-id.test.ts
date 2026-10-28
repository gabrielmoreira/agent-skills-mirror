import crypto from "crypto";
import { execFileSync } from "child_process";
import fs from "fs";
import os from "os";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { computeDeviceId, physicalMacAddresses, readSystemAnchor } from "./device-id.js";

/**
 * 设备指纹的判据只有两条，都必须可测：
 * 1. **锚点优先系统标识**（IOPlatformUUID / MachineGuid / machine-id），不是 MAC；
 * 2. **同一台机器反复算必须得到同一个 id** —— 取不到任何信号时也不能退回随机数
 *    （旧实现的 `crypto.randomBytes(16)` 正是「一台 Mac 一天变 39 个设备」的放大器）。
 */

vi.mock("child_process", () => ({ execFileSync: vi.fn() }));
vi.mock("fs", () => ({ default: { readFileSync: vi.fn() } }));
vi.mock("os", () => ({
  default: {
    hostname: vi.fn(),
    cpus: vi.fn(),
    networkInterfaces: vi.fn(),
  },
}));

const execFileSyncMock = vi.mocked(execFileSync);
const readFileSyncMock = vi.mocked(fs.readFileSync);
const hostnameMock = vi.mocked(os.hostname);
const cpusMock = vi.mocked(os.cpus);
const networkInterfacesMock = vi.mocked(os.networkInterfaces);

const MAC = "3c:22:fb:aa:bb:cc";

function sha256Short(input: string): string {
  return crypto.createHash("sha256").update(input).digest("hex").substring(0, 32);
}

/** 一台普通 Mac：物理网卡 en0 稳定，awdl0 / llw0 / utun 是漂移源 */
function macInterfaces() {
  return {
    lo0: [{ address: "127.0.0.1", internal: true, mac: "00:00:00:00:00:00", family: "IPv4" }],
    en0: [{ address: "192.168.1.9", internal: false, mac: MAC, family: "IPv4" }],
    awdl0: [{ address: "fe80::1", internal: false, mac: "6e:11:22:33:44:55", family: "IPv6" }],
    llw0: [{ address: "fe80::2", internal: false, mac: "7e:11:22:33:44:66", family: "IPv6" }],
    utun3: [{ address: "fe80::3", internal: false, mac: "8e:11:22:33:44:77", family: "IPv6" }],
    bridge0: [{ address: "192.168.2.1", internal: false, mac: "9e:11:22:33:44:88", family: "IPv4" }],
  } as unknown as ReturnType<typeof os.networkInterfaces>;
}

beforeEach(() => {
  execFileSyncMock.mockReset();
  readFileSyncMock.mockReset();
  hostnameMock.mockReset().mockReturnValue("bookers-macbook");
  cpusMock.mockReset().mockReturnValue([{ model: "Apple M3 Pro" }] as ReturnType<typeof os.cpus>);
  networkInterfacesMock.mockReset().mockReturnValue(macInterfaces());
  readFileSyncMock.mockImplementation(() => {
    throw Object.assign(new Error("ENOENT"), { code: "ENOENT" });
  });
});

afterEach(() => {
  vi.clearAllMocks();
});

describe("系统锚点优先", () => {
  it("macOS 用 IOPlatformUUID，而不是 MAC", () => {
    execFileSyncMock.mockReturnValue(
      '+-o J316sAP  <class IOPlatformExpertDevice>\n  {\n    "IOPlatformUUID" = "A1B2C3D4-0000-1111-2222-333344445555"\n  }\n' as never,
    );

    const { deviceId, source } = computeDeviceId("darwin");

    expect(source).toBe("platform-uuid");
    expect(deviceId).toBe(sha256Short("A1B2C3D4-0000-1111-2222-333344445555"));
    expect(deviceId).toHaveLength(32);
  });

  it("MAC 变了（换 SSID / 插拔网卡）也不改指纹 —— 这是这次要修的病根", () => {
    execFileSyncMock.mockReturnValue('"IOPlatformUUID" = "STABLE-UUID-1"' as never);
    const first = computeDeviceId("darwin");

    networkInterfacesMock.mockReturnValue({
      en0: [{ address: "192.168.1.9", internal: false, mac: "ff:ff:ff:ff:ff:01", family: "IPv4" }],
      awdl0: [{ address: "fe80::1", internal: false, mac: "ff:ff:ff:ff:ff:02", family: "IPv6" }],
    } as unknown as ReturnType<typeof os.networkInterfaces>);
    const second = computeDeviceId("darwin");

    expect(second.deviceId).toBe(first.deviceId);
  });

  it("Windows 解析 reg query 的 MachineGuid（分隔符是多个空格也认）", () => {
    execFileSyncMock.mockReturnValue(
      "\r\nHKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Cryptography\r\n    MachineGuid    REG_SZ    3F2A9C11-AAAA-BBBB-CCCC-DDDDEEEEFFFF\r\n\r\n" as never,
    );

    const { deviceId, source } = computeDeviceId("win32");

    expect(source).toBe("machine-guid");
    expect(deviceId).toBe(sha256Short("3f2a9c11-aaaa-bbbb-cccc-ddddeeeeffff"));
  });

  it("Linux 用 /etc/machine-id", () => {
    readFileSyncMock.mockImplementation(((file: string) => {
      if (file === "/etc/machine-id") {
        return "0123456789abcdef0123456789abcdef\n";
      }
      throw Object.assign(new Error("ENOENT"), { code: "ENOENT" });
    }) as never);

    const { deviceId, source } = computeDeviceId("linux");

    expect(source).toBe("machine-id");
    expect(deviceId).toBe(sha256Short("0123456789abcdef0123456789abcdef"));
    // 有系统锚点时不该去起子进程
    expect(execFileSyncMock).not.toHaveBeenCalled();
  });
});

describe("锚点取不到时的降级", () => {
  it("ioreg 抛错 → 退到 hostname + CPU + 过滤后的物理网卡", () => {
    execFileSyncMock.mockImplementation(() => {
      throw Object.assign(new Error("spawn ioreg ENOENT"), { code: "ENOENT" });
    });

    const { deviceId, source } = computeDeviceId("darwin");

    expect(source).toBe("host-fallback");
    // 虚拟网卡的 MAC 不能参与：它们随系统状态漂移
    expect(deviceId).not.toBe(sha256Short(`bookers-macbook|Apple M3 Pro|${MAC}|6e:11:22:33:44:55`));
    expect(deviceId).toBe(sha256Short(`bookers-macbook|Apple M3 Pro|${MAC}`));
  });

  it("ioreg 超时（ETIMEDOUT）不抛，按降级处理", () => {
    execFileSyncMock.mockImplementation(() => {
      throw Object.assign(new Error("Command timed out"), { code: "ETIMEDOUT" });
    });

    expect(() => computeDeviceId("darwin")).not.toThrow();
    expect(computeDeviceId("darwin").source).toBe("host-fallback");
  });

  it("machine-id 是全 0 的空壳（镜像里常见）→ 当作取不到，退到 dbus 那份", () => {
    readFileSyncMock.mockImplementation(((file: string) => {
      if (file === "/etc/machine-id") {
        return "00000000000000000000000000000000";
      }
      if (file === "/var/lib/dbus/machine-id") {
        return "fedcba9876543210fedcba9876543210";
      }
      throw Object.assign(new Error("ENOENT"), { code: "ENOENT" });
    }) as never);

    const { source, deviceId } = computeDeviceId("linux");

    expect(source).toBe("machine-id");
    expect(deviceId).toBe(sha256Short("fedcba9876543210fedcba9876543210"));
  });

  it("连网卡都读不到 → host-only，但仍返回稳定的 32 位 hex", () => {
    readFileSyncMock.mockImplementation(() => {
      throw Object.assign(new Error("EACCES"), { code: "EACCES" });
    });
    networkInterfacesMock.mockImplementation(() => {
      throw new Error("uv_interface_addresses failed");
    });

    const first = computeDeviceId("linux");
    const second = computeDeviceId("linux");

    expect(first.source).toBe("host-only");
    expect(first.deviceId).toMatch(/^[0-9a-f]{32}$/);
    expect(second.deviceId).toBe(first.deviceId);
  });

  it("hostname 与 CPU 都读不到也不崩，且两次结果一致（绝不退回随机数）", () => {
    hostnameMock.mockImplementation(() => {
      throw new Error("no hostname");
    });
    cpusMock.mockImplementation(() => {
      throw new Error("no cpus");
    });
    networkInterfacesMock.mockReturnValue({} as ReturnType<typeof os.networkInterfaces>);

    const first = computeDeviceId("linux");
    const second = computeDeviceId("linux");

    expect(first.deviceId).toBe(second.deviceId);
    expect(first.deviceId).toHaveLength(32);
  });
});

describe("物理网卡过滤", () => {
  it("过滤 awdl / llw / utun / bridge / docker / veth，保留 en0", () => {
    networkInterfacesMock.mockReturnValue({
      en0: [{ internal: false, mac: MAC }],
      awdl0: [{ internal: false, mac: "6e:11:22:33:44:55" }],
      llw0: [{ internal: false, mac: "7e:11:22:33:44:66" }],
      utun0: [{ internal: false, mac: "8e:11:22:33:44:77" }],
      bridge0: [{ internal: false, mac: "9e:11:22:33:44:88" }],
      docker0: [{ internal: false, mac: "02:42:ac:11:00:02" }],
      veth1a2b3c: [{ internal: false, mac: "aa:bb:cc:dd:ee:01" }],
    } as unknown as ReturnType<typeof os.networkInterfaces>);

    expect(physicalMacAddresses()).toEqual([MAC]);
  });

  it("网卡枚举顺序变了，指纹不变（MAC 去重后排序）", () => {
    const a = {
      en0: [{ internal: false, mac: "aa:aa:aa:aa:aa:aa" }],
      en5: [{ internal: false, mac: "bb:bb:bb:bb:bb:bb" }],
    } as unknown as ReturnType<typeof os.networkInterfaces>;
    const b = {
      en5: [{ internal: false, mac: "bb:bb:bb:bb:bb:bb" }],
      en0: [{ internal: false, mac: "aa:aa:aa:aa:aa:aa" }],
    } as unknown as ReturnType<typeof os.networkInterfaces>;

    networkInterfacesMock.mockReturnValue(a);
    const first = computeDeviceId("linux");
    networkInterfacesMock.mockReturnValue(b);
    const second = computeDeviceId("linux");

    expect(second.deviceId).toEqual(first.deviceId);
  });
});

describe("readSystemAnchor 的边界", () => {
  it("未知平台不报错，返回 undefined 交给降级", () => {
    expect(readSystemAnchor("freebsd")).toBeUndefined();
  });

  it("ioreg 有输出但没有 IOPlatformUUID 字段 → undefined", () => {
    execFileSyncMock.mockReturnValue("+-o J316sAP  <class IOPlatformExpertDevice>\n" as never);
    expect(readSystemAnchor("darwin")).toBeUndefined();
  });
});
