# 增强工作流快速参考

## 三大核心特性

### 1️⃣ Skills 集成

**什么是 Skills？**
Claude Code 的专业能力扩展，为特定任务提供专业知识和工具。

**如何使用？**

```python
# 在任务中指定 skill
manager.add_task(
    title="编写产品需求文档",
    skill="product-manager-toolkit",
    acceptance_criteria=["PRD 完整", "RICE 评分完成"]
)
```

**可用 Skills：**

| Skill | 用途 | 适用角色 |
|-------|------|----------|
| `product-manager-toolkit` | RICE 优先级、PRD 模板、用户访谈 | PM |
| `architecture-review` | 代码结构分析、重构建议 | Developer |
| `test:run` | 运行测试并报告结果 | Tester |
| `git:commit` | Conventional Commits 格式提交 | Developer |
| `git:pr` | 创建 PR 并推送 | Developer |
| `find-skills` | 发现和安装新 skills | All |

**在 Claude Code 中：**

```
# Claude 会自动识别任务的 skill 字段并调用
继续开发

# 或手动触发
/product-manager-toolkit
```

---

### 2️⃣ 多角色协作

**支持的角色：**

- **PM** (Product Manager) - 产品经理
- **Developer** - 开发工程师
- **Tester** - 测试工程师
- **Designer** - 设计师
- **Reviewer** - 代码审查者

**如何使用？**

```python
# PM 任务
manager.add_task(
    title="编写功能 PRD",
    role="PM",
    assignee="Alice",
    skill="product-manager-toolkit"
)

# 开发任务（依赖 PM 任务）
manager.add_task(
    title="实现功能",
    role="Developer",
    assignee="Bob",
    dependencies=["task-001"],  # 依赖 PM 任务
    reviewers=["Charlie", "David"]  # 需要审查
)

# 测试任务
manager.add_task(
    title="编写测试",
    role="Tester",
    assignee="Eve",
    dependencies=["task-002"],
    skill="test:run"
)
```

**工作流示例：**

```
PM (Alice)
  ↓ 依赖
Developer (Bob) → 审查 (Charlie, David)
  ↓ 依赖
Tester (Eve)
```

---

### 3️⃣ 验收标准

**什么是验收标准？**
任务完成的明确、可验证的条件。

**如何定义？**

```python
manager.add_task(
    title="实现登录功能",
    role="Developer",
    acceptance_criteria=[
        "用户可以使用邮箱和密码登录",
        "登录失败显示错误提示",
        "登录成功后跳转到首页",
        "所有单元测试通过",
        "代码审查通过"
    ]
)
```

**如何检查？**

```python
# 更新单个标准的状态
task.update_criterion_status("用户可以使用邮箱和密码登录", True)

# 检查是否所有标准都满足
if task.check_acceptance_criteria():
    manager.complete_task(task.id)
```

**在 Claude Code 中：**

```
当前任务: 实现登录功能

验收标准:
✅ 用户可以使用邮箱和密码登录
✅ 登录失败显示错误提示
⏳ 登录成功后跳转到首页
⏳ 所有单元测试通过
⏳ 代码审查通过

进度: 2/5 (40%)
```

---

## 完整示例

### 场景：构建用户认证系统

```python
from pathlib import Path
from core.tasks import TaskManager

manager = TaskManager(Path(".workflow"))

# 1. PM 任务
manager.add_task(
    title="用户认证功能 PRD",
    priority=1,
    role="PM",
    assignee="Alice",
    skill="product-manager-toolkit",
    steps=[
        "定义用户故事",
        "完成 RICE 评分",
        "定义成功指标"
    ],
    acceptance_criteria=[
        "PRD 包含至少 3 个用户故事",
        "完成 RICE 评分",
        "定义了可衡量的成功指标",
        "团队评审通过"
    ]
)

# 2. 架构设计
manager.add_task(
    title="设计认证系统架构",
    priority=2,
    role="Developer",
    assignee="Bob",
    dependencies=["task-001"],
    skill="architecture-review",
    reviewers=["Charlie"],
    acceptance_criteria=[
        "选择并文档化认证方案",
        "数据库模型设计完成",
        "API 接口定义完成",
        "架构评审通过"
    ]
)

# 3. 后端开发
manager.add_task(
    title="实现注册和登录 API",
    priority=3,
    role="Developer",
    assignee="Bob",
    dependencies=["task-002"],
    reviewers=["Charlie"],
    acceptance_criteria=[
        "注册接口实现并测试通过",
        "登录接口实现并测试通过",
        "密码使用 bcrypt 加密",
        "单元测试覆盖率 > 80%",
        "代码审查通过"
    ]
)

# 4. 测试
manager.add_task(
    title="编写集成测试",
    priority=4,
    role="Tester",
    assignee="David",
    dependencies=["task-003"],
    skill="test:run",
    acceptance_criteria=[
        "覆盖所有用户场景",
        "测试通过率 100%",
        "性能测试通过"
    ]
)
```

---

## 最佳实践

### ✅ 好的验收标准

- "所有单元测试通过"
- "代码审查通过"
- "API 响应时间 < 200ms"
- "文档包含使用示例"
- "测试覆盖率 > 80%"

### ❌ 不好的验收标准

- "代码质量好"（不可验证）
- "功能完成"（太模糊）
- "用户满意"（无法量化）

### 角色分配原则

- **PM** - 需求分析、优先级评估、产品决策
- **Developer** - 代码实现、架构设计、技术决策
- **Tester** - 测试设计、质量保证、bug 验证
- **Designer** - UI/UX 设计、交互设计
- **Reviewer** - 代码审查、架构审查、安全审查

### Skills 选择指南

| 任务类型 | 推荐 Skill |
|---------|-----------|
| 需求分析 | `product-manager-toolkit` |
| 架构设计 | `architecture-review` |
| 代码实现 | 无（或自定义 agent） |
| 测试 | `test:run` |
| 提交代码 | `git:commit` |
| 创建 PR | `git:pr` |

---

## 在 Claude Code 中使用

### 初始化项目

```bash
# 使用增强工作流示例
python3 examples/create_enhanced_example.py

# 或手动创建
python3 tools/init_workflow.py ./my_project --name "我的项目"
```

### 继续开发

```
继续开发
```

Claude 会：
1. 读取当前任务
2. 识别 `role`、`skill`、`acceptance_criteria`
3. 自动调用对应的 skill
4. 检查验收标准
5. 完成后更新状态

### 查看进度

```
/workflow:status
```

输出：

```
📊 任务统计:
   总计: 8
   ✅ 已完成: 3
   🔄 进行中: 1
   ⏳ 待处理: 4

📌 当前任务: [task-004] 实现注册和登录 API
   角色: Developer
   负责人: Bob
   审查人: Charlie
   Skill: 无

   验收标准:
   ✅ 注册接口实现并测试通过
   ✅ 登录接口实现并测试通过
   ⏳ 密码使用 bcrypt 加密
   ⏳ 单元测试覆盖率 > 80%
   ⏳ 代码审查通过

   进度: 2/5 (40%)
```

---

## 常见问题

### Q: 如何添加自定义 Skill？

A: 在 `.claude/skills/` 目录下创建新的 skill 定义。参考 `example-skills` 中的示例。

### Q: 如何处理跨角色的任务？

A: 使用 `dependencies` 和 `reviewers` 字段：

```python
manager.add_task(
    title="前端开发",
    role="Developer",
    dependencies=["task-001"],  # 依赖后端任务
    reviewers=["Designer", "PM"]  # 需要设计师和 PM 审查
)
```

### Q: 验收标准可以动态修改吗？

A: 可以。在任务执行过程中可以添加或修改验收标准：

```python
task = manager.load_tasks()[0]
task.acceptance_criteria.append("新增的验收标准")
task.criteria_status["新增的验收标准"] = False
manager.save_tasks([task])
```

### Q: 如何查看所有可用的 Skills？

A: 在 Claude Code 中输入：

```
/find-skills
```

---

## 相关文档

- [完整文档](docs/ENHANCED_WORKFLOW.md)
- [示例项目](examples/enhanced-workflow/)
- [主 README](README.md)
- [CLAUDE.md](CLAUDE.md)
