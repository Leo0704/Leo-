# 项目模板

本目录包含可复用的项目模板。

## 可用模板

### 1. Python 项目模板
- 位置: `python/`
- 适用: Python 后端服务、CLI 工具

### 2. Node.js 项目模板
- 位置: `nodejs/`
- 适用: Node.js 服务、API

### 3. Next.js 项目模板: `nextjs
- 位置/`
- 适用: 全栈 Web 应用

### 4. React 项目模板
- 位置: `react/`
- 适用: 前端应用

## 使用方式

```bash
# 使用 Python 模板
python tools/new_project.py my-project --template python

# 使用 Node.js 模板
python tools/new_project.py my-project --template nodejs

# 使用 Next.js 模板
python tools/new_project.py my-project --template nextjs
```

## 自定义模板

1. 在 `templates/` 目录下创建新文件夹
2. 添加项目文件
3. 创建 `CLAUDE.md` 描述项目
4. 在 `tools/new_project.py` 中添加模板选项
