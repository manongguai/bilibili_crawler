#!/bin/bash
# Claude Code 环境安装脚本
# 自动安装 Node.js、Claude Code CLI 和配置 API

set -e

echo "🚀 开始安装 Claude Code 环境..."

# 检测操作系统
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
else
    echo "❌ 不支持的操作系统: $OSTYPE"
    exit 1
fi

echo "📍 检测到操作系统: $OS"

# 检查是否已安装 Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js 已安装: $NODE_VERSION"
else
    echo "📦 安装 Node.js..."

    if [[ "$OS" == "macOS" ]]; then
        # macOS 使用 Homebrew
        if command -v brew &> /dev/null; then
            brew install node
        else
            echo "❌ 请先安装 Homebrew: https://brew.sh/"
            exit 1
        fi
    else
        # Linux 使用 nvm
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
        nvm install node
    fi
fi

# 安装 Claude Code CLI
echo "📦 安装 Claude Code CLI..."
npm install -g @anthropic-ai/claude-code

# 配置环境变量
echo "⚙️ 配置环境变量..."

# Claude Code 配置目录
CONFIG_DIR="$HOME/.claude"
mkdir -p "$CONFIG_DIR"

# 创建配置文件
cat > "$CONFIG_DIR/claude_code_config.json" << EOF
{
  "default_model": "claude-sonnet-4",
  "max_tokens": 4096,
  "temperature": 0.3
}
EOF

echo "✅ 配置文件已创建: $CONFIG_DIR/claude_code_config.json"

# 提示配置 API
echo ""
echo "🔑 接下来请配置 API 密钥："
echo "1. 访问 https://console.anthropic.com/"
echo "2. 注册或登录账号"
echo "3. 获取 API 密钥"
echo "4. 运行: claude-code auth login"
echo ""

echo "🎉 Claude Code 环境安装完成！"
echo ""
echo "📚 使用说明："
echo "- claude-code --help    # 查看帮助"
echo "- claude-code auth login   # 登录账号"
echo "- claude-code            # 启动交互模式"