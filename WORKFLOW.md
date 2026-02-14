# 无限开发工作流 v2.0

> 纯状态驱动，零代码依赖

## 核心理念

工作流 = **约定 + 提示词**，不需要任何代码。

```
┌─────────────────────────────────────────────────┐
│                                                 │
│   .workflow/STATUS.md  ←── Claude 读取状态      │
│   .workflow/tasks.json ←── Claude 读取任务      │
│                                                 │
│   Claude 执行任务                               │
│   Claude 更新状态                               │
│   Claude 提交代码                               │
│                                                 │
│   循环...                                       │
│                                                 │
└─────────────────────────────────────────────────┘
```

## 使用方法

### 开始新项目

复制这段给 Claude：

```
创建 .workflow/ 目录，包含：
- STATUS.md（项目状态）
- tasks.json（任务列表）

项目描述：[你的项目描述]
```

### 继续开发

复制这段给 Claude：

```
读取 .workflow/STATUS.md 和 .workflow/tasks.json
然后继续完成下一个任务
```

### 结束会话

复制这段给 Claude：

```
更新 .workflow/STATUS.md
记录本次完成的任务
```

---

## 状态文件格式

### STATUS.md（人类可读）

```markdown
# 项目状态

## 信息
- 项目：[项目名]
- 更新：[时间]

## 进度
- 总任务：10
- 已完成：5
- 进行中：task-006

## 当前任务
[task-006] 实现用户登录

## 下一步
1. [task-007] 添加表单验证
2. [task-008] 连接后端
```

### tasks.json（机器可读）

```json
{
  "tasks": [
    {"id": "task-001", "title": "初始化", "status": "completed"},
    {"id": "task-002", "title": "设计UI", "status": "completed"},
    {"id": "task-003", "title": "实现登录", "status": "in_progress"}
  ]
}
```

---

## Python 工具（可选）

Python 代码只是辅助工具，不是必需的：

```bash
# 可选：查看进度
python tools/view_progress.py

# 可选：初始化项目
python tools/init_workflow.py
```

**没有 Python 也能用！** 直接手动编辑状态文件即可。

---

## 完整示例

### 第一次会话

```
用户：创建一个博客系统，初始化工作流

Claude：
1. 创建 .workflow/STATUS.md
2. 创建 .workflow/tasks.json（包含10个任务）
3. 开始第一个任务：项目初始化
4. 完成后更新状态
```

### 第二次会话

```
用户：继续开发

Claude：
1. 读取 .workflow/STATUS.md
2. 发现 task-002 待处理
3. 执行 task-002
4. 更新状态
```

### 第 N 次会话

```
用户：继续

Claude：
1. 读取状态，发现所有任务完成
2. 提示：项目已完成！
```

---

## 目录结构（最小化）

```
项目/
├── .workflow/
│   ├── STATUS.md      # 必须：当前状态
│   └── tasks.json     # 必须：任务列表
└── [你的代码]/
```

**就这么简单！** 不需要任何配置文件、不需要安装任何东西。

---

## 与 v1 的区别

| v1（复杂） | v2（简单） |
|-----------|-----------|
| 需要 Python | 不需要 |
| 多个配置文件 | 只要 2 个文件 |
| 复杂的任务管理 | 简单的 JSON |
| 需要理解代码 | 只需理解约定 |

---

## 一句话总结

**工作流 = 状态文件 + 提示词，代码是可选的。**
