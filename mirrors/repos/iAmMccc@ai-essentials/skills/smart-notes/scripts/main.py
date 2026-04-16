#!/usr/bin/env python3
"""
Smart Notes — 智能笔记生成器
输入链接，自动识别平台，提取内容，生成结构化笔记。

用法: python3 main.py "链接"
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)


def detect_platform(url):
    """根据 URL 识别平台"""
    # 先从文本中提取 URL
    url_match = re.search(r"https?://[^\s]+", url)
    check_url = url_match.group(0) if url_match else url

    if "douyin.com" in check_url or "v.douyin.com" in check_url or "iesdouyin.com" in check_url:
        return "douyin"
    if "mp.weixin.qq.com" in check_url:
        return "wechat"
    if "juejin.cn" in check_url:
        return "juejin"

    return None


def load_config():
    for path in [os.path.join(ROOT_DIR, "config.json"), "config.json"]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    return {}


def interactive_config_ai(config):
    """交互式引导配置 AI 模型"""
    print("")
    print("请填写 AI 模型信息：")
    print("")
    print("  api_base — AI 服务的接口地址，例如：")
    print("    豆包: https://ark.cn-beijing.volces.com/api/v3")
    print("    DeepSeek: https://api.deepseek.com/v1")
    print("    OpenAI: https://api.openai.com/v1")
    print("")

    try:
        api_base = input("  api_base: ").strip()
        if not api_base:
            print("  已跳过")
            return config
        api_key = input("  api_key（API 密钥）: ").strip()
        if not api_key:
            print("  已跳过")
            return config
        model = input("  model（模型名称）: ").strip()
        if not model:
            print("  已跳过")
            return config
    except (EOFError, KeyboardInterrupt):
        print("\n  已跳过")
        return config

    config["api_base"] = api_base
    config["api_key"] = api_key
    config["model"] = model

    config_path = os.path.join(ROOT_DIR, "config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump({"api_base": api_base, "api_key": api_key, "model": model}, f, ensure_ascii=False, indent=2)
    print(f"  已保存，下次无需重复填写。")

    return config


def main():
    parser = argparse.ArgumentParser(description="Smart Notes — 智能笔记生成器")
    parser.add_argument("url", help="内容链接（抖音视频、微信文章等）")
    parser.add_argument("--no-ai", action="store_true", help="跳过 AI 总结")
    parser.add_argument("--output-dir", default="output", help="输出根目录（默认 output）")
    args = parser.parse_args()

    # 识别平台
    platform = detect_platform(args.url)
    if not platform:
        print(f"错误: 无法识别链接所属平台")
        print(f"当前支持：抖音视频、微信公众号文章")
        sys.exit(1)

    platform_names = {"douyin": "抖音", "wechat": "微信公众号", "juejin": "掘金"}
    print(f"· 识别平台: {platform_names.get(platform, platform)}")

    # 加载配置
    config = load_config()

    # 调用对应平台模块
    if platform == "douyin":
        from platforms.douyin import run as platform_run
    elif platform == "wechat":
        from platforms.wechat import run as platform_run
    else:
        print(f"错误: {platform} 暂未支持")
        sys.exit(1)

    # 先创建临时目录用于提取（平台模块会返回标题，之后再移动）
    import tempfile
    temp_raw = tempfile.mkdtemp()

    content_info, text, comments_text = platform_run(args.url, temp_raw)

    # 创建正式的输出目录
    from output import create_output_dirs, create_extra_template, get_next_version, load_supplements, print_result
    title = content_info.get("title", "untitled")
    project_dir, raw_dir, supplements_dir, output_dir = create_output_dirs(args.output_dir, title)

    # 移动临时文件到正式目录
    import shutil
    for f in Path(temp_raw).iterdir():
        dest = os.path.join(raw_dir, f.name)
        if not os.path.exists(dest):
            shutil.move(str(f), dest)
    shutil.rmtree(temp_raw, ignore_errors=True)

    # 生成补充信息模板
    url = content_info.get("url", args.url)
    create_extra_template(supplements_dir, url)

    # AI 总结
    summary_version = None
    if not args.no_ai:
        if not config.get("api_key"):
            print("")
            try:
                choice = input("是否配置 AI 模型生成总结？(y/n) [默认 n]：").strip().lower()
            except (EOFError, KeyboardInterrupt):
                choice = "n"
            if choice in ("y", "yes"):
                config = interactive_config_ai(config)

        if config.get("api_key"):
            from summarizer import ai_summarize
            print("· AI 总结...")
            supplements_text = load_supplements(supplements_dir)
            summary = ai_summarize(text, config, comments_text=comments_text,
                                   supplements_text=supplements_text, content_info=content_info)
            if summary:
                summary = summary.replace("（由调用方填入）", url)
                summary_version = get_next_version(output_dir)
                summary_path = os.path.join(output_dir, f"{summary_version}.md")
                with open(summary_path, "w", encoding="utf-8") as f:
                    f.write(f"# {title}\n\n{summary}\n")
                print("  完成")
            else:
                print("  失败，请检查 API 配置")
                try:
                    retry = input("是否重新配置？(y/n) [默认 n]：").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    retry = "n"
                if retry in ("y", "yes"):
                    config = interactive_config_ai(config)
                    if config.get("api_key"):
                        print("· AI 总结（重试）...")
                        summary = ai_summarize(text, config, comments_text=comments_text,
                                               supplements_text=supplements_text, content_info=content_info)
                        if summary:
                            summary = summary.replace("（由调用方填入）", url)
                            summary_version = get_next_version(output_dir)
                            summary_path = os.path.join(output_dir, f"{summary_version}.md")
                            with open(summary_path, "w", encoding="utf-8") as f:
                                f.write(f"# {title}\n\n{summary}\n")
                            print("  完成")
                        else:
                            print("  仍然失败，跳过 AI 总结")
        else:
            print("· 跳过 AI 总结")

    # 输出结果
    print_result(project_dir, raw_dir, supplements_dir, output_dir, summary_version)


if __name__ == "__main__":
    main()
