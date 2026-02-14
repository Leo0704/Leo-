# 快速开始（原生 Task 集成版）

## 5 分钟上手

### 1. 创建任务

```bash
/workflow:task 实现用户登录功能
```

Claude 会：
1. 使用原生 TaskCreate 创建任务
2. 询问你验收标准

示例对话：
```
Claude: 任务已创建。请设置验收标准：
- auto: 测试通过 (pytest tests/auth.test.py)
- manual: 代码审查

✅ 任务创建成功: task-003
```

### 2. 开发功能

直接让 Claude 开始开发：
```
帮我实现用户登录功能，使用 JWT
```

### 3. 验收检查

```bash
/workflow:verify
```

Claude 会：
1. 运行自动验证命令（测试、构建等）
2. 询问手动验证项
3. 全部通过后，自动标记任务完成

示例输出：
```
✅ task-003 验收通过
  ✅ 测试通过 (auto)
  ✅ 代码审查 (manual)
任务已标记为完成
```

---

## 核心命令

| 命令 | 用途 | 示例 |
|-----|------|------|
| `/workflow:task` | 创建任务 + 验收标准 | `/workflow:task 实现API` |
| `/workflow:verify` | 验收检查 | `/workflow:verify task-003` |
| `/workflow:status` | 查看状态 | `/workflow:status` |

---

## 与旧方案的区别

| 功能 | 旧方案 | 新方案（集成原生） |
|-----|--------|------------------|
| 创建任务 | 编辑 tasks.json | `/workflow:task` （调用原生） |
| 任务状态 | 自定义管理 | **原生 Task 系统** |
| 依赖管理 | dependencies | **blocks/blockedBy** |
| 验收标准 | acceptance_criteria | **保留** |
| 并行执行 | 手动分析 | **原生 Task 工具** |
| 代码量 | 441 行 | 140 行（-68%） |

---

## 迁移指南

### 从旧 tasks.json 迁移

**旧格式**：
```json
{
  "tasks": [{
    "id": "task-001",
    "title": "实现登录",
    "status": "pending",
    "acceptance_criteria": [...]
  }]
}
```

**新方案**：
```bash
# 1. 使用原生创建任务
/workflow:task 实现登录

# 2. 手动复制验收标准到 .workflow/criteria.json
# {
#   "task-001": {
#     "acceptance_criteria": [...]
#   }
# }
```

---

## 验收标准示例

### 自动验证

```json
{
  "criterion": "测试通过",
  "type": "auto",
  "verify": "pytest tests/ -q",
  "passed": false
}
```

### 手动验证

```json
{
  "criterion": "代码审查通过",
  "type": "manual",
  "passed": false
}
```

---

## 进阶：使用原生依赖管理

### 创建有依赖的任务

```bash
# 任务 1：设计数据库
/workflow:task 设计数据库表结构

# 任务 2：实现 API（依赖任务 1）
/workflow:task 实现 REST API

# 使用原生 TaskUpdate 设置依赖
TaskUpdate(taskId="2", addBlockedBy=["1"])
```

### 查看依赖关系

```bash
/workflow:status
```

输出：
```
当前任务: [2] 实现 REST API
等待: 1 (设计数据库表结构)
```

---

## 文件结构

```
.workflow/
├── config.json          # 配置文件（已生成）
├── criteria.json        # 验收标准（手动维护）
└── state.json          # 状态快照（自动生成）
```

**重要**：
- `criteria.json` 是你唯一需要手动维护的文件
- `state.json` 由 hooks.py 自动生成（不要手动编辑）
- 任务管理使用原生 TaskCreate/TaskUpdate

---

## 常见问题

### Q: 为什么要用原生 Task 系统？

A:
- ✅ 更强大的并行执行（Task 工具）
- ✅ 更好的依赖管理（blocks/blockedBy）
- ✅ 官方支持，持续更新
- ✅ 你只需要专注验收标准（独特价值）

### Q: 旧的 tasks.json 还能用吗？

A: 可以，但建议迁移：
- 旧文件仍可读取
- 新任务用 `/workflow:task` 创建
- 逐步迁移验收标准到 `criteria.json`

### Q: 如何跨会话保持任务？

A: 新方案已解决：
- SessionStart Hook 自动同步原生 Task → state.json
- state.json 可版本控制，跨机器共享
- criteria.json 保存验收标准

---

## 对比示例

### 旧方案：创建任务

```bash
用户: /workflow:add-task

Claude:
1. 编辑 tasks.json
2. 添加新任务
3. 手动检查 dependencies
4. 手动更新 status
（耗时：10+ 步操作）
```

### 新方案：创建任务

```bash
用户: /workflow:task 实现登录

Claude:
1. TaskCreate(subject="实现登录")
2. 询问验收标准
3. 保存到 criteria.json
（耗时：3 步操作）
```

---

## 下一步

1. ✅ 尝试创建一个任务：`/workflow:task 测试`
2. ✅ 设置验收标准
3. ✅ 完成功能后运行：`/workflow:verify`
4. ✅ 查看状态：`/workflow:status`

**就这么简单！**
