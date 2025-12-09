#!/bin/bash
# B站视频爬虫 - 一键启动脚本

echo "🎬 B站视频爬虫程序"
echo "=================="

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到Python3，请先安装Python"
    exit 1
fi

# 检查requests是否安装
if ! python3 -c "import requests" 2>/dev/null; then
    echo "📦 正在安装依赖..."
    python3 -m pip install requests --user
fi

echo ""
echo "🚀 启动爬虫程序..."
echo ""

# 运行爬虫程序
python3 run.py

# 如果用户直接运行这个脚本，可以传UID参数
if [ $# -gt 0 ]; then
    python3 run.py "$1"
else
    python3 run.py
fi