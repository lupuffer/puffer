#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISBN 测试图片生成器
根据数据库中的书籍信息生成带 ISBN 的测试图片

使用方法：
    python generate_isbn_images.py

生成的图片保存在当前目录，可用于测试 ISBN 双轨识别功能
"""

import os

from _generator_helpers import create_book_cover_image, create_isbn_only_image

TEST_BOOKS = [
    {"id": 1, "title": "高等数学（第七版）上册", "author": "同济大学数学系", "isbn": "9787000000001", "price": 39.80},
    {"id": 2, "title": "计算机网络（第七版）", "author": "谢希仁", "isbn": "9787000000002", "price": 46.00},
    {"id": 3, "title": "线性代数（第六版）", "author": "同济大学数学系", "isbn": "9787000000003", "price": 25.50},
    {"id": 100, "title": "Python编程：从入门到实践", "author": "Eric Matthes", "isbn": "9787000000100", "price": 89.00},
    {"id": 101, "title": "深入理解计算机系统", "author": "Randal E. Bryant", "isbn": "9787000000101", "price": 139.00},
]


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    print("=" * 60)
    print("SeekBook ISBN Test Image Generator")
    print("=" * 60)
    print()

    # Track 1: book cover images
    print("[Track 1] Book Cover Images (with ISBN text and barcode)")
    print("-" * 60)
    for book in TEST_BOOKS:
        filename = f"book_id{book['id']}_{book['isbn']}.jpg"
        create_book_cover_image(book, os.path.join(script_dir, filename))

    # Track 2: pure ISBN images
    print("[Track 2] Simple ISBN Images (for filename backdoor test)")
    print("-" * 60)
    for book in TEST_BOOKS[:3]:
        filename = f"{book['isbn']}.jpg"
        create_isbn_only_image(book['isbn'], os.path.join(script_dir, filename))

    print("=" * 60)
    print("All test images generated successfully!")
    print()
    print("Usage:")
    print("1. Track 1 Test (Cloud OCR):")
    print("   Drag 'book_idX_9787xxxx.jpg' to upload area")
    print("2. Track 2 Test (Filename Backdoor):")
    print("   Drag '9787xxxx.jpg' (pure ISBN filename) to upload area")
    print()
    print("Location:", script_dir)
    print("=" * 60)


if __name__ == "__main__":
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("请先安装 Pillow 库：")
        print("  pip install Pillow")
        exit(1)
    main()