"""
代理会话逻辑
============

核心代理交互函数，运行自主开发会话。
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from core.config import Config
from core.progress import ProgressTracker
from core.prompts import get_initializer_prompt, get_coding_prompt


async def run_agent_session(
    client,
    message: str,
    config: Config
) -> tuple[str, str]:
    """
    运行单个代理会话。

    Args:
        client: Claude SDK 客户端
        message: 要发送的提示
        config: 工作流配置

    Returns:
        (status, response_text) 其中 status 为:
        - "continue": 代理应继续工作
        - "error": 发生错误
        - "complete": 所有任务完成
    """
    print("发送提示到 Claude...\n")

    try:
        # 发送查询
        await client.query(message)

        # 收集响应
        response_text = ""
        async for msg in client.receive_response():
            msg_type = type(msg).__name__

            # 处理 AssistantMessage
            if msg_type == "AssistantMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    block_type = type(block).__name__

                    if block_type == "TextBlock" and hasattr(block, "text"):
                        response_text += block.text
                        print(block.text, end="", flush=True)

                    elif block_type == "ToolUseBlock" and hasattr(block, "name"):
                        print(f"\n[工具: {block.name}]", flush=True)
                        if hasattr(block, "input"):
                            input_str = str(block.input)
                            if len(input_str) > 200:
                                print(f"   输入: {input_str[:200]}...", flush=True)
                            else:
                                print(f"   输入: {input_str}", flush=True)

            # 处理 UserMessage（工具结果）
            elif msg_type == "UserMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    block_type = type(block).__name__

                    if block_type == "ToolResultBlock":
                        result_content = getattr(block, "content", "")
                        is_error = getattr(block, "is_error", False)

                        if "blocked" in str(result_content).lower():
                            print(f"   [已阻止] {result_content}", flush=True)
                        elif is_error:
                            error_str = str(result_content)[:500]
                            print(f"   [错误] {error_str}", flush=True)
                        else:
                            print("   [完成]", flush=True)

        print("\n" + "-" * 70 + "\n")

        # 检查是否所有任务完成
        tracker = ProgressTracker(config.project_dir)
        if tracker.is_complete():
            return "complete", response_text

        return "continue", response_text

    except Exception as e:
        print(f"会话错误: {e}")
        return "error", str(e)


async def run_autonomous_agent(config: Config) -> None:
    """
    运行自主代理循环。

    Args:
        config: 工作流配置
    """
    # 检查是新开始还是继续
    is_first_run = not config.feature_list_path.exists()

    if is_first_run:
        print("全新开始 - 将使用初始化代理")
        print()
        print("=" * 70)
        print("  注意: 首次会话可能需要较长时间!")
        print("  代理正在生成详细的任务清单和测试用例。")
        print("  这可能看起来像卡住了 - 但它正在工作。")
        print("=" * 70)
        print()

        # 复制 app_spec.txt 到项目目录
        source_spec = config.prompts_dir / "app_spec.txt"
        if source_spec.exists():
            import shutil
            shutil.copy(source_spec, config.app_spec_path)
            print(f"已复制规格文件到: {config.app_spec_path}")
    else:
        print("继续现有项目")
        tracker = ProgressTracker(config.project_dir)
        tracker.print_summary()

    # 主循环
    iteration = 0

    while True:
        iteration += 1

        # 检查最大迭代
        if config.max_iterations and iteration > config.max_iterations:
            print(f"\n达到最大迭代次数 ({config.max_iterations})")
            print("要继续，请运行脚本时不带 --max-iterations 参数")
            break

        # 打印会话头
        print_session_header(iteration, is_first_run)

        # 创建客户端（新上下文）
        try:
            client = create_client(config)
        except ImportError:
            print("警告: Claude SDK 未安装，使用模拟模式")
            print("安装方法: pip install claude-code-sdk")
            # 使用模拟客户端进行演示
            from core.mock_client import MockClient
            client = MockClient(config)

        # 选择提示
        if is_first_run:
            prompt = get_initializer_prompt(config)
            is_first_run = False
        else:
            prompt = get_coding_prompt(config)

        # 运行会话
        async with client:
            status, response = await run_agent_session(client, prompt, config)

        # 处理状态
        if status == "complete":
            print("\n所有任务已完成!")
            break
        elif status == "continue":
            print(f"\n代理将在 {config.session_delay} 秒后自动继续...")
            tracker = ProgressTracker(config.project_dir)
            tracker.print_summary()
            await asyncio.sleep(config.session_delay)
        elif status == "error":
            print("\n会话遇到错误")
            print("将使用新会话重试...")
            await asyncio.sleep(config.session_delay)

        # 会话间延迟
        if config.max_iterations is None or iteration < config.max_iterations:
            print("\n准备下一个会话...\n")
            await asyncio.sleep(1)

    # 最终摘要
    print_final_summary(config)


def print_session_header(session_num: int, is_initializer: bool) -> None:
    """打印格式化的会话头"""
    session_type = "初始化代理" if is_initializer else "编码代理"
    print("\n" + "=" * 70)
    print(f"  会话 {session_num}: {session_type}")
    print("=" * 70)
    print()


def print_final_summary(config: Config) -> None:
    """打印最终摘要"""
    print("\n" + "=" * 70)
    print("  工作流完成")
    print("=" * 70)
    print(f"\n项目目录: {config.project_dir}")

    tracker = ProgressTracker(config.project_dir)
    tracker.print_summary()

    print("\n" + "-" * 70)
    print("  运行生成的应用:")
    print("-" * 70)
    print(f"\n  cd {config.project_dir.resolve()}")
    print("  ./init.sh           # 运行设置脚本")
    print("  # 或手动:")
    print("  npm install && npm run dev")
    print("\n  然后打开 http://localhost:3000")
    print("-" * 70)
    print("\n完成!")


def create_client(config: Config):
    """创建 Claude SDK 客户端"""
    try:
        from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
        from claude_code_sdk.types import HookMatcher
    except ImportError:
        raise ImportError("Claude SDK 未安装。运行: pip install claude-code-sdk")

    from core.security import bash_security_hook

    # Puppeteer MCP 工具
    puppeteer_tools = [
        "mcp__puppeteer__puppeteer_navigate",
        "mcp__puppeteer__puppeteer_screenshot",
        "mcp__puppeteer__puppeteer_click",
        "mcp__puppeteer__puppeteer_fill",
        "mcp__puppeteer__puppeteer_select",
        "mcp__puppeteer__puppeteer_hover",
        "mcp__puppeteer__puppeteer_evaluate",
    ]

    # 内置工具
    builtin_tools = ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]

    # 安全设置
    security_settings = {
        "sandbox": {"enabled": config.sandbox_enabled, "autoAllowBashIfSandboxed": True},
        "permissions": {
            "defaultMode": "acceptEdits",
            "allow": [
                "Read(./**)",
                "Write(./**)",
                "Edit(./**)",
                "Glob(./**)",
                "Grep(./**)",
                "Bash(*)",
                *puppeteer_tools,
            ],
        },
    }

    # 写入设置文件
    settings_file = config.project_dir / ".claude_settings.json"
    with open(settings_file, "w") as f:
        json.dump(security_settings, f, indent=2)

    print(f"安全设置已创建: {settings_file}")
    print(f"   - 沙箱已{'启用' if config.sandbox_enabled else '禁用'}")
    print(f"   - 文件系统限制到: {config.project_dir.resolve()}")
    print(f"   - Bash 命令限制到白名单")
    print()

    return ClaudeSDKClient(
        options=ClaudeCodeOptions(
            model=config.model,
            system_prompt="你是一位专业的全栈开发者，正在构建一个生产级质量的 Web 应用。",
            allowed_tools=[*builtin_tools, *puppeteer_tools],
            mcp_servers=config.mcp_servers,
            hooks={
                "PreToolUse": [
                    HookMatcher(matcher="Bash", hooks=[bash_security_hook]),
                ],
            },
            max_turns=1000,
            cwd=str(config.project_dir.resolve()),
            settings=str(settings_file.resolve()),
        )
    )
