#!/usr/bin/env python3
"""
抖音登录 - 通过浏览器扫码获取 Cookie
Cookie 保存到脚本同级目录的 cookies.txt（Netscape 格式，yt-dlp 可直接使用）

用法: python3 douyin-login.py

依赖: pip install playwright && python -m playwright install chromium
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("错误: 需要安装 playwright")
    print("  pip install playwright")
    print("  python -m playwright install chromium")
    sys.exit(1)


SCRIPT_DIR = Path(__file__).parent
COOKIES_TXT = SCRIPT_DIR / "cookies_douyin.txt"
COOKIES_JSON = SCRIPT_DIR / "cookies_douyin.json"
DOUYIN_URL = "https://www.douyin.com"


def cookies_to_netscape(cookies, filepath):
    """将 Cookie 列表转为 Netscape cookies.txt 格式（yt-dlp 使用）"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("# Netscape HTTP Cookie File\n")
        f.write("# https://curl.haxx.se/rfc/cookie_spec.html\n\n")
        for c in cookies:
            domain = c.get("domain", "")
            if not domain.startswith("."):
                domain = "." + domain
            flag = "TRUE"
            path = c.get("path", "/")
            secure = "TRUE" if c.get("secure", False) else "FALSE"
            expires = str(int(c.get("expires", 0)))
            name = c.get("name", "")
            value = c.get("value", "")
            f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expires}\t{name}\t{value}\n")


async def login():
    """打开抖音，等待用户扫码登录，提取 Cookie"""
    print("正在启动浏览器...")
    print("请在浏览器中扫码登录抖音")
    print("登录成功后脚本会自动提取 Cookie 并关闭浏览器\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(DOUYIN_URL, wait_until="domcontentloaded")
        await asyncio.sleep(3)

        # 尝试点击登录按钮，触发登录弹窗
        try:
            login_btn = await page.query_selector('button:has-text("登录")')
            if not login_btn:
                login_btn = await page.query_selector('[data-e2e="user-login"]')
            if not login_btn:
                login_btn = await page.query_selector('text=登录')
            if login_btn:
                await login_btn.click()
                await asyncio.sleep(2)
                print("已弹出登录框，请用抖音 App 扫码")
            else:
                print("未找到登录按钮，请在页面中手动点击登录")
        except Exception:
            print("请在页面中手动点击登录")

        print("等待登录...\n")

        # 等待登录成功：检测页面中出现用户头像或个人信息元素
        # 抖音登录成功后 URL 不变，但页面会出现用户相关元素
        max_wait = 120  # 最多等 2 分钟
        start = time.time()
        logged_in = False

        while time.time() - start < max_wait:
            # 检查是否有登录态的 Cookie（如 sessionid）
            cookies = await context.cookies()
            session_cookies = [c for c in cookies if c["name"] in ("sessionid", "sessionid_ss")]
            if session_cookies and session_cookies[0].get("value"):
                logged_in = True
                break
            await asyncio.sleep(2)

        if not logged_in:
            print("登录超时（2 分钟），请重试")
            await browser.close()
            sys.exit(1)

        # 等一下确保 Cookie 完全写入
        await asyncio.sleep(3)
        all_cookies = await context.cookies()
        await browser.close()

        # 保存为 Netscape 格式（yt-dlp 使用）
        cookies_to_netscape(all_cookies, COOKIES_TXT)

        # 同时保存 JSON 格式（备用）
        with open(COOKIES_JSON, "w", encoding="utf-8") as f:
            json.dump(all_cookies, f, ensure_ascii=False, indent=2)

        douyin_cookies = [c for c in all_cookies if "douyin" in c.get("domain", "")]
        print(f"登录成功，已保存 {len(douyin_cookies)} 个抖音 Cookie")
        print(f"  {COOKIES_TXT}")
        print(f"  {COOKIES_JSON}")


def main():
    asyncio.run(login())


if __name__ == "__main__":
    main()
