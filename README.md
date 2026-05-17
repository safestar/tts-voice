# TTS 文本转语音技能

使用 StepFun StepAudio 2.5 API 将文本转换为高质量自然语音。

## 核心能力

| 功能 | 说明 |
|-----|------|
| 文本转语音 | 300+ 预设音色，20+ 情绪表达 |
| 音色复刻 | 上传 5-10秒音频创建自定义音色 |
| 语速控制 | 0.5 - 2.0 倍速调节 |
| 情绪指令 | 自然语言描述语气风格 |
| 多语言 | 中英粤语四川话等12种方言 |
| 零样本复刻 | 保持音色特征，自由调整情感 |

## 安装

```bash
pip install requests
```

## 配置

设置环境变量：

```bash
export STEP_API_KEY="您的API密钥"
```

获取 API Key：https://platform.stepfun.com

## 使用方法

### 文本转语音

```bash
# 基本用法
python3 tts_tool.py "要转换的文本"

# 指定参数
python3 tts_tool.py --voice wenrounansheng --speed 1.0 --instruction "语气自然" "文本内容"

# 从文件读取
python3 tts_tool.py --file text.txt

# 不自动播放
python3 tts_tool.py --no-play "文本"
```

**参数说明：**

| 参数 | 默认值 | 说明 |
|-----|--------|------|
| `--voice` | 自定义音色 | 音色 ID |
| `--speed` | 0.9 | 语速倍率 (0.5-2.0) |
| `--instruction` | 幽默风格 | 语气指令（≤200字符） |
| `--file` | - | 从文件读取文本 |
| `--no-play` | false | 不自动播放 |

### 音色复刻

```bash
# 一键复刻（上传+创建）
python3 voice_clone.py voice.mp3 --text "音频对应的文本"

# 测试复刻音色
python3 voice_clone.py --test voice-xyz789 --test-text "测试文本"
```

**音频要求：**

| 项目 | 要求 |
|-----|------|
| 格式 | mp3、wav |
| 时长 | 5-10 秒 |
| 大小 | ≤128MB |
| 内容 | 清晰人声，无背景噪音 |

**复刻成功后使用：**

```bash
python3 tts_tool.py --voice voice-xyz789 "测试自定义音色"
```

## 预设音色

| 音色 ID | 描述 |
|--------|------|
| `wenrounansheng` | 温柔男声 |
| `cixingnansheng` | 知性男声 |
| `wenrounvsheng` | 温柔女声 |

完整列表见：https://platform.stepfun.com/docs

## API 端点

| 功能 | URL |
|-----|-----|
| TTS | `https://api.stepfun.com/step_plan/v1/audio/speech` |
| 音色复刻 | `https://api.stepfun.com/step_plan/v1/audio/voices` |
| 文件上传 | `https://api.stepfun.com/v1/files` |

## 文件结构

```
tts/
├── tts_tool.py      # 文本转语音
├── voice_clone.py   # 音色复刻
├── file_upload.py   # 文件上传
└── SKILL.md         # Claude Code 技能定义
```

## 示例

```bash
# 新闻播报风格
python3 tts_tool.py --instruction "严肃正式，新闻播报语气" "今日要闻如下"

# 讲故事风格
python3 tts_tool.py --instruction "温柔讲述，情感适中" "从前有座山"

# 开心风格
python3 tts_tool.py --instruction "开心兴奋，语速稍快" "今天是个好日子"
```

## 注意事项

- 单次文本最大 1000 字符
- 超长文本自动分段生成
- 音频输出默认保存到桌面
- macOS 自动播放，其他系统手动播放

---

**API 文档**：https://platform.stepfun.com/docs/zh/api-reference/audio/speech