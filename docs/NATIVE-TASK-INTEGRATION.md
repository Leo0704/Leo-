# 原生 Task 集成方案

## 设计理念

**保留独特价值，依赖原生能力**

保留你的工作流的核心价值：
- ✅ 自动验收机制（acceptance_criteria）
- ✅ 文件持久化（跨会话/跨机器）
- ✅ SessionStart Hook（自动显示进度）

依赖 Claude Code 原生能力：
- ✅ TaskCreate/TaskUpdate/TaskList（任务管理）
- ✅ blocks/blockedBy（依赖管理）
- ✅ Task 工具（并行执行）

---

## 核心架构

```
┌─────────────────────────────────────────────────────┐
│                  用户层                              │
│  /workflow:task     /workflow:verify   /workflow:commit│
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│              原生 Task 系统 (Claude Code)             │
│  TaskCreate → TaskUpdate → TaskList                 │
│  ~/.claude/tasks/{session}/                          │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│              验收增强层 (你的工作流)                  │
│  - 同步 Hook: 监听原生 Task 变化                     │
│  - 验收检查: acceptance_criteria 自动验证             │
│  - 文件持久化: .workflow/state.json                 │
└─────────────────────────────────────────────────────┘
```

---

## 文件结构（简化版）

```
.workflow/
├── config.json              # 配置文件
├── criteria.json            # 验收标准映射（任务ID → 验收标准）
└── state.json              # 持久化状态（自动生成）

.claude/
├── hooks.py                # 同步 Hook（监听原生 Task → 同步到文件）
├── commands/
│   ├── workflow/
│   │   ├── task.md         # 创建任务（包装 TaskCreate + 验收标准）
│   │   ├── verify.md      # 验收检查（核心功能）
│   │   └── status.md      # 状态显示（简化版）
│   └── git/
│       └── commit.md       # 保留
```

---

## 核心文件设计

### 1. `.workflow/config.json`

```json
{
  "auto_verify_on_complete": true,
  "persist_native_tasks": true,
  "show_on_session_start": true,
  "verify_commands": {
    "test": "/test:run",
    "lint": "npm run lint",
    "build": "npm run build"
  }
}
```

### 2. `.workflow/criteria.json`

```json
{
  "task-001": {
    "acceptance_criteria": [
      {"criterion": "测试通过", "type": "auto", "verify": "pytest tests/ -q", "passed": false},
      {"criterion": "代码审查", "type": "manual", "passed": false}
    ]
  },
  "task-002": {
    "acceptance_criteria": [
      {"criterion": "文档完整", "type": "manual", "passed": false}
    ]
  }
}
```

**为什么分离？**
- 原生 Task 系统管理任务状态、依赖
- 你的系统只管理验收标准
- 通过 taskID 关联

### 3. `.claude/hooks.py`（重写）

```python
#!/usr/bin/env python3
"""
Task Sync Hook - 同步原生 Task 到文件

功能：
1. SessionStart: 读取 state.json，显示进度
2. PreResponse: 读取原生 Task，同步到 state.json（双向同步）
3. PostResponse: 检查 Task 变化，更新 state.json
"""

import json
from pathlib import Path
from typing import Dict, Any

def load_native_tasks() -> Dict[str, Any]:
    """读取 Claude Code 原生 Task 状态"""
    task_dir = Path.home() / ".claude" / "tasks"
    # 实现细节：读取最新 session 的任务
    pass

def sync_to_file(native_tasks: Dict[str, Any]) -> None:
    """将原生 Task 同步到 .workflow/state.json"""
    workflow_dir = Path.cwd() / ".workflow"
    state_file = workflow_dir / "state.json"

    # 读取现有验收标准
    criteria_file = workflow_dir / "criteria.json"
    criteria = json.loads(criteria_file.read_text()) if criteria_file.exists() else {}

    # 合并：原生任务状态 + 验收标准
    state = {
        "tasks": [],
        "last_sync": "2026-02-14T13:37:00Z"
    }

    for task_id, task_data in native_tasks.items():
        task_state = {
            "id": task_id,
            "subject": task_data.get("subject"),
            "status": task_data.get("status"),
            "acceptance_criteria": criteria.get(task_id, {}).get("acceptance_criteria", [])
        }
        state["tasks"].append(task_state)

    state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False))

def show_progress():
    """显示当前进度"""
    workflow_dir = Path.cwd() / ".workflow"
    state_file = workflow_dir / "state.json"

    if not state_file.exists():
        return

    state = json.loads(state_file.read_text())
    tasks = state.get("tasks", [])
    total = len(tasks)
    completed = sum(1 for t in tasks if t["status"] == "completed")

    print(f"\n{'='*50}")
    print(f"  目标驱动工作流")
    print(f"{'='*50}")
    print(f"\n  任务: {completed}/{total}")
    print(f"\n{'='*50}\n")

def main():
    show_progress()
    sync_to_file(load_native_tasks())

if __name__ == "__main__":
    main()
```

---

## 命令重写

### /workflow:task.md（20行）

```markdown
---
description: 创建任务并设置验收标准
Argument-hint: [任务标题]
---

# 创建任务

## 1. 创建原生 Task
使用 TaskCreate 工具创建任务，从 $ARGUMENTS 获取标题。

## 2. 设置验收标准
询问用户验收标准，保存到 .workflow/criteria.json

示例：
```json
{
  "task-001": {
    "acceptance_criteria": [
      {"criterion": "测试通过", "type": "auto", "verify": "pytest tests/ -q", "passed": false}
    ]
  }
}
```

## 3. 返回任务 ID
```
✅ 任务创建成功: task-001
验收标准: 1 项自动验证, 1 项手动验证
```
```

### /workflow:verify.md（核心功能，40行）

```markdown
---
description: 检查任务验收标准
Argument-hint: [任务ID，可选]
---

# 验收检查

## 1. 确定任务
- 如果提供 $ARGUMENTS，验证指定任务
- 如果未提供，验证当前 in_progress 任务

## 2. 读取验收标准
从 .workflow/criteria.json 读取任务的 acceptance_criteria

## 3. 执行验证

### 自动验证 (type: auto)
运行 verify 命令，成功则标记 passed: true

### 手动验证 (type: manual)
询问用户："是否满足：{criterion}?"

## 4. 更新状态

### 全部通过
- 更新 .workflow/criteria.json (passed: true)
- 使用 TaskUpdate 标记任务为 completed
- 输出：✅ 验收通过，任务完成

### 有失败项
- 保持 in_progress 状态
- 输出：❌ 验收失败，需修复：[失败项列表]

## 5. 同步文件
自动调用 hooks.py 同步到 .workflow/state.json
```

### /workflow:status.md（15行）

```markdown
---
description: 查看工作流状态
---

# 显示状态

## 1. 读取原生任务
使用 TaskList 工具获取当前任务列表

## 2. 读取验收标准
读取 .workflow/criteria.json

## 3. 显示

```
当前任务: [task-003] 实现用户认证
状态: in_progress
进度: 1/2 验收标准通过
  ✅ 单元测试通过
  ❌ 集成测试通过

阻塞:
- task-004: 编写文档（等待当前任务完成）

被阻塞:
- task-005: 部署到生产环境
```
```

---

## 工作流示例

### 创建任务

```bash
用户: /workflow:task 实现用户登录功能

Claude:
1. TaskCreate: 创建任务（返回 task-003）
2. 询问: 验收标准？
   用户: 1. 测试通过 2. 安全审查
3. 保存到 .workflow/criteria.json

输出:
✅ 任务创建成功: task-003
验收标准:
  - auto: pytest tests/auth.test.py (自动验证)
  - manual: 安全审查 (手动确认)
```

### 验收检查

```bash
用户: /workflow:verify

Claude:
1. 读取 task-003 的验收标准
2. 执行 pytest tests/auth.test.py
   - 成功 → passed: true
3. 询问: 安全审查是否通过？
   用户: 是 → passed: true
4. TaskUpdate: task-003 → completed
5. hooks.py: 同步到 .workflow/state.json

输出:
✅ task-003 验收通过
  ✅ 测试通过 (auto)
  ✅ 安全审查 (manual)
任务已标记为完成
```

### 并行执行（依赖原生）

```bash
用户: 同时实现前端和后端 API

Claude:
1. TaskCreate: task-004 (前端)
2. TaskCreate: task-005 (后端)
3. 检测到无依赖关系
4. 使用 Task 工具创建2个后台代理并行执行
5. 各自完成后，调用 /workflow:verify 验收
```

---

## 优势对比

| 功能 | 旧方案 | 新方案（集成原生） |
|-----|--------|------------------|
| 任务管理 | 自定义 tasks.json | ✅ 原生 Task 系统 |
| 依赖管理 | 自定义 dependencies | ✅ 原生 blocks/blockedBy |
| 验收标准 | acceptance_criteria | ✅ 保留（核心价值） |
| 文件持久化 | tasks.json | ✅ state.json（简化） |
| 并行执行 | 手动分析依赖 | ✅ 原生 Task 工具 |
| 代码量 | 348 行 continue.md | 40 行 verify.md |
| 维护成本 | 高 | 低 |

---

## 迁移步骤

### Phase 1: 保留旧功能
1. 保留旧的 tasks.json 作为备份
2. 新增 criteria.json

### Phase 2: 新旧共存
1. 新任务用 /workflow:task 创建
2. 旧任务手动迁移验收标准到 criteria.json

### Phase 3: 完全迁移
1. 删除旧的 tasks.json 管理逻辑
2. 简化 hooks.py

---

## 核心代码量对比

| 文件 | 旧方案 | 新方案 | 减少 |
|-----|--------|--------|------|
| workflow/continue.md | 348 行 | - | -348 |
| workflow/verify.md | - | 40 行 | +40 |
| workflow/task.md | - | 20 行 | +20 |
| hooks.py | 93 行 | 80 行 | -13 |
| tasks.json (格式) | 复杂 | criteria.json 简单 | - |
| **总计** | **441 行** | **140 行** | **-68%** |

---

## 总结

**核心改变**：
- ❌ 不再管理任务状态（交给原生）
- ❌ 不再管理依赖关系（交给原生）
- ❌ 不再手动分析并行（交给原生）
- ✅ **只专注验收标准**（核心价值）
- ✅ **只专注文件持久化**（跨会话）
- ✅ **只专注进度显示**（用户体验）

**结果**：
- 代码量减少 68%
- 维护成本降低
- 功能更强大（依赖原生并行、依赖管理）
- 保留独特价值（自动验收）
