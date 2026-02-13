"""
进度追踪器
==========

追踪和显示工作流进度。
"""

import json
from datetime import datetime
from pathlib import Path


class ProgressTracker:
    """进度追踪器"""

    def __init__(self, workflow_dir: Path):
        self.workflow_dir = workflow_dir
        self.status_file = workflow_dir / "status.json"
        self.status_md_file = workflow_dir / "STATUS.md"

    def load_status(self) -> dict:
        """加载状态"""
        if not self.status_file.exists():
            return {}
        with open(self.status_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_status(self, status: dict) -> None:
        """保存状态"""
        status["last_update"] = datetime.now().isoformat()
        with open(self.status_file, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=2, ensure_ascii=False)

    def update_progress(self, completed: int, total: int, current_task: str = None) -> None:
        """更新进度"""
        status = self.load_status()
        status["stats"] = {
            "total": total,
            "completed": completed,
            "pending": total - completed
        }
        if current_task:
            status["current_task"] = current_task
        self.save_status(status)

    def record_session(self, summary: str, completed_tasks: list = None) -> None:
        """记录会话"""
        sessions_dir = self.workflow_dir / "sessions"
        sessions_dir.mkdir(exist_ok=True)

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
            print(f"  - 待处理: {stats.get('pending', 0)}")

            if stats.get('total', 0) > 0:
                pct = stats['completed'] / stats['total'] * 100
                print(f"  - 完成率: {pct:.1f}%")

        current = status.get("current_task")
        if current:
            print(f"\n当前任务: {current}")

        print(f"\n最后更新: {status.get('last_update', 'N/A')}")
        print("=" * 50)
