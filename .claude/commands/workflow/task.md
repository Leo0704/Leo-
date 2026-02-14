---
description: 创建任务并设置验收标准
Argument-hint: [任务标题]
---

# 创建任务（集成原生 Task + 智能 Skills）

## 第零步：循环依赖检测（如果设置依赖）

**重要**：在创建任务之前，如果用户设置了 `blockedBy` 依赖关系，必须先检测循环依赖。

### 检测逻辑

1. **读取当前所有任务**：使用 **TaskList** 工具获取现有任务列表

2. **模拟添加新任务**：将新任务（包含其 blockedBy 依赖）临时加入任务列表

3. **检测循环依赖**：
   - 从新任务开始，沿着 blockedBy 链向上追踪
   - 如果在追踪路径中遇到重复的任务ID，说明存在循环

4. **如果检测到循环**：
   ```
   ❌ 错误：检测到循环依赖！

   依赖链：task-A → task-B → task-C → task-A

   这会导致任务永远无法开始。
   请修改依赖关系后重试。

   建议：
   - 重新审视任务之间的实际依赖关系
   - 考虑是否真的需要这个依赖
   - 可以拆分任务来避免循环
   ```
   - **不创建任务**
   - **不执行后续步骤**

5. **如果无循环**：继续执行第一步

### 检测代码示例（供参考）

```python
def check_circular_dependency(new_task_id, blocked_by, all_tasks):
    """检测是否会形成循环依赖"""
    visited = set()
    path = []

    def trace(task_id):
        if task_id in path:
            # 找到循环！
            cycle_start = path.index(task_id)
            cycle_path = path[cycle_start:] + [task_id]
            return " → ".join(cycle_path)

        if task_id in visited:
            return None

        visited.add(task_id)
        path.append(task_id)

        # 检查这个任务依赖谁
        if task_id in all_tasks:
            for dep_id in all_tasks[task_id].get("blockedBy", []):
                result = trace(dep_id)
                if result:
                    return result

        path.pop()
        return None

    # 检查新任务的依赖链
    if blocked_by:
        for dep_id in blocked_by:
            # 创建临时任务列表（包含新任务）
            temp_tasks = {**all_tasks, new_task_id: {"blockedBy": blocked_by}}
            cycle = trace(dep_id)
            if cycle:
                return cycle

    return None
```

### 使用示例

**场景**：
- 已存在 task-001，blockedBy: ["task-002"]
- 用户想创建 task-002，设置 blockedBy: ["task-001"]

**检测结果**：
```
循环依赖链: task-002 → task-001 → task-002

❌ 创建失败：形成循环依赖！
```

---

## 第一步：使用原生 TaskCreate

根据 $ARGUMENTS 提供的任务标题，使用 **TaskCreate 工具** 创建任务。

参数设置：
- `subject`: 任务标题（从 $ARGUMENTS 获取）
- `description`: 询问用户详细描述
- `activeForm`: 询问用户进行时态描述（可选，默认 "Working on..."）

## 第二步：智能分析任务上下文

**AI 需要分析任务性质**，思考以下问题：

1. **这个任务属于什么领域？**
   - 前端开发？ → 可能需要 frontend-design skill
   - 测试？ → 可能需要 webapp-testing skill
   - 文档？ → 可能需要 doc-coauthoring skill
   - 数据处理？ → 可能需要 xlsx skill
   - 设计？ → 可能需要 canvas-design skill

2. **这个任务需要什么能力？**
   - UI 设计？ → frontend-design, canvas-design
   - 测试功能？ → webapp-testing
   - 处理表格？ → xlsx
   - 生成文档？ → docx, pdf, pptx
   - 代码分析？ → architecture-review

3. **用户有这些技能吗？**
   - 运行 `npx skills list` 检查已安装技能
   - 如果没有，进入搜索流程

## 第三步：智能搜索 Skills（如果需要）

**只有 AI 判断需要时才搜索**，不是机械匹配关键词。

### 搜索决策示例

**场景 A：任务是"创建响应式登录页面"**

AI 分析：
```
这是一个前端 UI 任务，需要界面设计能力。
用户可能没有安装相关技能。

搜索策略：
- 关键词："responsive frontend" 或 "login page design"
- 目标：找专门处理前端设计的技能
```

执行：
```bash
npx skills find "responsive frontend"
```

分析结果：
```
搜索结果：
1. anthropics/skills@frontend-design (67.2K 安装) ⭐ 推荐
2. some-author/some-frontend-skill (1.5K 安装)

决策：选择 frontend-design（安装量最高，官方维护）
```

**场景 B：任务是"为 Excel 数据生成图表"**

AI 分析：
```
这是数据处理任务，需要操作 Excel 文件。
用户可能没有安装 xlsx 技能。

搜索策略：
- 关键词："excel chart" 或 "spreadsheet visualization"
```

执行：
```bash
npx skills find "excel chart"
```

**场景 C：任务是"编写 API 文档"**

AI 分析：
```
这是文档编写任务，但可能不需要特殊技能。
内置工具就够用（Read, Write）。

决策：不搜索 Skill，直接用内置工具。
```

## 第四步：智能选择和安装

**根据搜索结果，AI 自主决策**：

### 决策因素

1. **安装量** - 优先选择安装量高的（更可靠）
2. **官方维护** - 优先 `anthropic/skills@` 命名空间
3. **更新时间** - 检查最近更新（不要用僵尸项目）
4. **任务匹配度** - 描述是否真正符合当前需求

### 安装示例

**决策后说明**：
```
找到 3 个相关技能：
- frontend-design (67.2K 安装) ⭐ 推荐
- custom-ui-builder (2.1K 安装)
- design-helper (0.8K 安装)

我选择：frontend-design
理由：官方维护，安装量最高，功能最匹配

正在安装...
```

执行：
```bash
npx skills add anthropics/skills@frontend-design -g -y
```

**重要**：
- 使用 `-g -y` 参数：全局安装，自动确认
- 只在用户明确需要时安装
- 记录安装的技能到任务描述

## 第五步：设置验收标准

任务创建并（可能）安装技能后，询问验收标准：

**提示语**：
```
任务已创建 [可能已安装相关技能]。

请设置验收标准：

支持两种类型：
1. 自动验证 (auto) - 自动运行命令检查
   示例：
   - 测试: pytest tests/ -q
   - 构建: npm run build
   - 语法检查: npm run lint

   可选配置超时时间（默认120秒）：
   - auto: 测试通过 (pytest tests/ -q) [超时: 60秒]
   - auto: 集成测试 (npm run integration-test) [超时: 600秒]

2. 手动验证 (manual) - 需要你确认
   示例：
   - 代码审查通过
   - 文档完整
   - 设计评审通过

请输入验收标准，格式：
- auto: <描述> [<命令>] [超时:N秒]
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

## 第六步：返回结果

```
✅ 任务创建成功: task-003
标题: 实现用户登录功能

技能分析:
- 任务类型: 前端 UI 开发
- 需要能力: 界面设计、响应式布局
- 已安装技能: frontend-design (67.2K 安装)

验收标准: 2 项
  - auto: 测试通过 (pytest tests/auth.test.py)
  - manual: UI 审查通过

提示: 可以直接告诉 Claude "使用 frontend-design skill 创建登录页面"
```

## 智能提示（可选）

**如果 AI 发现任务明显需要某个技能，主动提示**：

```
💡 建议: 这个任务需要前端设计能力。

我可以：
1. 使用 frontend-design skill (已安装)
2. 先设计基础版本，再用 skill 优化

你希望哪种方式？(1/2)
```

---

## 关键原则

### ✅ 应该做的

- **AI 分析判断** - 根据任务描述思考需要什么能力
- **动态搜索** - 使用 `npx skills find` 查找相关技能
- **智能选择** - 对比搜索结果，选择最合适的
- **主动安装** - 需要时自动安装（告诉用户）
- **记录决策** - 说明为什么选择这个技能

### ❌ 不应该做的

- **机械映射** - 不要用关键词表硬编码映射
- **过度搜索** - 内置工具够用就不要搜索
- **盲目安装** - 只在真正需要时才安装
- **不解释** - 告诉用户为什么搜索/安装某个技能

---

## 完整示例流程

### 用户输入
```
/workflow:task 创建一个现代化的登录页面
```

### AI 执行流程

**Step 1: 创建任务**
```python
TaskCreate(
  subject="创建登录页面",
  description="现代化设计，支持响应式"
)
```

**Step 2: 分析任务**
```
这是一个前端 UI 任务。
需要：界面设计、响应式布局
可能需要：frontend-design skill
```

**Step 3: 检查技能**
```bash
npx skills list | grep -i "frontend"
# 如果没有 frontend-design，进入搜索
```

**Step 4: 搜索技能**
```bash
npx skills find "modern login ui"
```

**Step 5: 分析结果**
```
找到：
- frontend-design (67.2K) ⭐
- modern-ui-kit (3.5K)

选择：frontend-design (官方、高安装量)
```

**Step 6: 安装技能**
```bash
npx skills add anthropics/skills@frontend-design -g -y
```

**Step 7: 设置验收标准**
```
请设置验收标准：
- auto: npm run lint
- manual: UI 审查通过
```

### 最终输出
```
✅ 任务创建成功: task-004
标题: 创建登录页面（现代化设计）

已安装技能:
- frontend-design (67.2K 安装)
  → 专门用于前端界面设计

验收标准: 2 项
  ✅ auto: 代码检查 (npm run lint)
  ✅ manual: UI 审查

现在可以使用:
"使用 frontend-design skill 创建响应式登录页面"
```
