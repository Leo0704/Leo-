#!/usr/bin/env python3
"""
工具：初始化工作流
==================

为新项目创建工作流状态文件。
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def init_workflow(project_dir: Path, project_name: str, tasks: list = None):
    """初始化工作流状态文件"""

    workflow_dir = project_dir / ".workflow"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    (workflow_dir / "sessions").mkdir(exist_ok=True)

    now = datetime.now().isoformat()

    # 创建 STATUS.md
    status_md = f"""# 工作流状态

## 项目信息
- **项目名称**: {project_name}
- **创建时间**: {now[:10]}
- **最后更新**: {now[:19]}

## 当前进度
- **总任务**: {len(tasks) if tasks else 0}
- **已完成**: 0
- **进行中**: 无
- **待处理**: {len(tasks) if tasks else 0}

## 当前任务
- 无

## 下一步任务
{(chr(10).join([f'{i+1}. {t}' for i, t in enumerate(tasks[:5])]) if tasks else '- 暂无任务，请添加任务')}

## 技术栈
- 待确定

## 注意事项
- 此工作流不需要 API Key，直接在 Claude Code 中使用
- 每次会话开始说"继续开发"即可
"""

    with open(workflow_dir / "STATUS.md", "w", encoding="utf-8") as f:
        f.write(status_md)

    # 创建 status.json
    status_json = {
        "project_name": project_name,
        "created": now,
        "last_update": now,
        "stats": {
            "total_tasks": len(tasks) if tasks else 0,
            "completed": 0,
            "in_progress": 0,
            "pending": len(tasks) if tasks else 0
        },
        "current_task": None,
        "next_tasks": [],
        "sessions_count": 0
    }

    with open(workflow_dir / "status.json", "w", encoding="utf-8") as f:
        json.dump(status_json, f, indent=2, ensure_ascii=False)

    # 创建 tasks.json
    tasks_json = {
        "tasks": []
    }

    if tasks:
        for i, task_title in enumerate(tasks):
            tasks_json["tasks"].append({
                "id": f"task-{i+1:03d}",
                "title": task_title,
                "status": "pending",
                "priority": i + 1
            })

    with open(workflow_dir / "tasks.json", "w", encoding="utf-8") as f:
        json.dump(tasks_json, f, indent=2, ensure_ascii=False)

    # 创建 decisions.md
    with open(workflow_dir / "decisions.md", "w", encoding="utf-8") as f:
        f.write(f"# 技术决策记录\n\n")
        f.write(f"创建于 {now[:10]}\n\n")
        f.write("---\n\n")

    print(f"工作流初始化完成!")
    print(f"位置: {workflow_dir}")
    print(f"\n下一步:")
    print(f"  1. 编辑 {workflow_dir}/STATUS.md 添加项目信息")
    print(f"  2. 在 Claude Code 中说 '继续开发' 开始工作")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="初始化工作流")
    parser.add_argument("project_dir", type=Path, help="项目目录")
    parser.add_argument("--name", default="我的项目", help="项目名称")
    parser.add_argument("--tasks", nargs="+", help="初始任务列表")

    args = parser.parse_args()

    init_workflow(args.project_dir, args.name, args.tasks)


if __name__ == "__main__":
    main()
