#!/usr/bin/env python3
"""
🏀 OpenClaw 集成桥接器
让 OpenClaw 可以访问和操作打球记录
"""

import json
import subprocess
from typing import Optional, List, Dict, Any
from datetime import datetime, date


class BasketballOpenClawBridge:
    """
    OpenClaw 桥接类
    提供简单接口供 OpenClaw 调用
    """
    
    def __init__(self, server_url: str = "http://localhost:8080"):
        self.server_url = server_url
    
    def _api_call(self, endpoint: str, method: str = "GET", data: dict = None) -> dict:
        """调用 API"""
        import urllib.request
        import urllib.error
        
        url = f"{self.server_url}/api/{endpoint}"
        
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
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ============ OpenClaw 快捷操作 ============
    
    def quick_add_game(self, date_str: str, duration: int, score: str, 
                       cost: float = 0, note: str = "") -> str:
        """
        快速添加比赛记录
        
        Args:
            date_str: 日期 (YYYY-MM-DD)
            duration: 时长（分钟）
            score: 比分 (如 "100:95")
            cost: 花费
            note: 备注
        """
        result = self._api_call("records", "POST", {
            "type": "比赛",
            "date": date_str,
            "duration_minutes": duration,
            "cost": cost,
            "score": score,
            "note": note
        })
        
        if result.get("success"):
            return f"✅ 已添加比赛记录：{date_str} {duration}分钟 比分 {score}"
        return f"❌ 添加失败：{result.get('error', '未知错误')}"
    
    def quick_add_practice(self, date_str: str, duration: int, technique: str,
                          cost: float = 0, note: str = "") -> str:
        """
        快速添加练习记录
        
        Args:
            date_str: 日期 (YYYY-MM-DD)
            duration: 时长（分钟）
            technique: 训练内容
            cost: 花费
            note: 备注
        """
        result = self._api_call("records", "POST", {
            "type": "练习",
            "date": date_str,
            "duration_minutes": duration,
            "cost": cost,
            "technique": technique,
            "note": note
        })
        
        if result.get("success"):
            return f"✅ 已添加练习记录：{date_str} {duration}分钟 - {technique}"
        return f"❌ 添加失败：{result.get('error', '未知错误')}"
    
    def quick_add_lesson(self, date_str: str, duration: int, technique: str,
                        cost: float = 0, note: str = "") -> str:
        """
        快速添加上课记录
        
        Args:
            date_str: 日期 (YYYY-MM-DD)
            duration: 时长（分钟）
            technique: 上课内容
            cost: 花费
            note: 备注
        """
        result = self._api_call("records", "POST", {
            "type": "上课",
            "date": date_str,
            "duration_minutes": duration,
            "cost": cost,
            "technique": technique,
            "note": note
        })
        
        if result.get("success"):
            return f"✅ 已添加上课记录：{date_str} {duration}分钟 - {technique}"
        return f"❌ 添加失败：{result.get('error', '未知错误')}"
    
    def quick_add_casual(self, date_str: str, duration: int, 
                        cost: float = 0, note: str = "") -> str:
        """
        快速添加约球记录
        
        Args:
            date_str: 日期 (YYYY-MM-DD)
            duration: 时长（分钟）
            cost: 花费
            note: 备注
        """
        result = self._api_call("records", "POST", {
            "type": "约球",
            "date": date_str,
            "duration_minutes": duration,
            "cost": cost,
            "note": note
        })
        
        if result.get("success"):
            return f"✅ 已添加约球记录：{date_str} {duration}分钟"
        return f"❌ 添加失败：{result.get('error', '未知错误')}"
    
    def get_summary(self, days: int = 7) -> str:
        """
        获取近期打球汇总
        
        Args:
            days: 最近多少天
        """
        result = self._api_call(f"openclaw/summary?days={days}")
        
        if not result.get("success"):
            return f"❌ 获取失败：{result.get('error', '未知错误')}"
        
        data = result.get("data", {})
        summary = data.get("summary", {})
        overall = data.get("overall_stats", {})
        recent = data.get("recent_records", [])
        
        output = f"""
🏀 最近 {days} 天打球汇总

📊 统计：
   • 记录数：{summary.get('records_count', 0)} 条
   • 总时长：{summary.get('total_duration', 0)} 分钟 ({summary.get('total_duration', 0)//60}小时{summary.get('total_duration', 0)%60}分)
   • 总花费：¥{summary.get('total_cost', 0)}

🏆 累计数据：
   • 总记录：{overall.get('total_records', 0)} 条
   • 总时长：{overall.get('total_duration', 0)//60} 小时
   • 总花费：¥{overall.get('total_cost', 0)}
   • 胜率：{overall.get('win_rate', '--')}%

📝 最近记录：
"""
        for r in recent:
            icon = {"比赛": "🏆", "约球": "🤝", "练习": "💪", "上课": "🎓"}.get(r['type'], '🏀')
            output += f"   {icon} {r['date']} {r['type']} {r['duration_minutes']}分钟"
            if r.get('score'):
                output += f" 比分{r['score']}"
            if r.get('technique'):
                output += f" - {r['technique']}"
            output += "\n"
        
        return output
    
    def get_all_records(self, record_type: str = None) -> str:
        """
        获取所有记录
        
        Args:
            record_type: 筛选类型（可选）
        """
        endpoint = "records"
        if record_type:
            endpoint += f"?type={record_type}"
        
        result = self._api_call(endpoint)
        
        if not result.get("success"):
            return f"❌ 获取失败"
        
        records = result.get("data", [])
        
        if not records:
            return "📭 暂无记录"
        
        output = f"📋 共 {len(records)} 条记录\n" + "="*50 + "\n"
        
        for r in records:
            icon = {"比赛": "🏆", "约球": "🤝", "练习": "💪", "上课": "🎓"}.get(r['type'], '🏀')
            output += f"\n{icon} [{r['type']}] {r['date']}\n"
            output += f"   时长：{r['duration_minutes']}分钟"
            if r.get('cost', 0) > 0:
                output += f" | 花费：¥{r['cost']}"
            output += "\n"
            
            if r.get('score'):
                output += f"   比分：{r['score']}\n"
            if r.get('technique'):
                output += f"   内容：{r['technique']}\n"
            if r.get('note'):
                output += f"   备注：{r['note']}\n"
        
        return output


# ============ 全局实例 ============

bridge = BasketballOpenClawBridge()

# 快捷函数供 OpenClaw 直接调用
def add_game(date: str, duration: int, score: str, cost: float = 0, note: str = ""):
    """添加比赛记录"""
    return bridge.quick_add_game(date, duration, score, cost, note)

def add_practice(date: str, duration: int, technique: str, cost: float = 0, note: str = ""):
    """添加练习记录"""
    return bridge.quick_add_practice(date, duration, technique, cost, note)

def add_lesson(date: str, duration: int, technique: str, cost: float = 0, note: str = ""):
    """添加上课记录"""
    return bridge.quick_add_lesson(date, duration, technique, cost, note)

def add_casual(date: str, duration: int, cost: float = 0, note: str = ""):
    """添加约球记录"""
    return bridge.quick_add_casual(date, duration, cost, note)

def summary(days: int = 7):
    """查看近期汇总"""
    return bridge.get_summary(days)

def list_records(type: str = None):
    """列出所有记录"""
    return bridge.get_all_records(type)


# ============ CLI 入口 ============

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("""
🏀 OpenClaw 打球记录桥接器

使用方法:
  python openclaw_bridge.py <命令> [参数]

命令:
  add_game <日期> <时长> <比分> [花费] [备注]    添加比赛记录
  add_practice <日期> <时长> <内容> [花费] [备注]  添加练习记录
  add_lesson <日期> <时长> <内容> [花费] [备注]    添加上课记录
  add_casual <日期> <时长> [花费] [备注]           添加约球记录
  summary [天数]                                   查看近期汇总
  list [类型]                                      列出记录

示例:
  python openclaw_bridge.py add_game 2026-03-10 120 100:95 50 "vs火箭队"
  python openclaw_bridge.py add_practice 2026-03-11 60 "三分球训练"
  python openclaw_bridge.py summary 7
        """)
        sys.exit(0)
    
    cmd = sys.argv[1]
    args = sys.argv[2:]
    
    if cmd == "add_game" and len(args) >= 3:
        print(add_game(args[0], int(args[1]), args[2], 
                      float(args[3]) if len(args) > 3 else 0,
                      args[4] if len(args) > 4 else ""))
    
    elif cmd == "add_practice" and len(args) >= 3:
        print(add_practice(args[0], int(args[1]), args[2],
                          float(args[3]) if len(args) > 3 else 0,
                          args[4] if len(args) > 4 else ""))
    
    elif cmd == "add_lesson" and len(args) >= 3:
        print(add_lesson(args[0], int(args[1]), args[2],
                        float(args[3]) if len(args) > 3 else 0,
                        args[4] if len(args) > 4 else ""))
    
    elif cmd == "add_casual" and len(args) >= 2:
        print(add_casual(args[0], int(args[1]),
                        float(args[2]) if len(args) > 2 else 0,
                        args[3] if len(args) > 3 else ""))
    
    elif cmd == "summary":
        days = int(args[0]) if args else 7
        print(summary(days))
    
    elif cmd == "list":
        print(list_records(args[0] if args else None))
    
    else:
        print(f"❌ 未知命令: {cmd}")
