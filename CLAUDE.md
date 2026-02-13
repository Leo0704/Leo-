# 无限开发工作流 (Infinite Workflow)

> 让 Claude Code 跨会话持续开发的状态驱动框架

## 项目目标

创建一个**零 API Key 依赖**的工作流系统，让 Claude Code 可以通过状态文件持久化实现跨会话持续开发。

## 核心概念

1. **状态驱动** - 所有进度保存在 `.workflow/` 目录的状态文件中
2. **上下文无关** - 每个会话通过读取状态恢复上下文
3. **增量提交** - 每个任务完成后立即提交
4. **决策记录** - 重要决策写入 `decisions.md`

## 目录结构

```
项目目录/
├── .workflow/           # 工作流状态
│   ├── STATUS.md      # 人类可读状态
│   ├── status.json    # 机器可读状态
│   ├── tasks.json     # 任务列表
│   └── sessions/     # 会话历史
├── .claude/          # Claude Code 配置
│   ├── commands/     # 自定义命令
│   ├── skills/       # 自定义技能
│   └── settings.json # Hooks 配置
├── core/             # 核心模块
│   ├── tasks.py     # 任务管理
│   └── progress.py  # 进度跟踪
├── tools/            # 命令行工具
│   ├── init_workflow.py
│   ├── view_progress.py
│   ├── new_project.py
│   ├── auto_fix.py
│   └── changelog.py
├── docs/             # 文档
├── templates/        # 项目模板
└── WORKFLOW.md      # 工作流说明
```

## 快速开始

### 初始化新项目
```bash
python tools/init_workflow.py ./my_project --name "我的项目" --tasks "任务1" "任务2"
```

### 在 Claude Code 中继续开发
```
继续开发
```

### 使用自定义命令
```
/workflow:status      # 查看进度
/workflow:continue   # 继续任务
/workflow:add-task   # 添加任务
/git:commit         # 提交代码
/test:run           # 运行测试
```

## 关键文件说明

### .workflow/status.json
```json
{
  "project_name": "项目名",
  "current_task": { "id": "task-001", "title": "任务名", "status": "in_progress" },
  "stats": { "total": 10, "completed": 3, "in_progress": 1, "pending": 6 }
}
```

### .workflow/tasks.json
```json
{
  "tasks": [
    {
      "id": "task-001",
      "title": "任务名",
      "status": "in_progress",
      "priority": 1,
      "description": "描述",
      "steps": ["步骤1", "步骤2"]
    }
  ]
}
```

### 自定义命令格式 (.claude/commands/)
```
.claude/commands/
├── workflow/
│   ├── continue.md
│   ├── status.md
│   └── add-task.md
├── git/
│   ├── commit.md
│   └── pr.md
└── test/
    └── run.md
```

### Hooks 配置 (.claude/settings.json)
```json
{
  "hooks": {
    "SessionStart": [...],
    "PostToolUse": [...]
  }
}
```

### Skills (.claude/skills/)
```
.claude/skills/
├── architecture-review/
│   └── SKILL.md
├── product-manager-toolkit/
│   └── SKILL.md
└── find-skills/
    └── SKILL.md
```

## 使用规范

1. 每个任务应在 30 分钟内完成
2. 完成后立即更新状态并提交 Git
3. 重要决策记录到 `decisions.md`
4. 使用 Plan Mode 规划复杂任务
5. 使用 `/clear` 清理上下文

## 可用工具

- `python tools/init_workflow.py` - 初始化工作流
- `python tools/view_progress.py` - 查看进度
- `python tools/new_project.py` - 创建新项目
- `python tools/auto_fix.py` - 自动修复代码
- `python tools/changelog.py` - 生成变更日志

## 高级功能

### MCP 服务器
```bash
claude mcp add github --transport http https://api.github.com/mcp/
```

### Subagents
```bash
/agents create  # 创建自定义代理
/agents        # 列出可用代理
```

### Plan Mode
```bash
claude --permission-mode plan
# 或在会话中 Shift+Tab
```

## 注意事项

- 不需要任何 API Key，直接在 Claude Code 中使用
- 状态文件是唯一的事实来源
- 始终先读取当前状态再开始工作
- 使用 conventional commits 格式提交
