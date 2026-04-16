"""AI 总结模块（共用）"""

import json
import re
import urllib.request
import urllib.error


def cleanup_ai_output(text):
    """后处理：清理 AI 输出中的第三方视角用词"""
    replacements = [
        ("该内容", ""),
        ("该方法", "这个方法"),
        ("该视频", ""),
        ("该文章", ""),
        ("该技巧", "这个技巧"),
        ("该工具", "这个工具"),
        ("该流程", "这个流程"),
        ("作者指出", ""),
        ("作者提到", ""),
        ("作者分享了", ""),
        ("视频讲解了", ""),
        ("视频中提到", ""),
        ("文章介绍了", ""),
        ("文章中提到", ""),
        ("本视频", ""),
        ("本文", ""),
        ("部分开发者", "开发者"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)

    text = re.sub(r"  +", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def ai_summarize(text, config, comments_text="", supplements_text="", content_info=None):
    """AI 总结"""
    api_base = config.get("api_base", "").rstrip("/")
    api_key = config.get("api_key", "")
    model = config.get("model", "")

    if not api_base or not api_key or not model:
        return None

    has_supplements = bool(supplements_text and supplements_text.strip())
    has_comments = bool(comments_text and comments_text.strip())

    parts = ["原始内容"]
    if has_comments:
        parts.append("评论区")
    if has_supplements:
        parts.append("用户补充信息")
    basis = " + ".join(parts)

    # 构建来源元数据
    vi = content_info or {}
    meta_lines = [f"- 链接：（由调用方填入）"]
    if vi.get("author"):
        meta_lines.append(f"- 作者：{vi['author']}")
    if vi.get("publish_time"):
        meta_lines.append(f"- 发布时间：{vi['publish_time']}")
    if vi.get("tags"):
        meta_lines.append(f"- 标签：{'、'.join(vi['tags'])}")
    if vi.get("likes"):
        meta_lines.append(f"- 数据：{vi['likes']} 赞 · {vi.get('comments_count', '')} 评论 · {vi.get('favorites', '')} 收藏 · {vi.get('shares', '')} 转发")
    meta_lines.append(f"- 生成依据：{basis}")
    meta_block = "\n".join(meta_lines)

    prompt = f"""把下面的内容整理成学习笔记。直接写知识点，不要转述。

格式要求和示例：

## 来源
{meta_block}

## 摘要
示例（注意语气）：
「Vibe Coding 从零开始不要凭空让 AI 写代码，正确做法是从 GitHub 找成熟开源项目，让 AI 学习后按需改造，效率远高于从零开发。」
（2-3 句话，不超过 100 字。像上面的示例一样直接写观点。禁止用「该内容」「该视频」「该方法」「该文章」开头。）

## 要点
示例（注意语气）：
- 不要凭空让 AI 从零写代码
- 从 GitHub 找成熟开源项目作为基础
- 让 AI 学习项目代码后按需改造
（3-8 条，每条不超过 30 字。禁止用「该」字开头。）

## 正文
示例（注意语气）：
「### 常见误区
直接用 AI 从零写代码容易陷入需求模糊、代码破碎的死循环。
### 正确做法
从 GitHub 找一个成熟的开源项目...
### 注意事项
使用开源项目时要遵守对应的开源协议。」
（像上面的示例一样，直接写知识点。用小标题分段。评论区有价值的信息融入正文。禁止出现「该方法」「作者指出」「视频中提到」「文章介绍了」。）

## 评论
（保留有价值的讨论，忽略纯求资源的。如果没有评论内容则省略此章节。）

禁止用词清单（全文不得出现）：该内容、该方法、该视频、该文章、该技巧、作者指出、视频讲解、文章介绍、本视频、本文、部分开发者

原始内容：
{text}"""

    if has_supplements:
        prompt += f"\n\n用户补充信息：\n{supplements_text}"

    if has_comments:
        prompt += f"""\n\n评论区内容：\n{comments_text}

评论区处理规则：
- 标记为（作者）的评论是原作者的补充说明，将有价值的信息融入正文
- 其他用户的评论单独作为「## 评论」章节，保留有价值的反馈和讨论
- 忽略纯求资源、纯表情、无实质内容的评论
- 如果有作者对用户的回复，保留对话关系"""

    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 4096
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{api_base}/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            return cleanup_ai_output(content)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        print(f"  AI 总结失败（HTTP {e.code}）: {body[:200]}")
        return None
    except Exception as e:
        print(f"  AI 总结失败: {e}")
        return None
