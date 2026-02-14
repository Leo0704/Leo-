"""
任务管理器
==========

管理工作流中的任务列表，支持依赖关系、重试机制和错误处理。
"""

import json
import logging
import fcntl
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from enum import Enum

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class ErrorStrategy(str, Enum):
    """错误处理策略"""
    RETRY = "retry"
    SKIP = "skip"
    ESCALATE = "escalate"


@dataclass
class Task:
    """任务"""
    id: str
    title: str
    status: str = "pending"
    priority: int = 999
    description: str = ""
    steps: List[str] = field(default_factory=list)
    completed_at: Optional[str] = None

    # 依赖关系
    dependencies: List[str] = field(default_factory=list)  # 依赖的任务 ID
    blocked_by: List[str] = field(default_factory=list)    # 被哪些任务阻塞
    blocks: List[str] = field(default_factory=list)        # 阻塞哪些任务

    # 重试机制
    retry_count: int = 0
    max_retries: int = 3
    last_error: Optional[str] = None
    error_strategy: str = "retry"

    # 新增：Skills 集成
    skill: Optional[str] = None  # 使用的 skill 名称（如 "product-manager-toolkit"）
    agent: Optional[str] = None  # 使用的自定义 agent 名称

    # 新增：多角色协作
    role: Optional[str] = None  # 任务角色：PM, Developer, Tester, Designer, Reviewer
    assignee: Optional[str] = None  # 负责人
    reviewers: List[str] = field(default_factory=list)  # 审核人员列表

    # 新增：验收标准
    acceptance_criteria: List[str] = field(default_factory=list)  # 验收标准列表
    criteria_status: dict = field(default_factory=dict)  # 每个标准的完成状态

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        # 处理未知字段，避免报错
        known_fields = {
            'id', 'title', 'status', 'priority', 'description',
            'steps', 'completed_at', 'dependencies', 'blocked_by',
            'blocks', 'retry_count', 'max_retries', 'last_error',
            'error_strategy', 'skill', 'agent', 'role', 'assignee',
            'reviewers', 'acceptance_criteria', 'criteria_status'
        }
        filtered = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered)

    def can_start(self, completed_task_ids: set) -> bool:
        """检查任务是否可以开始（依赖已满足）"""
        return all(dep_id in completed_task_ids for dep_id in self.dependencies)

    def should_retry(self) -> bool:
        """检查是否应该重试"""
        return (
            self.status == "failed" and
            self.retry_count < self.max_retries and
            self.error_strategy == "retry"
        )

    def check_acceptance_criteria(self) -> bool:
        """检查所有验收标准是否满足"""
        if not self.acceptance_criteria:
            return True  # 没有验收标准则默认通过
        return all(
            self.criteria_status.get(criterion, False)
            for criterion in self.acceptance_criteria
        )

    def update_criterion_status(self, criterion: str, completed: bool) -> None:
        """更新单个验收标准的状态"""
        if criterion in self.acceptance_criteria:
            self.criteria_status[criterion] = completed


class FileLock:
    """文件锁，防止并发访问"""

    def __init__(self, lock_file: Path):
        self.lock_file = lock_file
        self.lock = None

    def __enter__(self):
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)
        self.lock = open(self.lock_file, 'w')
        fcntl.flock(self.lock.fileno(), fcntl.LOCK_EX)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lock:
            fcntl.flock(self.lock.fileno(), fcntl.LOCK_UN)
            self.lock.close()
        return False


class TaskManager:
    """任务管理器"""

    def __init__(self, workflow_dir: Path):
        self.workflow_dir = workflow_dir
        self.tasks_file = workflow_dir / "tasks.json"
        self.status_file = workflow_dir / "status.json"
        self.lock_file = workflow_dir / ".lock"
        self.backup_dir = workflow_dir / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _safe_read_json(self, file_path: Path, default=None) -> dict:
        """安全读取 JSON 文件"""
        if default is None:
            default = {}

        if not file_path.exists():
            return default

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析错误 {file_path}: {e}")
            # 尝试恢复备份
            backup = self._find_latest_backup(file_path)
            if backup:
                logger.info(f"尝试从备份恢复: {backup}")
                try:
                    with open(backup, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception:
                    pass
            return default
        except IOError as e:
            logger.error(f"文件读取错误 {file_path}: {e}")
            return default
        except Exception as e:
            logger.error(f"未知错误 {file_path}: {e}")
            return default

    def _safe_write_json(self, file_path: Path, data: dict) -> bool:
        """安全写入 JSON 文件"""
        try:
            # 先写入临时文件
            temp_file = file_path.with_suffix('.tmp')
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # 备份原文件
            if file_path.exists():
                backup_name = f"{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                backup_path = self.backup_dir / backup_name
                file_path.rename(backup_path)
                # 清理旧备份（保留最近 5 个）
                self._cleanup_backups(file_path.stem)

            # 原子操作：重命名临时文件
            temp_file.rename(file_path)
            return True

        except IOError as e:
            logger.error(f"文件写入错误 {file_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"未知错误 {file_path}: {e}")
            return False

    def _find_latest_backup(self, file_path: Path) -> Optional[Path]:
        """查找最新的备份文件"""
        pattern = f"{file_path.stem}_*.json"
        backups = sorted(self.backup_dir.glob(pattern), reverse=True)
        return backups[0] if backups else None

    def _cleanup_backups(self, file_stem: str, keep: int = 5):
        """清理旧备份"""
        pattern = f"{file_stem}_*.json"
        backups = sorted(self.backup_dir.glob(pattern), reverse=True)
        for old_backup in backups[keep:]:
            try:
                old_backup.unlink()
            except Exception:
                pass

    def load_tasks(self) -> List[Task]:
        """加载所有任务"""
        with FileLock(self.lock_file):
            data = self._safe_read_json(self.tasks_file, {"tasks": []})
            return [Task.from_dict(t) for t in data.get("tasks", [])]

    def save_tasks(self, tasks: List[Task]) -> bool:
        """保存所有任务"""
        with FileLock(self.lock_file):
            data = {"tasks": [t.to_dict() for t in tasks]}
            return self._safe_write_json(self.tasks_file, data)

    def get_next_task(self) -> Optional[Task]:
        """获取下一个待处理任务（考虑依赖关系）"""
        tasks = self.load_tasks()
        completed_ids = {t.id for t in tasks if t.status == "completed"}

        # 优先返回可开始的进行中任务
        for task in tasks:
            if task.status == "in_progress" or task.should_retry():
                return task

        # 返回优先级最高且依赖满足的待处理任务
        pending = [
            t for t in tasks
            if t.status == "pending" and t.can_start(completed_ids)
        ]
        if pending:
            return min(pending, key=lambda x: x.priority)

        # 检查是否有被阻塞的任务
        blocked = [
            t for t in tasks
            if t.status == "pending" and not t.can_start(completed_ids)
        ]
        if blocked and not pending:
            # 更新阻塞状态
            for task in blocked:
                task.blocked_by = [
                    dep_id for dep_id in task.dependencies
                    if dep_id not in completed_ids
                ]
                task.status = "blocked"
            self.save_tasks(tasks)

        return None

    def start_task(self, task_id: str) -> bool:
        """开始任务"""
        tasks = self.load_tasks()
        for task in tasks:
            if task.id == task_id:
                task.status = "in_progress"
                task.retry_count = 0
                task.last_error = None
                break
        else:
            logger.warning(f"任务不存在: {task_id}")
            return False

        success = self.save_tasks(tasks)
        if success:
            self._update_status()
        return success

    def complete_task(self, task_id: str) -> bool:
        """完成任务"""
        tasks = self.load_tasks()
        for task in tasks:
            if task.id == task_id:
                task.status = "completed"
                task.completed_at = datetime.now().isoformat()
                break
        else:
            logger.warning(f"任务不存在: {task_id}")
            return False

        success = self.save_tasks(tasks)
        if success:
            self._update_status()
            # 解锁依赖此任务的其他任务
            self._unblock_dependent_tasks(task_id, tasks)
        return success

    def fail_task(self, task_id: str, error: str) -> bool:
        """标记任务失败"""
        tasks = self.load_tasks()
        for task in tasks:
            if task.id == task_id:
                task.status = "failed"
                task.last_error = error
                task.retry_count += 1
                break
        else:
            return False

        success = self.save_tasks(tasks)
        if success:
            self._update_status()
        return success

    def retry_task(self, task_id: str) -> bool:
        """重试失败的任务"""
        tasks = self.load_tasks()
        for task in tasks:
            if task.id == task_id and task.should_retry():
                task.status = "in_progress"
                task.last_error = None
                break
        else:
            return False

        return self.save_tasks(tasks)

    def add_task(
        self,
        title: str,
        description: str = "",
        priority: int = 999,
        steps: List[str] = None,
        dependencies: List[str] = None,
        max_retries: int = 3,
        skill: str = None,
        agent: str = None,
        role: str = None,
        assignee: str = None,
        reviewers: List[str] = None,
        acceptance_criteria: List[str] = None
    ) -> Optional[Task]:
        """添加新任务"""
        tasks = self.load_tasks()

        # 生成新 ID
        existing_ids = {t.id for t in tasks}
        num = 1
        while f"task-{num:03d}" in existing_ids:
            num += 1

        task = Task(
            id=f"task-{num:03d}",
            title=title,
            description=description,
            priority=priority,
            steps=steps or [],
            dependencies=dependencies or [],
            max_retries=max_retries,
            skill=skill,
            agent=agent,
            role=role,
            assignee=assignee,
            reviewers=reviewers or [],
            acceptance_criteria=acceptance_criteria or [],
            criteria_status={criterion: False for criterion in (acceptance_criteria or [])}
        )

        tasks.append(task)

        # 更新被依赖任务的 blocks 字段
        if dependencies:
            for dep_id in dependencies:
                for t in tasks:
                    if t.id == dep_id:
                        if task.id not in t.blocks:
                            t.blocks.append(task.id)

        success = self.save_tasks(tasks)
        return task if success else None

    def _unblock_dependent_tasks(self, completed_task_id: str, tasks: List[Task]) -> None:
        """解锁依赖已完成的任务"""
        for task in tasks:
            if completed_task_id in task.dependencies:
                task.blocked_by = [
                    dep_id for dep_id in task.dependencies
                    if dep_id != completed_task_id
                ]
                if not task.blocked_by and task.status == "blocked":
                    task.status = "pending"
        self.save_tasks(tasks)

    def get_stats(self) -> dict:
        """获取统计信息"""
        tasks = self.load_tasks()

        return {
            "total": len(tasks),
            "completed": sum(1 for t in tasks if t.status == "completed"),
            "in_progress": sum(1 for t in tasks if t.status == "in_progress"),
            "pending": sum(1 for t in tasks if t.status == "pending"),
            "blocked": sum(1 for t in tasks if t.status == "blocked"),
            "failed": sum(1 for t in tasks if t.status == "failed"),
        }

    def _update_status(self) -> bool:
        """更新状态文件"""
        stats = self.get_stats()
        next_task = self.get_next_task()

        status = self._safe_read_json(self.status_file, {})
        status["stats"] = stats
        status["last_update"] = datetime.now().isoformat()

        if next_task:
            status["current_task"] = {
                "id": next_task.id,
                "title": next_task.title,
                "status": next_task.status
            }
        else:
            status["current_task"] = None

        return self._safe_write_json(self.status_file, status)

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
        print(f"   ❌ 已失败: {stats['failed']}")

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
            if next_task.dependencies:
                print(f"   依赖: {', '.join(next_task.dependencies)}")

    def validate_dependencies(self) -> List[str]:
        """验证依赖关系，返回问题列表"""
        tasks = self.load_tasks()
        task_ids = {t.id for t in tasks}
        issues = []

        for task in tasks:
            for dep_id in task.dependencies:
                if dep_id not in task_ids:
                    issues.append(f"任务 {task.id} 依赖不存在的任务 {dep_id}")

            # 检查循环依赖
            visited = set()
            self._check_circular_deps(task, tasks, visited, issues)

        return issues

    def _check_circular_deps(self, task: Task, all_tasks: List[Task],
                             visited: set, issues: List[str]) -> None:
        """检查循环依赖"""
        if task.id in visited:
            issues.append(f"检测到循环依赖: {task.id}")
            return

        visited.add(task.id)
        for dep_id in task.dependencies:
            dep_task = next((t for t in all_tasks if t.id == dep_id), None)
            if dep_task:
                self._check_circular_deps(dep_task, all_tasks, visited.copy(), issues)
