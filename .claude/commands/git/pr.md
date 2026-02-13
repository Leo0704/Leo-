---
description: 创建 PR 并推送到远程
Argument-hint: [可选：PR 标题]
Allowed-tools: Bash(git:*)
---

# 创建 PR

## 执行

1. 确保当前分支有提交
2. 运行 `git push -u origin HEAD` 推送分支
3. 使用 `gh pr create` 或 `git push` 创建 PR

## PR 描述

自动生成 PR 描述：
- 基于最近 commits
- 包含更改摘要

## 输出

显示 PR URL
