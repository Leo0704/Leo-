---
description: 检查任务验收标准并更新状态
Argument-hint: [任务ID，可选]
---

# 验收检查

## 第一步：确定要验证的任务

**情况 A：提供了 $ARGUMENTS**
- 直接验证指定的任务ID

**情况 B：未提供 $ARGUMENTS**
- 使用 **TaskList** 工具获取当前任务列表
- 找到 `status: "in_progress"` 的任务
- 如果有多个，询问用户验证哪一个

## 第二步：读取验收标准

从 `.workflow/criteria.json` 读取该任务的 `acceptance_criteria`。

**如果文件不存在或任务没有验收标准**：
```
该任务没有设置验收标准。
1. 立即设置验收标准
2. 跳过验收，直接标记完成（不推荐）

请选择: 1 或 2
```

## 第三步：执行验证

遍历每条验收标准：

### type: "auto"

运行 `verify` 字段中的命令：
- 使用 **Bash 工具** 执行命令
- **成功**（exit code 0）→ 更新 `passed: true`
- **失败**（exit code ≠ 0）→ 保持 `passed: false`，记录输出

**示例**：
```json
{"criterion": "测试通过", "type": "auto", "verify": "pytest tests/ -q", "passed": false}
```
执行：
```bash
pytest tests/ -q
```
如果成功，更新为：
```json
{"criterion": "测试通过", "type": "auto", "verify": "pytest tests/ -q", "passed": true}
```

**优先使用内置技能**：
- 如果 verify 命令是测试相关，优先调用 `/test:run`
- 如果 verify 命令是 git 相关，优先调用 `/git:commit`

### type: "manual"

**询问用户**：
```
是否满足：{criterion}？

回复:
- y / yes / 确认 → 标记为通过
- n / no / 不通过 → 标记为失败
```

根据用户回答，更新 `passed` 字段。

## 第四步：更新状态

### 计算通过率

```python
total = len(acceptance_criteria)
passed = sum(1 for c in acceptance_criteria if c["passed"])
```

### 情况 A：全部通过 (passed == total)

1. **更新验收标准文件**：
   - 将所有 `passed` 设为 `true`
   - 保存到 `.workflow/criteria.json`

2. **更新任务状态**：
   - 使用 **TaskUpdate** 工具
   - 将任务标记为 `completed`
   - 参数：`{"taskId": "任务ID", "status": "completed"}`

3. **输出结果**：
   ```
   ✅ 验收通过，任务已完成

   验收标准: 2/2 通过
     ✅ 测试通过 (auto)
     ✅ 代码审查 (manual)

   任务状态已更新为: completed
   ```

### 情况 B：部分通过 (passed < total)

1. **更新验收标准文件**：
   - 保存通过的项目
   - 未通过的项目保持 `passed: false`

2. **保持任务状态**：
   - 保持 `in_progress` 状态
   - 不要调用 TaskUpdate

3. **输出结果**：
   ```
   ❌ 验收未通过，任务保持进行中

   验收标准: 1/2 通过
     ✅ 测试通过 (auto)
     ❌ 代码审查 (manual) ← 未通过

   请修复未通过项后，再次运行 /workflow:verify
   ```

## 第五步：同步到文件（可选）

如果配置了 `auto_sync`，自动调用 hooks.py 同步到 `.workflow/state.json`。

---

## 完整示例

### 场景：自动验证 + 手动验证

```bash
用户: /workflow:verify

Claude:
1. TaskList → 找到 task-003 (in_progress)
2. 读取 criteria.json → 2 条验收标准
3. 执行验证：
   - auto: pytest tests/auth.test.py
     → 执行成功 → passed: true
   - manual: 询问用户
     → 用户回复 yes → passed: true
4. 全部通过 → TaskUpdate: status="completed"
5. 输出：✅ task-003 验收通过
```

### 场景：验证失败

```bash
用户: /workflow:verify

Claude:
1. 读取 task-004 → 3 条验收标准
2. 执行验证：
   - auto: npm run build
     → 失败 → passed: false
     → 错误信息：TypeScript compilation failed
   - auto: npm run lint
     → 成功 → passed: true
   - manual: 询问用户
     → 用户回复 yes → passed: true
3. 部分通过 → 保持 in_progress
4. 输出：
   ```
   ❌ 验收未通过

   通过: 2/3
     ✅ 代码检查 (auto)
     ✅ 功能确认 (manual)
     ❌ 构建成功 (auto) ← 失败

   错误: TypeScript compilation failed
   请修复后重新验证
   ```
```

---

## 错误处理

### 任务不存在
```
❌ 错误: 未找到任务 {taskID}

使用 /workflow:status 查看所有任务
```

### criteria.json 格式错误
```
❌ 错误: criteria.json 格式无效

请检查 JSON 格式，或删除该文件重新创建
```

### auto 验证命令执行超时
```
⚠️  警告: 验证命令执行超时 (120s)

命令: npm test
建议: 检查命令是否需要更长时间，或手动验证

跳过此项? (y/n)
```
