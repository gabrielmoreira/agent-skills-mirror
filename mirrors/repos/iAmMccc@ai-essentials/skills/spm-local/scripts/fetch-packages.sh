#!/bin/bash
# SPM 本地依赖下载脚本
# 读取 packages.json，将三方库 clone 到 Packages/Caches/
# 用法: ./Packages/scripts/fetch-packages.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PACKAGES_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CACHE_DIR="$PACKAGES_ROOT/Caches"
JSON_FILE="$PACKAGES_ROOT/packages.json"

# 检查 packages.json
if [ ! -f "$JSON_FILE" ]; then
  echo "错误: 未找到 $JSON_FILE"
  echo "请先创建 packages.json，参考 packages.json.example"
  exit 1
fi

# 检查 python3（用于解析 JSON）
if ! command -v python3 &>/dev/null; then
  echo "错误: 需要 python3 来解析 packages.json"
  exit 1
fi

mkdir -p "$CACHE_DIR"
cd "$CACHE_DIR"

# 继承终端代理设置
if [[ -n "$https_proxy" ]]; then
  export GIT_HTTP_PROXY="$https_proxy"
  export GIT_HTTPS_PROXY="$https_proxy"
fi
if [[ -n "$http_proxy" ]]; then
  export GIT_HTTP_PROXY="${GIT_HTTP_PROXY:-$http_proxy}"
fi

# 解析 packages.json
ENTRIES=$(python3 -c "
import json, sys
with open('$JSON_FILE') as f:
    pkgs = json.load(f)
for p in pkgs:
    url = p['url']
    version = p.get('version', '')
    # 从 URL 解析库名
    name = url.rstrip('/').split('/')[-1].removesuffix('.git')
    print(f'{name}\t{url}\t{version}')
")

clone_count=0
skip_count=0
update_count=0
fail_count=0

while IFS=$'\t' read -r name url version; do
  dir="$CACHE_DIR/$name"

  # 情况 1：目录存在但为空 → 删除后重新 clone
  if [ -d "$dir" ] && [ -z "$(ls -A "$dir" 2>/dev/null)" ]; then
    echo "[清理] $name"
    rm -rf "$dir"
  fi

  # 情况 2：目录存在且有内容
  if [ -d "$dir" ]; then
    if [ -n "$version" ]; then
      # 检查当前是否已在目标版本
      current_tag=$(cd "$dir" && git describe --tags --exact-match 2>/dev/null)
      if [ "$current_tag" = "$version" ] || [ "$current_tag" = "v${version}" ]; then
        echo "[跳过] $name $version"
        skip_count=$((skip_count + 1))
      else
        echo "[更新] $name $version"
        if (cd "$dir" && git fetch -q --tags 2>/dev/null && \
            (git checkout -q "$version" 2>/dev/null || git checkout -q "v${version}" 2>/dev/null)); then
          update_count=$((update_count + 1))
        else
          echo "  ⚠ checkout $version 失败"
          fail_count=$((fail_count + 1))
        fi
      fi
    else
      echo "[跳过] $name"
      skip_count=$((skip_count + 1))
    fi
    continue
  fi

  # 情况 3：目录不存在 → clone
  echo "[下载] $name ${version:+$version}"
  if [ -n "$version" ]; then
    if git clone -q "$url" "$name" 2>/dev/null && \
       (cd "$name" && (git checkout -q "$version" 2>/dev/null || git checkout -q "v${version}" 2>/dev/null)); then
      clone_count=$((clone_count + 1))
    else
      echo "  ⚠ clone 或 checkout 失败"
      fail_count=$((fail_count + 1))
    fi
  else
    if git clone -q --depth 1 "$url" "$name" 2>/dev/null; then
      clone_count=$((clone_count + 1))
    else
      echo "  ⚠ clone 失败，请检查网络或 URL"
      fail_count=$((fail_count + 1))
    fi
  fi

done <<< "$ENTRIES"

echo ""
echo "完成。下载: $clone_count / 更新: $update_count / 跳过: $skip_count / 失败: $fail_count"
echo "缓存目录: $CACHE_DIR"
