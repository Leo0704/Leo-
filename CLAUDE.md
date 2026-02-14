# 目标驱动工作流

> 一套文件约定 + Claude Code 命令，让 Claude 跨会话持续开发

## 这是什么

一组约定：用 `.workflow/` 目录下的三个文件（GOAL.md、REALITY.md、tasks.json）记录项目状态，配合 Claude Code 的自定义命令实现跨会话持续开发。

不是框架，不是 SDK，不需要安装任何东西。

## 事实来源

- `.workflow/GOAL.md` — 理想状态
- `.workflow/REALITY.md` — 当前状态
- `.workflow/tasks.json` — 任务列表和验收标准

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
      "context": "处理此任务时应关注什么",
      "acceptance_criteria": [
        {"criterion": "测试通过", "type": "auto", "verify": "pytest tests/ -q", "passed": false},
        {"criterion": "代码审查通过", "type": "manual", "passed": false}
      ]
    }
  ]
}
```

验收标准：`auto` 绑定 shell 命令自动验证，`manual` 需用户确认。

## 命令

```
/workflow:continue   # 继续任务（含验收检查）
/workflow:status     # 查看进度
/workflow:add-task   # 添加任务
/git:commit          # 提交代码
/test:run            # 运行测试
```

## 目录结构

```
.workflow/              # 状态（事实来源）
.claude/commands/       # 自定义命令
.claude/hooks.py        # 会话启动时自动显示进度
core/tasks.py           # Python 工具（可选）
tools/                  # CLI 工具（可选）
templates/quickstart/   # 快速开始模板
examples/               # 示例项目
```
