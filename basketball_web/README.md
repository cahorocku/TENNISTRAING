# 🏀 打球记录可视化系统

一个令人愉悦的打球记录 Web 应用，支持比赛/约球/练习/上课四种类型，并完整集成 OpenClaw。

![界面预览](preview.png)

## ✨ 特性

- 🎨 **现代化 UI**：暗色主题、流畅动画、响应式设计
- 📊 **数据可视化**：饼图、折线图展示统计数据
- 🤖 **OpenClaw 集成**：支持语音/对话方式录入记录
- 📱 **移动端适配**：随时随地记录
- 💾 **本地存储**：JSON 文件保存，数据安全

## 🚀 快速开始

### 1. 启动 Web 服务

```bash
cd /Users/ricky/basketball_web
python3 start_server.py
```

服务启动后会自动打开浏览器访问 `http://localhost:8080`

### 2. 使用 Web 界面

打开浏览器后即可：
- 点击类型图标选择记录类型
- 填写日期、时长、花费等信息
- 比赛自动显示比分输入框
- 练习/上课自动显示内容输入框
- 查看统计卡片和图表

## 🤖 OpenClaw 集成

### 方式一：使用桥接器（推荐）

在 OpenClaw 对话中直接使用 Python 函数：

```python
# 添加比赛记录
from basketball_web.openclaw_bridge import add_game
add_game("2026-03-10", 120, "105:98", 50, "vs 火箭队")

# 添加练习记录
from basketball_web.openclaw_bridge import add_practice
add_practice("2026-03-11", 90, "三分球训练", 0, "命中率65%")

# 添加约球记录
from basketball_web.openclaw_bridge import add_casual
add_casual("2026-03-12", 150, 30, "小区球场")

# 添加上课记录
from basketball_web.openclaw_bridge import add_lesson
add_lesson("2026-03-13", 60, "运球突破", 300, "李指导")

# 查看最近7天汇总
from basketball_web.openclaw_bridge import summary
summary(7)

# 列出所有记录
from basketball_web.openclaw_bridge import list_records
list_records()
list_records("比赛")  # 只列出比赛
```

### 方式二：命令行

```bash
cd /Users/ricky/basketball_web

# 添加比赛
python3 openclaw_bridge.py add_game 2026-03-10 120 105:98 50 "vs火箭队"

# 添加练习
python3 openclaw_bridge.py add_practice 2026-03-11 90 "三分球训练"

# 查看汇总
python3 openclaw_bridge.py summary 7

# 列出记录
python3 openclaw_bridge.py list
python3 openclaw_bridge.py list 比赛
```

### 方式三：MCP 服务器（供 OpenClaw 自动调用）

将以下配置添加到 OpenClaw 配置：

```json
{
  "mcpServers": {
    "basketball": {
      "command": "python3",
      "args": ["/Users/ricky/basketball_web/mcp_server.py"]
    }
  }
}
```

添加后 OpenClaw 会自动识别并使用这些工具：
- `add_basketball_record` - 添加记录
- `get_basketball_summary` - 获取汇总
- `list_basketball_records` - 列出记录
- `delete_basketball_record` - 删除记录

## 📡 API 接口

### REST API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/records` | 获取记录列表 |
| POST | `/api/records` | 创建记录 |
| GET | `/api/records/{id}` | 获取单条记录 |
| PUT | `/api/records/{id}` | 更新记录 |
| DELETE | `/api/records/{id}` | 删除记录 |
| GET | `/api/statistics` | 获取统计 |
| GET | `/api/openclaw/summary` | OpenClaw 汇总 |

### 示例请求

```bash
# 添加记录
curl -X POST http://localhost:8080/api/records \
  -H "Content-Type: application/json" \
  -d '{
    "type": "比赛",
    "date": "2026-03-10",
    "duration_minutes": 120,
    "score": "105:98",
    "cost": 50
  }'

# 获取统计
curl http://localhost:8080/api/statistics
```

## 📁 文件结构

```
basketball_web/
├── main.py              # FastAPI Web 服务端
├── start_server.py      # 启动脚本
├── openclaw_bridge.py   # OpenClaw 桥接器
├── mcp_server.py        # MCP 服务器
├── templates/
│   └── index.html       # 前端页面
├── static/              # 静态资源
└── README.md           # 说明文档

basketball_records.json  # 数据文件（自动创建）
```

## 🎯 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| type | string | 类型：比赛/约球/练习/上课 |
| date | string | 日期 (YYYY-MM-DD) |
| duration_minutes | int | 时长（分钟）|
| cost | float | 花费金额（元）|
| score | string | 比赛成绩（如 100:95）|
| technique | string | 练习/上课内容 |
| note | string | 备注 |

## 🎨 界面预览

- **统计卡片**：总记录数、累计时长、总花费、比赛胜率
- **类型占比饼图**：直观展示各类型的比例
- **每月趋势折线图**：追踪打球频率变化
- **记录列表**：按时间倒序展示，支持筛选和删除

## 🔧 技术栈

- **后端**：Python + FastAPI
- **前端**：HTML5 + CSS3 + Vanilla JS
- **图表**：Chart.js
- **字体**：Google Fonts (Noto Sans SC)

## 📝 数据存储

所有数据保存在 `/Users/ricky/basketball_records.json`，格式：

```json
[
  {
    "id": 1,
    "type": "比赛",
    "date": "2026-03-01",
    "duration_minutes": 120,
    "cost": 50,
    "score": "105:98",
    "technique": "",
    "note": "vs 火箭队",
    "created_at": "2026-03-01T10:00:00"
  }
]
```

## 🏆 享受记录的乐趣！

每次录入都会有愉悦的动画反馈，让记录打球成为一种享受 🎉
