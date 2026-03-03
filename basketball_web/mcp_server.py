#!/usr/bin/env python3
"""
🏀 打球记录 MCP 服务器
为 OpenClaw 提供 MCP 协议支持
"""

import json
import sys
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional

SERVER_URL = "http://localhost:8080"


def send_response(response: dict):
    """发送 MCP 响应"""
    print(json.dumps(response, ensure_ascii=False), flush=True)


def api_call(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """调用打球记录 API"""
    url = f"{SERVER_URL}/api/{endpoint}"
    
    if method == "GET" and data:
        params = "&".join([f"{k}={v}" for k, v in data.items()])
        url += "?" + params
        data = None
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode() if data else None,
        headers={'Content-Type': 'application/json'} if data else {},
        method=method
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        return {"success": False, "error": str(e)}


def handle_initialize(id: str):
    """处理初始化请求"""
    return {
        "jsonrpc": "2.0",
        "id": id,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "basketball-tracker",
                "version": "1.0.0"
            }
        }
    }


def handle_tools_list(id: str):
    """返回可用工具列表"""
    return {
        "jsonrpc": "2.0",
        "id": id,
        "result": {
            "tools": [
                {
                    "name": "add_basketball_record",
                    "description": "添加一条打球记录",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["比赛", "约球", "练习", "上课"],
                                "description": "记录类型"
                            },
                            "date": {
                                "type": "string",
                                "description": "日期，格式 YYYY-MM-DD"
                            },
                            "duration_minutes": {
                                "type": "integer",
                                "description": "打球时长（分钟）"
                            },
                            "cost": {
                                "type": "number",
                                "description": "花费金额（元）",
                                "default": 0
                            },
                            "score": {
                                "type": "string",
                                "description": "比赛成绩（如 100:95），仅比赛类型需要",
                                "default": ""
                            },
                            "technique": {
                                "type": "string",
                                "description": "训练内容/上课内容，仅练习和上课类型需要",
                                "default": ""
                            },
                            "note": {
                                "type": "string",
                                "description": "备注",
                                "default": ""
                            }
                        },
                        "required": ["type", "date", "duration_minutes"]
                    }
                },
                {
                    "name": "get_basketball_summary",
                    "description": "获取打球记录汇总统计",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "days": {
                                "type": "integer",
                                "description": "最近多少天的数据",
                                "default": 7
                            }
                        }
                    }
                },
                {
                    "name": "list_basketball_records",
                    "description": "列出打球记录",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["比赛", "约球", "练习", "上课", ""],
                                "description": "按类型筛选",
                                "default": ""
                            }
                        }
                    }
                },
                {
                    "name": "delete_basketball_record",
                    "description": "删除一条打球记录",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "integer",
                                "description": "记录ID"
                            }
                        },
                        "required": ["id"]
                    }
                }
            ]
        }
    }


def handle_tool_call(id: str, name: str, arguments: dict):
    """处理工具调用"""
    
    if name == "add_basketball_record":
        result = api_call("records", "POST", arguments)
        if result.get("success"):
            record = result.get("data", {})
            return {
                "jsonrpc": "2.0",
                "id": id,
                "result": {
                    "content": [{
                        "type": "text",
                        "text": f"✅ 已添加{record['type']}记录：\n"
                                f"📅 日期：{record['date']}\n"
                                f"⏱️ 时长：{record['duration_minutes']}分钟\n"
                                f"💰 花费：¥{record['cost']}\n"
                                + (f"🏆 比分：{record['score']}\n" if record.get('score') else "")
                                + (f"📝 内容：{record['technique']}\n" if record.get('technique') else "")
                                + (f"💬 备注：{record['note']}" if record.get('note') else "")
                    }]
                }
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": id,
                "error": {"code": -32600, "message": result.get("error", "添加失败")}
            }
    
    elif name == "get_basketball_summary":
        days = arguments.get("days", 7)
        result = api_call(f"openclaw/summary?days={days}")
        
        if result.get("success"):
            data = result.get("data", {})
            summary = data.get("summary", {})
            overall = data.get("overall_stats", {})
            
            text = f"🏀 最近{days}天打球汇总\n\n"
            text += f"📊 统计：\n"
            text += f"   • 记录数：{summary.get('records_count', 0)} 条\n"
            text += f"   • 总时长：{summary.get('total_duration', 0)} 分钟\n"
            text += f"   • 总花费：¥{summary.get('total_cost', 0)}\n\n"
            text += f"🏆 累计数据：\n"
            text += f"   • 总记录：{overall.get('total_records', 0)} 条\n"
            text += f"   • 总时长：{overall.get('total_duration', 0)//60} 小时\n"
            text += f"   • 总花费：¥{overall.get('total_cost', 0)}\n"
            text += f"   • 胜率：{overall.get('win_rate', '--')}%\n\n"
            
            recent = data.get("recent_records", [])
            if recent:
                text += "📝 最近5条记录：\n"
                for r in recent:
                    icon = {"比赛": "🏆", "约球": "🤝", "练习": "💪", "上课": "🎓"}.get(r['type'], '🏀')
                    text += f"   {icon} {r['date']} {r['type']} {r['duration_minutes']}分钟\n"
            
            return {
                "jsonrpc": "2.0",
                "id": id,
                "result": {"content": [{"type": "text", "text": text}]}
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": id,
                "error": {"code": -32600, "message": "获取汇总失败"}
            }
    
    elif name == "list_basketball_records":
        record_type = arguments.get("type", "")
        endpoint = f"records?type={record_type}" if record_type else "records"
        result = api_call(endpoint)
        
        if result.get("success"):
            records = result.get("data", [])
            if not records:
                text = "📭 暂无记录"
            else:
                text = f"📋 共 {len(records)} 条记录\n" + "="*40 + "\n"
                for r in records[:20]:  # 最多显示20条
                    icon = {"比赛": "🏆", "约球": "🤝", "练习": "💪", "上课": "🎓"}.get(r['type'], '🏀')
                    text += f"\n{icon} [{r['type']}] ID:{r['id']} {r['date']}\n"
                    text += f"   ⏱️ {r['duration_minutes']}分钟"
                    if r.get('cost', 0) > 0:
                        text += f" | 💰 ¥{r['cost']}"
                    text += "\n"
                    if r.get('score'):
                        text += f"   🏆 比分：{r['score']}\n"
                    if r.get('technique'):
                        text += f"   📝 内容：{r['technique']}\n"
            
            return {
                "jsonrpc": "2.0",
                "id": id,
                "result": {"content": [{"type": "text", "text": text}]}
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": id,
                "error": {"code": -32600, "message": "获取记录失败"}
            }
    
    elif name == "delete_basketball_record":
        record_id = arguments.get("id")
        result = api_call(f"records/{record_id}", "DELETE")
        
        if result.get("success"):
            return {
                "jsonrpc": "2.0",
                "id": id,
                "result": {
                    "content": [{"type": "text", "text": f"✅ 已删除记录 ID:{record_id}"}]
                }
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": id,
                "error": {"code": -32600, "message": "删除失败"}
            }
    
    return {
        "jsonrpc": "2.0",
        "id": id,
        "error": {"code": -32601, "message": f"未知工具: {name}"}
    }


def main():
    """主循环"""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line.strip())
            method = request.get("method")
            req_id = request.get("id")
            params = request.get("params", {})
            
            if method == "initialize":
                send_response(handle_initialize(req_id))
            
            elif method == "tools/list":
                send_response(handle_tools_list(req_id))
            
            elif method == "tools/call":
                name = params.get("name")
                arguments = params.get("arguments", {})
                send_response(handle_tool_call(req_id, name, arguments))
            
            elif method == "notifications/initialized":
                pass  # 无需响应
            
        except json.JSONDecodeError:
            continue
        except Exception as e:
            if req_id:
                send_response({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32603, "message": str(e)}
                })


if __name__ == "__main__":
    main()
