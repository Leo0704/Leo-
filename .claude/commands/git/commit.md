---
description: 使用 conventional commit 格式提交更改
Argument-hint: [可选：提交消息]
Allowed-tools: Bash(git:*)
---

# Git 提交

## 参数

$ARGUMENTS

## 执行

1. 运行 `git status` 查看当前更改
2. 运行 `git diff` 查看具体更改

## Commit 消息格式

使用 Conventional Commits：
- `feat:` 新功能
- `fix:` Bug 修复
- `docs:` 文档更新
- `style:` 代码格式
- `refactor:` 重构
- `test:` 测试
- `chore:` 杂项

如果提供了参数，使用参数作为提交消息。
否则，根据更改内容自动生成提交消息。

## 提交步骤

1. `git add -A` - 暂存所有更改
2. `git commit -m "<消息>"` - 提交

## 输出

显示提交哈希和消息
