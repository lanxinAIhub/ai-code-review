# 🤖 AI Code Review

> AI 自动评审代码工具：Bug检测、安全扫描、代码风格分析

[![Code Review](https://github.com/lanxinAIhub/ai-code-review/actions/workflows/code-review.yml/badge.svg)](https://github.com/lanxinAIhub/ai-code-review/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## ✨ 功能特性

- 🔍 **Bug 检测** — 逻辑错误、空指针、边界条件
- 🔒 **安全扫描** — SQL注入、XSS、敏感信息泄露
- 🎨 **代码风格** — 命名规范、注释质量、函数长度
- ⚡ **性能分析** — 循环优化、I/O效率
- 🔧 **GitHub Actions 集成** — PR 自动评论评审结果
- 🌐 **多 API 支持** — Claude / OpenAI / MiniMax

## 🚀 快速开始

### 1. 安装

```bash
git clone https://github.com/lanxinAIhub/ai-code-review.git
cd ai-code-review
pip install requests
```

### 2. 配置 API Key

```bash
# MiniMax (默认)
export MINIMAX_API_KEY="your_key"

# 或 Claude
export ANTHROPIC_API_KEY="your_key"

# 或 OpenAI
export OPENAI_API_KEY="your_key"
```

### 3. 评审代码

```bash
# 评审单个文件
python3 src/reviewer.py path/to/file.py

# 评审整个目录
python3 src/reviewer.py path/to/project --provider minimax

# 使用 Claude
python3 src/reviewer.py . --provider claude

# 使用 OpenAI
python3 src/reviewer.py . --provider openai
```

或使用便捷脚本：

```bash
chmod +x review.sh
./review.sh path/to/project --provider minimax
```

## 🐙 GitHub Actions 集成

### 方式一：使用本仓库的 Actions（推荐）

在你的仓库添加 `.github/workflows/ai-review.yml`：

```yaml
name: AI Code Review

on:
  pull_request:
  push:

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: lanxinAIhub/ai-code-review@v1
        with:
          provider: minimax
        env:
          MINIMAX_API_KEY: ${{ secrets.MINIMAX_API_KEY }}
```

### 方式二：在本仓库启用 Actions

本仓库已配置 Actions，PR 或 push 时自动评审。

**在 GitHub Settings 中添加 Secrets：**
- `MINIMAX_API_KEY` — MiniMax API Key
- `ANTHROPIC_API_KEY` — Anthropic API Key  
- `OPENAI_API_KEY` — OpenAI API Key

## 📊 评审报告示例

```
# 🤖 AI Code Review Report

**评审时间**: 2026-04-26
**评审文件数**: 5
**发现问题数**: 3 (🔴高:1 | 🟡中:2 | 🟢低:0)

---

### ⚠️ src/auth.py (Python)
> 评分: 72/100 | 存在安全隐患

- 🔴 安全 [L42]: 硬编码密码: `password = "admin123"`
  - 💡 建议: 使用环境变量或密钥管理服务
- 🟡 Bug [L38]: 潜在空指针: `user.name` 未做空检查
  - 💡 建议: 添加 `if not user:` 防御性检查
- 🟡 性能 [L15]: 重复数据库查询: 可使用缓存
  - 💡 建议: 引入 Redis 缓存热点数据
```

## 🛠 项目结构

```
ai-code-review/
├── src/
│   └── reviewer.py      # 核心评审模块
├── scripts/             # 辅助脚本
├── .github/
│   └── workflows/
│       └── code-review.yml  # GitHub Actions
├── review.sh            # 一键评审脚本
└── README.md
```

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📝 许可

[MIT License](LICENSE)
