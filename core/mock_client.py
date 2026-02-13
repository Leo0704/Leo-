"""
模拟客户端
==========

当 Claude SDK 未安装时使用的模拟客户端，用于演示和测试。
"""

import asyncio
import json
from pathlib import Path
from typing import AsyncIterator


class MockMessage:
    """模拟消息"""
    pass


class AssistantMessage(MockMessage):
    """模拟助手消息"""
    def __init__(self, text: str):
        self.content = [TextBlock(text)]


class UserMessage(MockMessage):
    """模拟用户消息"""
    def __init__(self, results: list):
        self.content = [ToolResultBlock(r) for r in results]


class TextBlock:
    """文本块"""
    def __init__(self, text: str):
        self.text = text


class ToolUseBlock:
    """工具使用块"""
    def __init__(self, name: str, input_data: dict):
        self.name = name
        self.input = input_data


class ToolResultBlock:
    """工具结果块"""
    def __init__(self, content: str, is_error: bool = False):
        self.content = content
        self.is_error = is_error


class MockClient:
    """模拟 Claude SDK 客户端"""

    def __init__(self, config):
        self.config = config
        self._in_context = False
        self._query = None

    async def __aenter__(self):
        self._in_context = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._in_context = False
        return False

    async def query(self, message: str):
        """发送查询"""
        self._query = message

    async def receive_response(self) -> AsyncIterator[MockMessage]:
        """接收响应（模拟）"""
        # 生成模拟响应
        responses = self._generate_mock_response()

        for response in responses:
            yield response
            await asyncio.sleep(0.1)  # 模拟延迟

    def _generate_mock_response(self) -> list[MockMessage]:
        """生成模拟响应"""
        responses = []

        # 检查是否是初始化会话
        if "初始化" in self._query or "首次会话" in self._query:
            responses.extend(self._mock_initializer_response())
        else:
            responses.extend(self._mock_coding_response())

        return responses

    def _mock_initializer_response(self) -> list[MockMessage]:
        """模拟初始化响应"""
        responses = []

        # 模拟读取规格文件
        responses.append(AssistantMessage(
            "我来开始初始化项目。首先读取项目规格..."
        ))

        # 模拟创建 feature_list.json
        feature_list = [
            {
                "id": f"feat-{i:03d}",
                "category": ["core", "ui", "api", "auth"][i % 4],
                "description": f"示例功能 {i}",
                "priority": i,
                "steps": [
                    "步骤 1: 分析需求",
                    "步骤 2: 设计实现",
                    "步骤 3: 编写代码",
                    "步骤 4: 测试验证"
                ],
                "status": "pending",
                "verification": f"验证功能 {i} 正常工作"
            }
            for i in range(1, 11)
        ]

        responses.append(AssistantMessage(
            f"\n\n我已经创建了 feature_list.json，包含 {len(feature_list)} 个功能。\n\n"
            "接下来我将创建 init.sh 脚本和初始化 Git 仓库...\n\n"
            "[模拟模式] 初始化完成。请安装 Claude SDK 以获得完整功能。"
        ))

        # 写入模拟的 feature_list.json
        feature_path = self.config.project_dir / "feature_list.json"
        with open(feature_path, "w", encoding="utf-8") as f:
            json.dump(feature_list, f, indent=2, ensure_ascii=False)

        return responses

    def _mock_coding_response(self) -> list[MockMessage]:
        """模拟编码响应"""
        responses = []

        responses.append(AssistantMessage(
            "我来继续开发。首先检查当前进度...\n\n"
            f"项目目录: {self.config.project_dir}\n\n"
        ))

        # 读取 feature_list.json
        feature_path = self.config.project_dir / "feature_list.json"
        if feature_path.exists():
            with open(feature_path, "r", encoding="utf-8") as f:
                features = json.load(f)

            pending = [f for f in features if f["status"] == "pending"]
            completed = [f for f in features if f["status"] == "completed"]

            responses.append(AssistantMessage(
                f"\n\n当前进度:\n"
                f"- 已完成: {len(completed)}\n"
                f"- 待处理: {len(pending)}\n\n"
                "[模拟模式] 请安装 Claude SDK 以获得完整的自主开发功能。\n"
                "安装方法: pip install claude-code-sdk"
            ))

            # 模拟完成一个功能
            if pending:
                feature = pending[0]
                feature["status"] = "completed"

                with open(feature_path, "w", encoding="utf-8") as f:
                    json.dump(features, f, indent=2, ensure_ascii=False)

                responses.append(AssistantMessage(
                    f"\n\n[模拟] 已标记功能 {feature['id']} 为完成。\n"
                    f"描述: {feature['description']}"
                ))
        else:
            responses.append(AssistantMessage(
                "\n\nfeature_list.json 不存在。请先运行初始化会话。"
            ))

        return responses


class MockCodeOptions:
    """模拟代码选项"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockSDKClient:
    """模拟 SDK 客户端类"""
    ClaudeCodeOptions = MockCodeOptions

    def __init__(self, options=None):
        self.options = options
