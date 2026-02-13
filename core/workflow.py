#!/usr/bin/env python3
"""
无限开发工作流 - 核心引擎
==========================

实现双代理模式的自主开发工作流，支持跨会话持续开发。
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.agent import run_autonomous_agent
from core.config import Config


def check_prerequisites():
    """检查运行前提条件"""
    # 检查 API Key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("错误: 未设置 ANTHROPIC_API_KEY 环境变量")
        print("\n获取 API Key: https://console.anthropic.com/")
        print("设置方法:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        return False
    return True


def create_initial_progress(project_dir: Path):
    """创建初始进度文件"""
    progress_file = project_dir / "progress.json"
    if not progress_file.exists():
        initial_progress = {
            "total_features": 0,
            "completed": 0,
            "in_progress": None,
            "last_session": datetime.now().isoformat(),
            "sessions_count": 0,
            "next_actions": [],
            "issues": [],
            "decisions": []
        }
        with open(progress_file, "w", encoding="utf-8") as f:
            json.dump(initial_progress, f, indent=2, ensure_ascii=False)


def print_banner(config: Config):
    """打印启动横幅"""
    print("\n" + "=" * 70)
    print("  无限开发工作流 (Infinite Development Workflow)")
    print("=" * 70)
    print(f"\n项目目录: {config.project_dir}")
    print(f"模型: {config.model}")
    print(f"最大迭代: {'无限制' if config.max_iterations is None else config.max_iterations}")
    print(f"会话延迟: {config.session_delay}秒")
    print()


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="无限开发工作流 - AI 自主开发框架",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 启动新项目
  python core/workflow.py --project-dir ./my_app

  # 限制迭代次数（测试用）
  python core/workflow.py --project-dir ./my_app --max-iterations 5

  # 使用特定模型
  python core/workflow.py --project-dir ./my_app --model claude-sonnet-4-5-20250929

环境变量:
  ANTHROPIC_API_KEY    Anthropic API 密钥（必需）
        """
    )

    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path("./generations/default_project"),
        help="项目目录（默认: ./generations/default_project）"
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="最大迭代次数（默认: 无限制）"
    )

    parser.add_argument(
        "--model",
        type=str,
        default="claude-sonnet-4-5-20250929",
        help="使用的 Claude 模型"
    )

    parser.add_argument(
        "--session-delay",
        type=int,
        default=3,
        help="会话间隔秒数（默认: 3）"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只显示配置，不实际运行"
    )

    args = parser.parse_args()

    # 检查前提条件
    if not check_prerequisites():
        sys.exit(1)

    # 创建配置
    config = Config(
        project_dir=args.project_dir,
        model=args.model,
        max_iterations=args.max_iterations,
        session_delay=args.session_delay
    )

    # 显示横幅
    print_banner(config)

    if args.dry_run:
        print("[DRY RUN] 配置已加载，但不执行")
        return

    # 确保项目目录存在
    config.project_dir.mkdir(parents=True, exist_ok=True)

    # 创建初始进度文件
    create_initial_progress(config.project_dir)

    # 运行工作流
    try:
        asyncio.run(run_autonomous_agent(config))
    except KeyboardInterrupt:
        print("\n\n用户中断")
        print("要继续，请运行相同的命令")
    except Exception as e:
        print(f"\n致命错误: {e}")
        raise


if __name__ == "__main__":
    main()
