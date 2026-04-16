"""微信公众号文章提取模块"""

import os
import re
import sys
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None


def fetch_article(url):
    """抓取微信公众号文章内容"""
    if not requests or not BeautifulSoup:
        print("错误: 需要安装 requests 和 beautifulsoup4")
        sys.exit(1)

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = resp.apparent_encoding or "utf-8"
        resp.raise_for_status()
    except Exception as e:
        print(f"  请求失败: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    info = {
        "title": "",
        "author": "",
        "publish_time": "",
        "tags": [],
        "url": url,
    }

    # 标题
    title_el = soup.find("h1", id="activity-name") or soup.find("h1")
    if title_el:
        info["title"] = title_el.get_text(strip=True)

    # 作者
    author_el = soup.find("a", id="js_name") or soup.find("span", class_="rich_media_meta_nickname")
    if author_el:
        info["author"] = author_el.get_text(strip=True)

    # 发布时间
    time_el = soup.find("em", id="publish_time")
    if time_el:
        info["publish_time"] = time_el.get_text(strip=True)

    # 正文
    content_el = soup.find("div", id="js_content") or soup.find("div", class_="rich_media_content")
    if content_el:
        # 去掉图片alt、脚本等
        for tag in content_el.find_all(["script", "style"]):
            tag.decompose()

        # 提取文本，保留段落换行
        paragraphs = []
        for el in content_el.find_all(["p", "section", "h1", "h2", "h3", "h4", "li"]):
            text = el.get_text(strip=True)
            if text:
                paragraphs.append(text)

        content = "\n\n".join(paragraphs)
    else:
        content = ""

    # 清理标题
    if info["title"]:
        info["title"] = re.sub(r'[\\/:*?"<>|\n\r]', '_', info["title"]).strip()
        if len(info["title"]) > 80:
            info["title"] = info["title"][:80]
    else:
        info["title"] = "wechat_article"

    return info, content


def run(url, raw_dir, no_login=False):
    """微信文章提取主流程，返回 (content_info, text, comments_text)"""
    print(f"· 获取文章内容...", end="", flush=True)
    result = fetch_article(url)
    if not result:
        print("失败")
        sys.exit(1)

    info, content = result
    if not content:
        print("失败（无法提取正文）")
        sys.exit(1)
    print(f"完成（{len(content)} 字）")

    # 显示文章信息
    print("")
    print("── 文章信息 ──────────────────")
    print(f"  标题: {info['title']}")
    if info["author"]:
        print(f"  作者: {info['author']}")
    if info["publish_time"]:
        print(f"  发布: {info['publish_time']}")
    print("")

    # 保存正文
    content_path = os.path.join(raw_dir, "content.md")
    with open(content_path, "w", encoding="utf-8") as f:
        f.write(content)

    info["url"] = url
    return info, content, ""  # 微信文章暂不获取评论
