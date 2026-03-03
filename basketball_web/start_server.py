#!/usr/bin/env python3
"""
🏀 打球记录 Web 服务启动器
"""

import subprocess
import sys
import webbrowser
import time
import os

# 检查依赖
def check_dependencies():
    """检查并安装依赖"""
    try:
        import fastapi
        import uvicorn
    except ImportError:
        print("📦 正在安装依赖...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "jinja2"])
        print("✅ 依赖安装完成\n")

def start_server():
    """启动服务器"""
    check_dependencies()
    
    print("""
🏀 =========================================
      打球记录可视化系统
=========================================
    
🌐 Web 界面: http://localhost:8080
📊 API 地址: http://localhost:8080/api
🤖 OpenClaw: 已集成桥接器

快捷键:
  • Ctrl+C 停止服务
  
=========================================
""")
    
    # 延迟打开浏览器
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:8080")
    
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    # 启动服务器
    os.chdir("/Users/ricky/basketball_web")
    subprocess.run([sys.executable, "main.py"])

if __name__ == "__main__":
    start_server()
