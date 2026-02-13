"""
配置管理
========

集中管理工作流的所有配置项。
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Set


@dataclass
class Config:
    """工作流配置"""

    # 项目设置
    project_dir: Path
    model: str = "claude-sonnet-4-5-20250929"

    # 迭代控制
    max_iterations: Optional[int] = None  # None 表示无限
    session_delay: int = 3  # 会话间隔秒数

    # 安全设置
    sandbox_enabled: bool = True
    allowed_commands: Set[str] = field(default_factory=lambda: {
        # 文件操作
        "ls", "cat", "head", "tail", "wc", "grep", "find",
        "cp", "mv", "mkdir", "chmod",
        # 目录
        "pwd", "cd",
        # 开发工具
        "npm", "node", "npx", "yarn", "pnpm",
        "python", "pip", "poetry",
        "go", "cargo",
        # 版本控制
        "git",
        # 进程管理
        "ps", "lsof", "kill", "pkill", "sleep",
        # 其他
        "echo", "env", "which", "curl", "wget",
    })

    # MCP 服务器
    mcp_servers: dict = field(default_factory=lambda: {
        "puppeteer": {
            "command": "npx",
            "args": ["puppeteer-mcp-server"]
        }
    })

    # 路径配置
    prompts_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "prompts")
    templates_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "templates")

    @property
    def feature_list_path(self) -> Path:
        """feature_list.json 路径"""
        return self.project_dir / "feature_list.json"

    @property
    def progress_path(self) -> Path:
        """progress.json 路径"""
        return self.project_dir / "progress.json"

    @property
    def session_notes_path(self) -> Path:
        """session_notes.md 路径"""
        return self.project_dir / "session_notes.md"

    @property
    def app_spec_path(self) -> Path:
        """app_spec.txt 路径"""
        return self.project_dir / "app_spec.txt"

    @property
    def init_script_path(self) -> Path:
        """init.sh 路径"""
        return self.project_dir / "init.sh"

    def __post_init__(self):
        """初始化后处理"""
        # 确保路径是 Path 对象
        if isinstance(self.project_dir, str):
            self.project_dir = Path(self.project_dir)
        if isinstance(self.prompts_dir, str):
            self.prompts_dir = Path(self.prompts_dir)
        if isinstance(self.templates_dir, str):
            self.templates_dir = Path(self.templates_dir)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "project_dir": str(self.project_dir),
            "model": self.model,
            "max_iterations": self.max_iterations,
            "session_delay": self.session_delay,
            "sandbox_enabled": self.sandbox_enabled,
            "allowed_commands": list(self.allowed_commands),
        }
