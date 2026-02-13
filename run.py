#!/usr/bin/env python3
"""
无限开发工作流 - 主入口
======================

快速启动无限开发工作流。
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="无限开发工作流 - AI 自主开发框架",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --project-dir ./my_app
  %(prog)s --project-dir ./my_app --max-iterations 5
  %(prog)s new my_new_app
  %(prog)s progress ./my_app

环境变量:
  ANTHROPIC_API_KEY    Anthropic API 密钥（必需）

更多信息请查看 README.md
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 运行命令
    run_parser = subparsers.add_parser("run", help="运行工作流")
    run_parser.add_argument("--project-dir", type=Path, default=Path("./generations/default_project"))
    run_parser.add_argument("--max-iterations", type=int, default=None)
    run_parser.add_argument("--model", type=str, default="claude-sonnet-4-5-20250929")
    run_parser.add_argument("--session-delay", type=int, default=3)

    # 新建命令
    new_parser = subparsers.add_parser("new", help="创建新项目")
    new_parser.add_argument("name", help="项目名称")
    new_parser.add_argument("--output-dir", type=Path, default=Path("./generations"))
    new_parser.add_argument("--spec", type=Path, help="应用规格文件")

    # 进度命令
    progress_parser = subparsers.add_parser("progress", help="查看进度")
    progress_parser.add_argument("project_dir", type=Path, nargs="?", default=Path("./generations/default_project"))

    # 默认参数（无子命令时）
    parser.add_argument("--project-dir", type=Path, default=None)
    parser.add_argument("--max-iterations", type=int, default=None)
    parser.add_argument("--model", type=str, default=None)
    parser.add_argument("--session-delay", type=int, default=None)

    args = parser.parse_args()

    # 检查 API Key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("提示: 未设置 ANTHROPIC_API_KEY 环境变量")
        print("      某些功能可能需要 API Key")
        print()

    # 处理命令
    if args.command == "new":
        from tools.new_project import create_new_project
        create_new_project(args.name, args.output_dir, args.spec)

    elif args.command == "progress":
        from tools.view_progress import view_progress
        view_progress(args.project_dir)

    elif args.command == "run":
        from core.workflow import main as run_main
        # 设置 sys.argv 以便 run_main 可以解析参数
        sys.argv = [
            "workflow.py",
            "--project-dir", str(args.project_dir),
            "--model", args.model,
            "--session-delay", str(args.session_delay),
        ]
        if args.max_iterations:
            sys.argv.extend(["--max-iterations", str(args.max_iterations)])
        run_main()

    else:
        # 默认行为：如果提供了 --project-dir，运行工作流
        if args.project_dir:
            from core.workflow import main as run_main
            sys.argv = [
                "workflow.py",
                "--project-dir", str(args.project_dir),
            ]
            if args.max_iterations:
                sys.argv.extend(["--max-iterations", str(args.max_iterations)])
            if args.model:
                sys.argv.extend(["--model", args.model])
            if args.session_delay:
                sys.argv.extend(["--session-delay", str(args.session_delay)])
            run_main()
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
