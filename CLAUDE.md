# 无限开发工作流 (Infinite Workflow)

> 让 Claude Code 跨会话持续开发的状态驱动框架

## 项目目标

创建一个**零 API Key 依赖**的工作流系统，让 Claude Code 可以通过状态文件持久化实现跨会话持续开发。

## 设计原则

1. **状态驱动** - 所有进度保存在 `.workflow/` 目录
2. **上下文无关** - 每个会话通过读取状态恢复上下文
3. **增量提交** - 每个任务完成后立即提交
4. **验收标准** - 每个任务有明确的完成条件，区分自动验证和手动确认

## 事实来源

项目有且只有两层状态：

- `GOAL.md` + `REALITY.md` — 高层目标和当前现实的差距
- `tasks.json` — 具体任务列表、验收标准、依赖关系

其他文件（STATUS.md、status.json）是辅助展示，不是事实来源。

## 目录结构

```
项目目录/
├── .workflow/           # 工作流状态
│   ├── GOAL.md         # 理想状态（事实来源）
│   ├── REALITY.md      # 当前状态（事实来源）
│   └── tasks.json      # 任务列表（事实来源）
├── .claude/            # Claude Code 配置
│   ├── commands/       # 自定义命令
│   ├── skills/         # 自定义技能
│   └── settings.json   # Hooks 配置
├── core/               # Python 可选工具
│   └── tasks.py        # 任务管理（可选，Claude 可直接编辑 JSON）
├── tools/              # 命令行工具（可选）
├── templates/          # 项目模板
└── WORKFLOW.md         # 工作流说明
```

## tasks.json 格式

```json
{
  "tasks": [
    {
      "id": "task-001",
      "title": "任务名",
      "status": "pending",
      "priority": 1,
      "description": "描述",
      "steps": ["步骤1", "步骤2"],
      "dependencies": ["task-000"],
      "context": "执行此任务时的视角和关注点",
      "acceptance_criteria": [
        {
          "criterion": "测试通过",
          "type": "auto",
          "verify": "pytest tests/ -q",
          "passed": false
        },
        {
          "criterion": "代码审查通过",
          "type": "manual",
          "passed": false
        }
      ]
    }
  ]
}
```

### 验收标准类型

- `auto` — 可通过运行 `verify` 命令自动验证（exit code 0 = 通过）
- `manual` — 需要用户手动确认

### context 字段

替代虚假的"角色分配"。不是假装有多个人在协作，而是诚实地告诉 Claude 处理此任务时应关注什么：

```json
"context": "以安全工程师的视角审查，关注 OWASP Top 10"
"context": "关注用户体验，确保交互流畅"
"context": "关注性能，API 响应时间 < 200ms"
```

## 使用方法

### 自定义命令
```
/workflow:status      # 查看进度和验收标准
/workflow:continue   # 继续任务（含验收检查）
/workflow:add-task   # 添加任务（含验收标准）
/git:commit         # 提交代码
/test:run           # 运行测试
```

### 快速开始
```bash
cp -r templates/quickstart/.workflow ./my_project/
# 编辑 GOAL.md，然后在 Claude Code 中说"继续开发"
```

## 注意事项

- 不需要任何 API Key，直接在 Claude Code 中使用
- Python 工具是可选的，Claude 可以直接读写 JSON 文件
- 始终先读取当前状态再开始工作
- 使用 conventional commits 格式提交
