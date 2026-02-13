# Plan Mode 使用指南

## 什么是 Plan Mode

Plan Mode 是 Claude Code 的一种权限模式，在此模式下：
- Claude 会先分析需求并制定计划
- 等待用户确认后再执行
- 适合复杂任务和关键操作

## 启动方式

### 命令行
```bash
# 从 Plan Mode 开始会话
claude --permission-mode plan

# 在当前会话切换到 Plan Mode
# Mac: Shift+Tab
# Windows/Linux: Alt+T
```

### 在工作流中使用

对于复杂任务，建议使用 Plan Mode：

```
用户: 添加用户认证系统

Claude (Plan Mode):
我来分析一下需求...

## 计划

### 1. 创建用户模型 (10分钟)
- 添加 User 数据类
- 实现密码哈希

### 2. 创建登录API (15分钟)
- 添加 /login 路由
- 实现 JWT 认证

### 3. 创建注册API (10分钟)
- 添加 /register 路由
- 添加邮箱验证

### 4. 添加测试 (15分钟)
- 单元测试
- 集成测试

预计总时间: 50分钟

是否同意此计划？
```

## 工作流集成

### 复杂任务判断标准

使用 Plan Mode 当任务：
- 涉及多个模块/文件
- 需要数据库变更
- 涉及 API 设计
- 可能影响现有功能
- 估计超过 30 分钟

### 在 tasks.json 中标记

```json
{
  "id": "task-005",
  "title": "实现用户认证",
  "requires_plan": true,
  "estimated_time": "50分钟"
}
```

## 最佳实践

1. **先思考再行动** - Plan Mode 强制先规划
2. **小步迭代** - 将大任务拆分为小任务
3. **明确时间** - 每个子任务设定时间限制
4. **记录决策** - 计划中的关键决策写入 decisions.md

## 配置文件

可在 `.claude/settings.json` 中设置默认模式：

```json
{
  "permissions": {
    "defaultMode": "plan"
  }
}
```

可用模式：
- `normal` - 正常模式，每次操作需确认
- `auto-accept` - 自动接受编辑
- `plan` - 计划模式，先规划再执行
