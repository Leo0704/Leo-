---
description: 创建任务并设置验收标准
Argument-hint: [任务标题]
---

# 创建任务（集成原生 Task）

## 第一步：使用原生 TaskCreate

根据 $ARGUMENTS 提供的任务标题，使用 **TaskCreate 工具** 创建任务。

参数设置：
- `subject`: 任务标题（从 $ARGUMENTS 获取）
- `description`: 询问用户详细描述
- `activeForm`: 询问用户进行时态描述（可选，默认 "Working on..."）

## 第二步：设置验收标准

任务创建后，询问用户需要哪些验收标准：

**提示语**：
```
任务已创建。请设置验收标准：

支持两种类型：
1. 自动验证 (auto) - 自动运行命令检查
   示例：
   - 测试: pytest tests/ -q
   - 构建: npm run build
   - 语法检查: npm run lint

2. 手动验证 (manual) - 需要你确认
   示例：
   - 代码审查通过
   - 文档完整
   - 设计评审通过

请输入验收标准，格式：
- auto: <描述>
- manual: <描述>
（可以输入多个，输入空行结束）
```

**解析用户输入**，将验收标准保存到 `.workflow/criteria.json`：

```json
{
  "task-001": {
    "acceptance_criteria": [
      {"criterion": "测试通过", "type": "auto", "verify": "pytest tests/ -q", "passed": false},
      {"criterion": "代码审查", "type": "manual", "passed": false}
    ]
  }
}
```

**智能提示**：
- 如果任务包含 "测试"、"test" → 提示 pytest/npm test
- 如果任务包含 "构建"、"build" → 提示 npm run build
- 如果任务包含 "检查"、"lint" → 提示 eslint/pylint

## 第三步：返回结果

```
✅ 任务创建成功: task-003
标题: 实现用户登录功能
验收标准: 2 项
  - auto: 测试通过 (pytest tests/auth.test.py)
  - manual: 代码审查通过

使用 /workflow:verify 验收，或直接开始开发
```
