---
description: 继续工作流开发 - 读取当前状态并继续下一个任务
Argument-hint: [可选：指定任务ID]
---

# 继续工作流开发

## 第一步：读取状态

读取以下文件，理解当前进度：
1. `.workflow/GOAL.md` — 项目的理想状态
2. `.workflow/REALITY.md` — 当前实际状态
3. `.workflow/tasks.json` — 任务列表和验收标准

## 第二步：确定当前任务

从 tasks.json 中找到当前应处理的任务：
- 如果有 `status: "in_progress"` 的任务，继续它
- 否则找 `status: "pending"` 且依赖已满足的最高优先级任务
- 如果指定了任务 ID，直接处理该任务

## 第三步：理解任务上下文

读取任务的以下字段：
- `description` 和 `steps` — 任务内容
- `context` — 执行此任务时应采用的视角和关注点
- `acceptance_criteria` — 完成标准（重要！）

## 第四步：执行任务

将任务状态更新为 `in_progress`，然后开始工作。

## 第五步：验收

任务完成后，逐项检查 `acceptance_criteria`：

### 自动验证（type: "auto"）
运行 `verify` 字段中的命令，如果命令成功（exit code 0），标记该标准为 `passed: true`。

示例：
```json
{"criterion": "测试通过", "type": "auto", "verify": "pytest tests/ -q", "passed": false}
```
→ 运行 `pytest tests/ -q`，成功则更新为 `passed: true`

### 手动验证（type: "manual"）
向用户确认该标准是否满足。如果用户确认，标记为 `passed: true`。

示例：
```json
{"criterion": "代码审查通过", "type": "manual", "passed": false}
```
→ 询问用户："代码审查是否通过？"

### 完成条件
只有当所有 acceptance_criteria 都 `passed: true` 时，才能将任务标记为 `completed`。
如果有未通过的标准，保持 `in_progress` 状态并报告哪些标准未满足。

## 第六步：更新状态

1. 更新 `tasks.json` 中的任务状态和验收标准
2. 更新 `REALITY.md` 反映最新进展
3. 提交 Git: `git add .workflow/ && git commit -m "feat: 完成 [任务ID] [任务标题]"`

## 第七步：报告

输出：
- 完成的任务及其验收标准通过情况
- 下一个待处理任务
- 整体进度

$ARGUMENTS
