# 无限开发工作流

> 让 Claude Code 跨会话持续开发的状态驱动框架

## 核心理念

**不需要 API Key，直接在 Claude Code 中使用！**

工作流通过**状态文件**驱动，而非代码调用 API：

```
状态文件 → Claude 读取 → Claude 工作 → Claude 更新状态 → 循环
```

## 特性

- **状态驱动** - 基于文件系统的状态持久化
- **零 API 依赖** - 直接在 Claude Code 中使用
- **自定义命令** - 支持 20+ Slash Commands
- **Hooks 自动化** - 自动格式化、lint、通知
- **MCP 集成** - 连接 GitHub、数据库等外部服务
- **Skills** - 自定义 AI 子代理
- **Plan Mode** - 复杂任务先规划再执行

## 快速开始

### 1. 初始化工作流

在 Claude Code 中说：

```
帮我初始化一个新项目的无限开发工作流
```

或者在命令行：

```bash
python tools/init_workflow.py ./my_project --name "我的项目" --tasks "任务1" "任务2" "任务3"
```

### 2. 开始开发

每次新会话开始时说：

```
继续开发
```

### 3. 使用自定义命令

```
/workflow:status    # 查看进度
/workflow:continue  # 继续工作
/workflow:add-task  # 添加任务
/git:commit        # 提交代码
/test:run          # 运行测试
```

## 目录结构

```
项目目录/
├── .workflow/           # 工作流状态
│   ├── STATUS.md       # 人类可读状态
│   ├── status.json     # 机器可读状态
│   ├── tasks.json      # 任务列表
│   └── sessions/       # 会话历史
├── .claude/           # Claude Code 配置
│   ├── commands/      # 自定义命令
│   ├── skills/        # 自定义技能
│   └── settings.json  # Hooks 配置
├── core/              # 核心模块
├── tools/             # 命令行工具
├── docs/              # 文档
└── templates/         # 项目模板
```

## 高级功能

### 自定义命令

```bash
/workflow:status      # 查看工作流状态
/workflow:continue    # 继续下一个任务
/workflow:add-task    # 添加新任务
/git:commit          # 提交更改
/git:pr              # 创建 PR
/test:run            # 运行测试
```

### Hooks 自动化

在 `.claude/settings.json` 中配置：

```json
{
  "hooks": {
    "SessionStart": [...],
    "PostToolUse": [...]
  }
}
```

### MCP 服务器

```bash
# 添加 MCP 服务器
claude mcp add github --transport http https://api.github.com/mcp/
```

### Skills

```bash
# 使用架构审查技能
使用 architecture-review skill 分析项目
```

## 工具命令

```bash
# 初始化工作流
python tools/init_workflow.py ./项目目录 --name "项目名"

# 查看进度
python tools/view_progress.py ./项目目录

# 创建新项目
python tools/new_project.py 项目名

# 自动修复
python tools/auto_fix.py

# 生成变更日志
python tools/changelog.py
```

## 许可证

MIT License
