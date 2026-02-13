"""
安全钩子
========

Bash 命令安全验证钩子。使用白名单机制，只允许预定义的安全命令。
"""

import os
import re
import shlex
from typing import Set

from core.config import Config


# 需要额外验证的命令
COMMANDS_NEEDING_EXTRA_VALIDATION = {"pkill", "chmod", "rm"}


def split_command_segments(command_string: str) -> list[str]:
    """
    将复合命令分割为独立段。

    处理命令链（&&, ||, ;）但不处理管道（管道是单个命令）。
    """
    # 分割 && 和 ||
    segments = re.split(r"\s*(?:&&|\|\|)\s*", command_string)

    # 进一步分割分号
    result = []
    for segment in segments:
        sub_segments = re.split(r'(?<!["\'])\s*;\s*(?!["\'])', segment)
        for sub in sub_segments:
            sub = sub.strip()
            if sub:
                result.append(sub)

    return result


def extract_commands(command_string: str) -> list[str]:
    """
    从 Shell 命令字符串提取命令名。

    处理管道、命令链和子 Shell。
    返回基础命令名（不含路径）。
    """
    commands = []

    # 预处理分号
    segments = re.split(r'(?<!["\'])\s*;\s*(?!["\'])', command_string)

    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue

        try:
            tokens = shlex.split(segment)
        except ValueError:
            return []  # 解析失败，安全起见返回空

        if not tokens:
            continue

        expect_command = True

        for token in tokens:
            # Shell 操作符
            if token in ("|", "||", "&&", "&"):
                expect_command = True
                continue

            # Shell 关键字
            if token in ("if", "then", "else", "elif", "fi", "for", "while",
                         "until", "do", "done", "case", "esac", "in", "!", "{", "}"):
                continue

            # 跳过标志
            if token.startswith("-"):
                continue

            # 跳过变量赋值
            if "=" in token and not token.startswith("="):
                continue

            if expect_command:
                cmd = os.path.basename(token)
                commands.append(cmd)
                expect_command = False

    return commands


def validate_pkill_command(command_string: str, allowed_processes: Set[str]) -> tuple[bool, str]:
    """验证 pkill 命令 - 只允许终止开发相关进程"""
    try:
        tokens = shlex.split(command_string)
    except ValueError:
        return False, "无法解析 pkill 命令"

    if not tokens:
        return False, "空的 pkill 命令"

    args = [t for t in tokens[1:] if not t.startswith("-")]

    if not args:
        return False, "pkill 需要进程名"

    target = args[-1]
    if " " in target:
        target = target.split()[0]

    if target in allowed_processes:
        return True, ""
    return False, f"pkill 只允许用于开发进程: {allowed_processes}"


def validate_chmod_command(command_string: str) -> tuple[bool, str]:
    """验证 chmod 命令 - 只允许 +x 模式"""
    try:
        tokens = shlex.split(command_string)
    except ValueError:
        return False, "无法解析 chmod 命令"

    if not tokens or tokens[0] != "chmod":
        return False, "不是 chmod 命令"

    mode = None
    for token in tokens[1:]:
        if token.startswith("-"):
            return False, "不允许 chmod 标志"
        elif mode is None:
            mode = token

    if mode is None:
        return False, "chmod 需要模式"

    if not re.match(r"^[ugoa]*\+x$", mode):
        return False, f"chmod 只允许 +x 模式，得到: {mode}"

    return True, ""


def validate_rm_command(command_string: str) -> tuple[bool, str]:
    """验证 rm 命令 - 禁止递归删除和强制删除"""
    try:
        tokens = shlex.split(command_string)
    except ValueError:
        return False, "无法解析 rm 命令"

    # 检查危险标志
    for token in tokens[1:]:
        if token in ("-r", "-rf", "-fr", "-R", "-Rf", "-fR", "--recursive"):
            return False, "禁止递归或强制删除"

    return True, ""


async def bash_security_hook(input_data, tool_use_id=None, context=None):
    """
    Bash 命令安全钩子。

    使用白名单验证 Bash 命令。只有 ALLOWED_COMMANDS 中的命令被允许。
    """
    if input_data.get("tool_name") != "Bash":
        return {}

    command = input_data.get("tool_input", {}).get("command", "")
    if not command:
        return {}

    # 从配置获取允许的命令（或使用默认）
    # 在实际使用中，应该从 Config 读取
    allowed_commands = {
        "ls", "cat", "head", "tail", "wc", "grep", "find",
        "cp", "mv", "mkdir", "chmod", "pwd", "cd",
        "npm", "node", "npx", "yarn", "pnpm",
        "python", "pip", "poetry",
        "git",
        "ps", "lsof", "kill", "pkill", "sleep",
        "echo", "env", "which", "curl", "wget",
    }

    allowed_pkill_processes = {"node", "npm", "npx", "vite", "next", "python"}

    # 提取命令
    commands = extract_commands(command)

    if not commands:
        return {
            "decision": "block",
            "reason": f"无法解析命令进行安全验证: {command}",
        }

    # 分割段
    segments = split_command_segments(command)

    # 检查每个命令
    for cmd in commands:
        if cmd not in allowed_commands:
            return {
                "decision": "block",
                "reason": f"命令 '{cmd}' 不在允许列表中",
            }

        # 额外验证
        if cmd in COMMANDS_NEEDING_EXTRA_VALIDATION:
            cmd_segment = command
            for segment in segments:
                if cmd in extract_commands(segment):
                    cmd_segment = segment
                    break

            if cmd == "pkill":
                allowed, reason = validate_pkill_command(cmd_segment, allowed_pkill_processes)
                if not allowed:
                    return {"decision": "block", "reason": reason}
            elif cmd == "chmod":
                allowed, reason = validate_chmod_command(cmd_segment)
                if not allowed:
                    return {"decision": "block", "reason": reason}
            elif cmd == "rm":
                allowed, reason = validate_rm_command(cmd_segment)
                if not allowed:
                    return {"decision": "block", "reason": reason}

    return {}
