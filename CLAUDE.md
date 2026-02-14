# 目标驱动工作流（原生 Task 集成版）

> 一套文件约定 + Claude Code 原生能力，让 Claude 跨会话持续开发

## 这是什么

一组约定：用 `.workflow/` 目录下的文件记录项目状态，配合 Claude Code 的原生 Task 系统实现跨会话持续开发。

**核心改变**：
- ✅ 用原生 TaskCreate/TaskUpdate 管理任务
- ✅ 用原生 blocks/blockedBy 管理依赖
- ✅ 保留验收标准系统（acceptance_criteria）
- ✅ 自动同步到 state.json（文件持久化）

## 事实来源

- `.workflow/GOAL.md` — 理想状态
- `.workflow/REALITY.md` — 当前状态
- `.workflow/criteria.json` — 任务验收标准
- `.workflow/state.json` — 状态快照（自动生成）

## criteria.json 格式

```json
{
  "task-001": {
    "acceptance_criteria": [
      {"criterion": "测试通过", "type": "auto", "verify": "pytest tests/ -q", "passed": false},
      {"criterion": "代码审查通过", "type": "manual", "passed": false}
    ]
  }
}
```

验收标准：`auto` 绑定 shell 命令自动验证，`manual` 需用户确认。

## 命令

```
/workflow:task      # 创建任务并设置验收标准
/workflow:verify    # 验收检查（运行测试、询问用户）
/workflow:status    # 查看进度
/git:commit         # 提交代码
/test:run          # 运行测试
```

## 目录结构

```
.workflow/              # 状态（事实来源）
.claude/              # Claude Code 配置
├── hooks.py          # 同步原生 Task 到 state.json
└── commands/         # 自定义命令
    └── workflow/     # 工作流命令
docs/                 # 文档
examples/             # 示例项目
```

## 核心理念

**保留独特价值，依赖原生能力**：
- ✅ 验收标准自动验证（独特价值）
- ✅ 文件持久化（跨会话/跨机器）
- ✅ SessionStart Hook 自动显示进度
- ✅ 原生任务管理（更强大）
- ✅ 原生依赖管理（更可靠）
- ✅ 原生并行执行（更简单）

## 与旧方案的区别

| 功能 | 旧方案 | 新方案 |
|-----|---------|---------|
| 任务管理 | tasks.json | 原生 Task 系统 |
| 依赖管理 | dependencies | blocks/blockedBy |
| 并行执行 | 手动分析 | 原生 Task 工具 |
| 代码量 | 441 行 | 140 行（-68%） |
