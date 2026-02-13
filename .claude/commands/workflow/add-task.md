---
description: 添加新任务到工作流
Argument-hint: <任务标题>
---

# 添加新任务

## 参数

$ARGUMENTS

## 执行

1. 读取当前 `.workflow/tasks.json`
2. 生成新任务 ID（最大 ID + 1）
3. 添加新任务：
   - status: pending
   - priority: 999（最低优先级）
   - title: $ARGUMENTS

4. 保存 tasks.json
5. 更新 status.json 的 stats
6. 更新 STATUS.md

## 输出

报告新添加的任务 ID 和标题
