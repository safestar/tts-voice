#!/usr/bin/env python3
"""
StepFun 音色复刻工具
上传音频文件并复刻音色，获取音色ID用于TTS
API 文档: https://platform.stepfun.com/docs/zh/api-reference/audio/voices
"""

import os
import sys
import argparse
import json
from pathlib import Path

try:
    import requests
except ImportError:
    print("请先安装 requests: pip install requests")
    sys.exit(1)

# API 配置
FILES_API_URL = "https://api.stepfun.com/v1/files"
VOICES_API_URL = "https://api.stepfun.com/step_plan/v1/audio/voices"
API_KEY = os.environ.get("STEP_API_KEY", "")

# 支持的音频格式
AUDIO_FORMATS = ['.mp3', '.wav']

# 可用模型
MODELS = {
    "stepaudio-2.5-tts": "高质量TTS模型（推荐）",
    "step-tts-2": "高质量TTS模型",
    "step-tts-mini": "轻量级TTS模型"
}


def upload_audio(file_path: str) -> str:
    """
    上传音频文件用于音色复刻

    Args:
        file_path: 音频文件路径（mp3/wav，时长5~10秒）

    Returns:
        file_id: 上传成功后的文件ID
    """
    if not API_KEY:
        raise ValueError("请设置 STEP_API_KEY 环境变量")

    file_path = Path(file_path).expanduser()
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    # 检查文件格式
    if file_path.suffix.lower() not in AUDIO_FORMATS:
        raise ValueError(f"不支持格式 {file_path.suffix}，仅支持: mp3, wav")

    # 检查文件大小
    file_size = file_path.stat().st_size
    max_size = 128 * 1024 * 1024  # 128MB
    if file_size > max_size:
        raise ValueError(f"文件过大: {file_size / 1024 / 1024:.2f}MB，最大限制: 128MB")

    print(f"📁 上传音频文件: {file_path.name}")
    print(f"   文件大小: {file_size / 1024:.2f}KB")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
    }

    with open(file_path, 'rb') as f:
        files = {
            "file": (file_path.name, f)
        }
        data = {
            "purpose": "storage"  # 音色复刻必须使用 storage
        }

        response = requests.post(
            FILES_API_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=120
        )

    if response.status_code != 200:
        raise Exception(f"上传失败 ({response.status_code}): {response.text}")

    result = response.json()
    file_id = result.get('id')
    print(f"✅ 上传成功! 文件ID: {file_id}")

    return file_id


def clone_voice(file_id: str, text: str = None, model: str = "step-tts-mini") -> dict:
    """
    复刻音色

    Args:
        file_id: 上传的音频文件ID
        text: 音频对应的文本内容（可选，建议传入以提高效果）
        model: 模型名称 (step-tts-2 或 step-tts-mini)

    Returns:
        音色对象，包含 id, object, duplicated
    """
    if not API_KEY:
        raise ValueError("请设置 STEP_API_KEY 环境变量")

    if model not in MODELS:
        raise ValueError(f"不支持模型 {model}，可选: {list(MODELS.keys())}")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "file_id": file_id,
        "model": model
    }

    if text:
        payload["text"] = text

    print(f"\n🎤 复刻音色...")
    print(f"   文件ID: {file_id}")
    print(f"   模型: {model} ({MODELS[model]})")
    if text:
        print(f"   文本: {text[:50]}{'...' if len(text) > 50 else ''}")

    response = requests.post(
        VOICES_API_URL,
        headers=headers,
        json=payload,
        timeout=60
    )

    if response.status_code != 200:
        raise Exception(f"复刻失败 ({response.status_code}): {response.text}")

    result = response.json()

    if result.get('duplicated'):
        print("⚠️  提示: 该音色已存在，返回已有音色ID")

    return result


def clone_voice_from_file(file_path: str, text: str = None, model: str = "step-tts-mini") -> dict:
    """
    一键完成：上传音频 + 复刻音色

    Args:
        file_path: 音频文件路径
        text: 音频对应文本（可选）
        model: 模型名称

    Returns:
        音色对象
    """
    # Step 1: 上传文件
    print("=" * 50)
    print("StepFun 音色复刻工具")
    print("=" * 50)

    file_id = upload_audio(file_path)

    # Step 2: 复刻音色
    voice_result = clone_voice(file_id, text, model)

    return voice_result


def test_voice(voice_id: str, test_text: str = "这是测试语音"):
    """
    测试复刻的音色

    Args:
        voice_id: 音色ID
        test_text: 测试文本
    """
    import subprocess
    from datetime import datetime

    TTS_API_URL = "https://api.stepfun.com/step_plan/v1/audio/speech"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "stepaudio-2.5-tts",
        "input": test_text,
        "voice": voice_id
    }

    print(f"\n🔊 测试音色...")
    print(f"   音色ID: {voice_id}")
    print(f"   测试文本: {test_text}")

    response = requests.post(
        TTS_API_URL,
        headers=headers,
        json=payload,
        timeout=60
    )

    if response.status_code != 200:
        raise Exception(f"测试失败 ({response.status_code}): {response.text}")

    # 保存测试音频
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path("~/Downloads").expanduser() / f"voice_test_{voice_id}_{timestamp}.mp3"

    with open(output_path, 'wb') as f:
        f.write(response.content)

    print(f"✅ 测试音频已保存: {output_path}")

    # macOS 自动播放
    if sys.platform == "darwin":
        subprocess.run(["afplay", str(output_path)], check=False)


def main():
    parser = argparse.ArgumentParser(
        description="StepFun 音色复刻工具 - 上传音频并创建自定义音色",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用说明:
  音色复刻需要上传一段 5~10 秒的音频文件（mp3 或 wav）

  建议提供音频对应的文本内容，以提高复刻效果

  复刻成功后会返回音色ID，可用于 TTS 生成音频

示例:
  # 一键完成：上传 + 复刻
  %(prog)s voice.mp3 --text "大家好，欢迎来到我的频道"

  # 仅复刻（已有 file_id）
  %(prog)s --file-id file-abc123 --text "欢迎光临"

  # 测试复刻的音色
  %(prog)s --test voice-xyz789 --test-text "这是测试"

模型选择:
  step-tts-mini  轻量级模型（推荐，速度快）
  step-tts-2     高质量模型
"""
    )

    # 音频文件参数
    parser.add_argument("file", nargs="?", help="音频文件路径（mp3/wav，5~10秒）")

    # 文件ID参数（如果已有）
    parser.add_argument("--file-id", help="已上传的文件ID（跳过上传步骤）")

    # 音频文本
    parser.add_argument("--text", help="音频对应的文本内容（建议传入）")

    # 模型选择
    parser.add_argument("--model", default="step-tts-mini",
                        choices=list(MODELS.keys()),
                        help=f"TTS模型 (默认: step-tts-mini)")

    # 测试参数
    parser.add_argument("--test", metavar="VOICE_ID", help="测试音色ID")
    parser.add_argument("--test-text", default="这是测试语音，效果怎么样？",
                        help="测试文本内容")

    # 显示详细信息
    parser.add_argument("--verbose", "-v", action="store_true", help="显示完整响应")

    args = parser.parse_args()

    # 测试模式
    if args.test:
        try:
            test_voice(args.test, args.test_text)
            return
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            sys.exit(1)

    # 需要文件或文件ID
    if not args.file and not args.file_id:
        parser.error("请提供音频文件路径 或 --file-id 参数")

    try:
        # 一键模式：上传 + 复刻
        if args.file:
            result = clone_voice_from_file(args.file, args.text, args.model)

        # 仅复刻模式
        elif args.file_id:
            print("=" * 50)
            print("StepFun 音色复刻工具")
            print("=" * 50)
            result = clone_voice(args.file_id, args.text, args.model)

        # 输出结果
        print("\n" + "=" * 50)
        print("✅ 音色复刻成功!")
        print("=" * 50)
        print(f"音色ID: {result.get('id', 'N/A')}")

        if args.verbose:
            print(f"\n完整响应:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

        print(f"\n💡 使用方法:")
        print(f"   在 TTS API 中设置 voice='{result.get('id')}' 即可使用此音色")
        print(f"   或运行: python3 tts_tool.py --voice {result.get('id')} '测试文本'")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()