#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扩展 ISBN 测试图片生成器
生成更多测试图片，包含：
1. 纯数字命名（文件名后门测试）
2. 正常命名（云端OCR测试）

使用方法：
    python generate_more_isbn_images.py
"""

import os

from _generator_helpers import create_book_cover_image, create_isbn_only_image

TEST_BOOKS = [
    {"id": 1, "title": "高等数学（第七版）上册", "author": "同济大学数学系", "isbn": "9787000000001", "price": 39.80},
    {"id": 2, "title": "计算机网络（第七版）", "author": "谢希仁", "isbn": "9787000000002", "price": 46.00},
    {"id": 3, "title": "线性代数（第六版）", "author": "同济大学数学系", "isbn": "9787000000003", "price": 25.50},
    {"id": 4, "title": "概率论与数理统计", "author": "盛骤", "isbn": "9787000000004", "price": 32.00},
    {"id": 5, "title": "大学英语综合教程1", "author": "李荫华", "isbn": "9787000000005", "price": 28.50},
    {"id": 100, "title": "Python编程：从入门到实践", "author": "Eric Matthes", "isbn": "9787000000100", "price": 89.00},
    {"id": 101, "title": "深入理解计算机系统", "author": "Randal E. Bryant", "isbn": "9787000000101", "price": 139.00},
    {"id": 102, "title": "算法导论（原书第3版）", "author": "Thomas H. Cormen", "isbn": "9787000000102", "price": 128.00},
    {"id": 200, "title": "经济学原理（第8版）", "author": "曼昆", "isbn": "9787000000200", "price": 98.00},
    {"id": 201, "title": "心理学与生活（第19版）", "author": "Richard J. Gerrig", "isbn": "9787000000201", "price": 88.00},
]

COLORS = ['#F5F5DC', '#E8F4F8', '#FFF8E7', '#F0F8FF', '#F5F5F5']


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    print("=" * 70)
    print("SeekBook 扩展 ISBN 测试图片生成器")
    print("=" * 70)
    print()

    # Track 1: book cover images
    print("[Track 1] 书籍封面图片（云端OCR识别 - 正常命名）")
    print("-" * 70)
    for book in TEST_BOOKS:
        bg_color = COLORS[book['id'] % len(COLORS)]
        filename = f"book_id{book['id']}_{book['isbn']}.jpg"
        create_book_cover_image(book, os.path.join(script_dir, filename), bg_color)

    # Track 2: pure ISBN images
    print("[Track 2] 纯ISBN图片（文件名后门 - 纯数字命名）")
    print("-" * 70)
    for book in TEST_BOOKS:
        filename = f"{book['isbn']}.jpg"
        create_isbn_only_image(book['isbn'], os.path.join(script_dir, filename))

    # Track 3: extra pure ISBN images
    print("[Track 3] 额外纯数字测试图（文件名后门）")
    print("-" * 70)
    for isbn in ["9787000000006", "9787000000007", "9787000000008"]:
        create_isbn_only_image(isbn, os.path.join(script_dir, f"{isbn}.jpg"))

    print("=" * 70)
    print("所有测试图片生成完成！")
    print()
    print("使用说明：")
    print("-" * 70)
    print("【第一轨 - 云端OCR测试】（需要配置API key）")
    for book in TEST_BOOKS[:5]:
        print(f"    - book_id{book['id']}_{book['isbn']}.jpg")
    print()
    print("【第二轨 - 文件名后门测试】（无需API key）")
    for book in TEST_BOOKS[:5]:
        print(f"    - {book['isbn']}.jpg")
    print()
    print(f"图片位置: {script_dir}")
    print("=" * 70)


if __name__ == "__main__":
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("请先安装 Pillow 库：")
        print("  pip install Pillow")
        exit(1)
    main()