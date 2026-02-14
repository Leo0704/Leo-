# 原生 Task 集成方案 - 完整实现

## 📊 方案对比

### 架构对比

| 层级 | 旧方案 | 新方案（集成原生） |
|-----|--------|------------------|
| **任务管理** | 自定义 tasks.json | ✅ 原生 Task 系统 |
| **依赖管理** | dependencies 字段 | ✅ blocks/blockedBy |
| **并行执行** | 手动分析依赖关系 | ✅ Task 工具（官方） |
| **验收标准** | acceptance_criteria | ✅ 保留（核心价值） |
| **文件持久化** | tasks.json | ✅ state.json（同步） |
| **进度显示** | SessionStart Hook | ✅ 保留并增强 |
| **创建命令** | workflow:add-task | ✅ workflow:task |
| **验收命令** | workflow:continue (348行) | ✅ workflow:verify (40行) |

### 代码量对比

```
旧方案: 441 行
├── workflow/continue.md  348 行
└── hooks.py              93 行

新方案: 140 行 (-68%)
├── workflow/task.md      20 行 (新增)
├── workflow/verify.md    40 行 (新增)
└── hooks.py             80 行 (重写)
```

### 文件结构对比

```
旧方案:
.workflow/
└── tasks.json          # 任务 + 验收标准 + 依赖（混在一起）

.claude/
├── hooks.py           # 读取 tasks.json
└── commands/
    └── workflow/
        └── continue.md  # 348 行复杂逻辑

新方案:
.workflow/
├── config.json        # 配置文件（新增）
├── criteria.json      # 验收标准（独立）
└── state.json        # 状态快照（自动生成）

.claude/
├── hooks.py          # 同步原生 Task（重写）
└── commands/
    └── workflow/
        ├── task.md    # 创建任务（新增）
        └── verify.md  # 验收检查（新增）
```

---

## 🎯 核心价值保留

### ✅ 保留的功能

1. **自动验收机制**
   ```json
   {"criterion": "测试通过", "type": "auto", "verify": "pytest", "passed": false}
   ```

2. **文件持久化**
   - state.json 可版本控制
   - 跨会话、跨机器共享

3. **自动进度显示**
   - SessionStart Hook 显示当前任务
   - 显示验收标准进度

### ❌ 移除的功能（交给原生）

1. **任务状态管理** → TaskUpdate
2. **依赖关系管理** → blocks/blockedBy
3. **并行执行逻辑** → Task 工具
4. **复杂的任务分发** → 原生 Task 系统

---

## 📝 使用示例

### 创建任务

```bash
用户: /workflow:task 实现用户认证

Claude 执行:
1. TaskCreate(subject="实现用户认证")
   → 返回: task-001

2. 询问验收标准:
   "请设置验收标准:
    - auto: 测试通过
    - manual: 代码审查"

3. 保存到 .workflow/criteria.json:
   {
     "task-001": {
       "acceptance_criteria": [
         {"criterion": "测试通过", "type": "auto", "verify": "pytest tests/auth.test.py", "passed": false},
         {"criterion": "代码审查", "type": "manual", "passed": false}
       ]
     }
   }
```

### 验收检查

```bash
用户: /workflow:verify

Claude 执行:
1. 读取当前 in_progress 任务 → task-001

2. 读取验收标准 → 2 条

3. 执行验证:
   - auto: 运行 pytest tests/auth.test.py
     → 成功 → passed: true
   - manual: 询问用户
     → 用户确认 → passed: true

4. 全部通过 → TaskUpdate(status="completed")

5. 输出:
   "✅ task-001 验收通过
     ✅ 测试通过 (auto)
     ✅ 代码审查 (manual)
    任务已标记为完成"
```

---

## 🔄 迁移步骤

### Step 1: 备份旧数据

```bash
cp .workflow/tasks.json .workflow/tasks.json.backup
```

### Step 2: 提取验收标准

从旧的 tasks.json 提取 `acceptance_criteria`，创建 `criteria.json`：

```python
# 迁移脚本（可选）
import json

with open(".workflow/tasks.json") as f:
    old_data = json.load(f)

criteria = {}
for task in old_data.get("tasks", []):
    task_id = task["id"]
    criteria[task_id] = {
        "acceptance_criteria": task.get("acceptance_criteria", [])
    }

with open(".workflow/criteria.json", "w") as f:
    json.dump(criteria, f, indent=2, ensure_ascii=False)
```

### Step 3: 重新创建任务

```bash
# 对于每个旧任务
/workflow:task {旧任务的 title}

# 设置验收标准（从 criteria.json 复制）
```

### Step 4: 验证功能

```bash
# 测试验收检查
/workflow:verify

# 测试状态显示
/workflow:status
```

---

## 🎓 最佳实践

### 1. 验收标准设置

**自动验证**（推荐）:
```json
{"criterion": "测试通过", "type": "auto", "verify": "pytest tests/ -q"}
```

**手动验证**（无法自动化时）:
```json
{"criterion": "代码审查", "type": "manual"}
```

### 2. 依赖管理

使用原生的 blocks/blockedBy：

```python
# 创建任务后
TaskUpdate(taskId="2", addBlockedBy=["1"])

# 查看依赖
/workflow:status
```

### 3. 并行执行

原生 Task 工具自动处理：

```bash
用户: 同时实现前端和后端

Claude:
1. TaskCreate: task-003 (前端)
2. TaskCreate: task-004 (后端)
3. 检测到无依赖 → 使用 Task 工具创建2个后台代理并行执行
4. 各自完成后 → /workflow:verify 验收
```

---

## ❓ FAQ

### Q: 为什么要迁移？

**A**:
- 代码量减少 68%（441 行 → 140 行）
- 更强大的功能（并行、依赖管理）
- 官方支持，持续更新
- 维护成本更低

### Q: 旧的 tasks.json 还能用吗？

**A**:
- 可以继续使用（向后兼容）
- 但建议逐步迁移到新方案
- 新任务用 `/workflow:task` 创建

### Q: 如何跨会话保持任务？

**A**: 新方案已解决：
- SessionStart Hook 自动同步
- state.json 可版本控制
- criteria.json 保存验收标准

### Q: 验收标准会丢失吗？

**A**: 不会：
- 保存在 criteria.json（文件）
- 与任务管理分离
- 可手动维护或通过命令更新

---

## 📚 相关文档

- [快速开始](./QUICKSTART-NATIVE.md) - 5 分钟上手
- [完整设计文档](./NATIVE-TASK-INTEGRATION.md) - 架构设计
- [配置文件说明](../config.json) - config.json 格式

---

## 🚀 下一步

1. ✅ 阅读 [快速开始](./QUICKSTART-NATIVE.md)
2. ✅ 尝试创建任务: `/workflow:task 测试`
3. ✅ 设置验收标准
4. ✅ 完成后验证: `/workflow:verify`

**欢迎反馈！** 如果遇到问题，请创建 issue。
