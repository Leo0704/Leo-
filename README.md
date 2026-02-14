# 目标驱动工作流（原生 Task 集成版）

> 一套让 Claude Code 能够**自主地**把软件开发到理想状态的工作流框架。

## 核心理念

**保留独特价值，依赖原生能力**

- ✅ **自动验收机制** - shell 命令自动验证
- ✅ **文件持久化** - 跨会话、跨机器
- ✅ **自动进度显示** - SessionStart Hook

- ✅ **原生任务管理** - TaskCreate/TaskUpdate
- ✅ **原生依赖管理** - blocks/blockedBy
- ✅ **原生并行执行** - Task 工具

## 快速开始

```bash
# 1. 创建任务
/workflow:task 实现用户登录

# 2. 设置验收标准（交互式）
→ auto: 测试通过
→ manual: 代码审查

# 3. 完成后验收
/workflow:verify

# 4. 查看状态
/workflow:status
```

## 文件结构

```
.workflow/              # 状态（事实来源）
├── config.json        # 配置文件
├── criteria.json      # 验收标准
├── state.json        # 状态快照（自动生成）
├── GOAL.md          # 理想状态
└── REALITY.md        # 当前状态

.claude/
├── hooks.py          # 同步原生 Task → state.json
└── commands/
    ├── workflow/
    │   ├── task.md    # 创建任务
    │   ├── verify.md  # 验收检查
    │   └── status.md  # 查看状态
    ├── git/
    │   ├── commit.md
    │   └── pr.md
    └── test/
        └── run.md

docs/                 # 文档
├── QUICKSTART-NATIVE.md      # 5分钟上手
├── MIGRATION-GUIDE.md       # 迁移指南
└── NATIVE-TASK-INTEGRATION.md # 完整设计

examples/             # 示例项目
├── todo-app/        # 待办事项应用
└── cli-tool/        # CLI 工具
```

## 核心命令

| 命令 | 说明 | 示例 |
|-----|------|------|
| `/workflow:task` | 创建任务 + 验收标准 | `/workflow:task 实现API` |
| `/workflow:verify` | 验收检查 | `/workflow:verify task-003` |
| `/workflow:status` | 查看状态 | `/workflow:status` |
| `/git:commit` | 提交代码 | `/git:commit` |
| `/test:run` | 运行测试 | `/test:run` |

## 与旧方案的区别

| 指标 | 旧方案 | 新方案（集成原生） |
|-----|--------|------------------|
| 代码量 | 441 行 | 140 行（-68%） |
| 任务管理 | 自定义 tasks.json | **原生 Task 系统** |
| 依赖管理 | dependencies | **blocks/blockedBy** |
| 并行执行 | 手动分析 | **原生 Task 工具** |
| 验收标准 | acceptance_criteria | **保留** |
| 文件持久化 | tasks.json | **state.json（同步）** |

## 验收标准示例

```json
{
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
```

## 学习资源

1. **快速上手** → [docs/QUICKSTART-NATIVE.md](docs/QUICKSTART-NATIVE.md)
2. **完整设计** → [docs/NATIVE-TASK-INTEGRATION.md](docs/NATIVE-TASK-INTEGRATION.md)
3. **迁移指南** → [docs/MIGRATION-GUIDE.md](docs/MIGRATION-GUIDE.md)
4. **示例项目** → [examples/](examples/)

## License

MIT
