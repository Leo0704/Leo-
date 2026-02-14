"""
进度追踪器
==========

追踪和显示工作流进度，支持检查点机制。
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import shutil

from core.tasks import FileLock

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Checkpoint:
    """检查点"""
    def __init__(
        self,
        checkpoint_id: str,
        task_id: str,
        timestamp: str,
        state: dict,
        description: str = ""
    ):
        self.checkpoint_id = checkpoint_id
        self.task_id = task_id
        self.timestamp = timestamp
        self.state = state
        self.description = description

    def to_dict(self) -> dict:
        return {
            "checkpoint_id": self.checkpoint_id,
            "task_id": self.task_id,
            "timestamp": self.timestamp,
            "state": self.state,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Checkpoint":
        return cls(
            checkpoint_id=data["checkpoint_id"],
            task_id=data["task_id"],
            timestamp=data["timestamp"],
            state=data["state"],
            description=data.get("description", "")
        )


class CheckpointManager:
    """检查点管理器"""

    def __init__(self, workflow_dir: Path):
        self.workflow_dir = workflow_dir
        self.checkpoints_dir = workflow_dir / "checkpoints"
        self.checkpoints_file = workflow_dir / "checkpoints.json"
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        self.lock_file = workflow_dir / ".lock"

    def create_checkpoint(
        self,
        task_id: str,
        state: dict,
        description: str = ""
    ) -> Optional[Checkpoint]:
        """创建检查点"""
        try:
            timestamp = datetime.now().isoformat()
            checkpoint_id = f"cp-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            checkpoint = Checkpoint(
                checkpoint_id=checkpoint_id,
                task_id=task_id,
                timestamp=timestamp,
                state=state,
                description=description
            )

            # 保存检查点
            checkpoints = self._load_checkpoints()
            checkpoints.append(checkpoint)

            with FileLock(self.lock_file):
                data = {"checkpoints": [cp.to_dict() for cp in checkpoints]}
                with open(self.checkpoints_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

            # 保存状态快照
            snapshot_file = self.checkpoints_dir / f"{checkpoint_id}.json"
            with open(snapshot_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)

            logger.info(f"检查点已创建: {checkpoint_id}")
            return checkpoint

        except Exception as e:
            logger.error(f"创建检查点失败: {e}")
            return None

    def restore_checkpoint(self, checkpoint_id: str) -> Optional[dict]:
        """恢复到检查点"""
        try:
            checkpoints = self._load_checkpoints()
            checkpoint = next(
                (cp for cp in checkpoints if cp.checkpoint_id == checkpoint_id),
                None
            )

            if not checkpoint:
                logger.warning(f"检查点不存在: {checkpoint_id}")
                return None

            # 读取快照
            snapshot_file = self.checkpoints_dir / f"{checkpoint_id}.json"
            if not snapshot_file.exists():
                logger.error(f"快照文件不存在: {snapshot_file}")
                return None

            with open(snapshot_file, "r", encoding="utf-8") as f:
                state = json.load(f)

            logger.info(f"检查点已恢复: {checkpoint_id}")
            return state

        except Exception as e:
            logger.error(f"恢复检查点失败: {e}")
            return None

    def list_checkpoints(self, limit: int = 10) -> List[Checkpoint]:
        """列出所有检查点"""
        checkpoints = self._load_checkpoints()
        return sorted(checkpoints, key=lambda x: x.timestamp, reverse=True)[:limit]

    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """删除检查点"""
        try:
            checkpoints = self._load_checkpoints()
            checkpoints = [cp for cp in checkpoints if cp.checkpoint_id != checkpoint_id]

            with FileLock(self.lock_file):
                data = {"checkpoints": [cp.to_dict() for cp in checkpoints]}
                with open(self.checkpoints_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

            # 删除快照文件
            snapshot_file = self.checkpoints_dir / f"{checkpoint_id}.json"
            if snapshot_file.exists():
                snapshot_file.unlink()

            logger.info(f"检查点已删除: {checkpoint_id}")
            return True

        except Exception as e:
            logger.error(f"删除检查点失败: {e}")
            return False

    def _load_checkpoints(self) -> List[Checkpoint]:
        """加载检查点列表"""
        if not self.checkpoints_file.exists():
            return []

        try:
            with open(self.checkpoints_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [Checkpoint.from_dict(cp) for cp in data.get("checkpoints", [])]
        except Exception as e:
            logger.error(f"加载检查点失败: {e}")
            return []


class ProgressTracker:
    """进度追踪器"""

    def __init__(self, workflow_dir: Path):
        self.workflow_dir = workflow_dir
        self.status_file = workflow_dir / "status.json"
        self.status_md_file = workflow_dir / "STATUS.md"
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
            logger.error(f"JSON 解析错误: {e}")
            return default
        except IOError as e:
            logger.error(f"文件读取错误: {e}")
            return default
        except Exception as e:
            logger.error(f"未知错误: {e}")
            return default

    def _safe_write_json(self, file_path: Path, data: dict) -> bool:
        """安全写入 JSON 文件"""
        try:
            temp_file = file_path.with_suffix('.tmp')
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            if file_path.exists():
                backup_name = f"{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                backup_path = self.backup_dir / backup_name
                shutil.copy(file_path, backup_path)

            temp_file.rename(file_path)
            return True

        except Exception as e:
            logger.error(f"文件写入错误: {e}")
            return False

    def load_status(self) -> dict:
        """加载状态"""
        with FileLock(self.lock_file):
            return self._safe_read_json(self.status_file, {})

    def save_status(self, status: dict) -> bool:
        """保存状态"""
        status["last_update"] = datetime.now().isoformat()
        with FileLock(self.lock_file):
            return self._safe_write_json(self.status_file, status)

    def update_progress(
        self,
        completed: int,
        total: int,
        current_task: str = None
    ) -> bool:
        """更新进度"""
        status = self.load_status()
        status["stats"] = {
            "total": total,
            "completed": completed,
            "pending": total - completed
        }
        if current_task:
            status["current_task"] = current_task
        return self.save_status(status)

    def record_session(self, summary: str, completed_tasks: List[str] = None) -> bool:
        """记录会话"""
        sessions_dir = self.workflow_dir / "sessions"
        sessions_dir.mkdir(exist_ok=True)

        try:
            # 计算会话编号
            existing = list(sessions_dir.glob("session-*.md"))
            num = len(existing) + 1

            # 写入会话记录
            session_file = sessions_dir / f"session-{num:03d}.md"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

            content = f"""# 会话 {num:03d}

**时间**: {timestamp}

## 完成内容

{summary}

"""

            if completed_tasks:
                content += "## 完成的任务\n\n"
                for task in completed_tasks:
                    content += f"- {task}\n"
                content += "\n"

            content += "---\n"

            with open(session_file, "w", encoding="utf-8") as f:
                f.write(content)

            # 更新状态中的会话计数
            status = self.load_status()
            status["sessions_count"] = status.get("sessions_count", 0) + 1
            self.save_status(status)

            logger.info(f"会话记录已保存: session-{num:03d}")
            return True

        except Exception as e:
            logger.error(f"记录会话失败: {e}")
            return False

    def update_status_md(self, project_name: str, stats: dict,
                         current_task: dict = None, next_tasks: List[str] = None) -> bool:
        """更新 STATUS.md 文件"""
        try:
            content = f"""# 工作流状态

## 项目信息
- **项目名称**: {project_name}
- **最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 当前进度
- **总任务**: {stats.get('total', 0)}
- **已完成**: {stats.get('completed', 0)}
- **进行中**: {stats.get('in_progress', 0)}
- **待处理**: {stats.get('pending', 0)}
- **已阻塞**: {stats.get('blocked', 0)}
- **已失败**: {stats.get('failed', 0)}

"""

            if current_task:
                content += f"""## 当前任务
- **ID**: {current_task.get('id', 'N/A')}
- **标题**: {current_task.get('title', 'N/A')}
- **状态**: {current_task.get('status', 'N/A')}

"""

            if next_tasks:
                content += "## 下一步任务\n"
                for i, task in enumerate(next_tasks, 1):
                    content += f"{i}. {task}\n"
                content += "\n"

            progress = 0
            if stats.get('total', 0) > 0:
                progress = stats['completed'] / stats['total'] * 100
            bar_len = int(progress / 5)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            content += f"## 完成度\n\n[{bar}] {progress:.1f}%\n"

            with open(self.status_md_file, "w", encoding="utf-8") as f:
                f.write(content)

            return True

        except Exception as e:
            logger.error(f"更新 STATUS.md 失败: {e}")
            return False

    def print_summary(self) -> None:
        """打印进度摘要"""
        status = self.load_status()

        print("\n" + "=" * 50)
        print("  项目状态")
        print("=" * 50)

        if "project_name" in status:
            print(f"\n项目: {status['project_name']}")

        stats = status.get("stats", {})
        if stats:
            print(f"\n进度:")
            print(f"  - 总任务: {stats.get('total', 0)}")
            print(f"  - 已完成: {stats.get('completed', 0)}")
            print(f"  - 进行中: {stats.get('in_progress', 0)}")
            print(f"  - 待处理: {stats.get('pending', 0)}")
            print(f"  - 已阻塞: {stats.get('blocked', 0)}")
            print(f"  - 已失败: {stats.get('failed', 0)}")

            if stats.get('total', 0) > 0:
                pct = stats['completed'] / stats['total'] * 100
                print(f"  - 完成率: {pct:.1f}%")

        current = status.get("current_task")
        if current:
            print(f"\n当前任务: {current.get('title', 'N/A')} [{current.get('id', '?')}]")

        print(f"\n最后更新: {status.get('last_update', 'N/A')}")
        print(f"会话次数: {status.get('sessions_count', 0)}")
        print("=" * 50)
