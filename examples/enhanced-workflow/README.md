# 增强工作流示例项目

这是一个演示增强工作流特性的示例项目，展示了如何使用：
- Skills 集成
- 多角色协作
- 验收标准

## 项目目标

实现一个完整的用户认证系统，包括：
- 用户注册
- 用户登录
- JWT 认证
- 安全审查
- 完整文档

## 团队角色

- **Alice** - Product Manager (PM)
- **Bob** - Tech Lead / Backend Developer
- **Eve** - Frontend Developer
- **David** - QA Engineer
- **Grace** - Security Engineer
- **Charlie** - Senior Developer (Reviewer)
- **Frank** - Designer (Reviewer)

## 工作流程

```
1. PM 编写 PRD (Alice)
   ↓
2. 架构设计 (Bob) → 审查 (Charlie, Alice)
   ↓
3. 后端开发 (Bob) → 审查 (Charlie)
   ↓
4. 前端开发 (Eve) → 审查 (Frank, Charlie)
   ↓
5. 集成测试 (David)
   ↓
6. 安全审查 (Grace)
   ↓
7. 文档更新 (Bob)
   ↓
8. 部署上线 (Bob)
```

## 使用方法

### 在 Claude Code 中继续开发

```
继续开发
```

### 查看进度

```
/workflow:status
```

### 查看当前任务

```
python tools/view_progress.py
```

## Skills 使用

- `product-manager-toolkit` - 用于 PRD 编写和优先级评估
- `architecture-review` - 用于架构设计和审查
- `test:run` - 用于自动化测试
- `git:commit` - 用于代码提交
- `git:pr` - 用于创建 PR

## 验收标准示例

每个任务都有明确的验收标准，例如：

**后端开发任务的验收标准：**
- ✅ 注册接口实现并测试通过
- ✅ 登录接口实现并测试通过
- ✅ 密码使用 bcrypt 加密
- ✅ 单元测试覆盖率 > 80%
- ✅ 代码审查通过
- ✅ API 文档更新

## 多角色协作

任务会自动分配给对应角色：
- PM 负责需求和优先级
- Developer 负责实现
- Tester 负责测试
- Reviewer 负责审查

## 下一步

1. 运行 `python tools/view_progress.py` 查看详细进度
2. 在 Claude Code 中输入 `继续开发` 开始工作
3. 使用 `/workflow:status` 随时查看状态
