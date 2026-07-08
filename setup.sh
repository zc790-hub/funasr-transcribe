#!/usr/bin/env bash
# 一键初始化 funasr-transcribe 运行环境。
# 在 skill 目录下建 venv 并装好依赖；模型在首次转写时自动下载。
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SKILL_DIR/venv"

echo "📁 Skill 目录: $SKILL_DIR"

# 找一个 3.9–3.11 的解释器（funasr/torch 在这些版本上最稳；
# macOS 上避开 3.13 的 managed-Python 代码签名冲突）。
PY=""
for c in python3.11 python3.10 python3.9 python3; do
  if command -v "$c" >/dev/null 2>&1; then
    v="$("$c" -c 'import sys;print("%d%d"%sys.version_info[:2])' 2>/dev/null || echo 0)"
    if [ "$v" -ge 39 ] && [ "$v" -le 311 ]; then PY="$c"; break; fi
  fi
done
if [ -z "$PY" ]; then
  echo "❌ 未找到 Python 3.9–3.11。请先安装（如 brew install python@3.11）后重试。"
  exit 1
fi
echo "🐍 使用 $PY ($("$PY" --version 2>&1))"

if [ ! -d "$VENV" ]; then
  "$PY" -m venv "$VENV"
  echo "✅ 已创建 venv: $VENV"
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"
python -m pip install --upgrade pip >/dev/null
echo "📦 安装依赖（torch 体积较大，请耐心）..."
pip install -r "$SKILL_DIR/requirements.txt"

# 可选：装 ffmpeg 以支持任意格式音频（macOS 已自带 afconvert 可兜底）
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ℹ️  未检测到 ffmpeg。macOS 下可用自带 afconvert；其它平台建议安装 ffmpeg。"
fi

echo ""
echo "🎉 安装完成。用法："
echo "   source \"$VENV/bin/activate\""
echo "   python \"$SKILL_DIR/scripts/transcribe.py\" 你的音频.m4a --out 结果.txt"
