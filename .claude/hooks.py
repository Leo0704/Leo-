#!/usr/bin/env python3
"""
SessionStart Hook - 自动显示工作流状态

读取 tasks.json 和 REALITY.md，显示当前进度。
"""

import json
import re
import sys
from pathlib import Path


def main():
    workflow_dir = Path.cwd() / ".workflow"

    if not workflow_dir.exists():
        sys.exit(0)

    # 从 tasks.json 读取进度
    tasks_file = workflow_dir / "tasks.json"
    if tasks_file.exists():
        try:
            data = json.loads(tasks_file.read_text(encoding="utf-8"))
            tasks = data.get("tasks", [])
            total = len(tasks)
            completed = sum(1 for t in tasks if t.get("status") == "completed")
            progress = int(completed / total * 100) if total > 0 else 0
        except Exception:
            total, completed, progress = 0, 0, 0
    else:
        total, completed, progress = 0, 0, 0

    # 从 REALITY.md 读取待改进项
    pending = []
    reality_file = workflow_dir / "REALITY.md"
    if reality_file.exists():
        in_section = False
        for line in reality_file.read_text(encoding="utf-8").split("\n"):
            if "待改进" in line or "TODO" in line.lower():
                in_section = True
                continue
            if in_section and line.strip().startswith("-"):
                pending.append(line.strip("- ").strip())
            elif in_section and line.strip() == "":
                break

    # 找到下一个任务
    next_task = None
    if tasks_file.exists():
        try:
            data = json.loads(tasks_file.read_text(encoding="utf-8"))
            for t in data.get("tasks", []):
                if t.get("status") == "in_progress":
                    next_task = t
                    break
            if not next_task:
                completed_ids = {t["id"] for t in data.get("tasks", []) if t.get("status") == "completed"}
                for t in data.get("tasks", []):
                    if t.get("status") == "pending":
                        deps = t.get("dependencies", [])
                        if all(d in completed_ids for d in deps):
                            next_task = t
                            break
        except Exception:
            pass

    print()
    print("=" * 50)
    print("  目标驱动工作流")
    print("=" * 50)
    print(f"\n  任务: {completed}/{total} ({progress}%)")

    if next_task:
        print(f"  当前: [{next_task['id']}] {next_task['title']}")
        criteria = next_task.get("acceptance_criteria", [])
        if criteria:
            passed = sum(1 for c in criteria if c.get("passed"))
            print(f"  验收: {passed}/{len(criteria)}")

    if pending:
        print(f"\n  待改进:")
        for i, item in enumerate(pending[:3], 1):
            print(f"    {i}. {item}")

    print("\n" + "=" * 50)
    print()
    sys.exit(0)


if __name__ == "__main__":
    main()
