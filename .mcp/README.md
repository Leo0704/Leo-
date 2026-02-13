# MCP 配置示例

本目录包含工作流可以使用的 MCP 服务器配置示例。

## 添加 MCP 服务器

在项目根目录创建 `.mcp.json` 文件：

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "your-token-here"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "./data"]
    },
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "./data/workflow.db"]
    }
  }
}
```

## 常用 MCP 服务器

### 数据库
- `mcp-server-postgres` - PostgreSQL
- `mcp-server-sqlite` - SQLite

### 搜索
- `mcp-server-brave-search` - Brave 搜索
- `mcp-server-fetch` - Web 获取

### 存储
- `mcp-server-memory` - 知识图谱存储
- `mcp-server-filesystem` - 文件系统访问

## 使用方式

```bash
# 列出已配置的 MCP 服务器
claude mcp list

# 添加 MCP 服务器
claude mcp add github --transport http https://api.github.com/mcp/
```

## 更多信息

参见: https://modelcontextprotocol.io
