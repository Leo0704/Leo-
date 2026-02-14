"""
任务管理器
==========

管理工作流中的任务列表。
设计原则：只保留 Claude Code 实际会用到的功能，不做假设性的过度设计。
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List


@dataclass
class Task:
    """任务

    字段说明：
    - id/title/status/priority/description/steps: 基础字段
    - dependencies: 依赖的任务 ID 列表（任务调度用）
    - acceptance_criteria: 验收标准列表，每项是一个 dict：
        - criterion: 标准描述
        - type: "auto"（可自动验证）或 "manual"（需用户确认）
        - verify: 当 type="auto" 时，用于验证的 shell 命令
        - passed: 是否已通过
    - context: 执行此任务时的视角/背景提示（替代虚假的"角色分配"）
    """
    id: str
    title: str
    status: str = "pending"
    priority: int = 999
    description: str = ""
    steps: List[str] = field(default_factory=list)
    completed_at: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    acceptance_criteria: List[dict] = field(default_factory=list)
    context: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        known_fields = {
            'id', 'title', 'status', 'priority', 'description',
            'steps', 'completed_at', 'dependencies',
            'acceptance_criteria', 'context'
        }
        filtered = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered)

    def can_start(self, completed_task_ids: set) -> bool:
        """检查依赖是否满足"""
        return all(dep in completed_task_ids for dep in self.dependencies)

    def pending_criteria(self) -> List[dict]:
        """返回未通过的验收标准"""
        return [c for c in self.acceptance_criteria if not c.get("passed")]

    def auto_criteria(self) -> List[dict]:
        """返回可自动验证的验收标准"""
        return [c for c in self.acceptance_criteria
                if c.get("type") == "auto" and not c.get("passed")]

    def manual_criteria(self) -> List[dict]:
        """返回需要用户确认的验收标准"""
        return [c for c in self.acceptance_criteria
                if c.get("type") == "manual" and not c.get("passed")]

    def all_criteria_passed(self) -> bool:
        """所有验收标准是否都已通过"""
        if not self.acceptance_criteria:
            return True
        return all(c.get("passed") for c in self.acceptance_criteria)

    def pass_criterion(self, index: int) -> None:
        """标记第 index 个验收标准为通过"""
        if 0 <= index < len(self.acceptance_criteria):
            self.acceptance_criteria[index]["passed"] = True

    def criteria_summary(self) -> str:
        """返回验收标准的文本摘要"""
        if not self.acceptance_criteria:
            return "（无验收标准）"
        lines = []
        for c in self.acceptance_criteria:
            icon = "pass" if c.get("passed") else "pending"
            tag = f"[{c.get('type', '?')}]"
            lines.append(f"  {'[x]' if icon == 'pass' else '[ ]'} {tag} {c['criterion']}")
        total = len(self.acceptance_criteria)
        passed = sum(1 for c in self.acceptance_criteria if c.get("passed"))
        lines.append(f"  进度: {passed}/{total}")
        return "\n".join(lines)


class TaskManager:
    """任务管理器

    职责：读写 tasks.json，提供任务查询和状态更新。
    不做：文件锁（单线程）、备份轮转（git 已有）、检查点（不需要）。
    """

    def __init__(self, workflow_dir: Path):
        self.workflow_dir = workflow_dir
        self.tasks_file = workflow_dir / "tasks.json"

    def _read_json(self, path: Path, default=None) -> dict:
        if default is None:
            default = {}
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            return default

    def _write_json(self, path: Path, data: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    def load_tasks(self) -> List[Task]:
        data = self._read_json(self.tasks_file, {"tasks": []})
        return [Task.from_dict(t) for t in data.get("tasks", [])]

    def save_tasks(self, tasks: List[Task]) -> None:
        self._write_json(self.tasks_file, {"tasks": [t.to_dict() for t in tasks]})

    def get_next_task(self) -> Optional[Task]:
        """获取下一个应处理的任务"""
        tasks = self.load_tasks()
        completed_ids = {t.id for t in tasks if t.status == "completed"}

        # 优先返回进行中的任务
        for task in tasks:
            if task.status == "in_progress":
                return task

        # 返回优先级最高且依赖满足的待处理任务
        pending = [
            t for t in tasks
            if t.status == "pending" and t.can_start(completed_ids)
        ]
        return min(pending, key=lambda x: x.priority) if pending else None

    def start_task(self, task_id: str) -> None:
        tasks = self.load_tasks()
        for task in tasks:
            if task.id == task_id:
                task.status = "in_progress"
                break
        self.save_tasks(tasks)

    def complete_task(self, task_id: str) -> None:
        tasks = self.load_tasks()
        for task in tasks:
            if task.id == task_id:
                task.status = "completed"
                task.completed_at = datetime.now().isoformat()
                break
        self.save_tasks(tasks)

    def add_task(
        self,
        title: str,
        description: str = "",
        priority: int = 999,
        steps: List[str] = None,
        dependencies: List[str] = None,
        acceptance_criteria: List[dict] = None,
        context: str = None
    ) -> Task:
        """添加新任务"""
        tasks = self.load_tasks()
        existing_ids = {t.id for t in tasks}
        num = 1
        while f"task-{num:03d}" in existing_ids:
            num += 1

        # 确保每个 criterion 都有 passed 字段
        criteria = acceptance_criteria or []
        for c in criteria:
            c.setdefault("passed", False)
            c.setdefault("type", "manual")

        task = Task(
            id=f"task-{num:03d}",
            title=title,
            description=description,
            priority=priority,
            steps=steps or [],
            dependencies=dependencies or [],
            acceptance_criteria=criteria,
            context=context
        )
        tasks.append(task)
        self.save_tasks(tasks)
        return task

    def get_stats(self) -> dict:
        tasks = self.load_tasks()
        return {
            "total": len(tasks),
            "completed": sum(1 for t in tasks if t.status == "completed"),
            "in_progress": sum(1 for t in tasks if t.status == "in_progress"),
            "pending": sum(1 for t in tasks if t.status == "pending"),
        }

    def print_summary(self) -> None:
        stats = self.get_stats()
        next_task = self.get_next_task()

        total = stats['total']
        completed = stats['completed']
        progress = (completed / total * 100) if total > 0 else 0

        print(f"\n任务: {completed}/{total} ({progress:.0f}%)")

        if next_task:
            print(f"下一个: [{next_task.id}] {next_task.title}")
            if next_task.acceptance_criteria:
                print(next_task.criteria_summary())
