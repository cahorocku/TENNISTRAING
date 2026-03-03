#!/usr/bin/env python3
"""
打球记录系统
记录类型：比赛/约球/练习/上课
"""

import json
import os
from datetime import datetime, date
from typing import Optional, List, Dict, Any

DATA_FILE = "/Users/ricky/basketball_records.json"


class BasketballTracker:
    """打球记录追踪器"""
    
    RECORD_TYPES = ["比赛", "约球", "练习", "上课"]
    
    def __init__(self):
        self.records: List[Dict[str, Any]] = []
        self.load_data()
    
    def load_data(self):
        """加载数据"""
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                self.records = json.load(f)
        else:
            self.records = []
    
    def save_data(self):
        """保存数据"""
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, ensure_ascii=False, indent=2)
    
    def add_record(self, record_type: str, record_date: str, duration_minutes: int,
                   cost: float = 0, score: str = "", technique: str = "", 
                   note: str = "") -> bool:
        """
        添加记录
        
        Args:
            record_type: 记录类型（比赛/约球/练习/上课）
            record_date: 日期（YYYY-MM-DD）
            duration_minutes: 时长（分钟）
            cost: 花费金额（元）
            score: 比赛成绩（如 "100:95"）
            technique: 练习/上课的技术内容
            note: 备注
        """
        if record_type not in self.RECORD_TYPES:
            print(f"❌ 无效的记录类型，请选择: {', '.join(self.RECORD_TYPES)}")
            return False
        
        record = {
            "id": len(self.records) + 1,
            "type": record_type,
            "date": record_date,
            "duration_minutes": duration_minutes,
            "cost": cost,
            "score": score,
            "technique": technique,
            "note": note,
            "created_at": datetime.now().isoformat()
        }
        
        self.records.append(record)
        self.save_data()
        print(f"✅ 已添加记录: {record_date} {record_type} {duration_minutes}分钟")
        return True
    
    def get_records(self, record_type: Optional[str] = None, 
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """查询记录"""
        result = self.records.copy()
        
        if record_type:
            result = [r for r in result if r["type"] == record_type]
        
        if start_date:
            result = [r for r in result if r["date"] >= start_date]
        
        if end_date:
            result = [r for r in result if r["date"] <= end_date]
        
        return sorted(result, key=lambda x: x["date"])
    
    def get_record_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取记录"""
        for record in self.records:
            if record["id"] == record_id:
                return record
        return None
    
    def update_record(self, record_id: int, **kwargs) -> bool:
        """更新记录"""
        record = self.get_record_by_id(record_id)
        if not record:
            print(f"❌ 未找到ID为 {record_id} 的记录")
            return False
        
        valid_fields = ["type", "date", "duration_minutes", "cost", "score", "technique", "note"]
        for key, value in kwargs.items():
            if key in valid_fields:
                record[key] = value
        
        record["updated_at"] = datetime.now().isoformat()
        self.save_data()
        print(f"✅ 已更新记录 ID: {record_id}")
        return True
    
    def delete_record(self, record_id: int) -> bool:
        """删除记录"""
        for i, record in enumerate(self.records):
            if record["id"] == record_id:
                del self.records[i]
                # 重新编号
                for idx, r in enumerate(self.records):
                    r["id"] = idx + 1
                self.save_data()
                print(f"✅ 已删除记录 ID: {record_id}")
                return True
        print(f"❌ 未找到ID为 {record_id} 的记录")
        return False
    
    def get_statistics(self, start_date: Optional[str] = None, 
                       end_date: Optional[str] = None) -> Dict[str, Any]:
        """获取统计信息"""
        records = self.get_records(start_date=start_date, end_date=end_date)
        
        stats = {
            "总记录数": len(records),
            "总时长(分钟)": 0,
            "总花费(元)": 0,
            "各类型统计": {}
        }
        
        for rtype in self.RECORD_TYPES:
            type_records = [r for r in records if r["type"] == rtype]
            stats["各类型统计"][rtype] = {
                "次数": len(type_records),
                "总时长(分钟)": sum(r["duration_minutes"] for r in type_records),
                "总花费(元)": sum(r["cost"] for r in type_records)
            }
        
        stats["总时长(分钟)"] = sum(r["duration_minutes"] for r in records)
        stats["总花费(元)"] = sum(r["cost"] for r in records)
        
        # 比赛胜率统计
        game_records = [r for r in records if r["type"] == "比赛" and r["score"]]
        if game_records:
            wins = 0
            for r in game_records:
                try:
                    my_score, opponent_score = r["score"].split(":")
                    if int(my_score) > int(opponent_score):
                        wins += 1
                except:
                    pass
            stats["比赛胜率"] = f"{wins}/{len(game_records)} ({wins/len(game_records)*100:.1f}%)"
        
        return stats
    
    def display_records(self, records: List[Dict[str, Any]]):
        """格式化显示记录"""
        if not records:
            print("暂无记录")
            return
        
        print("\n" + "="*100)
        print(f"{'ID':<5}{'日期':<12}{'类型':<8}{'时长(分)':<10}{'花费(元)':<10}{'成绩/技术':<20}{'备注':<20}")
        print("-"*100)
        
        for r in records:
            score_tech = r.get("score") or r.get("technique") or ""
            score_tech = score_tech[:18]  # 截断显示
            note = (r.get("note") or "")[:18]
            print(f"{r['id']:<5}{r['date']:<12}{r['type']:<8}{r['duration_minutes']:<10}"
                  f"{r['cost']:<10.2f}{score_tech:<20}{note:<20}")
        print("="*100)
    
    def display_statistics(self, stats: Dict[str, Any]):
        """显示统计信息"""
        print("\n" + "="*50)
        print("📊 打球统计")
        print("="*50)
        for key, value in stats.items():
            if key == "各类型统计":
                print(f"\n【{key}】")
                for rtype, type_stats in value.items():
                    if type_stats["次数"] > 0:
                        print(f"  📌 {rtype}:")
                        for k, v in type_stats.items():
                            if isinstance(v, float):
                                print(f"     {k}: {v:.2f}")
                            else:
                                print(f"     {k}: {v}")
            else:
                if isinstance(value, float):
                    print(f"{key}: {value:.2f}")
                else:
                    print(f"{key}: {value}")
        print("="*50)


# ============ 快捷操作函数 ============

tracker = BasketballTracker()


def add_game(record_date: str, duration: int, score: str, cost: float = 0, note: str = ""):
    """添加比赛记录"""
    return tracker.add_record("比赛", record_date, duration, cost, score=score, note=note)


def add_casual(record_date: str, duration: int, cost: float = 0, note: str = ""):
    """添加约球记录"""
    return tracker.add_record("约球", record_date, duration, cost, note=note)


def add_practice(record_date: str, duration: int, technique: str, cost: float = 0, note: str = ""):
    """添加练习记录"""
    return tracker.add_record("练习", record_date, duration, cost, technique=technique, note=note)


def add_lesson(record_date: str, duration: int, technique: str, cost: float = 0, note: str = ""):
    """添加上课记录"""
    return tracker.add_record("上课", record_date, duration, cost, technique=technique, note=note)


def show_all():
    """显示所有记录"""
    records = tracker.get_records()
    tracker.display_records(records)


def show_stats():
    """显示统计"""
    stats = tracker.get_statistics()
    tracker.display_statistics(stats)


def delete(id: int):
    """删除记录"""
    return tracker.delete_record(id)


def update(id: int, **kwargs):
    """更新记录"""
    return tracker.update_record(id, **kwargs)


def search(record_type: str = None, start_date: str = None, end_date: str = None):
    """搜索记录"""
    records = tracker.get_records(record_type, start_date, end_date)
    tracker.display_records(records)


# ============ 命令行交互 ============

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("""
🏀 打球记录系统

用法:
  python basketball_tracker.py add <类型> <日期> <时长> [选项]
  python basketball_tracker.py list [类型]
  python basketball_tracker.py stats
  python basketball_tracker.py delete <ID>
  
类型: 比赛 / 约球 / 练习 / 上课

示例:
  python basketball_tracker.py add 比赛 2026-03-01 120 --score 100:95 --cost 50
  python basketball_tracker.py add 练习 2026-03-02 60 --technique "投篮训练" --cost 0
  python basketball_tracker.py add 上课 2026-03-03 90 --technique "运球技巧" --cost 200
  python basketball_tracker.py list
  python basketball_tracker.py stats
        """)
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "add":
        if len(sys.argv) < 5:
            print("用法: add <类型> <日期> <时长>")
            sys.exit(1)
        
        rtype = sys.argv[2]
        rdate = sys.argv[3]
        duration = int(sys.argv[4])
        
        cost = 0
        score = ""
        technique = ""
        note = ""
        
        # 解析可选参数
        i = 5
        while i < len(sys.argv):
            if sys.argv[i] == "--cost" and i + 1 < len(sys.argv):
                cost = float(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == "--score" and i + 1 < len(sys.argv):
                score = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--technique" and i + 1 < len(sys.argv):
                technique = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--note" and i + 1 < len(sys.argv):
                note = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        
        tracker.add_record(rtype, rdate, duration, cost, score, technique, note)
    
    elif cmd == "list":
        rtype = sys.argv[2] if len(sys.argv) > 2 else None
        records = tracker.get_records(record_type=rtype)
        tracker.display_records(records)
    
    elif cmd == "stats":
        stats = tracker.get_statistics()
        tracker.display_statistics(stats)
    
    elif cmd == "delete":
        if len(sys.argv) < 3:
            print("用法: delete <ID>")
            sys.exit(1)
        tracker.delete_record(int(sys.argv[2]))
    
    else:
        print(f"未知命令: {cmd}")
