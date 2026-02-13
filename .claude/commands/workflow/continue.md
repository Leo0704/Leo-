---
description: 继续工作流开发 - 读取当前状态并继续下一个任务
Argument-hint: [可选：指定任务ID]
---

# 继续工作流开发

## 当前任务

读取当前工作流状态：
1. 读取 `.workflow/status.json` 获取当前进度
2. 读取 `.workflow/tasks.json` 获取任务列表
3. 读取 `.workflow/STATUS.md` 获取人类可读状态

## 执行任务

如果是 in_progress 状态，继续当前任务。
如果是 pending 状态，开始下一个任务。

## 任务执行标准

每个任务完成后：
1. 更新 `.workflow/status.json` 的 stats
2. 更新 `.workflow/tasks.json` 的任务状态
3. 更新 `.workflow/STATUS.md`
4. 提交 Git: `git add -A && git commit -m "feat: 完成 [任务ID]"`

## 报告

完成后报告：
- 完成的任务
- 下一个任务
- 进度百分比

$ARGUMENTS
