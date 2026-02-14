---
description: 继续工作流开发 - 智能分析任务并选择工具
Argument-hint: [可选：指定任务ID]
---

# 继续工作流开发（智能 Skills 集成）

## 第一步：读取状态

读取以下文件，理解当前进度：
1. `.workflow/GOAL.md` — 项目的理想状态
2. `.workflow/REALITY.md` — 当前实际状态
3. `.workflow/tasks.json` — 任务列表和验收标准

## 第二步：确定当前任务

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

**读取并发限制配置**：
- 从 `.workflow/config.json` 读取 `max_parallel_tasks`（默认值：3）
- 统计当前 `in_progress` 任务数
- 计算可启动数 = max_parallel_tasks - 当前运行数

**情况 A：有 `in_progress` 任务**
- 继续执行该任务
- 检查是否可以同时启动其他独立任务（未超过并发限制）

**情况 B：指定了任务 ID**
- 直接处理该任务
- 检查是否可以同时启动其他独立任务（未超过并发限制）

**情况 C：寻找下一个任务（智能并行）**

1. 找出所有 `status: "pending"` 的任务
2. 检查每个任务的依赖是否已满足（所有依赖都是 `completed`）
3. **分组**：将满足条件的任务按依赖关系分组
   - 同一组：完全独立的任务，可以并行
   - 不同组：有依赖关系，必须串行
4. **执行优先级**：
   - 优先级（`priority` 数值越小越优先）
   - 如果优先级相同，可以并行执行
5. **应用并发限制**：
   - 只选择前 N 个任务（N = 可启动数）
   - 如果可执行任务数 ≤ N → 全部并行执行
   - 如果可执行任务数 > N → 只并行执行前 N 个
6. **决定并行策略**：
   - 如果找到多个完全独立的任务 → 并行执行（使用 Task 工具创建多个后台任务）
   - 如果只有一个可执行任务 → 串行执行

**并发限制示例**：

```json
// config.json
{
  "max_parallel_tasks": 3  // 最多同时运行3个任务
}
```

```
当前状态：
- 运行中: 2 个任务
- 配置限制: 3 个
- 可启动: 1 个任务

可执行任务: [task-004] 编写文档
```

**并行分组逻辑**：
- 组1（完全独立）: [task-A, task-B] → 可以并行
- 组2（依赖组1）: [task-C] → 等待组1完成
- 组3（依赖组1）: [task-D] → 等待组1完成
### 4.1 三层工具选择策略

**第一层：内置工具检查**

思考：内置工具是否足够？

| 任务类型 | 内置工具 | 足够？ |
|---------|----------|--------|
| 读取文件 | Read, Glob, Grep | ✅ 是 |
| 编辑代码 | Edit, Write | ✅ 是 |
| 运行命令 | Bash | ✅ 是 |
| Git 操作 | Bash (git) | ✅ 是 |
| 任务管理 | TaskCreate/Update | ✅ 是 |

**如果内置工具够用 → 直接使用，不搜索 Skills**

**第二层：动态搜索 Skills**

只有 AI 判断内置工具不足时，才搜索 Skills：

**AI 分析流程：**
```
1. 理解任务需要什么能力
2. 判断内置工具是否足够
3. 如果不够 → 构思搜索关键词
4. 执行 npx skills find
5. 分析搜索结果
6. 选择最合适的技能
7. 按需安装
```

**搜索示例（AI 自主决策）**

**场景 A：创建现代化登录界面**

AI 分析：
```
任务要求：
- 响应式设计
- 现代化 UI
- 良好的用户体验

内置工具够用吗？
- Read, Write, Edit 可以写代码
- 但设计能力不足，需要专业设计技能

搜索策略：
- 关键词1: "responsive frontend"
- 关键词2: "modern ui design"

执行搜索：
npx skills find "responsive frontend"
```

分析搜索结果：
```
找到技能:
1. anthropics/skills@frontend-design (67.2K installs)
   - 描述: Create distinctive, production-grade frontend interfaces
   - 最后更新: 2 weeks ago
   - 推荐: ⭐⭐⭐

2. some-custom/skill (3.5K installs)
   - 描述: Simple UI builder
   - 最后更新: 6 months ago

3. another-ui-kit (1.2K installs)
   - 描述: Basic UI components
   - 最后更新: 1 year ago

AI 决策:
选择: frontend-design
理由:
1. 官方维护 (anthropic/skills)
2. 安装量最高 (67.2K vs 3.5K/1.2K)
3. 更新活跃 (2 weeks ago)
4. 描述明确匹配 "production-grade frontend interfaces"
```

**场景 B：分析应用性能**

AI 分析：
```
任务要求：
- 分析代码瓶颈
- 识别性能问题
- 提供优化建议

内置工具够用吗？
- Read, Grep 可以分析代码
- 但缺少专业的性能分析视角

搜索策略：
- 关键词: "performance analysis" 或 "code review"

执行搜索：
npx skills find "performance analysis code"
```

如果搜索结果不理想：
```
AI 决策:
没有找到高度匹配的技能。
使用内置工具：
1. Grep 搜索性能相关代码
2. Read 分析瓶颈
3. 手动分析并提供优化建议
```

**场景 C：处理 Excel 导出数据**

AI 分析：
```
任务要求：
- 读取 Excel 文件
- 处理数据
- 生成新表格

内置工具够用吗？
- Python 可以用 openpyxl
- 但 xlsx skill 更专业、更快

搜索策略：
- 关键词: "excel" 或 "spreadsheet"

执行搜索：
npx skills find "excel"
```

**场景 D：编写技术文档**

AI 分析：
```
任务要求：
- 结构化文档
- 协作和迭代
- 验证文档可用性

内置工具够用吗？
- Write 可以生成 Markdown
- 但 doc-coauthoring skill 有专门的协作文档

搜索策略：
- 关键词: "documentation" 或 "doc"

执行搜索：
npx skills find "documentation"
```

### 4.2 执行策略

**优先级排序**：
1. **内置工具** - 零成本，立即可用
2. **已安装 Skills** - 无需安装，直接使用
3. **搜索并安装新 Skill** - 只在真正需要时

**决策示例**：
```
任务: "创建响应式登录页面"

Step 1: 内置工具检查
  → Edit, Write 可以写代码
  → 但缺少设计专业性

Step 2: 检查已安装 Skills
  → npx skills list
  → 没有 frontend-design

Step 3: 搜索 Skills
  → npx skills find "responsive frontend"
  → 找到 frontend-design (67.2K)

Step 4: 安装并使用
  → npx skills add ... -g -y
  → Skill tool with skill="frontend-design"
```

### 4.3 不要做什么

❌ **机械式关键词匹配**：
```python
# 错误做法
if "前端" in task_description:
    use_skill("frontend-design")
```

✅ **AI 智能分析**：
```
# 正确做法
思考：这个任务真正需要什么？
- 需要设计能力吗？ → 搜索 frontend-design
- 只是要写 HTML/CSS？ → 内置工具足够
- 需要测试吗？ → 搜索 webapp-testing
```

❌ **过度搜索**：
```
任务: "修复一个 bug"
→ 不需要搜索 Skill（内置工具够用）
→ 不要执行 npx skills find
```

✅ **合理搜索**：
```
任务: "创建现代化数据可视化大屏"
→ 需要专业设计能力
→ 值得搜索 canvas-design 或 frontend-design
```

## 第五步：执行任务

### 5.1 单任务执行

1. 将任务状态更新为 `in_progress`

2. **应用第四步选择的工具**
   - 如果是内置工具：直接使用 Read, Write, Edit, Bash
   - 如果是已安装 Skill：直接调用 `Skill` 工具
   - 如果是需要安装的 Skill：先安装（`npx skills add ... -g -y`），再调用
   - 如果是 MCP 工具：在需要时直接调用

### 5.2 并行执行（多个独立任务）

**当第二步分析发现多个完全独立的任务时：**

**并行执行流程：**

1. **将所有并行任务状态更新为 `in_progress`**

2. **为每个任务智能选择工具**（应用第四步的逻辑）

3. **使用 Task 工具创建后台代理并行执行**

   **并行执行示例：**
   ```
   发现可并行任务：[task-004, task-005, task-006]
   ↓
   依赖分析：三个任务完全独立，无共享依赖
   ↓
   任务分析和工具选择：
   - task-004: 实现后端 API
     → 内置工具足够（Read, Write, Edit）
     → 不需要 Skill

   - task-005: 实现前端界面
     → 需要设计能力
     → 搜索/使用 frontend-design skill

   - task-006: 编写测试用例
     → 需要测试能力
     → 搜索/使用 webapp-testing skill
   ↓
   并行执行（创建3个后台代理）：
   1. Task tool: 执行 task-004（后台运行）
   2. Task tool: 执行 task-005，使用 frontend-design（后台运行）
   3. Task tool: 执行 task-006，使用 webapp-testing（后台运行）
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

**优先使用内置技能**：
- 如果 verify 命令是测试相关，调用 `/test:run` 而非直接执行
- 如果 verify 命令是 git 相关，调用 `/git:commit`

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

**报告格式示例：**
```
✅ 任务完成: task-003 (实现后端 API)

验收标准: 2/2 通过
  ✅ 测试通过 (auto) - pytest tests/api/ -q
  ✅ API 文档完整 (manual) - 用户确认

使用工具:
  - 内置: Read, Write, Edit (代码编写)
  - 技能: 无（内置工具足够）

下一个任务: task-004 (实现前端界面)
```

$ARGUMENTS
