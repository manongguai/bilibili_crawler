# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个 Python 学习项目，包含多个简单的计算器应用程序和基础示例。项目结构简洁，主要用于 Python 基础学习和小型应用程序开发练习。

## 项目结构

```
python_project/
├── 01_helloworld.py          # Python 基础示例
├── sum_calculator.py         # 加法计算器
├── difference_calculator.py  # 减法计算器
└── claude_code_env.sh        # Claude Code 环境安装脚本
```

## 运行 Python 脚本

所有 Python 脚本都可以直接运行：

```bash
# 运行加法计算器
python sum_calculator.py

# 运行减法计算器
python difference_calculator.py

# 运行基础示例
python 01_helloworld.py
```

## 代码架构说明

### 计算器应用程序模式

项目中的计算器应用遵循统一的架构模式：

1. **核心函数**：每个计算器都包含一个执行计算的核心函数
   - `add_numbers(a, b)` - 加法计算
   - `calculate_difference(a, b)` - 减法计算

2. **交互式界面**：所有计算器都提供命令行交互界面
   - 使用 `input()` 获取用户输入
   - 包含输入验证和异常处理
   - 支持优雅退出（Ctrl+C）

3. **异常处理**：
   - `ValueError` - 处理无效的数字输入
   - `KeyboardInterrupt` - 处理用户中断操作
   - 通用异常捕获作为最后保障

### 代码质量标准

- **文档字符串**：所有核心函数都包含完整的 docstring
- **类型提示**：函数参数和返回值使用类型注解
- **错误处理**：包含完善的异常处理机制
- **用户友好**：提供清晰的错误提示和操作指导

## 开发注意事项

1. **项目依赖**：此项目不依赖任何外部包，仅使用 Python 标准库
2. **Python 版本**：建议使用 Python 3.6+ 以支持类型提示
3. **代码风格**：遵循 PEP 8 规范
4. **测试**：当前项目没有测试套件，建议为新增功能添加单元测试

## 添加新的计算器

当添加新的计算器功能时，请遵循现有的模式：

1. 创建核心计算函数，包含类型提示和文档字符串
2. 实现交互式命令行界面
3. 添加完整的异常处理
4. 使用 `if __name__ == "__main__":` 保护主程序逻辑
5. 确保用户输入验证和友好的错误提示