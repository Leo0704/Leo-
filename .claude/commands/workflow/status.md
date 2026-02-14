---
description: 查看当前工作流进度状态
---

# 查看工作流进度

## 执行

1. 读取 `.workflow/tasks.json`
2. 计算进度

## 输出格式

```
进度: X/Y (Z%)

当前任务: [task-ID] 标题
  描述: ...
  验收标准:
    [x] [auto] 测试通过
    [ ] [manual] 代码审查通过
    进度: 1/2

待处理:
  1. [task-ID] 标题 (依赖: task-XXX)
  2. [task-ID] 标题
```

如果任务有 `context` 字段，也一并显示。
如果有 `acceptance_criteria`，逐项列出通过状态。
