#!/usr/bin/env python3
"""
工具：查看进度
==============

查看项目的当前开发进度。
"""

import json
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.tasks import TaskManager
from core.progress import ProgressTracker


def view_progress(project_dir: Path):
    """显示项目进度"""

    workflow_dir = project_dir / ".workflow"

    if not workflow_dir.exists():
        print(f"\n[!] 工作流目录不存在: {workflow_dir}")
        print("    请先初始化工作流")
        return

    # 使用任务管理器
    task_manager = TaskManager(workflow_dir)
    task_manager.print_summary()

    # 显示状态文件内容
    status_file = workflow_dir / "STATUS.md"
    if status_file.exists():
        print("\n" + "=" * 50)
        print("  STATUS.md 内容")
        print("=" * 50)
        with open(status_file, "r", encoding="utf-8") as f:
            print(f.read())


def main():
    import argparse

    parser = argparse.ArgumentParser(description="查看无限开发工作流进度")
    parser.add_argument(
        "project_dir",
        type=Path,
        nargs="?",
        default=Path("."),
        help="项目目录（默认: 当前目录）"
    )

    args = parser.parse_args()
    view_progress(args.project_dir)


if __name__ == "__main__":
    main()
