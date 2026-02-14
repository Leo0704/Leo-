# Todo App 示例

一个简单的前端待办应用，展示如何使用目标驱动工作流开发前端项目。

## 功能特性

- ✅ 添加待办事项
- ✅ 标记完成/未完成
- ✅ 删除待办事项
- ✅ LocalStorage 数据持久化
- ✅ 简洁现代的卡片式布局

## 技术栈

- HTML5
- CSS3
- 原生 JavaScript
- LocalStorage

## 如何使用工作流

### 1. 设置目标

编辑 `.workflow/GOAL.md` 定义项目目标

### 2. 创建任务

```bash
cd examples/todo-app
/workflow:task 添加待办事项输入框
```

### 3. 查看进度

```bash
/workflow:status
```

### 4. 完成任务

```bash
/workflow:task 记录添加成功功能为完成
```

## 与旧方式对比

| 特性 | 旧方式 | 新工作流 |
|------|---------|----------|
| 任务管理 | 看板工具 | /workflow:task |
| 进度追踪 | 感觉判断 | /workflow:status |
| 状态存储 | LocalStorage | .workflow/state.json |

## 快速开始

1. 用浏览器打开 `index.html`
2. 开始添加待办事项
3. 使用 `/workflow:task` 管理开发任务
