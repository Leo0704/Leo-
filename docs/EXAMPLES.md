# 使用示例

## 示例 1: 初始化新项目

```bash
# 在 Claude Code 中
cd ~/projects
mkdir my-blog
cd my-blog

# 告诉 Claude:
请帮我初始化一个博客系统的工作流，任务包括：
1. 创建项目基础结构
2. 实现文章列表页面
3. 实现文章详情页
4. 添加评论功能
5. 部署到生产环境
```

Claude 会自动：
1. 创建 `.workflow/` 目录和状态文件
2. 创建任务列表
3. 开始第一个任务

## 示例 2: 继续开发

```bash
# 新会话开始时
claude

# 告诉 Claude:
继续开发
```

Claude 会：
1. 读取 `.workflow/status.json`
2. 获取当前任务
3. 继续工作

## 示例 3: 查看进度

```bash
# 使用命令
/workflow:status

# 或运行脚本
python ../自动工作流/tools/view_progress.py .
```

## 示例 4: 添加任务

```bash
# 告诉 Claude:
添加任务：实现用户收藏功能
```

## 示例 5: 使用 Plan Mode

```bash
# 对于复杂任务
claude --permission-mode plan

# 或在会话中
[按下 Shift+Tab 切换到 Plan Mode]
```

## 示例 6: 使用自定义命令

```bash
# 查看状态
/workflow:status

# 继续工作
/workflow:continue

# 添加任务
/workflow:add-task 实现搜索功能
```

## 示例 7: 代码审查

```bash
# 告诉 Claude:
请审查 src/auth 模块的代码
```

## 示例 8: 运行测试

```bash
# 运行测试
/test:run

# 或指定文件
/test:run tests/test_auth.py
```

## 示例 9: Git 提交

```bash
# 提交更改
/git:commit

# 或带消息
/git:commit 添加用户登录功能

# 创建 PR
/git:pr
```

## 示例 10: 使用 MCP

```bash
# 添加 MCP 服务器
claude mcp add github --transport http https://api.github.com/mcp/

# 列出可用 MCP
claude mcp list
```

## 示例 11: 使用 Subagents

```bash
# 列出可用代理
/agents

# 创建新代理
/agents create
```

## 示例 12: 使用 Skills

```bash
# 加载 skill
使用 architecture-review skill 分析项目结构
```
