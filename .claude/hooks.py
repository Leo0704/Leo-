#!/usr/bin/env python3
"""
Task Sync Hook - 原生 Task 系统集成

功能：
1. SessionStart: 读取 state.json，显示进度
2. 读取原生 Task，同步到 state.json（持久化）

设计理念：
- 任务管理交给 Claude Code 原生 Task 系统
- 验收标准由 .workflow/criteria.json 管理
- 此脚本只负责同步和显示
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


def get_current_session_tasks() -> Dict[str, Any]:
    """
    读取当前会话的原生 Task

    Returns:
        Dict: {taskID: taskData}
    """
    task_dir = Path.home() / ".claude" / "tasks"

    # 找到最新的 session 目录
    if not task_dir.exists():
        return {}

    sessions = sorted(task_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
    if not sessions:
        return {}

    latest_session = sessions[0]
    task_files = list(latest_session.glob("*.json"))

    tasks = {}
    for task_file in task_files:
        try:
            data = json.loads(task_file.read_text(encoding="utf-8"))
            task_id = data.get("id", task_file.stem)
            tasks[task_id] = data
        except Exception:
            continue

    return tasks


def load_criteria() -> Dict[str, Any]:
    """
    读取验收标准

    Returns:
        Dict: {taskID: criteriaData}
    """
    criteria_file = Path.cwd() / ".workflow" / "criteria.json"

    if not criteria_file.exists():
        return {}

    try:
        return json.loads(criteria_file.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_state() -> Dict[str, Any]:
    """
    读取持久化状态

    Returns:
        Dict: state 数据
    """
    state_file = Path.cwd() / ".workflow" / "state.json"

    if not state_file.exists():
        return {"tasks": [], "last_sync": None}

    try:
        return json.loads(state_file.read_text(encoding="utf-8"))
    except Exception:
        return {"tasks": [], "last_sync": None}


def save_state(state: Dict[str, Any]) -> None:
    """保存状态到文件"""
    state_file = Path.cwd() / ".workflow" / "state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)

    state["last_sync"] = datetime.now().isoformat()
    state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def sync_tasks() -> None:
    """
    同步原生 Task 到 state.json

    逻辑：
    1. 读取原生 Task（当前状态）
    2. 读取现有 state.json（获取历史记录）
    3. 读取验收标准（criteria.json）
    4. 合并保存到 state.json（包含历史记录）
    """
    # 导入历史记录功能
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "workflow_utils",
        Path(__file__).parent / "workflow_utils.py"
    )
    workflow_utils = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(workflow_utils)

    native_tasks = get_current_session_tasks()
    criteria = load_criteria()
    old_state = load_state()

    # 构建旧任务的映射 {task_id: task_data}
    old_tasks_map = {t["id"]: t for t in old_state.get("tasks", [])}

    # 构建合并后的状态
    state_tasks = []
    for task_id, task_data in native_tasks.items():
        current_status = task_data.get("status", "pending")

        # 检查是否是新任务或状态发生变化
        if task_id in old_tasks_map:
            old_task = old_tasks_map[task_id]
            old_status = old_task.get("status")

            # 状态未变化，保留旧的历史记录
            if old_status == current_status:
                state_task = old_task
            else:
                # 状态发生变化，添加历史记录
                note = f"状态从 {old_status} 变更为 {current_status}"
                state_task = workflow_utils.add_history_entry(
                    old_task.copy(),
                    current_status,
                    note
                )
        else:
            # 新任务，添加创建历史
            state_task = {
                "id": task_id,
                "subject": task_data.get("subject", ""),
                "description": task_data.get("description", ""),
                "status": current_status,
                "active_form": task_data.get("activeForm", ""),
                "owner": task_data.get("owner", ""),
                "blocks": task_data.get("blocks", []),
                "blocked_by": task_data.get("blockedBy", []),
                "history": [{
                    "status": current_status,
                    "timestamp": datetime.now().isoformat(),
                    "note": "任务创建"
                }]
            }

        # 更新基本信息（确保最新）
        state_task["subject"] = task_data.get("subject", state_task.get("subject", ""))
        state_task["description"] = task_data.get("description", state_task.get("description", ""))
        state_task["active_form"] = task_data.get("activeForm", state_task.get("active_form", ""))
        state_task["owner"] = task_data.get("owner", state_task.get("owner", ""))
        state_task["blocks"] = task_data.get("blocks", state_task.get("blocks", []))
        state_task["blocked_by"] = task_data.get("blockedBy", state_task.get("blocked_by", []))

        # 添加验收标准
        if task_id in criteria:
            state_task["acceptance_criteria"] = criteria[task_id].get("acceptance_criteria", [])

        state_tasks.append(state_task)

    # 按状态排序：in_progress → pending → completed
    def sort_key(task):
        status = task["status"]
        if status == "in_progress":
            return 0
        elif status == "pending":
            return 1
        else:
            return 2

    state_tasks.sort(key=sort_key)

    save_state({"tasks": state_tasks})


def show_progress() -> None:
    """显示当前进度"""
    state = load_state()
    tasks = state.get("tasks", [])

    if not tasks:
        return

    # 统计
    total = len(tasks)
    completed = sum(1 for t in tasks if t["status"] == "completed")
    in_progress = sum(1 for t in tasks if t["status"] == "in_progress")
    progress = int(completed / total * 100) if total > 0 else 0

    # 找当前任务
    current_task = None
    for task in tasks:
        if task["status"] == "in_progress":
            current_task = task
            break

    # 如果没有 in_progress，找第一个 pending
    if not current_task:
        for task in tasks:
            if task["status"] == "pending":
                current_task = task
                break

    # 显示
    print()
    print("=" * 50)
    print("  目标驱动工作流（原生 Task 集成）")
    print("=" * 50)
    print(f"\n  进度: {completed}/{total} ({progress}%)")
    print(f"  进行中: {in_progress} | 待办: {total - completed - in_progress}")

    if current_task:
        print(f"\n  当前任务:")
        print(f"    [{current_task['id']}] {current_task['subject']}")

        # 显示验收标准进度
        if "acceptance_criteria" in current_task:
            criteria = current_task["acceptance_criteria"]
            passed = sum(1 for c in criteria if c.get("passed", False))
            total_criteria = len(criteria)
            if total_criteria > 0:
                print(f"    验收: {passed}/{total_criteria} 通过")

        # 显示阻塞关系
        if current_task.get("blocked_by"):
            blocked_by = current_task["blocked_by"]
            print(f"    等待: {', '.join(blocked_by)}")

        if current_task.get("blocks"):
            blocks = current_task["blocks"]
            print(f"    阻塞: {', '.join(blocks)}")

    # 显示待改进项（从 REALITY.md）
    reality_file = Path.cwd() / ".workflow" / "REALITY.md"
    if reality_file.exists():
        pending = []
        in_section = False
        for line in reality_file.read_text(encoding="utf-8").split("\n"):
            if "待改进" in line or "TODO" in line.lower():
                in_section = True
                continue
            if in_section and line.strip().startswith("-"):
                pending.append(line.strip("- ").strip())
            elif in_section and line.strip() == "":
                break

        if pending:
            print(f"\n  待改进:")
            for i, item in enumerate(pending[:3], 1):
                print(f"    {i}. {item}")

    print("\n" + "=" * 50)
    print()


def main():
    """主函数"""
    workflow_dir = Path.cwd() / ".workflow"

    # 检查是否在工作流项目中
    if not workflow_dir.exists():
        sys.exit(0)

    # 显示进度
    show_progress()

    # 同步原生任务到文件
    sync_tasks()

    sys.exit(0)


if __name__ == "__main__":
    main()
