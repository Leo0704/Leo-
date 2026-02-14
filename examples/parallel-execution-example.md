# 并行执行示例

## 场景：电商网站开发

### 任务列表

```json
{
  "tasks": [
    {
      "id": "task-001",
      "title": "设计数据库",
      "status": "completed",
      "dependencies": []
    },
    {
      "id": "task-002",
      "title": "设计 API 接口",
      "status": "completed",
      "dependencies": []
    },
    {
      "id": "task-003",
      "title": "实现后端 API",
      "status": "pending",
      "dependencies": ["task-001", "task-002"],
      "description": "实现用户认证、商品管理等 API 接口",
      "context": "使用 Node.js + Express"
    },
    {
      "id": "task-004",
      "title": "实现前端页面",
      "status": "pending",
      "dependencies": ["task-002"],
      "description": "实现商品列表、详情页、购物车等页面",
      "context": "使用 React + TailwindCSS"
    },
    {
      "id": "task-005",
      "title": "编写 API 测试",
      "status": "pending",
      "dependencies": ["task-001"],
      "description": "为后端 API 编写单元测试",
      "context": "使用 Jest 测试框架"
    },
    {
      "id": "task-006",
      "title": "编写使用文档",
      "status": "pending",
      "dependencies": ["task-002"],
      "description": "编写 API 使用文档和前端组件文档",
      "context": "使用 Markdown 格式"
    }
  ]
}
```

## 依赖关系图

```
task-001 (数据库设计) ✓ 完成
     ↓
     ├─→ task-003 (后端 API) [等待: task-001 + task-002]
     └─→ task-005 (API 测试) [等待: task-001]

task-002 (API 设计) ✓ 完成
     ↓
     ├─→ task-003 (后端 API) [等待: task-001 + task-002]
     ├─→ task-004 (前端页面) [等待: task-002]
     └─→ task-006 (使用文档) [等待: task-002]

当前可执行任务分析：
- task-003: 依赖 [task-001✓, task-002✓] → ✅ 可执行
- task-004: 依赖 [task-002✓] → ✅ 可执行
- task-005: 依赖 [task-001✓] → ✅ 可执行
- task-006: 依赖 [task-002✓] → ✅ 可执行

独立性分析：
- task-004: 只依赖 task-002，与 task-005/task-006 无冲突 → 可并行
- task-005: 只依赖 task-001，与 task-004/task-006 无冲突 → 可并行
- task-006: 只依赖 task-002，与 task-004/task-005 无冲突 → 可并行
- task-003: 依赖 task-001 和 task-002，且 task-004/task-006 都在用 API 设计
  → 建议：task-004/task-005/task-006 并行，task-003 最后执行
```

## 并行执行策略

### 执行计划

**组 1 - 并行执行（3 个任务同时进行）：**

```
task-004: 实现前端页面
  ├─ 技能搜索：npx skills find "react frontend"
  ├─ 安装：npx skills add anthropics/skills@frontend-design -g -y
  └─ 使用：frontend-design 技能

task-005: 编写 API 测试
  ├─ 技能搜索：npx skills find "jest testing"
  ├─ 安装：npx skills add wshobson/agents@javascript-testing-patterns -g -y
  └─ 使用：javascript-testing-patterns 技能

task-006: 编写使用文档
  ├─ 使用内置技能：doc-coauthoring
  └─ 直接调用，无需搜索
```

**执行命令：**
```
1. Task tool (agent-1): 执行 task-004 [后台运行]
2. Task tool (agent-2): 执行 task-005 [后台运行]
3. Task tool (agent-3): 执行 task-006 [后台运行]
   ↓
等待所有代理完成...
   ↓
收集结果并验收
```

**组 2 - 串行执行（组 1 完成后）：**
```
task-003: 实现后端 API
  ├─ 技能搜索：npx skills find "nodejs backend api"
  ├─ 选择合适的后端技能
  └─ 单独执行（因为依赖最多，需等待其他任务完成）
```

## 时间对比

### 串行执行（旧方式）
```
task-004: 2小时
task-005: 1小时
task-006: 1小时
task-003: 3小时
────────────────
总计：7小时
```

### 并行执行（新方式）
```
组1 (并行): max(2小时, 1小时, 1小时) = 2小时
组2 (串行): 3小时
────────────────────────────────
总计：5小时（节省 29% 时间）
```

## 并行执行决策流程

```
开始 /workflow:continue
  ↓
第一步：读取状态
  ↓
第二步：分析依赖关系
  ├─ 扫描所有任务的 dependencies 字段
  ├─ 构建依赖图
  └─ 识别可执行任务组
  ↓
第三步：检查独立性
  ├─ task-004 vs task-005: 无共享依赖 ✅ 可并行
  ├─ task-004 vs task-006: 无共享依赖 ✅ 可并行
  └─ task-005 vs task-006: 无共享依赖 ✅ 可并行
  ↓
第四步：选择执行策略
  ├─ 发现 3 个完全独立的任务
  └─ 决定：并行执行
  ↓
第五步：并行执行
  ├─ 为每个任务分配独立代理
  ├─ 每个代理独立选择和使用技能
  └─ 等待所有代理完成
  ↓
第六步：验收
  ├─ 检查 task-004 验收标准
  ├─ 检查 task-005 验收标准
  └─ 检查 task-006 验收标准
  ↓
第七步：更新状态并提交
  └─ /git:commit "feat: 完成前端、测试、文档（并行）"
```

## 关键原则

### ✅ 可以并行的情况

1. **完全无依赖** - 两个任务都 `dependencies: []`
2. **依赖不同源** - task-A 依赖 task-001，task-B 依赖 task-002
3. **依赖已完成** - 依赖的任务都是 `completed` 状态
4. **资源不冲突** - 不会修改同一个文件或资源

### ❌ 不能并行的情况

1. **直接依赖** - task-B 依赖 task-A
2. **间接依赖** - task-A 和 task-B 都依赖 task-C，且 task-C 未完成
3. **输出冲突** - 两个任务都要修改同一个文件
4. **资源竞争** - 两个任务都需要独占资源（如编译服务器）

### ⚠️ 需要谨慎的情况

1. **优先级差异大** - priority 1 的任务应该优先单独执行
2. **资源密集型** - 编译、构建等任务可能需要串行
3. **测试环境共享** - 多个测试任务可能需要串行以避免冲突
4. **依赖复杂** - 需要仔细分析传递性依赖

## 实际使用建议

### 1. 任务设计建议

在设计任务时，尽量让它们**独立可并行**：

```json
// ❌ 不好：过度依赖
{
  "id": "task-A",
  "dependencies": ["task-setup", "task-config", "task-db"]
}

// ✅ 好：最小依赖
{
  "id": "task-A",
  "dependencies": ["task-setup"]  // 只依赖必需的前置任务
}
```

### 2. 优先级设置

```
priority: 1  // 核心功能（应优先）
priority: 2  // 重要功能
priority: 3  // 辅助功能（可并行）
```

### 3. 并行度控制

- 小项目（< 10 个任务）：2-3 个并行
- 中型项目（10-50 个任务）：3-5 个并行
- 大型项目（> 50 个任务）：5-8 个并行

## 总结

并行执行的核心价值：

1. **效率提升** - 通过依赖分析和智能分组，大幅缩短总执行时间
2. **资源利用** - 充分利用多核 CPU 和并发能力
3. **智能决策** - 不是盲目并行，而是基于依赖关系的科学决策
4. **透明可控** - 明确说明哪些任务并行、哪些串行、为什么

记住：并行是为了加速，但正确性第一。如果不确定，优先串行执行。
