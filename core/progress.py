"""
进度追踪
========

追踪和显示工作流进度的工具函数。
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class Feature:
    """功能项"""
    id: str
    category: str
    description: str
    priority: int
    status: str  # pending, in_progress, completed, blocked
    steps: list[str]
    verification: str
    notes: Optional[str] = None


class ProgressTracker:
    """进度追踪器"""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.feature_list_path = project_dir / "feature_list.json"
        self.progress_path = project_dir / "progress.json"

    def load_features(self) -> list[Feature]:
        """加载功能列表"""
        if not self.feature_list_path.exists():
            return []

        with open(self.feature_list_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return [Feature(**item) for item in data]

    def save_features(self, features: list[Feature]) -> None:
        """保存功能列表"""
        data = [
            {
                "id": f.id,
                "category": f.category,
                "description": f.description,
                "priority": f.priority,
                "status": f.status,
                "steps": f.steps,
                "verification": f.verification,
                "notes": f.notes,
            }
            for f in features
        ]

        with open(self.feature_list_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def count_status(self) -> dict[str, int]:
        """统计各状态的数量"""
        features = self.load_features()
        counts = {
            "total": len(features),
            "completed": 0,
            "in_progress": 0,
            "pending": 0,
            "blocked": 0,
        }

        for f in features:
            if f.status == "completed":
                counts["completed"] += 1
            elif f.status == "in_progress":
                counts["in_progress"] += 1
            elif f.status == "blocked":
                counts["blocked"] += 1
            else:
                counts["pending"] += 1

        return counts

    def get_next_feature(self) -> Optional[Feature]:
        """获取下一个待处理的功能"""
        features = self.load_features()

        # 优先级排序：in_progress > pending（按 priority）
        in_progress = [f for f in features if f.status == "in_progress"]
        if in_progress:
            return min(in_progress, key=lambda x: x.priority)

        pending = [f for f in features if f.status == "pending"]
        if pending:
            return min(pending, key=lambda x: x.priority)

        return None

    def update_feature_status(self, feature_id: str, new_status: str) -> None:
        """更新功能状态"""
        features = self.load_features()
        for f in features:
            if f.id == feature_id:
                f.status = new_status
                break
        self.save_features(features)

    def load_progress(self) -> dict:
        """加载进度数据"""
        if not self.progress_path.exists():
            return {
                "total_features": 0,
                "completed": 0,
                "in_progress": None,
                "last_session": None,
                "sessions_count": 0,
                "next_actions": [],
                "issues": [],
                "decisions": [],
            }

        with open(self.progress_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_progress(self, progress: dict) -> None:
        """保存进度数据"""
        progress["last_session"] = datetime.now().isoformat()
        with open(self.progress_path, "w", encoding="utf-8") as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)

    def update_progress(self) -> None:
        """更新进度文件"""
        counts = self.count_status()
        next_feature = self.get_next_feature()

        progress = self.load_progress()
        progress["total_features"] = counts["total"]
        progress["completed"] = counts["completed"]
        progress["in_progress"] = next_feature.id if next_feature else None

        if next_feature:
            progress["next_actions"] = [
                f"完成 {next_feature.id}: {next_feature.description}"
            ]

        self.save_progress(progress)

    def is_complete(self) -> bool:
        """检查是否所有任务已完成"""
        counts = self.count_status()
        if counts["total"] == 0:
            return False
        return counts["completed"] == counts["total"]

    def print_summary(self) -> None:
        """打印进度摘要"""
        counts = self.count_status()

        if counts["total"] > 0:
            percentage = (counts["completed"] / counts["total"]) * 100
            print(f"\n进度: {counts['completed']}/{counts['total']} 功能已完成 ({percentage:.1f}%)")
            print(f"   - 进行中: {counts['in_progress']}")
            print(f"   - 待处理: {counts['pending']}")
            print(f"   - 已阻塞: {counts['blocked']}")
        else:
            print("\n进度: feature_list.json 尚未创建")

    def record_session(self, summary: str, issues: list[str] = None, decisions: list[str] = None) -> None:
        """记录会话摘要"""
        notes_path = self.project_dir / "session_notes.md"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        entry = f"\n## 会话 - {timestamp}\n\n"
        entry += f"### 完成\n{summary}\n\n"

        if issues:
            entry += "### 问题\n"
            for issue in issues:
                entry += f"- {issue}\n"
            entry += "\n"

        if decisions:
            entry += "### 决策\n"
            for decision in decisions:
                entry += f"- {decision}\n"
            entry += "\n"

        entry += "---\n"

        with open(notes_path, "a", encoding="utf-8") as f:
            f.write(entry)
