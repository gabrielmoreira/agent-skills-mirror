"""输出管理模块（共用）"""

import os
import re
from pathlib import Path


def create_output_dirs(base_dir, title):
    """创建输出目录结构，返回各目录路径"""
    project_dir = os.path.join(base_dir, title)
    raw_dir = os.path.join(project_dir, "raw")
    supplements_dir = os.path.join(project_dir, "supplements")
    output_dir = os.path.join(project_dir, "output")

    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(supplements_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    return project_dir, raw_dir, supplements_dir, output_dir


def create_extra_template(supplements_dir, url):
    """创建补充信息模板（如果不存在）"""
    extra_path = os.path.join(supplements_dir, "extra.md")
    if not os.path.exists(extra_path):
        with open(extra_path, "w", encoding="utf-8") as f:
            f.write(f"# 补充信息\n\n")
            f.write(f"链接: {url}\n\n")
            f.write(f"（在这里添加额外信息：GitHub 地址、工具名称、关键截图描述、相关链接等）\n")


def get_next_version(output_dir):
    """获取下一个版本号"""
    existing = list(Path(output_dir).glob("v*.md"))
    if not existing:
        return "v1"
    nums = []
    for f in existing:
        match = re.match(r"v(\d+)", f.stem)
        if match:
            nums.append(int(match.group(1)))
    return f"v{max(nums) + 1}" if nums else "v1"


def load_supplements(supplements_dir):
    """读取补充信息目录下的所有文本内容（忽略未编辑的模板）"""
    texts = []
    if not os.path.isdir(supplements_dir):
        return ""

    placeholder_markers = ["在这里添加你的补充信息", "（在这里添加"]

    for f in sorted(Path(supplements_dir).iterdir()):
        if f.is_file() and f.suffix in (".md", ".txt"):
            try:
                content = f.read_text(encoding="utf-8").strip()
                if not content:
                    continue
                is_template = any(marker in content for marker in placeholder_markers)
                if is_template:
                    continue
                texts.append(f"--- {f.name} ---\n{content}")
            except Exception:
                pass
    return "\n\n".join(texts)


def print_result(project_dir, raw_dir, supplements_dir, output_dir, summary_version=None):
    """打印输出结果"""
    raw_contents = []
    for name, label in [("transcript.txt", "字幕"), ("content.md", "正文"), ("audio.mp3", "音频"),
                         ("video.mp4", "视频"), ("comments.txt", "评论")]:
        if os.path.exists(os.path.join(raw_dir, name)):
            raw_contents.append(label)

    output_file = f"{summary_version}.md" if summary_version else "（未生成）"

    print("")
    print("── 输出结果 ──────────────────")
    print(f"  {project_dir}/")
    print(f"  ├── raw/          {' · '.join(raw_contents)}")
    print(f"  ├── supplements/  补充信息（可编辑）")
    print(f"  └── output/       {output_file}")
    print("")

    if summary_version:
        next_ver = get_next_version(output_dir)
        print(f"编辑 supplements/ 后重新执行，将生成 {next_ver}.md。")
