# 无限开发工作流

> 让 Claude Code 跨会话持续开发 - **零代码，纯状态驱动**

## 一句话说明

**工作流 = 2个状态文件 + 3个提示词**

不需要安装任何东西，不需要 Python，直接用。

---

## 快速开始

### 1️⃣ 开始新项目

告诉 Claude：

```
创建 .workflow/ 目录，初始化项目状态
项目：[你的项目描述]
```

### 2️⃣ 继续开发

每次新会话说：

```
继续开发
```

### 3️⃣ 完成

Claude 会自动：
- 读取状态
- 执行任务
- 更新进度
- 提交代码

---

## 核心文件（只要2个）

```
.workflow/
├── STATUS.md     # 当前状态（人类可读）
└── tasks.json    # 任务列表（JSON格式）
```

### STATUS.md 示例

```markdown
# 项目状态

## 进度
- 总任务：10
- 已完成：5
- 进行中：task-006

## 当前任务
实现用户登录功能

## 下一步
1. 添加表单验证
2. 连接后端 API
```

### tasks.json 示例

```json
{
  "tasks": [
    {"id": "task-001", "title": "项目初始化", "status": "completed"},
    {"id": "task-002", "title": "设计 UI", "status": "completed"},
    {"id": "task-003", "title": "实现登录", "status": "in_progress"}
  ]
}
```

---

## 工作原理

```
┌────────────────────────────────────────┐
│           Claude Code 会话             │
│                                        │
│  1. 读取 .workflow/STATUS.md          │
│  2. 读取 .workflow/tasks.json         │
│  3. 找到下一个任务                     │
│  4. 执行任务                           │
│  5. 更新状态文件                       │
│  6. 提交 Git（可选）                   │
│                                        │
│  下次会话继续...                       │
└────────────────────────────────────────┘
```

---

## 提示词模板

### 开始新项目

```
创建一个无限开发工作流：

1. 创建 .workflow/ 目录
2. 创建 STATUS.md 文件，包含项目状态
3. 创建 tasks.json 文件，包含任务列表

项目描述：[在这里描述你的项目]
```

### 继续开发

```
继续开发。请：
1. 读取 .workflow/STATUS.md
2. 读取 .workflow/tasks.json
3. 找到下一个待处理任务
4. 执行该任务
5. 完成后更新状态文件
```

### 结束会话

```
更新 .workflow/STATUS.md，记录本次完成的任务
```

---

## 可选：Python 工具

Python 代码只是**辅助工具**，不是必需的：

```bash
# 查看进度（可选）
python tools/view_progress.py

# 初始化项目（可选）
python tools/init_workflow.py ./my_project --name "项目名"
```

**没有 Python？** 直接手动编辑 `.workflow/STATUS.md` 和 `.workflow/tasks.json` 即可！

---

## 为什么不需要代码？

| 传统方式 | 无限工作流 |
|---------|----------|
| 程序调用 API | Claude 直接工作 |
| 代码管理状态 | 文件管理状态 |
| 需要安装依赖 | 零依赖 |
| 需要配置 | 零配置 |

**Claude Code 本身就是执行引擎**，不需要额外的代码来驱动。

---

## 目录结构

```
你的项目/
├── .workflow/           # 工作流状态（必需）
│   ├── STATUS.md       # 当前状态
│   ├── tasks.json      # 任务列表
│   └── sessions/       # 会话记录（可选）
├── src/                # 你的源代码
└── ...
```

---

## 许可证

MIT License
