import crypto from 'crypto';
import { execFileSync } from 'child_process';
import fs from 'fs';
import os from 'os';

/**
 * 匿名设备指纹。
 *
 * 为什么要有这个文件：旧实现是 `sha256(hostname | CPU model | 全部非内部网卡 MAC)`，
 * 锚点选错了 —— macOS 开着「私有 Wi-Fi 地址」时每个 SSID 一个随机 MAC，`awdl0` / `llw0` /
 * `bridge0` 的 MAC 随系统状态漂移，容器里 hostname 和 MAC 每次重建都变。结果是同一台 Mac
 * 一天能上报成几十个「设备」（2026-10-26 实测：Mac 指纹 82% 只在那一天出现过，
 * Windows 同口径 22%）。
 *
 * 现在的取值顺序：
 * 1. 系统级不可变标识 —— macOS `IOPlatformUUID`、Windows `MachineGuid`、Linux `/etc/machine-id`；
 * 2. 取不到时退到 `hostname + CPU model + 过滤后的物理网卡 MAC`；
 * 3. 再取不到只留 `hostname + CPU model`。
 *
 * 三条纪律：
 * - **格式不变**：仍是 SHA256 前 32 位 hex，灯塔 `A2` 字段与后端都不用改。
 * - **绝不用随机数兜底**。旧实现取不到信息时 `crypto.randomBytes(16)`，等于每次启动都是
 *   一台新设备 —— 正是要消灭的行为。宁可所有机器共用一个弱指纹，也不要一堆假设备。
 * - **只在构造时跑一次**。锚点要起子进程（`ioreg` / `reg`），1s 超时就降级，
 *   绝不放进每次上报的路径。
 *
 * 口径变化（换锚点当天就会看到，报表侧要提前打招呼）：
 * - 历史 `A2` 全部失效，老设备会以新指纹重新出现 —— 报表上「装机量跳一下」不是增长。
 * - 容器内多实例若共享镜像固化的 `/etc/machine-id`，会被合并成同一台设备（以前是各算一个新设备）。
 */

/** 取系统级锚点的子进程超时：超了直接降级，不能拖慢进程启动 */
const ANCHOR_TIMEOUT_MS = 1000;

/**
 * 虚拟 / 隧道网卡名前缀（小写比较）。这些接口的 MAC 会随系统状态漂移或每次重建都变，
 * 拼进指纹就等于给同一台机器发新身份。
 */
const VIRTUAL_NIC_PREFIXES = [
    'awdl', // Apple Wireless Direct Link
    'llw', // Apple 低延迟 WLAN
    'bridge', // macOS / Windows 网桥
    'utun', // macOS / iOS VPN 隧道
    'tun',
    'tap',
    'veth', // 容器 veth pair
    'docker',
    'br-', // docker bridge
    'vmnet', // VMware
    'vboxnet', // VirtualBox
    'vether', // Hyper-V 虚拟交换机（vEthernet）
    'zt', // ZeroTier
    'tailscale',
    'wg', // WireGuard
    'lo', // loopback（正常情况下 internal 已过滤，兜一层）
];

export type DeviceAnchorSource =
    /** macOS `IOPlatformUUID` */
    | 'platform-uuid'
    /** Windows `HKLM\SOFTWARE\Microsoft\Cryptography\MachineGuid` */
    | 'machine-guid'
    /** Linux `/etc/machine-id`（或 `/var/lib/dbus/machine-id`） */
    | 'machine-id'
    /** 锚点取不到：hostname + CPU model + 过滤后的物理网卡 MAC */
    | 'host-fallback'
    /** 连网卡都取不到：hostname + CPU model */
    | 'host-only';

export type DeviceAnchor = {
    /** 参与哈希的原始串（不含任何明文上报，只进 sha256） */
    value: string;
    source: DeviceAnchorSource;
};

function sha256Short(input: string): string {
    return crypto.createHash('sha256').update(input).digest('hex').substring(0, 32);
}

/** `machine-id` 合法值：16–64 位 hex，且不能是全 0（有些镜像里就是全 0 的空壳） */
function isUsableMachineId(value: string): boolean {
    if (!/^[0-9a-f]{16,64}$/i.test(value)) {
        return false;
    }
    return !/^0+$/.test(value);
}

function readFileQuietly(filePath: string): string | undefined {
    try {
        return fs.readFileSync(filePath, 'utf8').trim();
    } catch {
        return undefined;
    }
}

/** 起一次子进程读锚点。超时 / 不存在 / 权限不足一律返回 undefined，由调用方降级。 */
function execQuietly(file: string, args: string[]): string | undefined {
    try {
        return execFileSync(file, args, {
            timeout: ANCHOR_TIMEOUT_MS,
            encoding: 'utf8',
            // 子进程的 stderr 全部吞掉：`ioreg` 在受限环境会打噪音，`reg` 在 32 位 Node
            // 下可能报找不到键，这些都不该出现在 MCP 的 stdout（stdio transport 上是协议流）
            stdio: ['ignore', 'pipe', 'ignore'],
            windowsHide: true,
        });
    } catch {
        return undefined;
    }
}

/**
 * 读系统级不可变标识。**只读一次**，失败即降级。
 * `platform` 参数只为测试注入，正常运行不传。
 */
export function readSystemAnchor(platform: string = process.platform): DeviceAnchor | undefined {
    if (platform === 'darwin') {
        const out = execQuietly('ioreg', ['-rd1', '-c', 'IOPlatformExpertDevice']);
        const matched = out && /"IOPlatformUUID"\s*=\s*"([^"]+)"/.exec(out);
        if (matched?.[1]) {
            return { value: matched[1].trim(), source: 'platform-uuid' };
        }
        return undefined;
    }

    if (platform === 'win32') {
        const out = execQuietly('reg', [
            'query',
            'HKLM\\SOFTWARE\\Microsoft\\Cryptography',
            '/v',
            'MachineGuid',
        ]);
        // 形如：`    MachineGuid    REG_SZ    3f2a....`（分隔符是多个空格或 tab）
        const matched = out && /MachineGuid\s+REG_SZ\s+([0-9a-fA-F-]{8,})/.exec(out);
        if (matched?.[1]) {
            return { value: matched[1].trim().toLowerCase(), source: 'machine-guid' };
        }
        return undefined;
    }

    // linux / openharmony / 其他类 Unix：先 /etc/machine-id，再 dbus 那份
    for (const candidate of ['/etc/machine-id', '/var/lib/dbus/machine-id']) {
        const raw = readFileQuietly(candidate);
        if (raw && isUsableMachineId(raw)) {
            return { value: raw.toLowerCase(), source: 'machine-id' };
        }
    }

    return undefined;
}

function isVirtualNic(name: string): boolean {
    const lower = name.toLowerCase();
    return VIRTUAL_NIC_PREFIXES.some((prefix) => lower.startsWith(prefix));
}

/**
 * 非内部、非虚拟、MAC 不是全 0 / 广播地址的网卡 MAC，去重后排序。
 * 排序是为了让指纹与网卡枚举顺序无关（枚举顺序在重启后可能变）。
 */
export function physicalMacAddresses(interfaces: ReturnType<typeof os.networkInterfaces> = os.networkInterfaces()): string[] {
    const macs = new Set<string>();
    for (const [name, list] of Object.entries(interfaces)) {
        if (!list || isVirtualNic(name)) {
            continue;
        }
        for (const nic of list) {
            const mac = nic?.mac?.toLowerCase();
            if (!nic || nic.internal || !mac) {
                continue;
            }
            if (mac === '00:00:00:00:00:00' || mac === 'ff:ff:ff:ff:ff:ff') {
                continue;
            }
            macs.add(mac);
        }
    }
    return [...macs].sort();
}

/** 取不到系统锚点时的兜底信号：**不含虚拟网卡**，主机名与 CPU 型号足够稳。 */
export function collectHostSignal(): DeviceAnchor {
    let hostname = 'unknown-host';
    try {
        hostname = os.hostname() || hostname;
    } catch {
        // 主机名读不到不影响降级：CPU + MAC 仍可用
    }

    let cpu = '';
    try {
        cpu = os
            .cpus()
            .map((item) => item.model)
            .join(',');
    } catch {
        // 同上
    }

    let macs: string[] = [];
    try {
        macs = physicalMacAddresses();
    } catch {
        // 同上
    }

    const parts = [hostname, cpu, ...macs].filter((part) => Boolean(part));
    return {
        value: parts.join('|'),
        source: macs.length > 0 ? 'host-fallback' : 'host-only',
    };
}

/**
 * 计算匿名设备指纹（SHA256 前 32 位 hex），并返回这次用的锚点来源 ——
 * 来源只进 debug 日志，用于上线后确认「到底有多少机器走到了兜底」。
 */
export function computeDeviceId(platform: string = process.platform): { deviceId: string; source: DeviceAnchorSource } {
    const anchor = readSystemAnchor(platform) ?? collectHostSignal();
    return { deviceId: sha256Short(anchor.value), source: anchor.source };
}
