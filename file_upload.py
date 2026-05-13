#!/usr/bin/env python3
"""
StepFun 文件上传工具
用于上传音色刻录文件，获取文件ID
API 文档: https://platform.stepfun.com/docs/zh/api-reference/files/create
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
API_URL = "https://api.stepfun.com/v1/files"
API_KEY = os.environ.get("STEP_API_KEY", "")

# 文件用途类型
PURPOSES = {
    "file-extract": "提取文件内容",
    "retrieval-text": "文本知识库",
    "retrieval-image": "图片知识库",
    "storage": "图片理解、视频理解、音色复刻"
}

# 各用途支持的文件格式
SUPPORTED_FORMATS = {
    "file-extract": ['.txt', '.md', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.csv', '.html', '.htm', '.xml'],
    "retrieval-text": ['.txt', '.md', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.csv', '.html', '.htm', '.xml'],
    "retrieval-image": ['.jpg', '.png'],
    "storage": ['.mp4', '.jpg', '.jpeg', '.png', '.webp', '.gif', '.mp3', '.wav']
}

# 文件大小限制（字节）
SIZE_LIMITS = {
    "file-extract": 64 * 1024 * 1024,    # 64MB
    "retrieval-text": 64 * 1024 * 1024,  # 64MB
    "retrieval-image": 64 * 1024 * 1024, # 64MB
    "storage": 128 * 1024 * 1024         # 128MB
}


def upload_file(file_path: str, purpose: str = "storage") -> dict:
    """
    上传文件到 StepFun

    Args:
        file_path: 文件路径
        purpose: 文件用途
            - file-extract: 提取文件内容
            - retrieval-text: 文本知识库
            - retrieval-image: 图片知识库
            - storage: 图片理解、视频理解、音色复刻（默认）

    Returns:
        File 对象，包含 id, object, bytes, created_at, filename, purpose, status
    """
    if not API_KEY:
        raise ValueError("请设置 STEP_API_KEY 环境变量")

    if purpose not in PURPOSES:
        raise ValueError(f"不支持的 purpose: {purpose}，可选: {list(PURPOSES.keys())}")

    file_path = Path(file_path).expanduser()
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    # 检查文件格式
    supported = SUPPORTED_FORMATS.get(purpose, [])
    if file_path.suffix.lower() not in supported:
        raise ValueError(f"purpose={purpose} 不支持格式 {file_path.suffix}，支持: {supported}")

    # 检查文件大小
    file_size = file_path.stat().st_size
    max_size = SIZE_LIMITS.get(purpose, 128 * 1024 * 1024)
    if file_size > max_size:
        raise ValueError(f"文件过大: {file_size / 1024 / 1024:.2f}MB，最大限制: {max_size / 1024 / 1024}MB")

    # 音色复刻特殊检查：音频时长 5~10 秒
    if purpose == "storage" and file_path.suffix.lower() in ['.mp3', '.wav']:
        print("⚠️  提示: 音色复刻要求音频时长 5~10 秒")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
    }

    print(f"正在上传文件: {file_path.name}")
    print(f"文件大小: {file_size / 1024:.2f}KB")
    print(f"用途: {purpose} ({PURPOSES[purpose]})")

    with open(file_path, 'rb') as f:
        files = {
            "file": (file_path.name, f)
        }
        data = {
            "purpose": purpose
        }

        response = requests.post(
            API_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=120
        )

    if response.status_code != 200:
        raise Exception(f"API 错误 ({response.status_code}): {response.text}")

    result = response.json()
    return result


def upload_from_url(url: str, purpose: str = "storage") -> dict:
    """
    从 URL 上传文件

    Args:
        url: 远程文件 URL
        purpose: 文件用途

    Returns:
        File 对象
    """
    if not API_KEY:
        raise ValueError("请设置 STEP_API_KEY 环境变量")

    if purpose not in PURPOSES:
        raise ValueError(f"不支持的 purpose: {purpose}")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
    }

    data = {
        "purpose": purpose,
        "url": url
    }

    print(f"正在从 URL 上传: {url}")
    print(f"用途: {purpose} ({PURPOSES[purpose]})")

    response = requests.post(
        API_URL,
        headers=headers,
        data=data,
        timeout=120
    )

    if response.status_code != 200:
        raise Exception(f"API 错误 ({response.status_code}): {response.text}")

    return response.json()


def main():
    parser = argparse.ArgumentParser(
        description="StepFun 文件上传工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
用途说明:
  file-extract    提取文件内容 (txt, md, pdf, doc, xls, ppt, csv, html, xml)
  retrieval-text  文本知识库 (同上)
  retrieval-image 图片知识库 (jpg, png)
  storage         图片理解、视频理解、音色复刻 (mp4, jpg, png, webp, gif, mp3, wav)

示例:
  # 上传音频用于音色复刻
  %(prog)s voice.mp3 --purpose storage

  # 上传 PDF 提取内容
  %(prog)s document.pdf --purpose file-extract

  # 从 URL 上传
  %(prog)s --url https://example.com/audio.mp3 --purpose storage
"""
    )
    parser.add_argument("file", nargs="?", help="要上传的文件路径")
    parser.add_argument("--purpose", default="storage",
                        choices=list(PURPOSES.keys()),
                        help="文件用途 (默认: storage，用于音色复刻)")
    parser.add_argument("--url", help="远程文件 URL（可选，与 file 二选一）")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示完整响应")

    args = parser.parse_args()

    if not args.file and not args.url:
        parser.error("请提供 file 或 --url 参数")

    try:
        if args.url:
            result = upload_from_url(args.url, args.purpose)
        else:
            result = upload_file(args.file, args.purpose)

        print(f"\n✅ 上传成功!")
        print(f"文件ID: {result.get('id', 'N/A')}")
        print(f"文件名: {result.get('filename', 'N/A')}")
        print(f"状态: {result.get('status', 'N/A')}")

        if args.verbose:
            print(f"\n完整响应:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

        # 返回 file_id
        return result.get('id')

    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    file_id = main()
    if file_id:
        print(f"\n💡 提示: 您可以使用此 file_id 进行后续操作（如音色刻录）")