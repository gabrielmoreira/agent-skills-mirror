#!/bin/bash

# Smart Notes — 智能笔记生成器
# 用法: ./run.sh "链接"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# 检测可用的 Python（playwright 不支持 3.14+）
find_python() {
  for cmd in python3.12 python3.13 python3.11 python3.10 python3; do
    if command -v "$cmd" &>/dev/null; then
      version=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
      major=$(echo "$version" | cut -d. -f1)
      minor=$(echo "$version" | cut -d. -f2)
      if [ "$major" = "3" ] && [ "$minor" -ge 10 ] && [ "$minor" -le 13 ]; then
        echo "$cmd"
        return 0
      fi
    fi
  done
  return 1
}

SYSTEM_PYTHON=$(find_python)
if [ -z "$SYSTEM_PYTHON" ]; then
  echo "错误: 未找到兼容的 Python（需要 3.10 ~ 3.13）"
  echo ""
  echo "安装方式:"
  echo "  brew install python@3.12"
  exit 1
fi

# 自动创建和激活虚拟环境
setup_venv() {
  if [ ! -d "$VENV_DIR" ]; then
    echo "· 首次运行，正在创建 Python 环境..."
    "$SYSTEM_PYTHON" -m venv "$VENV_DIR"
    echo "  完成"
  fi
  source "$VENV_DIR/bin/activate"
}

# 检测依赖，缺少则自动安装
check_and_install_deps() {
  if ! command -v ffmpeg &>/dev/null; then
    echo "错误: 需要安装 ffmpeg"
    echo "  brew install ffmpeg"
    exit 1
  fi

  local missing=()
  if ! python -c "import playwright" &>/dev/null; then
    missing+=("playwright")
  fi
  if ! python -c "import whisper" &>/dev/null; then
    missing+=("openai-whisper")
  fi
  if ! python -c "import requests" &>/dev/null; then
    missing+=("requests")
  fi
  if ! python -c "import bs4" &>/dev/null; then
    missing+=("beautifulsoup4")
  fi

  if [ ${#missing[@]} -gt 0 ]; then
    echo "· 正在安装依赖: ${missing[*]}..."
    pip install -q "${missing[@]}" 2>&1 | grep -v "already satisfied"

    if [[ " ${missing[*]} " == *" playwright "* ]]; then
      echo "· 正在安装浏览器（首次较慢）..."
      playwright install chromium 2>&1 | tail -1
    fi

    echo "  依赖安装完成"
  fi
}

# 无参数时显示帮助
if [ -z "$1" ]; then
  echo "Smart Notes — 智能笔记生成器"
  echo ""
  echo "用法:"
  echo "  $0 \"链接\"          提取内容并生成笔记"
  echo "  $0 \"链接\" --no-ai  只提取原始内容"
  echo ""
  echo "支持：抖音视频、微信公众号文章"
  echo "首次使用会自动安装依赖。"
  exit 0
fi

setup_venv
check_and_install_deps
python "$SCRIPT_DIR/scripts/main.py" "$@"
