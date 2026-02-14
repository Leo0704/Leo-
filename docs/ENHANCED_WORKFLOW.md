# 增强工作流特性

## 概述

本文档介绍工作流系统的三个核心增强特性：
1. **Skills 集成** - 利用 Claude Code 的 skills 系统
2. **多角色协作** - 支持团队分工和协作
3. **验收标准** - 明确的任务完成标准

## 1. Skills 集成

### 什么是 Skills？

Skills 是 Claude Code 的专业能力扩展，可以为特定任务提供专业知识和工具。

### 可用的 Skills

- `product-manager-toolkit` - 产品管理工具包（RICE 优先级、PRD 模板等）
- `architecture-review` - 架构审查（代码结构分析、重构建议）
- `test:run` - 测试运行器
- `git:commit` - Git 提交助手
- `git:pr` - PR 创建助手
- 更多 skills 可通过 `find-skills` 发现

### 如何在任务中使用 Skills

```python
from core.tasks import TaskManager

manager = TaskManager(Path(".workflow"))

# 创建使用 skill 的任务
task = manager.add_task(
    title="设计新功能的产品需求",
    description="为用户认证功能编写 PRD",
    role="PM",
    skill="product-manager-toolkit",  # 指定使用的 skill
    acceptance_criteria=[
        "PRD 包含用户故事",
        "定义了验收标准",
        "完成 RICE 优先级评分"
    ]
)
```

### 在 Claude Code 中执行

当 Claude 看到任务指定了 `skill` 字段时，会自动调用对应的 skill：

```
# Claude 会自动识别并使用 skill
继续开发

# 或手动触发
/product-manager-toolkit
```

## 2. 多角色协作

### 支持的角色

- **PM** (Product Manager) - 产品经理
- **Developer** - 开发工程师
- **Tester** - 测试工程师
- **Designer** - 设计师
- **Reviewer** - 代码审查者

### 任务分配示例

```python
# PM 任务
manager.add_task(
    title="编写功能 PRD",
    role="PM",
    assignee="Alice",
    skill="product-manager-toolkit",
    acceptance_criteria=[
        "PRD 包含用户故事",
        "定义了成功指标"
    ]
)

# 开发任务（依赖 PM 任务）
manager.add_task(
    title="实现用户认证",
    role="Developer",
    assignee="Bob",
    dependencies=["task-001"],  # 依赖 PM 任务
    reviewers=["Charlie"],  # 需要代码审查
    acceptance_criteria=[
        "所有单元测试通过",
        "代码审查通过",
        "API 文档更新"
    ]
)

# 测试任务
manager.add_task(
    title="编写集成测试",
    role="Tester",
    assignee="David",
    dependencies=["task-002"],
    skill="test:run",
    acceptance_criteria=[
        "覆盖所有用户场景",
        "测试通过率 100%"
    ]
)
```

### 协作工作流

```
PM 任务 (task-001)
    ↓ (依赖)
开发任务 (task-002) → 代码审查 (Charlie)
    ↓ (依赖)
测试任务 (task-003)
```

## 3. 验收标准

### 什么是验收标准？

验收标准（Acceptance Criteria）是任务完成的明确、可验证的条件。

### 定义验收标准

```python
task = manager.add_task(
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

### 检查验收标准

```python
# 更新单个标准的状态
task.update_criterion_status("用户可以使用邮箱和密码登录", True)
task.update_criterion_status("登录失败显示错误提示", True)

# 检查是否所有标准都满足
if task.check_acceptance_criteria():
    manager.complete_task(task.id)
else:
    print("还有验收标准未满足")
```

### 在 Claude Code 中使用

Claude 会自动检查验收标准：

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

## 完整示例：构建用户认证功能

```python
from pathlib import Path
from core.tasks import TaskManager

manager = TaskManager(Path(".workflow"))

# 1. PM 任务：需求分析
manager.add_task(
    title="用户认证功能 PRD",
    description="定义用户认证的需求和范围",
    priority=1,
    role="PM",
    assignee="Alice",
    skill="product-manager-toolkit",
    acceptance_criteria=[
        "完成用户故事定义",
        "完成 RICE 优先级评分",
        "定义成功指标"
    ]
)

# 2. 架构设计任务
manager.add_task(
    title="认证系统架构设计",
    description="设计认证系统的技术架构",
    priority=2,
    role="Developer",
    assignee="Bob",
    dependencies=["task-001"],
    skill="architecture-review",
    reviewers=["Charlie"],
    acceptance_criteria=[
        "选择认证方案（JWT/Session）",
        "设计数据库模型",
        "定义 API 接口",
        "架构审查通过"
    ]
)

# 3. 开发任务
manager.add_task(
    title="实现用户注册和登录",
    description="实现核心认证功能",
    priority=3,
    role="Developer",
    assignee="Bob",
    dependencies=["task-002"],
    reviewers=["Charlie"],
    acceptance_criteria=[
        "注册功能完成",
        "登录功能完成",
        "密码加密存储",
        "单元测试覆盖率 > 80%",
        "代码审查通过"
    ]
)

# 4. 测试任务
manager.add_task(
    title="认证功能集成测试",
    description="编写和执行集成测试",
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

# 5. 文档任务
manager.add_task(
    title="更新 API 文档",
    description="更新认证相关的 API 文档",
    priority=5,
    role="Developer",
    assignee="Bob",
    dependencies=["task-004"],
    acceptance_criteria=[
        "API 文档完整",
        "包含使用示例",
        "文档审查通过"
    ]
)

# 查看任务摘要
manager.print_summary()
```

## 在 Claude Code 中的工作流

### 1. 初始化项目

```bash
python tools/init_workflow.py ./my_auth_project \
  --name "用户认证系统" \
  --tasks "PRD" "架构设计" "开发" "测试" "文档"
```

### 2. 在 Claude Code 中继续开发

```
继续开发
```

Claude 会：
1. 读取当前任务
2. 识别任务的 `role` 和 `skill`
3. 自动调用对应的 skill
4. 检查验收标准
5. 完成后更新状态

### 3. 使用自定义命令

```
/workflow:status      # 查看进度和验收标准
/workflow:continue   # 继续下一个任务
/git:commit         # 提交代码（自动检查验收标准）
/test:run           # 运行测试（更新验收标准状态）
```

## 最佳实践

### 1. 定义清晰的验收标准

✅ 好的验收标准：
- "所有单元测试通过"
- "代码审查通过"
- "API 响应时间 < 200ms"
- "文档包含使用示例"

❌ 不好的验收标准：
- "代码质量好"（不可验证）
- "功能完成"（太模糊）

### 2. 合理分配角色

- PM 负责需求和优先级
- Developer 负责实现和代码审查
- Tester 负责测试和质量保证
- Designer 负责 UI/UX 设计

### 3. 利用 Skills

- 使用 `product-manager-toolkit` 进行需求分析
- 使用 `architecture-review` 进行架构设计
- 使用 `test:run` 自动运行测试
- 使用 `git:commit` 和 `git:pr` 管理代码

### 4. 设置合理的依赖关系

```
需求分析 → 架构设计 → 开发 → 测试 → 部署
```

## 总结

通过整合 Skills、多角色协作和验收标准，工作流系统可以：

1. **提高效率** - 自动调用专业 skills
2. **明确分工** - 清晰的角色和责任
3. **保证质量** - 可验证的完成标准
4. **促进协作** - 依赖关系和审查机制

这使得 Claude Code 可以更好地支持团队协作和复杂项目开发。
