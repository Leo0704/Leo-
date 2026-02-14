#!/usr/bin/env python3
"""
创建增强工作流示例项目
演示 Skills、多角色协作和验收标准的使用
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.tasks import TaskManager


def create_enhanced_example():
    """创建增强工作流示例"""

    # 创建示例项目目录
    example_dir = project_root / "examples" / "enhanced-workflow"
    workflow_dir = example_dir / ".workflow"
    workflow_dir.mkdir(parents=True, exist_ok=True)

    # 初始化任务管理器
    manager = TaskManager(workflow_dir)

    print("🚀 创建增强工作流示例项目...")
    print()

    # 1. PM 任务：产品需求
    print("📋 添加 PM 任务...")
    manager.add_task(
        title="编写用户认证功能 PRD",
        description="定义用户认证的需求、用户故事和成功指标",
        priority=1,
        role="PM",
        assignee="Alice (Product Manager)",
        skill="product-manager-toolkit",
        steps=[
            "定义用户故事",
            "完成 RICE 优先级评分",
            "定义成功指标和 KPI"
        ],
        acceptance_criteria=[
            "PRD 包含至少 3 个用户故事",
            "完成 RICE 评分（Reach, Impact, Confidence, Effort）",
            "定义了可衡量的成功指标",
            "团队评审通过"
        ]
    )

    # 2. 架构设计任务
    print("🏗️  添加架构设计任务...")
    manager.add_task(
        title="设计认证系统架构",
        description="设计用户认证系统的技术架构和数据模型",
        priority=2,
        role="Developer",
        assignee="Bob (Tech Lead)",
        dependencies=["task-001"],
        skill="architecture-review",
        reviewers=["Charlie (Senior Dev)", "Alice (PM)"],
        steps=[
            "选择认证方案（JWT vs Session）",
            "设计数据库模型",
            "定义 API 接口",
            "评估安全风险"
        ],
        acceptance_criteria=[
            "选择并文档化认证方案",
            "数据库模型设计完成",
            "API 接口定义完成",
            "安全审查通过",
            "架构评审通过"
        ]
    )

    # 3. 后端开发任务
    print("💻 添加后端开发任务...")
    manager.add_task(
        title="实现用户注册和登录 API",
        description="实现用户注册、登录、登出的后端 API",
        priority=3,
        role="Developer",
        assignee="Bob (Backend Dev)",
        dependencies=["task-002"],
        reviewers=["Charlie (Senior Dev)"],
        steps=[
            "实现用户注册接口",
            "实现登录接口（JWT）",
            "实现登出接口",
            "添加密码加密",
            "编写单元测试"
        ],
        acceptance_criteria=[
            "注册接口实现并测试通过",
            "登录接口实现并测试通过",
            "密码使用 bcrypt 加密",
            "单元测试覆盖率 > 80%",
            "代码审查通过",
            "API 文档更新"
        ]
    )

    # 4. 前端开发任务
    print("🎨 添加前端开发任务...")
    manager.add_task(
        title="实现登录和注册页面",
        description="实现用户登录和注册的前端界面",
        priority=4,
        role="Developer",
        assignee="Eve (Frontend Dev)",
        dependencies=["task-002"],
        reviewers=["Frank (Designer)", "Charlie (Senior Dev)"],
        steps=[
            "设计登录表单",
            "设计注册表单",
            "实现表单验证",
            "集成后端 API",
            "添加错误处理"
        ],
        acceptance_criteria=[
            "登录页面实现完成",
            "注册页面实现完成",
            "表单验证正常工作",
            "错误提示友好",
            "UI 审查通过",
            "代码审查通过"
        ]
    )

    # 5. 集成测试任务
    print("🧪 添加测试任务...")
    manager.add_task(
        title="编写认证功能集成测试",
        description="编写和执行用户认证功能的集成测试",
        priority=5,
        role="Tester",
        assignee="David (QA Engineer)",
        dependencies=["task-003", "task-004"],
        skill="test:run",
        steps=[
            "编写注册流程测试",
            "编写登录流程测试",
            "编写错误场景测试",
            "执行性能测试"
        ],
        acceptance_criteria=[
            "覆盖所有正常用户场景",
            "覆盖所有错误场景",
            "测试通过率 100%",
            "API 响应时间 < 200ms",
            "测试报告完成"
        ]
    )

    # 6. 安全审查任务
    print("🔒 添加安全审查任务...")
    manager.add_task(
        title="安全审查和渗透测试",
        description="对认证系统进行安全审查和渗透测试",
        priority=6,
        role="Reviewer",
        assignee="Grace (Security Engineer)",
        dependencies=["task-005"],
        steps=[
            "检查 SQL 注入风险",
            "检查 XSS 风险",
            "检查密码存储安全",
            "检查 JWT 安全配置",
            "执行渗透测试"
        ],
        acceptance_criteria=[
            "无 SQL 注入漏洞",
            "无 XSS 漏洞",
            "密码安全存储",
            "JWT 配置安全",
            "渗透测试通过",
            "安全报告完成"
        ]
    )

    # 7. 文档任务
    print("📚 添加文档任务...")
    manager.add_task(
        title="更新 API 文档和用户指南",
        description="更新认证相关的 API 文档和用户使用指南",
        priority=7,
        role="Developer",
        assignee="Bob (Tech Lead)",
        dependencies=["task-006"],
        steps=[
            "更新 API 文档",
            "编写用户指南",
            "添加代码示例",
            "更新 README"
        ],
        acceptance_criteria=[
            "API 文档完整准确",
            "包含请求/响应示例",
            "用户指南清晰易懂",
            "代码示例可运行",
            "文档审查通过"
        ]
    )

    # 8. 部署任务
    print("🚀 添加部署任务...")
    manager.add_task(
        title="部署到生产环境",
        description="将认证功能部署到生产环境",
        priority=8,
        role="Developer",
        assignee="Bob (Tech Lead)",
        dependencies=["task-007"],
        steps=[
            "准备部署脚本",
            "配置环境变量",
            "执行数据库迁移",
            "部署到生产环境",
            "验证功能正常"
        ],
        acceptance_criteria=[
            "部署脚本测试通过",
            "环境变量配置正确",
            "数据库迁移成功",
            "生产环境功能正常",
            "监控和日志配置完成"
        ]
    )

    print()
    print("✅ 示例项目创建完成！")
    print()

    # 打印摘要
    manager.print_summary()

    # 创建 README
    readme_content = """# 增强工作流示例项目

这是一个演示增强工作流特性的示例项目，展示了如何使用：
- Skills 集成
- 多角色协作
- 验收标准

## 项目目标

实现一个完整的用户认证系统，包括：
- 用户注册
- 用户登录
- JWT 认证
- 安全审查
- 完整文档

## 团队角色

- **Alice** - Product Manager (PM)
- **Bob** - Tech Lead / Backend Developer
- **Eve** - Frontend Developer
- **David** - QA Engineer
- **Grace** - Security Engineer
- **Charlie** - Senior Developer (Reviewer)
- **Frank** - Designer (Reviewer)

## 工作流程

```
1. PM 编写 PRD (Alice)
   ↓
2. 架构设计 (Bob) → 审查 (Charlie, Alice)
   ↓
3. 后端开发 (Bob) → 审查 (Charlie)
   ↓
4. 前端开发 (Eve) → 审查 (Frank, Charlie)
   ↓
5. 集成测试 (David)
   ↓
6. 安全审查 (Grace)
   ↓
7. 文档更新 (Bob)
   ↓
8. 部署上线 (Bob)
```

## 使用方法

### 在 Claude Code 中继续开发

```
继续开发
```

### 查看进度

```
/workflow:status
```

### 查看当前任务

```
python tools/view_progress.py
```

## Skills 使用

- `product-manager-toolkit` - 用于 PRD 编写和优先级评估
- `architecture-review` - 用于架构设计和审查
- `test:run` - 用于自动化测试
- `git:commit` - 用于代码提交
- `git:pr` - 用于创建 PR

## 验收标准示例

每个任务都有明确的验收标准，例如：

**后端开发任务的验收标准：**
- ✅ 注册接口实现并测试通过
- ✅ 登录接口实现并测试通过
- ✅ 密码使用 bcrypt 加密
- ✅ 单元测试覆盖率 > 80%
- ✅ 代码审查通过
- ✅ API 文档更新

## 多角色协作

任务会自动分配给对应角色：
- PM 负责需求和优先级
- Developer 负责实现
- Tester 负责测试
- Reviewer 负责审查

## 下一步

1. 运行 `python tools/view_progress.py` 查看详细进度
2. 在 Claude Code 中输入 `继续开发` 开始工作
3. 使用 `/workflow:status` 随时查看状态
"""

    readme_file = example_dir / "README.md"
    readme_file.write_text(readme_content, encoding="utf-8")

    print(f"\n📄 README 已创建: {readme_file}")
    print(f"\n💡 提示: cd {example_dir} && claude")
    print("   然后输入 '继续开发' 开始工作")


if __name__ == "__main__":
    create_enhanced_example()
