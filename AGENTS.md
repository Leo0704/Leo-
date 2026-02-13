# 自定义子代理定义

本文件定义了可用于此工作流的子代理。

## 任务管理器 (Task Manager)

负责管理工作流中的任务：
- 读取/更新 .workflow/tasks.json
- 读取/更新 .workflow/status.json
- 跟踪任务进度
- 生成任务报告

## 进度追踪器 (Progress Tracker)

负责追踪和报告项目进度：
- 计算完成百分比
- 生成进度图表
- 更新 STATUS.md

## 代码审查员 (Code Reviewer)

负责审查代码质量：
- 检查代码风格
- 识别潜在问题
- 提供改进建议

## 文档工程师 (Documentation Engineer)

负责维护项目文档：
- 更新 README.md
- 维护 API 文档
- 生成变更日志
