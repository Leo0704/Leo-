---
description: 继续工作流开发 - 读取当前状态并继续下一个任务
Argument-hint: [可选：指定任务ID]
---

# 继续工作流开发

## 第一步：读取状态

读取以下文件，理解当前进度：
1. `.workflow/GOAL.md` — 项目的理想状态
2. `.workflow/REALITY.md` — 当前实际状态
3. `.workflow/tasks.json` — 任务列表和验收标准

## 第二步：确定当前任务（支持并行）

### 2.1 分析任务依赖关系

从 tasks.json 中读取所有任务的 `dependencies` 字段，构建依赖图：

**依赖分析规则：**
1. 无依赖的任务（`dependencies: []` 或字段不存在）→ 可立即执行
2. 有依赖的任务 → 必须等待所有依赖任务完成（`status: "completed"`）
3. 同一依赖链的任务 → 必须串行执行
4. 不同依赖链的任务 → 可以并行执行

**示例：**
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
      "title": "设计API",
      "status": "completed",
      "dependencies": []
    },
    {
      "id": "task-003",
      "title": "实现后端",
      "status": "pending",
      "dependencies": ["task-001", "task-002"]  // 等待两个设计完成
    },
    {
      "id": "task-004",
      "title": "编写测试",
      "status": "pending",
      "dependencies": ["task-001"]  // 只等待数据库设计
    }
  ]
}
```

**分析结果：**
- `task-001` 和 `task-002` 可以并行（无依赖）
- `task-003` 等待 `task-001` 和 `task-002` 都完成
- `task-004` 只等待 `task-001`，所以可以和 `task-002` 并行（如果 `task-001` 已完成）

### 2.2 确定执行策略

**情况 A：有 `in_progress` 任务**
- 继续执行该任务
- 检查是否有其他可以并启动的独立任务

**情况 B：指定了任务 ID**
- 直接处理该任务
- 检查是否可以同时启动其他独立任务

**情况 C：寻找下一个任务（智能并行）**

1. 找出所有 `status: "pending"` 的任务
2. 检查每个任务的依赖是否已满足（所有依赖都是 `completed`）
3. **分组**：将满足条件的任务按依赖关系分组
   - 同一组：完全独立的任务，可以并行
   - 不同组：有依赖关系，必须串行
4. **执行优先级**：
   - 优先级（`priority` 数值越小越优先）
   - 如果优先级相同，可以并行执行
5. **决定并行策略**：
   - 如果找到多个完全独立的任务 → 并行执行（使用 Task 工具创建多个后台任务）
   - 如果只有一个可执行任务 → 串行执行

**并行决策示例：**
```
当前状态：
- task-001 (completed): 设计数据库
- task-002 (completed): 设计API
- task-003 (pending): 实现后端，依赖 [task-001, task-002]
- task-004 (pending): 编写测试，依赖 [task-001]
- task-005 (pending): 编写文档，依赖 [task-002]

依赖分析：
- task-003: 等待 task-001 ✓ task-002 ✓ → 可执行
- task-004: 等待 task-001 ✓ → 可执行
- task-005: 等待 task-002 ✓ → 可执行

独立性分析：
- task-003 vs task-004: task-003 依赖 task-002，task-004 不依赖
  → task-004 和 task-005 可以并行（都只依赖各自的任务）
  → task-003 应该最后执行（依赖最多）

并行执行策略：
组1 (并行): [task-004, task-005] - 完全独立
组2 (串行): [task-003] - 等待组1完成后
```

## 第三步：理解任务上下文

读取任务的以下字段：
- `description` 和 `steps` — 任务内容
- `context` — 执行此任务时应采用的视角和关注点
- `acceptance_criteria` — 完成标准（重要！）

## 第四步：智能选择工具（重要！）

**主动分析任务类型**，动态搜索并使用合适的技能包和 MCP 工具：

### 4.1 动态搜索技能（使用 skills.sh 生态系统）

**关键步骤：使用 `npx skills find` 动态搜索**

1. **提取关键词** - 从任务的 `description`、`steps`、`context` 中提取 2-3 个核心关键词
2. **执行搜索** - 运行 `npx skills find <关键词>` 查找相关技能
3. **分析结果** - 从返回的技能列表中选择最合适的（按安装量排序）
4. **安装并使用** - 如果技能未安装，先安装再使用

**示例工作流：**
```
任务："创建响应式登录页面"
↓
提取关键词："响应式"、"登录页面"、"前端"
↓
执行搜索：npx skills find "responsive frontend"
↓
搜索结果：
  - anthropics/skills@frontend-design (67.2K installs)
  - anthropics/claude-code@frontend-design (3.5K installs)
↓
选择：frontend-design（安装量最高）
↓
安装：npx skills add anthropics/skills@frontend-design -g -y
↓
使用：Skill tool with skill="frontend-design"
```

### 4.2 内置技能快捷映射

对于常见任务，优先使用已安装的内置技能（无需搜索）：

| 任务类型 | 内置技能 | 说明 |
|---------|---------|------|
| 测试运行 | `/test:run` | 运行测试并报告结果 |
| 代码提交 | `/git:commit` | 使用 conventional commit 格式 |
| PR 创建 | `/git:pr` | 创建 PR 并推送到远程 |
| 文档协作 | `doc-coauthoring` | 结构化文档编写工作流 |
| Excel 处理 | `xlsx` | 表格文件处理 |
| PDF 处理 | `pdf` | PDF 文件操作 |
| PPT 制作 | `pptx` | 演示文稿处理 |

### 4.3 MCP 工具使用时机

根据任务需求，主动调用 MCP 工具：

| 需求场景 | MCP 工具 | 调用时机 |
|---------|----------|---------|
| 分析截图/设计图 | `mcp__4_5v_mcp__analyze_image` | 任务提到"看这个图"、"分析截图" |
| 执行 Python 代码 | `mcp__ide__executeCode` | 需要运行代码验证逻辑 |
| 检查代码错误 | `mcp__ide__getDiagnostics` | 任务提到"检查错误"、"诊断" |
| 获取网页内容 | `mcp__web_reader__webReader` | 需要读取外部文档或网页 |

### 4.4 执行策略

1. **先查内置** - 检查是否有内置技能可直接使用
2. **再搜外部** - 如果内置技能不匹配，使用 `npx skills find` 搜索
3. **优先级排序** - 按"安装量 → 相关性 → 更新时间"排序
4. **记录决策** - 说明："搜索到 [X] 个技能，选择 [技能名] ([安装量] 安装)"
5. **主动安装** - 需要时自动安装（使用 `-g -y` 参数）

## 第五步：执行任务

1. 将任务状态更新为 `in_progress`

2. **应用第四步选择的工具**
   - 如果是内置技能：直接调用 `Skill` 工具
   - 如果是外部技能：先安装（`npx skills add <skill> -g -y`），再调用
   - 如果是 MCP 工具：在需要时直接调用

3. **实际执行示例**

   **场景A：使用内置技能**
   ```
   任务：测试用户认证功能
   ↓
   检测：测试任务 → 内置技能 /test:run
   ↓
   调用：/test:run tests/auth.test.py
   ```

   **场景B：动态搜索并使用外部技能**
   ```
   任务：创建现代化的登录界面
   ↓
   提取关键词："modern login ui"
   ↓
   搜索：npx skills find "login ui"
   ↓
   结果：anthropics/skills@frontend-design (67.2K installs)
   ↓
   安装：npx skills add anthropics/skills@frontend-design -g -y
   ↓
   调用：Skill tool with skill="frontend-design", args="创建现代化登录界面"
   ```

   **场景C：使用 MCP 工具**
   ```
   任务：分析这个设计稿 https://example.com/design.png
   ↓
   检测：需要分析图片 → MCP 工具 analyze_image
   ↓
   调用：mcp__4_5v_mcp__analyze_image with imageSource="..."
   ```

4. **工作原则**
   - 不要等待用户要求使用技能
   - 先搜索，再使用，最后报告
   - 在执行过程中明确说明使用了哪些工具

### 5.2 并行执行（多个独立任务）

**当第二步分析发现多个完全独立的任务时：**

**并行执行流程：**

1. **将所有并行任务状态更新为 `in_progress`**

2. **为每个任务选择合适的工具**（应用第四步的逻辑）

3. **使用 Task 工具创建后台代理并行执行**

   **并行执行示例：**
   ```
   发现可并行任务：[task-004, task-005, task-006]
   ↓
   依赖分析：三个任务完全独立，无共享依赖
   ↓
   任务分配：
   - task-004: 实现后端 API → 需要 backend 技能
   - task-005: 实现前端界面 → 需要 frontend-design 技能
   - task-006: 编写测试用例 → 需要 webapp-testing 技能
   ↓
   并行执行（创建3个后台代理）：
   1. Task tool: 执行 task-004（后台运行）
   2. Task tool: 执行 task-005（后台运行）
   3. Task tool: 执行 task-006（后台运行）
   ↓
   等待所有代理完成（使用 TaskOutput 检查状态）
   ↓
   收集结果和验收
   ```

4. **并行任务验收**
   - 等待所有并行任务完成
   - 逐个检查每个任务的 `acceptance_criteria`
   - 只有所有任务都通过验收，才标记为 `completed`
   - 如果有任务失败，标记为 `in_progress` 并报告具体问题

5. **并行 vs 串行决策树**

   ```
   开始第二步分析
   ↓
   找出所有可执行任务（依赖已满足）
   ↓
   检查任务数量
   ↓
   ┌─ 只1个 → 串行执行
   │
   └─ 多个 → 检查独立性
      ↓
      ┌─ 完全独立（无共享依赖） → 并行执行
      │  使用 Task 工具创建多个代理
      │
      └─ 有依赖关系 → 分组执行
         组1（独立）并行 → 组2（依赖组1）串行 → 组3（依赖组2）串行
   ```

### 5.3 并行工作原则

- **智能判断独立性** - 只有真正独立的任务才并行，有依赖关系的任务必须串行
- **优先级相同才并行** - 如果优先级差异大，先执行高优先级任务
- **资源考虑** - 如果任务需要大量资源（如编译），可能需要串行
- **透明化执行** - 明确说明"检测到 X 个独立任务，将并行执行"
- **容错处理** - 如果并行任务失败，记录失败原因，不影响其他任务

## 第六步：验收

任务完成后，逐项检查 `acceptance_criteria`：

### 自动验证（type: "auto"）

运行 `verify` 字段中的命令，如果命令成功（exit code 0），标记该标准为 `passed: true`。

**优先使用内置技能：**
- 如果 verify 命令是测试相关，调用 `/test:run` 而非直接执行

示例：
```json
{"criterion": "测试通过", "type": "auto", "verify": "pytest tests/ -q", "passed": false}
```
→ 优先调用：`/test:run pytest tests/ -q`
→ 或运行：`pytest tests/ -q`，成功则更新为 `passed: true`

### 手动验证（type: "manual"）

向用户确认该标准是否满足。如果用户确认，标记为 `passed: true`。

示例：
```json
{"criterion": "代码审查通过", "type": "manual", "passed": false}
```
→ 询问用户："代码审查是否通过？"

### 完成条件

只有当所有 acceptance_criteria 都 `passed: true` 时，才能将任务标记为 `completed`。
如果有未通过的标准，保持 `in_progress` 状态并报告哪些标准未满足。

## 第七步：更新状态

1. 更新 `tasks.json` 中的任务状态和验收标准
2. 更新 `REALITY.md` 反映最新进展
3. **使用内置技能提交代码**：`/git:commit feat: 完成 [任务ID] [任务标题]`

## 第八步：报告

输出：
- 完成的任务及其验收标准通过情况
- 使用的技能和工具（重要！让用户知道工作流在主动工作）
- 下一个待处理任务
- 整体进度

$ARGUMENTS
