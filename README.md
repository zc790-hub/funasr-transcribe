# funasr-transcribe · 本地语音转文字 Skill

**中文** | [English](#english)

一个 **Agent Skill**（[什么是 Skill](https://docs.claude.com/en/docs/claude-code/skills)）。把录音（m4a / mp3 / wav…）转成文字，可进一步整理成
结构化会议记录。基于 [FunASR](https://github.com/modelscope/FunASR) + SenseVoiceSmall，
**完全本地运行、不上传云端、不需要 API Key**。

**不挑厂商、不调任何大模型 API、不用 API Key**——模型在本地跑，因此 Claude Code、
OpenClaw、WorkBuddy 等任何能读 [Agent Skills](https://docs.claude.com/en/docs/claude-code/skills)
的 agent 都能用，装进对应的 skills 目录即可。

## 它能做什么

- 中文为主、支持 50+ 语言的语音识别（SenseVoiceSmall）
- 自动切分长音频（VAD）、自动加标点、自动去语气词
- 任意音频格式自动转码（ffmpeg / macOS afconvert）
- 设备自动选择：Apple Silicon (MPS) / NVIDIA (CUDA) / CPU

## 一键安装（推荐）

```bash
curl -fsSL https://raw.githubusercontent.com/zc790-hub/funasr-transcribe/main/install.sh | bash
```

自动探测你的 skills 目录（`~/.claude/skills` 或 `~/.workbuddy/skills`）、clone 进去、
装好运行环境。需 Python 3.9–3.11。首次转写时自动下载模型（约 1.2G），之后离线可用。

**用别的 agent / 自定义目录**：把目录作为参数或环境变量传进去即可——

```bash
bash install.sh ~/你的agent/skills
# 或
SKILLS_DIR=~/你的agent/skills bash install.sh
```

## 让 agent 自己装（把下面整段复制给你的 agent）

> 请帮我安装并使用这个语音转文字 skill：https://github.com/zc790-hub/funasr-transcribe
> 把它 clone 进我的 skills 目录（Claude Code 是 `~/.claude/skills/`），然后运行其中的
> `setup.sh` 装好环境。装完用自带的 `examples/asr_example.wav` 跑一次确认能用
> （期望输出「每一天都要快乐。」）。之后我给你音频文件时，按 SKILL.md 帮我转写。

## 手动安装

```bash
# 1. clone 进 skills 目录
git clone https://github.com/zc790-hub/funasr-transcribe \
  ~/.claude/skills/funasr-transcribe
# 2. 装环境
bash ~/.claude/skills/funasr-transcribe/setup.sh
```

## 验证装好没（自检）

```bash
source <skill目录>/venv/bin/activate
python <skill目录>/scripts/transcribe.py <skill目录>/examples/asr_example.wav
# 期望输出：每一天都要快乐。
```

## 直接命令行用

```bash
source <skill目录>/venv/bin/activate
python <skill目录>/scripts/transcribe.py 录音.m4a --out 结果.txt
```

| 参数 | 说明 |
|---|---|
| `--out FILE` | 结果写入文件（默认只打印到屏幕） |
| `--no-punc` | 不加标点，更快 |
| `--keep-fillers` | 保留「嗯/啊」等语气词 |

## 通过 agent 用

装好后直接对 agent 说「把这段录音转成文字」「帮我转写会议录音」即可，
agent 会读 [SKILL.md](SKILL.md) 自动跑完转写 → 整理流程。

## 可选

- 整理成结构化会议记录：见 [SKILL.md](SKILL.md) 第 2 节
- **上传到云文档**：转写默认输出到屏幕（`--out` 可存 txt）。如果你想再把结果上传到
  金山文档 / 飞书 / Notion 等，自己接对应平台的 CLI 即可——这是个人工作流，
  没有封进 skill。

## 常见问题

- **首次很慢 / 卡在下载**：在下模型（约 1.2G），看终端进度即可。
- **2G 模型没下完就中断了**：直接**重新运行**转写命令——ModelScope 会从已下载的缓存
  断点续传，不会从头来。确认网络通畅、磁盘有约 3G 空间（venv 845M + 模型 1.2G）。
  国内网络慢可设镜像加速：`export MODELSCOPE_DOMAIN=www.modelscope.cn` 后重试。
- **`~/.modelscope` 权限错误**：脚本已把缓存改到 skill 目录；仍报错就
  `export FUNASR_CACHE=/某个可写路径` 再跑。
- **非 macOS 且没 ffmpeg**：先把音频转成 16k WAV，或装 ffmpeg。

## 模型与致谢

本 skill 只是把下面这些开源项目/模型串成一条好用的流程，**模型本身是它们的功劳**：

- **[FunASR](https://github.com/modelscope/FunASR)**（阿里巴巴达摩院，MIT 许可）——语音识别框架
- **SenseVoiceSmall**（`iic/SenseVoiceSmall`）——主 ASR 模型
- **fsmn-vad**（`iic/speech_fsmn_vad_zh-cn-16k-common-pytorch`）——语音端点检测
- **punc_ct-transformer**（`iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch`）——标点恢复

模型均托管在 [ModelScope](https://www.modelscope.cn/)（命名空间 `iic` = 阿里巴巴达摩院），
首次运行自动下载。各模型的具体许可请以其 ModelScope 页面为准。

## 许可

本仓库代码：[MIT](LICENSE)。所用模型的许可见上面「模型与致谢」中各自页面。

---

## English

A **local speech-to-text Agent Skill**. Transcribes audio (m4a / mp3 / wav…) to text and
can further organize it into structured meeting notes. Powered by
[FunASR](https://github.com/modelscope/FunASR) + SenseVoiceSmall —
**fully local, nothing uploaded, no API key needed**.

**Vendor-agnostic — no LLM API, no API key.** The model runs locally, so any agent that
reads [Agent Skills](https://docs.claude.com/en/docs/claude-code/skills) works — Claude Code,
OpenClaw, WorkBuddy, etc. Just drop it into that agent's skills directory.

### Features

- Speech recognition for Chinese + 50 other languages (SenseVoiceSmall)
- Auto-segments long audio (VAD), adds punctuation, strips filler words
- Auto-transcodes any audio format (ffmpeg / macOS afconvert)
- Auto device selection: Apple Silicon (MPS) / NVIDIA (CUDA) / CPU

### One-line install

```bash
curl -fsSL https://raw.githubusercontent.com/zc790-hub/funasr-transcribe/main/install.sh | bash
```

Auto-detects your skills dir, clones, and sets up the environment. Needs Python 3.9–3.11.
Models (~1.2G) download on first transcription, then run offline.

**Other agents / custom dir**: pass it as an arg or env var —

```bash
bash install.sh ~/your-agent/skills
# or
SKILLS_DIR=~/your-agent/skills bash install.sh
```

### Let your agent install it (paste this to your agent)

> Please install and use this speech-to-text skill:
> https://github.com/zc790-hub/funasr-transcribe — clone it into my skills directory
> (`~/.claude/skills/` for Claude Code), run its `setup.sh`, then verify with the bundled
> `examples/asr_example.wav`. After that, transcribe audio files I give you per SKILL.md.

### Manual install

```bash
git clone https://github.com/zc790-hub/funasr-transcribe \
  ~/.claude/skills/funasr-transcribe
bash ~/.claude/skills/funasr-transcribe/setup.sh
```

### Verify

```bash
source <skill_dir>/venv/bin/activate
python <skill_dir>/scripts/transcribe.py <skill_dir>/examples/asr_example.wav
# Expected output: 每一天都要快乐。
```

### CLI usage

```bash
python <skill_dir>/scripts/transcribe.py audio.m4a --out result.txt
```

| Flag | Meaning |
|---|---|
| `--out FILE` | Write result to file (default: print to stdout) |
| `--no-punc` | Skip punctuation (faster) |
| `--keep-fillers` | Keep filler words |

### Troubleshooting

- **Slow / stuck on first run**: downloading models (~1.2G); watch the terminal progress.
- **2G download interrupted**: just re-run — ModelScope resumes from cached partial files.
  Ensure network is up and you have ~3G free disk (venv 845M + models 1.2G).
- **`~/.modelscope` permission error**: cache is already redirected into the skill dir; if it
  still fails, `export FUNASR_CACHE=/some/writable/path` and retry.

### Models & credits

This skill just wires up existing open-source projects/models — the models are their work:

- **[FunASR](https://github.com/modelscope/FunASR)** (Alibaba DAMO Academy, MIT) — ASR framework
- **SenseVoiceSmall** (`iic/SenseVoiceSmall`) — main ASR model
- **fsmn-vad** — voice activity detection
- **punc_ct-transformer** — punctuation restoration

Models are hosted on [ModelScope](https://www.modelscope.cn/) (`iic` = Alibaba DAMO Academy)
and downloaded on first run. See each model's ModelScope page for its license.

### License

This repo's code: [MIT](LICENSE). Model licenses: see "Models & credits" above.
