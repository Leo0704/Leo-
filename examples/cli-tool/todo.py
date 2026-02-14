#!/usr/bin/env python3
"""
简单的命令行待办工具

用法:
    python todo.py add "任务内容"    # 添加任务
    python todo.py list             # 列出所有任务
    python todo.py done <编号>      # 完成任务
    python todo.py delete <编号>    # 删除任务
"""

import json
import sys
from pathlib import Path

DATA_FILE = Path.home() / ".todo_cli.json"


def load_todos():
    """加载任务列表"""
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_todos(todos):
    """保存任务列表"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2, ensure_ascii=False)


def add_todo(text):
    """添加任务"""
    todos = load_todos()
    todos.append({"text": text, "done": False})
    save_todos(todos)
    print(f"✓ 已添加: {text}")


def list_todos():
    """列出所有任务"""
    todos = load_todos()
    if not todos:
        print("暂无任务")
        return

    for i, todo in enumerate(todos, 1):
        status = "✓" if todo["done"] else "○"
        print(f"  {i}. [{status}] {todo['text']}")


def done_todo(index):
    """完成任务"""
    todos = load_todos()
    if 1 <= index <= len(todos):
        todos[index - 1]["done"] = True
        save_todos(todos)
        print(f"✓ 已完成: {todos[index - 1]['text']}")
    else:
        print("错误: 无效的编号")


def delete_todo(index):
    """删除任务"""
    todos = load_todos()
    if 1 <= index <= len(todos):
        text = todos.pop(index - 1)["text"]
        save_todos(todos)
        print(f"✓ 已删除: {text}")
    else:
        print("错误: 无效的编号")


def print_help():
    """打印帮助"""
    print(__doc__)


def main():
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) < 3:
            print("用法: python todo.py add \"任务内容\"")
        else:
            add_todo(sys.argv[2])
    elif command == "list":
        list_todos()
    elif command == "done":
        if len(sys.argv) < 3:
            print("用法: python todo.py done <编号>")
        else:
            done_todo(int(sys.argv[2]))
    elif command == "delete":
        if len(sys.argv) < 3:
            print("用法: python todo.py delete <编号>")
        else:
            delete_todo(int(sys.argv[2]))
    else:
        print_help()


if __name__ == "__main__":
    main()
