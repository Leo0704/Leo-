# CLI 工具示例

一个传统的命令行工具示例，展示目标驱动工作流在 CLI 项目中的应用。

## 功能特性

- ✅ 添加待办事项
- ✅ 列出所有事项
- ✅ 标记完成
- ✅ 删除事项
- ✅ JSON 文件持久化

## 技术栈

- Python 3
- argparse
- JSON 文件存储
- 命令行参数解析

## 如何使用工作流

### 1. 设置目标

编辑 `.workflow/GOAL.md` 定义项目目标

### 2. 创建任务

```bash
cd examples/cli-tool
/workflow:task 添加新功能
```

### 3. 查看进度

```bash
/workflow:status
```

### 4. 设置验收标准

```bash
/workflow:verify
```

## 与旧方式对比

| 特性 | 旧方式 | 新工作流 |
|------|---------|----------|
| 任务管理 | python todo.py add | /workflow:task |
| 进度追踪 | python todo.py list | /workflow:status |
| 状态存储 | ~/.todo_cli.json | .workflow/state.json |
| 验收标准 | 无 | criteria.json |

## 快速开始

这个示例展示如何从传统方式迁移到新的工作流系统。建议直接在新项目中使用新工作流！
