#!/usr/bin/env python3
"""
SessionStart Hook - 自动目标驱动工作流

当会话开始时：
1. 检查是否存在 .workflow 目录
2. 读取 GOAL.md（理想状态）和 REALITY.md（当前状态）
3. 如果未达到理想状态，输出继续开发的指令
"""

import sys
from pathlib import Path


def get_workflow_status():
    """获取工作流状态"""
    workflow_dir = Path.cwd() / ".workflow"

    if not workflow_dir.exists():
        return None, None, None

    goal_file = workflow_dir / "GOAL.md"
    reality_file = workflow_dir / "REALITY.md"

    if not goal_file.exists():
        return None, None, None

    goal = goal_file.read_text(encoding="utf-8") if goal_file.exists() else ""
    reality = reality_file.read_text(encoding="utf-8") if reality_file.exists() else "项目初始化"

    # 计算进度
    progress = 0
    for line in reality.split("\n"):
        if "%" in line and any(c.isdigit() for c in line):
            # 提取百分比
            import re
            match = re.search(r'(\d+)%', line)
            if match:
                progress = int(match.group(1))
                break

    return goal, reality, progress


def extract_pending_items(reality: str) -> list:
    """从 REALITY.md 提取待改进项"""
    items = []
    in_section = False
    for line in reality.split("\n"):
        if "待改进" in line or "TODO" in line.lower():
            in_section = True
            continue
        if in_section and line.strip().startswith("-"):
            items.append(line.strip("- ").strip())
        elif in_section and line.strip() == "":
            break
    return items


def main():
    goal, reality, progress = get_workflow_status()

    if not goal:
        # 没有工作流，静默退出
        sys.exit(0)

    # 提取待改进项
    pending = extract_pending_items(reality)

    # 输出状态提示
    print()
    print("=" * 50)
    print("  🎯 目标驱动工作流 - 自动触发")
    print("=" * 50)
    print(f"\n  📊 当前进度: {progress}%")
    print(f"  📋 待改进: {len(pending)} 项")

    if pending:
        print("\n  📌 下一步建议:")
        for i, item in enumerate(pending[:3], 1):
            # 清理 emoji 和格式
            clean_item = item.replace("🔄", "").replace("❌", "").strip()
            print(f"     {i}. {clean_item}")

    print("\n" + "=" * 50)
    print("  💡 提示: 说 '继续' 或 '继续开发' 开始工作")
    print("=" * 50)
    print()

    sys.exit(0)


if __name__ == "__main__":
    main()
