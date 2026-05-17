#!/usr/bin/env python3
"""
StepFun StepAudio 2.5 TTS 文本转语音工具
支持多音色、情绪控制、语速调节
"""

import os
import sys
import json
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("请先安装 requests: pip install requests")
    sys.exit(1)

# API 配置
API_URL = "https://api.stepfun.com/step_plan/v1/audio/speech"
API_KEY = os.environ.get("STEP_API_KEY", "")
MODEL_NAME = "stepaudio-2.5-tts"

# 默认参数
DEFAULT_VOICE = "voice-tone-QYvA34GkvQ"  # 自定义复刻音色
DEFAULT_SPEED = 0.9
DEFAULT_INSTRUCTION = "幽默搞笑风格，语气活泼有趣，像个搞笑主播，带有调侃和自嘲的感觉，语调生动变化，让人听了就想笑"

def split_text(text: str, max_length: int = 1000) -> list:
    """将长文本按行分割，确保每段不超过max_length"""
    paragraphs = text.strip().split('\n')
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) + 1 <= max_length:
            current_chunk += para + "\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def generate_filename(text: str, voice: str) -> str:
    """生成文件名: 时间戳_文本摘要_音色.mp3"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # 取前20个字符作为摘要
    summary = text[:20].replace('\n', '').replace(' ', '_')
    # 清理特殊字符
    summary = ''.join(c for c in summary if c.isalnum() or c == '_')
    return f"{timestamp}_{summary}_{voice}.mp3"

def tts_request(text: str, voice: str, speed: float, instruction: str, max_retries: int = 5) -> bytes:
    """调用 StepFun TTS API，支持重试"""
    if not API_KEY:
        raise ValueError("请设置 STEP_API_KEY 环境变量")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "input": text,
        "voice": voice,
        "speed": speed,
        "instruction": instruction
    }

    import time
    for attempt in range(max_retries):
        try:
            print(f"正在生成语音... (音色: {voice}, 语速: {speed}, 尝试: {attempt+1}/{max_retries})")
            response = requests.post(API_URL, headers=headers, json=payload, timeout=600)

            if response.status_code != 200:
                # 服务器错误时重试
                if response.status_code in [502, 503, 504]:
                    if attempt < max_retries - 1:
                        wait_time = 15 * (attempt + 1)
                        print(f"⚠️ 服务器错误 ({response.status_code}), {wait_time}秒后重试...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(f"API 服务器多次错误，请稍后重试")
                raise Exception(f"API 错误 ({response.status_code}): {response.text}")

            return response.content
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                wait_time = 15 * (attempt + 1)
                print(f"⏱️ 超时，{wait_time}秒后重试...")
                time.sleep(wait_time)
            else:
                raise Exception("API 多次超时，请稍后重试")
        except requests.exceptions.ConnectionError as e:
            if attempt < max_retries - 1:
                wait_time = 10 * (attempt + 1)
                print(f"🔌 连接错误，{wait_time}秒后重试...")
                time.sleep(wait_time)
            else:
                raise Exception(f"连接失败: {e}")

def save_and_play(audio_data: bytes, filename: str, output_dir: str = "~/Desktop", play: bool = True):
    """保存音频文件并自动播放"""
    output_path = Path(output_dir).expanduser() / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'wb') as f:
        f.write(audio_data)

    print(f"✅ 音频已保存: {output_path}")

    # macOS 自动播放
    if play and sys.platform == "darwin":
        subprocess.run(["afplay", str(output_path)], check=False)

    return str(output_path)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="StepFun TTS 文本转语音")
    parser.add_argument("text", nargs="?", help="要转换的文本")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help=f"音色 (默认: {DEFAULT_VOICE})")
    parser.add_argument("--speed", type=float, default=DEFAULT_SPEED, help=f"语速 0.5-2.0 (默认: {DEFAULT_SPEED})")
    parser.add_argument("--instruction", default=DEFAULT_INSTRUCTION, help=f"语气指令 (默认: {DEFAULT_INSTRUCTION})")
    parser.add_argument("--output", help="输出文件名")
    parser.add_argument("--file", help="从文件读取文本")
    parser.add_argument("--no-play", action="store_true", help="不自动播放")

    args = parser.parse_args()

    # 获取文本
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        print("请提供文本或使用 --file 参数")
        sys.exit(1)

    # 检查并分割文本
    chunks = split_text(text)
    print(f"文本长度: {len(text)} 字符, 分为 {len(chunks)} 段")

    output_files = []
    for i, chunk in enumerate(chunks):
        filename = args.output or generate_filename(chunk, args.voice)
        if len(chunks) > 1:
            filename = f"part{i+1}_{filename}"

        try:
            audio_data = tts_request(chunk, args.voice, args.speed, args.instruction)
            output_path = save_and_play(audio_data, filename, "~/Desktop", play=not args.no_play)
            output_files.append(output_path)
        except Exception as e:
            print(f"❌ 错误: {e}")
            sys.exit(1)

    print(f"\n🎉 完成! 共生成 {len(output_files)} 个音频文件")
    for f in output_files:
        print(f"  - {f}")

if __name__ == "__main__":
    main()