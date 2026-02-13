#!/usr/bin/env python3
"""
工具：查看进度
==============

查看项目的当前开发进度。
"""

import argparse
import json
from pathlib import Path


def view_progress(project_dir: Path):
    """显示项目进度"""
    feature_file = project_dir / "feature_list.json"
    progress_file = project_dir / "progress.json"

    print(f"\n项目目录: {project_dir}")
    print("=" * 50)

    # 检查 feature_list.json
    if not feature_file.exists():
        print("\n[!] feature_list.json 不存在")
        print("    项目可能尚未初始化")
        return

    # 读取功能列表
    with open(feature_file, "r", encoding="utf-8") as f:
        features = json.load(f)

    # 统计
    total = len(features)
    by_status = {}
    by_category = {}

    for feature in features:
        status = feature.get("status", "pending")
        category = feature.get("category", "unknown")

        by_status[status] = by_status.get(status, 0) + 1
        by_category[category] = by_category.get(category, 0) + 1

    # 显示统计
    print(f"\n功能统计:")
    print(f"  总计: {total}")

    if by_status:
        print(f"\n  按状态:")
        for status, count in sorted(by_status.items()):
            percentage = (count / total * 100) if total > 0 else 0
            bar = "█" * int(percentage / 5) + "░" * (20 - int(percentage / 5))
            print(f"    {status:12} {count:4} ({percentage:5.1f}%) {bar}")

    if by_category:
        print(f"\n  按类别:")
        for category, count in sorted(by_category.items(), key=lambda x: -x[1]):
            print(f"    {category:12} {count:4}")

    # 显示进度文件
    if progress_file.exists():
        with open(progress_file, "r", encoding="utf-8") as f:
            progress = json.load(f)

        print(f"\n进度信息:")
        if progress.get("last_session"):
            print(f"  最后会话: {progress['last_session']}")
        if progress.get("in_progress"):
            print(f"  进行中: {progress['in_progress']}")
        if progress.get("next_actions"):
            print(f"\n  下一步:")
            for action in progress["next_actions"][:5]:
                print(f"    - {action}")

    # 显示待处理功能
    pending = [f for f in features if f.get("status") == "pending"]
    if pending:
        pending_sorted = sorted(pending, key=lambda x: x.get("priority", 999))
        print(f"\n待处理功能 (前 5 个):")
        for feature in pending_sorted[:5]:
            print(f"  [{feature.get('id', '?')}] {feature.get('description', 'N/A')}")

    # 显示最近完成
    completed = [f for f in features if f.get("status") == "completed"]
    if completed:
        print(f"\n已完成功能 (最近 5 个):")
        # 注意：这里没有时间信息，只显示列表
        for feature in completed[-5:]:
            print(f"  [{feature.get('id', '?')}] {feature.get('description', 'N/A')}")

    # 完成度
    if total > 0:
        completed_count = by_status.get("completed", 0)
        percentage = completed_count / total * 100
        print(f"\n完成度: {percentage:.1f}%")
        print(f"{'█' * int(percentage / 2)}{'░' * (50 - int(percentage / 2))}")


def main():
    parser = argparse.ArgumentParser(description="查看无限开发工作流项目进度")
    parser.add_argument(
        "project_dir",
        type=Path,
        nargs="?",
        default=Path("./generations/default_project"),
        help="项目目录"
    )

    args = parser.parse_args()
    view_progress(args.project_dir)


if __name__ == "__main__":
    main()
