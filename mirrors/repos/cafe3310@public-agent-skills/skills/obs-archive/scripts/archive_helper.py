#!/usr/bin/env python3
"""
archive_helper.py
辅助将外部链接（X/Twitter、视频站点、互联网文章）或本地文件（文档、视频、图片、演示文稿）
获取、本地化并归档至 Obsidian 仓库的附件目录。
"""

import argparse
import dataclasses
from dataclasses import dataclass, field
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# 数据结构定义
# ---------------------------------------------------------------------------

@dataclass
class VaultConfig:
    vault_path: str
    note_dir: str
    attachment_dir: str
    attachment_folder_setting: str
    agents_md_path: Optional[str] = None


@dataclass
class FetchedAsset:
    temp_path: str
    original_source: str
    media_type: str  # image | video | audio | document | presentation | other
    should_move: bool


@dataclass
class ArticleImageRef:
    original_url: str
    temp_path: str


@dataclass
class FetchResult:
    input_source: str
    source_kind: str  # local_file | twitter | video | article
    site_name: str = ""
    title: str = ""
    author: str = ""
    published_at: str = ""
    description: str = ""
    article_md_path: Optional[str] = None
    subtitle_paths: List[str] = field(default_factory=list)
    assets: List[FetchedAsset] = field(default_factory=list)
    article_images: List[ArticleImageRef] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class StagedAsset:
    source_path: str
    final_path: str
    attachment_name: str
    action: str  # moved | copied
    media_type: str
    obsidian_embed: str


@dataclass
class StageResult:
    vault_path: str
    note_dir: str
    attachment_dir: str
    note_suggested_filename: str
    note_suggested_path: str
    staged_assets: List[StagedAsset] = field(default_factory=list)
    localized_article_md_path: Optional[str] = None


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".heic", ".avif"}
VIDEO_EXTS = {".mp4", ".mkv", ".webm", ".mov", ".m4v", ".avi"}
AUDIO_EXTS = {".mp3", ".m4a", ".wav", ".flac", ".ogg", ".aac"}
PRESENTATION_EXTS = {".pptx", ".ppt", ".key"}
DOCUMENT_EXTS = {".pdf", ".docx", ".doc", ".epub", ".txt", ".md", ".csv", ".xlsx"}


def classify_media_type(filepath: str) -> str:
    ext = os.path.splitext(filepath)[1].lower()
    if ext in IMAGE_EXTS:
        return "image"
    if ext in VIDEO_EXTS:
        return "video"
    if ext in AUDIO_EXTS:
        return "audio"
    if ext in PRESENTATION_EXTS:
        return "presentation"
    if ext in DOCUMENT_EXTS:
        return "document"
    return "other"


def sanitize_slug(text: str, max_len: int = 40) -> str:
    cleaned = re.sub(r'[\\/*?:"<>|\r\n\t]+', " ", text).strip()
    cleaned = re.sub(r"\s+", "-", cleaned)
    return cleaned[:max_len].strip("-") or "artifact"


def is_in_desktop_or_downloads(filepath: str) -> bool:
    real_p = os.path.realpath(os.path.expanduser(filepath))
    desktop = os.path.realpath(os.path.expanduser("~/Desktop"))
    downloads = os.path.realpath(os.path.expanduser("~/Downloads"))
    return (
        real_p.startswith(desktop + os.sep)
        or real_p.startswith(downloads + os.sep)
    )


def detect_source_kind(input_str: str) -> str:
    if not (input_str.startswith("http://") or input_str.startswith("https://")):
        return "local_file"
    parsed = urllib.parse.urlparse(input_str)
    host = parsed.netloc.lower()
    if any(h in host for h in ("x.com", "twitter.com", "fxtwitter.com", "vxtwitter.com")):
        return "twitter"
    if any(h in host for h in ("youtube.com", "youtu.be", "bilibili.com", "b23.tv", "vimeo.com")):
        return "video"
    return "article"


def infer_site_name(input_str: str) -> str:
    if not (input_str.startswith("http://") or input_str.startswith("https://")):
        return "Local"
    host = urllib.parse.urlparse(input_str).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    mapping = {
        "github.com": "GitHub",
        "raw.githubusercontent.com": "GitHub",
        "x.com": "X",
        "twitter.com": "X",
        "fxtwitter.com": "X",
        "vxtwitter.com": "X",
        "youtube.com": "YouTube",
        "youtu.be": "YouTube",
        "bilibili.com": "Bilibili",
        "b23.tv": "Bilibili",
        "arxiv.org": "arXiv",
        "mp.weixin.qq.com": "WeChat",
        "zhihu.com": "Zhihu",
        "zhuanlan.zhihu.com": "Zhihu",
        "xiaohongshu.com": "Xiaohongshu",
        "news.ycombinator.com": "HackerNews",
        "huggingface.co": "HuggingFace",
    }
    for domain, label in mapping.items():
        if host == domain or host.endswith("." + domain):
            return label
    base = host.split(".")[0]
    return base.capitalize() if base else "Web"


# ---------------------------------------------------------------------------
# 1. Vault 与附件目录解析
# ---------------------------------------------------------------------------

def find_vault_path(explicit_vault: Optional[str] = None, preferred_name: str = "obsidian-agi") -> str:
    if explicit_vault:
        expanded = os.path.abspath(os.path.expanduser(explicit_vault))
        if os.path.isdir(expanded):
            return expanded

    # 1. 检查当前工作目录或其父目录是否本身就是 Obsidian 仓库
    curr = os.path.abspath(os.getcwd())
    while curr and curr != os.path.dirname(curr):
        if os.path.isdir(os.path.join(curr, ".obsidian")):
            return curr
        curr = os.path.dirname(curr)

    # 2. 读取 Obsidian 全局注册表 obsidian.json 查找 preferred_name (默认 obsidian-agi)
    obsidian_json_candidates = [
        os.path.expanduser("~/Library/Application Support/obsidian/obsidian.json"),
        os.path.expanduser("~/.config/obsidian/obsidian.json"),
    ]
    fallback_open_vault = None
    for cfg_path in obsidian_json_candidates:
        if os.path.isfile(cfg_path):
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                vaults = data.get("vaults", {})
                for _, vinfo in vaults.items():
                    vpath = vinfo.get("path", "")
                    if not vpath or not os.path.isdir(vpath):
                        continue
                    if os.path.basename(vpath.rstrip("/")) == preferred_name:
                        return vpath
                    if vinfo.get("open"):
                        fallback_open_vault = vpath
                    elif not fallback_open_vault:
                        fallback_open_vault = vpath
            except Exception:
                pass

    # 3. 检查常用路径下的 obsidian-agi 或常用仓库
    common_candidates = [
        f"~/Library/Mobile Documents/iCloud~md~obsidian/Documents/{preferred_name}",
        f"~/workspace/{preferred_name}",
        f"~/Documents/{preferred_name}",
        f"~/{preferred_name}",
        "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/cafe3310-db",
    ]
    for cand in common_candidates:
        expanded = os.path.expanduser(cand)
        if os.path.isdir(expanded):
            return expanded

    if fallback_open_vault:
        return fallback_open_vault

    raise FileNotFoundError(
        f"无法自动定位 Obsidian 仓库（如 {preferred_name}），请通过 --vault 指定仓库路径。"
    )


def resolve_vault_config(
    explicit_vault: Optional[str] = None,
    note_dir: Optional[str] = None,
    preferred_name: str = "obsidian-agi",
) -> VaultConfig:
    vault_path = find_vault_path(explicit_vault, preferred_name=preferred_name)
    default_archive_dir = os.path.join(vault_path, "cafe3310", "archives")
    target_note_dir = os.path.abspath(os.path.expanduser(note_dir)) if note_dir else default_archive_dir

    app_json_path = os.path.join(vault_path, ".obsidian", "app.json")
    attachment_setting = "_attachments"
    if os.path.isfile(app_json_path):
        try:
            with open(app_json_path, "r", encoding="utf-8") as f:
                app_cfg = json.load(f)
            attachment_setting = app_cfg.get("attachmentFolderPath", "/")
        except Exception:
            pass

    if not attachment_setting or attachment_setting == "/":
        attachment_dir = vault_path
    elif attachment_setting == "./":
        attachment_dir = target_note_dir
    elif attachment_setting.startswith("./"):
        sub = attachment_setting[2:].strip("/")
        attachment_dir = os.path.join(target_note_dir, sub)
    else:
        sub = attachment_setting.lstrip("/")
        attachment_dir = os.path.join(vault_path, sub)

    agents_md_path = None
    for name in ("AGENTS.md", "agents.md", "GEMINI.md"):
        candidate = os.path.join(vault_path, name)
        if os.path.isfile(candidate):
            agents_md_path = candidate
            break

    return VaultConfig(
        vault_path=vault_path,
        note_dir=target_note_dir,
        attachment_dir=attachment_dir,
        attachment_folder_setting=attachment_setting,
        agents_md_path=agents_md_path,
    )


# ---------------------------------------------------------------------------
# 2. 获取与本地化 (Fetch)
# ---------------------------------------------------------------------------

def download_binary(url: str, dest_path: str, referer: Optional[str] = None) -> bool:
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
        }
        if referer:
            headers["Referer"] = referer
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            with open(dest_path, "wb") as out:
                shutil.copyfileobj(resp, out)
        return True
    except Exception:
        return False


def fetch_local_file(input_path: str) -> FetchResult:
    abs_path = os.path.abspath(os.path.expanduser(input_path))
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"找不到本地文件: {abs_path}")

    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(abs_path)).strftime("%Y-%m-%d %H:%M")
    mtype = classify_media_type(abs_path)
    should_move = is_in_desktop_or_downloads(abs_path)

    asset = FetchedAsset(
        temp_path=abs_path,
        original_source=abs_path,
        media_type=mtype,
        should_move=should_move,
    )
    return FetchResult(
        input_source=abs_path,
        source_kind="local_file",
        title=os.path.splitext(os.path.basename(abs_path))[0],
        published_at=mtime,
        assets=[asset],
    )


def fetch_twitter(url: str, work_dir: str, cookies_from_browser: Optional[str] = None) -> FetchResult:
    os.makedirs(work_dir, exist_ok=True)
    res = FetchResult(input_source=url, source_kind="twitter")

    # 1. 使用 gallery-dl 下载图片与元数据
    gdl_cmd = ["gallery-dl", "--write-metadata", "-D", work_dir]
    if cookies_from_browser:
        gdl_cmd.extend(["--cookies-from-browser", cookies_from_browser])
    gdl_cmd.append(url)

    gdl_proc = subprocess.run(gdl_cmd, capture_output=True, text=True)
    if gdl_proc.returncode != 0:
        res.warnings.append(f"gallery-dl 返回非零状态: {gdl_proc.stderr.strip()[:200]}")

    # 2. 使用 yt-dlp 尝试抓取可能存在的推文视频与 info.json
    yt_cmd = [
        "yt-dlp",
        "--write-info-json",
        "--no-playlist",
        "-f",
        "bestvideo+bestaudio/best",
        "-o",
        os.path.join(work_dir, "yt_%(id)s.%(ext)s"),
    ]
    if cookies_from_browser:
        yt_cmd.extend(["--cookies-from-browser", cookies_from_browser])
    yt_cmd.append(url)
    subprocess.run(yt_cmd, capture_output=True, text=True)

    # 3. 解析元数据与收集媒体文件
    for fname in sorted(os.listdir(work_dir)):
        fpath = os.path.join(work_dir, fname)
        if not os.path.isfile(fpath):
            continue
        if fname.endswith(".json"):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                if not res.description:
                    res.description = meta.get("content") or meta.get("description") or ""
                if not res.author:
                    author_obj = meta.get("author")
                    if isinstance(author_obj, dict):
                        res.author = author_obj.get("name") or author_obj.get("nick") or ""
                    else:
                        res.author = meta.get("uploader") or meta.get("uploader_id") or ""
                if not res.published_at:
                    res.published_at = meta.get("date") or meta.get("upload_date") or ""
                if not res.title:
                    res.title = meta.get("title") or (res.description[:40] if res.description else "Twitter-Post")
            except Exception:
                pass
        elif not fname.endswith((".part", ".ytdl")):
            mtype = classify_media_type(fpath)
            if mtype in ("image", "video", "audio"):
                res.assets.append(
                    FetchedAsset(
                        temp_path=fpath,
                        original_source=url,
                        media_type=mtype,
                        should_move=True,
                    )
                )

    return res


def fetch_video(url: str, work_dir: str, cookies_from_browser: Optional[str] = None) -> FetchResult:
    os.makedirs(work_dir, exist_ok=True)
    res = FetchResult(input_source=url, source_kind="video")

    yt_cmd = [
        "yt-dlp",
        "--write-info-json",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs",
        "zh.*,en.*",
        "--no-playlist",
        "-f",
        "bestvideo+bestaudio/best",
        "-o",
        os.path.join(work_dir, "%(id)s.%(ext)s"),
    ]
    if cookies_from_browser:
        yt_cmd.extend(["--cookies-from-browser", cookies_from_browser])
    yt_cmd.append(url)

    proc = subprocess.run(yt_cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        res.warnings.append(f"yt-dlp 警告或错误: {proc.stderr.strip()[:240]}")

    for fname in sorted(os.listdir(work_dir)):
        fpath = os.path.join(work_dir, fname)
        if not os.path.isfile(fpath):
            continue
        if fname.endswith(".info.json"):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                res.title = meta.get("title") or ""
                res.author = meta.get("uploader") or meta.get("channel") or ""
                res.published_at = meta.get("upload_date") or ""
                res.description = meta.get("description") or ""
            except Exception:
                pass
        elif fname.endswith((".vtt", ".srt", ".ass")):
            res.subtitle_paths.append(fpath)
        elif not fname.endswith((".json", ".part", ".ytdl")):
            mtype = classify_media_type(fpath)
            if mtype in ("video", "audio", "image"):
                res.assets.append(
                    FetchedAsset(
                        temp_path=fpath,
                        original_source=url,
                        media_type=mtype,
                        should_move=True,
                    )
                )

    return res


def find_markdown_new_script() -> Optional[str]:
    candidates = [
        os.path.expanduser("~/.gemini/config/skills/markdown-new/scripts/markdown_convert.py"),
        os.path.expanduser("~/.agents/skills/markdown-new/scripts/markdown_convert.py"),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../markdown-new/scripts/markdown_convert.py")),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


def github_blob_to_raw(url: str) -> Optional[str]:
    """将 GitHub blob 页面链接转换为 raw.githubusercontent.com 原始文件链接。"""
    m = re.match(r"^https?://github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)$", url)
    if m:
        owner, repo, ref, path = m.groups()
        return f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}"
    return None


def fetch_article(url: str, work_dir: str) -> FetchResult:
    os.makedirs(work_dir, exist_ok=True)
    res = FetchResult(input_source=url, source_kind="article")
    raw_md_path = os.path.join(work_dir, "article_raw.md")

    md_content = ""
    gh_raw_url = github_blob_to_raw(url)
    if gh_raw_url and download_binary(gh_raw_url, raw_md_path):
        try:
            with open(raw_md_path, "r", encoding="utf-8") as f:
                md_content = f.read()
        except Exception:
            md_content = ""

    md_new_script = find_markdown_new_script()
    if not md_content and md_new_script:
        cmd = [
            sys.executable,
            md_new_script,
            "convert",
            "--url",
            url,
            "--retain-images",
            "-o",
            raw_md_path,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode == 0 and os.path.isfile(raw_md_path):
            with open(raw_md_path, "r", encoding="utf-8") as f:
                md_content = f.read()
        else:
            res.warnings.append("markdown-new 转换失败，回退至本地抓取 + pandoc 转换。")

    if not md_content:
        html_path = os.path.join(work_dir, "page.html")
        if download_binary(url, html_path):
            pandoc_cmd = ["pandoc", "-f", "html", "-t", "gfm-raw_html", html_path, "-o", raw_md_path]
            subprocess.run(pandoc_cmd, capture_output=True, text=True)
            if os.path.isfile(raw_md_path):
                with open(raw_md_path, "r", encoding="utf-8") as f:
                    md_content = f.read()

    if not md_content:
        res.warnings.append("未能通过自动工具提取网页正文，建议调用 agent-browser 提取。")
        return res

    res.article_md_path = raw_md_path

    # 提取标题
    title_match = re.search(r"^#\s+(.+)$", md_content, re.MULTILINE)
    if title_match:
        res.title = title_match.group(1).strip()

    # 提取并下载文章内的远程图片
    img_dir = os.path.join(work_dir, "article_images")
    os.makedirs(img_dir, exist_ok=True)

    # 匹配 Markdown 图片 ![alt](url)
    md_img_pattern = re.compile(r"!\[[^\]]*\]\((https?://[^\s\)]+)\)")
    found_urls: List[str] = []
    for m in md_img_pattern.finditer(md_content):
        img_url = m.group(1).strip()
        if img_url not in found_urls:
            found_urls.append(img_url)

    for idx, img_url in enumerate(found_urls, start=1):
        parsed_u = urllib.parse.urlparse(img_url)
        ext = os.path.splitext(parsed_u.path)[1].lower()
        if ext not in IMAGE_EXTS:
            ext = ".jpg"
        temp_img = os.path.join(img_dir, f"img_{idx:02d}{ext}")
        if download_binary(img_url, temp_img, referer=url):
            res.article_images.append(ArticleImageRef(original_url=img_url, temp_path=temp_img))

    return res


# ---------------------------------------------------------------------------
# 3. 归档附件入库与原文链接重写 (Stage Assets)
# ---------------------------------------------------------------------------

def stage_single_file(
    src_path: str,
    attachment_dir: str,
    dest_filename: str,
    force_move: Optional[bool] = None,
) -> StagedAsset:
    os.makedirs(attachment_dir, exist_ok=True)
    dest_path = os.path.join(attachment_dir, dest_filename)

    # 决定移动还是复制：桌面或下载目录默认移动，临时目录默认移动，其余目录默认复制
    should_move = force_move if force_move is not None else is_in_desktop_or_downloads(src_path)

    if os.path.abspath(src_path) == os.path.abspath(dest_path):
        action = "kept"
    elif should_move:
        shutil.move(src_path, dest_path)
        action = "moved"
    else:
        shutil.copy2(src_path, dest_path)
        action = "copied"

    return StagedAsset(
        source_path=src_path,
        final_path=dest_path,
        attachment_name=dest_filename,
        action=action,
        media_type=classify_media_type(dest_path),
        obsidian_embed=f"![[{dest_filename}]]",
    )


def run_stage_assets(
    vault_cfg: VaultConfig,
    slug: str,
    timestamp_hour: str,
    site: Optional[str] = None,
    work_dir: Optional[str] = None,
    extra_files: Optional[List[str]] = None,
) -> StageResult:
    try:
        os.makedirs(vault_cfg.note_dir, exist_ok=True)
    except OSError:
        pass
    clean_slug = sanitize_slug(slug)

    inferred_site = site
    if not inferred_site and work_dir:
        manifest_path = os.path.join(work_dir, "fetch_manifest.json")
        if os.path.isfile(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    mdata = json.load(f)
                inferred_site = mdata.get("site_name") or infer_site_name(mdata.get("input_source", ""))
            except Exception:
                pass

    slug_str = slug.strip()
    if inferred_site and not slug_str.startswith(f"{inferred_site} -"):
        note_filename = f"{timestamp_hour} {inferred_site} - {slug_str}.md"
    else:
        note_filename = f"{timestamp_hour} {slug_str}.md"

    result = StageResult(
        vault_path=vault_cfg.vault_path,
        note_dir=vault_cfg.note_dir,
        attachment_dir=vault_cfg.attachment_dir,
        note_suggested_filename=note_filename,
        note_suggested_path=os.path.join(vault_cfg.note_dir, note_filename),
    )

    asset_counter = 1

    # 1. 如果提供了 extra_files（如本地文件），按桌面/下载目录移动、其他目录复制处理
    if extra_files:
        for fpath in extra_files:
            abs_f = os.path.abspath(os.path.expanduser(fpath))
            if not os.path.isfile(abs_f):
                continue
            ext = os.path.splitext(abs_f)[1].lower()
            dest_name = f"{timestamp_hour}-{clean_slug}-{asset_counter:02d}{ext}"
            staged = stage_single_file(abs_f, vault_cfg.attachment_dir, dest_name, force_move=None)
            result.staged_assets.append(staged)
            asset_counter += 1

    # 2. 如果提供了 work_dir 且存在 fetch_manifest.json，按清单处理媒体与文章图片
    if work_dir:
        manifest_path = os.path.join(work_dir, "fetch_manifest.json")
        if os.path.isfile(manifest_path):
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            # 2a. 处理主媒体资产
            for item in manifest.get("assets", []):
                tpath = item.get("temp_path", "")
                if not tpath or not os.path.isfile(tpath):
                    continue
                ext = os.path.splitext(tpath)[1].lower()
                dest_name = f"{timestamp_hour}-{clean_slug}-{asset_counter:02d}{ext}"
                # 若文件位于 work_dir 内部，强制 move；否则遵循桌面/下载目录判断
                in_workdir = os.path.realpath(tpath).startswith(os.path.realpath(work_dir) + os.sep)
                force_mv = True if in_workdir else item.get("should_move")
                staged = stage_single_file(tpath, vault_cfg.attachment_dir, dest_name, force_move=force_mv)
                result.staged_assets.append(staged)
                asset_counter += 1

            # 2b. 处理互联网文章配图并重写原文图片引用
            article_md_path = manifest.get("article_md_path")
            if article_md_path and os.path.isfile(article_md_path):
                with open(article_md_path, "r", encoding="utf-8") as f:
                    md_text = f.read()

                url_to_embed: Dict[str, str] = {}
                for img_idx, img_item in enumerate(manifest.get("article_images", []), start=1):
                    orig_url = img_item.get("original_url", "")
                    tpath = img_item.get("temp_path", "")
                    if not orig_url or not tpath or not os.path.isfile(tpath):
                        continue
                    ext = os.path.splitext(tpath)[1].lower()
                    dest_name = f"{timestamp_hour}-{clean_slug}-img-{img_idx:02d}{ext}"
                    staged = stage_single_file(tpath, vault_cfg.attachment_dir, dest_name, force_move=True)
                    result.staged_assets.append(staged)
                    url_to_embed[orig_url] = staged.obsidian_embed

                if url_to_embed:
                    def replace_md_img(match: re.Match) -> str:
                        u = match.group(1).strip()
                        return url_to_embed.get(u, match.group(0))

                    md_text = re.sub(r"!\[[^\]]*\]\((https?://[^\s\)]+)\)", replace_md_img, md_text)

                localized_path = os.path.join(work_dir, "article_localized.md")
                with open(localized_path, "w", encoding="utf-8") as f:
                    f.write(md_text)
                result.localized_article_md_path = localized_path

    return result


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Obsidian Artifact Archiver 辅助工具：定位仓库配置、抓取外部链接素材、归档附件并重写内嵌链接。"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. inspect-vault
    p_inspect = subparsers.add_parser("inspect-vault", help="解析 Obsidian 仓库路径与附件目录配置")
    p_inspect.add_argument("--vault", help="显式指定 Obsidian 仓库路径（默认自动查找 obsidian-agi 等常用仓库）")
    p_inspect.add_argument("--note-dir", help="拟写入笔记的子目录（用于计算相对附件路径）")
    p_inspect.add_argument("--preferred-name", default="obsidian-agi", help="优先匹配的仓库名（默认 obsidian-agi）")

    # 2. fetch
    p_fetch = subparsers.add_parser("fetch", help="获取输入源（本地文件、Twitter、视频链接、网页文章）至临时目录")
    p_fetch.add_argument("--input", required=True, help="本地文件路径或外部 URL")
    p_fetch.add_argument("--work-dir", required=True, help="临时工作目录路径")
    p_fetch.add_argument(
        "--cookies-from-browser",
        help="可选：传给 gallery-dl / yt-dlp 的浏览器 Cookie 来源（如 chrome, safari）",
    )

    # 3. stage-assets
    p_stage = subparsers.add_parser("stage-assets", help="将附件重命名并移入/复制到 Obsidian 附件目录")
    p_stage.add_argument("--vault", help="Obsidian 仓库路径（不传则自动查找 obsidian-agi）")
    p_stage.add_argument("--note-dir", help="笔记所在目录")
    p_stage.add_argument("--site", help="站点或来源名称（如 GitHub, X, YouTube，不传则自动从链接推断）")
    p_stage.add_argument("--slug", required=True, help="简述标题（用于生成规范的笔记名与附件名）")
    p_stage.add_argument(
        "--timestamp",
        default=datetime.datetime.now().strftime("%Y-%m-%d-%H"),
        help="时间戳前缀，格式 YYYY-MM-DD-HH（不含分钟）",
    )
    p_stage.add_argument("--work-dir", help="fetch 阶段生成的临时目录")
    p_stage.add_argument("--files", nargs="*", help="直接归档的本地文件路径列表")

    args = parser.parse_args()

    if args.command == "inspect-vault":
        cfg = resolve_vault_config(
            explicit_vault=args.vault,
            note_dir=args.note_dir,
            preferred_name=args.preferred_name,
        )
        print(json.dumps(dataclasses.asdict(cfg), ensure_ascii=False, indent=2))

    elif args.command == "fetch":
        os.makedirs(args.work_dir, exist_ok=True)
        kind = detect_source_kind(args.input)
        if kind == "local_file":
            res = fetch_local_file(args.input)
        elif kind == "twitter":
            res = fetch_twitter(args.input, args.work_dir, args.cookies_from_browser)
        elif kind == "video":
            res = fetch_video(args.input, args.work_dir, args.cookies_from_browser)
        else:
            res = fetch_article(args.input, args.work_dir)
        res.site_name = infer_site_name(args.input)

        manifest_path = os.path.join(args.work_dir, "fetch_manifest.json")
        data = dataclasses.asdict(res)
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(json.dumps(data, ensure_ascii=False, indent=2))

    elif args.command == "stage-assets":
        cfg = resolve_vault_config(explicit_vault=args.vault, note_dir=args.note_dir)
        stage_res = run_stage_assets(
            vault_cfg=cfg,
            slug=args.slug,
            timestamp_hour=args.timestamp,
            site=args.site,
            work_dir=args.work_dir,
            extra_files=args.files,
        )
        print(json.dumps(dataclasses.asdict(stage_res), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
