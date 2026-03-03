#!/usr/bin/env python3
"""
🏀 打球记录 Web 服务端
为前端和 OpenClaw 提供 API 接口
"""

import json
import os
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 数据文件路径
DATA_FILE = Path("/Users/ricky/basketball_records.json")
WEB_DIR = Path("/Users/ricky/basketball_web")

app = FastAPI(title="🏀 打球记录系统", version="1.0.0")

# 启用 CORS，允许 OpenClaw 访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件和模板
app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")
templates = Jinja2Templates(directory=WEB_DIR / "templates")


# ============ 数据模型 ============

class RecordCreate(BaseModel):
    type: str  # 比赛/约球/练习/上课
    date: str
    duration_minutes: int
    cost: float = 0
    score: str = ""  # 比赛成绩
    technique: str = ""  # 练习/上课技术
    note: str = ""


class RecordUpdate(BaseModel):
    type: Optional[str] = None
    date: Optional[str] = None
    duration_minutes: Optional[int] = None
    cost: Optional[float] = None
    score: Optional[str] = None
    technique: Optional[str] = None
    note: Optional[str] = None


class Record(RecordCreate):
    id: int
    created_at: str


# ============ 数据操作 ============

class BasketballDataStore:
    RECORD_TYPES = ["比赛", "约球", "练习", "上课"]
    
    def __init__(self):
        self.records: List[Dict[str, Any]] = []
        self.load_data()
    
    def load_data(self):
        """加载数据"""
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                self.records = json.load(f)
        else:
            self.records = []
    
    def save_data(self):
        """保存数据"""
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, ensure_ascii=False, indent=2)
    
    def get_all_records(self, record_type: Optional[str] = None) -> List[Dict]:
        """获取所有记录"""
        records = self.records.copy()
        if record_type:
            records = [r for r in records if r["type"] == record_type]
        return sorted(records, key=lambda x: x["date"], reverse=True)
    
    def get_record(self, record_id: int) -> Optional[Dict]:
        """获取单条记录"""
        for record in self.records:
            if record["id"] == record_id:
                return record
        return None
    
    def create_record(self, data: RecordCreate) -> Dict:
        """创建记录"""
        if data.type not in self.RECORD_TYPES:
            raise ValueError(f"无效的类型: {data.type}")
        
        new_id = max([r["id"] for r in self.records], default=0) + 1
        
        record = {
            "id": new_id,
            "type": data.type,
            "date": data.date,
            "duration_minutes": data.duration_minutes,
            "cost": data.cost,
            "score": data.score,
            "technique": data.technique,
            "note": data.note,
            "created_at": datetime.now().isoformat()
        }
        
        self.records.append(record)
        self.save_data()
        return record
    
    def update_record(self, record_id: int, data: RecordUpdate) -> Optional[Dict]:
        """更新记录"""
        record = self.get_record(record_id)
        if not record:
            return None
        
        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                record[key] = value
        
        record["updated_at"] = datetime.now().isoformat()
        self.save_data()
        return record
    
    def delete_record(self, record_id: int) -> bool:
        """删除记录"""
        for i, record in enumerate(self.records):
            if record["id"] == record_id:
                del self.records[i]
                # 重新编号
                for idx, r in enumerate(self.records):
                    r["id"] = idx + 1
                self.save_data()
                return True
        return False
    
    def get_statistics(self) -> Dict:
        """获取统计数据"""
        stats = {
            "total_records": len(self.records),
            "total_duration": sum(r["duration_minutes"] for r in self.records),
            "total_cost": sum(r["cost"] for r in self.records),
            "by_type": {},
            "monthly": {}
        }
        
        # 按类型统计
        for rtype in self.RECORD_TYPES:
            type_records = [r for r in self.records if r["type"] == rtype]
            stats["by_type"][rtype] = {
                "count": len(type_records),
                "duration": sum(r["duration_minutes"] for r in type_records),
                "cost": sum(r["cost"] for r in type_records)
            }
        
        # 按月统计
        for record in self.records:
            month = record["date"][:7]  # YYYY-MM
            if month not in stats["monthly"]:
                stats["monthly"][month] = {"count": 0, "duration": 0, "cost": 0}
            stats["monthly"][month]["count"] += 1
            stats["monthly"][month]["duration"] += record["duration_minutes"]
            stats["monthly"][month]["cost"] += record["cost"]
        
        # 比赛胜率
        games = [r for r in self.records if r["type"] == "比赛" and r.get("score")]
        if games:
            wins = 0
            for g in games:
                try:
                    my, opp = g["score"].split(":")
                    if int(my) > int(opp):
                        wins += 1
                except:
                    pass
            stats["win_rate"] = round(wins / len(games) * 100, 1)
            stats["wins"] = wins
            stats["total_games"] = len(games)
        
        return stats


# 全局数据存储
data_store = BasketballDataStore()


# ============ 页面路由 ============

@app.get("/")
async def index(request: Request):
    """主页"""
    return templates.TemplateResponse("index.html", {"request": request})


# ============ API 路由 (供前端和 OpenClaw 使用) ============

@app.get("/api/records")
async def api_get_records(type: Optional[str] = None):
    """获取记录列表"""
    return {"success": True, "data": data_store.get_all_records(type)}


@app.get("/api/records/{record_id}")
async def api_get_record(record_id: int):
    """获取单条记录"""
    record = data_store.get_record(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return {"success": True, "data": record}


@app.post("/api/records")
async def api_create_record(record: RecordCreate):
    """创建记录"""
    try:
        new_record = data_store.create_record(record)
        return {"success": True, "data": new_record, "message": "✅ 记录添加成功！"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/records/{record_id}")
async def api_update_record(record_id: int, record: RecordUpdate):
    """更新记录"""
    updated = data_store.update_record(record_id, record)
    if not updated:
        raise HTTPException(status_code=404, detail="记录不存在")
    return {"success": True, "data": updated, "message": "✅ 记录更新成功！"}


@app.delete("/api/records/{record_id}")
async def api_delete_record(record_id: int):
    """删除记录"""
    if data_store.delete_record(record_id):
        return {"success": True, "message": "✅ 记录删除成功！"}
    raise HTTPException(status_code=404, detail="记录不存在")


@app.get("/api/statistics")
async def api_get_statistics():
    """获取统计数据"""
    return {"success": True, "data": data_store.get_statistics()}


@app.get("/api/types")
async def api_get_types():
    """获取支持的记录类型"""
    return {"success": True, "data": data_store.RECORD_TYPES}


# ============ OpenClaw 专用接口 ============

@app.get("/api/openclaw/quick-add")
async def openclaw_quick_add(
    type: str,
    date: str,
    duration: int,
    cost: float = 0,
    score: str = "",
    technique: str = "",
    note: str = ""
):
    """
    OpenClaw 快速添加接口
    示例: /api/openclaw/quick-add?type=比赛&date=2026-03-10&duration=120&score=100:95
    """
    try:
        record_data = RecordCreate(
            type=type,
            date=date,
            duration_minutes=duration,
            cost=cost,
            score=score,
            technique=technique,
            note=note
        )
        new_record = data_store.create_record(record_data)
        return {
            "success": True,
            "message": f"✅ 已添加{type}记录: {date} {duration}分钟",
            "data": new_record
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/openclaw/summary")
async def openclaw_summary(days: int = 7):
    """OpenClaw 获取近期汇总"""
    from datetime import datetime, timedelta
    
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    recent = [r for r in data_store.records if r["date"] >= cutoff]
    
    stats = data_store.get_statistics()
    
    return {
        "success": True,
        "period": f"最近{days}天",
        "summary": {
            "records_count": len(recent),
            "total_duration": sum(r["duration_minutes"] for r in recent),
            "total_cost": sum(r["cost"] for r in recent)
        },
        "recent_records": sorted(recent, key=lambda x: x["date"], reverse=True)[:5],
        "overall_stats": stats
    }


if __name__ == "__main__":
    print("🏀 启动打球记录 Web 服务...")
    print(f"📊 数据文件: {DATA_FILE}")
    print(f"🌐 访问地址: http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
