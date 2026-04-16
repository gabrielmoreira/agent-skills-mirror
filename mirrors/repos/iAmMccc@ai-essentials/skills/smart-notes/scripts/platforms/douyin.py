"""抖音视频提取模块"""

import asyncio
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COOKIES_JSON = os.path.join(SCRIPT_DIR, "cookies_douyin.json")


def check_cookies():
    if not os.path.exists(COOKIES_JSON):
        return False
    if os.path.getsize(COOKIES_JSON) < 50:
        return False
    return True


def extract_url_from_text(text):
    match = re.search(r"https?://[^\s]+", text)
    return match.group(0).rstrip("/") if match else text


def extract_video_id(url):
    url = url.replace(r"\?", "?").replace(r"\=", "=").replace(r"\&", "&")
    modal_match = re.search(r"modal_id=(\d+)", url)
    if modal_match:
        return modal_match.group(1)
    match = re.search(r"/video/(\d+)", url)
    if match:
        return match.group(1)
    return None


def resolve_video_id(raw_input):
    url = extract_url_from_text(raw_input)
    vid = extract_video_id(url)
    if vid:
        return vid
    if "v.douyin.com" in url or "iesdouyin.com" in url:
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)"
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                return extract_video_id(resp.url)
        except Exception:
            pass
    return None


def fetch_video_info(video_id):
    """通过移动端分享页获取视频元数据（无需登录）"""
    info = {
        "title": "douyin_video", "video_url": None, "author": "",
        "tags": [], "likes": "", "comments_count": "",
        "favorites": "", "shares": "", "publish_time": "",
    }

    share_url = f"https://www.iesdouyin.com/share/video/{video_id}/"
    try:
        req = urllib.request.Request(share_url, headers={
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  请求失败: {e}")
        return info

    def extract(pattern, text, default=""):
        m = re.search(pattern, text)
        return m.group(1) if m else default

    raw_desc = extract(r'"desc":"([^"]*)"', html)
    info["author"] = extract(r'"nickname":"([^"]*)"', html)
    info["likes"] = extract(r'"digg_count":(\d+)', html)
    info["comments_count"] = extract(r'"comment_count":(\d+)', html)
    info["favorites"] = extract(r'"collect_count":(\d+)', html)
    info["shares"] = extract(r'"share_count":(\d+)', html)

    create_time = extract(r'"create_time":(\d+)', html)
    if create_time:
        from datetime import datetime
        info["publish_time"] = datetime.fromtimestamp(int(create_time)).strftime("%Y-%m-%d %H:%M")

    tags = re.findall(r"#(\S+)", raw_desc)
    clean_title = re.sub(r"\s*#\S+", "", raw_desc).strip()
    if not clean_title:
        clean_title = "douyin_video"
    clean_title = re.sub(r'[\\/:*?"<>|\n\r]', '_', clean_title).strip()
    if len(clean_title) > 80:
        clean_title = clean_title[:80]

    info["title"] = clean_title
    info["tags"] = tags

    play_match = re.search(r'"play_addr":\{[^}]*"url_list":\["([^"]+)"', html)
    if play_match:
        video_url = play_match.group(1).replace("\\u002F", "/")
        if not video_url.startswith("http"):
            video_url = "https:" + video_url
        info["video_url"] = video_url

    return info


def download_file(url, output_path):
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Referer": "https://www.douyin.com/"
        })
        with urllib.request.urlopen(req, timeout=120) as resp:
            with open(output_path, "wb") as f:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
        return os.path.getsize(output_path) / (1024 * 1024)
    except Exception:
        return 0


def extract_audio(video_path, audio_path):
    try:
        subprocess.run(
            ["ffmpeg", "-i", video_path, "-vn", "-acodec", "libmp3lame", "-q:a", "4", audio_path, "-y"],
            capture_output=True, check=True, timeout=60
        )
        return True
    except Exception:
        return False


def transcribe_audio(audio_path):
    try:
        import whisper
    except ImportError:
        return None

    model = whisper.load_model("base")
    result = model.transcribe(audio_path, language="zh")
    segments = result.get("segments", [])
    if segments:
        lines = [seg.get("text", "").strip() for seg in segments if seg.get("text", "").strip()]
        return "\n".join(lines)
    return result.get("text", "").strip() or None


async def fetch_comments(url, video_author="", max_scroll=5):
    """用 Playwright 获取评论（需要登录）"""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        return []

    if not os.path.exists(COOKIES_JSON):
        return []

    with open(COOKIES_JSON, "r", encoding="utf-8") as f:
        cookies = json.load(f)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_cookies(cookies)
        page = await context.new_page()

        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(5)

        for i in range(max_scroll):
            await page.evaluate("window.scrollBy(0, 800)")
            await asyncio.sleep(2)

        raw_text = await page.evaluate("""
            () => {
                const container = document.querySelector('[class*="comment-mainContent"]');
                return container ? container.innerText : '';
            }
        """)

        author_tagged = await page.evaluate("""
            () => {
                const tags = document.querySelectorAll('[class*="comment-item-tag-text"]');
                const names = new Set();
                for (const tag of tags) {
                    if (tag.innerText.trim() === '作者') {
                        const wrap = tag.closest('[class*="comment-item-info-wrap"]');
                        if (wrap && wrap.children[0]) {
                            const name = wrap.children[0].innerText.trim().replace('\\n作者', '').trim();
                            names.add(name);
                        }
                    }
                }
                return Array.from(names);
            }
        """)

        await browser.close()

        author_names = set(author_tagged or [])
        if video_author:
            author_names.add(video_author)

        return parse_comment_text(raw_text, author_names)


def parse_comment_text(raw_text, author_names=None):
    if not raw_text or not raw_text.strip():
        return []

    author_names = author_names or set()
    comments = []
    lines = raw_text.strip().split("\n")

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line in ("分享", "回复", "加载中", "全部评论", "...") or line.startswith("展开"):
            i += 1
            continue
        if re.match(r"^\d+.*前·", line) or re.match(r"^\d{4}-", line):
            i += 1
            continue
        if re.match(r"^\d+$", line):
            i += 1
            continue
        if line == "作者":
            i += 1
            continue

        author = line
        content = ""
        j = i + 1
        while j < len(lines):
            next_line = lines[j].strip()
            if next_line == "..." or next_line == "作者" or not next_line:
                j += 1
                continue
            if re.match(r"^\d+.*前·", next_line) or re.match(r"^\d{4}-", next_line):
                break
            if next_line in ("分享", "回复") or re.match(r"^\d+$", next_line):
                break
            if next_line.startswith("展开"):
                break
            content = next_line
            break

        if content and len(content) > 1:
            likes = "0"
            for k in range(j, min(j + 5, len(lines))):
                lk = lines[k].strip()
                if re.match(r"^\d+$", lk):
                    likes = lk
                    break

            is_author = author in author_names
            comments.append({
                "author": author, "content": content,
                "likes": likes, "is_author": is_author
            })

        i = j + 1 if j > i else i + 1

    return comments


def save_comments(comments, raw_dir):
    if not comments:
        return
    json_path = os.path.join(raw_dir, "comments.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)

    txt_path = os.path.join(raw_dir, "comments.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        for c in comments:
            author = c.get("author", "匿名")
            content = c.get("content", "")
            likes = c.get("likes", "0")
            tag = "（作者）" if c.get("is_author") else ""
            f.write(f"[{author}]{tag} {content}")
            if likes and likes != "0":
                f.write(f"  ({likes} 赞)")
            f.write("\n")


def run(url, raw_dir, no_login=False):
    """抖音提取主流程，返回 (content_info, transcript, comments_text)"""
    # 解析视频 ID
    print(f"· 解析链接...", end="", flush=True)
    video_id = resolve_video_id(url)
    if not video_id:
        print("失败（无法提取视频 ID）")
        sys.exit(1)
    clean_url = f"https://www.douyin.com/video/{video_id}"
    print(f"完成")

    # 获取元数据
    print(f"· 获取视频信息...", end="", flush=True)
    info = fetch_video_info(video_id)
    if not info["video_url"]:
        print("失败（无法获取视频地址）")
        sys.exit(1)
    print("完成")

    # 显示视频信息
    print("")
    print("── 视频信息 ──────────────────")
    print(f"  标题: {info['title']}")
    if info["author"]:
        print(f"  作者: {info['author']}")
    if info["likes"]:
        print(f"  数据: {info['likes']} 赞 · {info['comments_count']} 评论 · {info['favorites']} 收藏 · {info['shares']} 转发")
    if info["tags"]:
        print(f"  标签: {', '.join(info['tags'])}")
    if info["publish_time"]:
        print(f"  发布: {info['publish_time']}")
    print("")

    # 文件路径
    video_path = os.path.join(raw_dir, "video.mp4")
    audio_path = os.path.join(raw_dir, "audio.mp3")
    transcript_path = os.path.join(raw_dir, "transcript.txt")

    has_transcript = os.path.exists(transcript_path) and os.path.getsize(transcript_path) > 10

    if has_transcript:
        print("· 检测到已有字幕，跳过下载和转写")
        transcript = Path(transcript_path).read_text(encoding="utf-8")
    else:
        has_audio = os.path.exists(audio_path) and os.path.getsize(audio_path) > 1000
        if has_audio:
            print("· 检测到已有音频，跳过下载")
        else:
            print("· 下载视频...", end="", flush=True)
            size = download_file(info["video_url"], video_path)
            if size == 0:
                print("失败")
                sys.exit(1)
            print(f"完成（{size:.1f} MB）")

            print("· 提取音频...", end="", flush=True)
            if not extract_audio(video_path, audio_path):
                audio_path = video_path
                print("跳过（直接使用视频文件）")
            else:
                audio_size = os.path.getsize(audio_path) / (1024 * 1024)
                print(f"完成（{audio_size:.1f} MB）")

        import warnings
        print("· 转为文字...", end="", flush=True)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            transcript = transcribe_audio(audio_path)
        if not transcript:
            print("失败")
            sys.exit(1)
        print(f"完成（{len(transcript)} 字）")

        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)

    # 评论获取（交互式）
    comments_text = ""
    comments_txt_path = os.path.join(raw_dir, "comments.txt")
    comments_json_path = os.path.join(raw_dir, "comments.json")

    if os.path.exists(comments_txt_path):
        print("· 检测到已有评论，跳过获取")
        comments_text = Path(comments_txt_path).read_text(encoding="utf-8").strip()
    elif not no_login:
        print("")
        try:
            choice = input("是否登录抖音获取评论内容？(y/n) [默认 n]：").strip().lower()
        except (EOFError, KeyboardInterrupt):
            choice = "n"

        if choice in ("y", "yes"):
            if not check_cookies():
                print("· 正在启动登录...")
                import subprocess as _sp
                login_script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "douyin-login.py")
                _sp.run([sys.executable, login_script])

            if check_cookies():
                print("· 获取评论...", end="", flush=True)
                comments = asyncio.run(fetch_comments(clean_url, video_author=info["author"]))
                if comments:
                    save_comments(comments, raw_dir)
                    print(f"完成（{len(comments)} 条）")
                    comments_text = Path(comments_txt_path).read_text(encoding="utf-8").strip()
                else:
                    print("无评论")
        else:
            print("· 跳过评论获取")

    info["url"] = clean_url
    return info, transcript, comments_text
