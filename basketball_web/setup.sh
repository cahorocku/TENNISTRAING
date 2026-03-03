#!/bin/bash
# 🏀 打球记录系统安装脚本

echo "🏀 正在安装打球记录系统依赖..."

# 检查 Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ 请先安装 Python3"
    exit 1
fi

# 安装依赖
echo "📦 安装 FastAPI, Uvicorn, Jinja2..."
python3 -m pip install fastapi uvicorn jinja2 --trusted-host pypi.org --trusted-host files.pythonhosted.org -q

if [ $? -eq 0 ]; then
    echo "✅ 依赖安装完成！"
    echo ""
    echo "🚀 启动服务器："
    echo "   python3 /Users/ricky/basketball_web/start_server.py"
else
    echo "❌ 安装失败，请检查网络连接"
    exit 1
fi
