#!/usr/bin/env bash
# 一键安装 funasr-transcribe：把 skill 装进任意 agent 的 skills 目录。
#
# 用法：
#   curl -fsSL https://raw.githubusercontent.com/zc790-hub/funasr-transcribe/main/install.sh | bash
#   bash install.sh                         # 自动探测目录
#   bash install.sh ~/.claude/skills        # 指定目录（任意 agent）
#   SKILLS_DIR=~/某agent/skills bash install.sh   # 用环境变量指定
set -euo pipefail

REPO_URL="https://github.com/zc790-hub/funasr-transcribe.git"
NAME="funasr-transcribe"

# 目标 skills 目录，优先级：显式指定 > 自动探测已存在的 > 默认 ~/.claude/skills
SKILLS_DIR="${SKILLS_DIR:-${1:-}}"
if [ -z "$SKILLS_DIR" ]; then
  for d in "$HOME/.claude/skills" "$HOME/.workbuddy/skills"; do
    [ -d "$d" ] && SKILLS_DIR="$d" && break
  done
fi
SKILLS_DIR="${SKILLS_DIR:-$HOME/.claude/skills}"
mkdir -p "$SKILLS_DIR"
echo "📁 安装到: $SKILLS_DIR/$NAME"
echo "   （装到别处可：bash install.sh <你的skills目录>  或  SKILLS_DIR=... ）"

# clone（已存在则更新）
TARGET="$SKILLS_DIR/$NAME"
if [ -d "$TARGET/.git" ]; then
  echo "🔄 已存在，拉取最新..."
  git -C "$TARGET" pull --ff-only
else
  git clone --depth 1 "$REPO_URL" "$TARGET"
fi

# 装环境
echo "📦 初始化运行环境..."
bash "$TARGET/setup.sh"

echo ""
echo "🎉 安装完成。验证一下："
echo "   source \"$TARGET/venv/bin/activate\""
echo "   python \"$TARGET/scripts/transcribe.py\" \"$TARGET/examples/asr_example.wav\""
echo "   # 期望输出：每一天都要快乐。"
echo ""
echo "之后对你的 agent 说「把这段录音转成文字」即可。"
