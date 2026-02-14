# 工作流权限配置指南

## 问题

工作流设计了自动化执行（搜索技能、并行任务、自动提交等），但默认情况下，每次调用工具时都需要你手动批准。

## 解决方案

### 方案 1：更新 settings.local.json（推荐）

在项目根目录的 `.claude/settings.local.json` 中添加工作流需要的权限：

```json
{
  "permissions": {
    "allow": [
      // === Git 操作（自动提交） ===
      "Bash(git:*)",
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Bash(git push:*)",
      "Bash(git rm:*)",

      // === 技能搜索和安装 ===
      "Bash(npx skills find:*)",
      "Bash(npx skills add:*)",
      "Bash(npx skills check:*)",
      "Bash(npx skills update:*)",

      // === 测试命令 ===
      "Bash(npm test:*)",
      "Bash(npm run test:*)",
      "Bash(pytest:*)",
      "Bash(python -m pytest:*)",
      "Bash(python3 -m pytest:*)",
      "Bash(cargo test:*)",

      // === Python 环境 ===
      "Bash(python:*)",
      "Bash(python3:*)",
      "Bash(pip:*)",
      "Bash(pip3:*)",
      "Bash(uv:*)",
      "Bash(source venv:*)",
      "Bash(source:venv:*)",

      // === Web 搜索（查找技能） ===
      "WebSearch"
    ],
    "deny": [
      // === 危险命令保护 ===
      "Bash(rm -rf /)",
      "Bash(rm -rf ~)",
      "Bash(rm -rf .*env)",
      "Bash(mkfs:*)",
      "Bash(dd:*)",
      "Bash(:> *)",  // 重定向覆盖文件
      "Bash(chmod -R 777:*)"  // 危险权限
    ]
  }
}
```

### 方案 2：全局配置（影响所有项目）

如果你希望工作流在所有项目中都无需确认，修改全局配置：

```bash
~/.claude/settings.json
```

添加相同的权限规则。

### 方案 3：会话级临时权限（不推荐）

在会话开始时使用以下提示：

```
@claude 在这个会话中，允许所有工作流相关的操作：
- npx skills 命令
- git 操作
- npm/pip 安装
- 文件读写
```

**缺点：** 每次会话都要重复，不推荐。

## 需要的权限类型

### 1. Bash 工具权限

**工具用途：**
- 搜索技能：`npx skills find <query>`
- 安装技能：`npx skills add <skill> -g -y`
- 运行测试：`npm test`, `pytest tests/`
- Git 提交：`git add`, `git commit`

**权限模式：**
```
Bash(npx skills:*)     # 所有 npx skills 命令
Bash(npm test:*)       # 测试命令
Bash(git:*)            # Git 操作
```

### 2. Skill 工具权限

**工具用途：**
- 调用内置技能：`frontend-design`, `webapp-testing`, `doc-coauthoring` 等
- 调用外部技能：从 skills.sh 安装的技能

**配置：**
Skill 工具通常不需要额外权限配置，但会触发 Bash 命令（见第 1 点）

### 3. 文件操作权限

**工具用途：**
- Read: 读取任务状态、配置文件
- Write: 创建新文件（代码、文档）
- Edit: 修改现有文件

**配置：**
```
Read(*.workflow/realty.md)
Read(*.workflow/goal.md)
Read(*.workflow/tasks.json)
Write(*.py)
Write(*.js)
Write(*.ts)
Edit(*.py)
Edit(*.js)
Edit(*.ts)
```

### 4. Task 工具权限（并行执行）

**工具用途：**
- 创建后台代理并行执行任务
- 查询代理状态和结果

**配置：**
Task 工具不需要权限配置，但会启动独立代理，这些代理可能需要自己的权限。

## 安全性说明

### ✅ 安全的权限授予

```json
"allow": [
  // ✅ 模式匹配 - 精确控制
  "Bash(npx skills add:*)",     // 只允许 npx skills add
  "Bash(npm test:*)",          // 只允许 npm test
  "Bash(git commit:*)"          // 只允许 git commit
]
```

### ❌ 不安全的权限授予

```json
"allow": [
  // ❌ 通配符 - 太宽泛
  "Bash(*)",                   // 允许所有 Bash 命令！危险！
  "Write(*)",                  // 允许写入任何文件！危险！
]
```

### ⚠️ 有风险的权限

```json
"allow": [
  // ⚠️ 需要谨慎
  "Bash(rm:*)",              // 允许删除文件
  "Bash(chmod:*)",            // 允许修改权限
  "Write(*.sh)",              // 允许写脚本文件
]
```

**建议：** 如果必须授予这些权限，确保 `deny` 列表中有相应的保护规则。

## 当前配置的权限

查看项目当前配置：

```bash
cat .claude/settings.local.json
```

## 验证权限是否生效

### 测试 1：技能搜索（应该无需确认）

```bash
# 在工作流中运行
npx skills find "frontend"
```

**期望：** 直接执行，不弹确认框

### 测试 2：Git 提交（应该无需确认）

```bash
git add .workflow/tasks.json
git commit -m "test: update tasks"
```

**期望：** 直接执行，不弹确认框

### 测试 3：危险命令（应该被拒绝）

```bash
rm -rf /
```

**期望：** 自动拒绝，不会执行

## 故障排查

### 问题：还是需要确认？

**可能原因：**
1. 权限模式不匹配（检查命令是否完全匹配）
2. 使用了全局配置，但项目有 local 配置（local 优先级更高）
3. Claude Code 版本更新，重置了权限

**解决方法：**
```bash
# 1. 检查当前权限
cat .claude/settings.local.json | jq '.permissions.allow'

# 2. 测试权限模式
# 在命令前加 @符号查看是否匹配
@npx skills find "test"

# 3. 如果还不行，重启 Claude Code
```

### 问题：某些命令被拒绝了？

**可能原因：**
1. 触发了 `deny` 列表中的规则
2. 权限模式写错了（语法错误）

**解决方法：**
```bash
# 1. 检查 deny 列表
cat .claude/settings.local.json | jq '.permissions.deny'

# 2. 检查权限模式语法
# 确保没有多余的空格或引号

# 3. 临时测试
# 从 deny 列表移除该规则，重新测试
```

## 工作流推荐的完整权限配置

复制以下内容到 `.claude/settings.local.json`：

```json
{
  "env": {},
  "permissions": {
    "allow": [
      "Bash(python3:*)",
      "Bash(python:*)",
      "Bash(git:*)",
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Bash(git rm:*)",
      "Bash(git push:*)",
      "Bash(pip:*)",
      "Bash(pip3:*)",
      "Bash(source:venv:*)",
      "Bash(uv:*)",
      "WebSearch",
      "Bash(npx skills find:*)",
      "Bash(npx skills add:*)",
      "Bash(npx skills check:*)",
      "Bash(npx skills update:*)",
      "Bash(npm test:*)",
      "Bash(npm run test:*)",
      "Bash(npm run build:*)",
      "Bash(pytest:*)",
      "Bash(python -m pytest:*)",
      "Bash(python3 -m pytest:*)",
      "Bash(cargo test:*)"
    ],
    "deny": [
      "Bash(rm -rf /)",
      "Bash(rm -rf ~)",
      "Bash(rm -rf .*env)",
      "Bash(mkfs:*)",
      "Bash(dd:*)",
      "Bash(:> *)"
    ]
  }
}
```

## 总结

1. **项目级配置优先** - 使用 `.claude/settings.local.json` 而非全局配置
2. **模式匹配精确** - 使用 `Bash(npm test:*)` 而非 `Bash(*)`
3. **保护危险命令** - 在 `deny` 列表中添加危险操作
4. **测试生效** - 配置后立即测试是否无需确认
5. **文档化权限** - 在 README 中说明项目需要的权限

配置完成后，工作流应该能够：
- ✅ 自动搜索技能（无需确认）
- ✅ 自动安装技能（无需确认）
- ✅ 自动运行测试（无需确认）
- ✅ 自动提交代码（无需确认）
- ✅ 并行执行任务（无需确认）

真正实现"自主工作"！
