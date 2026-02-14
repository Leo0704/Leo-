#!/bin/bash
# 工作流权限配置脚本
# 用法：source setup-permissions.sh 或 . setup-permissions.sh

set -e

echo "=================================================="
echo "  目标驱动工作流 - 权限配置"
echo "=================================================="
echo ""

# 检查 .claude 目录
if [ ! -d ".claude" ]; then
  echo "❌ 错误：未找到 .claude 目录"
  echo "   请在项目根目录运行此脚本"
  exit 1
fi

# 备份现有配置
if [ -f ".claude/settings.local.json" ]; then
  echo "📦 备份现有配置..."
  cp .claude/settings.local.json .claude/settings.local.json.backup.$(date +%s)
  echo "   ✅ 已备份到: .claude/settings.local.json.backup.$(date +%s)"
fi

# 创建新配置
echo "📝 创建工作流权限配置..."
cat > .claude/settings.local.json << 'EOF'
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
EOF

echo "   ✅ 配置文件已创建"

# 显示配置摘要
echo ""
echo "📋 已授予的权限："
echo ""
echo "  ✅ Git 操作"
echo "     - git commit, push, add, rm"
echo ""
echo "  ✅ 技能搜索和安装"
echo "     - npx skills find/add/check/update"
echo ""
echo "  ✅ 测试命令"
echo "     - npm test, pytest, cargo test"
echo ""
echo "  ✅ Python 环境"
echo "     - python, pip, uv"
echo ""
echo "  ✅ Web 搜索"
echo "     - WebSearch (用于查找技能)"
echo ""
echo "🛡️  安全保护："
echo ""
echo "  ❌ 已禁止危险命令："
echo "     - rm -rf / (删除根目录)"
echo "     - mkfs, dd (磁盘操作)"
echo ""
echo "=================================================="
echo "  ✅ 权限配置完成！"
echo "=================================================="
echo ""
echo "📚 更多信息请查看：docs/PERMISSIONS.md"
echo ""
echo "💡 下次使用 /workflow:continue 时，工作流将自动运行，无需手动确认！"
echo ""
