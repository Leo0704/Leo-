#!/usr/bin/env python3
"""
生成变更日志
"""

import json
from pathlib import Path
from datetime import datetime, timedelta


def get_git_log(days=30):
    """获取 Git 提交历史"""
    import subprocess

    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    result = subprocess.run(
        ["git", "log", f"--since={since}", "--pretty=format:%s|%an|%ar"],
        capture_output=True,
        text=True,
    )

    commits = []
    for line in result.stdout.strip().split("\n"):
        if line:
            parts = line.split("|")
            if len(parts) >= 3:
                commits.append(
                    {"message": parts[0], "author": parts[1], "date": parts[2]}
                )

    return commits


def categorize_commits(commits):
    """分类提交"""
    categories = {
        "feat": [],
        "fix": [],
        "docs": [],
        "refactor": [],
        "test": [],
        "chore": [],
    }

    for commit in commits:
        msg = commit["message"].lower()
        if msg.startswith("feat"):
            categories["feat"].append(commit)
        elif msg.startswith("fix"):
            categories["fix"].append(commit)
        elif msg.startswith("docs"):
            categories["docs"].append(commit)
        elif msg.startswith("refactor"):
            categories["refactor"].append(commit)
        elif msg.startswith("test"):
            categories["test"].append(commit)
        else:
            categories["chore"].append(commit)

    return categories


def generate_changelog(categories):
    """生成变更日志"""
    changelog = "# 变更日志\n\n"

    if categories["feat"]:
        changelog += "## 新功能\n\n"
        for commit in categories["feat"]:
            changelog += f"- {commit['message']} ({commit['date']})\n"
        changelog += "\n"

    if categories["fix"]:
        changelog += "## Bug 修复\n\n"
        for commit in categories["fix"]:
            changelog += f"- {commit['message']} ({commit['date']})\n"
        changelog += "\n"

    if categories["docs"]:
        changelog += "## 文档\n\n"
        for commit in categories["docs"]:
            changelog += f"- {commit['message']} ({commit['date']})\n"
        changelog += "\n"

    return changelog


def main():
    commits = get_git_log()
    categories = categorize_commits(commits)
    changelog = generate_changelog(categories)

    print(changelog)

    # 保存到文件
    with open("CHANGELOG.md", "w", encoding="utf-8") as f:
        f.write(changelog)

    print("\n已保存到 CHANGELOG.md")


if __name__ == "__main__":
    main()
