# 目标驱动工作流

> 告诉 Claude 你想要什么，让它自己想办法。

## 用法

### 1. 复制模板到你的项目

```bash
cp -r templates/quickstart/.workflow ./你的项目/
```

### 2. 编辑 GOAL.md

```markdown
# 项目理想状态

## 产品愿景
一个简洁的博客系统

## 成功标准
- [ ] 用户可以登录
- [ ] 用户可以发文章

## 验收条件
1. 注册流程 < 30秒
2. 写文章体验流畅
```

### 3. 在 Claude Code 中

```
继续目标驱动开发
```

每次新会话说同样的话，Claude 会读取状态文件继续工作。

## 验收标准

任务可以定义两种验收标准：

```json
{"criterion": "测试通过", "type": "auto", "verify": "pytest tests/ -q", "passed": false}
{"criterion": "UI 审查通过", "type": "manual", "passed": false}
```

`auto` 绑定命令自动验证，`manual` 需用户确认。所有标准通过才能完成任务。

## 示例

| 项目 | 类型 |
|------|------|
| [examples/todo-app](examples/todo-app/) | Web 待办应用 |
| [examples/cli-tool](examples/cli-tool/) | CLI 待办工具 |

## 许可证

MIT
