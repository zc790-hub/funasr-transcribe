#!/usr/bin/env python3
"""
FunASR 语音转文字 —— 可移植版

用法:
    python3 transcribe.py <音频文件> [--out result.txt] [--keep-fillers] [--no-punc] [--spk]

支持任意常见音频格式（m4a/mp3/wav/...）。非 16k WAV 会自动用 ffmpeg
（找不到则退回 macOS 的 afconvert）转码后再识别。

模型缓存默认放在 skill 目录下的 .modelscope/，首次运行会自动从 ModelScope
下载（约 1.2G），之后走本地缓存。可用环境变量 FUNASR_CACHE 覆盖缓存位置。
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

# ---- 路径自适应：以本脚本所在 skill 目录为锚点 ----
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.environ.get("FUNASR_CACHE") or os.path.join(SKILL_DIR, ".modelscope")
os.makedirs(CACHE_DIR, exist_ok=True)

# 必须在 import funasr/modelscope 之前设置缓存路径，否则会写到 ~/.modelscope，
# 在沙箱里可能被拒。
os.environ["MODELSCOPE_CACHE"] = CACHE_DIR

FILLERS = ['嗯', '啊', '呃', '哎', '喔', '噢', '啦', '呗', '咯', '呵', '呀', '哦', '唔',
           'um', 'uh']


def convert_to_wav16k(src: str) -> str:
    """把任意音频转成 16k 单声道 WAV，返回临时文件路径。"""
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    if shutil.which("ffmpeg"):
        cmd = ["ffmpeg", "-y", "-i", src, "-ar", "16000", "-ac", "1",
               "-f", "wav", tmp.name]
    elif shutil.which("afconvert"):  # macOS 自带
        cmd = ["afconvert", src, tmp.name, "-d", "LEI16@16000", "-f", "WAVE"]
    else:
        os.unlink(tmp.name)
        sys.exit("❌ 需要 ffmpeg（或 macOS afconvert）来转码音频，请先安装 ffmpeg")
    subprocess.run(cmd, check=True, capture_output=True)
    return tmp.name


def pick_device():
    import torch
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio", help="音频文件路径")
    ap.add_argument("--out", help="把结果写入该文件（默认只打印到 stdout）")
    ap.add_argument("--keep-fillers", action="store_true", help="保留嗯/啊等语气词")
    ap.add_argument("--no-punc", action="store_true", help="不加标点（更快）")
    ap.add_argument("--spk", action="store_true",
                    help="说话人分离（cam++ 声纹模型），输出带 [说话人N] 标注")
    args = ap.parse_args()

    if not os.path.exists(args.audio):
        sys.exit(f"❌ 文件不存在: {args.audio}")

    # ModelScope 凭证路径也指到缓存目录
    from modelscope.hub.api import ModelScopeConfig
    ModelScopeConfig.path_credential = CACHE_DIR

    from funasr import AutoModel

    # 非 wav 一律转码
    tmp_wav = None
    audio = args.audio
    if not audio.lower().endswith(".wav"):
        print(f"🔄 转码 {os.path.basename(audio)} → 16k WAV ...", file=sys.stderr)
        tmp_wav = convert_to_wav16k(audio)
        audio = tmp_wav

    device = pick_device()
    print(f"🔥 设备: {device}", file=sys.stderr)
    print("⏳ 加载模型（首次会自动下载约 1.2G）...", file=sys.stderr)

    model_kwargs = dict(
        model="iic/SenseVoiceSmall",      # 主 ASR，50+ 语言，中文优秀
        vad_model="fsmn-vad",             # 端点检测，自动切分长音频
        device=device,
        disable_update=True,
    )
    if not args.no_punc:
        # 标点恢复
        model_kwargs["punc_model"] = "iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch"
    if args.spk:
        # 说话人分离：按音色聚类，给每句话标上说话人编号
        model_kwargs["spk_model"] = "cam++"

    model = AutoModel(**model_kwargs)

    print("✅ 模型就绪，开始转写（长音频请耐心等待）...", file=sys.stderr)
    result = model.generate(input=audio)

    if tmp_wav:
        os.unlink(tmp_wav)

    def clean(t: str) -> str:
        t = re.sub(r'<\|[^>]+\|>', '', t).strip()  # 去掉 <|zh|><|NEUTRAL|> 等标记
        if not args.keep_fillers:
            for f in FILLERS:
                t = t.replace(f, '')
        return t

    # ---- 说话人分离输出（--spk）----
    if args.spk:
        lines = []
        for item in (result if isinstance(result, list) else [result]):
            if not isinstance(item, dict):
                continue
            for seg in item.get("sentence_info") or []:
                t = clean(seg.get("text", ""))
                if t:
                    lines.append(f"[说话人{seg.get('spk', '?')}] {t}")
        if lines:
            text = "\n".join(lines)
            print(text)
            if args.out:
                with open(args.out, "w", encoding="utf-8") as fh:
                    fh.write(text)
                print(f"\n💾 已写入 {args.out}", file=sys.stderr)
            return
        print("⚠️  未拿到说话人信息，改用普通输出", file=sys.stderr)

    # ---- 普通输出 ----
    parts = []
    for item in (result if isinstance(result, list) else [result]):
        t = item.get("text", "") if isinstance(item, dict) else str(item)
        t = clean(t)
        if t:
            parts.append(t)
    text = "".join(parts)
    if not args.keep_fillers:
        text = re.sub(r'\s+', '', text) if not re.search(r'[a-zA-Z]', text) else text

    print(text)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"\n💾 已写入 {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
