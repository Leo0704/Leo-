#!/usr/bin/env python3
"""
自动修复脚本 - 自动修复常见的代码问题
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None):
    """运行命令"""
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def fix_python():
    """修复 Python 代码"""
    print("检查 Python 代码...")

    # 运行 ruff
    code, out, err = run_command("ruff check . --fix")
    if code == 0:
        print("✓ Ruff 检查通过")

    # 运行 isort
    code, out, err = run_command("ruff check . --select I --fix")
    if code == 0:
        print("✓ Import 排序完成")


def fix_javascript():
    """修复 JavaScript 代码"""
    print("检查 JavaScript 代码...")

    # 运行 prettier
    code, out, err = run_command("npx prettier --write .")
    if code == 0:
        print("✓ Prettier 格式化完成")


def main():
    project_dir = Path(".")

    if not project_dir.exists():
        print(f"错误: 目录 {project_dir} 不存在")
        sys.exit(1)

    # 检测项目类型
    if (project_dir / "pyproject.toml").exists():
        fix_python()
    elif (project_dir / "package.json").exists():
        fix_javascript()
    else:
        print("未知项目类型")

    print("修复完成!")


if __name__ == "__main__":
    main()
