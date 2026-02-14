#!/usr/bin/env python3
"""
工具：初始化工作流
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def init_workflow(project_dir: Path, project_name: str, tasks: list = None):
    """初始化工作流状态文件"""

    workflow_dir = project_dir / ".workflow"
    workflow_dir.mkdir(parents=True, exist_ok=True)

    # 创建 GOAL.md
    goal_md = """# 项目理想状态

## 产品愿景
[用一句话描述你的产品是什么，解决什么问题]

## 成功标准
- [ ] [功能 1：具体描述]
- [ ] [功能 2：具体描述]
- [ ] [功能 3：具体描述]

## 验收条件
当我作为用户使用这个产品时：
1. [场景 1：应该发生什么]
2. [场景 2：应该发生什么]
"""
    (workflow_dir / "GOAL.md").write_text(goal_md, encoding="utf-8")

    # 创建 REALITY.md
    reality_md = f"""# 当前状态

## 已实现
（刚开始，暂无）

## 待改进
{chr(10).join([f'- {t}' for t in (tasks or ['核心功能'])]) }

## 距离理想状态
0% - 项目初始化

## 最后更新
{datetime.now().strftime('%Y-%m-%d')}
"""
    (workflow_dir / "REALITY.md").write_text(reality_md, encoding="utf-8")

    # 创建 tasks.json
    task_list = []
    if tasks:
        for i, title in enumerate(tasks):
            task_list.append({
                "id": f"task-{i+1:03d}",
                "title": title,
                "status": "pending",
                "priority": i + 1
            })

    (workflow_dir / "tasks.json").write_text(
        json.dumps({"tasks": task_list}, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"工作流初始化完成: {workflow_dir}")
    print(f"\n下一步:")
    print(f"  1. 编辑 {workflow_dir}/GOAL.md 描述理想状态")
    print(f"  2. 在 Claude Code 中说 '继续开发'")


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
