---
description: 运行测试并报告结果
Argument-hint: [可选：测试文件或目录路径]
Allowed-tools: Bash
---

# 运行测试

## 参数

$ARGUMENTS

## 执行

1. 如果提供了参数，运行指定测试
2. 否则，运行所有测试

## 测试命令

尝试以下命令（按优先级）：
- `python -m pytest` - pytest
- `npm test` - Node.js
- `cargo test` - Rust

## 输出

报告：
- 测试数量
- 通过/失败数量
- 失败的测试详情（如果有）
