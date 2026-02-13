#!/usr/bin/env python3
"""
工具：创建新项目
================

快速创建一个新的无限开发工作流项目。
"""

import argparse
import shutil
from pathlib import Path


def create_new_project(name: str, output_dir: Path, spec_file: Path = None):
    """创建新项目目录结构"""

    project_dir = output_dir / name
    project_dir.mkdir(parents=True, exist_ok=True)

    # 创建目录结构
    (project_dir / "frontend").mkdir(exist_ok=True)
    (project_dir / "backend").mkdir(exist_ok=True)

    # 复制模板文件
    templates_dir = Path(__file__).parent.parent / "templates"

    if templates_dir.exists():
        # 复制 init.sh
        init_src = templates_dir / "init.sh"
        if init_src.exists():
            shutil.copy(init_src, project_dir / "init.sh")
            print(f"  创建: init.sh")

        # 复制 README.md
        readme_src = templates_dir / "README.md"
        if readme_src.exists():
            shutil.copy(readme_src, project_dir / "README.md")
            print(f"  创建: README.md")

    # 复制或创建 app_spec.txt
    if spec_file and spec_file.exists():
        shutil.copy(spec_file, project_dir / "app_spec.txt")
        print(f"  创建: app_spec.txt (从 {spec_file})")
    else:
        prompts_dir = Path(__file__).parent.parent / "prompts"
        spec_src = prompts_dir / "app_spec.txt"
        if spec_src.exists():
            shutil.copy(spec_src, project_dir / "app_spec.txt")
            print(f"  创建: app_spec.txt (使用默认模板)")

    # 创建空的 feature_list.json
    feature_list = []
    import json
    with open(project_dir / "feature_list.json", "w") as f:
        json.dump(feature_list, f, indent=2)
    print(f"  创建: feature_list.json")

    # 创建 progress.json
    progress = {
        "total_features": 0,
        "completed": 0,
        "in_progress": None,
        "last_session": None,
        "sessions_count": 0,
        "next_actions": [],
        "issues": [],
        "decisions": []
    }
    with open(project_dir / "progress.json", "w") as f:
        json.dump(progress, f, indent=2)
    print(f"  创建: progress.json")

    # 创建 session_notes.md
    with open(project_dir / "session_notes.md", "w") as f:
        f.write(f"# 会话笔记 - {name}\n\n")
        f.write("此文件记录每个开发会话的进度和决策。\n\n")
        f.write("---\n")
    print(f"  创建: session_notes.md")

    print(f"\n项目 '{name}' 创建成功!")
    print(f"位置: {project_dir}")
    print(f"\n下一步:")
    print(f"  1. 编辑 {project_dir}/app_spec.txt 描述你的项目")
    print(f"  2. 运行: python core/workflow.py --project-dir {project_dir}")


def main():
    parser = argparse.ArgumentParser(description="创建新的无限开发工作流项目")
    parser.add_argument("name", help="项目名称")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./generations"),
        help="输出目录（默认: ./generations）"
    )
    parser.add_argument(
        "--spec",
        type=Path,
        help="应用规格文件路径"
    )

    args = parser.parse_args()

    print(f"\n创建项目: {args.name}")
    print(f"输出目录: {args.output_dir}")
    print()

    create_new_project(args.name, args.output_dir, args.spec)


if __name__ == "__main__":
    main()
