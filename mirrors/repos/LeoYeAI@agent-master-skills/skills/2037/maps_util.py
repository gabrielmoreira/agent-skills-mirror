#!/usr/bin/env python3
"""
Earth2037 地图坐标：tileID / VillageID / CityID ↔ (x, y)
与服务端 Maps 一致。含 ASCII 线框图，供 Skill / AI 阅读。
"""

import math

# 主图 mapId=1：Count=802，坐标轴 ∈ [-400, 401]（与游戏主图一致）
MAIN_COUNT_X = 802
MAIN_MAX = 401
MAIN_MIN = -400

# 小图 mapId=2: 162×162, X/Y ∈ [-80, 81]
MINI_COUNT_X = 162
MINI_MAX = 81
MINI_MIN = -80


def _v_main(x):
    """主图边界环绕"""
    if x > MAIN_MAX:
        return x - MAIN_COUNT_X
    if x < MAIN_MIN:
        return x + MAIN_COUNT_X
    return x


def _v_mini(x):
    """小图边界环绕"""
    if x > MINI_MAX:
        return x - MINI_COUNT_X
    if x < MINI_MIN:
        return x + MINI_COUNT_X
    return x


def get_x(tile_id, mini=False):
    """tileID → X"""
    count = MINI_COUNT_X if mini else MAIN_COUNT_X
    max_val = MINI_MAX if mini else MAIN_MAX
    v_fn = _v_mini if mini else _v_main
    val = ((tile_id % count) + count) % count - max_val
    return v_fn(val)


def get_y(tile_id, mini=False):
    """tileID → Y"""
    x = get_x(tile_id, mini)
    count = MINI_COUNT_X if mini else MAIN_COUNT_X
    max_val = MINI_MAX if mini else MAIN_MAX
    v_fn = _v_mini if mini else _v_main
    val = (max_val + 1) - math.ceil((tile_id - x) / count)
    return v_fn(int(val))


def get_id(x, y, mini=False):
    """(x, y) → tileID"""
    count = MINI_COUNT_X if mini else MAIN_COUNT_X
    max_val = MINI_MAX if mini else MAIN_MAX
    v_fn = _v_mini if mini else _v_main
    return (max_val + 1 - v_fn(y)) * count + v_fn(x) - max_val


def get_xy(tile_id, mini=False):
    """tileID → (x, y)"""
    return get_x(tile_id, mini), get_y(tile_id, mini)


def format_xy(tile_id, mini=False):
    """tileID → 字符串 '(x,y)'"""
    x, y = get_xy(tile_id, mini)
    return f"({x},{y})"


def ascii_map_window(cx, cy, radius=3, mini=False):
    """
    文字线框图：行 = y（上行 y 更大），列 = x 增大方向。
    @ = 中心格，· = 邻格。与服务器 (x,y)/tileID 一致。
    """
    xs = list(range(cx - radius, cx + radius + 1))
    ys = list(range(cy + radius, cy - radius - 1, -1))
    cw = 6
    # 分隔行：6 格 +「+」与数据行「y=xxxx|」末尾的「|」同列（拐角）
    pad = "      "
    # 表头：左侧与「y=xxxx|」同宽；每列必须与数据行一致为「cw 格内容 + |」，少写 | 会每列少 1 格整行错位
    header_pad = " " * len(f"y={0:>4}|")
    lines = []
    tag = "小图 162×162" if mini else "主图 802×802 (mapId=1)"
    lines.append(f"# Earth2037 — {tag}")
    lines.append(f"# 窗口: 中心=({cx},{cy})  半径={radius}  |  x 轴向右为正")
    lines.append("")
    lines.append(header_pad + "".join(f"{x:^{cw}}|" for x in xs))
    row_sep = pad + "+" + "+".join("-" * cw for _ in xs) + "+"
    lines.append(row_sep)
    for y in ys:
        row = f"y={y:>4}|"
        for x in xs:
            ch = "@" if (x == cx and y == cy) else "·"
            row += f"{ch:^{cw}}|"
        lines.append(row)
        lines.append(row_sep)
    lines.append("")
    lines.append(f"# 中心坐标 (x,y) = ({cx},{cy})   # 向玩家只描述坐标，不强调 tileID")
    lines.append("# 图例: @ = 中心; · = 邻格")
    return "\n".join(lines)


def ascii_map_from_tile_id(tile_id, radius=3, mini=False):
    """以 tileID 对应 (x,y) 为中心的 ASCII 窗口。"""
    x, y = get_xy(tile_id, mini)
    return ascii_map_window(x, y, radius=radius, mini=mini)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法:")
        print("  maps_util.py <tileID> [--mini]")
        print("  maps_util.py --id <x> <y> [--mini]")
        print("  maps_util.py --ascii <cx> <cy> [radius] [--mini]   # (x,y) 为中心的文字地图")
        print("  maps_util.py --ascii-tile <tileID> [radius] [--mini]")
        print("  tileID/VillageID/CityID 为同一数值")
        sys.exit(1)
    args = sys.argv[1:]
    mini = "--mini" in args
    if "--mini" in args:
        args.remove("--mini")
    if args[0] == "--ascii" and len(args) >= 3:
        cx, cy = int(args[1]), int(args[2])
        r = 3
        if len(args) >= 4:
            try:
                r = int(args[3])
            except ValueError:
                r = 3
        print(ascii_map_window(cx, cy, radius=r, mini=mini))
    elif args[0] == "--ascii-tile" and len(args) >= 2:
        tid = int(args[1])
        r = 3
        if len(args) >= 3:
            try:
                r = int(args[2])
            except ValueError:
                r = 3
        print(ascii_map_from_tile_id(tid, radius=r, mini=mini))
    elif args[0] == "--id" and len(args) >= 3:
        x, y = int(args[1]), int(args[2])
        print(get_id(x, y, mini))
    else:
        tid = int(args[0])
        x, y = get_xy(tid, mini)
        print(f"(x,y)=({x},{y})   # 玩家可见坐标；tileID={tid} 仅供程序换算")
