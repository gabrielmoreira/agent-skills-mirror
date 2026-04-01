#!/bin/bash
# Surrogate-Modeling Expert Agent - Quick Actions
# 用于手动触发各种任务

WORKSPACE="/home/gem/.openclaw/workspace/3d_surrogate_proj"
AGENT_DIR="/home/gem/.openclaw/agents/surrogate-modeling-expert"

echo "==================================="
echo "Surrogate-Modeling Expert Agent"
echo "==================================="
echo ""
echo "可用操作："
echo "1. 查看今日检索结果"
echo "2. 查看本周论文列表"
echo "3. 查看最新周报"
echo "4. 手动触发论文检索"
echo "5. 手动生成周报"
echo "6. 查看定时任务状态"
echo ""
read -p "请选择操作 (1-6): " choice

case $choice in
    1)
        echo ""
        echo "今日检索结果："
        echo "--------------"
        if [ -d "$WORKSPACE/papers" ]; then
            find "$WORKSPACE/papers" -type f -name "*.pdf" -mtime -1 -exec ls -lh {} \;
        else
            echo "暂无今日检索结果"
        fi
        ;;
    2)
        echo ""
        echo "本周论文列表："
        echo "--------------"
        if [ -d "$WORKSPACE/papers" ]; then
            find "$WORKSPACE/papers" -type d -mindepth 1 -maxdepth 1 -mtime -7 | while read dir; do
                basename "$dir"
            done
        else
            echo "暂无本周论文"
        fi
        ;;
    3)
        echo ""
        echo "最新周报："
        echo "----------"
        if [ -d "$WORKSPACE/weekly_reports" ]; then
            latest_report=$(ls -t "$WORKSPACE/weekly_reports"/*.md 2>/dev/null | head -1)
            if [ -n "$latest_report" ]; then
                cat "$latest_report"
            else
                echo "暂无周报"
            fi
        else
            echo "暂无周报"
        fi
        ;;
    4)
        echo ""
        echo "手动触发论文检索..."
        echo "请通过对话方式触发："
        echo "  '帮我检索 geometry-aware neural operator 相关的最新论文'"
        ;;
    5)
        echo ""
        echo "手动生成周报..."
        echo "请通过对话方式触发："
        echo "  '生成本周的三维几何代理模型研究周报'"
        ;;
    6)
        echo ""
        echo "定时任务状态："
        echo "--------------"
        echo "1. 每日论文检索: 21:00 (UTC+8)"
        echo "2. 每周报告生成: 周日 10:00 (UTC+8)"
        ;;
    *)
        echo "无效选择"
        ;;
esac
