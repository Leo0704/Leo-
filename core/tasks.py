"""
任务管理器
==========

管理工作流中的任务列表。
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class Task:
    """任务"""
    id: str
    title: str
    status: str = "pending"  # pending, in_progress, completed, blocked
    priority: int = 999
    description: str = ""
    steps: list = field(default_factory=list)
    completed_at: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(**data)


class TaskManager:
    """任务管理器"""

    def __init__(self, workflow_dir: Path):
        self.workflow_dir = workflow_dir
        self.tasks_file = workflow_dir / "tasks.json"
        self.status_file = workflow_dir / "status.json"

    def load_tasks(self) -> list[Task]:
        """加载所有任务"""
        if not self.tasks_file.exists():
            return []

        with open(self.tasks_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return [Task.from_dict(t) for t in data.get("tasks", [])]

    def save_tasks(self, tasks: list[Task]) -> None:
        """保存所有任务"""
        data = {"tasks": [t.to_dict() for t in tasks]}
        with open(self.tasks_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_next_task(self) -> Optional[Task]:
        """获取下一个待处理任务"""
        tasks = self.load_tasks()

        # 优先返回进行中的任务
        for task in tasks:
            if task.status == "in_progress":
                return task

        # 否则返回优先级最高的待处理任务
        pending = [t for t in tasks if t.status == "pending"]
        if pending:
            return min(pending, key=lambda x: x.priority)

        return None

    def start_task(self, task_id: str) -> None:
        """开始任务"""
        tasks = self.load_tasks()
        for task in tasks:
            if task.id == task_id:
                task.status = "in_progress"
                break
        self.save_tasks(tasks)
        self._update_status()

    def complete_task(self, task_id: str) -> None:
        """完成任务"""
        tasks = self.load_tasks()
        for task in tasks:
            if task.id == task_id:
                task.status = "completed"
                task.completed_at = datetime.now().isoformat()
                break
        self.save_tasks(tasks)
        self._update_status()

    def add_task(self, title: str, description: str = "", priority: int = 999, steps: list = None) -> Task:
        """添加新任务"""
        tasks = self.load_tasks()

        # 生成新 ID
        existing_ids = [t.id for t in tasks]
        num = 1
        while f"task-{num:03d}" in existing_ids:
            num += 1

        task = Task(
            id=f"task-{num:03d}",
            title=title,
            description=description,
            priority=priority,
            steps=steps or []
        )

        tasks.append(task)
        self.save_tasks(tasks)

        return task

    def get_stats(self) -> dict:
        """获取统计信息"""
        tasks = self.load_tasks()

        return {
            "total": len(tasks),
            "completed": sum(1 for t in tasks if t.status == "completed"),
            "in_progress": sum(1 for t in tasks if t.status == "in_progress"),
            "pending": sum(1 for t in tasks if t.status == "pending"),
            "blocked": sum(1 for t in tasks if t.status == "blocked"),
        }

    def _update_status(self) -> None:
        """更新状态文件"""
        stats = self.get_stats()
        next_task = self.get_next_task()

        if self.status_file.exists():
            with open(self.status_file, "r", encoding="utf-8") as f:
                status = json.load(f)
        else:
            status = {}

        status["stats"] = stats
        status["last_update"] = datetime.now().isoformat()
        status["current_task"] = {
            "id": next_task.id,
            "title": next_task.title,
            "status": next_task.status
        } if next_task else None

        with open(self.status_file, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=2, ensure_ascii=False)

    def print_summary(self) -> None:
        """打印摘要"""
        stats = self.get_stats()
        next_task = self.get_next_task()

        print(f"\n📊 任务统计:")
        print(f"   总计: {stats['total']}")
        print(f"   ✅ 已完成: {stats['completed']}")
        print(f"   🔄 进行中: {stats['in_progress']}")
        print(f"   ⏳ 待处理: {stats['pending']}")
        print(f"   🚫 已阻塞: {stats['blocked']}")

        if stats['total'] > 0:
            progress = stats['completed'] / stats['total'] * 100
            bar_len = int(progress / 5)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            print(f"\n   进度: [{bar}] {progress:.1f}%")

        if next_task:
            print(f"\n📌 下一个任务:")
            print(f"   [{next_task.id}] {next_task.title}")
            if next_task.description:
                print(f"   {next_task.description}")
