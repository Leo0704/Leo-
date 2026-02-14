# 目标驱动工作流

> 让 Claude Code 自主地把软件开发到理想状态

## 核心理念

**不告诉 AI 做什么，而是告诉 AI 你想要什么。**

```
传统方式：任务列表 → 执行 → 完成
目标驱动：理想状态 → 差距分析 → 自主行动 → 迭代
```

## 快速开始

### 1. 复制模板

```bash
cp -r templates/quickstart/.workflow ./你的项目/
```

### 2. 编辑 GOAL.md

描述你想要的**理想状态**：

```markdown
# 项目理想状态

## 产品愿景
一个简洁的博客系统

## 成功标准
- [ ] 用户可以登录
- [ ] 用户可以发文章
- [ ] 页面加载 < 2秒

## 验收条件
当我使用时：
1. 注册流程 < 30秒
2. 写文章体验流畅
```

### 3. 启动开发

发送给 Claude：

```
读取 .workflow/GOAL.md 和 .workflow/REALITY.md
分析差距，开始实现核心功能
完成后更新 REALITY.md
```

### 4. 持续迭代

每次新会话：

```
继续目标驱动开发
```

---

## 示例项目

| 项目 | 类型 | 描述 | 状态 |
|------|------|------|------|
| [examples/todo-app](examples/todo-app/) | Web | 浏览器待办应用 | ✅ 95% |
| [examples/cli-tool](examples/cli-tool/) | CLI | 命令行待办工具 | ✅ 100% |
| [examples/enhanced-workflow](examples/enhanced-workflow/) | 增强工作流 | Skills + 多角色 + 验收标准 | ✅ 新增 |

---

## 自动触发

配置 `.claude/settings.json` 后，每次会话自动显示进度：

```
==================================================
  🎯 目标驱动工作流 - 自动触发
==================================================

  📊 当前进度: 90%
  📋 待改进: 2 项

  📌 下一步建议:
     1. 更多示例项目
     2. MCP 集成
==================================================
```

---

## 文件结构

```
项目/
├── .workflow/
│   ├── GOAL.md       # 理想状态（你想要的）
│   └── REALITY.md    # 当前状态（实际是）
├── .claude/          # Claude Code 配置（可选）
│   ├── settings.json # Hooks 配置
│   └── hooks.py      # 自动触发脚本
└── [你的代码]/
```

---

## 增强特性

### 🎯 Skills 集成

利用 Claude Code 的专业能力扩展：

```python
manager.add_task(
    title="编写产品需求文档",
    skill="product-manager-toolkit",  # 自动调用 PM 工具
    acceptance_criteria=["PRD 包含用户故事", "完成 RICE 评分"]
)
```

可用 Skills：
- `product-manager-toolkit` - 产品管理（RICE、PRD）
- `architecture-review` - 架构审查
- `test:run` - 自动化测试
- `git:commit` / `git:pr` - Git 工作流

### 👥 多角色协作

支持团队分工和协作：

```python
# PM 任务
manager.add_task(
    title="需求分析",
    role="PM",
    assignee="Alice"
)

# 开发任务（依赖 PM）
manager.add_task(
    title="实现功能",
    role="Developer",
    assignee="Bob",
    dependencies=["task-001"],
    reviewers=["Charlie"]  # 代码审查
)
```

支持角色：PM、Developer、Tester、Designer、Reviewer

### ✅ 验收标准

明确的任务完成标准：

```python
manager.add_task(
    title="实现登录功能",
    acceptance_criteria=[
        "用户可以使用邮箱登录",
        "登录失败显示错误",
        "单元测试通过",
        "代码审查通过"
    ]
)
```

Claude 会自动检查验收标准并更新进度。

详见：[增强工作流文档](docs/ENHANCED_WORKFLOW.md)

---

## 目录结构

```
自动工作流/
├── templates/quickstart/  # 快速开始模板
├── examples/todo-app/     # 示例项目
├── core/                  # Python 可选工具
├── tools/                 # 命令行工具
├── .claude/              # Hooks 配置
└── .workflow/            # 本项目的工作流状态
```

---

## 一句话总结

**告诉 Claude 你想要什么，让它自己想办法。**

## 许可证

MIT
