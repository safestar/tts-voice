---
name: tts
description: 文本转语音工具。使用 StepFun StepAudio 2.5 TTS API 将文本转换为自然语音，支持300+音色、20种情绪表达、多语言方言、语速控制、音色复刻等高级功能。适用于配音、有声内容、智能交互。关键词：语音合成、TTS、配音、朗读、转语音、StepFun、StepAudio、音色复刻
trigger: 当用户需要将文字转成语音、生成配音、朗读文本、复刻音色时
---

# 文本转语音 (TTS) 技能

使用 StepFun StepAudio 2.5 TTS API 将文本转换为高质量自然语音。

## 核心能力

| 能力 | 说明 |
|------|------|
| 全局语境控制 | 定义整段语音的情感基调、角色状态、场景氛围 |
| 文中语境控制 | 逐帧调节语气强度、语速节奏、停顿位置 |
| 零样本复刻 | 保持音色特征不变，自由调整情感与风格 |
| 音色复刻 | 上传5~10秒音频，创建自定义音色 |
| 300+ 预设音色 | 新闻主播、卡通角色、老年嗓音等 |
| 20+ 情绪表达 | 开心、悲伤、愤怒、平静、兴奋等 |
| 多语言支持 | 中英文、粤语、四川话等12种方言 |

## 功能模块

### 1. 文本转语音 (tts_tool.py)

将文本转换为语音文件。

```
python3 tts_tool.py [文本] --voice <音色> --speed <语速> --instruction <指令>
```

### 2. 音色复刻 (voice_clone.py)

上传音频文件，创建自定义音色。

```
python3 voice_clone.py <音频文件> --text <音频文本>
```

### 3. 文件上传 (file_upload.py)

上传文件获取 file_id。

```
python3 file_upload.py <文件> --purpose storage
```

---

## 文本转语音

### 基本用法

```
/tts [文本内容]
```

### 指定参数

```
/tts --voice <音色> --speed <语速> --instruction <指令> [文本内容]
```

### 参数说明

| 参数 | 默认值 | 说明 | 可选值 |
|------|--------|------|--------|
| `voice` | `wenrounansheng` | 音色类型 | 预设音色或复刻音色ID |
| `speed` | `1.0` | 语速倍率 | 0.5 - 2.0 |
| `instruction` | `语气自然` | 全局指导 | 自然语言描述（≤200字符） |

### 音色列表

**男声：**
- `wenrounansheng` - 温柔男声（默认） ★
- `cixingnansheng` - 知性男声

**女声：**
- `wenrounvsheng` - 温柔女声

**自定义音色：** 通过音色复刻功能创建，使用返回的 `voice_id`

### 情绪控制示例

```bash
# 开心风格
python3 tts_tool.py --instruction "开心兴奋，语速稍快" "今天是个好日子！"

# 讲故事风格
python3 tts_tool.py --instruction "温柔讲述，绝对符合真人发声，杜绝生硬机械，发音准确，二声四声柔和，情感适中" "从前有座山..."

# 新闻播报
python3 tts_tool.py --instruction "严肃正式，新闻播报语气" "今日要闻如下..."
```

### 文本长度限制

- 单次最大 **1000 字符**
- 超长文本自动分段生成

---

## 音色复刻

### 要求

| 项目 | 要求 |
|------|------|
| 音频格式 | mp3、wav |
| 音频时长 | **5~10 秒** |
| 文件大小 | ≤128MB |
| 音频内容 | 清晰人声，无背景噪音 |

### 一键复刻

```bash
# 上传音频并复刻音色（推荐提供文本）
python3 voice_clone.py voice.mp3 --text "大家好，欢迎来到我的频道"

# 仅复刻（已有 file_id）
python3 voice_clone.py --file-id file-abc123 --text "欢迎光临"
```

### 模型选择

| 模型 | 说明 |
|------|------|
| `step-tts-mini` | 轻量级模型（推荐，速度快） |
| `step-tts-2` | 高质量模型 |

### 测试音色

```bash
# 测试复刻的音色
python3 voice_clone.py --test voice-xyz789 --test-text "这是测试语音"
```

### 使用复刻音色

复刻成功后，将返回的 `音色ID` 用于 TTS：

```bash
python3 tts_tool.py --voice voice-xyz789 "你好，这是我的自定义音色"
```

---

## 执行步骤

### TTS 生成
1. 解析文本和参数
2. 构建 API 请求
3. 调用 StepFun API
4. 保存音频文件
5. 自动播放（macOS）

### 音色复刻
1. 上传音频文件获取 file_id
2. 调用复刻 API 创建音色
3. 返回音色 ID
4. 可选：测试音色效果

---

## API 配置

| 配置项 | 值 |
|--------|-----|
| TTS API | `https://api.stepfun.com/step_plan/v1/audio/speech` |
| 音色复刻 | `https://api.stepfun.com/step_plan/v1/audio/voices` |
| 文件上传 | `https://api.stepfun.com/v1/files` |
| TTS 模型 | `stepaudio-2.5-tts` |

## 环境配置

首次使用需设置 API Key：

```bash
export STEP_API_KEY="您的API密钥"
```

获取 API Key: https://platform.stepfun.com