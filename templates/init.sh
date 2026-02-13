#!/bin/bash

# 项目初始化脚本
# 由无限开发工作流自动生成

set -e

echo "=========================================="
echo "  项目初始化"
echo "=========================================="
echo ""

# 检测项目类型
if [ -f "package.json" ]; then
    echo "检测到 Node.js 项目"
    echo ""

    # 安装依赖
    if [ -f "yarn.lock" ]; then
        echo "使用 yarn 安装依赖..."
        yarn install
    elif [ -f "pnpm-lock.yaml" ]; then
        echo "使用 pnpm 安装依赖..."
        pnpm install
    else
        echo "使用 npm 安装依赖..."
        npm install
    fi

    # 启动开发服务器
    echo ""
    echo "启动开发服务器..."
    if [ -f "node_modules/.bin/vite" ]; then
        npm run dev
    elif [ -f "node_modules/.bin/next" ]; then
        npm run dev
    else
        npm start
    fi

elif [ -f "requirements.txt" ]; then
    echo "检测到 Python 项目"
    echo ""

    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        echo "创建虚拟环境..."
        python3 -m venv venv
    fi

    # 激活虚拟环境
    source venv/bin/activate

    # 安装依赖
    echo "安装依赖..."
    pip install -r requirements.txt

    # 启动服务器
    echo ""
    echo "启动服务器..."
    if [ -f "main.py" ]; then
        python main.py
    elif [ -f "app.py" ]; then
        python app.py
    else
        echo "请手动启动服务器"
    fi

elif [ -f "go.mod" ]; then
    echo "检测到 Go 项目"
    echo ""

    # 下载依赖
    echo "下载依赖..."
    go mod download

    # 运行
    echo ""
    echo "运行项目..."
    go run main.go

else
    echo "未检测到已知的项目类型"
    echo "请手动配置项目"
fi

echo ""
echo "=========================================="
echo "  初始化完成"
echo "=========================================="
