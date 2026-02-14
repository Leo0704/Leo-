# 动态技能搜索示例

## 场景演示

### 场景 1：前端任务（动态搜索）

**任务描述：**
```json
{
  "id": "task-001",
  "title": "创建现代化登录页面",
  "status": "pending",
  "description": "创建一个响应式的登录界面，包含用户名、密码输入框和登录按钮",
  "context": "需要现代化的 UI 设计，适配移动端"
}
```

**工作流执行过程：**
```
1. 分析任务描述 → 关键词："登录界面"、"响应式"、"现代化"
2. 检查内置技能 → 无完美匹配
3. 动态搜索：
   $ npx skills find "responsive modern ui"
   ↓
   结果：anthropics/skills@frontend-design (67.2K installs)
4. 安装技能：
   $ npx skills add anthropics/skills@frontend-design -g -y
5. 使用技能：
   → Skill tool with skill="frontend-design"
6. 完成任务并提交：
   → /git:commit "feat: 完成现代化登录页面"
```

### 场景 2：测试任务（使用内置技能）

**任务描述：**
```json
{
  "id": "task-002",
  "title": "编写并运行用户认证测试",
  "status": "pending",
  "description": "为登录功能编写单元测试并运行验证",
  "steps": ["编写测试用例", "运行测试", "修复失败用例"],
  "acceptance_criteria": [
    {"criterion": "所有测试通过", "type": "auto", "verify": "pytest tests/auth.test.py -q", "passed": false}
  ]
}
```

**工作流执行过程：**
```
1. 分析任务描述 → 关键词："测试"、"运行"
2. 检查内置技能 → 匹配 /test:run
3. 直接使用（无需搜索）：
   → /test:run tests/auth.test.py
4. 验收检查：
   → 自动运行 pytest tests/auth.test.py -q
   → 通过则标记为 passed: true
5. 提交：
   → /git:commit "feat: 完成用户认证测试"
```

### 场景 3：图片分析任务（使用 MCP 工具）

**任务描述：**
```json
{
  "id": "task-003",
  "title": "分析设计稿并实现",
  "status": "pending",
  "description": "查看设计稿 https://example.com/design.png 并实现为代码",
  "context": "需要准确还原设计稿的布局和样式"
}
```

**工作流执行过程：**
```
1. 分析任务描述 → 关键词："设计稿"、"图片"
2. 识别需求 → 需要分析图片 → MCP 工具
3. 调用 MCP 工具：
   → mcp__4_5v_mcp__analyze_image with imageSource="https://example.com/design.png"
4. 根据分析结果：
   - 提取布局信息
   - 识别颜色和样式
5. 搜索前端技能：
   → npx skills find "ui implementation"
6. 实现代码
7. 提交：
   → /git:commit "feat: 实现设计稿"
```

## 工作流决策树

```
开始任务
  ↓
分析任务描述（提取关键词）
  ↓
检查内置技能 → 匹配？ → 是 → 直接使用
  ↓ 否
动态搜索外部技能
  ↓
执行 npx skills find <关键词>
  ↓
选择最合适技能（按安装量）
  ↓
安装技能（-g -y）
  ↓
使用技能完成任务
  ↓
运行验收标准
  ↓
提交代码
  ↓
报告进度
```

## 关键优势

1. **动态发现** - 不依赖硬编码的技能列表
2. **最新最优** - 始终使用安装量最高、最新的技能
3. **按需安装** - 只安装任务需要的技能
4. **优先内置** - 常见任务使用内置技能，提升效率
5. **智能选择** - 自动判断使用内置技能还是搜索外部技能

## 使用建议

- 对于频繁使用的技能（如 frontend-design），建议预先全局安装
- 对于特殊任务，依赖工作流动态搜索
- 可以在任务的 `context` 字段中明确提示技能需求
