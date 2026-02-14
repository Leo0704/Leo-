#!/usr/bin/env python3
"""
工具：查看进度
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.tasks import TaskManager


def view_progress(project_dir: Path):
    """显示项目进度"""
    workflow_dir = project_dir / ".workflow"

    if not workflow_dir.exists():
        print(f"\n工作流目录不存在: {workflow_dir}")
        print("请先初始化工作流")
        return

    task_manager = TaskManager(workflow_dir)
    task_manager.print_summary()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="查看工作流进度")
    parser.add_argument(
        "project_dir", type=Path, nargs="?", default=Path("."),
        help="项���目录（默认: 当前目录）"
    )
    args = parser.parse_args()
    view_progress(args.project_dir)


if __name__ == "__main__":
    main()
