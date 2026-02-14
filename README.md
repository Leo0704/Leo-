# 目标驱动工作流

> 让 Claude Code 自主地把软件开发到理想状态

## 核心理念

**不告诉 AI 做什么，而是告诉 AI 你想要什么。**

```
传统方式：任务列表 → 执行 → 完成
目标驱动：理想状态 → 差距分析 → 自主行动 → 迭代
```

## 快速开始

### 1. 复制模板

```bash
cp -r templates/quickstart/.workflow ./你的项目/
```

### 2. 编辑 GOAL.md

描述你想要的**理想状态**：

```markdown
# 项目理想状态

## 产品愿景
一个简洁的博客系统

## 成功标准
- [ ] 用户可以登录
- [ ] 用户可以发文章
- [ ] 页面加载 < 2秒

## 验收条件
当我使用时：
1. 注册流程 < 30秒
2. 写文章体验流畅
```

### 3. 启动开发

```
读取 .workflow/GOAL.md 和 .workflow/REALITY.md
分析差距，开始实现核心功能
完成后更新 REALITY.md
```

### 4. 持续迭代

每次新会话：

```
继续目标驱动开发
```

---

## 示例项目

| 项目 | 类型 | 描述 |
|------|------|------|
| [examples/todo-app](examples/todo-app/) | Web | 浏览器待办应用 |
| [examples/cli-tool](examples/cli-tool/) | CLI | 命令行待办工具 |

---

## 验收标准

每个任务可以定义验收标准，分两种类型：

**自动验证** — 绑定 shell 命令，运行通过即达标：
```json
{"criterion": "测试通过", "type": "auto", "verify": "pytest tests/ -q", "passed": false}
```

**手动确认** — 需要用户确认：
```json
{"criterion": "UI 审查通过", "type": "manual", "passed": false}
```

`/workflow:continue` 会在任务完成时自动运行 auto 验证，并向用户确认 manual 标准。只有所有标准通过，任务才能标记为完成。

---

## 文件结构

```
项目/
├── .workflow/
│   ├── GOAL.md       # 理想状态（你想要的）
│   ├── REALITY.md    # 当前状态（实际是）
│   └── tasks.json    # 任务列表和验收标准
├── .claude/          # Claude Code 配置（可选）
│   ├── settings.json # Hooks 配置
│   └── hooks.py      # 自动触发脚本
└── [你的代码]/
```

---

## 自动触发

配置 `.claude/settings.json` 后，每次会话自动显示进度。

---

## 一句话总结

**告诉 Claude 你想要什么，让它自己想办法。**

## 许可证

MIT
