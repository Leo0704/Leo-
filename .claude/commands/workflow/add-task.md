---
description: 添加新任务到工作流
Argument-hint: <任务标题>
---

# 添加新任务

## 参数

$ARGUMENTS

## 执行

1. 读取当前 `.workflow/tasks.json`
2. 生成新任务 ID（最大 ID + 1）
3. 向用户确认以下信息：
   - 任务描述
   - 执行步骤
   - 依赖关系（是否依赖其他任务）
   - 验收标准（如何判断任务完成）
4. 添加新任务到 tasks.json

## 验收标准格式

每个验收标准是一个对象：

```json
{
  "criterion": "标准描述",
  "type": "auto 或 manual",
  "verify": "当 type=auto 时，用于验证的 shell 命令",
  "passed": false
}
```

- `auto`: 可通过运行命令自动验证（如测试、lint）
- `manual`: 需要用户手动确认（如 UI 审查、文档质量）

## 示例

```json
{
  "id": "task-005",
  "title": "实现用户登录",
  "status": "pending",
  "priority": 5,
  "description": "实现基于 JWT 的用户登录功能",
  "steps": ["创建登录 API", "添加 JWT 生成", "编写测试"],
  "dependencies": ["task-003"],
  "acceptance_criteria": [
    {"criterion": "登录 API 返回 JWT", "type": "auto", "verify": "pytest tests/test_auth.py -q", "passed": false},
    {"criterion": "密码使用 bcrypt 加密", "type": "manual", "passed": false}
  ],
  "context": "关注安全性，参考 OWASP 认证最佳实践"
}
```

## 输出

报告新添加的任务 ID、标题和验收标准数量。
